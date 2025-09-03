from django.db import models
from .tournament import Tournament
from .season_team import SeasonTeam


class TournamentRanking(models.Model):
    """
    Rappresenta la posizione di una squadra nella classifica di un torneo.
    Memorizza statistiche come vittorie, pareggi, sconfitte e calcola la posizione.
    """
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='tournament_rankings')
    team = models.ForeignKey(SeasonTeam, on_delete=models.CASCADE, related_name='team_tournament_rankings')
    group = models.CharField(max_length=50, blank=True, help_text="Gruppo di appartenenza per tornei con gironi")

    # Risultati delle partite
    matches_played = models.PositiveIntegerField(default=0, help_text="Numero di partite giocate")
    win = models.PositiveIntegerField(default=0, help_text="Numero di vittorie")
    draw = models.PositiveIntegerField(default=0, help_text="Numero di pareggi")
    loss = models.PositiveIntegerField(default=0, help_text="Numero di sconfitte")
    win_penalty = models.PositiveIntegerField(default=0, help_text="Numero di vittorie ai rigori")
    loss_penalty = models.PositiveIntegerField(default=0, help_text="Numero di sconfitte ai rigori")
    win_extra_time = models.PositiveIntegerField(default=0, help_text="Numero di vittorie ai tempi supplementari")
    loss_extra_time = models.PositiveIntegerField(default=0, help_text="Numero di sconfitte ai tempi supplementari")

    # Statistiche gol
    goals_for = models.PositiveIntegerField(default=0, help_text="Gol segnati")
    goals_against = models.PositiveIntegerField(default=0, help_text="Gol subiti")

    # Disciplina
    yellow_cards = models.PositiveIntegerField(default=0, help_text="Cartellini gialli totali")
    red_cards = models.PositiveIntegerField(default=0, help_text="Cartellini rossi totali")

    # Punti e penalità
    points = models.IntegerField(default=0, help_text="Punti totali in classifica")
    points_penalty = models.IntegerField(default=0, help_text="Punti di penalizzazione")

    # Flag per stato
    qualified = models.BooleanField(default=False, help_text="Indica se la squadra è qualificata al turno successivo")
    relegated = models.BooleanField(default=False, help_text="Indica se la squadra è retrocessa")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('tournament', 'team', 'group')
        verbose_name = "Classifica Torneo"
        verbose_name_plural = "Classifiche Tornei"
        ordering = ['tournament', 'group', '-points', '-win', 'goals_against']

    def calculate_points(self):
        """Calcola i punti totali in base alle regole del torneo"""
        base_points = 0

        # Prima vediamo se ci sono regole specifiche
        rules = self.tournament.rules.filter(is_active=True)

        if rules.exists():
            # Se ci sono regole specifiche, le seguiamo
            for rule in rules:
                if rule.rule_type == 'point_win':
                    base_points += self.win * rule.value
                elif rule.rule_type == 'point_draw':
                    base_points += self.draw * rule.value
                elif rule.rule_type == 'point_loss':
                    base_points += self.loss * rule.value
                elif rule.rule_type == 'win_penalty':
                    base_points += self.win_penalty * rule.value
                elif rule.rule_type == 'loss_penalty':
                    base_points -= self.loss_penalty * rule.value
        else:
            # Altrimenti usiamo le regole generali dalla struttura del torneo
            structure = self.tournament.structure
            base_points += self.win * structure.POINTS_WIN
            base_points += self.draw * structure.POINTS_DRAW
            base_points += self.loss * structure.POINTS_LOSS

            # Aggiungiamo punti per vittorie/sconfitte ai rigori e ai tempi supplementari
            base_points += self.win_penalty * structure.POINTS_WIN_SHOOTOUT
            base_points += self.loss_penalty * structure.POINTS_LOSS_SHOOTOUT
            base_points += self.win_extra_time * structure.POINTS_WIN_EXTRA_TIME
            base_points += self.loss_extra_time * structure.POINTS_LOSS_EXTRA_TIME

        # Sottraiamo eventuali penalizzazioni
        total_points = base_points - self.points_penalty

        # Aggiorniamo il campo points
        if self.points != total_points:
            self.points = total_points
            self.save(update_fields=['points'])

        return total_points

    def update_match_stats(self):
        """Aggiorna le statistiche partite (gol fatti/subiti)"""
        from .match import Match

        # Partite in casa
        home_matches = Match.objects.filter(
            tournament=self.tournament,
            home_team=self.team.team,
            played=True
        )

        # Partite in trasferta
        away_matches = Match.objects.filter(
            tournament=self.tournament,
            away_team=self.team.team,
            played=True
        )

        # Reset statistiche
        self.win = 0
        self.draw = 0
        self.loss = 0
        self.win_penalty = 0
        self.loss_penalty = 0
        self.win_extra_time = 0
        self.loss_extra_time = 0
        self.goals_for = 0
        self.goals_against = 0

        # Conta vittorie, pareggi, sconfitte e gol per partite in casa
        for match in home_matches:
            if match.home_score is not None and match.away_score is not None:
                self.goals_for += match.home_score
                self.goals_against += match.away_score

                # Se il torneo non consente pareggi, verifichiamo il vincitore considerando tempi supplementari/rigori
                if match.home_score == match.away_score and not self.tournament.structure.allow_draws:
                    # Determiniamo il vincitore in base al metodo di spareggio
                    if match.extra_time_played:
                        if match.home_score_extra_time > match.away_score_extra_time:
                            self.win_extra_time += 1
                        elif match.away_score_extra_time > match.home_score_extra_time:
                            self.loss_extra_time += 1
                        # Se ancora pareggio, verifichiamo i rigori
                        elif match.penalties_played:
                            if match.home_score_penalties > match.away_score_penalties:
                                self.win_penalty += 1
                            else:
                                self.loss_penalty += 1
                    # Se solo rigori senza supplementari
                    elif match.penalties_played:
                        if match.home_score_penalties > match.away_score_penalties:
                            self.win_penalty += 1
                        else:
                            self.loss_penalty += 1
                else:
                    # Gestione normale per partite con risultato definito
                    if match.home_score > match.away_score:
                        self.win += 1
                    elif match.home_score == match.away_score:
                        self.draw += 1
                    else:
                        self.loss += 1

        # Conta vittorie, pareggi, sconfitte e gol per partite in trasferta
        for match in away_matches:
            if match.home_score is not None and match.away_score is not None:
                self.goals_for += match.away_score
                self.goals_against += match.home_score

                # Se il torneo non consente pareggi, verifichiamo il vincitore considerando tempi supplementari/rigori
                if match.home_score == match.away_score and not self.tournament.structure.allow_draws:
                    # Determiniamo il vincitore in base al metodo di spareggio
                    if match.extra_time_played:
                        if match.away_score_extra_time > match.home_score_extra_time:
                            self.win_extra_time += 1
                        elif match.home_score_extra_time > match.away_score_extra_time:
                            self.loss_extra_time += 1
                        # Se ancora pareggio, verifichiamo i rigori
                        elif match.penalties_played:
                            if match.away_score_penalties > match.home_score_penalties:
                                self.win_penalty += 1
                            else:
                                self.loss_penalty += 1
                    # Se solo rigori senza supplementari
                    elif match.penalties_played:
                        if match.away_score_penalties > match.home_score_penalties:
                            self.win_penalty += 1
                        else:
                            self.loss_penalty += 1
                else:
                    # Gestione normale per partite con risultato definito
                    if match.away_score > match.home_score:
                        self.win += 1
                    elif match.away_score == match.home_score:
                        self.draw += 1
                    else:
                        self.loss += 1

        # Aggiorna il totale partite giocate
        self.matches_played = self.win + self.draw + self.loss + self.win_penalty + self.loss_penalty + self.win_extra_time + self.loss_extra_time

        # Calcola i punti
        self.calculate_points()

        self.save()

    def get_ranking_position(self):
        """Calcola la posizione in classifica del team"""
        filters = {'tournament': self.tournament}

        # Se il torneo ha gironi, filtra per lo stesso girone
        if self.group:
            filters['group'] = self.group

        rankings = list(TournamentRanking.objects.filter(**filters))
        # Ordina per punti (decrescente), vittorie, differenza reti, ecc.
        rankings.sort(key=lambda r: (-r.points, -r.win, -(r.goals_for - r.goals_against), -r.goals_for, r.team.team.name))

        for index, ranking in enumerate(rankings, start=1):
            if ranking.id == self.id:
                return index
        return None

    def get_goal_difference(self):
        """Calcola la differenza reti"""
        return self.goals_for - self.goals_against

    def get_complete_ranking(self):
        """Restituisce la classifica completa del torneo/girone"""
        filters = {'tournament': self.tournament}

        if self.group:
            filters['group'] = self.group

        rankings = list(TournamentRanking.objects.filter(**filters))
        rankings.sort(key=lambda r: (-r.points, -r.win, -(r.goals_for - r.goals_against), -r.goals_for, r.team.team.name))

        result = []
        for position, ranking in enumerate(rankings, start=1):
            result.append({
                'position': position,
                'team': ranking.team,
                'points': ranking.points,
                'played': ranking.matches_played,
                'win': ranking.win,
                'draw': ranking.draw,
                'loss': ranking.loss,
                'goals_for': ranking.goals_for,
                'goals_against': ranking.goals_against,
                'goal_diff': ranking.get_goal_difference(),
                'qualified': ranking.qualified,
                'relegated': ranking.relegated
            })

        return result

    def __str__(self):
        position = self.get_ranking_position() or '?'
        group_str = f" (Girone {self.group})" if self.group else ""
        return f"{self.team.team.name}{group_str} - {self.tournament.name} [{position}°]"

    def squad_points(self):
        """Restituisce i punti della squadra in classifica (per compatibilità con i test)"""
        return self.points

    def squad_ranking(self):
        """Restituisce la posizione in classifica (per compatibilità con i test)"""
        return self.get_ranking_position() or 1

    def get_matches_played(self):
        """Restituisce il numero di partite giocate (per compatibilità con i test)"""
        return self.matches_played

    def squad_goals(self):
        """Restituisce i gol segnati dalla squadra (per compatibilità con i test)"""
        return self.goals_for

    def squad_goals_against(self):
        """Restituisce i gol subiti dalla squadra (per compatibilità con i test)"""
        return self.goals_against

    def squad_goal_difference(self):
        """Restituisce la differenza reti (per compatibilità con i test)"""
        return self.goals_for - self.goals_against

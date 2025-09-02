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
        rules = self.tournament.rules.filter(is_active=True)

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
        self.goals_for = 0
        self.goals_against = 0

        # Conta vittorie, pareggi, sconfitte e gol per partite in casa
        for match in home_matches:
            if match.home_score is not None and match.away_score is not None:
                self.goals_for += match.home_score
                self.goals_against += match.away_score

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

                if match.away_score > match.home_score:
                    self.win += 1
                elif match.away_score == match.home_score:
                    self.draw += 1
                else:
                    self.loss += 1

        # Aggiorna il totale partite giocate
        self.matches_played = self.win + self.draw + self.loss + self.win_penalty + self.loss_penalty

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

from django.db import models
from .player import Player
from .tournament import Tournament
from .season import Season


class PlayerStatistics(models.Model):
    """
    Statistiche complessive di un giocatore in una stagione o un torneo specifico.
    """
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='statistics', verbose_name="Giocatore", help_text="Il giocatore a cui appartengono le statistiche")
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='player_statistics', null=True, blank=True, help_text="Stagione di riferimento")
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='player_statistics', null=True, blank=True, help_text="Torneo di riferimento")

    # Statistiche di base
    matches_played = models.PositiveIntegerField(default=0, help_text="Partite giocate")
    matches_started = models.PositiveIntegerField(default=0, help_text="Partite iniziate da titolare")
    minutes_played = models.PositiveIntegerField(default=0, help_text="Minuti giocati")

    # Gol e assist
    goals_scored = models.PositiveIntegerField(default=0, help_text="Gol segnati")
    assists_made = models.PositiveIntegerField(default=0, help_text="Assist effettuati")
    penalties_scored = models.PositiveIntegerField(default=0, help_text="Rigori segnati")
    penalties_missed = models.PositiveIntegerField(default=0, help_text="Rigori sbagliati")

    # Cartellini e disciplina
    yellow_cards = models.PositiveIntegerField(default=0, help_text="Cartellini gialli")
    red_cards = models.PositiveIntegerField(default=0, help_text="Cartellini rossi")
    fouls_committed = models.PositiveIntegerField(default=0, help_text="Falli commessi")
    fouls_suffered = models.PositiveIntegerField(default=0, help_text="Falli subiti")

    # Statistiche specifiche per ruolo
    clean_sheets = models.PositiveIntegerField(default=0, help_text="Porte inviolate (portieri e difensori)")
    goals_conceded = models.PositiveIntegerField(default=0, help_text="Gol subiti (portieri)")
    saves = models.PositiveIntegerField(default=0, help_text="Parate (portieri)")
    penalties_saved = models.PositiveIntegerField(default=0, help_text="Rigori parati (portieri)")

    # Altre statistiche avanzate
    shots = models.PositiveIntegerField(default=0, help_text="Tiri totali")
    shots_on_target = models.PositiveIntegerField(default=0, help_text="Tiri in porta")
    key_passes = models.PositiveIntegerField(default=0, help_text="Passaggi chiave")
    accurate_passes = models.PositiveIntegerField(default=0, help_text="Passaggi precisi")
    pass_success_rate = models.FloatField(default=0.0, help_text="Percentuale passaggi riusciti")
    tackles = models.PositiveIntegerField(default=0, help_text="Tackle")
    interceptions = models.PositiveIntegerField(default=0, help_text="Intercetti")
    own_goals = models.PositiveIntegerField(default=0, help_text="Autogol")

    # Statistiche Fantacalcio
    fanta_average = models.FloatField(default=0.0, help_text="Media fantavoto")
    fanta_total = models.FloatField(default=0.0, help_text="Totale fantavoto")
    bonus_points = models.FloatField(default=0.0, help_text="Punti bonus totali")
    malus_points = models.FloatField(default=0.0, help_text="Punti malus totali")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Statistiche Giocatore"
        verbose_name_plural = "Statistiche Giocatori"
        ordering = ['-matches_played', '-goals_scored', '-assists_made']
        unique_together = ('player', 'season', 'tournament')

    def calculate_average_rating(self):
        """Calcola la media dei voti del giocatore"""
        if self.matches_played > 0:
            from .fanta_score import FantaScore
            scores = FantaScore.objects.filter(player=self.player)

            if self.season:
                scores = scores.filter(match__tournament__season=self.season)

            if self.tournament:
                scores = scores.filter(match__tournament=self.tournament)

            valid_scores = scores.exclude(vote=None)
            if valid_scores.count() > 0:
                avg = valid_scores.aggregate(models.Avg('vote'))['vote__avg'] or 0
                return round(avg, 2)
        return 0.0

    def update_fanta_stats(self):
        """Aggiorna le statistiche del fantacalcio"""
        from .fanta_score import FantaScore
        scores = FantaScore.objects.filter(player=self.player)

        if self.season:
            scores = scores.filter(match__tournament__season=self.season)

        if self.tournament:
            scores = scores.filter(match__tournament=self.tournament)

        valid_scores = scores.exclude(final_score=0)

        if valid_scores.count() > 0:
            self.fanta_total = valid_scores.aggregate(models.Sum('final_score'))['final_score__sum'] or 0
            self.fanta_average = valid_scores.aggregate(models.Avg('final_score'))['final_score__avg'] or 0
            self.bonus_points = sum([
                (s.goals * 3) + (s.assists * 1) + (s.penalties_scored * 2) +
                (s.penalties_saved * 3) + (1 if s.clean_sheet else 0)
                for s in valid_scores
            ])
            self.malus_points = sum([
                (s.yellow_cards * 0.5) + (s.red_cards * 1) +
                (s.own_goals * 2) + (s.penalties_missed * 3) +
                (s.goals_conceded if self.player.main_role == 'P' else 0)
                for s in valid_scores
            ])

            self.save()

    def __str__(self):
        period = ""
        if self.season:
            period += f" - Stagione {self.season.year}"
        if self.tournament:
            period += f" - {self.tournament.name}"

        return f"Statistiche {self.player.person.surname}{period}"

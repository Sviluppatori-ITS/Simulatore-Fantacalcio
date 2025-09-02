from django.db import models
from django.utils import timezone
from .team import Team
from .tournament import Tournament


class Match(models.Model):
    """
    Rappresenta una partita tra due squadre in un torneo.
    """
    # Squadre e risultato
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches', help_text="Squadra di casa")
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches', help_text="Squadra ospite")
    home_score = models.PositiveIntegerField(null=True, blank=True, help_text="Gol squadra di casa")
    away_score = models.PositiveIntegerField(null=True, blank=True, help_text="Gol squadra ospite")

    # Dettagli partita
    round = models.ForeignKey('Round', on_delete=models.CASCADE, related_name='matches', null=True, blank=True, help_text="Giornata della partita")
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches', help_text="Torneo a cui appartiene la partita")
    venue = models.CharField(max_length=200, blank=True, help_text="Luogo della partita")
    referee = models.CharField(max_length=200, blank=True, help_text="Arbitro della partita")

    # Date e stato
    kickoff_datetime = models.DateTimeField(null=True, blank=True, help_text="Data e ora di inizio")
    played = models.BooleanField(default=False, help_text="Indica se la partita è stata giocata")
    cancelled = models.BooleanField(default=False, help_text="Indica se la partita è stata annullata")
    postponed = models.BooleanField(default=False, help_text="Indica se la partita è stata rinviata")

    # Statistiche partita
    home_possession = models.FloatField(null=True, blank=True, help_text="Possesso palla squadra di casa (%)")
    away_possession = models.FloatField(null=True, blank=True, help_text="Possesso palla squadra ospite (%)")
    home_shots = models.PositiveIntegerField(null=True, blank=True, help_text="Tiri totali squadra di casa")
    away_shots = models.PositiveIntegerField(null=True, blank=True, help_text="Tiri totali squadra ospite")
    home_shots_on_target = models.PositiveIntegerField(null=True, blank=True, help_text="Tiri in porta squadra di casa")
    away_shots_on_target = models.PositiveIntegerField(null=True, blank=True, help_text="Tiri in porta squadra ospite")
    home_corners = models.PositiveIntegerField(null=True, blank=True, help_text="Calci d'angolo squadra di casa")
    away_corners = models.PositiveIntegerField(null=True, blank=True, help_text="Calci d'angolo squadra ospite")
    home_fouls = models.PositiveIntegerField(null=True, blank=True, help_text="Falli commessi squadra di casa")
    away_fouls = models.PositiveIntegerField(null=True, blank=True, help_text="Falli commessi squadra ospite")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Partita"
        verbose_name_plural = "Partite"
        ordering = ['tournament', 'round', 'kickoff_datetime']

    def is_upcoming(self):
        """Verifica se la partita è futura"""
        return self.kickoff_datetime and self.kickoff_datetime > timezone.now() and not self.played

    def is_live(self):
        """Verifica se la partita è in corso"""
        now = timezone.now()
        if not self.kickoff_datetime:
            return False
        return self.kickoff_datetime <= now and now <= (self.kickoff_datetime + timezone.timedelta(hours=2)) and not self.played

    def get_status(self):
        """Restituisce lo stato attuale della partita"""
        if self.cancelled:
            return "Annullata"
        if self.postponed:
            return "Rinviata"
        if self.played:
            return "Terminata"
        if self.is_live():
            return "In corso"
        if self.is_upcoming():
            return "Da giocare"
        return "Non programmata"

    def __str__(self):
        if self.home_score is not None and self.away_score is not None:
            result = f"{self.home_score}-{self.away_score}"
        else:
            result = "vs"

        return f"{self.home_team.name} {result} {self.away_team.name} - {self.tournament.name} (Giornata {self.round.number})"

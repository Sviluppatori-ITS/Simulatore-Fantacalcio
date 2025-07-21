from django.db import models
from .tournament_structure import TournamentStructure
from .season import Season
from .season_team import SeasonTeam
from .trophy import Trophy


class Tournament(models.Model):
    name = models.CharField(max_length=100)  # Serie A, Coppa Italia, ecc.
    description = models.TextField(blank=True)
    structure = models.ForeignKey(TournamentStructure, on_delete=models.PROTECT)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='tournament')
    teams = models.ManyToManyField(SeasonTeam, related_name='tournaments', blank=True)  # Squadre partecipanti
    current_match_day = models.PositiveIntegerField(default=1)  # Giorno corrente del torneo
    trophy = models.ForeignKey(Trophy, on_delete=models.SET_NULL, null=True, blank=True, related_name='tournaments')  # Trofeo associato
    is_active = models.BooleanField(default=True, help_text="Indica se il torneo è attivo")
    start_date = models.DateField(null=True, blank=True, help_text="Data di inizio del torneo")
    end_date = models.DateField(null=True, blank=True, help_text="Data di fine del torneo")
    logo = models.ImageField(upload_to='tournaments/', null=True, blank=True, help_text="Logo del torneo")  # Logo del torneo

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # tutto il resto può essere semplificato o spostato

    def __str__(self):
        return f"{self.name} - {self.season.year} ({'Attivo - Giornata Corrente: ' + str(self.current_match_day) if self.is_active else 'Inattivo'})"

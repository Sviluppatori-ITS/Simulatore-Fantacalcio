from django.db import models
from .tournament import Tournament
from .match import Match


class Round(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='rounds')
    matches = models.ManyToManyField(Match, related_name='rounds', blank=True)
    match_day = models.PositiveIntegerField()
    label = models.CharField(max_length=100, blank=True, help_text="Nome del turno, es. 'Ottavi di finale'")
    knockout_stage = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.label:
            return f"{self.label} - {self.tournament.name}"
        return f"Turno {self.match_day} - {self.tournament.name}"

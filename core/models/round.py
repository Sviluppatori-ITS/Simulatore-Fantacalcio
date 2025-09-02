from django.db import models
from .tournament import Tournament


class Round(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='rounds')
    number = models.PositiveIntegerField(default=1, help_text="Numero della giornata o turno")
    label = models.CharField(max_length=100, blank=True, help_text="Nome del turno, es. 'Ottavi di finale'")
    knockout_stage = models.BooleanField(default=False, help_text="Indica se è una fase a eliminazione diretta")
    label = models.CharField(max_length=100, blank=True, help_text="Nome del turno, es. 'Ottavi di finale'")
    knockout_stage = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.label:
            return f"{self.label} - {self.tournament.name}"
        return f"Turno {self.number} - {self.tournament.name}"

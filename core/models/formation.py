from django.db import models
from .season_team import SeasonTeam
from .tournament import Tournament
from .default_formation import DefaultFormation


class Formation(models.Model):
    team = models.ForeignKey(SeasonTeam, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    tactic_name = models.CharField(max_length=100, default="4-3-3", help_text="Nome della formazione, es. '4-3-3', '3-5-2', ecc.")
    is_default_formation = models.BooleanField(default=False, help_text="Indica se questa è la formazione predefinita per il torneo")
    default_formation = models.ForeignKey('DefaultFormation', on_delete=models.SET_NULL, null=True, blank=True, related_name='default_formations', help_text="Formazione predefinita associata")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('team', 'tournament', 'tactic_name')
        ordering = ['team', 'tournament', 'tactic_name']
        verbose_name = "Formazione"
        verbose_name_plural = "Formazioni"

    def save(self, *args, **kwargs):
        if self.is_default_formation and not self.default_formation:
            # Se è una formazione predefinita, assicurati che esista una DefaultFormation
            default_formation, created = DefaultFormation.objects.get_or_create(name=self.tactic_name, formation=self.tactic_name, description=f"Formazione predefinita per {self.tactic_name}")
            self.default_formation = default_formation

        elif not self.is_default_formation and self.default_formation:
            # Se non è una formazione predefinita, rimuovi il riferimento alla DefaultFormation
            self.default_formation = None
            # Assicurati che il nome della formazione sia unico per la combinazione di squadra e torneo
            if not self.tactic_name:
                self.tactic_name = "4-3-3"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Formazione: {self.tactic_name} - {self.team.name} ({self.tournament.name})"

from django.db import models
from .season_team import SeasonTeam
from .player import Player


class RosterSlot(models.Model):
    team = models.ForeignKey(SeasonTeam, on_delete=models.CASCADE, related_name='roster')
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    is_starting = models.BooleanField(default=False)  # titolare o panchina
    role = models.CharField(max_length=20, choices=[('P', 'Portiere'), ('D', 'Difensore'), ('C', 'Centrocampista'), ('A', 'Attaccante')], default='C')
    shirt_number = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [
            ('team', 'player'),
            ('team', 'shirt_number'),
        ]
        ordering = ['team', 'shirt_number']

    def __str__(self):
        return f"{self.player.name} ({self.role}) - {self.team.team.name} {'(Titolare)' if self.is_starting else '(Panchina)'}"

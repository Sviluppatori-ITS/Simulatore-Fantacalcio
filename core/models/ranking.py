from django.db import models
from .team import Team
from .tournament import Tournament


class Ranking(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='rankings')
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='rankings')
    rank = models.PositiveIntegerField()  # Posizione in classifica
    points = models.PositiveIntegerField(default=0)  # Punti accumulati

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('team', 'tournament')

    def __str__(self):
        return f"{self.team.name} - {self.tournament.name} (Rank: {self.rank}, Points: {self.points})"

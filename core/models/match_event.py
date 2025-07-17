from django.db import models
from .match import Match
from .player import Player
from .season_team import SeasonTeam


class MatchEvent(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='events')
    minute = models.PositiveIntegerField()
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True)
    team = models.ForeignKey(SeasonTeam, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=20, choices=[
        ('goal', 'Goal'),
        ('assist', 'Assist'),
        ('yellow_card', 'Ammonizione'),
        ('red_card', 'Espulsione'),
        ('substitution', 'Sostituzione'),
        ('injury', 'Infortunio'),
        ('penalty', 'Rigore'),
        ('own_goal', 'Autogol'),
        ('foul', 'Fallo'),
        ('corner', 'Calcio d\'angolo'),
        ('offside', 'Fuorigioco'),
        ('save', 'Parata'),
        ('clearance', 'Rinvio')
        # ...
    ])
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['minute']
        unique_together = ('match', 'minute', 'event_type', 'player')

    def __str__(self):
        return f"{self.event_type} at {self.minute}' - {self.match.home_team.name} vs {self.match.away_team.name} ({self.player.name if self.player else 'N/A'})"

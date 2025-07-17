from django.db import models
from .player import Player
from .match import Match


class MatchHistory(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="match_performances")
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="performances")
    rating = models.FloatField()
    goals = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    minutes_played = models.PositiveIntegerField(default=0)
    is_starting = models.BooleanField(default=False)
    yellow_cards = models.PositiveIntegerField(default=0)
    red_cards = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('player', 'match')

    def __str__(self):
        return f"Match Performance: {self.player.name} in {self.match.home_team.name} vs {self.match.away_team.name}"

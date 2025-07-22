from django.db import models
from .team import Team


class SeasonTeam(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='season_teams')
    season = models.ForeignKey("Season", on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # class Meta:
    #     unique_together = ('team', 'tournament')

    def __str__(self):
        return f"{self.team.name}"

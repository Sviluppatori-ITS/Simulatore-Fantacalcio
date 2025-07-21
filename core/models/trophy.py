from django.db import models
# from .season_team import SeasonTeam


class Trophy(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    trophy_img = models.ImageField(upload_to='trophies/', null=True, blank=True)  # Immagine del trofeo
    awarded_to = models.ForeignKey("core.SeasonTeam", on_delete=models.CASCADE, related_name='trophies', null=True, blank=True)  # Squadra vincitrice

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_awarded(self):
        return self.awarded_to is not None

    def __str__(self):
        tournament = self.tournaments.first()
        return f"{self.name} - {self.awarded_to.team.name if self.awarded_to else 'No Winner'} ({tournament.name if tournament else 'No Tournament'})"

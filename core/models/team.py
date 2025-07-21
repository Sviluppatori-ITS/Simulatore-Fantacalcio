from django.db import models
from django.contrib.auth.models import User


class Team(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=5)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teams')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.code:
            self.code = self.code.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        tournament_names = set()
        for st in self.season_teams.all():
            for tournament in st.tournaments.all():
                tournament_names.add(tournament.name)
        tournaments_str = ", ".join(tournament_names)
        return f"{self.name} ({self.code}) - [{tournaments_str}]"

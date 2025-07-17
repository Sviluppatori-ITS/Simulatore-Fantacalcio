from django.db import models


class TournamentStructure(models.Model):
    is_cup = models.BooleanField(default=False)
    use_groups = models.BooleanField(default=False)
    home_and_away = models.BooleanField(default=True)

    has_playoff = models.BooleanField(default=False)
    has_playout = models.BooleanField(default=False)

    relegation_enabled = models.BooleanField(default=False)
    relegation_teams = models.PositiveIntegerField(default=0)
    playoff_teams = models.PositiveIntegerField(default=0)
    playout_teams = models.PositiveIntegerField(default=0)
    qualification_spots = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{'Coppa' if self.is_cup else 'Campionato'}{' con gironi' if self.use_groups else ''}"

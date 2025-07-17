from django.db import models
from .player import Player


class PlayerStatistics(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE, related_name='statistics', verbose_name="Giocatore", help_text="Il giocatore a cui appartengono le statistiche")
    matches_played = models.PositiveIntegerField(default=0)
    goals_scored = models.PositiveIntegerField(default=0)
    assists_made = models.PositiveIntegerField(default=0)
    yellow_cards = models.PositiveIntegerField(default=0)
    red_cards = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Statistiche Giocatore"
        verbose_name_plural = "Statistiche Giocatori"
        ordering = ['-matches_played', '-goals_scored', '-assists_made', '-yellow_cards', '-red_cards']

    def __str__(self):
        return f"Statistics for {self.player.name}"

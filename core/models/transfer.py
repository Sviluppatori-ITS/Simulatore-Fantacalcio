from re import I
from django.db import models
from .player import Player
from .season_team import SeasonTeam


class Transfer(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    from_team = models.ForeignKey(SeasonTeam, on_delete=models.CASCADE, related_name='transfers_out')
    to_team = models.ForeignKey(SeasonTeam, on_delete=models.CASCADE, related_name='transfers_in')
    fee = models.DecimalField(max_digits=6, decimal_places=2, help_text="Quota di trasferimento pagata per il giocatore")
    transfer_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('player', 'from_team', 'to_team', 'transfer_date')

    def __str__(self):
        return f"{self.player.person.name} transferred from {self.from_team.team.name} to {self.to_team.team.name} for {self.fee} on {self.transfer_date}"

from django.db import models
from django.contrib.auth.models import User
from .player import Player
from .tournament import Tournament
from .season import Season


class FantaTeam(models.Model):
    """
    Rappresenta una squadra di Fantacalcio creata da un utente.
    """
    name = models.CharField(max_length=100, help_text="Nome della squadra di fantacalcio")
    logo = models.ImageField(upload_to='fanta_teams/', null=True, blank=True, help_text="Logo della squadra")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fanta_teams', help_text="Proprietario della squadra")
    budget = models.IntegerField(default=500, help_text="Budget disponibile per il mercato (in crediti)")
    motto = models.CharField(max_length=200, blank=True, help_text="Motto della squadra")
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='fanta_teams', help_text="Stagione di riferimento")
    players = models.ManyToManyField(Player, through='FantaTeamPlayer', related_name='fanta_teams', help_text="Giocatori nella rosa")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Squadra Fantacalcio"
        verbose_name_plural = "Squadre Fantacalcio"
        unique_together = ('name', 'owner', 'season')

    def get_total_value(self):
        """Calcola il valore totale della rosa"""
        return sum(tp.purchase_price for tp in self.fantateamplayer_set.all())

    def get_remaining_budget(self):
        """Calcola il budget rimanente"""
        return self.budget - self.get_total_value()

    def __str__(self):
        return f"{self.name} ({self.owner.username}) - {self.season}"


class FantaTeamPlayer(models.Model):
    """
    Tabella di relazione tra FantaTeam e Player con attributi aggiuntivi
    """
    fanta_team = models.ForeignKey(FantaTeam, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    purchase_price = models.IntegerField(help_text="Prezzo di acquisto in crediti")
    purchase_date = models.DateTimeField(auto_now_add=True, help_text="Data di acquisto")
    is_active = models.BooleanField(default=True, help_text="Indica se il giocatore è ancora nella rosa")

    class Meta:
        verbose_name = "Giocatore in Rosa"
        verbose_name_plural = "Giocatori in Rosa"
        unique_together = ('fanta_team', 'player')

    def __str__(self):
        return f"{self.player} in {self.fanta_team.name} ({self.purchase_price} crediti)"

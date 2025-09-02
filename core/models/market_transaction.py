from django.db import models
from django.contrib.auth.models import User
from .fanta_team import FantaTeam
from .fanta_league import FantaLeague
from .player import Player


class MarketTransaction(models.Model):
    """
    Rappresenta una transazione di mercato nel fantacalcio (acquisto, vendita o scambio).
    """
    TRANSACTION_TYPES = [
        ('buy', 'Acquisto'),
        ('sell', 'Vendita'),
        ('trade', 'Scambio'),
        ('loan', 'Prestito'),
        ('bid', 'Offerta Asta'),
        ('free_agent', 'Svincolato'),
    ]

    STATUS_CHOICES = [
        ('pending', 'In attesa'),
        ('completed', 'Completata'),
        ('rejected', 'Rifiutata'),
        ('cancelled', 'Annullata'),
    ]

    # Dati generali della transazione
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, help_text="Tipo di transazione")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', help_text="Stato della transazione")
    league = models.ForeignKey(FantaLeague, on_delete=models.CASCADE, related_name='transactions', help_text="Lega in cui avviene la transazione")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_transactions', help_text="Utente che ha creato la transazione")

    # Dati specifici per acquisto/vendita
    team = models.ForeignKey(FantaTeam, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True, help_text="Squadra che effettua la transazione")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True, help_text="Giocatore coinvolto nella transazione")
    price = models.IntegerField(default=0, help_text="Prezzo della transazione in crediti")

    # Dati specifici per scambi
    team_counterparty = models.ForeignKey(FantaTeam, on_delete=models.CASCADE, related_name='counterparty_transactions', null=True, blank=True, help_text="Squadra controparte nello scambio")
    player_counterparty = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='counterparty_transactions', null=True, blank=True, help_text="Giocatore ricevuto nello scambio")
    price_adjustment = models.IntegerField(default=0, help_text="Conguaglio economico per lo scambio")

    # Timestamp e note
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True, help_text="Data di completamento della transazione")
    notes = models.TextField(blank=True, help_text="Note aggiuntive sulla transazione")

    class Meta:
        verbose_name = "Transazione di Mercato"
        verbose_name_plural = "Transazioni di Mercato"
        ordering = ['-created_at']

    def complete_transaction(self):
        """
        Completa la transazione aggiornando i roster e i budget delle squadre
        """
        from django.utils import timezone

        if self.status != 'pending':
            return False

        # Logica per i diversi tipi di transazione
        if self.transaction_type == 'buy':
            # Aggiorna il roster e il budget della squadra acquirente
            self.team.fantateamplayer_set.create(
                player=self.player,
                purchase_price=self.price,
                is_active=True
            )
            self.team.budget -= self.price
            self.team.save()

        elif self.transaction_type == 'sell':
            # Rimuovi il giocatore dal roster e aggiorna il budget
            team_player = self.team.fantateamplayer_set.get(player=self.player, is_active=True)
            team_player.is_active = False
            team_player.save()

            self.team.budget += self.price
            self.team.save()

        elif self.transaction_type == 'trade':
            # Gestisci lo scambio tra due squadre
            if not all([self.team, self.team_counterparty, self.player, self.player_counterparty]):
                self.status = 'rejected'
                self.save()
                return False

            # Rimuovi giocatori dalle rispettive squadre
            team1_player = self.team.fantateamplayer_set.get(player=self.player, is_active=True)
            team1_player.is_active = False
            team1_player.save()

            team2_player = self.team_counterparty.fantateamplayer_set.get(player=self.player_counterparty, is_active=True)
            team2_player.is_active = False
            team2_player.save()

            # Aggiungi i giocatori alle nuove squadre
            self.team.fantateamplayer_set.create(
                player=self.player_counterparty,
                purchase_price=team2_player.purchase_price,
                is_active=True
            )

            self.team_counterparty.fantateamplayer_set.create(
                player=self.player,
                purchase_price=team1_player.purchase_price,
                is_active=True
            )

            # Gestisci il conguaglio economico
            if self.price_adjustment != 0:
                self.team.budget -= self.price_adjustment
                self.team_counterparty.budget += self.price_adjustment
                self.team.save()
                self.team_counterparty.save()

        # Aggiorna lo stato della transazione
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
        return True

    def __str__(self):
        if self.transaction_type == 'trade':
            return f"Scambio: {self.player.person.surname} ({self.team.name}) ⇄ {self.player_counterparty.person.surname} ({self.team_counterparty.name})"
        elif self.transaction_type == 'buy':
            return f"Acquisto: {self.player.person.surname} → {self.team.name} ({self.price} crediti)"
        elif self.transaction_type == 'sell':
            return f"Vendita: {self.player.person.surname} ← {self.team.name} ({self.price} crediti)"
        else:
            return f"Transazione: {self.get_transaction_type_display()} - {self.get_status_display()}"


class AuctionBid(models.Model):
    """
    Rappresenta un'offerta in un'asta per un giocatore.
    """
    league = models.ForeignKey(FantaLeague, on_delete=models.CASCADE, related_name='bids')
    team = models.ForeignKey(FantaTeam, on_delete=models.CASCADE, related_name='bids')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='bids')
    amount = models.IntegerField(help_text="Offerta in crediti")
    is_winning = models.BooleanField(default=False, help_text="Indica se questa è l'offerta vincente")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Offerta Asta"
        verbose_name_plural = "Offerte Asta"
        ordering = ['-amount', 'timestamp']

    def __str__(self):
        status = "vincente" if self.is_winning else "in corso"
        return f"{self.team.name}: {self.amount} crediti per {self.player.person.surname} ({status})"

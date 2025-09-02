from django.db import models
from django.contrib.auth.models import User
from .tournament import Tournament
from .season import Season
from .fanta_team import FantaTeam


class FantaLeague(models.Model):
    """
    Rappresenta una lega privata di Fantacalcio tra utenti.
    """
    name = models.CharField(max_length=100, help_text="Nome della lega")
    description = models.TextField(blank=True, help_text="Descrizione della lega")
    logo = models.ImageField(upload_to='fanta_leagues/', null=True, blank=True, help_text="Logo della lega")
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='administered_leagues', help_text="Amministratore della lega")
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='fanta_leagues', help_text="Stagione di riferimento")
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='fanta_leagues', help_text="Torneo di riferimento")
    teams = models.ManyToManyField(FantaTeam, related_name='leagues', help_text="Squadre partecipanti alla lega")
    is_private = models.BooleanField(default=True, help_text="Indica se la lega è privata (richiede invito)")
    invite_code = models.CharField(max_length=20, blank=True, null=True, help_text="Codice di invito per leghe private")
    max_teams = models.PositiveIntegerField(default=10, help_text="Numero massimo di squadre nella lega")
    initial_budget = models.IntegerField(default=500, help_text="Budget iniziale per ogni squadra in crediti")

    # Configurazioni asta
    auction_type = models.CharField(
        max_length=20,
        choices=[
            ('live', 'Asta Live'),
            ('silent', 'Asta Silenziosa'),
            ('auto', 'Asta Automatica')
        ],
        default='live',
        help_text="Tipo di asta"
    )
    auction_date = models.DateTimeField(null=True, blank=True, help_text="Data di inizio dell'asta")

    # Configurazioni punteggi
    scoring_system = models.CharField(
        max_length=20,
        choices=[
            ('classic', 'Classico'),
            ('bonus', 'Con Bonus/Malus'),
            ('custom', 'Personalizzato')
        ],
        default='classic',
        help_text="Sistema di punteggio"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lega Fantacalcio"
        verbose_name_plural = "Leghe Fantacalcio"
        unique_together = ('name', 'season', 'admin')

    def is_full(self):
        """Verifica se la lega ha raggiunto il numero massimo di squadre"""
        return self.teams.count() >= self.max_teams

    def __str__(self):
        return f"{self.name} ({self.season}) - Admin: {self.admin.username}"


class FantaLeagueRule(models.Model):
    """
    Regole personalizzate per una lega di Fantacalcio.
    """
    fanta_league = models.ForeignKey(FantaLeague, on_delete=models.CASCADE, related_name='rules')
    name = models.CharField(max_length=100, help_text="Nome della regola")
    description = models.TextField(help_text="Descrizione dettagliata della regola")

    # Regole di punteggio
    goal_value = models.FloatField(default=3.0, help_text="Punti per ogni gol")
    assist_value = models.FloatField(default=1.0, help_text="Punti per ogni assist")
    clean_sheet_value = models.FloatField(default=1.0, help_text="Punti per porta inviolata (difensori e portieri)")
    yellow_card_value = models.FloatField(default=-0.5, help_text="Punti per ammonizione")
    red_card_value = models.FloatField(default=-1.0, help_text="Punti per espulsione")
    goal_conceded_value = models.FloatField(default=-1.0, help_text="Punti per gol subito (portieri)")
    penalty_saved_value = models.FloatField(default=3.0, help_text="Punti per rigore parato")
    penalty_missed_value = models.FloatField(default=-3.0, help_text="Punti per rigore sbagliato")
    own_goal_value = models.FloatField(default=-2.0, help_text="Punti per autogol")

    # Regole di formazione
    formation_lock_time = models.IntegerField(default=10, help_text="Minuti prima del calcio d'inizio per bloccare le formazioni")
    max_players_same_team = models.PositiveIntegerField(default=5, help_text="Numero massimo di giocatori della stessa squadra")

    # Regole di mercato
    transfer_window_open = models.BooleanField(default=True, help_text="Indica se il mercato è aperto")
    max_transfers_per_week = models.PositiveIntegerField(default=3, help_text="Numero massimo di trasferimenti a settimana")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Regola Lega Fantacalcio"
        verbose_name_plural = "Regole Lega Fantacalcio"

    def __str__(self):
        return f"Regole per {self.fanta_league.name}"

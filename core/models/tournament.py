from django.db import models
from django.utils import timezone
from .tournament_structure import TournamentStructure
from .season import Season
from .season_team import SeasonTeam
from .trophy import Trophy


class Tournament(models.Model):
    """
    Rappresenta un torneo come Serie A, Coppa Italia, Champions League, ecc.
    Un torneo appartiene a una stagione e include squadre, struttura e regole.
    """
    # Dati base
    name = models.CharField(max_length=100, help_text="Nome del torneo (es. Serie A, Coppa Italia)")
    description = models.TextField(blank=True, help_text="Descrizione dettagliata del torneo")
    structure = models.ForeignKey(TournamentStructure, on_delete=models.PROTECT, help_text="Struttura del torneo (campionato, coppa, ecc.)")
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='tournaments', help_text="Stagione di appartenenza")
    parent_tournament = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child_tournaments',
                                          help_text="Torneo 'padre' (es. Serie B è parent di playoff Serie B)")

    # Squadre e partecipanti
    teams = models.ManyToManyField(SeasonTeam, related_name='tournaments', blank=True, help_text="Squadre partecipanti al torneo")
    max_teams = models.PositiveIntegerField(default=20, help_text="Numero massimo di squadre ammesse")
    min_teams = models.PositiveIntegerField(default=2, help_text="Numero minimo di squadre per avviare il torneo")

    # Stato corrente
    current_match_day = models.PositiveIntegerField(default=1, help_text="Giornata/turno corrente del torneo")
    is_active = models.BooleanField(default=True, help_text="Indica se il torneo è attivo")
    status = models.CharField(max_length=20, choices=[
        ('pending', 'In attesa di inizio'),
        ('active', 'In corso'),
        ('completed', 'Completato'),
        ('cancelled', 'Annullato')
    ], default='pending', help_text="Stato corrente del torneo")

    # Date e tempistiche
    start_date = models.DateField(null=True, blank=True, help_text="Data di inizio del torneo")
    end_date = models.DateField(null=True, blank=True, help_text="Data di fine del torneo")
    registration_deadline = models.DateField(null=True, blank=True, help_text="Scadenza per l'iscrizione")

    # Media e presentazione
    logo = models.ImageField(upload_to='tournaments/', null=True, blank=True, help_text="Logo del torneo")
    trophy = models.ForeignKey(Trophy, on_delete=models.SET_NULL, null=True, blank=True, related_name='tournaments', help_text="Trofeo assegnato al vincitore")

    # Metadati
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Torneo"
        verbose_name_plural = "Tornei"
        ordering = ['season__year', 'name']
        unique_together = ('name', 'season')

    def is_registration_open(self):
        """Verifica se le iscrizioni sono ancora aperte"""
        if not self.registration_deadline:
            return True
        return timezone.now().date() <= self.registration_deadline

    def get_winner(self):
        """Restituisce la squadra vincitrice del torneo, se disponibile"""
        if self.status == 'completed':
            from .tournament_ranking import TournamentRanking
            rankings = TournamentRanking.objects.filter(tournament=self).order_by('squad_ranking')
            if rankings.exists():
                return rankings.first().team
        return None

    def can_add_team(self):
        """Verifica se è possibile aggiungere altre squadre al torneo"""
        return (self.teams.count() < self.max_teams and
                self.is_registration_open() and
                self.status == 'pending')

    def __str__(self):
        status_label = {
            'pending': 'In attesa',
            'active': f'In corso (Giornata {self.current_match_day})',
            'completed': 'Completato',
            'cancelled': 'Annullato'
        }
        return f"{self.name} - {self.season.year} [{status_label.get(self.status, 'Sconosciuto')}]"

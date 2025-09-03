from django.db import models
from django.core.validators import MinValueValidator


class TournamentStructure(models.Model):
    """
    Definisce la struttura e le regole generali di un torneo.
    Es: campionato, coppa a eliminazione diretta, formato misto, ecc.
    """
    # Nome e tipo
    name = models.CharField(max_length=100, default="Standard", help_text="Nome della struttura (es. 'Campionato', 'Coppa')")

    # Formato base
    FORMAT_CHOICES = [
        ('league', 'Campionato'),
        ('cup', 'Coppa a eliminazione diretta'),
        ('group_stage', 'Fase a gironi'),
        ('hybrid', 'Formato misto')
    ]
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='league', help_text="Formato base del torneo")
    is_cup = models.BooleanField(default=False, help_text="Indica se è una competizione a eliminazione diretta")
    legs = models.PositiveSmallIntegerField(default=2, validators=[MinValueValidator(1)], help_text="Numero di partite per accoppiamento (1=solo andata, 2=andata e ritorno, ecc.)")

    # Fasi aggiuntive
    has_playoff = models.BooleanField(default=False, help_text="Indica se il torneo prevede playoff")
    has_playout = models.BooleanField(default=False, help_text="Indica se il torneo prevede playout")
    has_knockout_stage = models.BooleanField(default=False, help_text="Indica se il torneo ha una fase finale a eliminazione diretta")

    # Parametri di qualificazione
    relegation_enabled = models.BooleanField(default=False, help_text="Indica se sono previste retrocessioni")
    relegation_teams = models.PositiveIntegerField(default=0, help_text="Numero di squadre retrocesse direttamente")
    promotion_teams = models.PositiveIntegerField(default=0, help_text="Numero di squadre promosse direttamente")
    playoff_teams = models.PositiveIntegerField(default=0, help_text="Numero di squadre partecipanti ai playoff")
    playout_teams = models.PositiveIntegerField(default=0, help_text="Numero di squadre partecipanti ai playout")
    qualification_spots = models.PositiveIntegerField(default=0, help_text="Posti per qualificazione a competizioni esterne")

    # Regole personalizzate
    POINTS_WIN = models.PositiveSmallIntegerField(default=3, help_text="Punti per vittoria")
    POINTS_DRAW = models.PositiveSmallIntegerField(default=1, help_text="Punti per pareggio")
    POINTS_LOSS = models.PositiveSmallIntegerField(default=0, help_text="Punti per sconfitta")

    # Punti speciali per risultati dopo metodi di risoluzione pareggi
    POINTS_WIN_SHOOTOUT = models.PositiveSmallIntegerField(default=2, help_text="Punti per vittoria ai rigori")
    POINTS_LOSS_SHOOTOUT = models.PositiveSmallIntegerField(default=1, help_text="Punti per sconfitta ai rigori")
    POINTS_WIN_EXTRA_TIME = models.PositiveSmallIntegerField(default=3, help_text="Punti per vittoria ai tempi supplementari")
    POINTS_LOSS_EXTRA_TIME = models.PositiveSmallIntegerField(default=0, help_text="Punti per sconfitta ai tempi supplementari")

    # Regole per i pareggi
    allow_draws = models.BooleanField(default=True, help_text="Indica se sono consentiti pareggi nelle partite")
    DRAW_RESOLUTION_CHOICES = [
        ('penalties', 'Calci di rigore'),
        ('extra_time', 'Tempi supplementari'),
        ('extra_time_penalties', 'Tempi supplementari e rigori'),
        ('replay', 'Ripetizione della partita'),
        ('golden_goal', 'Golden goal')
    ]
    draw_resolution = models.CharField(
        max_length=20,
        choices=DRAW_RESOLUTION_CHOICES,
        default='penalties',
        help_text="Come risolvere i pareggi se non consentiti"
    )

    # Regole di spareggio
    HEAD_TO_HEAD_CHOICES = [
        ('none', 'Non utilizzato'),
        ('all', 'Scontri diretti (tutti)'),
        ('goals', 'Differenza reti scontri diretti'),
        ('away_goals', 'Gol in trasferta negli scontri diretti')
    ]
    tiebreaker_head_to_head = models.CharField(
        max_length=10,
        choices=HEAD_TO_HEAD_CHOICES,
        default='none',
        help_text="Criterio scontri diretti per spareggi"
    )
    tiebreaker_goal_difference = models.BooleanField(
        default=True,
        help_text="Usa differenza reti come criterio di spareggio"
    )
    tiebreaker_goals_scored = models.BooleanField(
        default=True,
        help_text="Usa gol segnati come criterio di spareggio"
    )
    tiebreaker_away_goals = models.BooleanField(
        default=False,
        help_text="Usa gol in trasferta come criterio di spareggio"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Struttura Torneo"
        verbose_name_plural = "Strutture Tornei"

    def __str__(self):
        format_name = self.get_format_display()
        details = []

        if self.format == 'group_stage' or self.format == 'hybrid':
            details.append("con gironi")

        if self.legs > 1:
            details.append(f"andata/ritorno ({self.legs} partite)")
        else:
            details.append("partita singola")

        if not self.allow_draws:
            resolution_display = dict(self.DRAW_RESOLUTION_CHOICES).get(self.draw_resolution)
            details.append(f"no pareggi ({resolution_display})")

        if self.has_playoff:
            details.append("con playoff")

        if self.has_knockout_stage:
            details.append("con fase a eliminazione")

        details_str = ", ".join(details)
        return f"{self.name}: {format_name} ({details_str})"

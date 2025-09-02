from django.db import models


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
    use_groups = models.BooleanField(default=False, help_text="Indica se il torneo usa una fase a gironi")
    home_and_away = models.BooleanField(default=True, help_text="Indica se le partite si giocano andata e ritorno")
    legs = models.PositiveSmallIntegerField(default=2, help_text="Numero di partite per accoppiamento (1=solo andata, 2=andata e ritorno)")

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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Struttura Torneo"
        verbose_name_plural = "Strutture Tornei"

    def __str__(self):
        format_name = self.get_format_display()
        details = []

        if self.use_groups:
            details.append("con gironi")

        if self.home_and_away:
            details.append("andata/ritorno")
        else:
            details.append("partita singola")

        if self.has_playoff:
            details.append("con playoff")

        if self.has_knockout_stage:
            details.append("con fase a eliminazione")

        details_str = ", ".join(details)
        return f"{self.name}: {format_name} ({details_str})"

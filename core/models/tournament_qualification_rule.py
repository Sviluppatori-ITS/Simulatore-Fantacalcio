from django.db import models
from .tournament import Tournament


class TournamentQualificationRule(models.Model):
    """
    Regola che definisce come le squadre si qualificano da un torneo a un altro.
    Ad esempio: le prime 3 della Serie B vengono promosse in Serie A.
    """
    from_tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='qualification_rules',
                                        help_text="Torneo di origine")
    to_tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='qualified_from',
                                      help_text="Torneo di destinazione")

    # Range di posizioni per la qualificazione
    min_rank = models.PositiveIntegerField(help_text="Posizione minima per la qualificazione (es. 1)")
    max_rank = models.PositiveIntegerField(help_text="Posizione massima per la qualificazione (es. 4)")

    # Tipo di qualificazione
    QUALIFICATION_TYPE_CHOICES = [
        ('promotion', 'Promozione'),
        ('relegation', 'Retrocessione'),
        ('qualification', 'Qualificazione'),
        ('playoff', 'Playoff'),
        ('playout', 'Playout')
    ]
    qualification_type = models.CharField(max_length=20, choices=QUALIFICATION_TYPE_CHOICES, default='qualification',
                                          help_text="Tipo di qualificazione")

    # Opzioni avanzate
    group = models.CharField(max_length=50, blank=True, help_text="Gruppo specifico (se il torneo ha gironi)")
    description = models.CharField(max_length=255, blank=True, help_text="Descrizione della regola")
    season_offset = models.IntegerField(default=0, help_text="Offset stagione (0=stessa stagione, 1=stagione successiva)")
    is_active = models.BooleanField(default=True, help_text="Indica se la regola è attiva")

    class Meta:
        verbose_name = "Regola di Qualificazione"
        verbose_name_plural = "Regole di Qualificazione"
        ordering = ['from_tournament', 'min_rank']

    def apply_rule(self):
        """
        Applica la regola di qualificazione, aggiornando lo stato delle squadre nella classifica.
        """
        from .tournament_ranking import TournamentRanking

        # Ottieni le classifiche del torneo di origine
        rankings = TournamentRanking.objects.filter(tournament=self.from_tournament)

        # Se specificato un gruppo, filtra per quel gruppo
        if self.group:
            rankings = rankings.filter(group=self.group)

        # Ordina per punti (decrescente)
        rankings = list(rankings)
        rankings.sort(key=lambda r: (-r.points, -r.win, -(r.goals_for - r.goals_against)))

        # Identifica le squadre che rientrano nel range di qualificazione
        qualified_teams = []
        for position, ranking in enumerate(rankings, start=1):
            if self.min_rank <= position <= self.max_rank:
                qualified_teams.append(ranking.team)

                # Aggiorna lo stato di qualificazione o retrocessione
                if self.qualification_type in ['promotion', 'qualification', 'playoff']:
                    ranking.qualified = True
                    ranking.save(update_fields=['qualified'])
                elif self.qualification_type in ['relegation', 'playout']:
                    ranking.relegated = True
                    ranking.save(update_fields=['relegated'])

        return qualified_teams

    def __str__(self):
        qualification_type_labels = {
            'promotion': 'Promozione',
            'relegation': 'Retrocessione',
            'qualification': 'Qualificazione',
            'playoff': 'Playoff',
            'playout': 'Playout'
        }

        type_label = qualification_type_labels.get(self.qualification_type, self.qualification_type)
        group_str = f" (Girone {self.group})" if self.group else ""

        return f"{type_label}: {self.from_tournament.name}{group_str} [{self.min_rank}-{self.max_rank}] → {self.to_tournament.name}"

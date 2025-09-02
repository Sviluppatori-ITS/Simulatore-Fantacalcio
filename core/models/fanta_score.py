from django.db import models
from .player import Player
from .match import Match
from .round import Round


class FantaScore(models.Model):
    """
    Rappresenta il voto di un giocatore in una specifica partita, con i relativi bonus/malus.
    """
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='fanta_scores')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='player_scores')
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='player_scores')

    # Voto base e minutaggio
    vote = models.FloatField(null=True, blank=True, help_text="Voto base del giocatore (senza bonus/malus)")
    minutes_played = models.PositiveIntegerField(default=0, help_text="Minuti giocati")
    entered_at = models.PositiveIntegerField(null=True, blank=True, help_text="Minuto di ingresso")
    exited_at = models.PositiveIntegerField(null=True, blank=True, help_text="Minuto di uscita")

    # Eventi positivi
    goals = models.PositiveIntegerField(default=0, help_text="Gol segnati")
    assists = models.PositiveIntegerField(default=0, help_text="Assist effettuati")
    penalties_scored = models.PositiveIntegerField(default=0, help_text="Rigori segnati")
    penalties_saved = models.PositiveIntegerField(default=0, help_text="Rigori parati (portieri)")
    clean_sheet = models.BooleanField(default=False, help_text="Porta inviolata (portieri e difensori)")

    # Eventi negativi
    yellow_cards = models.PositiveIntegerField(default=0, help_text="Cartellini gialli")
    red_cards = models.PositiveIntegerField(default=0, help_text="Cartellini rossi")
    own_goals = models.PositiveIntegerField(default=0, help_text="Autogol")
    penalties_missed = models.PositiveIntegerField(default=0, help_text="Rigori sbagliati")
    goals_conceded = models.PositiveIntegerField(default=0, help_text="Gol subiti (portieri)")

    # Campi aggiuntivi per statistiche avanzate
    shots = models.PositiveIntegerField(default=0, help_text="Tiri effettuati")
    shots_on_target = models.PositiveIntegerField(default=0, help_text="Tiri in porta")
    key_passes = models.PositiveIntegerField(default=0, help_text="Passaggi chiave")
    accurate_passes = models.PositiveIntegerField(default=0, help_text="Passaggi precisi")
    tackles = models.PositiveIntegerField(default=0, help_text="Tackle effettuati")
    interceptions = models.PositiveIntegerField(default=0, help_text="Intercetti")
    saves = models.PositiveIntegerField(default=0, help_text="Parate (portieri)")

    # Punteggio finale
    final_score = models.FloatField(default=0.0, help_text="Punteggio finale (voto + bonus/malus)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Voto Fantacalcio"
        verbose_name_plural = "Voti Fantacalcio"
        unique_together = ('player', 'match')
        ordering = ['-round__number', '-final_score']

    def calculate_final_score(self):
        """
        Calcola il punteggio finale basato sul voto e i bonus/malus
        """
        if self.vote is None:
            # Se il giocatore non è stato votato (SV)
            if self.minutes_played < 15:
                # Meno di 15 minuti, non considerato
                self.final_score = 0
                return self.final_score
            else:
                # Altrimenti voto d'ufficio 6
                base_score = 6.0
        else:
            base_score = self.vote

        # Calcola bonus
        bonus = (
            (3.0 * self.goals) +
            (1.0 * self.assists) +
            (2.0 * self.penalties_scored) +
            (3.0 * self.penalties_saved)
        )

        # Calcola malus
        malus = (
            (-0.5 * self.yellow_cards) +
            (-1.0 * self.red_cards) +
            (-2.0 * self.own_goals) +
            (-3.0 * self.penalties_missed)
        )

        # Per i portieri: -1 punto per ogni gol subito
        if self.player.main_role == 'P':
            malus += (-1.0 * self.goals_conceded)

            # Bonus porta inviolata per portieri
            if self.clean_sheet:
                bonus += 1.0

        # Bonus porta inviolata per difensori
        elif self.player.main_role == 'D' and self.clean_sheet:
            bonus += 1.0

        # Calcola punteggio finale
        self.final_score = round(base_score + bonus + malus, 2)
        self.save()

        return self.final_score

    def __str__(self):
        return f"Voto {self.player.person.surname} - Giornata {self.round.number}: {self.final_score}"

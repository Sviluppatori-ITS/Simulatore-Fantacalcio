from django.db import models
from .fanta_team import FantaTeam
from .player import Player
from .tournament import Tournament
from .round import Round


class FantaLineup(models.Model):
    """
    Rappresenta la formazione schierata da un utente per una giornata specifica.
    """
    fanta_team = models.ForeignKey(FantaTeam, on_delete=models.CASCADE, related_name='lineups')
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='lineups', help_text="Giornata di riferimento")
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='lineups')
    formation = models.CharField(max_length=10, help_text="Schema tattico (es. 4-3-3, 3-5-2)")
    is_submitted = models.BooleanField(default=False, help_text="Indica se la formazione è stata confermata")
    submission_time = models.DateTimeField(null=True, blank=True, help_text="Orario di invio della formazione")
    total_score = models.FloatField(default=0.0, help_text="Punteggio totale della formazione")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Formazione Fantacalcio"
        verbose_name_plural = "Formazioni Fantacalcio"
        unique_together = ('fanta_team', 'round')

    def calculate_score(self):
        """Calcola il punteggio totale della formazione basato sui voti dei giocatori titolari e subentrati"""
        lineup_players = self.players.filter(is_starter=True)
        substitutions = self.substitutions.all()

        # Calcola punteggio iniziale dai titolari
        score = sum(lp.get_final_score() for lp in lineup_players)

        # Aggiungi punteggio dalle sostituzioni effettive
        for sub in substitutions:
            if sub.is_applied:
                score += sub.substitute.get_final_score()
                score -= sub.player_out.get_final_score()  # Sottrai il punteggio del giocatore sostituito

        self.total_score = round(score, 2)
        self.save()
        return self.total_score

    def __str__(self):
        return f"Formazione di {self.fanta_team.name} - Giornata {self.round.number} ({self.formation})"


class FantaLineupPlayer(models.Model):
    """
    Rappresenta un giocatore in una formazione di Fantacalcio.
    """
    fanta_lineup = models.ForeignKey(FantaLineup, on_delete=models.CASCADE, related_name='players')
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    position = models.PositiveSmallIntegerField(help_text="Posizione nella formazione (1-11 titolari, 12+ riserve)")
    is_starter = models.BooleanField(default=False, help_text="Indica se il giocatore è titolare")
    is_captain = models.BooleanField(default=False, help_text="Indica se il giocatore è capitano")
    is_vice_captain = models.BooleanField(default=False, help_text="Indica se il giocatore è vice-capitano")
    score = models.FloatField(null=True, blank=True, help_text="Voto base")
    bonus_points = models.FloatField(default=0.0, help_text="Punti bonus/malus complessivi")

    class Meta:
        verbose_name = "Giocatore in Formazione"
        verbose_name_plural = "Giocatori in Formazione"
        unique_together = ('fanta_lineup', 'player')
        ordering = ['position']

    def get_final_score(self):
        """Calcola il punteggio finale del giocatore (voto + bonus)"""
        if self.score is None:
            return 0

        final_score = self.score + self.bonus_points

        # Applica bonus capitano se necessario
        if self.is_captain:
            # Bonus capitano (esempio: 10% in più)
            captain_bonus = 0.1 * final_score
            final_score += captain_bonus

        return round(final_score, 2)

    def __str__(self):
        position_str = "Titolare" if self.is_starter else "Riserva"
        captain_str = " (C)" if self.is_captain else " (VC)" if self.is_vice_captain else ""
        return f"{self.player.person.surname} - {position_str}{captain_str}"


class FantaLineupSubstitution(models.Model):
    """
    Rappresenta una sostituzione automatica effettuata durante l'applicazione dei voti.
    """
    fanta_lineup = models.ForeignKey(FantaLineup, on_delete=models.CASCADE, related_name='substitutions')
    player_out = models.ForeignKey(FantaLineupPlayer, on_delete=models.CASCADE, related_name='substitutions_out')
    substitute = models.ForeignKey(FantaLineupPlayer, on_delete=models.CASCADE, related_name='substitutions_in')
    reason = models.CharField(max_length=100, help_text="Motivazione della sostituzione")
    is_applied = models.BooleanField(default=False, help_text="Indica se la sostituzione è stata applicata")

    class Meta:
        verbose_name = "Sostituzione"
        verbose_name_plural = "Sostituzioni"

    def __str__(self):
        return f"Sostituzione: {self.player_out.player.person.surname} OUT, {self.substitute.player.person.surname} IN"

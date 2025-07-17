from django.db import models
from .tournament import Tournament
from .season_team import SeasonTeam


class TournamentRanking(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='tournament_rankings')
    team = models.ForeignKey(SeasonTeam, on_delete=models.CASCADE, related_name='team_tournament_rankings')
    win = models.PositiveIntegerField(default=0, help_text="Numero di vittorie")
    draw = models.PositiveIntegerField(default=0, help_text="Numero di pareggi")
    loss = models.PositiveIntegerField(default=0, help_text="Numero di sconfitte")
    win_penalty = models.PositiveIntegerField(default=0, help_text="Numero di vittorie ai rigori")
    loss_penalty = models.PositiveIntegerField(default=0, help_text="Numero di sconfitte ai rigori")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('tournament', 'team')

    def total_points(self):
        # Calcola i punti totali in base alle regole del torneo
        points = 0
        rules = self.tournament.rules.filter(is_active=True)

        for rule in rules:
            if rule.rule_type == 'point_win':
                points += self.win * rule.value
            elif rule.rule_type == 'point_draw':
                points += self.draw * rule.value
            elif rule.rule_type == 'point_loss':
                points += self.loss * rule.value
            elif rule.rule_type == 'win_penalty':
                points += self.win_penalty * rule.value
            elif rule.rule_type == 'loss_penalty':
                points -= self.loss_penalty * rule.value

        return points

    def matches_played(self):
        # Calcola il numero di partite giocate dalla squadra nel torneo
        return self.win + self.draw + self.loss + self.win_penalty + self.loss_penalty

    def squad_points(self):
        # Calcola i punti totali della squadra nel torneo
        return self.total_points()

    def squad_goals(self):
        # Calcola i gol totali della squadra nel torneo
        performances = self.team.roster.all()
        total_goals = 0
        for performance in performances:
            total_goals += performance.player.simulatedperformance_set.aggregate(models.Sum('goals'))['goals__sum'] or 0
        return total_goals

    def squad_goals_against(self):
        # Calcola i gol subiti dalla squadra nel torneo
        performances = self.team.roster.all()
        total_goals_against = 0
        for performance in performances:
            total_goals_against += performance.player.simulatedperformance_set.aggregate(models.Sum('goals_against'))['goals_against__sum'] or 0
        return total_goals_against

    def squad_goal_difference(self):
        # Calcola la differenza reti della squadra nel torneo
        return self.squad_goals() - self.squad_goals_against()

    # def squad_ranking(self):
    #     # Calcola la posizione della squadra nella classifica del torneo
    #     rankings = TournamentRanking.objects.filter(tournament=self.tournament).order_by('-total_points', 'team__team__name')
    #     for index, ranking in enumerate(rankings, start=1):
    #         if ranking.team == self.team:
    #             return index
    #     return None

    def squad_ranking(self):
        # Calcola la posizione della squadra nella classifica del torneo
        rankings = list(TournamentRanking.objects.filter(tournament=self.tournament))

        # Ordina manualmente in Python, poiché total_points è un metodo
        rankings.sort(key=lambda r: (-r.total_points(), r.team.team.name))

        for index, ranking in enumerate(rankings, start=1):
            if ranking.team == self.team:
                return index
        return None

    def tourbament_ranking(self):
        # Calcola la classifica completa del torneo
        rankings = TournamentRanking.objects.filter(tournament=self.tournament).order_by('-total_points', 'team__team__name')
        return [(ranking.team.team.name, ranking.total_points(), ranking.squad_ranking()) for ranking in rankings]

    def __str__(self):
        return f"{self.team.team.name} - {self.tournament.name}"

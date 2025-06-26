from core.models import Tournament, Match, Giornata, Team
from django.db import transaction
import random
from itertools import combinations, permutations


class TournamentFactory:

    def __init__(self, structure, season, name, teams, description=""):
        self.structure = structure
        self.season = season
        self.name = name
        self.teams = list(teams)
        self.description = description

    @transaction.atomic
    def create(self):
        tournament = Tournament.objects.create(
            name=self.name,
            description=self.description,
            structure=self.structure,
            season=self.season,
        )
        tournament.teams.set(self.teams)

        if self.structure.is_cup:
            self._generate_knockout(tournament)
        else:
            self._generate_league(tournament)

        return tournament

    def _generate_league(self, tournament):
        matchups = list(combinations(self.teams, 2))
        if self.structure.home_and_away:
            matchups += [(away, home) for home, away in matchups]

        giornata_counter = 1
        random.shuffle(matchups)

        giornate = []
        for i in range(0, len(matchups), len(self.teams) // 2):
            giornate.append(matchups[i:i + len(self.teams) // 2])

        for matches in giornate:
            g = Giornata.objects.create(
                tournament=tournament,
                match_day=giornata_counter
            )
            for home, away in matches:
                match = Match.objects.create(
                    home_team=home,
                    away_team=away,
                    tournament=tournament
                )
                g.matches.add(match)
            giornata_counter += 1

    def _generate_knockout(self, tournament):
        round_num = 1
        current_teams = self.teams.copy()
        random.shuffle(current_teams)

        while len(current_teams) >= 2:
            g = Giornata.objects.create(
                tournament=tournament,
                match_day=round_num,
                label=self._round_label(len(current_teams)),
                knockout_stage=True
            )
            next_round = []

            for i in range(0, len(current_teams), 2):
                if i + 1 >= len(current_teams):
                    # dispari, passaggio automatico
                    next_round.append(current_teams[i])
                    continue
                home, away = current_teams[i], current_teams[i + 1]
                Match.objects.create(
                    home_team=home,
                    away_team=away,
                    tournament=tournament
                ).giornate.add(g)
                # Placeholder: vincitore scelto a caso
                next_round.append(random.choice([home, away]))

            current_teams = next_round
            round_num += 1

    def _round_label(self, n):
        if n == 2:
            return "Finale"
        elif n == 4:
            return "Semifinali"
        elif n == 8:
            return "Quarti di finale"
        elif n == 16:
            return "Ottavi di finale"
        elif n == 32:
            return "Sedicesimi di finale"
        elif n == 64:
            return "Trentaduesimi di finale"
        elif n == 128:
            return "Sessantaquattresimi di finale"
        return f"Turno a {n}"

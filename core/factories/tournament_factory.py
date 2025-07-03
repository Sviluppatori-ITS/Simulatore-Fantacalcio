"""
from core.models import Tournament, Match, Round, Team
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
            g = Round.objects.create(
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
            g = Round.objects.create(
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
"""

from core.models import Tournament, Match, Round, Team
from django.db import transaction
import random
from itertools import combinations
import logging
import inspect
import os
from core.logger import get_logger
import math


class TournamentFactory:
    def __init__(self, structure, season, name, teams, description=""):
        self.logger = get_logger()
        if not structure:
            self.logger.error("Devi fornire una struttura torneo valida")
            raise ValueError("Devi fornire una struttura torneo valida")
        if not season:
            self.logger.error("Devi fornire una stagione valida")
            raise ValueError("Devi fornire una stagione valida")
        if not name:
            self.logger.error("Devi fornire un nome torneo")
            raise ValueError("Devi fornire un nome torneo")
        if not teams or len(teams) < 2:
            self.logger.error("Devi fornire almeno 2 squadre")
            raise ValueError("Devi fornire almeno 2 squadre")

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
        self.logger.info(f"Torneo '{self.name}' creato con {len(self.teams)} squadre.")

        if self.structure.is_cup:
            self._generate_knockout(tournament)
        else:
            self._generate_league(tournament)

        return tournament

    def _generate_league(self, tournament):
        matchups = list(combinations(self.teams, 2))

        if self.structure.home_and_away:
            matchups += [(away, home) for home, away in matchups]

        random.shuffle(matchups)
        matches_per_round = len(self.teams) // 2
        giornate = [matchups[i:i + matches_per_round] for i in range(0, len(matchups), matches_per_round)]

        giornata_counter = 1
        for matches in giornate:
            round_obj = Round.objects.create(
                tournament=tournament,
                match_day=giornata_counter
            )
            self.logger.info(f"Creata giornata {giornata_counter} con {len(matches)} partite.")
            for home, away in matches:
                match = Match.objects.create(
                    home_team=home,
                    away_team=away,
                    tournament=tournament
                )
                round_obj.matches.add(match)
            giornata_counter += 1

    import math

    def _generate_knockout(self, tournament):
        round_num = 1
        current_teams = self.teams.copy()
        random.shuffle(current_teams)

        while len(current_teams) > 1:
            num_teams = len(current_teams)
            power = 2 ** math.floor(math.log2(num_teams))
            matches_to_play = (num_teams - power)  # Numero di match da giocare in questo turno
            teams_in_match = matches_to_play * 2

            # Se il numero è già una potenza di 2, fai tutte le partite
            if matches_to_play == 0:
                teams_in_match = num_teams

            round_obj = Round.objects.create(
                tournament=tournament,
                match_day=round_num,
                label=self._round_label(num_teams),
                knockout_stage=True
            )
            self.logger.info(f"Creata fase '{round_obj.label}' (round {round_num}) con {num_teams} squadre.")

            next_round_teams = []

            playing = current_teams[:teams_in_match]
            advancing = current_teams[teams_in_match:]  # squadre che passano senza giocare

            for i in range(0, len(playing), 2):
                home, away = playing[i], playing[i + 1]
                match = Match.objects.create(
                    home_team=home,
                    away_team=away,
                    tournament=tournament
                )
                round_obj.matches.add(match)

                winner = random.choice([home, away])
                next_round_teams.append(winner)
                self.logger.info(f"Match {home} vs {away} -> vincitore (casuale): {winner}")

            for team in advancing:
                self.logger.info(f"Squadra {team} passa turno per sorteggio (numero dispari).")
                next_round_teams.append(team)

            current_teams = next_round_teams
            round_num += 1

    def _round_label(self, n):
        labels = {
            2: "Finale",
            4: "Semifinali",
            8: "Quarti di finale",
            16: "Ottavi di finale",
            32: "Sedicesimi di finale",
            64: "Trentaduesimi di finale",
            128: "Sessantaquattresimi di finale"
        }
        return labels.get(n, f"Turno a {n}")

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


class TournamentFactory:
    def __init__(self, structure, season, name, teams, description=""):
        if not structure:
            raise ValueError("Devi fornire una struttura torneo valida")
        if not season:
            raise ValueError("Devi fornire una stagione valida")
        if not name:
            raise ValueError("Devi fornire un nome torneo")
        if not teams or len(teams) < 2:
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
        print(f"Torneo '{self.name}' creato con {len(self.teams)} squadre.")

        if self.structure.is_cup:
            self._generate_knockout(tournament)
        else:
            self._generate_league(tournament)

        return tournament

    def _generate_league(self, tournament):
        # Partite tutte contro tutte
        matchups = list(combinations(self.teams, 2))

        if self.structure.home_and_away:
            matchups += [(away, home) for home, away in matchups]

        random.shuffle(matchups)

        # Calcolo numero partite per giornata (metà squadre per giornata)
        matches_per_round = len(self.teams) // 2
        giornate = [matchups[i:i + matches_per_round] for i in range(0, len(matchups), matches_per_round)]

        giornata_counter = 1
        for matches in giornate:
            round_obj = Round.objects.create(
                tournament=tournament,
                match_day=giornata_counter
            )
            print(f"Creata giornata {giornata_counter} con {len(matches)} partite.")
            for home, away in matches:
                match = Match.objects.create(
                    home_team=home,
                    away_team=away,
                    tournament=tournament
                )
                round_obj.matches.add(match)
            giornata_counter += 1

    def _generate_knockout(self, tournament):
        round_num = 1
        current_teams = self.teams.copy()
        random.shuffle(current_teams)

        while len(current_teams) > 1:
            round_obj = Round.objects.create(
                tournament=tournament,
                match_day=round_num,
                label=self._round_label(len(current_teams)),
                knockout_stage=True
            )
            print(f"Creata fase '{round_obj.label}' (round {round_num}) con {len(current_teams)} squadre.")
            next_round_teams = []

            # Gestione squadre a coppie, eventuale passaggio turno per dispari
            for i in range(0, len(current_teams), 2):
                if i + 1 >= len(current_teams):
                    # Squadra con bye (passaggio turno)
                    bye_team = current_teams[i]
                    print(f"Squadra {bye_team} passa turno per numero dispari.")
                    next_round_teams.append(bye_team)
                    continue

                home, away = current_teams[i], current_teams[i + 1]
                match = Match.objects.create(
                    home_team=home,
                    away_team=away,
                    tournament=tournament
                )
                round_obj.matches.add(match)

                # Sceglie casualmente un vincitore (placeholder)
                winner = random.choice([home, away])
                next_round_teams.append(winner)
                print(f"Match {home} vs {away} -> vincitore (casuale): {winner}")

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

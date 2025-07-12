from core.models import Tournament, Match, Round, Team, TournamentStructure, Season, TournamentQualificationRule, TournamentRule
from django.db import transaction
import random
from itertools import combinations
import math
from core.logger import get_logger
from core.services.standings import get_tournament_standings


class TournamentFactory:
    def __init__(self, structure, season, name, teams, description="", tournament_direct_qualification_rule=None, tournament_playoff_qualification_rule=None, other_tournament=None):
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
        if Tournament.objects.filter(name=name, season=season).exists():
            self.logger.error(f"Torneo '{name}' già esistente per la stagione {season.year}")
            raise ValueError(f"Torneo '{name}' già esistente per la stagione {season.year}")
        if not teams or len(teams) < 2:
            self.logger.error("Devi fornire almeno 2 squadre")
            raise ValueError("Devi fornire almeno 2 squadre")
        if not structure.is_cup and structure.has_playoff and tournament_playoff_qualification_rule is None:
            self.logger.error("Devi fornire una regola di qualificazione per i playoff")
            raise ValueError("Devi fornire una regola di qualificazione per i playoff")
        if not structure.is_cup and structure.relegation_enabled and structure.relegation_teams < 1:
            self.logger.error("Devi fornire almeno 1 squadra per la retrocessione")
            raise ValueError("Devi fornire almeno 1 squadra per la retrocessione")
        if not structure.is_cup and structure.relegation_enabled and not structure.relegation_enabled:
            if structure.relegation_teams < (tournament_direct_qualification_rule.max_rank - tournament_direct_qualification_rule.min_rank + 1):
                self.logger.error("Il numero di squadre per la retrocessione deve essere minore o uguale al numero di squadre promosse")
                raise ValueError("Il numero di squadre per la retrocessione deve essere minore o uguale al numero di squadre promosse")
        if not structure.is_cup and structure.relegation_enabled and structure.has_playoff:
            if structure.relegation_teams < (tournament_direct_qualification_rule.max_rank - tournament_direct_qualification_rule.min_rank + 2):
                self.logger.error("Il numero di squadre per la retrocessione deve essere minore o uguale al numero di squadre promosse")
                raise ValueError("Il numero di squadre per la retrocessione deve essere minore o uguale al numero di squadre promosse")

        self.structure = structure
        self.season = season
        self.name = name
        self.teams = list(teams)
        self.description = description
        self.tournament_direct_qualification_rule = tournament_direct_qualification_rule
        self.tournament_playoff_qualification_rule = tournament_playoff_qualification_rule
        self.other_tournament = other_tournament
        self.logger.info(f"Inizializzato TournamentFactory per '{self.name}' ({self.structure}) con {len(self.teams)} squadre.")

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

        if self.structure.relegation_enabled:
            if self.tournament_playoff_qualification_rule not in [None, ""]:
                self.logger.info("Generazione regole di qualificazione per il torneo di promozione e retrocessione.")
                tournament_direct_qualification_rule = TournamentQualificationRule.objects.create(
                    from_tournament=tournament,
                    to_tournament=self.other_tournament,
                    min_rank=self.tournament_direct_qualification_rule.min_rank,
                    max_rank=self.tournament_direct_qualification_rule.max_rank,
                )
                self.logger.info(f"Regola di qualificazione diretta creata: {tournament_direct_qualification_rule}")
                if self.structure.has_playoff:
                    play_off = self._generate_playoff(tournament)

                    tournament_playoff_qualification_rule = TournamentQualificationRule.objects.create(
                        from_tournament=tournament,
                        to_tournament=play_off,
                        min_rank=self.tournament_playoff_qualification_rule.min_rank,
                        max_rank=self.tournament_playoff_qualification_rule.max_rank,
                    )

                    tournament_playoff_winner_qualification_rule = TournamentQualificationRule.objects.create(
                        from_tournament=play_off,
                        to_tournament=self.other_tournament,
                        min_rank=1,
                        max_rank=1,
                    )

                    self.logger.info(f"Regola di qualificazione playoff creata: {tournament_playoff_qualification_rule}")

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

    def _generate_knockout(self, tournament):
        round_num = 1
        current_teams = self.teams.copy()
        random.shuffle(current_teams)

        while len(current_teams) > 1:
            num_teams = len(current_teams)
            power = 2 ** math.floor(math.log2(num_teams))
            matches_to_play = (num_teams - power)  # Numero di match da giocare in questo turno
            teams_in_match = matches_to_play * 2

            if matches_to_play == 0:
                teams_in_match = num_teams

            round_obj = Round.objects.create(
                tournament=tournament,
                match_day=round_num,
                label=self._round_label(num_teams),
                knockout_stage=True
            )
            self.logger.info(f"Creata fase '{round_obj.label}' (round {round_num}) con {num_teams} squadre.")

            playing = current_teams[:teams_in_match]
            advancing = current_teams[teams_in_match:]  # squadre che passano turno senza giocare

            for i in range(0, len(playing), 2):
                home, away = playing[i], playing[i + 1]
                match = Match.objects.create(
                    home_team=home,
                    away_team=away,
                    tournament=tournament
                )
                round_obj.matches.add(match)

            # Squadre che passano turno senza giocare restano nella lista corrente
            current_teams = advancing + playing  # Nota: senza decidere vincitori

            round_num += 1

            # Qui non si simulano risultati, quindi non possiamo "avanzare" realmente squadre
            # La logica per avanzare squadre va fatta con i risultati delle partite

            break  # creiamo solo il primo turno

    # def _generate_playoff(self, tournament):
    #     playoff_teams_count = self.structure.playoff_teams
    #     if playoff_teams_count < 2:
    #         self.logger.warning("Numero insufficiente di squadre per playoff.")
    #         return

    #     standings = get_tournament_standings(tournament)
    #     teams_ranked = [team for team, data in standings][:playoff_teams_count]

    #     round_num = 100
    #     round_label = self._round_label(len(teams_ranked))
    #     round_obj = Round.objects.create(
    #         tournament=tournament,
    #         match_day=round_num,
    #         label=f"Playoff - {round_label}",
    #         knockout_stage=True
    #     )

    #     for i in range(0, len(teams_ranked), 2):
    #         home, away = teams_ranked[i], teams_ranked[i + 1]
    #         match = Match.objects.create(
    #             home_team=home,
    #             away_team=away,
    #             tournament=tournament
    #         )
    #         round_obj.matches.add(match)

    #     self.logger.info(f"Creato primo turno playoff con {len(teams_ranked)} squadre.")

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

    def _generate_playoff(self, tournament):
        # Prendi tutte le regole di qualificazione per questo torneo
        qualification_rules = tournament.qualification_rules.all()

        if not qualification_rules.exists():
            self.logger.warning("Nessuna regola di qualificazione trovata, impossibile generare playoff.")
            return

        # Ottieni la classifica aggiornata
        standings = get_tournament_standings(tournament)

        # Costruisci la lista delle squadre qualificate in base alle regole
        qualified_teams = []
        for rule in qualification_rules:
            # Estrai le squadre che si trovano nel range indicato dalla regola
            teams_in_range = [
                team for pos, (team, _) in enumerate(standings, start=1)
                if rule.min_rank <= pos <= rule.max_rank
            ]
            qualified_teams.extend(teams_in_range)

        # Evita duplicati
        qualified_teams = list(dict.fromkeys(qualified_teams))

        if len(qualified_teams) < 2:
            self.logger.warning("Numero insufficiente di squadre qualificate per playoff.")
            return

        round_num = 100  # Deve essere più alto rispetto ai turni della regular season
        current_teams = qualified_teams
        self.logger.info(f"Generazione playoff con {len(current_teams)} squadre")

        # Per ora creiamo solo il primo turno playoff, i turni successivi si creeranno dopo con i risultati
        round_label = self._round_label(len(current_teams))
        round_obj = Round.objects.create(
            tournament=tournament,
            match_day=round_num,
            label=f"Playoff - {round_label}",
            knockout_stage=True
        )

        for i in range(0, len(current_teams), 2):
            home, away = current_teams[i], current_teams[i + 1]
            match = Match.objects.create(
                home_team=home,
                away_team=away,
                tournament=tournament
            )
            round_obj.matches.add(match)

        self.logger.info(f"Primo turno playoff creato con {len(current_teams) // 2} partite.")

        # Non creiamo turni successivi qui: li gestirai dopo in base ai risultati
        return round_obj

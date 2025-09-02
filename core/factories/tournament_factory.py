import math
import random
from datetime import timedelta
from itertools import combinations
from typing import List, Dict, Any, Optional, Tuple, Union

from django.db import transaction
from django.utils import timezone

from core.logger import get_logger
from core.models import (Match, Round, Season, Team, SeasonTeam, Tournament,
                         TournamentQualificationRule, TournamentRule,
                         TournamentRanking, TournamentStructure)
from core.services.standings import get_tournament_standings


class TournamentFactory:
    """
    Factory per la creazione di tornei e campionati.
    Gestisce la creazione della struttura del torneo, delle giornate/turni, e delle partite.
    """

    def __init__(
        self,
        structure: TournamentStructure,
        season: Season,
        name: str,
        teams: List[Team],
        description: str = "",
        start_date=None,
        parent_tournament=None,
        qualification_rules: Dict = None,
        tournament_direct_qualification_rule=None,
        tournament_playoff_qualification_rule=None,
        other_tournament=None
    ):
        self.logger = get_logger()
        # Aggiungiamo il metodo di validazione input
        self._validate_inputs(structure, season, name, teams, tournament_direct_qualification_rule, tournament_playoff_qualification_rule)

        self.structure = structure
        self.season = season
        self.name = name
        self.teams = list(teams)
        self.description = description
        self.parent_tournament = parent_tournament
        self.start_date = start_date
        self.qualification_rules = qualification_rules or {}

        # Parametri per retrocompatibilità
        self.tournament_direct_qualification_rule = tournament_direct_qualification_rule
        self.tournament_playoff_qualification_rule = tournament_playoff_qualification_rule
        self.other_tournament = other_tournament

        self.logger.info(f"Inizializzato TournamentFactory per '{self.name}' ({self.structure}) con {len(self.teams)} squadre.")

    def _validate_inputs(self, structure, season, name, teams, tournament_direct_qualification_rule, tournament_playoff_qualification_rule):
        """Validazione degli input per la creazione di un torneo"""
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

        # Commento: la validazione per la retrocessione verrà gestita separatamente
        # quando le regole di retrocessione sono effettivamente fornite

        # Commento: la validazione per la relazione tra retrocessione e promozione diretta
        # verrà gestita quando vengono fornite le regole specifiche

        # Commento: la validazione per la relazione tra retrocessione, promozione diretta e playoff
        # verrà gestita quando vengono fornite le regole specifiche

    @transaction.atomic
    def create(self):
        """
        Crea un nuovo torneo con tutti i suoi componenti (squadre, giornate, partite)
        """
        # Creare il torneo
        tournament = Tournament.objects.create(
            name=self.name,
            description=self.description,
            structure=self.structure,
            season=self.season,
            start_date=self.start_date or timezone.now().date(),
            parent_tournament=self.parent_tournament,
            status='pending'
        )

        # Associare le squadre al torneo tramite SeasonTeam
        season_teams = []
        for team in self.teams:
            # Gestione sia per oggetti Team che per oggetti SeasonTeam
            if hasattr(team, 'team'):  # È già un SeasonTeam
                season_team = team
            else:  # È un Team
                season_team = SeasonTeam.objects.get_or_create(team=team, season=self.season)[0]
            season_teams.append(season_team)

        tournament.teams.set(season_teams)
        self.teams = season_teams  # 🔁 così i metodi interni usano SeasonTeam
        self.logger.info(f"Torneo '{self.name}' creato con {len(self.teams)} squadre.")

        # Creare le classifiche iniziali per ogni squadra
        self._initialize_rankings(tournament)

        # Creare la struttura del torneo in base al tipo
        if self.structure.is_cup:
            self._generate_knockout(tournament)
        else:
            self._generate_league(tournament)

        # Gestire le regole di qualificazione e promozione/retrocessione
        self._setup_qualification_rules(tournament)

        # Aggiornare lo stato del torneo a pronto
        tournament.status = 'active'
        tournament.save(update_fields=['status'])

        self.logger.info(f"Torneo '{tournament.name}' completamente configurato e pronto.")
        return tournament

    def _create_qualification_rule(self, tournament, rule_type, rule_config):
        """Crea una regola di qualificazione in base al tipo e configurazione"""
        if not rule_config.get('to_tournament'):
            self.logger.warning(f"Configurazione regola '{rule_type}' non valida: manca to_tournament")
            return

        rule = TournamentQualificationRule.objects.create(
            from_tournament=tournament,
            to_tournament=rule_config['to_tournament'],
            min_rank=rule_config.get('min_rank', 1),
            max_rank=rule_config.get('max_rank', 1),
            qualification_type=rule_config.get('type', 'promotion')
        )
        self.logger.info(f"Creata regola di qualificazione {rule_type}: {rule}")

    def _initialize_rankings(self, tournament):
        """Inizializza la classifica per ogni squadra nel torneo"""
        for team in self.teams:
            TournamentRanking.objects.create(
                tournament=tournament,
                team=team,  # Già un oggetto SeasonTeam
                matches_played=0,
                win=0,
                draw=0,
                loss=0,
                goals_for=0,
                goals_against=0
            )
        self.logger.info(f"Inizializzate {len(self.teams)} posizioni in classifica per il torneo '{tournament.name}'")

    def _setup_qualification_rules(self, tournament):
        """Configura le regole di qualificazione per promozione e playoff"""
        # Gestire le regole di qualificazione personalizzate
        if self.qualification_rules:
            for rule_type, rule_config in self.qualification_rules.items():
                self._create_qualification_rule(tournament, rule_type, rule_config)

        # Retrocompatibilità con il vecchio sistema
        elif self.structure.relegation_enabled and self.other_tournament:
            if self.tournament_direct_qualification_rule:
                self.logger.info("Generazione regole di qualificazione per il torneo di promozione e retrocessione.")
                tournament_direct_qualification_rule = TournamentQualificationRule.objects.create(
                    from_tournament=tournament,
                    to_tournament=self.other_tournament,
                    min_rank=self.tournament_direct_qualification_rule.min_rank,
                    max_rank=self.tournament_direct_qualification_rule.max_rank,
                    qualification_type='promotion'
                )
                self.logger.info(f"Regola di qualificazione diretta creata: {tournament_direct_qualification_rule}")

                if self.structure.has_playoff and self.tournament_playoff_qualification_rule:
                    play_off = self._generate_playoff(tournament)

                    tournament_playoff_qualification_rule = TournamentQualificationRule.objects.create(
                        from_tournament=tournament,
                        to_tournament=play_off,
                        min_rank=self.tournament_playoff_qualification_rule.min_rank,
                        max_rank=self.tournament_playoff_qualification_rule.max_rank,
                        qualification_type='playoff'
                    )

                    tournament_playoff_winner_qualification_rule = TournamentQualificationRule.objects.create(
                        from_tournament=play_off,
                        to_tournament=self.other_tournament,
                        min_rank=1,
                        max_rank=1,
                        qualification_type='promotion'
                    )

                    self.logger.info(f"Regola di qualificazione playoff creata: {tournament_playoff_qualification_rule}")

        return tournament

    def _generate_league(self, tournament):
        """
        Genera un campionato a girone (all'italiana) con partite di andata ed eventualmente ritorno
        """
        # Creare gli accoppiamenti tra le squadre
        matchups = list(combinations(self.teams, 2))

        # Se è un campionato con andata e ritorno, aggiungi anche le partite con le squadre invertite
        if self.structure.home_and_away:
            matchups += [(away, home) for home, away in matchups]

        # Mescoliamo le partite per avere un calendario più vario
        random.shuffle(matchups)

        # Calcola il numero di partite per giornata (metà del numero di squadre)
        matches_per_round = len(self.teams) // 2

        # Dividiamo le partite in giornate
        giornate = [matchups[i:i + matches_per_round] for i in range(0, len(matchups), matches_per_round)]

        # Creiamo le giornate e le partite
        start_date = self.start_date or timezone.now().date()
        giornata_counter = 1
        for matches in giornate:
            # Creare la giornata
            match_date = start_date + timedelta(days=(giornata_counter - 1) * 7) if start_date else None
            round_obj = Round.objects.create(
                tournament=tournament,
                number=giornata_counter
            )
            self.logger.info(f"Creata giornata {giornata_counter} con {len(matches)} partite.")

            # Creare le partite della giornata
            for home, away in matches:
                match = Match.objects.create(
                    home_team=home.team,  # .team per ottenere il Team da SeasonTeam
                    away_team=away.team,
                    tournament=tournament
                )
                round_obj.matches.add(match)
            giornata_counter += 1

    def _generate_knockout(self, tournament):
        """
        Genera un torneo a eliminazione diretta (coppa)
        Supporta sia torneo con numero di squadre potenza di 2, sia con numero arbitrario
        """
        round_num = 1
        current_teams = self.teams.copy()
        random.shuffle(current_teams)

        start_date = self.start_date or timezone.now().date()

        while len(current_teams) > 1:
            num_teams = len(current_teams)
            power = 2 ** math.floor(math.log2(num_teams))
            matches_to_play = (num_teams - power)  # Numero di match da giocare in questo turno
            teams_in_match = matches_to_play * 2

            if matches_to_play == 0:  # Se numero di squadre è potenza di 2
                teams_in_match = num_teams

            # Calcola la data del turno (ogni turno dopo 2 settimane)
            round_date = start_date + timedelta(days=(round_num - 1) * 14) if start_date else None

            # Crea il turno
            round_obj = Round.objects.create(
                tournament=tournament,
                number=round_num,
                label=self._round_label(num_teams),
                knockout_stage=True
            )
            self.logger.info(f"Creata fase '{round_obj.label}' (round {round_num}) con {num_teams} squadre.")

            # Suddividi le squadre tra quelle che giocano e quelle che passano automaticamente
            playing = current_teams[:teams_in_match]
            advancing = current_teams[teams_in_match:]  # squadre che passano turno senza giocare

            # Crea le partite per le squadre che giocano
            for i in range(0, len(playing), 2):
                if i + 1 < len(playing):  # Verifica che ci sia una squadra avversaria
                    home, away = playing[i], playing[i + 1]
                    match = Match.objects.create(
                        home_team=home.team,  # .team per ottenere il Team da SeasonTeam
                        away_team=away.team,
                        tournament=tournament
                    )
                    round_obj.matches.add(match)
                else:
                    # Se il numero di squadre è dispari, l'ultima passa automaticamente
                    advancing.append(playing[i])

            # Per ora, consideriamo tutte le squadre come potenziali avanzanti al turno successivo
            # (la logica per determinare chi avanza va implementata quando ci sono i risultati)
            current_teams = advancing + playing
            round_num += 1

            # Per ora creiamo solo il primo turno, i turni successivi saranno creati dopo che avremo i risultati
            # Questo permette di gestire correttamente l'avanzamento delle squadre in base ai risultati effettivi
            break

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
        """
        Genera un torneo playoff con qualificazione basata su regole
        Questo metodo viene utilizzato per generare tornei di playoff basati sulle classifiche di altri tornei
        """
        # Se il torneo non è stato ancora avviato, non possiamo generare i playoff
        if not self.tournament_playoff_qualification_rule:
            self.logger.warning("Regola di qualificazione playoff non configurata. Impossibile generare playoff.")
            return

        # Per retrocompatibilità, creiamo un torneo playoff come figlio di questo
        playoff_name = f"{tournament.name} Playoff"
        playoff_tournament = Tournament.objects.create(
            name=playoff_name,
            description=f"Playoff del torneo {tournament.name}",
            structure=TournamentStructure.objects.get(is_cup=True, has_playoff=False),
            season=tournament.season,
            parent_tournament=tournament,
            status='pending'
        )
        self.logger.info(f"Creato torneo playoff '{playoff_name}' come figlio di '{tournament.name}'")

        # Ottieni la classifica aggiornata (qui usiamo la funzione esistente per simulare)
        standings = get_tournament_standings(tournament)

        # Costruisci la lista delle squadre qualificate in base alle regole
        qualified_teams = []
        min_rank = self.tournament_playoff_qualification_rule.min_rank
        max_rank = self.tournament_playoff_qualification_rule.max_rank

        # Estrai le squadre che si trovano nel range indicato dalla regola
        for pos, (team, _) in enumerate(standings, start=1):
            if min_rank <= pos <= max_rank:
                qualified_teams.append(team)

        if len(qualified_teams) < 2:
            self.logger.warning(f"Numero insufficiente di squadre qualificate per playoff: {len(qualified_teams)}")
            return

        # Associa le squadre qualificate al torneo playoff
        season_teams = []
        for season_team in qualified_teams:  # qualified_teams contiene SeasonTeam, non Team
            season_teams.append(season_team)

        playoff_tournament.teams.set(season_teams)
        self.logger.info(f"Aggiunte {len(season_teams)} squadre al torneo playoff")

        # Inizializza le classifiche per il nuovo torneo
        for season_team in qualified_teams:
            TournamentRanking.objects.create(
                tournament=playoff_tournament,
                team=season_team,  # Usa SeasonTeam direttamente, non team.team
                points=0,
                matches_played=0
            )

        # Imposta la data di inizio dopo la fine del torneo principale
        playoff_start_date = None
        if tournament.end_date:
            playoff_start_date = tournament.end_date + timedelta(days=7)

        # Crea il primo turno dei playoff
        round_obj = Round.objects.create(
            tournament=playoff_tournament,
            number=1,
            label=self._round_label(len(qualified_teams)),
            knockout_stage=True
        )

        # Crea le partite del primo turno
        for i in range(0, len(qualified_teams), 2):
            if i + 1 < len(qualified_teams):
                home, away = qualified_teams[i], qualified_teams[i + 1]
                match = Match.objects.create(
                    home_team=home.team,  # Usa Team, non SeasonTeam
                    away_team=away.team,  # Usa Team, non SeasonTeam
                    tournament=playoff_tournament
                    # Il campo date e legs non sono nel modello Match
                )
                round_obj.matches.add(match)

        playoff_tournament.status = 'active'
        playoff_tournament.save(update_fields=['status'])

        self.logger.info(f"Torneo playoff '{playoff_name}' configurato con {len(qualified_teams) // 2} partite nel primo turno")
        return playoff_tournament

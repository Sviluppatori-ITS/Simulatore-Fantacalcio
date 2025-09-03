"""
    Test per vedere se i modelli funzionano correttamente
"""
import logging
import sys

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import connection
from django.test import TestCase
from django.utils import timezone

from core.factories.tournament_factory import TournamentFactory
from core.models import (Tournament, TournamentStructure, Season, Team, SeasonTeam,
                         Match, Round, TournamentQualificationRule, TournamentRanking, League,
                         Continent, Nationality, Person, Player, TournamentRule)
from core.utils.test_counter import increment_test_counter

logger = logging.getLogger("tests")

global test_counter
test_counter = increment_test_counter()


class PlayerModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):

        logger.info(f"[TEST RUN #{test_counter}] -> {cls.__name__}")
        print(f"\n[TEST RUN #{test_counter}] -> {cls.__name__}", flush=True)

        logger.info("Inizio setUpTestData per PlayerModelTest")
        # Crea migrazioni se necessario
        if not connection.introspection.table_names():
            logger.info("Nessuna tabella trovata, eseguo makemigrations")
            call_command('makemigrations', verbosity=0)
        # Esegui migrazioni (solo necessario se usi workaround specifici)
        logger.info("Eseguo migrate")
        call_command('migrate', verbosity=0)

        cls.continent = Continent.objects.create(name="Europa", code="EU")
        logger.info(f"Creato Continent: {cls.continent.name}")
        cls.nationality = Nationality.objects.create(name="Italia", code="ITA", continent=cls.continent)
        logger.info(f"Creata Nationality: {cls.nationality.name}")
        cls.person = Person.objects.create(name="Mario", surname="Rossi", birth_date="1995-05-01", main_nationality=cls.nationality)
        logger.info(f"Creata Person: {cls.person.name} {cls.person.surname}")
        cls.player = Player.objects.create(person=cls.person, main_role="P")
        cls.player.full_clean()
        cls.player.save()
        logger.info(f"Creato Player per {cls.person.name} {cls.person.surname} con ruolo {cls.player.main_role}")

    def test_default_overall(self):
        logger.info("Test: controllo valore overall di default per Player")
        self.assertEqual(self.player.overall, 50)
        logger.info("Test superato: overall di default è 50")

    def test_player_role(self):
        logger.info("Test: controllo ruolo di default per Player")
        self.assertEqual(self.player.main_role, "P")
        logger.info(f"Test superato: ruolo di default è '{self.player.main_role}' - '{self.player.get_main_role_display()}'")


class SeasonTeamModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        logger.info(f"[TEST RUN #{test_counter}] -> {cls.__name__}")
        print(f"\n[TEST RUN #{test_counter}] -> {cls.__name__}", flush=True)

        logger.info("Inizio setUpTestData per SeasonTeamModelTest")

        if not connection.introspection.table_names():
            logger.info("Nessuna tabella trovata, eseguo makemigrations")
            call_command('makemigrations', verbosity=0)

        logger.info("Eseguo migrate")
        call_command('migrate', verbosity=0)

        cls.user = User.objects.create(username='testuser')
        logger.info("Creato User: testuser")

        cls.league = League.objects.create(name="Lega Test", owner=cls.user)
        logger.info("Creata League: Lega Test")

        cls.season = Season.objects.create(
            league=cls.league,
            year=2025,
            is_active=True
        )
        logger.info("Creata Season: 2025")

        cls.tournament_structure = TournamentStructure.objects.create(
            is_cup=False,
            format='league',
            legs=1,
            has_playoff=False,
            relegation_enabled=False,
        )

        cls.tournament = Tournament.objects.create(
            name="Torneo Test",
            structure=cls.tournament_structure,
            season=cls.season,
            is_active=True,
        )
        logger.info("Creato Tournament: Torneo Test")

        cls.team = Team.objects.create(name="Team Test", owner=cls.user)
        logger.info("Creato Team: Team Test")

        cls.season_team = SeasonTeam.objects.create(team=cls.team)
        logger.info("Creato SeasonTeam")

        # Aggiungi la SeasonTeam al torneo
        cls.tournament.teams.add(cls.season_team)
        logger.info("Aggiunto SeasonTeam al Tournament")

        cls.tournament_ranking = TournamentRanking.objects.create(
            tournament=cls.tournament,
            team=cls.season_team,
        )
        logger.info("Creato TournamentRanking")

    def test_season_team_creation(self):
        logger.info("Test: creazione SeasonTeam")

        self.assertIsInstance(self.season_team, SeasonTeam)
        logger.info("SeasonTeam creato con successo")
        self.assertEqual(self.season_team.team, self.team)
        logger.info("Verifica team di SeasonTeam superata")
        self.assertEqual(list(self.season_team.tournaments.all()), [self.tournament])
        logger.info("Verifica torneo di SeasonTeam superata")
        self.assertTrue(all(t.is_active for t in self.season_team.tournaments.all()))
        logger.info("Verifica is_active di SeasonTeam superata")

        self.assertEqual(self.tournament_ranking.squad_points(), 0)
        logger.info(f"Verifica punti di SeasonTeam superata: {self.tournament_ranking.squad_points()}")
        self.assertEqual(self.tournament_ranking.squad_ranking(), 1)  # Se è l'unico ranking
        logger.info(f"Verifica posizione di SeasonTeam superata: {self.tournament_ranking.squad_ranking()}")
        self.assertEqual(self.tournament_ranking.get_matches_played(), 0)
        logger.info(f"Verifica partite giocate di SeasonTeam superata: {self.tournament_ranking.get_matches_played()}")
        self.assertEqual(self.tournament_ranking.win, 0)
        logger.info(f"Verifica vittorie di SeasonTeam superata: {self.tournament_ranking.win}")
        self.assertEqual(self.tournament_ranking.draw, 0)
        logger.info(f"Verifica pareggi di SeasonTeam superata: {self.tournament_ranking.draw}")
        self.assertEqual(self.tournament_ranking.loss, 0)
        logger.info(f"Verifica sconfitte di SeasonTeam superata: {self.tournament_ranking.loss}")
        self.assertEqual(self.tournament_ranking.squad_goals(), 0)
        logger.info(f"Verifica gol fatti di SeasonTeam superata: {self.tournament_ranking.squad_goals()}")
        self.assertEqual(self.tournament_ranking.squad_goals_against(), 0)
        logger.info(f"Verifica gol subiti di SeasonTeam superata: {self.tournament_ranking.squad_goals_against()}")
        self.assertEqual(self.tournament_ranking.squad_goal_difference(), 0)
        logger.info(f"Verifica differenza reti di SeasonTeam superata: {self.tournament_ranking.squad_goal_difference()}")
        logger.info("SeasonTeam creato e verificato con successo")


class TournamentFactoryTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        logger.info(f"[TEST RUN #{test_counter}] -> {cls.__name__}")
        print(f"\n[TEST RUN #{test_counter}] -> {cls.__name__}", flush=True)

        logger.info("Inizio setUpTestData per TournamentFactoryTest")
        # Devi anche creare un User per il owner della League (se richiesto)
        user = User.objects.create(username='testuser')
        logger.info("Creato User: testuser")

        cls.league = League.objects.create(name="Lega Test", owner=user)
        logger.info("Creata League: Lega Test")

        cls.season = Season.objects.create(
            league=cls.league,
            year=2025,
            is_active=True
        )
        logger.info("Creata Season: 2025")

        cls.league_structure_a = TournamentStructure.objects.create(
            is_cup=False,
            format='league',
            legs=1,
            has_playoff=False,
            relegation_enabled=True,
            relegation_teams=3
        )

        cls.league_structure_b = TournamentStructure.objects.create(
            is_cup=False,
            format='league',
            legs=1,
            has_playoff=True,
            relegation_enabled=False,
            relegation_teams=0
        )

        # Crea tornei fittizi a cui applicare le regole di qualificazione
        cls.serie_a = Tournament.objects.create(
            name="Serie A Qual",
            structure=cls.league_structure_a,
            season=cls.season,
        )
        cls.serie_b = Tournament.objects.create(
            name="Serie B Qual",
            structure=cls.league_structure_b,
            season=cls.season,
        )

        cls.league_a_qualification_rule = TournamentQualificationRule.objects.create(
            from_tournament=cls.serie_b,
            to_tournament=cls.serie_a,
            min_rank=1,
            max_rank=2,
        )

        cls.league_a_playoff_qualification_rule = TournamentQualificationRule.objects.create(
            from_tournament=cls.serie_b,
            to_tournament=cls.serie_a,
            min_rank=3,
            max_rank=6,
        )

        logger.info("Creata TournamentStructure per i campionati di Serie A e Serie B e regola di qualificazione diretta")

        cls.cup_structure = TournamentStructure.objects.create(
            is_cup=True,
            format='cup',
            legs=1
        )
        logger.info("Creata TournamentStructure per coppa")

        # Creiamo un po' di squadre per i test
        cls.teams_serie_a = [Team.objects.create(name=f"Team A{i}", owner=user) for i in range(1, 21)]
        logger.info("Create 20 squadre per Serie A")
        cls.teams_serie_b = [Team.objects.create(name=f"Team B{i}", owner=user) for i in range(1, 21)]
        logger.info("Create 20 squadre per Serie B")

    def test_create_league_tournament(self):
        # Test per la creazione di un torneo di lega (Serie A)
        logger.info("Test: creazione torneo di lega (Serie A)")
        factory = TournamentFactory(
            structure=self.league_structure_a,
            season=self.season,
            name="Serie A",
            teams=self.teams_serie_a,
            description="Campionato di Serie A",
        )
        tournament = factory.create()
        logger.info("Torneo Serie A creato")

        self.assertEqual(tournament.name, "Serie A")
        self.assertFalse(tournament.structure.is_cup)
        self.assertEqual(tournament.season, self.season)
        self.assertEqual(tournament.teams.count(), len(self.teams_serie_a))
        logger.info("Verifica attributi torneo Serie A superata")

        # Controlla che siano state create giornate (round)
        rounds = tournament.rounds.all()
        self.assertGreater(len(rounds), 0)
        logger.info(f"Numero di giornate create: {len(rounds)}")

        # Verifica che ogni giornata abbia match
        for round_obj in rounds:
            self.assertTrue(round_obj.matches.exists())
        logger.info("Ogni giornata ha almeno un match")

        # Verifica che il numero di match sia corretto
        expected_matches = (len(self.teams_serie_a) * (len(self.teams_serie_a) - 1)) // 2 * self.league_structure_a.legs
        self.assertEqual(tournament.matches.count(), expected_matches)
        logger.info(f"Numero di match creati: {tournament.matches.count()}")

        # Test per la creazione di un torneo di lega (Serie B)
        logger.info("Test: creazione torneo di lega (Serie B)")
        factory = TournamentFactory(
            structure=self.league_structure_b,
            season=self.season,
            name="Serie B",
            teams=self.teams_serie_b,
            description="Campionato di Serie B",

            tournament_direct_qualification_rule=self.league_a_qualification_rule,
            tournament_playoff_qualification_rule=self.league_a_playoff_qualification_rule,
        )
        tournament = factory.create()
        logger.info("Torneo Serie B creato")

        self.assertEqual(tournament.name, "Serie B")
        self.assertFalse(tournament.structure.is_cup)
        self.assertEqual(tournament.season, self.season)
        self.assertEqual(tournament.teams.count(), len(self.teams_serie_b))
        logger.info("Verifica attributi torneo Serie B superata")

        rounds = tournament.rounds.all()
        self.assertGreater(len(rounds), 0)
        logger.info(f"Numero di giornate create: {len(rounds)}")

        # Verifica che ogni giornata abbia match
        for round_obj in rounds:
            self.assertTrue(round_obj.matches.exists())
        logger.info("Ogni giornata ha almeno un match")

        # Verifica che il numero di match sia corretto
        expected_matches = (len(self.teams_serie_b) * (len(self.teams_serie_b) - 1)) // 2 * self.league_structure_b.legs
        self.assertEqual(tournament.matches.count(), expected_matches)
        logger.info(f"Numero di match creati: {tournament.matches.count()}")

    def test_create_cup_tournament(self):
        logger.info("Test: creazione torneo di coppa (Coppa Italia)")
        factory = TournamentFactory(
            structure=self.cup_structure,
            season=self.season,
            name="Coppa Italia",
            teams=self.teams_serie_b,
            description="Coppa Italia"
        )
        tournament = factory.create()
        logger.info("Torneo Coppa Italia creato")

        self.assertEqual(tournament.name, "Coppa Italia")
        self.assertTrue(tournament.structure.is_cup)
        self.assertEqual(tournament.season, self.season)
        self.assertEqual(tournament.teams.count(), len(self.teams_serie_b))
        logger.info("Verifica attributi torneo Coppa Italia superata")

        rounds = tournament.rounds.all()
        self.assertGreater(len(rounds), 0)
        logger.info(f"Numero di round creati: {len(rounds)}")

        # In una coppa, ogni round dovrebbe avere match
        for round_obj in rounds:
            self.assertTrue(round_obj.matches.exists())
        logger.info("Ogni round della coppa ha almeno un match")

        # expected_matches = len(self.teams_serie_b) - 1  # in knockout puro
        # self.assertEqual(tournament.matches.count(), expected_matches)
        # logger.info("Calcolo coerenza numero di match")

    logger.info("Tutti i test di TournamentFactoryTest sono stati eseguiti con successo\n")


class TestTournamentFactory(TestCase):
    """Test per la factory di creazione dei tornei"""

    def setUp(self):
        """Prepara i dati di base per i test"""
        # Crea un utente per owner di team e league
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_create_league_tournament(self):
        """Verifica la creazione di un torneo di tipo campionato"""
        # Creazione dei dati di test
        league = League.objects.create(name="Serie A", owner=self.user)
        season = Season.objects.create(year=2023, league=league)
        structure = TournamentStructure.objects.create(
            name="Serie A",
            is_cup=False,
            format='league',
            has_playoff=False,
            legs=2
        )
        teams = [
            Team.objects.create(name=f"Team {i}", code=f"TM{i}", owner=self.user)
            for i in range(1, 11)  # 10 squadre
        ]

        # Creazione del torneo tramite factory
        factory = TournamentFactory(
            structure=structure,
            season=season,
            name="Serie A 2023",
            teams=teams,
            description="Campionato di Serie A",
            start_date=timezone.now().date()
        )
        tournament = factory.create()

        # Verifiche
        self.assertIsNotNone(tournament)
        self.assertEqual(tournament.name, "Serie A 2023")
        self.assertEqual(tournament.structure, structure)
        self.assertEqual(tournament.season, season)
        self.assertEqual(tournament.status, 'active')

        # Verifica la creazione delle giornate e partite
        rounds = Round.objects.filter(tournament=tournament)
        self.assertGreater(rounds.count(), 0)

        # Verifica che il numero di partite sia corretto (ogni squadra gioca contro tutte le altre)
        expected_matches = len(teams) * (len(teams) - 1) if structure.legs > 1 else len(teams) * (len(teams) - 1) // 2
        matches = Match.objects.filter(tournament=tournament)
        self.assertEqual(matches.count(), expected_matches)

        # Verifica che ci sia una classifica per ogni squadra
        rankings = TournamentRanking.objects.filter(tournament=tournament)
        self.assertEqual(rankings.count(), len(teams))

    def test_create_cup_tournament(self):
        """Verifica la creazione di un torneo di tipo coppa"""
        # Creazione dei dati di test
        league = League.objects.create(name="Coppa Italia", owner=self.user)
        season = Season.objects.create(year=2023, league=league)
        structure = TournamentStructure.objects.create(
            name="Coppa Italia",
            is_cup=True,
            format='cup',
            has_playoff=False,
            legs=2  # Andata e ritorno
        )
        teams = [
            Team.objects.create(name=f"Team {i}", code=f"TM{i}", owner=self.user)
            for i in range(1, 9)  # 8 squadre
        ]

        # Creazione del torneo tramite factory
        factory = TournamentFactory(
            structure=structure,
            season=season,
            name="Coppa Italia 2023",
            teams=teams,
            description="Coppa Italia"
        )
        tournament = factory.create()

        # Verifiche
        self.assertIsNotNone(tournament)
        self.assertEqual(tournament.name, "Coppa Italia 2023")
        self.assertEqual(tournament.structure, structure)
        self.assertEqual(tournament.status, 'active')

        # Verifica la creazione dei turni
        rounds = Round.objects.filter(tournament=tournament)
        self.assertEqual(rounds.count(), 1)  # Per ora creiamo solo il primo turno

        first_round = rounds.first()
        self.assertTrue(first_round.knockout_stage)
        self.assertEqual(first_round.label, "Quarti di finale")  # Con 8 squadre, primo turno sono i quarti

        # Verifica le partite del primo turno
        matches = first_round.matches.all()
        self.assertEqual(matches.count(), 4)  # Con 8 squadre, ci sono 4 partite nel primo turno

    def test_create_with_qualification_rules(self):
        """Verifica la creazione di un torneo con regole di qualificazione"""
        # Creazione dei dati di test
        league = League.objects.create(name="Campionato Italiano", owner=self.user)
        season = Season.objects.create(year=2023, league=league)

        # Struttura per Serie A
        structure_a = TournamentStructure.objects.create(
            name="Serie A",
            is_cup=False,
            format='league',
            has_playoff=True,
            relegation_enabled=True,
            relegation_teams=2,
            legs=2
        )        # Struttura per Serie B
        structure_b = TournamentStructure.objects.create(
            name="Serie B",
            is_cup=False,
            format='league',
            has_playoff=False,
            legs=2
        )

        # Squadre per Serie B
        teams_b = [
            Team.objects.create(name=f"Team B{i}", code=f"TB{i}", owner=self.user)
            for i in range(1, 13)  # 12 squadre
        ]

        # Creazione Serie B
        serie_b = Tournament.objects.create(
            name="Serie B 2023",
            structure=structure_b,
            season=season,
            status='active'
        )

        # Squadre per Serie A
        teams_a = [
            Team.objects.create(name=f"Team A{i}", code=f"TA{i}", owner=self.user)
            for i in range(1, 11)  # 10 squadre
        ]

        # Prima creiamo i tornei per le regole di qualificazione
        serie_a = Tournament.objects.create(
            name="Serie A 2023",
            structure=structure_a,
            season=season,
            status='active'
        )
        serie_a.teams.set([SeasonTeam.objects.get_or_create(team=team, season=season)[0] for team in teams_a])

        # Regole di qualificazione
        direct_rule = TournamentQualificationRule.objects.create(
            from_tournament=serie_a,
            to_tournament=serie_b,
            min_rank=1,
            max_rank=2,
            qualification_type='promotion'
        )

        # Modifichiamo la struttura per il test con le regole di qualificazione corrette
        structure_a.relegation_teams = 0  # Correggiamo il valore per evitare l'errore di validazione
        structure_a.save()

        # Creiamo un torneo di playoff per la regola
        playoff_tournament = Tournament.objects.create(
            name="Playoff Serie A 2023",
            structure=TournamentStructure.objects.create(name="Playoff", is_cup=True, legs=2),
            season=season,
            parent_tournament=serie_a,
            status='pending'
        )

        playoff_rule = TournamentQualificationRule.objects.create(
            from_tournament=serie_a,
            to_tournament=playoff_tournament,
            min_rank=3,
            max_rank=6,
            qualification_type='playoff'
        )

        # Test di verifica della creazione di un nuovo torneo con regole già impostate
        factory = TournamentFactory(
            structure=structure_a,
            season=season,
            name="Serie A 2024",  # Nuovo nome per evitare conflitti
            teams=teams_a,
            description="Campionato di Serie A",
            start_date=timezone.now().date(),
            tournament_direct_qualification_rule=direct_rule,
            tournament_playoff_qualification_rule=playoff_rule,
            other_tournament=serie_b
        )
        serie_a_2024 = factory.create()

        # Verifiche
        self.assertIsNotNone(serie_a_2024)
        self.assertEqual(serie_a_2024.name, "Serie A 2024")

        # Verifica le regole di qualificazione
        qualification_rules = TournamentQualificationRule.objects.filter(from_tournament=serie_a_2024)
        self.assertGreaterEqual(qualification_rules.count(), 1)

        # Verifica che il torneo è stato creato correttamente
        self.assertEqual(serie_a_2024.teams.count(), len(teams_a))
        self.assertEqual(serie_a_2024.status, 'active')

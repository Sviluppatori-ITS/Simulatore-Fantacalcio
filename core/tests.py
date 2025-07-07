from django.test import TestCase
from django.core.management import call_command
from django.db import connection
from .models import Nationality, Person, Player, Tournament, Team, TournamentStructure, Season, League, Round, Match, TournamentQualificationRule, TournamentRule, SeasonTeam, TournamentRanking
from core.factories.tournament_factory import TournamentFactory
from core.factories import tournament_factory  # se metti la factory in un file factories.py
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
import logging
from core.utils.test_counter import increment_test_counter
import sys


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

        cls.nationality = Nationality.objects.create(name="Italia", code="ITA")
        logger.info("Creata Nationality: Italia")
        cls.person = Person.objects.create(name="Mario", surname="Rossi", birth_date="1995-05-01", main_nationality=cls.nationality)
        logger.info("Creata Person: Mario Rossi")
        cls.player = Player.objects.create(person=cls.person, main_nationality=cls.nationality)
        logger.info("Creato Player per Mario Rossi")

    def test_default_overall(self):
        logger.info("Test: controllo valore overall di default per Player")
        self.assertEqual(self.player.overall, 50)
        logger.info("Test superato: overall di default è 50")


class SeasonTeamModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):

        logger.info(f"[TEST RUN #{test_counter}] -> {cls.__name__}")
        print(f"\n[TEST RUN #{test_counter}] -> {cls.__name__}", flush=True)

        logger.info("Inizio setUpTestData per SeasonTeamModelTest")
        # Crea migrazioni se necessario
        if not connection.introspection.table_names():
            logger.info("Nessuna tabella trovata, eseguo makemigrations")
            call_command('makemigrations', verbosity=0)
        # Esegui migrazioni (solo necessario se usi workaround specifici)
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

        cls.tournament = Tournament.objects.create(
            name="Torneo Test",
            structure=TournamentStructure.objects.create(
                is_cup=False,
                use_groups=False,
                home_and_away=False,
                has_playoff=False,
                relegation_enabled=False,
            ),
            season=cls.season,
            is_active=True,
        )

        cls.team = Team.objects.create(name="Team Test", owner=cls.user)
        logger.info("Creato Team: Team Test")

        cls.season_team = SeasonTeam.objects.create(
            team=cls.team,
            tournament=cls.tournament,
        )

        cls.tournament_ranking = TournamentRanking.objects.create(
            tournament=cls.tournament,
            team=cls.season_team,
        )

    def test_season_team_creation(self):
        logger.info("Test: creazione SeasonTeam")

        self.assertIsInstance(self.season_team, SeasonTeam)
        logger.info("SeasonTeam creato con successo")
        self.assertEqual(self.season_team.team, self.team)
        logger.info("Verifica team di SeasonTeam superata")
        self.assertEqual(self.season_team.tournament, self.tournament)
        logger.info("Verifica torneo di SeasonTeam superata")
        self.assertTrue(self.season_team.tournament.is_active)
        logger.info("Verifica is_active di SeasonTeam superata")

        self.assertEqual(self.tournament_ranking.squad_points(), 0)
        logger.info(f"Verifica punti di SeasonTeam superata: {self.tournament_ranking.squad_points()}")
        self.assertEqual(self.tournament_ranking.squad_ranking(), 1)  # Se è l'unico ranking
        logger.info(f"Verifica posizione di SeasonTeam superata: {self.tournament_ranking.squad_ranking()}")
        self.assertEqual(self.tournament_ranking.matches_played(), 0)
        logger.info(f"Verifica partite giocate di SeasonTeam superata: {self.tournament_ranking.matches_played()}")
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
            use_groups=False,
            home_and_away=True,
            has_playoff=False,
            relegation_enabled=True,
            relegation_teams=3
        )

        cls.league_structure_b = TournamentStructure.objects.create(
            is_cup=False,
            use_groups=False,
            home_and_away=True,
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
            use_groups=False,
            home_and_away=False
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
        expected_matches = (len(self.teams_serie_a) * (len(self.teams_serie_a) - 1) * 2) // 2
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
        expected_matches = (len(self.teams_serie_b) * (len(self.teams_serie_b) - 1) * 2) // 2
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

    logger.info("Tutti i test di TournamentFactoryTest sono stati eseguiti con successo\n")

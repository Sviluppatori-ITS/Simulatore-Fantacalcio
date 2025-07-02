from django.test import TestCase
from django.core.management import call_command
from django.db import connection
from .models import Nationality, Person, Player, Tournament, Team, TournamentStructure, Season, League, Round, Match
from core.factories.tournament_factory import TournamentFactory
from core.factories import tournament_factory  # se metti la factory in un file factories.py
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User


class PlayerModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Crea migrazioni se necessario
        if not connection.introspection.table_names():
            call_command('makemigrations', verbosity=0)
        # Esegui migrazioni (solo necessario se usi workaround specifici)
        call_command('migrate', verbosity=0)

        cls.nationality = Nationality.objects.create(name="Italia", code="ITA")
        cls.person = Person.objects.create(name="Mario", surname="Rossi", birth_date="1995-05-01", main_nationality=cls.nationality)
        cls.player = Player.objects.create(person=cls.person, main_nationality=cls.nationality)

    def test_default_overall(self):
        self.assertEqual(self.player.overall, 50)


class TournamentFactoryTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Devi anche creare un User per il owner della League (se richiesto)
        user = User.objects.create(username='testuser')

        cls.league = League.objects.create(name="Lega Test", owner=user)

        cls.season = Season.objects.create(
            league=cls.league,
            year=2025,
            is_active=True
        )

        cls.league_structure = TournamentStructure.objects.create(
            is_cup=False,
            use_groups=False,
            home_and_away=True,
            has_playoff=False,
            relegation_enabled=True,
            relegation_teams=3
        )
        cls.cup_structure = TournamentStructure.objects.create(
            is_cup=True,
            use_groups=False,
            home_and_away=False
        )

        # Creiamo un po' di squadre per i test
        cls.teams_serie_a = [Team.objects.create(name=f"Team A{i}", owner=user) for i in range(1, 21)]
        cls.teams_serie_b = [Team.objects.create(name=f"Team B{i}", owner=user) for i in range(1, 21)]

    def test_create_league_tournament(self):
        factory = TournamentFactory(
            structure=self.league_structure,
            season=self.season,
            name="Serie A",
            teams=self.teams_serie_a,
            description="Campionato di Serie A"
        )
        tournament = factory.create()

        self.assertEqual(tournament.name, "Serie A")
        self.assertFalse(tournament.structure.is_cup)
        self.assertEqual(tournament.season, self.season)
        self.assertEqual(tournament.teams.count(), len(self.teams_serie_a))

        # Controlla che siano state create giornate (round)
        rounds = tournament.rounds.all()
        self.assertGreater(len(rounds), 0)

        # Verifica che ogni giornata abbia match
        for round_obj in rounds:
            self.assertTrue(round_obj.matches.exists())

    def test_create_cup_tournament(self):
        factory = TournamentFactory(
            structure=self.cup_structure,
            season=self.season,
            name="Coppa Italia",
            teams=self.teams_serie_b,
            description="Coppa Italia"
        )
        tournament = factory.create()

        self.assertEqual(tournament.name, "Coppa Italia")
        self.assertTrue(tournament.structure.is_cup)
        self.assertEqual(tournament.season, self.season)
        self.assertEqual(tournament.teams.count(), len(self.teams_serie_b))

        rounds = tournament.rounds.all()
        self.assertGreater(len(rounds), 0)

        # In una coppa, ogni round dovrebbe avere match
        for round_obj in rounds:
            self.assertTrue(round_obj.matches.exists())

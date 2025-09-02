"""
Test per la factory di creazione dei tornei
"""
from django.test import TestCase
from django.utils import timezone

from core.factories.tournament_factory import TournamentFactory
from django.contrib.auth.models import User
from core.models import (Tournament, TournamentStructure, Season, Team, SeasonTeam,
                         Match, Round, TournamentQualificationRule, TournamentRanking,
                         League)


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
            has_playoff=False,
            home_and_away=True,
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
        expected_matches = len(teams) * (len(teams) - 1) if structure.home_and_away else len(teams) * (len(teams) - 1) // 2
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
            has_playoff=True,
            home_and_away=True,
            relegation_enabled=True,
            relegation_teams=2,
            legs=2
        )        # Struttura per Serie B
        structure_b = TournamentStructure.objects.create(
            name="Serie B",
            is_cup=False,
            has_playoff=False,
            home_and_away=True,
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

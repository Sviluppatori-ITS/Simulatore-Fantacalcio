from django.test import TestCase
from django.core.management import call_command
from django.db import connection
from .models import Nationality, Person, Player


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

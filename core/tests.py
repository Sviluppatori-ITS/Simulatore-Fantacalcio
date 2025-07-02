from django.test import TestCase
from .models import Player, Person, Nationality


class PlayerModelTest(TestCase):
    def setUp(self):
        nationality = Nationality.objects.create(name="Italia", code="ITA")
        person = Person.objects.create(name="Mario", surname="Rossi", birth_date="1995-05-01", main_nationality=nationality)
        self.player = Player.objects.create(person=person, main_nationality=nationality)

    def test_default_overall(self):
        self.assertEqual(self.player.overall, 50)

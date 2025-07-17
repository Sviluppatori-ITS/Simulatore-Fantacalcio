from datetime import date
from django.db import models

from core.models.nationality import Nationality  # import diretto da django


class Person(models.Model):
    name = models.CharField(max_length=100, help_text="Nome della persona")
    surname = models.CharField(max_length=100, blank=True, help_text="Cognome della persona")
    birth_date = models.DateField(help_text="Data di nascita della persona")
    main_nationality = models.ForeignKey(Nationality, on_delete=models.SET_NULL, null=True, blank=True, help_text="Nazionalità principale della persona")
    other_nationalities = models.ManyToManyField(Nationality, related_name='other_nationalities', blank=True, help_text="Altre nazionalità della persona")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def age(self):
        if self.birth_date:
            today = date.today()
            years = today.year - self.birth_date.year

            if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
                years -= 1
            return years
        return None

    def __str__(self):
        return f"{self.name} {self.surname}"

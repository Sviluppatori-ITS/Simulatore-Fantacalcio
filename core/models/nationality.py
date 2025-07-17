from django.db import models
from .continent import Continent


class Nationality(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3, unique=True)
    continent = models.ForeignKey(Continent, on_delete=models.CASCADE, related_name='nationalities', null=True, blank=True, help_text="Continente di appartenenza")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

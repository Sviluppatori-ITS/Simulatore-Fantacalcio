from django.db import models


class Continent(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Nome del continente")
    code = models.CharField(max_length=3, unique=True, help_text="Codice ISO del continente")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

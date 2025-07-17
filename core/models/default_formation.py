from django.db import models


class DefaultFormation(models.Model):
    name = models.CharField(max_length=100, unique=True)
    formation = models.CharField(max_length=100, help_text="Formazione in formato '4-3-3', '3-5-2', ecc.")
    description = models.TextField(blank=True, help_text="Descrizione della formazione")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

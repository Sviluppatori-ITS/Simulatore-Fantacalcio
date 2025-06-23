from django.db import models
from django.contrib.auth.models import User


class League(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='leagues')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=100)
    league = models.ForeignKey(
        League, on_delete=models.CASCADE, related_name='teams')
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='teams')

    def __str__(self):
        return f"{self.name} - {self.league.name}"

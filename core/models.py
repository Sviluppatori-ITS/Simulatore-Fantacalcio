from django.db import models
from django.contrib.auth.models import User


class League(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='leagues')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=100)
    league = models.ForeignKey(
        League, on_delete=models.CASCADE, related_name='teams')
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='teams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.league.name}"


class Nationality(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3, unique=True)  # Codice ISO della nazione
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=[('P', 'Portiere'), ('D', 'Difensore'), ('C', 'Centrocampista'), ('A', 'Attaccante')])
    main_nationality = models.ForeignKey(Nationality, on_delete=models.CASCADE, related_name='players')  # Nazionalità principale
    other_nationalities = models.ManyToManyField(Nationality, related_name='other_players', blank=True)  # Altre nazionalità
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')  # Squadra attuale
    old_team_name = models.ManyToManyField(Team, related_name='old_players', blank=True)  # Squadre precedenti
    value = models.DecimalField(max_digits=5, decimal_places=2)  # Valore di mercato o fantavalore
    overall = models.PositiveSmallIntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_overall(self):
        self.overall = self.calculate_overall()
        self.save()

    def calculate_overall(self):
        performances = self.simulatedperformance_set.all()

        if not performances.exists():
            return 50  # valore neutro iniziale

        avg_rating = performances.aggregate(models.Avg("rating"))["rating__avg"] or 0
        goal_bonus = performances.aggregate(models.Sum("goals"))["goals__sum"] or 0
        assist_bonus = performances.aggregate(models.Sum("assists"))["assists__sum"] or 0

        raw_score = avg_rating * 10 + goal_bonus * 2 + assist_bonus
        normalized = min(100, max(1, round(raw_score)))  # tra 1 e 100
        return normalized

    def __str__(self):
        return f"{self.name} ({self.role}) - {self.team.name}"


class RosterSlot(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='roster')
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    is_starting = models.BooleanField(default=False)  # titolare o panchina

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


class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='manager_profile')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='manager', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.team.name if self.team else 'No Team'}"


class Match(models.Model):
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches')
    match_day = models.PositiveIntegerField()
    home_score = models.PositiveIntegerField(null=True, blank=True)
    away_score = models.PositiveIntegerField(null=True, blank=True)
    played = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name} - Matchday {self.match_day} ({'Played' if self.played else 'Upcoming'})"


class Season(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='seasons')
    year = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)  # Indica se la stagione è attiva
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.league.name} - Season {self.year} (Matchday {self.current_match_day})"


class Tournament(models.Model):
    name = models.CharField(max_length=100)
    is_cup = models.BooleanField(default=False)

    parent_tournament = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='child_tournaments'
    )

    # Relegation/Promotion system
    promotion_to = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='relegated_from'
    )
    relegation_to = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='promoted_from'
    )

    qualified_to = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='qualifies_from',
        blank=True,
        help_text="Tornei/cup in cui le migliori squadre si qualificano"
    )

    relegation_enabled = models.BooleanField(default=False)
    relegation_teams = models.PositiveIntegerField(default=0)
    playoff_teams = models.PositiveIntegerField(default=0)
    playout_teams = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class TournamentQualificationRule(models.Model):
    from_tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='qualification_rules')
    to_tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='qualified_from')
    min_rank = models.PositiveIntegerField()  # ad es. 1
    max_rank = models.PositiveIntegerField()  # ad es. 4
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.from_tournament.name} {self.min_rank}-{self.max_rank} → {self.to_tournament.name}"

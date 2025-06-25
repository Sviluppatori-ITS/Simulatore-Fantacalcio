from django.db import models
from django.contrib.auth.models import User


class Nationality(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3, unique=True)  # Codice ISO della nazione
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

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


class Team(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='teams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.tournament.name}"


class League(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='leagues')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Season(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='seasons')
    year = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)  # Indica se la stagione è attiva
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.league.name} - Season {self.year} (Matchday {self.current_match_day})"


class TournamentStructure(models.Model):
    is_cup = models.BooleanField(default=False)
    use_groups = models.BooleanField(default=False)
    home_and_away = models.BooleanField(default=True)

    has_playoff = models.BooleanField(default=False)
    has_playout = models.BooleanField(default=False)

    relegation_enabled = models.BooleanField(default=False)
    relegation_teams = models.PositiveIntegerField(default=0)
    playoff_teams = models.PositiveIntegerField(default=0)
    playout_teams = models.PositiveIntegerField(default=0)
    qualification_spots = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.structure__name


class Tournament(models.Model):
    name = models.CharField(max_length=100)  # Serie A, Coppa Italia, ecc.
    description = models.TextField(blank=True)
    structure = models.ForeignKey(TournamentStructure, on_delete=models.PROTECT)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='tournaments')
    teams = models.ManyToManyField(Team, related_name='tournaments', blank=True)  # Squadre partecipanti
    current_match_day = models.PositiveIntegerField(default=1)  # Giorno corrente del torneo
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # tutto il resto può essere semplificato o spostato


class TournamentQualificationRule(models.Model):
    from_tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='qualification_rules')
    to_tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='qualified_from')
    min_rank = models.PositiveIntegerField()  # ad es. 1
    max_rank = models.PositiveIntegerField()  # ad es. 4
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.from_tournament.name} {self.min_rank}-{self.max_rank} → {self.to_tournament.name}"


class SeasonTeam(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='season_teams')
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='season_teams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('team', 'season')

    def __str__(self):
        return f"{self.team.name} - {self.season.year}"


class Player(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=[('P', 'Portiere'), ('D', 'Difensore'), ('C', 'Centrocampista'), ('A', 'Attaccante')])
    main_nationality = models.ForeignKey(Nationality, on_delete=models.CASCADE, related_name='players')  # Nazionalità principale
    other_nationalities = models.ManyToManyField(Nationality, related_name='other_players', blank=True)  # Altre nazionalità
    value = models.DecimalField(max_digits=5, decimal_places=2)  # Valore di mercato o fantavalore
    overall = models.PositiveSmallIntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


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


class Ranking(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='rankings')
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='rankings')
    rank = models.PositiveIntegerField()  # Posizione in classifica
    points = models.PositiveIntegerField(default=0)  # Punti accumulati
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('team', 'tournament')

    def __str__(self):
        return f"{self.team.name} - {self.tournament.name} (Rank: {self.rank}, Points: {self.points})"

from django.db import models
from django.contrib.auth.models import User
from datetime import date


class Nationality(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3, unique=True)  # Codice ISO della nazione

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teams')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        tournaments = ", ".join([t.name for t in self.tournaments.all()])
        return f"{self.name} ({tournaments})"


class League(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leagues')

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


class Trophy(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    trophy_img = models.ImageField(upload_to='trophies/', null=True, blank=True)  # Immagine del trofeo
    awarded_to = models.ForeignKey('SeasonTeam', on_delete=models.CASCADE, related_name='trophies', null=True, blank=True)  # Squadra vincitrice

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_awarded(self):
        return self.awarded_to is not None

    def __str__(self):
        return f"{self.name} - {self.awarded_to.name} ({self.tournament.name if self.tournament else 'No Tournament'})"


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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{'Coppa' if self.is_cup else 'Campionato'}{' con gironi' if self.use_groups else ''}"


class Tournament(models.Model):
    name = models.CharField(max_length=100)  # Serie A, Coppa Italia, ecc.
    description = models.TextField(blank=True)
    structure = models.ForeignKey(TournamentStructure, on_delete=models.PROTECT)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='tournament')
    teams = models.ManyToManyField(Team, related_name='tournaments', blank=True)  # Squadre partecipanti
    current_match_day = models.PositiveIntegerField(default=1)  # Giorno corrente del torneo
    trophy = models.ForeignKey(Trophy, on_delete=models.SET_NULL, null=True, blank=True, related_name='tournament')  # Trofeo associato

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # tutto il resto può essere semplificato o spostato

    def __str__(self):
        return f"{self.name} - {self.season.year} ({'Attivo' if self.season.is_active else 'Inattivo'})"


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
        unique_together = ('team', 'tournament')

    def __str__(self):
        return f"{self.team.name} - {self.tournament.season.year}"


class Player(models.Model):
    name = models.CharField(max_length=100, help_text="Nome del giocatore")  # Nome del giocatore
    surname = models.CharField(max_length=100, blank=True, help_text="Cognome del giocatore")  # Cognome del giocatore
    born = models.DateField(help_text="Data di nascita del giocatore")  # Data di nascita del giocatore
    main_role = models.CharField(max_length=20, choices=[('P', 'Portiere'), ('D', 'Difensore'), ('C', 'Centrocampista'), ('A', 'Attaccante')], null=True, blank=True, help_text="Ruolo principale del giocatore")  # Ruolo principale del giocatore
    main_nationality = models.ForeignKey(Nationality, on_delete=models.CASCADE, related_name='players', help_text="Nazionalità principale del giocatore")  # Nazionalità principale
    other_nationalities = models.ManyToManyField(Nationality, related_name='other_players', blank=True, help_text="Altre nazionalità del giocatore, se esistenti")  # Altre nazionalità
    overall = models.PositiveSmallIntegerField(default=50, help_text="Overall del giocatore, da 1 a 100")  # Overall del giocatore, da 1 a 100
    fanta_value = models.PositiveIntegerField(default=50000, help_text="Valore di fanta-mercato del giocatore")  # Valore di fanta-mercato del giocatore
    value = models.PositiveIntegerField(default=0, help_text="Valore di mercato del giocatore")  # Valore di mercato del giocatore, calcolato in base all'overall e al ruolo

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def age(self):
        if self.born:
            today = date.today()
            years = today.year - self.born.year

            # Se il compleanno non è ancora arrivato quest'anno, sottrai 1
            if (today.month, today.day) < (self.born.month, self.born.day):
                years -= 1
            return years
        return None

    class Meta:
        verbose_name = "Giocatore"
        verbose_name_plural = "Giocatori"
        ordering = ['name', 'surname', 'born']

    def save(self, *args, **kwargs):
        if not self.overall:
            self.overall = self.calculate_overall() or 50  # Calcola l'overall prima di salvare

        # Calcola il valore di mercato prima di salvare
        if not self.fanta_value:
            self.fanta_value = int(self.fanta_value())

        super().save(*args, **kwargs)

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

    def fanta_value(self):
        # Calcola il valore di mercato del giocatore basato su overall e ruolo
        base_value = self.overall * 1000

        # Moltiplicatore basato sul ruolo
        role_multiplier = {
            'P': 1.2,
            'D': 1.1,
            'C': 1.0,
            'A': 1.3
        }

        # Modifica il valore in base all'età del giocatore
        age = self.age()
        if age is not None:
            if age < 20:
                base_value *= 1.5
            elif age < 25:
                base_value *= 1.2
            elif age > 30:
                base_value *= 1.0
            elif age > 35:
                base_value *= 0.8
            elif age > 40:
                base_value *= 0.5
        else:
            base_value *= 1.0  # Se l'età non è disponibile, usa il valore base

        return base_value * role_multiplier.get(self.main_role, 1.0)

    def update_fanta_value(self):
        # Aggiorna il valore di mercato del giocatore
        self.fanta_value = self.fanta_value()
        self.save()

    @property
    def dynamic_overall(self):
        return self.calculate_overall()

    @property
    def dynamic_fanta_value(self):
        return self.fanta_value()

    def __str__(self):
        return f"{self.name} ({self.role}) - {self.main_nationality.name}"


class RosterSlot(models.Model):
    team = models.ForeignKey(SeasonTeam, on_delete=models.CASCADE, related_name='roster')
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    is_starting = models.BooleanField(default=False)  # titolare o panchina
    role = models.CharField(max_length=20, choices=[('P', 'Portiere'), ('D', 'Difensore'), ('C', 'Centrocampista'), ('A', 'Attaccante')], default='C')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


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
    home_score = models.PositiveIntegerField(null=True, blank=True)
    away_score = models.PositiveIntegerField(null=True, blank=True)
    played = models.BooleanField(default=False)
    kickoff_datetime = models.DateTimeField(null=True, blank=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name} - Matchday {self.match_day} ({'Played' if self.played else 'Upcoming'})"


class MatchHistory(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="match_performances")
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="performances")
    rating = models.FloatField()
    goals = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    minutes_played = models.PositiveIntegerField(default=0)
    is_starting = models.BooleanField(default=False)
    yellow_cards = models.PositiveIntegerField(default=0)
    red_cards = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('player', 'match')

    def __str__(self):
        return f"Match Performance: {self.player.name} in {self.match.home_team.name} vs {self.match.away_team.name}"


class Round(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='rounds')
    matches = models.ManyToManyField(Match, related_name='rounds', blank=True)
    match_day = models.PositiveIntegerField()
    label = models.CharField(max_length=100, blank=True, help_text="Nome del turno, es. 'Ottavi di finale'")
    knockout_stage = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.label:
            return f"{self.label} - {self.tournament.name}"
        return f"Turno {self.match_day} - {self.tournament.name}"


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


class PlayerStatistics(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE, related_name='statistics', verbose_name="Giocatore", help_text="Il giocatore a cui appartengono le statistiche")
    matches_played = models.PositiveIntegerField(default=0)
    goals_scored = models.PositiveIntegerField(default=0)
    assists_made = models.PositiveIntegerField(default=0)
    yellow_cards = models.PositiveIntegerField(default=0)
    red_cards = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Statistiche Giocatore"
        verbose_name_plural = "Statistiche Giocatori"
        ordering = ['-matches_played', '-goals_scored', '-assists_made', '-yellow_cards', '-red_cards']

    def __str__(self):
        return f"Statistics for {self.player.name}"

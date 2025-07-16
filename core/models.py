"""Models per il simulatore di fantacalcio."""

from datetime import date

from django.contrib.auth.models import User
from django.db import models


class Person(models.Model):
    name = models.CharField(max_length=100, help_text="Nome della persona")
    surname = models.CharField(max_length=100, blank=True, help_text="Cognome della persona")
    birth_date = models.DateField(help_text="Data di nascita della persona")
    main_nationality = models.ForeignKey('Nationality', on_delete=models.SET_NULL, null=True, blank=True, help_text="Nazionalità principale della persona")
    other_nationalities = models.ManyToManyField('Nationality', related_name='other_nationalities', blank=True, help_text="Altre nazionalità della persona")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def age(self):
        if self.birth_date:
            today = date.today()
            years = today.year - self.birth_date.year

            # Se il compleanno non è ancora arrivato quest'anno, sottrai 1
            if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
                years -= 1
            return years
        return None

    def __str__(self):
        return f"{self.name} {self.surname}"


class Continent(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Nome del continente")
    code = models.CharField(max_length=3, unique=True, help_text="Codice ISO del continente")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Nationality(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3, unique=True)  # Codice ISO della nazione
    continent = models.ForeignKey(Continent, on_delete=models.CASCADE, related_name='nationalities', null=True, blank=True, help_text="Continente di appartenenza")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=5)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teams')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.code:
            self.code = self.code.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        tournaments = ", ".join([t.name for t in self.tournaments.all()])
        return f"{self.name} ({tournaments})"


class League(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leagues', blank=True, null=True)

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
    is_active = models.BooleanField(default=True, help_text="Indica se il torneo è attivo")
    start_date = models.DateField(null=True, blank=True, help_text="Data di inizio del torneo")
    end_date = models.DateField(null=True, blank=True, help_text="Data di fine del torneo")
    logo = models.ImageField(upload_to='tournaments/', null=True, blank=True, help_text="Logo del torneo")  # Logo del torneo

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


from django.db import models

# (valore, etichetta visibile)
RULE_TYPE_CHOICES = [
    ("point_win", "Punti Vittoria"),
    ("point_draw", "Punti Pareggio"),
    ("point_loss", "Punti Sconfitta"),
    ("goal_diff", "Differenza Reti"),
    ("red_cards", "Cartellini Rossi"),
    ("yellow_cards", "Cartellini Gialli"),
    ("head_to_head", "Scontri Diretti"),
    ("away_goals", "Gol in Trasferta"),
    ("draw", "Pareggi"),
]

# Mappa per logica di tipo (interno, non usato come choices)
RULE_TYPE_LOGIC = {
    "point_win": "integer",
    "point_draw": "integer",
    "point_loss": "integer",
    "goal_diff": "integer",
    "red_cards": "bool",
    "yellow_cards": "bool",
    "head_to_head": "bool",
    "away_goals": "bool",
    "draw": "bool",
}


class TournamentRule(models.Model):
    tournament = models.ForeignKey('Tournament', on_delete=models.CASCADE, related_name='rules')
    rule_type = models.CharField(max_length=50, choices=RULE_TYPE_CHOICES, help_text="Tipo di regola applicata nel torneo")
    value = models.IntegerField(help_text="Valore della regola, ad esempio 3 punti per vittoria, 1 punto per pareggio, ecc.")
    boolean_value = models.BooleanField(default=False, help_text="Valore booleano per regole che richiedono un attivo/passivo")
    priority = models.PositiveIntegerField(default=0, help_text="Priorità della regola, più basso è il numero, più alta è la priorità")
    is_active = models.BooleanField(default=True, help_text="Indica se la regola è attiva")
    description = models.TextField(blank=True, help_text="Descrizione della regola")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('tournament', 'rule_type')

    def save(self, *args, **kwargs):
        logic_type = RULE_TYPE_LOGIC.get(self.rule_type)

        if logic_type == "integer" and not isinstance(self.value, int):
            raise ValueError("Il valore deve essere un intero per le regole di tipo 'integer'")

        if logic_type == "bool" and not isinstance(self.boolean_value, bool):
            raise ValueError("Il valore deve essere un booleano per le regole di tipo 'bool'")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tournament.name} - {self.rule_type} ({self.value}) {'(Attiva)' if self.is_active else '(Inattiva)'}"


class SeasonTeam(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='season_teams')
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='season_teams')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('team', 'tournament')

    def __str__(self):
        return f"{self.team.name} - {self.tournament.season.year}"


class TournamentRanking(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='tournament_rankings')
    team = models.ForeignKey(SeasonTeam, on_delete=models.CASCADE, related_name='team_tournament_rankings')
    win = models.PositiveIntegerField(default=0, help_text="Numero di vittorie")
    draw = models.PositiveIntegerField(default=0, help_text="Numero di pareggi")
    loss = models.PositiveIntegerField(default=0, help_text="Numero di sconfitte")
    win_penalty = models.PositiveIntegerField(default=0, help_text="Numero di vittorie ai rigori")
    loss_penalty = models.PositiveIntegerField(default=0, help_text="Numero di sconfitte ai rigori")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('tournament', 'team')

    def total_points(self):
        # Calcola i punti totali in base alle regole del torneo
        points = 0
        rules = self.tournament.rules.filter(is_active=True)

        for rule in rules:
            if rule.rule_type == 'point_win':
                points += self.win * rule.value
            elif rule.rule_type == 'point_draw':
                points += self.draw * rule.value
            elif rule.rule_type == 'point_loss':
                points += self.loss * rule.value
            elif rule.rule_type == 'win_penalty':
                points += self.win_penalty * rule.value
            elif rule.rule_type == 'loss_penalty':
                points -= self.loss_penalty * rule.value

        return points

    def matches_played(self):
        # Calcola il numero di partite giocate dalla squadra nel torneo
        return self.win + self.draw + self.loss + self.win_penalty + self.loss_penalty

    def squad_points(self):
        # Calcola i punti totali della squadra nel torneo
        return self.total_points()

    def squad_goals(self):
        # Calcola i gol totali della squadra nel torneo
        performances = self.team.roster.all()
        total_goals = 0
        for performance in performances:
            total_goals += performance.player.simulatedperformance_set.aggregate(models.Sum('goals'))['goals__sum'] or 0
        return total_goals

    def squad_goals_against(self):
        # Calcola i gol subiti dalla squadra nel torneo
        performances = self.team.roster.all()
        total_goals_against = 0
        for performance in performances:
            total_goals_against += performance.player.simulatedperformance_set.aggregate(models.Sum('goals_against'))['goals_against__sum'] or 0
        return total_goals_against

    def squad_goal_difference(self):
        # Calcola la differenza reti della squadra nel torneo
        return self.squad_goals() - self.squad_goals_against()

    # def squad_ranking(self):
    #     # Calcola la posizione della squadra nella classifica del torneo
    #     rankings = TournamentRanking.objects.filter(tournament=self.tournament).order_by('-total_points', 'team__team__name')
    #     for index, ranking in enumerate(rankings, start=1):
    #         if ranking.team == self.team:
    #             return index
    #     return None

    def squad_ranking(self):
        # Calcola la posizione della squadra nella classifica del torneo
        rankings = list(TournamentRanking.objects.filter(tournament=self.tournament))

        # Ordina manualmente in Python, poiché total_points è un metodo
        rankings.sort(key=lambda r: (-r.total_points(), r.team.team.name))

        for index, ranking in enumerate(rankings, start=1):
            if ranking.team == self.team:
                return index
        return None

    def tourbament_ranking(self):
        # Calcola la classifica completa del torneo
        rankings = TournamentRanking.objects.filter(tournament=self.tournament).order_by('-total_points', 'team__team__name')
        return [(ranking.team.team.name, ranking.total_points(), ranking.squad_ranking()) for ranking in rankings]

    def __str__(self):
        return f"{self.team.team.name} - {self.tournament.name}"


class Player(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='player_profile', help_text="Profilo del giocatore")
    main_role = models.CharField(max_length=20, choices=[('P', 'Portiere'), ('D', 'Difensore'), ('C', 'Centrocampista'), ('A', 'Attaccante')], null=True, blank=True, help_text="Ruolo principale del giocatore")  # Ruolo principale del giocatore
    overall = models.PositiveSmallIntegerField(default=50, help_text="Overall del giocatore, da 1 a 100")  # Overall del giocatore, da 1 a 100
    fanta_value = models.PositiveIntegerField(default=50000, help_text="Valore di fanta-mercato del giocatore")  # Valore di fanta-mercato del giocatore
    value = models.PositiveIntegerField(default=0, help_text="Valore di mercato del giocatore")  # Valore di mercato del giocatore, calcolato in base all'overall e al ruolo

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Giocatore"
        verbose_name_plural = "Giocatori"
        ordering = ['person__name', 'person__surname', 'person__birth_date']

    def save(self, *args, **kwargs):
        if not self.overall:
            self.overall = self.calculate_overall() or 50  # Calcola l'overall prima di salvare

        # Calcola il valore di mercato prima di salvare
        if not self.fanta_value:
            self.fanta_value = int(self.calculate_fanta_value())

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

    def calculate_fanta_value(self):
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
        age = self.person.age()
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
        return f"{self.person.name} ({self.main_role}) - {self.person.main_nationality.name}"


class RosterSlot(models.Model):
    team = models.ForeignKey(SeasonTeam, on_delete=models.CASCADE, related_name='roster')
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    is_starting = models.BooleanField(default=False)  # titolare o panchina
    role = models.CharField(max_length=20, choices=[('P', 'Portiere'), ('D', 'Difensore'), ('C', 'Centrocampista'), ('A', 'Attaccante')], default='C')
    shirt_number = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [
            ('team', 'player'),
            ('team', 'shirt_number'),
        ]
        ordering = ['team', 'shirt_number']

    def __str__(self):
        return f"{self.player.name} ({self.role}) - {self.team.team.name} {'(Titolare)' if self.is_starting else '(Panchina)'}"


class Formations(models.Model):
    team = models.ForeignKey(SeasonTeam, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    tactic_name = models.CharField(max_length=100, default="4-3-3", help_text="Nome della formazione, es. '4-3-3', '3-5-2', ecc.")
    is_default_formation = models.BooleanField(default=False, help_text="Indica se questa è la formazione predefinita per il torneo")
    default_formation = models.ForeignKey('DefaultFormation', on_delete=models.SET_NULL, null=True, blank=True, related_name='default_formations', help_text="Formazione predefinita associata")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('team', 'tournament', 'tactic_name')
        ordering = ['team', 'tournament', 'tactic_name']
        verbose_name = "Formazione"
        verbose_name_plural = "Formazioni"

    def save(self, *args, **kwargs):
        if self.is_default_formation and not self.default_formation:
            # Se è una formazione predefinita, assicurati che esista una DefaultFormation
            default_formation, created = DefaultFormation.objects.get_or_create(name=self.tactic_name, formation=self.tactic_name, description=f"Formazione predefinita per {self.tactic_name}")
            self.default_formation = default_formation

        elif not self.is_default_formation and self.default_formation:
            # Se non è una formazione predefinita, rimuovi il riferimento alla DefaultFormation
            self.default_formation = None
            # Assicurati che il nome della formazione sia unico per la combinazione di squadra e torneo
            if not self.tactic_name:
                self.tactic_name = "4-3-3"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Formazione: {self.tactic_name} - {self.team.name} ({self.tournament.name})"


class DefaultFormation(models.Model):
    name = models.CharField(max_length=100, unique=True)
    formation = models.CharField(max_length=100, help_text="Formazione in formato '4-3-3', '3-5-2', ecc.")
    description = models.TextField(blank=True, help_text="Descrizione della formazione")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Staff(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='staff_profile', help_text="Profilo del membro dello staff")
    team = models.ForeignKey(SeasonTeam, on_delete=models.CASCADE, related_name='staff')
    role = models.CharField(max_length=50, choices=[('Coach', 'Allenatore'), ('Scout', 'Osservatore')], help_text="Ruolo del membro dello staff")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.person.name} - {self.role} ({self.team.team.name})"


class Transfer(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    from_team = models.ForeignKey(SeasonTeam, on_delete=models.CASCADE, related_name='transfers_out')
    to_team = models.ForeignKey(SeasonTeam, on_delete=models.CASCADE, related_name='transfers_in')
    fee = models.DecimalField(max_digits=6, decimal_places=2, help_text="Quota di trasferimento pagata per il giocatore")
    transfer_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('player', 'from_team', 'to_team', 'transfer_date')

    def __str__(self):
        return f"{self.player.person.name} transferred from {self.from_team.team.name} to {self.to_team.team.name} for {self.fee} on {self.transfer_date}"


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


class MatchEvent(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='events')
    minute = models.PositiveIntegerField()
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True)
    team = models.ForeignKey(SeasonTeam, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=20, choices=[
        ('goal', 'Goal'),
        ('assist', 'Assist'),
        ('yellow_card', 'Ammonizione'),
        ('red_card', 'Espulsione'),
        ('substitution', 'Sostituzione'),
        ('injury', 'Infortunio'),
        ('penalty', 'Rigore'),
        ('own_goal', 'Autogol'),
        ('foul', 'Fallo'),
        ('corner', 'Calcio d\'angolo'),
        ('offside', 'Fuorigioco'),
        ('save', 'Parata'),
        ('clearance', 'Rinvio')
        # ...
    ])
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['minute']
        unique_together = ('match', 'minute', 'event_type', 'player')

    def __str__(self):
        return f"{self.event_type} at {self.minute}' - {self.match.home_team.name} vs {self.match.away_team.name} ({self.player.name if self.player else 'N/A'})"


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

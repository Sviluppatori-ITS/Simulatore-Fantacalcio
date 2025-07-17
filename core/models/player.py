from django.db import models
from .person import Person


class Player(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='player_profile', help_text="Profilo del giocatore")
    main_role = models.CharField(max_length=20, choices=[('P', 'Portiere'), ('D', 'Difensore'), ('C', 'Centrocampista'), ('A', 'Attaccante')], null=True, blank=True, help_text="Ruolo principale del giocatore")
    overall = models.PositiveSmallIntegerField(default=50, help_text="Overall del giocatore, da 1 a 100")
    fanta_value = models.PositiveIntegerField(default=50000, help_text="Valore di fanta-mercato del giocatore")
    value = models.PositiveIntegerField(default=0, help_text="Valore di mercato del giocatore")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Giocatore"
        verbose_name_plural = "Giocatori"
        ordering = ['person__name', 'person__surname', 'person__birth_date']

    def save(self, *args, **kwargs):
        if not self.overall:
            self.overall = self.calculate_overall() or 50

        if not self.fanta_value:
            self.fanta_value = int(self.calculate_fanta_value())

        super().save(*args, **kwargs)

    def calculate_overall(self):
        performances = self.simulatedperformance_set.all()

        if not performances.exists():
            return 50

        avg_rating = performances.aggregate(models.Avg("rating"))["rating__avg"] or 0
        goal_bonus = performances.aggregate(models.Sum("goals"))["goals__sum"] or 0
        assist_bonus = performances.aggregate(models.Sum("assists"))["assists__sum"] or 0

        raw_score = avg_rating * 10 + goal_bonus * 2 + assist_bonus
        normalized = min(100, max(1, round(raw_score)))
        return normalized

    def calculate_fanta_value(self):
        base_value = self.overall * 1000

        role_multiplier = {
            'P': 1.2,
            'D': 1.1,
            'C': 1.0,
            'A': 1.3
        }

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

        return base_value * role_multiplier.get(self.main_role, 1.0)

    def __str__(self):
        return f"{self.person.name} ({self.main_role}) - {self.person.main_nationality.name if self.person.main_nationality else 'N/A'}"

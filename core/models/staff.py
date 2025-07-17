from django.db import models
from .person import Person
from .season_team import SeasonTeam


class Staff(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='staff_profile', help_text="Profilo del membro dello staff")
    team = models.ForeignKey(SeasonTeam, on_delete=models.CASCADE, related_name='staff')
    role = models.CharField(max_length=50, choices=[('Coach', 'Allenatore'), ('Scout', 'Osservatore')], help_text="Ruolo del membro dello staff")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.person.name} - {self.role} ({self.team.team.name})"

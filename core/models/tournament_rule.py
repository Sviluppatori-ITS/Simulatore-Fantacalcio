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

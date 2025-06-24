from django.contrib import admin
from .models import League, Team, Nationality, Player

admin.site.register(League)
admin.site.register(Team)
admin.site.register(Nationality)
admin.site.register(Player)

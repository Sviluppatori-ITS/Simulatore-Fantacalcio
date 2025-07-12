from django.contrib import admin
from . import models
from django.contrib.auth.models import User


@admin.register(models.Continent)
class ContinentAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")
    ordering = ("code",)


@admin.register(models.Nationality)
class NationalityAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "continent")
    search_fields = ("name", "code", "continent__name")
    ordering = ("code",)


@admin.register(models.Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("name", "surname", "birth_date", "main_nationality")
    search_fields = ("name", "surname")
    list_filter = ("main_nationality",)


@admin.register(models.Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "owner")
    search_fields = ("name",)
    list_filter = ("owner",)


@admin.register(models.League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ("name", "owner")
    search_fields = ("name",)
    list_filter = ("owner",)


@admin.register(models.Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ("league", "year", "is_active")
    list_filter = ("league", "is_active")
    search_fields = ("league__name",)


@admin.register(models.Trophy)
class TrophyAdmin(admin.ModelAdmin):
    list_display = ("name", "awarded_to")
    search_fields = ("name", "awarded_to__team__name")
    list_filter = ("awarded_to",)


@admin.register(models.TournamentStructure)
class TournamentStructureAdmin(admin.ModelAdmin):
    list_display = ("is_cup", "use_groups", "home_and_away")
    list_filter = ("is_cup", "use_groups")


@admin.register(models.Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ("name", "season", "current_match_day")
    search_fields = ("name",)
    list_filter = ("season", "structure")


@admin.register(models.TournamentRule)
class TournamentRuleAdmin(admin.ModelAdmin):
    list_display = ("tournament", "rule_type", "value", "boolean_value", "priority", "is_active")
    list_filter = ("tournament", "is_active")


@admin.register(models.TournamentQualificationRule)
class TournamentQualificationRuleAdmin(admin.ModelAdmin):
    list_display = ("from_tournament", "to_tournament", "min_rank", "max_rank")


@admin.register(models.SeasonTeam)
class SeasonTeamAdmin(admin.ModelAdmin):
    list_display = ("team", "tournament")
    list_filter = ("tournament",)


@admin.register(models.Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("person", "main_role", "overall", "fanta_value")
    list_filter = ("main_role", "main_nationality")
    search_fields = ("person__name", "person__surname")


@admin.register(models.PlayerStatistics)
class PlayerStatisticsAdmin(admin.ModelAdmin):
    list_display = ("player", "matches_played", "goals_scored", "assists_made")
    search_fields = ("player__person__name",)


@admin.register(models.RosterSlot)
class RosterSlotAdmin(admin.ModelAdmin):
    list_display = ("team", "player", "is_starting", "role", "shirt_number")
    list_filter = ("role", "is_starting")


@admin.register(models.Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ("person", "team", "role")
    list_filter = ("role",)


@admin.register(models.Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ("user", "team")


@admin.register(models.Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("home_team", "away_team", "home_score", "away_score", "played", "tournament")
    list_filter = ("played", "tournament")
    search_fields = ("home_team__name", "away_team__name")


@admin.register(models.MatchHistory)
class MatchHistoryAdmin(admin.ModelAdmin):
    list_display = ("player", "match", "rating", "goals", "assists")
    search_fields = ("player__person__name",)


@admin.register(models.MatchEvent)
class MatchEventAdmin(admin.ModelAdmin):
    list_display = ("match", "minute", "event_type", "player", "team")
    list_filter = ("event_type",)
    search_fields = ("player__person__name", "match__home_team__name", "match__away_team__name")


@admin.register(models.Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ("tournament", "label", "match_day", "knockout_stage")
    list_filter = ("tournament", "knockout_stage")


@admin.register(models.Ranking)
class RankingAdmin(admin.ModelAdmin):
    list_display = ("team", "tournament", "rank", "points")
    list_filter = ("tournament",)
    ordering = ("tournament", "rank")


@admin.register(models.Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ("player", "from_team", "to_team", "fee", "transfer_date")
    list_filter = ("transfer_date",)
    search_fields = ("player__person__name",)


@admin.register(models.DefaultFormation)
class DefaultFormationAdmin(admin.ModelAdmin):
    list_display = ("name", "formation")
    search_fields = ("name",)


@admin.register(models.Formations)
class FormationsAdmin(admin.ModelAdmin):
    list_display = ("team", "tournament", "tactic_name", "is_default_formation")
    list_filter = ("tournament", "is_default_formation")
    search_fields = ("team__team__name", "tactic_name")

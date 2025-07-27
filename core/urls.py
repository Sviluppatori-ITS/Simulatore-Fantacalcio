"""
    Inserire qui le root degli url delle pagine del sito per quanto riguarda la parte delle api
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (ContinentViewSet, LeagueViewSet, NationalityViewSet,
                    PlayerViewSet, RegisterView, SeasonViewSet, TeamViewSet,
                    TournamentStructureViewSet, TournamentViewSet, TrophyViewSet, SeasonTeamViewSet)

router = DefaultRouter()
router.register(r'leagues', LeagueViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'nationalities', NationalityViewSet)
router.register(r'continent', ContinentViewSet)
router.register(r'season', SeasonViewSet)
router.register(r'tournament_structure', TournamentStructureViewSet)
router.register(r'tournament', TournamentViewSet)
router.register(r'trophy', TrophyViewSet)
router.register(r'player', PlayerViewSet)
router.register(r'season_team', SeasonTeamViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
]

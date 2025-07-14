from django.urls import path, include
from .views import RegisterView
from rest_framework.routers import DefaultRouter
from .views import LeagueViewSet, TeamViewSet, NationalityViewSet, ContinentViewSet, TrophyViewSet, TournamentStructureViewSet, SeasonViewSet

router = DefaultRouter()
router.register(r'leagues', LeagueViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'nationalities', NationalityViewSet)
router.register(r'continent', ContinentViewSet)
router.register(r'season', SeasonViewSet)
router.register(r'tounament_structure', TournamentStructureViewSet)
router.register(r'trophy', TrophyViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
]

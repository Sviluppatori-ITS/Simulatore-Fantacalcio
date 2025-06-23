from django.urls import path, include
from .views import RegisterView
from rest_framework.routers import DefaultRouter
from .views import LeagueViewSet, TeamViewSet

router = DefaultRouter()
router.register(r'leagues', LeagueViewSet)
router.register(r'teams', TeamViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
]

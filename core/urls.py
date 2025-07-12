from django.urls import path, include
from .views import RegisterView
from rest_framework.routers import DefaultRouter
from .views import LeagueViewSet, TeamViewSet, NationalityViewSet

router = DefaultRouter()
router.register(r'leagues', LeagueViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'nationalities', NationalityViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
]

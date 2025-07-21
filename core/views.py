from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.serializers import ModelSerializer

from core.filters.player_filter import PlayerFilter
from core.logger import get_logger

from django.contrib.auth.models import User
from .models import (Continent, League, Nationality, Player, Season, Team,
                     TournamentStructure, Trophy, SeasonTeam, Tournament)
from .serializers import (ContinentSerializer, LeagueSerializer,
                          NationalitySerializer, PlayerSerializer,
                          SeasonSerializer, TeamSerializer,
                          TournamentStructureSerializer, TrophySerializer,
                          SeasonTeamSerializer, TournamentSerializer,
                          UserSerializer)

logger = get_logger()

# IsAuthenticated or AllowAny based on your needs
permission = AllowAny


class LeagueViewSet(viewsets.ModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer
    permission_classes = [permission]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permission]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class SeasonTeamViewSet(viewsets.ModelViewSet):
    queryset = SeasonTeam.objects.all()
    serializer_class = SeasonTeamSerializer
    permission_classes = [permission]


class ContinentViewSet(viewsets.ModelViewSet):
    queryset = Continent.objects.all()
    serializer_class = ContinentSerializer
    permission_classes = [permission]


class NationalityViewSet(viewsets.ModelViewSet):
    queryset = Nationality.objects.all()
    serializer_class = NationalitySerializer
    permission_classes = [permission]


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [permission]
    filter_backends = [DjangoFilterBackend]
    filterset_class = PlayerFilter

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class SeasonViewSet(viewsets.ModelViewSet):
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer
    permission_classes = [permission]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TrophyViewSet(viewsets.ModelViewSet):
    queryset = Trophy.objects.all()
    serializer_class = TrophySerializer
    permission_classes = [permission]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TournamentStructureViewSet(viewsets.ModelViewSet):
    queryset = TournamentStructure.objects.all()
    serializer_class = TournamentStructureSerializer
    permission_classes = [permission]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    permission_classes = [permission]

    def perform_create(self, serializer):
        return super().perform_create(serializer)

    def perform_update(self, serializer):
        return super().perform_update(serializer)


class RegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

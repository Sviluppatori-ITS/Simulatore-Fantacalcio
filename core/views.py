from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, generics
from rest_framework.serializers import ModelSerializer
from rest_framework.permissions import AllowAny
from .models import League, Team, User, Nationality, Player, Continent, Season, Trophy, TournamentStructure
from .serializers import LeagueSerializer, TeamSerializer, NationalitySerializer, PlayerSerializer, ContinentSerializer, SeasonSerializer, TrophySerializer, TournamentStructureSerializer, UserSerializer
import logging

permission = AllowAny  # IsAuthenticated or AllowAny based on your needs


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
    permission_classes = [AllowAny]

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

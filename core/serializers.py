from rest_framework import serializers
from .models import League, Team, Nationality, Player, Continent, PlayerStatistics, Season, Trophy, TournamentStructure
from django.contrib.auth.models import User


class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = League
        fields = '__all__'


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'


class ContinentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Continent
        fields = '__all__'


class ContinentNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Continent
        fields = ['id', 'name', 'code']  # o altri campi utili


class NationalitySerializer(serializers.ModelSerializer):
    # Se passi un id, userà quello. Se passi un oggetto, lo crea se non esistente.
    continent = serializers.PrimaryKeyRelatedField(
        queryset=Continent.objects.all(),
        required=False,
        allow_null=True
    )
    # In lettura, mostriamo i dettagli
    continent_info = ContinentNestedSerializer(source='continent', read_only=True)

    class Meta:
        model = Nationality
        fields = ['id', 'name', 'code', 'continent', 'continent_info']

    def create(self, validated_data):
        continent = validated_data.pop('continent', None)
        # Se continent è un dict, allora è stato passato un oggetto
        if isinstance(continent, dict):
            continent = Continent.objects.create(**continent)
        nationality = Nationality.objects.create(continent=continent, **validated_data)
        return nationality


class PlayerSerializer(serializers.ModelSerializer):
    main_nationality = NationalitySerializer()
    other_nationalities = NationalitySerializer(many=True)
    team = TeamSerializer()
    old_team_name = TeamSerializer(many=True, read_only=True)

    class Meta:
        model = Player
        fields = '__all__'

    def create(self, validated_data):
        main_nationality_data = validated_data.pop('main_nationality')
        other_nationalities_data = validated_data.pop('other_nationalities', [])
        team_data = validated_data.pop('team')
        old_team_name_data = validated_data.pop('old_team_name', [])


class PlayerStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerStatistics
        fields = '__all__'


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = '__all__'


class TrophySerializer(serializers.ModelSerializer):
    class Meta:
        model = Trophy
        fields = '__all__'


class TournamentStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = TournamentStructure
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

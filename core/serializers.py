from rest_framework import serializers
from .models import League, Team, Nationality, Player, Continent, PlayerStatistics, Season, Trophy, TournamentStructure, Person
from django.contrib.auth.models import User


class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = League
        fields = '__all__'


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'


class TeamNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name', 'code']


class ContinentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Continent
        fields = '__all__'


class ContinentNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Continent
        fields = ['id', 'name', 'code']  # o altri campi utili


class NationalitySerializer(serializers.ModelSerializer):
    continent_info = ContinentNestedSerializer(source='continent', read_only=True)
    continent = serializers.SerializerMethodField()

    class Meta:
        model = Nationality
        fields = ['id', 'name', 'code', 'continent', 'continent_info']

    def get_continent(self, obj):
        return obj.continent.id if obj.continent else None

    def to_internal_value(self, data):
        if isinstance(data, dict):
            continent_data = data.pop('continent', None)
            if continent_data and isinstance(continent_data, dict):
                continent, _ = Continent.objects.get_or_create(**continent_data)
                data['continent'] = continent.id
            else:
                data['continent'] = continent_data
        return super().to_internal_value(data)


class PersonSerializer(serializers.ModelSerializer):
    main_nationality = serializers.PrimaryKeyRelatedField(
        queryset=Nationality.objects.all(),
        required=False,
        allow_null=True
    )
    other_nationalities = serializers.PrimaryKeyRelatedField(
        queryset=Nationality.objects.all(),
        many=True,
        required=False
    )

    # Per lettura dettagliata
    main_nationality_info = NationalitySerializer(source='main_nationality', read_only=True)
    other_nationalities_info = NationalitySerializer(source='other_nationalities', many=True, read_only=True)

    class Meta:
        model = Person
        fields = [
            'id', 'name', 'birth_date',
            'main_nationality', 'other_nationalities',
            'main_nationality_info', 'other_nationalities_info'
        ]

    def create(self, validated_data):
        other_nationalities_data = validated_data.pop('other_nationalities', [])
        person = Person.objects.create(**validated_data)
        person.other_nationalities.set(other_nationalities_data)
        return person

    def update(self, instance, validated_data):
        other_nationalities_data = validated_data.pop('other_nationalities', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if other_nationalities_data is not None:
            instance.other_nationalities.set(other_nationalities_data)
        return instance


class PlayerSerializer(serializers.ModelSerializer):
    person = PersonSerializer()
    team = TeamSerializer()
    old_team_name = TeamNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Player
        fields = '__all__'

    def create(self, validated_data):
        person_data = validated_data.pop('person')
        team_data = validated_data.pop('team')

        # Gestione PERSON
        person_serializer = PersonSerializer(data=person_data)
        person_serializer.is_valid(raise_exception=True)
        person = person_serializer.save()

        # Gestione TEAM
        if isinstance(team_data, dict):
            team, _ = Team.objects.get_or_create(**team_data)
        else:
            team = Team.objects.get(id=team_data)

        # Crea PLAYER
        player = Player.objects.create(
            person=person,
            team=team,
            **validated_data
        )

        return player


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

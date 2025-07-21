from django.contrib.auth.models import User
from rest_framework import serializers


# from .models import League, Team, Nationality, Player, Continent, PlayerStatistics, Season, Trophy, TournamentStructure, Person
from . import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.League
        fields = '__all__'


class TeamSerializer(serializers.ModelSerializer):
    owner = UserSerializer()

    class Meta:
        model = models.Team
        fields = '__all__'

    def create(self, validate_data):
        owner_data = validate_data.pop('owner')
        owner = User.objects.get_or_create(**owner_data)[0]

        team = models.Team.objects.create(
            owner=owner,
            **validate_data
        )

        return team


class TeamNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Team
        fields = ['id', 'name', 'code']


class SeasonTeamSerializer(serializers.ModelSerializer):
    team = TeamSerializer()

    class Meta:
        model = models.SeasonTeam
        fields = '__all__'

    def create(self, validated_data):
        team_data = validated_data.pop('team')

        team = models.Team.objects.get_or_create(**team_data)[0]

        season_team = models.SeasonTeam.objects.create(
            team=team,
            **validated_data
        )

        return season_team


class ContinentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Continent
        fields = '__all__'


class ContinentNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Continent
        fields = ['id', 'name', 'code']  # o altri campi utili


class NationalitySerializer(serializers.ModelSerializer):
    continent_info = ContinentNestedSerializer(source='continent', read_only=True)

    class Meta:
        model = models.Nationality
        fields = ['id', 'name', 'code', 'continent', 'continent_info']

    def to_internal_value(self, data):
        if isinstance(data, dict):
            continent_data = data.pop('continent', None)
            if continent_data and isinstance(continent_data, dict):
                continent, _ = models.Continent.objects.get_or_create(**continent_data)
                data['continent'] = continent.id
            else:
                data['continent'] = continent_data
        return super().to_internal_value(data)


class PersonSerializer(serializers.ModelSerializer):
    main_nationality = serializers.PrimaryKeyRelatedField(
        queryset=models.Nationality.objects.all(),
        required=False,
        allow_null=True
    )
    other_nationalities = serializers.PrimaryKeyRelatedField(
        queryset=models.Nationality.objects.all(),
        many=True,
        required=False
    )

    # Per lettura dettagliata
    main_nationality_info = NationalitySerializer(source='main_nationality', read_only=True)
    other_nationalities_info = NationalitySerializer(source='other_nationalities', many=True, read_only=True)

    class Meta:
        model = models.Person
        fields = [
            'id', 'name', 'surname', 'birth_date',
            'main_nationality', 'other_nationalities',
            'main_nationality_info', 'other_nationalities_info'
        ]

    def create(self, validated_data):
        other_nationalities_data = validated_data.pop('other_nationalities', [])
        person = models.Person.objects.create(**validated_data)
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
    old_team_name = TeamNestedSerializer(many=True, read_only=True)

    class Meta:
        model = models.Player
        fields = '__all__'

    def create(self, validated_data):
        person_data = validated_data.pop('person')

        # Gestione PERSON
        person_serializer = PersonSerializer(data=person_data)
        person_serializer.is_valid(raise_exception=True)
        person = person_serializer.save()

        # Crea PLAYER
        player = models.Player.objects.create(
            person=person,
            **validated_data
        )

        return player


class PlayerStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PlayerStatistics
        fields = '__all__'


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Season
        fields = '__all__'


class TrophySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Trophy
        fields = '__all__'


class TournamentStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TournamentStructure
        fields = '__all__'


class FormationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Formation
        fields = '__all__'


class DefaultFormationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DefaultFormation
        fields = '__all__'


class MatchSerializer(serializers.ModelSerializer):
    home_team = TeamSerializer()
    away_team = TeamSerializer()

    class Meta:
        model = models.Match
        fields = '__all__'

    def create(self, validated_data):
        home_team_data = validated_data.pop('home_team')
        away_team_data = validated_data.pop('away_team')

        try:
            home_team = models.Team.objects.get(**home_team_data)
        except models.Team.DoesNotExist:
            raise serializers.ValidationError({'home_team': 'Team non trovato'})

        try:
            away_team = models.Team.objects.get(**away_team_data)
        except models.Team.DoesNotExist:
            raise serializers.ValidationError({'away_team': 'Team non trovato'})

        validated_data['home_team'] = home_team
        validated_data['away_team'] = away_team

        return models.Match.objects.create(**validated_data)


class TournamentSerializer(serializers.ModelSerializer):
    structure = TournamentStructureSerializer()
    season = SeasonSerializer()
    teams = TeamSerializer(many=True)
    trophy = TrophySerializer()

    class Meta:
        model = models.Tournament
        fields = '__all__'

    def create(self, validated_data):
        structure_data = validated_data.pop('structure')
        season_data = validated_data.pop('season')
        trophy_data = validated_data.pop('trophy')
        teams_data = validated_data.pop('teams')

        structure = models.TournamentStructure.objects.get_or_create(**structure_data)[0]
        season = models.Season.objects.get_or_create(**season_data)[0]
        trophy = models.Trophy.objects.get_or_create(**trophy_data)[0]

        tournament = models.Tournament.objects.create(
            structure=structure,
            season=season,
            trophy=trophy,
            **validated_data
        )

        for team_data in teams_data:
            team, _ = models.Team.objects.get_or_create(**team_data)
            tournament.teams.add(team)

        return tournament

    def update(self, instance, validated_data):
        structure_data = validated_data.pop('structure', None)
        season_data = validated_data.pop('season', None)
        trophy_data = validated_data.pop('trophy', None)
        teams_data = validated_data.pop('teams', None)

        # Aggiorna o crea struttura
        if structure_data:
            structure, _ = models.TournamentStructure.objects.get_or_create(**structure_data)
            instance.structure = structure

        # Aggiorna o crea season
        if season_data:
            season, _ = models.Season.objects.get_or_create(**season_data)
            instance.season = season

        # Aggiorna o crea trophy
        if trophy_data:
            trophy, _ = models.Trophy.objects.get_or_create(**trophy_data)
            instance.trophy = trophy

        # Aggiorna altri campi semplici
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # Aggiorna relazione ManyToMany con i team
        if teams_data is not None:
            team_instances = []
            for team_data in teams_data:
                team, _ = models.Team.objects.get_or_create(**team_data)
                team_instances.append(team)
            instance.teams.set(team_instances)  # sostituisce tutti i team

        return instance

from rest_framework import serializers
from .models import League, Team, Nationality, Player


class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = League
        fields = '__all__'


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'


class NationalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Nationality
        fields = '__all__'


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

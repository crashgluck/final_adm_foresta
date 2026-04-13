from rest_framework import serializers

from apps.core.parcel_display import get_parcel_owner_display
from apps.missions.models import DroneFlight, Mission, MissionReport
from apps.parcels.models import Parcel
from apps.people.models import Person


class MissionSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(source='parcela', queryset=Parcel.objects.all(), required=False, allow_null=True)
    persona_id = serializers.PrimaryKeyRelatedField(source='persona', queryset=Person.objects.all(), required=False, allow_null=True)
    owner_display = serializers.SerializerMethodField()
    owner_parcel_code = serializers.SerializerMethodField()
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True)

    class Meta:
        model = Mission
        fields = [
            'id',
            'title',
            'description',
            'mission_type',
            'owner',
            'owner_display',
            'owner_parcel_code',
            'persona_id',
            'team_name',
            'assigned_to',
            'assigned_to_username',
            'status',
            'scheduled_for',
            'started_at',
            'completed_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_owner_parcel_code(self, obj):
        code, _ = get_parcel_owner_display(obj.parcela)
        return code

    def get_owner_display(self, obj):
        _, display = get_parcel_owner_display(obj.parcela)
        return display


class DroneFlightSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(source='parcela', queryset=Parcel.objects.all(), required=False, allow_null=True)
    persona_id = serializers.PrimaryKeyRelatedField(source='persona', queryset=Person.objects.all(), required=False, allow_null=True)
    pilot_username = serializers.CharField(source='pilot.username', read_only=True)
    owner_display = serializers.SerializerMethodField()
    owner_parcel_code = serializers.SerializerMethodField()

    class Meta:
        model = DroneFlight
        fields = [
            'id',
            'pilot',
            'pilot_username',
            'owner',
            'owner_display',
            'owner_parcel_code',
            'persona_id',
            'flight_datetime',
            'mission_code',
            'team_code',
            'battery_code',
            'takeoff_platform',
            'notes',
            'photo_path',
            'video_path',
            'legacy_source_id',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['legacy_source_id', 'created_at', 'updated_at']

    def get_owner_parcel_code(self, obj):
        code, _ = get_parcel_owner_display(obj.parcela)
        return code

    def get_owner_display(self, obj):
        _, display = get_parcel_owner_display(obj.parcela)
        return display


class MissionReportSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = MissionReport
        fields = [
            'id',
            'mission',
            'created_by',
            'created_by_username',
            'report_date',
            'summary',
            'media_url',
            'media_type',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

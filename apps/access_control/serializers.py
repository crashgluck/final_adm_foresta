from rest_framework import serializers

from apps.access_control.models import AccessRecord, AccessSource, AccessStatus, BlacklistEntry
from apps.core.parcel_display import get_parcel_owner_display
from apps.parcels.models import Parcel
from apps.people.models import Person


class BlacklistEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlacklistEntry
        fields = ['id', 'rut', 'plate', 'reason', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class AccessRecordSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(source='parcela', queryset=Parcel.objects.all(), required=False, allow_null=True)
    persona_id = serializers.PrimaryKeyRelatedField(source='persona', queryset=Person.objects.all(), required=False, allow_null=True)
    owner_display = serializers.SerializerMethodField()
    owner_parcel_code = serializers.SerializerMethodField()

    class Meta:
        model = AccessRecord
        fields = [
            'id',
            'owner',
            'owner_display',
            'owner_parcel_code',
            'persona_id',
            'full_name',
            'rut',
            'plate',
            'motive',
            'company_name',
            'access_datetime',
            'note',
            'card_number',
            'card_color',
            'status',
            'source',
            'created_from',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['status', 'source', 'created_by', 'updated_by', 'created_at', 'updated_at']

    def get_owner_parcel_code(self, obj):
        code, _ = get_parcel_owner_display(obj.parcela)
        return code

    def get_owner_display(self, obj):
        _, display = get_parcel_owner_display(obj.parcela)
        return display

    def create(self, validated_data):
        if not validated_data.get('source'):
            validated_data['source'] = AccessSource.MANUAL
        if not validated_data.get('status'):
            validated_data['status'] = AccessStatus.ALLOWED
        return super().create(validated_data)


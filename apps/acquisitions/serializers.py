from rest_framework import serializers

from apps.acquisitions.models import RFIDCard, RemoteControl, VehicleLogo
from apps.core.parcel_display import get_parcel_owner_display
from apps.parcels.models import Parcel
from apps.people.models import Person


class BaseOwnerSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(source='parcela', queryset=Parcel.objects.all())
    persona_id = serializers.PrimaryKeyRelatedField(source='persona', queryset=Person.objects.all(), required=False, allow_null=True)
    owner_display = serializers.SerializerMethodField()
    owner_parcel_code = serializers.SerializerMethodField()

    def get_owner_parcel_code(self, obj):
        code, _ = get_parcel_owner_display(obj.parcela)
        return code

    def get_owner_display(self, obj):
        _, display = get_parcel_owner_display(obj.parcela)
        return display


class RemoteControlSerializer(BaseOwnerSerializer):
    class Meta:
        model = RemoteControl
        fields = [
            'id',
            'owner',
            'owner_display',
            'owner_parcel_code',
            'persona_id',
            'serial_number',
            'model',
            'status',
            'issued_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class RFIDCardSerializer(BaseOwnerSerializer):
    class Meta:
        model = RFIDCard
        fields = [
            'id',
            'owner',
            'owner_display',
            'owner_parcel_code',
            'persona_id',
            'uid',
            'color',
            'status',
            'issued_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class VehicleLogoSerializer(BaseOwnerSerializer):
    class Meta:
        model = VehicleLogo
        fields = [
            'id',
            'owner',
            'owner_display',
            'owner_parcel_code',
            'persona_id',
            'plate',
            'logo_code',
            'status',
            'issued_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


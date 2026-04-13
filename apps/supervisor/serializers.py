from rest_framework import serializers

from apps.core.parcel_display import get_parcel_owner_display
from apps.parcels.models import Parcel
from apps.people.models import Person
from apps.supervisor.models import NotificationFine, Round, Shift


class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = ['id', 'name', 'supervisor', 'start_datetime', 'end_datetime', 'status', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = ['id', 'shift', 'guard', 'started_at', 'ended_at', 'status', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class NotificationFineSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(source='parcela', queryset=Parcel.objects.all(), required=False, allow_null=True)
    persona_id = serializers.PrimaryKeyRelatedField(source='persona', queryset=Person.objects.all(), required=False, allow_null=True)
    owner_display = serializers.SerializerMethodField()

    class Meta:
        model = NotificationFine
        fields = [
            'id',
            'owner',
            'owner_display',
            'persona_id',
            'shift',
            'title',
            'description',
            'amount',
            'status',
            'issued_at',
            'due_date',
            'paid_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_owner_display(self, obj):
        _, display = get_parcel_owner_display(obj.parcela)
        return display


from rest_framework import serializers

from apps.people.models import Person
from apps.people.serializers import PersonSerializer
from apps.vehicles.models import Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    persona = PersonSerializer(read_only=True)
    persona_id = serializers.PrimaryKeyRelatedField(source='persona', queryset=Person.objects.all(), required=False, allow_null=True, write_only=True)

    class Meta:
        model = Vehicle
        fields = [
            'id',
            'parcela',
            'persona',
            'persona_id',
            'ppu',
            'ppu_normalizado',
            'marca',
            'modelo',
            'tipo',
            'color',
            'codigo_acceso',
            'activo',
            'observaciones',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ('ppu_normalizado', 'created_at', 'updated_at')

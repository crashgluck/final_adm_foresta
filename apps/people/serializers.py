from rest_framework import serializers

from apps.people.models import ParcelOwnership, ParcelResident, Person


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted', 'deleted_at')


class ParcelOwnershipSerializer(serializers.ModelSerializer):
    persona = PersonSerializer(read_only=True)
    persona_id = serializers.PrimaryKeyRelatedField(queryset=Person.objects.all(), source='persona', write_only=True)

    class Meta:
        model = ParcelOwnership
        fields = [
            'id',
            'parcela',
            'persona',
            'persona_id',
            'tipo',
            'is_active',
            'fecha_inicio',
            'fecha_fin',
            'notas',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ('created_at', 'updated_at')


class ParcelResidentSerializer(serializers.ModelSerializer):
    persona = PersonSerializer(read_only=True)
    persona_id = serializers.PrimaryKeyRelatedField(
        queryset=Person.objects.all(), source='persona', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = ParcelResident
        fields = [
            'id',
            'parcela',
            'persona',
            'persona_id',
            'tipo_residencia',
            'is_active',
            'observaciones',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ('created_at', 'updated_at')


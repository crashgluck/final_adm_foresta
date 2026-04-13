from rest_framework import serializers

from apps.notes.models import AdministrativeNote


class AdministrativeNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdministrativeNote
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted', 'deleted_at', 'usuario_registra')


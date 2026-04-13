from rest_framework import serializers

from apps.works.models import ParcelWorkStatus


class ParcelWorkStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParcelWorkStatus
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted', 'deleted_at')


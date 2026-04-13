from rest_framework import serializers

from apps.utilities.models import ServiceCut, ServiceHistory


class ServiceCutSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCut
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted', 'deleted_at')


class ServiceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceHistory
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted', 'deleted_at')


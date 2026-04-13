from rest_framework import serializers

from apps.data_imports.models import ImportIssue, ImportJob, ImportSheetResult


class ImportIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportIssue
        fields = '__all__'


class ImportSheetResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportSheetResult
        fields = '__all__'


class ImportJobSerializer(serializers.ModelSerializer):
    sheet_results = ImportSheetResultSerializer(many=True, read_only=True)

    class Meta:
        model = ImportJob
        fields = '__all__'


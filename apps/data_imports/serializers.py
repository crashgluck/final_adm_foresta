from rest_framework import serializers

from apps.data_imports.models import ImportIssue, ImportJob, ImportSheetResult, ImportUploadSession


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
    issues_count = serializers.SerializerMethodField()

    def get_issues_count(self, obj):
        return obj.issues.count()

    class Meta:
        model = ImportJob
        fields = '__all__'


class ImportUploadSessionSerializer(serializers.ModelSerializer):
    preview_job = ImportJobSerializer(read_only=True)
    executed_job = ImportJobSerializer(read_only=True)

    class Meta:
        model = ImportUploadSession
        fields = '__all__'


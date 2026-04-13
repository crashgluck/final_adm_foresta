from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import UserRole
from apps.core.permissions import RoleBasedActionPermission, has_role_at_least
from apps.data_imports.models import ImportIssue, ImportJob
from apps.data_imports.serializers import ImportIssueSerializer, ImportJobSerializer
from apps.data_imports.services.excel_importer import ExcelMasterImporter


class ImportJobViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ImportJob.objects.all().prefetch_related('sheet_results')
    serializer_class = ImportJobSerializer
    permission_classes = [RoleBasedActionPermission]
    filterset_fields = ['status', 'dry_run', 'initiated_by']
    ordering_fields = ['started_at', 'finished_at', 'status']

    required_roles_per_action = {
        'list': UserRole.ADMINISTRADOR,
        'retrieve': UserRole.ADMINISTRADOR,
        'run': UserRole.OPERADOR,
    }

    @action(detail=False, methods=['post'])
    def run(self, request):
        file_path = request.data.get('file_path')
        if not file_path:
            return Response({'detail': 'file_path es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        sheets = request.data.get('sheets')
        if isinstance(sheets, str):
            sheets = [s.strip() for s in sheets.split(',') if s.strip()]

        dry_run = bool(request.data.get('dry_run', False))
        importer = ExcelMasterImporter(file_path=file_path, dry_run=dry_run, initiated_by=request.user, sheets=sheets)
        job = importer.run()
        return Response(ImportJobSerializer(job).data, status=status.HTTP_201_CREATED)


class ImportIssueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ImportIssue.objects.select_related('import_job', 'sheet_result').all()
    serializer_class = ImportIssueSerializer
    permission_classes = [RoleBasedActionPermission]
    filterset_fields = ['severity', 'sheet_name', 'import_job']
    ordering_fields = ['created_at', 'row_number']

    required_roles_per_action = {
        'list': UserRole.ADMINISTRADOR,
        'retrieve': UserRole.ADMINISTRADOR,
    }


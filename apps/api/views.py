from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserRole
from apps.api.services.dashboard_analytics import DashboardAnalyticsService
from apps.core.permissions import has_role_at_least


class DashboardSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not has_role_at_least(request.user, UserRole.CONSULTA):
            return Response({'detail': 'No autorizado'}, status=403)

        service = DashboardAnalyticsService.from_request(request)
        return Response(service.build())

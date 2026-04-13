from rest_framework import viewsets

from apps.accounts.models import UserActorType, UserRole
from apps.core.permissions import RoleBasedActionPermission
from apps.finance.models import CommonExpenseDebt, FinancialMovement, PaymentAgreement, ServiceDebt, UnpaidFine
from apps.finance.serializers import (
    CommonExpenseDebtSerializer,
    FinancialMovementSerializer,
    PaymentAgreementSerializer,
    ServiceDebtSerializer,
    UnpaidFineSerializer,
)


class CommonExpenseDebtViewSet(viewsets.ModelViewSet):
    queryset = CommonExpenseDebt.objects.select_related('parcela', 'persona').all()
    serializer_class = CommonExpenseDebtSerializer
    permission_classes = [RoleBasedActionPermission]
    search_fields = ['parcela__codigo_parcela']
    filterset_fields = ['parcela', 'estado_pago']
    ordering_fields = ['created_at', 'fecha_corte', 'total_pesos']
    required_roles_per_action = {
        'list': UserRole.CONSULTA,
        'retrieve': UserRole.CONSULTA,
        'create': UserRole.OPERADOR,
        'update': UserRole.OPERADOR,
        'partial_update': UserRole.OPERADOR,
        'destroy': UserRole.ADMINISTRADOR,
    }
    disallowed_actor_types_per_action = {
        '*': [UserActorType.CENTRAL_MONITOREO, UserActorType.PORTAL_ACCESO, UserActorType.OPERADOR_DRONE]
    }


class ServiceDebtViewSet(viewsets.ModelViewSet):
    queryset = ServiceDebt.objects.select_related('parcela', 'persona').all()
    serializer_class = ServiceDebtSerializer
    permission_classes = [RoleBasedActionPermission]
    search_fields = ['parcela__codigo_parcela']
    filterset_fields = ['parcela', 'estado_pago', 'tipo_servicio']
    ordering_fields = ['created_at', 'saldo_total']
    required_roles_per_action = {
        'list': UserRole.CONSULTA,
        'retrieve': UserRole.CONSULTA,
        'create': UserRole.OPERADOR,
        'update': UserRole.OPERADOR,
        'partial_update': UserRole.OPERADOR,
        'destroy': UserRole.ADMINISTRADOR,
    }
    disallowed_actor_types_per_action = {
        '*': [UserActorType.CENTRAL_MONITOREO, UserActorType.PORTAL_ACCESO, UserActorType.OPERADOR_DRONE]
    }


class PaymentAgreementViewSet(viewsets.ModelViewSet):
    queryset = PaymentAgreement.objects.select_related('parcela').all()
    serializer_class = PaymentAgreementSerializer
    permission_classes = [RoleBasedActionPermission]
    search_fields = ['parcela__codigo_parcela', 'empresa', 'tipo', 'detalle']
    filterset_fields = ['parcela', 'estado_pago']
    ordering_fields = ['created_at', 'fecha_vencimiento', 'saldo_monto']
    required_roles_per_action = {
        'list': UserRole.CONSULTA,
        'retrieve': UserRole.CONSULTA,
        'create': UserRole.OPERADOR,
        'update': UserRole.OPERADOR,
        'partial_update': UserRole.OPERADOR,
        'destroy': UserRole.ADMINISTRADOR,
    }
    disallowed_actor_types_per_action = {
        '*': [UserActorType.CENTRAL_MONITOREO, UserActorType.PORTAL_ACCESO, UserActorType.OPERADOR_DRONE]
    }


class UnpaidFineViewSet(viewsets.ModelViewSet):
    queryset = UnpaidFine.objects.select_related('parcela').all()
    serializer_class = UnpaidFineSerializer
    permission_classes = [RoleBasedActionPermission]
    search_fields = ['parcela__codigo_parcela', 'empresa', 'tipo', 'detalle']
    filterset_fields = ['parcela', 'estado_pago']
    ordering_fields = ['created_at', 'fecha_vencimiento', 'saldo_monto']
    required_roles_per_action = {
        'list': UserRole.CONSULTA,
        'retrieve': UserRole.CONSULTA,
        'create': UserRole.OPERADOR,
        'update': UserRole.OPERADOR,
        'partial_update': UserRole.OPERADOR,
        'destroy': UserRole.ADMINISTRADOR,
    }
    disallowed_actor_types_per_action = {
        '*': [UserActorType.CENTRAL_MONITOREO, UserActorType.PORTAL_ACCESO, UserActorType.OPERADOR_DRONE]
    }


class FinancialMovementViewSet(viewsets.ModelViewSet):
    queryset = FinancialMovement.objects.select_related('parcela', 'persona').all()
    serializer_class = FinancialMovementSerializer
    permission_classes = [RoleBasedActionPermission]
    search_fields = ['parcela__codigo_parcela', 'persona__nombre_completo', 'reference', 'description', 'source_label']
    filterset_fields = ['parcela', 'movement_type', 'category', 'is_confirmed', 'payment_method']
    ordering_fields = ['occurred_at', 'created_at', 'amount']
    required_roles_per_action = {
        'list': UserRole.CONSULTA,
        'retrieve': UserRole.CONSULTA,
        'create': UserRole.OPERADOR,
        'update': UserRole.OPERADOR,
        'partial_update': UserRole.OPERADOR,
        'destroy': UserRole.ADMINISTRADOR,
    }
    disallowed_actor_types_per_action = {
        '*': [UserActorType.CENTRAL_MONITOREO, UserActorType.PORTAL_ACCESO, UserActorType.OPERADOR_DRONE]
    }


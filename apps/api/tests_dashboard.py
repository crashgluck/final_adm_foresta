from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User, UserRole
from apps.finance.models import (
    CommonExpenseDebt,
    FinancialMovement,
    FinancialMovementCategory,
    FinancialMovementType,
    PaymentStatus,
)
from apps.maps_app.models import Visit
from apps.parcels.models import Parcel
from apps.people.models import ParcelResident, ResidentType
from apps.vehicles.models import Vehicle


class DashboardAnalyticsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='dash@test.com', password='Pass123456', role=UserRole.CONSULTA)
        login = self.client.post('/api/v1/auth/login/', {'email': self.user.email, 'password': 'Pass123456'}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        self.parcel_active = Parcel.objects.create(codigo_parcela='A-01', estado='ACTIVA')
        self.parcel_inactive = Parcel.objects.create(codigo_parcela='B-02', estado='INACTIVA')

        CommonExpenseDebt.objects.create(
            parcela=self.parcel_active,
            numero_gastos_comunes=2,
            total_pesos=Decimal('120000'),
            estado_pago=PaymentStatus.PENDIENTE,
        )
        CommonExpenseDebt.objects.create(
            parcela=self.parcel_inactive,
            numero_gastos_comunes=1,
            total_pesos=Decimal('50000'),
            estado_pago=PaymentStatus.PAGADO,
        )

        ParcelResident.objects.create(parcela=self.parcel_active, tipo_residencia=ResidentType.RESIDENTE, is_active=True)
        Vehicle.objects.create(parcela=self.parcel_active, ppu='AA1111', activo=True)

        now = timezone.now()
        FinancialMovement.objects.create(
            parcela=self.parcel_active,
            movement_type=FinancialMovementType.INCOME,
            category=FinancialMovementCategory.PAYMENT_GC,
            amount=Decimal('75000'),
            occurred_at=now,
            is_confirmed=True,
        )
        FinancialMovement.objects.create(
            parcela=self.parcel_active,
            movement_type=FinancialMovementType.EXPENSE,
            category=FinancialMovementCategory.OPERATIONAL_EXPENSE,
            amount=Decimal('12000'),
            occurred_at=now,
            is_confirmed=True,
        )
        FinancialMovement.objects.create(
            parcela=self.parcel_active,
            movement_type=FinancialMovementType.INCOME,
            category=FinancialMovementCategory.PAYMENT_SERVICE,
            amount=Decimal('25000'),
            occurred_at=now - timedelta(days=1),
            is_confirmed=True,
        )

        Visit.objects.create(
            parcela=self.parcel_active,
            visitor_name='Visita test',
            purpose='Revisión',
            visit_datetime=now,
        )

    def test_dashboard_resumen_retorna_estructura_analitica(self):
        response = self.client.get('/api/v1/dashboard/resumen/?preset=last_7_days')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('kpis', response.data)
        self.assertIn('charts', response.data)
        self.assertIn('smart_indicators', response.data)
        self.assertIn('insights', response.data)
        self.assertIn('alerts', response.data)
        self.assertIn('rankings', response.data)

        self.assertGreaterEqual(response.data['kpis']['parcels_total'], 2)
        self.assertGreaterEqual(response.data['kpis']['pending_total'], 120000)
        self.assertGreaterEqual(response.data['kpis']['payments_today'], 1)
        self.assertGreaterEqual(response.data['kpis']['visits_today'], 1)
        self.assertGreaterEqual(len(response.data['charts']['arrears_daily']), 1)

    def test_dashboard_resumen_filtra_por_estado_parcela(self):
        response = self.client.get('/api/v1/dashboard/resumen/?preset=last_7_days&parcel_status=ACTIVA')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['kpis']['parcels_total'], 1)

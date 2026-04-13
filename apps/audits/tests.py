from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User, UserActorType, UserRole
from apps.audits.models import AuditEventLog, SessionAction, UserSessionLog


class AuditTrailTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email='audit-admin@example.com',
            password='Clave12345',
            role=UserRole.ADMINISTRADOR,
            actor_type=UserActorType.ADMIN_SISTEMA,
        )

    def test_login_creates_session_log(self):
        response = self.client.post(
            '/api/v1/auth/login/',
            {'email': self.admin_user.email, 'password': 'Clave12345'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        session_log = UserSessionLog.objects.filter(user=self.admin_user, action=SessionAction.LOGIN).first()
        self.assertIsNotNone(session_log)
        self.assertTrue(session_log.success)

    def test_create_parcel_creates_audit_event(self):
        login = self.client.post('/api/v1/auth/login/', {'email': self.admin_user.email, 'password': 'Clave12345'}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        response = self.client.post('/api/v1/parcelas/', {'codigo_parcela': 'Z-88', 'estado': 'ACTIVA'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        event = AuditEventLog.objects.filter(user=self.admin_user, request_method='POST', request_path='/api/v1/parcelas/').first()
        self.assertIsNotNone(event)
        self.assertEqual(event.status_code, 201)
        self.assertEqual(event.resource, 'parcelas')


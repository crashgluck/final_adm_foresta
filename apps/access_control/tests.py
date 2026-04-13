from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.access_control.models import AccessRecord, AccessStatus, BlacklistEntry
from apps.accounts.models import User, UserRole


class AccessControlTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='operator@example.com', password='Clave12345', role=UserRole.OPERADOR)
        login = self.client.post('/api/v1/auth/login/', {'email': self.user.email, 'password': 'Clave12345'}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_blacklist_blocks_access_record(self):
        BlacklistEntry.objects.create(rut='12345678-9', reason='Prueba', is_active=True)
        response = self.client.post(
            '/api/v1/access/access-records/',
            {
                'full_name': 'Persona Test',
                'rut': '12345678-9',
                'access_datetime': timezone.now().isoformat(),
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        record = AccessRecord.objects.get(pk=response.data['id'])
        self.assertEqual(record.status, AccessStatus.BLOCKED)


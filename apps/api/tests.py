from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User, UserRole


class ParcelPermissionsTests(APITestCase):
    def test_consulta_no_puede_crear_parcela(self):
        user = User.objects.create_user(email='consulta@example.com', password='Pass123456', role=UserRole.CONSULTA)
        login = self.client.post('/api/v1/auth/login/', {'email': user.email, 'password': 'Pass123456'}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        response = self.client.post('/api/v1/parcelas/', {'codigo_parcela': 'B-99', 'estado': 'ACTIVA'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_operador_si_puede_crear_parcela(self):
        user = User.objects.create_user(email='operador@example.com', password='Pass123456', role=UserRole.OPERADOR)
        login = self.client.post('/api/v1/auth/login/', {'email': user.email, 'password': 'Pass123456'}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        response = self.client.post('/api/v1/parcelas/', {'codigo_parcela': 'B-100', 'estado': 'ACTIVA'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.parcels.models import Parcel


class ParcelModelTests(TestCase):
    def test_normaliza_codigo_parcela(self):
        parcel = Parcel.objects.create(codigo_parcela=' n  - 0019 ')
        self.assertEqual(parcel.codigo_parcela, 'N-19')
        self.assertEqual(parcel.codigo_parcela_key, 'N-19')
        self.assertEqual(parcel.letra_lote, 'N')
        self.assertEqual(parcel.numero_lote, 19)

    def test_codigo_invalido_lanza_error(self):
        parcel = Parcel(codigo_parcela='INVALIDO')
        with self.assertRaises(ValidationError):
            parcel.full_clean()

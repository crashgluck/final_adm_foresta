import os
import tempfile

from django.test import TestCase
from openpyxl import Workbook

from apps.core.normalizers import normalize_parcel_code
from apps.data_imports.services.excel_importer import ExcelMasterImporter
from apps.parcels.models import Parcel


class ImportAndNormalizerTests(TestCase):
    def test_normalize_parcel_code_variants(self):
        self.assertEqual(normalize_parcel_code('n19'), 'N-19')
        self.assertEqual(normalize_parcel_code(' N-019 '), 'N-19')
        self.assertEqual(normalize_parcel_code('C 40b'), 'C-40B')

    def test_import_dry_run(self):
        wb = Workbook()
        ws = wb.active
        ws.title = 'Datos_Propietarios'
        ws.append(['PARCELA', 'NOMBRE COMPLETO', 'RUT', 'DV', 'TELÉFONO FIJO', 'TELEFONO MÓVIL', 'E-MAIL'])
        ws.append(['B-01', 'JUAN PEREZ', '12345678', '5', '', '912345678', 'juan@example.com'])

        fd, path = tempfile.mkstemp(suffix='.xlsx')
        os.close(fd)
        try:
            wb.save(path)
            importer = ExcelMasterImporter(file_path=path, dry_run=True)
            job = importer.run()
        finally:
            if os.path.exists(path):
                os.remove(path)

        self.assertTrue(job.dry_run)
        self.assertGreaterEqual(job.total_inserted, 1)
        self.assertEqual(Parcel.objects.count(), 0)

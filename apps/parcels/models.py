from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import BaseDomainModel
from apps.core.normalizers import parse_parcel_code


class ParcelStatus(models.TextChoices):
    ACTIVA = 'ACTIVA', 'Activa'
    INACTIVA = 'INACTIVA', 'Inactiva'
    SUSPENDIDA = 'SUSPENDIDA', 'Suspendida'


class Parcel(BaseDomainModel):
    codigo_parcela = models.CharField(max_length=20, unique=True)
    codigo_parcela_key = models.CharField(max_length=20, unique=True, db_index=True, blank=True)
    letra_lote = models.CharField(max_length=3, db_index=True, blank=True)
    numero_lote = models.PositiveIntegerField(db_index=True, null=True, blank=True)
    sufijo_lote = models.CharField(max_length=2, blank=True, default='')
    estado = models.CharField(max_length=20, choices=ParcelStatus.choices, default=ParcelStatus.ACTIVA, db_index=True)
    referencia_direccion = models.CharField(max_length=255, blank=True)
    observaciones_generales = models.TextField(blank=True)

    class Meta:
        ordering = ['letra_lote', 'numero_lote', 'sufijo_lote']

    def __str__(self):
        return self.codigo_parcela

    def _normalize(self):
        parsed = parse_parcel_code(self.codigo_parcela)
        if not parsed:
            raise ValidationError({'codigo_parcela': 'Formato inválido de parcela. Ej: N-19 o C-40B'})
        self.codigo_parcela = parsed.code
        self.codigo_parcela_key = parsed.code
        self.letra_lote = parsed.letter
        self.numero_lote = parsed.number
        self.sufijo_lote = parsed.suffix

    def clean(self):
        self._normalize()

    def save(self, *args, **kwargs):
        self._normalize()
        self.full_clean()
        super().save(*args, **kwargs)

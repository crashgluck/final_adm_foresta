from django.db import models

from apps.core.models import BaseDomainModel


class RiskLevel(models.TextChoices):
    BAJA = 'BAJA', 'Baja'
    MEDIA = 'MEDIA', 'Media'
    ALTA = 'ALTA', 'Alta'


class KpiState(models.TextChoices):
    NORMAL = 'NORMAL', 'Normal'
    ATENCION = 'ATENCION', 'Atención'
    PELIGRO = 'PELIGRO', 'Peligro'


class ParcelWorkStatus(BaseDomainModel):
    parcela = models.OneToOneField('parcels.Parcel', on_delete=models.CASCADE, related_name='work_status')
    deshabitada = models.CharField(max_length=30, blank=True)
    cercada = models.CharField(max_length=30, blank=True)
    sucia = models.CharField(max_length=30, blank=True)
    casas = models.CharField(max_length=80, blank=True)
    otra_construccion = models.CharField(max_length=120, blank=True)
    cumplen = models.CharField(max_length=30, blank=True)
    cortafuego = models.CharField(max_length=30, blank=True)
    limpieza = models.CharField(max_length=30, blank=True)
    foco_incendio = models.CharField(max_length=10, choices=RiskLevel.choices, blank=True)
    atributo_kpi = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    kpi = models.CharField(max_length=20, choices=KpiState.choices, blank=True)
    estado_actual = models.CharField(max_length=120, blank=True)
    rol_sii = models.CharField(max_length=80, blank=True)
    certificado_obras = models.CharField(max_length=30, blank=True)
    permiso_dom = models.CharField(max_length=30, blank=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f'Estado obras {self.parcela}'


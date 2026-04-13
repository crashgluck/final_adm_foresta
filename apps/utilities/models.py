from django.db import models

from apps.core.models import BaseDomainModel


class CutType(models.TextChoices):
    LUZ = 'LUZ', 'Luz'
    AGUA = 'AGUA', 'Agua'
    AYS = 'AYS', 'Agua y servicios'


class ServiceCut(BaseDomainModel):
    parcela = models.ForeignKey('parcels.Parcel', on_delete=models.CASCADE, related_name='service_cuts')
    tipo_corte = models.CharField(max_length=20, choices=CutType.choices, default=CutType.AYS)
    estado = models.CharField(max_length=120, blank=True)
    fecha = models.DateField(null=True, blank=True)
    motivo = models.CharField(max_length=255, blank=True)
    sello = models.CharField(max_length=80, blank=True)
    observaciones = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['-activo', '-fecha', '-created_at']


class ServiceHistory(BaseDomainModel):
    parcela = models.ForeignKey('parcels.Parcel', on_delete=models.CASCADE, related_name='service_history')
    numero_orden = models.CharField(max_length=30, blank=True)
    solicitante = models.CharField(max_length=120, blank=True)
    resultado = models.CharField(max_length=120, blank=True)
    descripcion = models.TextField(blank=True)
    fecha_ingreso = models.DateField(null=True, blank=True)
    fecha_ejecucion = models.DateField(null=True, blank=True)
    ejecutante = models.CharField(max_length=120, blank=True)
    lugar_corte_reposicion = models.CharField(max_length=255, blank=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha_ingreso', '-created_at']


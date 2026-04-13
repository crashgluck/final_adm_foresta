from django.db import models
from django.db.models import Q

from apps.core.models import BaseDomainModel


class Vehicle(BaseDomainModel):
    parcela = models.ForeignKey('parcels.Parcel', on_delete=models.CASCADE, related_name='vehicles')
    persona = models.ForeignKey('people.Person', on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicles')
    ppu = models.CharField(max_length=20)
    ppu_normalizado = models.CharField(max_length=20, db_index=True)
    marca = models.CharField(max_length=80, blank=True)
    modelo = models.CharField(max_length=80, blank=True)
    tipo = models.CharField(max_length=80, blank=True)
    color = models.CharField(max_length=80, blank=True)
    codigo_acceso = models.CharField(max_length=50, blank=True)
    activo = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ['ppu_normalizado']
        constraints = [
            models.UniqueConstraint(
                fields=['parcela', 'ppu_normalizado'],
                condition=Q(is_deleted=False),
                name='uniq_vehicle_parcel_ppu_alive',
            )
        ]

    def __str__(self):
        return f'{self.ppu_normalizado} - {self.parcela}'

    def save(self, *args, **kwargs):
        self.ppu_normalizado = ''.join(ch for ch in (self.ppu or '').upper() if ch.isalnum())
        if not self.ppu:
            self.ppu = self.ppu_normalizado
        super().save(*args, **kwargs)


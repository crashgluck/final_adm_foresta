from django.conf import settings
from django.db import models

from apps.core.models import BaseDomainModel


class ObjectiveStatus(models.TextChoices):
    PENDING = 'pending', 'Pendiente'
    IN_PROGRESS = 'in_progress', 'En curso'
    COMPLETED = 'completed', 'Completada'
    OVERDUE = 'overdue', 'Vencida'


class ParcelMapGeometry(BaseDomainModel):
    parcela = models.OneToOneField('parcels.Parcel', on_delete=models.CASCADE, related_name='map_geometry')
    coordinates = models.JSONField(blank=True, null=True)
    color = models.CharField(max_length=9, default='#51ff00')
    source_label = models.CharField(max_length=80, blank=True)

    class Meta:
        ordering = ['parcela__codigo_parcela']

    def __str__(self):
        return f'Mapa {self.parcela.codigo_parcela}'


class Objective(BaseDomainModel):
    parcela = models.ForeignKey('parcels.Parcel', on_delete=models.SET_NULL, null=True, blank=True, related_name='map_objectives')
    persona = models.ForeignKey('people.Person', on_delete=models.SET_NULL, null=True, blank=True, related_name='map_objectives')
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='map_objectives'
    )
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    coordinates = models.JSONField(blank=True, null=True)
    color = models.CharField(max_length=9, default='#51ff00')
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=ObjectiveStatus.choices, default=ObjectiveStatus.PENDING)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Visit(BaseDomainModel):
    parcela = models.ForeignKey('parcels.Parcel', on_delete=models.CASCADE, related_name='map_visits')
    persona = models.ForeignKey('people.Person', on_delete=models.SET_NULL, null=True, blank=True, related_name='map_visits')
    objective = models.ForeignKey(Objective, on_delete=models.SET_NULL, null=True, blank=True, related_name='visits')
    visitor_name = models.CharField(max_length=150)
    visitor_rut = models.CharField(max_length=20, blank=True)
    vehicle_plate = models.CharField(max_length=20, blank=True)
    purpose = models.CharField(max_length=200)
    visit_datetime = models.DateTimeField(db_index=True)
    notes = models.TextField(blank=True)
    admitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='map_visits_admitted'
    )

    class Meta:
        ordering = ['-visit_datetime']

    def __str__(self):
        return f'{self.visitor_name} - {self.visit_datetime:%Y-%m-%d %H:%M}'


from django.conf import settings
from django.db import models

from apps.core.models import BaseDomainModel


class ShiftStatus(models.TextChoices):
    OPEN = 'open', 'Abierto'
    CLOSED = 'closed', 'Cerrado'


class Shift(BaseDomainModel):
    name = models.CharField(max_length=120)
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='supervised_shifts'
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=ShiftStatus.choices, default=ShiftStatus.OPEN)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-start_datetime']

    def __str__(self):
        return f'{self.name} ({self.start_datetime:%Y-%m-%d})'


class RoundStatus(models.TextChoices):
    PLANNED = 'planned', 'Planificada'
    IN_PROGRESS = 'in_progress', 'En curso'
    COMPLETED = 'completed', 'Completada'


class Round(BaseDomainModel):
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='rounds')
    guard = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='rounds')
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=RoundStatus.choices, default=RoundStatus.PLANNED)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f'Ronda {self.id} - {self.shift_id}'


class NotificationStatus(models.TextChoices):
    PENDING = 'pending', 'Pendiente'
    PAID = 'paid', 'Pagada'
    CANCELLED = 'cancelled', 'Anulada'


class NotificationFine(BaseDomainModel):
    parcela = models.ForeignKey('parcels.Parcel', on_delete=models.SET_NULL, null=True, blank=True, related_name='supervisor_notifications')
    persona = models.ForeignKey('people.Person', on_delete=models.SET_NULL, null=True, blank=True, related_name='supervisor_notifications')
    shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=NotificationStatus.choices, default=NotificationStatus.PENDING)
    issued_at = models.DateTimeField()
    due_date = models.DateField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-issued_at']

    def __str__(self):
        return f'{self.title} - {self.parcela or self.persona or "sin destino"}'


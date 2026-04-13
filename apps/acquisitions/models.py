from django.db import models

from apps.core.models import BaseDomainModel


class AcquisitionStatus(models.TextChoices):
    ACTIVE = 'active', 'Activo'
    INACTIVE = 'inactive', 'Inactivo'
    LOST = 'lost', 'Perdido'


class RemoteControl(BaseDomainModel):
    parcela = models.ForeignKey('parcels.Parcel', on_delete=models.CASCADE, related_name='remote_controls')
    persona = models.ForeignKey('people.Person', on_delete=models.SET_NULL, null=True, blank=True, related_name='remote_controls')
    serial_number = models.CharField(max_length=80, unique=True)
    model = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=AcquisitionStatus.choices, default=AcquisitionStatus.ACTIVE)
    issued_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['serial_number']

    def __str__(self):
        return self.serial_number


class RFIDCard(BaseDomainModel):
    parcela = models.ForeignKey('parcels.Parcel', on_delete=models.CASCADE, related_name='rfid_cards')
    persona = models.ForeignKey('people.Person', on_delete=models.SET_NULL, null=True, blank=True, related_name='rfid_cards')
    uid = models.CharField(max_length=120, unique=True)
    color = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=20, choices=AcquisitionStatus.choices, default=AcquisitionStatus.ACTIVE)
    issued_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['uid']

    def __str__(self):
        return self.uid


class VehicleLogo(BaseDomainModel):
    parcela = models.ForeignKey('parcels.Parcel', on_delete=models.CASCADE, related_name='vehicle_logos')
    persona = models.ForeignKey('people.Person', on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicle_logos')
    plate = models.CharField(max_length=20)
    logo_code = models.CharField(max_length=120, unique=True)
    status = models.CharField(max_length=20, choices=AcquisitionStatus.choices, default=AcquisitionStatus.ACTIVE)
    issued_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['plate', 'logo_code']
        constraints = [models.UniqueConstraint(fields=['parcela', 'plate'], name='uniq_vehicle_logo_per_parcel_plate')]

    def __str__(self):
        return f'{self.plate} ({self.logo_code})'


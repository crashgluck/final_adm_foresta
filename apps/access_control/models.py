from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import BaseDomainModel


def _clean_plate(value: str) -> str:
    return ''.join(ch for ch in (value or '').upper() if ch.isalnum())


class BlacklistEntry(BaseDomainModel):
    rut = models.CharField(max_length=20, blank=True)
    plate = models.CharField(max_length=20, blank=True)
    reason = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        self.rut = (self.rut or '').strip().upper()
        self.plate = _clean_plate(self.plate)
        if not self.rut and not self.plate:
            raise ValidationError('Debe indicar RUT o patente.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.rut or self.plate


class AccessStatus(models.TextChoices):
    ALLOWED = 'allowed', 'Permitido'
    BLOCKED = 'blocked', 'Bloqueado'


class AccessSource(models.TextChoices):
    MANUAL = 'manual', 'Manual'
    IOT = 'iot', 'IoT'
    LEGACY_IMPORT = 'legacy_import', 'Migración legacy'


class AccessRecord(BaseDomainModel):
    parcela = models.ForeignKey('parcels.Parcel', on_delete=models.SET_NULL, null=True, blank=True, related_name='access_records')
    persona = models.ForeignKey('people.Person', on_delete=models.SET_NULL, null=True, blank=True, related_name='access_records')
    full_name = models.CharField(max_length=180)
    rut = models.CharField(max_length=20, blank=True)
    plate = models.CharField(max_length=20, blank=True)
    motive = models.CharField(max_length=200, blank=True)
    company_name = models.CharField(max_length=150, blank=True)
    access_datetime = models.DateTimeField(db_index=True)
    note = models.TextField(blank=True)
    card_number = models.CharField(max_length=30, blank=True)
    card_color = models.CharField(max_length=30, blank=True)
    status = models.CharField(max_length=20, choices=AccessStatus.choices, default=AccessStatus.ALLOWED, db_index=True)
    source = models.CharField(max_length=20, choices=AccessSource.choices, default=AccessSource.MANUAL, db_index=True)
    created_from = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ['-access_datetime']

    def clean(self):
        self.full_name = (self.full_name or '').strip()
        self.rut = (self.rut or '').strip().upper()
        self.plate = _clean_plate(self.plate)
        if not self.full_name:
            raise ValidationError({'full_name': 'El nombre completo es obligatorio.'})

        blocked = BlacklistEntry.objects.filter(is_active=True, is_deleted=False).filter(
            models.Q(rut__iexact=self.rut) | models.Q(plate__iexact=self.plate)
        )
        if blocked.exists():
            self.status = AccessStatus.BLOCKED

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.full_name} - {self.access_datetime:%Y-%m-%d %H:%M}'

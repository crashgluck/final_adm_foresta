from django.conf import settings
from django.db import models

from apps.core.models import BaseDomainModel


class NoteType(models.TextChoices):
    ADMINISTRATIVA = 'ADMINISTRATIVA', 'Administrativa'
    COBRANZA = 'COBRANZA', 'Cobranza'
    OPERATIVA = 'OPERATIVA', 'Operativa'
    ALERTA = 'ALERTA', 'Alerta'


class AdministrativeNote(BaseDomainModel):
    parcela = models.ForeignKey('parcels.Parcel', on_delete=models.CASCADE, related_name='notes')
    tipo = models.CharField(max_length=20, choices=NoteType.choices, default=NoteType.ADMINISTRATIVA)
    texto = models.TextField()
    fecha_evento = models.DateField(null=True, blank=True)
    usuario_registra = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registered_notes',
    )

    class Meta:
        ordering = ['-fecha_evento', '-created_at']

    def __str__(self):
        return f'{self.parcela} - {self.tipo}'


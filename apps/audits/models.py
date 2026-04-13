from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class SessionAction(models.TextChoices):
    LOGIN = 'LOGIN', 'Inicio de sesion'
    LOGOUT = 'LOGOUT', 'Cierre de sesion'
    REFRESH = 'REFRESH', 'Refresh token'
    PASSWORD_CHANGE = 'PASSWORD_CHANGE', 'Cambio de contrasena'


class AuditAction(models.TextChoices):
    LIST = 'LIST', 'Listado'
    RETRIEVE = 'RETRIEVE', 'Detalle'
    CREATE = 'CREATE', 'Creacion'
    UPDATE = 'UPDATE', 'Actualizacion'
    DELETE = 'DELETE', 'Eliminacion'
    CUSTOM = 'CUSTOM', 'Accion custom'


class UserSessionLog(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='session_logs')
    action = models.CharField(max_length=30, choices=SessionAction.choices, db_index=True)
    success = models.BooleanField(default=True, db_index=True)
    auth_identifier = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['action', 'success']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f'{self.action} - {self.user_id or "anon"} - {self.created_at:%Y-%m-%d %H:%M:%S}'


class AuditEventLog(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_events')
    user_role = models.CharField(max_length=20, blank=True)
    user_actor_type = models.CharField(max_length=40, blank=True)
    action = models.CharField(max_length=20, choices=AuditAction.choices, db_index=True)
    request_method = models.CharField(max_length=10, db_index=True)
    request_path = models.CharField(max_length=255, db_index=True)
    resource = models.CharField(max_length=120, blank=True, db_index=True)
    object_id = models.CharField(max_length=64, blank=True, db_index=True)
    status_code = models.PositiveSmallIntegerField(default=0, db_index=True)
    is_success = models.BooleanField(default=True, db_index=True)
    message = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    query_params = models.JSONField(default=dict, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    response_summary = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['action', 'request_method']),
            models.Index(fields=['resource', 'object_id']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f'{self.request_method} {self.request_path} ({self.status_code})'


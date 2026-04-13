from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.managers import UserManager
from apps.core.models import TimeStampedModel


class UserRole(models.TextChoices):
    SUPERADMIN = 'SUPERADMIN', _('Superadmin')
    ADMINISTRADOR = 'ADMINISTRADOR', _('Administrador')
    OPERADOR = 'OPERADOR', _('Operador / Gestión')
    CONSULTA = 'CONSULTA', _('Consulta / Solo lectura')


class UserActorType(models.TextChoices):
    GERENTE_GENERAL = 'GERENTE_GENERAL', _('Gerente general')
    JEFE_OBRAS_COMUNIDAD = 'JEFE_OBRAS_COMUNIDAD', _('Jefe direccion de obras y comunidad')
    JEFE_SEGURIDAD_OPERACIONAL = 'JEFE_SEGURIDAD_OPERACIONAL', _('Jefe seguridad y operacional')
    CENTRAL_MONITOREO = 'CENTRAL_MONITOREO', _('Operador central de monitoreo')
    PORTAL_ACCESO = 'PORTAL_ACCESO', _('Portal de acceso')
    OPERADOR_DRONE = 'OPERADOR_DRONE', _('Operador drone')
    CONSULTA_EJECUTIVA = 'CONSULTA_EJECUTIVA', _('Consulta ejecutiva')
    ADMIN_SISTEMA = 'ADMIN_SISTEMA', _('Administrador de sistema')


class User(TimeStampedModel, AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.CONSULTA)
    actor_type = models.CharField(max_length=40, choices=UserActorType.choices, default=UserActorType.CONSULTA_EJECUTIVA)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip() or self.email


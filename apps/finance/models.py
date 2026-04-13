from django.db import models
from django.utils import timezone

from apps.core.models import BaseDomainModel


class PaymentStatus(models.TextChoices):
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    PARCIAL = 'PARCIAL', 'Parcial'
    PAGADO = 'PAGADO', 'Pagado'
    VENCIDO = 'VENCIDO', 'Vencido'
    SIN_INFO = 'SIN_INFO', 'Sin información'


class ServiceType(models.TextChoices):
    AGUA = 'AGUA', 'Agua'
    LUZ = 'LUZ', 'Luz'
    AYS = 'AYS', 'Agua y servicios'


class FinancialMovementType(models.TextChoices):
    INCOME = 'INCOME', 'Ingreso'
    EXPENSE = 'EXPENSE', 'Egreso'


class FinancialMovementCategory(models.TextChoices):
    PAYMENT_GC = 'PAYMENT_GC', 'Pago gasto común'
    PAYMENT_SERVICE = 'PAYMENT_SERVICE', 'Pago servicio/AYS'
    PAYMENT_AGREEMENT = 'PAYMENT_AGREEMENT', 'Pago convenio'
    PAYMENT_FINE = 'PAYMENT_FINE', 'Pago multa'
    OTHER_INCOME = 'OTHER_INCOME', 'Otro ingreso'
    OPERATIONAL_EXPENSE = 'OPERATIONAL_EXPENSE', 'Egreso operacional'
    MAINTENANCE_EXPENSE = 'MAINTENANCE_EXPENSE', 'Egreso mantención'
    SECURITY_EXPENSE = 'SECURITY_EXPENSE', 'Egreso seguridad'
    OTHER_EXPENSE = 'OTHER_EXPENSE', 'Otro egreso'


class PaymentMethod(models.TextChoices):
    TRANSFER = 'TRANSFER', 'Transferencia'
    CASH = 'CASH', 'Efectivo'
    CARD = 'CARD', 'Tarjeta'
    ONLINE = 'ONLINE', 'Pago online'
    OTHER = 'OTHER', 'Otro'


class CommonExpenseDebt(BaseDomainModel):
    parcela = models.ForeignKey('parcels.Parcel', on_delete=models.CASCADE, related_name='common_expense_debts')
    persona = models.ForeignKey('people.Person', on_delete=models.SET_NULL, null=True, blank=True, related_name='common_expense_debts')
    fecha_corte = models.DateField(null=True, blank=True)
    numero_gastos_comunes = models.PositiveIntegerField(default=0)
    mora_uf = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    interes_mora_uf = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    total_uf = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    total_pesos = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    estado_pago = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDIENTE)
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']


class ServiceDebt(BaseDomainModel):
    parcela = models.ForeignKey('parcels.Parcel', on_delete=models.CASCADE, related_name='service_debts')
    persona = models.ForeignKey('people.Person', on_delete=models.SET_NULL, null=True, blank=True, related_name='service_debts')
    tipo_servicio = models.CharField(max_length=20, choices=ServiceType.choices, default=ServiceType.AYS)
    numero_boletas = models.PositiveIntegerField(default=0)
    monto_total = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    convenios = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    anticipos = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    saldo_total = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    estado_pago = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDIENTE)
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']


class PaymentAgreement(BaseDomainModel):
    parcela = models.ForeignKey('parcels.Parcel', on_delete=models.CASCADE, related_name='payment_agreements')
    empresa = models.CharField(max_length=120, blank=True)
    tipo = models.CharField(max_length=120, blank=True)
    fecha_emision = models.DateField(null=True, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    detalle = models.CharField(max_length=255, blank=True)
    saldo_monto = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    estado_pago = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDIENTE)

    class Meta:
        ordering = ['-fecha_vencimiento', '-created_at']


class UnpaidFine(BaseDomainModel):
    parcela = models.ForeignKey('parcels.Parcel', on_delete=models.CASCADE, related_name='unpaid_fines')
    empresa = models.CharField(max_length=120, blank=True)
    tipo = models.CharField(max_length=120, blank=True)
    fecha_emision = models.DateField(null=True, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    detalle = models.CharField(max_length=255, blank=True)
    saldo_monto = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    estado_pago = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDIENTE)

    class Meta:
        ordering = ['-fecha_vencimiento', '-created_at']


class FinancialMovement(BaseDomainModel):
    parcela = models.ForeignKey('parcels.Parcel', on_delete=models.SET_NULL, null=True, blank=True, related_name='financial_movements')
    persona = models.ForeignKey('people.Person', on_delete=models.SET_NULL, null=True, blank=True, related_name='financial_movements')
    movement_type = models.CharField(max_length=20, choices=FinancialMovementType.choices, default=FinancialMovementType.INCOME, db_index=True)
    category = models.CharField(max_length=40, choices=FinancialMovementCategory.choices, default=FinancialMovementCategory.OTHER_INCOME, db_index=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    occurred_at = models.DateTimeField(default=timezone.now, db_index=True)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.TRANSFER)
    is_confirmed = models.BooleanField(default=True, db_index=True)
    reference = models.CharField(max_length=120, blank=True)
    source_label = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-occurred_at', '-created_at']

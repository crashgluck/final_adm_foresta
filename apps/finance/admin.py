from django.contrib import admin

from apps.finance.models import CommonExpenseDebt, FinancialMovement, PaymentAgreement, ServiceDebt, UnpaidFine


@admin.register(CommonExpenseDebt)
class CommonExpenseDebtAdmin(admin.ModelAdmin):
    list_display = ('parcela', 'numero_gastos_comunes', 'total_pesos', 'estado_pago')
    search_fields = ('parcela__codigo_parcela',)
    list_filter = ('estado_pago',)


@admin.register(ServiceDebt)
class ServiceDebtAdmin(admin.ModelAdmin):
    list_display = ('parcela', 'tipo_servicio', 'saldo_total', 'estado_pago')
    search_fields = ('parcela__codigo_parcela',)
    list_filter = ('tipo_servicio', 'estado_pago')


@admin.register(PaymentAgreement)
class PaymentAgreementAdmin(admin.ModelAdmin):
    list_display = ('parcela', 'empresa', 'tipo', 'saldo_monto', 'estado_pago')
    search_fields = ('parcela__codigo_parcela', 'empresa', 'tipo')
    list_filter = ('estado_pago',)


@admin.register(UnpaidFine)
class UnpaidFineAdmin(admin.ModelAdmin):
    list_display = ('parcela', 'empresa', 'tipo', 'saldo_monto', 'estado_pago')
    search_fields = ('parcela__codigo_parcela', 'empresa', 'tipo')
    list_filter = ('estado_pago',)


@admin.register(FinancialMovement)
class FinancialMovementAdmin(admin.ModelAdmin):
    list_display = ('occurred_at', 'movement_type', 'category', 'amount', 'is_confirmed', 'parcela')
    search_fields = ('parcela__codigo_parcela', 'reference', 'description', 'source_label')
    list_filter = ('movement_type', 'category', 'is_confirmed', 'payment_method')


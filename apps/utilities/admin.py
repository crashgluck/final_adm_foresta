from django.contrib import admin

from apps.utilities.models import ServiceCut, ServiceHistory


@admin.register(ServiceCut)
class ServiceCutAdmin(admin.ModelAdmin):
    list_display = ('parcela', 'tipo_corte', 'estado', 'fecha', 'activo')
    search_fields = ('parcela__codigo_parcela', 'estado', 'motivo')
    list_filter = ('tipo_corte', 'activo')


@admin.register(ServiceHistory)
class ServiceHistoryAdmin(admin.ModelAdmin):
    list_display = ('parcela', 'numero_orden', 'solicitante', 'resultado', 'fecha_ingreso')
    search_fields = ('parcela__codigo_parcela', 'numero_orden', 'descripcion')


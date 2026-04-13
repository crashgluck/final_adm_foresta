from django.contrib import admin

from apps.works.models import ParcelWorkStatus


@admin.register(ParcelWorkStatus)
class ParcelWorkStatusAdmin(admin.ModelAdmin):
    list_display = ('parcela', 'foco_incendio', 'kpi', 'estado_actual')
    search_fields = ('parcela__codigo_parcela', 'estado_actual', 'rol_sii')
    list_filter = ('foco_incendio', 'kpi')


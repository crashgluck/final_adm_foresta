from django.contrib import admin

from apps.vehicles.models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('ppu_normalizado', 'parcela', 'marca', 'tipo', 'activo')
    search_fields = ('ppu_normalizado', 'parcela__codigo_parcela', 'marca', 'modelo')
    list_filter = ('activo', 'tipo')


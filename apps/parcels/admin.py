from django.contrib import admin

from apps.parcels.models import Parcel


@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    list_display = ('codigo_parcela', 'estado', 'letra_lote', 'numero_lote', 'sufijo_lote')
    search_fields = ('codigo_parcela', 'codigo_parcela_key', 'referencia_direccion')
    list_filter = ('estado', 'letra_lote')


from django.contrib import admin

from apps.notes.models import AdministrativeNote


@admin.register(AdministrativeNote)
class AdministrativeNoteAdmin(admin.ModelAdmin):
    list_display = ('parcela', 'tipo', 'fecha_evento', 'usuario_registra')
    search_fields = ('parcela__codigo_parcela', 'texto')
    list_filter = ('tipo',)


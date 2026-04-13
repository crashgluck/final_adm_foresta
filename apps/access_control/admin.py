from django.contrib import admin

from apps.access_control.models import AccessRecord, BlacklistEntry


@admin.register(BlacklistEntry)
class BlacklistEntryAdmin(admin.ModelAdmin):
    list_display = ('rut', 'plate', 'reason', 'is_active', 'created_at')
    search_fields = ('rut', 'plate', 'reason')
    list_filter = ('is_active',)


@admin.register(AccessRecord)
class AccessRecordAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'rut', 'plate', 'parcela', 'status', 'source', 'access_datetime')
    search_fields = ('full_name', 'rut', 'plate', 'parcela__codigo_parcela')
    list_filter = ('status', 'source')


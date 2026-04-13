from django.contrib import admin

from apps.supervisor.models import NotificationFine, Round, Shift


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('name', 'supervisor', 'start_datetime', 'status')
    list_filter = ('status',)


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ('shift', 'guard', 'started_at', 'status')
    list_filter = ('status',)


@admin.register(NotificationFine)
class NotificationFineAdmin(admin.ModelAdmin):
    list_display = ('title', 'parcela', 'amount', 'status', 'issued_at')
    search_fields = ('title', 'parcela__codigo_parcela')
    list_filter = ('status',)


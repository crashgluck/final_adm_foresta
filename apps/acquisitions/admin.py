from django.contrib import admin

from apps.acquisitions.models import RFIDCard, RemoteControl, VehicleLogo


@admin.register(RemoteControl)
class RemoteControlAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'parcela', 'status', 'issued_at')
    search_fields = ('serial_number', 'parcela__codigo_parcela')
    list_filter = ('status',)


@admin.register(RFIDCard)
class RFIDCardAdmin(admin.ModelAdmin):
    list_display = ('uid', 'parcela', 'status', 'issued_at')
    search_fields = ('uid', 'parcela__codigo_parcela')
    list_filter = ('status',)


@admin.register(VehicleLogo)
class VehicleLogoAdmin(admin.ModelAdmin):
    list_display = ('plate', 'logo_code', 'parcela', 'status', 'issued_at')
    search_fields = ('plate', 'logo_code', 'parcela__codigo_parcela')
    list_filter = ('status',)


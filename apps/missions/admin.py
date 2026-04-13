from django.contrib import admin

from apps.missions.models import DroneFlight, Mission, MissionReport


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'parcela', 'status', 'team_name', 'scheduled_for')
    search_fields = ('title', 'description', 'parcela__codigo_parcela')
    list_filter = ('status',)


@admin.register(DroneFlight)
class DroneFlightAdmin(admin.ModelAdmin):
    list_display = ('mission_code', 'team_code', 'parcela', 'pilot', 'flight_datetime')
    search_fields = ('mission_code', 'team_code', 'parcela__codigo_parcela')


@admin.register(MissionReport)
class MissionReportAdmin(admin.ModelAdmin):
    list_display = ('mission', 'report_date', 'media_type', 'created_by')
    search_fields = ('mission__title', 'summary')


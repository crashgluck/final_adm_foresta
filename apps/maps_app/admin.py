from django.contrib import admin

from apps.maps_app.models import Objective, ParcelMapGeometry, Visit


@admin.register(ParcelMapGeometry)
class ParcelMapGeometryAdmin(admin.ModelAdmin):
    list_display = ('parcela', 'color', 'source_label', 'updated_at')
    search_fields = ('parcela__codigo_parcela', 'source_label')


@admin.register(Objective)
class ObjectiveAdmin(admin.ModelAdmin):
    list_display = ('title', 'parcela', 'status', 'due_date', 'assigned_to')
    list_filter = ('status',)
    search_fields = ('title', 'description', 'parcela__codigo_parcela')


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('visitor_name', 'parcela', 'visit_datetime', 'objective')
    search_fields = ('visitor_name', 'visitor_rut', 'parcela__codigo_parcela')


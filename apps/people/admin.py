from django.contrib import admin

from apps.people.models import ParcelOwnership, ParcelResident, Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'rut_normalizado', 'email', 'telefono_principal', 'activo')
    search_fields = ('nombre_completo', 'rut_normalizado', 'email')
    list_filter = ('activo',)


@admin.register(ParcelOwnership)
class ParcelOwnershipAdmin(admin.ModelAdmin):
    list_display = ('parcela', 'persona', 'tipo', 'is_active')
    search_fields = ('parcela__codigo_parcela', 'persona__nombre_completo')
    list_filter = ('tipo', 'is_active')


@admin.register(ParcelResident)
class ParcelResidentAdmin(admin.ModelAdmin):
    list_display = ('parcela', 'persona', 'tipo_residencia', 'is_active')
    search_fields = ('parcela__codigo_parcela', 'persona__nombre_completo')
    list_filter = ('tipo_residencia', 'is_active')


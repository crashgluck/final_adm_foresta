from django.contrib import admin

from apps.audits.models import AuditEventLog, UserSessionLog


@admin.register(UserSessionLog)
class UserSessionLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'action', 'success', 'user', 'auth_identifier', 'ip_address')
    search_fields = ('user__email', 'auth_identifier', 'ip_address')
    list_filter = ('action', 'success', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(AuditEventLog)
class AuditEventLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'request_method', 'resource', 'object_id', 'status_code', 'is_success', 'user')
    search_fields = ('request_path', 'resource', 'object_id', 'user__email', 'message')
    list_filter = ('action', 'request_method', 'is_success', 'status_code', 'created_at')
    readonly_fields = ('created_at',)


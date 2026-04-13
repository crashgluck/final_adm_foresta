from rest_framework import serializers

from apps.audits.models import AuditEventLog, UserSessionLog


class UserSessionLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = UserSessionLog
        fields = [
            'id',
            'created_at',
            'user',
            'user_email',
            'user_name',
            'action',
            'success',
            'auth_identifier',
            'ip_address',
            'user_agent',
            'metadata',
        ]
        read_only_fields = fields

    def get_user_name(self, obj):
        if not obj.user:
            return ''
        return obj.user.full_name


class AuditEventLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = AuditEventLog
        fields = [
            'id',
            'created_at',
            'user',
            'user_email',
            'user_name',
            'user_role',
            'user_actor_type',
            'action',
            'request_method',
            'request_path',
            'resource',
            'object_id',
            'status_code',
            'is_success',
            'message',
            'ip_address',
            'user_agent',
            'query_params',
            'payload',
            'response_summary',
        ]
        read_only_fields = fields

    def get_user_name(self, obj):
        if not obj.user:
            return ''
        return obj.user.full_name


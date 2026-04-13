from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.core.thread_local import set_current_user


class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()

    def __call__(self, request):
        resolved_user = getattr(request, 'user', None)

        if not getattr(resolved_user, 'is_authenticated', False):
            try:
                header = self.jwt_auth.get_header(request)
                if header:
                    raw_token = self.jwt_auth.get_raw_token(header)
                    if raw_token:
                        validated_token = self.jwt_auth.get_validated_token(raw_token)
                        resolved_user = self.jwt_auth.get_user(validated_token)
            except Exception:
                resolved_user = getattr(request, 'user', None)

        request.audit_user = resolved_user
        set_current_user(resolved_user)
        response = self.get_response(request)
        set_current_user(None)
        return response

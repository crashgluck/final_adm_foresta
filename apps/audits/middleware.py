from apps.audits.services import create_audit_event


class AuditTrailMiddleware:
    EXCLUDED_PREFIXES = (
        '/admin/',
        '/api/schema/',
        '/api/docs/',
        '/api/redoc/',
        '/api/v1/auth/login/',
        '/api/v1/auth/logout/',
        '/api/v1/auth/refresh/',
        '/api/v1/audits/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.method == 'OPTIONS':
            return response
        if not request.path.startswith('/api/v1/'):
            return response
        if request.path.startswith(self.EXCLUDED_PREFIXES):
            return response

        try:
            resolver_match = getattr(request, 'resolver_match', None)
            kwargs = resolver_match.kwargs if resolver_match else {}
            object_id = ''
            for key in ('pk', 'id', 'parcelId', 'parcel_id'):
                if key in kwargs:
                    object_id = str(kwargs[key])
                    break

            segments = [segment for segment in request.path.strip('/').split('/') if segment]
            resource = '/'.join(segments[2:4]) if len(segments) >= 4 else '/'.join(segments[2:]) if len(segments) >= 3 else ''

            create_audit_event(
                request=request,
                response=response,
                resource=resource,
                object_id=object_id,
            )
        except Exception:
            # Auditoria nunca debe quebrar el flujo principal.
            return response

        return response


from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/v1/", include("apps.api.urls")),
    path("foresta/api/schema/", SpectacularAPIView.as_view(), name="foresta-schema"),
    path("foresta/api/docs/", SpectacularSwaggerView.as_view(url_name="foresta-schema"), name="foresta-swagger-ui"),
    path("foresta/api/redoc/", SpectacularRedocView.as_view(url_name="foresta-schema"), name="foresta-redoc"),
    path("foresta/api/v1/", include("apps.api.urls")),
]

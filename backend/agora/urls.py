"""Rutas raíz de ÁGORA."""
from django.contrib import admin
from django.urls import include, path

from core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("personas/", include("personas.urls")),
    path("planes-vida/", include("pia.urls")),
    path("intervenciones/", include("intervenciones.urls")),
    path("agenda/", include("agenda.urls")),
    path("indicadores/", include("indicadores.urls")),
    path("", core_views.inicio, name="inicio"),
]

from django.urls import path

from . import views

app_name = "personas"

urlpatterns = [
    path("", views.lista_personas, name="lista"),
    path("nueva/", views.crear_persona, name="crear"),
    path("avisos-cambio-profesional/", views.avisos_cambio_profesional, name="avisos_cambio_profesional"),
    path("avisos-cambio-profesional/<uuid:aviso_id>/resolver/", views.resolver_aviso, name="resolver_aviso"),
    path("mapa-ocupacion/", views.mapa_ocupacion, name="mapa_ocupacion"),
    path("mapa-ocupacion/<str:centro_codigo>/", views.mapa_ocupacion, name="mapa_ocupacion_centro"),
    path("<uuid:persona_id>/", views.detalle_persona, name="detalle"),
    path("<uuid:persona_id>/editar/", views.editar_persona, name="editar"),
    path("<uuid:persona_id>/cuidados/", views.cuidados_enfermeria, name="cuidados"),
    path("<uuid:persona_id>/ficha-salud/", views.ficha_salud, name="ficha_salud"),
]

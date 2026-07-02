from django.urls import path

from . import views

app_name = "intervenciones"

urlpatterns = [
    path("persona/<uuid:persona_id>/", views.lista_intervenciones, name="lista"),
    path("persona/<uuid:persona_id>/nueva/", views.crear_intervencion, name="crear"),
    path("persona/<uuid:persona_id>/<uuid:intervencion_id>/editar/", views.editar_intervencion, name="editar"),
    path("persona/<uuid:persona_id>/valoracion/nueva/", views.crear_valoracion, name="crear_valoracion"),
]

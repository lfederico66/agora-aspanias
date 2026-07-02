from django.urls import path

from . import views

app_name = "agenda"

urlpatterns = [
    # Vista por defecto: hoy
    path("", views.vista_hoy, name="hoy"),
    path("semana/", views.vista_semana, name="semana"),
    path("mes/", views.vista_mes, name="mes"),
    path("nueva/", views.crear_cita, name="crear"),
    path("<uuid:cita_id>/editar/", views.editar_cita, name="editar"),
]

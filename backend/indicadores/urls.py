from django.urls import path

from . import views

app_name = "indicadores"

urlpatterns = [
    path("", views.cuadro_mando, name="cuadro_mando"),
    path("planes-vida/", views.kpis_pv, name="kpis_pv"),
    path("gestores-caso/", views.gestores_caso, name="gestores_caso"),
]

from django.urls import path

from . import views

app_name = "planes_vida"

urlpatterns = [
    path("control/", views.control_pv_por_servicio, name="control_pv_centros"),
    path("control/<str:centro_codigo>/", views.control_pv_por_servicio, name="control_pv_servicio"),
    path("control/<str:centro_codigo>/exportar.xlsx", views.exportar_control_pv_excel, name="control_pv_exportar"),
    path("persona/<uuid:persona_id>/", views.detalle_plan_vida, name="detalle"),
    path("persona/<uuid:persona_id>/panel/", views.panel_objetivos, name="panel"),
    path(
        "persona/<uuid:persona_id>/revision-objetivos/<int:anualidad>/",
        views.documento_revision_objetivos, name="revision_objetivos",
    ),
    path(
        "persona/<uuid:persona_id>/historia-vida/<int:anualidad>/",
        views.documento_historia_vida, name="historia_vida",
    ),
    path(
        "persona/<uuid:persona_id>/algo-sobre-mi/<int:anualidad>/",
        views.documento_algo_sobre_mi, name="algo_sobre_mi",
    ),
    path(
        "persona/<uuid:persona_id>/plan-apoyo/<int:anualidad>/",
        views.documento_plan_apoyo, name="plan_apoyo",
    ),
    path(
        "persona/<uuid:persona_id>/proyecto-vida/<int:anualidad>/",
        views.documento_proyecto_vida, name="proyecto_vida",
    ),
    # ----- Edición web -----
    path(
        "persona/<uuid:persona_id>/historia-vida/<int:anualidad>/editar/",
        views.editar_historia_vida, name="editar_historia_vida",
    ),
    path(
        "persona/<uuid:persona_id>/algo-sobre-mi/<int:anualidad>/editar/",
        views.editar_algo_sobre_mi, name="editar_algo_sobre_mi",
    ),
    path(
        "persona/<uuid:persona_id>/revision-objetivos/<int:anualidad>/editar/",
        views.editar_revision_objetivos, name="editar_revision_objetivos",
    ),
    path(
        "persona/<uuid:persona_id>/plan-apoyo/<int:anualidad>/editar/",
        views.editar_plan_apoyo, name="editar_plan_apoyo",
    ),
    path(
        "persona/<uuid:persona_id>/proyecto-vida/<int:anualidad>/editar/",
        views.editar_proyecto_vida, name="editar_proyecto_vida",
    ),
]

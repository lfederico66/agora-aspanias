from django.contrib import admin

from .models import (
    AlgoSobreMi,
    CambioSignificativo,
    DimensionCalidadVida,
    DocumentoPlanDeVida,
    EntradaPlanApoyo,
    HistoriaDeVida,
    Objetivo,
    PlanDeApoyo,
    PlanDeVida,
    ProyectoDeVida,
    RespuestaHistoriaVida,
    RevisionObjetivo,
    SeccionAlgoSobreMi,
)


class DocumentoPlanDeVidaInline(admin.TabularInline):
    model = DocumentoPlanDeVida
    extra = 0
    fields = ("tipo", "estado", "url_almacenamiento", "fecha_completado", "publicado_en_repriss")


class ObjetivoInline(admin.TabularInline):
    model = Objetivo
    extra = 0
    fields = ("ambito", "descripcion", "prioridad", "estado", "responsable_seguimiento")


@admin.register(PlanDeVida)
class PlanDeVidaAdmin(admin.ModelAdmin):
    list_display = (
        "persona", "anualidad", "estado",
        "pv_realizado", "pv_revisado", "estado_revision",
        "gestor_caso", "persona_referencia", "fecha_proxima_revision",
    )
    list_filter = (
        "estado", "anualidad", "pv_realizado", "pv_revisado",
        "estado_revision", "gestor_caso",
    )
    search_fields = (
        "persona__nombre", "persona__apellido_1", "persona__apellido_2",
        "persona__codigo_interno",
    )
    inlines = [DocumentoPlanDeVidaInline, ObjetivoInline]
    readonly_fields = ("id", "created_at", "updated_at")
    autocomplete_fields = ("persona", "gestor_caso", "persona_referencia")


@admin.register(DocumentoPlanDeVida)
class DocumentoPlanDeVidaAdmin(admin.ModelAdmin):
    list_display = ("plan_vida", "tipo", "estado", "fecha_completado", "publicado_en_repriss")
    list_filter = ("tipo", "estado", "publicado_en_repriss")
    search_fields = ("plan_vida__persona__apellido_1", "url_almacenamiento")


class RevisionObjetivoInline(admin.StackedInline):
    model = RevisionObjetivo
    extra = 0
    fields = (
        "anualidad", "fecha_revision", "realizada_por",
        "que_ha_logrado", "motivo_no_consecucion", "propuesta_apoyos",
    )


@admin.register(Objetivo)
class ObjetivoAdmin(admin.ModelAdmin):
    list_display = ("ambito", "descripcion_corta", "prioridad", "estado", "plan_vida")
    list_filter = ("ambito", "estado", "prioridad")
    search_fields = ("descripcion", "plan_vida__persona__apellido_1")
    inlines = [RevisionObjetivoInline]

    def descripcion_corta(self, obj):
        return obj.descripcion[:80]
    descripcion_corta.short_description = "Descripción"


@admin.register(RevisionObjetivo)
class RevisionObjetivoAdmin(admin.ModelAdmin):
    list_display = ("anualidad", "fecha_revision", "objetivo", "realizada_por")
    list_filter = ("anualidad", "fecha_revision")
    search_fields = (
        "objetivo__descripcion",
        "objetivo__plan_vida__persona__apellido_1",
    )
    date_hierarchy = "fecha_revision"


@admin.register(CambioSignificativo)
class CambioSignificativoAdmin(admin.ModelAdmin):
    list_display = ("fecha_deteccion", "ambito", "persona", "detectado_por", "procesado")
    list_filter = ("ambito", "procesado", "fecha_deteccion")
    search_fields = ("persona__apellido_1", "persona__apellido_2", "descripcion")
    date_hierarchy = "fecha_deteccion"


# ---- Documento 1: Historia de Vida ----

class RespuestaHistoriaVidaInline(admin.StackedInline):
    model = RespuestaHistoriaVida
    extra = 0
    fields = ("orden", "pregunta_codigo", "pregunta_texto", "respuesta_texto")


@admin.register(HistoriaDeVida)
class HistoriaDeVidaAdmin(admin.ModelAdmin):
    list_display = ("plan_vida", "fecha_recogida", "facilitador")
    search_fields = ("plan_vida__persona__apellido_1", "plan_vida__persona__nombre")
    inlines = [RespuestaHistoriaVidaInline]


# ---- Documento 2: Algo sobre mí ----

class SeccionAlgoSobreMiInline(admin.StackedInline):
    model = SeccionAlgoSobreMi
    extra = 0
    fields = ("orden", "codigo", "titulo", "contenido")


@admin.register(AlgoSobreMi)
class AlgoSobreMiAdmin(admin.ModelAdmin):
    list_display = ("plan_vida", "fecha_actualizacion", "actualizado_por")
    search_fields = ("plan_vida__persona__apellido_1", "plan_vida__persona__nombre")
    inlines = [SeccionAlgoSobreMiInline]


# ---- Documento 4: Plan de Apoyo ----

@admin.register(DimensionCalidadVida)
class DimensionCalidadVidaAdmin(admin.ModelAdmin):
    list_display = ("orden", "codigo", "nombre")
    ordering = ("orden",)


class EntradaPlanApoyoInline(admin.StackedInline):
    model = EntradaPlanApoyo
    extra = 0
    fields = (
        "orden", "titulo_objetivo", "objetivo_vinculado",
        "actividades", "dimensiones_cdv",
        "apoyo_que", "apoyo_quien", "apoyo_cuando",
        "observaciones", "seguimiento_cuantitativo", "seguimiento_descriptivo",
    )
    filter_horizontal = ("dimensiones_cdv",)


@admin.register(PlanDeApoyo)
class PlanDeApoyoAdmin(admin.ModelAdmin):
    list_display = ("plan_vida", "fecha_realizacion", "realizado_por")
    search_fields = ("plan_vida__persona__apellido_1", "plan_vida__persona__nombre")
    inlines = [EntradaPlanApoyoInline]


# ---- Documento 5: Proyecto de Vida ----

@admin.register(ProyectoDeVida)
class ProyectoDeVidaAdmin(admin.ModelAdmin):
    list_display = ("plan_vida", "fecha", "elaborado_por", "publicado_en_repriss")
    list_filter = ("publicado_en_repriss",)
    search_fields = ("plan_vida__persona__apellido_1", "plan_vida__persona__nombre")

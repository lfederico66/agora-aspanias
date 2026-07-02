from django.contrib import admin

from .models import Indicador, MedicionIndicador, SnapshotPlanesVida


@admin.register(Indicador)
class IndicadorAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "unidad", "objetivo_valor", "activo")
    list_filter = ("unidad", "activo", "requiere_anonimizacion")
    search_fields = ("codigo", "nombre")


@admin.register(MedicionIndicador)
class MedicionIndicadorAdmin(admin.ModelAdmin):
    list_display = ("periodo", "indicador", "centro", "valor", "calculado_at")
    list_filter = ("indicador", "centro", "periodo")
    date_hierarchy = "periodo"
    readonly_fields = ("calculado_at",)


@admin.register(SnapshotPlanesVida)
class SnapshotPlanesVidaAdmin(admin.ModelAdmin):
    list_display = (
        "fecha", "etiqueta", "total_usuarios",
        "pv_realizados", "pv_pendientes", "pv_revisados", "pv_fuera_plazo",
    )
    list_filter = ("fecha",)
    readonly_fields = ("created_at",)
    date_hierarchy = "fecha"

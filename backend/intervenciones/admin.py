from django.contrib import admin

from .models import Intervencion, TipoIntervencion, Valoracion


@admin.register(TipoIntervencion)
class TipoIntervencionAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "color")
    search_fields = ("codigo", "nombre")


@admin.register(Intervencion)
class IntervencionAdmin(admin.ModelAdmin):
    list_display = ("fecha_hora", "tipo", "persona", "profesional", "confidencialidad")
    list_filter = ("tipo", "confidencialidad", "fecha_hora")
    search_fields = ("persona__apellido_1", "persona__apellido_2", "descripcion", "profesional__nombre_completo")
    date_hierarchy = "fecha_hora"
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Valoracion)
class ValoracionAdmin(admin.ModelAdmin):
    list_display = ("fecha", "instrumento", "persona", "aplicado_por")
    list_filter = ("instrumento", "fecha")
    search_fields = ("persona__apellido_1", "persona__apellido_2", "observaciones")
    date_hierarchy = "fecha"

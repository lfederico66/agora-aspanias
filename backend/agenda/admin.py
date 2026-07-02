from django.contrib import admin

from .models import Cita


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ("inicio", "fin", "tipo", "persona", "estado", "notificada_a_familia")
    list_filter = ("tipo", "estado", "notificada_a_familia", "inicio")
    search_fields = ("persona__apellido_1", "persona__apellido_2", "ubicacion", "notas")
    date_hierarchy = "inicio"
    filter_horizontal = ("profesionales",)
    readonly_fields = ("id", "created_at", "updated_at")

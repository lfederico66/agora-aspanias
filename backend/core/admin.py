from django.contrib import admin

from .models import RegistroAcceso


@admin.register(RegistroAcceso)
class RegistroAccesoAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "profesional", "accion", "entidad", "persona_consultada_id", "ip")
    list_filter = ("accion", "entidad", "timestamp")
    search_fields = ("profesional__username", "profesional__email", "persona_consultada_id", "ruta")
    readonly_fields = tuple(f.name for f in RegistroAcceso._meta.fields)
    date_hierarchy = "timestamp"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

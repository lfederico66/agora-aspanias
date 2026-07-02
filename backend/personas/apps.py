from django.apps import AppConfig


class PersonasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "personas"
    verbose_name = "Personas atendidas y entorno"

    def ready(self):
        # Engancha signals: avisos automáticos de cambio de profesional (Protocolo §9)
        from . import signals  # noqa: F401

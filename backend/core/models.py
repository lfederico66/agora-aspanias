"""Modelos transversales: bitácora de accesos y auditoría."""
import uuid

from django.conf import settings
from django.db import models


class RegistroAcceso(models.Model):
    """Registro append-only de accesos a fichas y entidades sensibles.

    Cada lectura, edición, exportación o firma genera una entrada.
    Retención mínima 24 meses (configurable vía AGORA_BITACORA_RETENCION_DIAS).
    """

    class Accion(models.TextChoices):
        LEER = "leer", "Leer"
        EDITAR = "editar", "Editar"
        CREAR = "crear", "Crear"
        ELIMINAR = "eliminar", "Eliminar"
        EXPORTAR = "exportar", "Exportar"
        FIRMAR = "firmar", "Firmar"
        LOGIN = "login", "Inicio de sesión"
        LOGOUT = "logout", "Cierre de sesión"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    profesional = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="accesos",
        null=True,
        blank=True,
        verbose_name="Profesional",
    )
    persona_consultada_id = models.UUIDField(
        null=True, blank=True, db_index=True,
        verbose_name="Persona atendida consultada",
        help_text="UUID de la persona si el acceso afecta a una ficha concreta.",
    )
    accion = models.CharField(max_length=16, choices=Accion.choices, db_index=True)
    entidad = models.CharField(
        max_length=128, blank=True,
        verbose_name="Entidad afectada",
        help_text="Nombre del modelo o sección consultada.",
    )
    ruta = models.CharField(max_length=512, blank=True, verbose_name="Ruta")
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True)
    motivo = models.CharField(
        max_length=255, blank=True,
        verbose_name="Motivo",
        help_text="Justificación del acceso cuando se requiera.",
    )

    class Meta:
        verbose_name = "Registro de acceso (bitácora)"
        verbose_name_plural = "Registros de acceso (bitácora)"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["profesional", "-timestamp"]),
            models.Index(fields=["persona_consultada_id", "-timestamp"]),
        ]

    def __str__(self) -> str:
        return f"{self.timestamp:%Y-%m-%d %H:%M} · {self.accion} · {self.entidad or '-'}"

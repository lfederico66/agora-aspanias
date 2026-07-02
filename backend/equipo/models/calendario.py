"""Calendario laboral anual del centro.

Documento obligatorio por convenio (VII Discapacidad / VII Residencias) que
fija festivos, jornada anual y distribución para cada año natural y centro.
Debe estar aprobado por Dirección y firmado por la RLT antes del 1 enero.
"""
import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class CalendarioLaboral(models.Model):
    """Calendario laboral anual de un centro y año concretos."""

    class Estado(models.TextChoices):
        BORRADOR = "borrador", "Borrador"
        APROBADO_DIRECCION = "aprobado_direccion", "Aprobado por Dirección"
        ENVIADO_RLT = "enviado_rlt", "Enviado a RLT"
        FIRMADO = "firmado", "Firmado por RLT"
        PUBLICADO = "publicado", "Publicado en tablón"
        SUSTITUIDO = "sustituido", "Sustituido"

    class Convenio(models.TextChoices):
        DISCAPACIDAD = "vii_discapacidad", "VII Convenio Discapacidad (1 752 h/año)"
        RESIDENCIAS = "vii_residencias_mayores", "VII Estatal Residencias (1 770 h/año)"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    centro = models.ForeignKey(
        "personas.Centro",
        on_delete=models.PROTECT,
        related_name="calendarios_laborales",
    )
    anio = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(2024), MaxValueValidator(2099)],
    )

    convenio = models.CharField(max_length=32, choices=Convenio.choices)
    jornada_anual_horas = models.PositiveSmallIntegerField(
        help_text="Horas anuales convenio. 1 752 (DI) / 1 770 (Res Mayores).",
    )

    # Festivos (lista JSON con fechas y etiquetas)
    festivos = models.JSONField(
        default=list,
        help_text='Lista [{"fecha":"2026-01-01","tipo":"nacional","nombre":"Año Nuevo"}, ...]',
    )

    # Versionado
    version = models.CharField(max_length=8, default="v1.0")
    estado = models.CharField(
        max_length=24, choices=Estado.choices,
        default=Estado.BORRADOR,
    )
    fecha_aprobacion_direccion = models.DateField(null=True, blank=True)
    fecha_firma_rlt = models.DateField(null=True, blank=True)

    aprobado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="calendarios_aprobados",
    )

    notas = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Calendario laboral del centro"
        verbose_name_plural = "Calendarios laborales del centro"
        ordering = ["-anio", "centro__nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["centro", "anio", "version"],
                name="calendario_centro_anio_version_unico",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.centro.nombre} · {self.anio} · {self.version}"

    @property
    def esta_firmado(self) -> bool:
        return self.estado in (self.Estado.FIRMADO, self.Estado.PUBLICADO)

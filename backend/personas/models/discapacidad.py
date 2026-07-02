"""Modelo de datos · módulo "discapacidad" (split de models.py para legibilidad).

Referencia: docs/modelo-datos/modelo_v0_1.md
"""
import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# ---------------------------------------------------------------------------
# Centros, servicios y profesionales (contexto organizativo)
# ---------------------------------------------------------------------------

class CertificadoDiscapacidad(models.Model):
    """Certificado oficial de discapacidad (Junta de Castilla y León).

    Histórico: se conservan los certificados anteriores cuando hay revisión.
    El último activo (`vigente=True`) es el que aplica.
    """

    class TipoReconocimiento(models.TextChoices):
        PERMANENTE = "permanente", "Permanente"
        REVISABLE = "revisable", "Revisable"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    persona = models.ForeignKey("personas.PersonaAtendida", on_delete=models.CASCADE,
        related_name="certificados_discapacidad",
    )
    fecha_reconocimiento = models.DateField()
    fecha_efectividad = models.DateField(
        null=True, blank=True,
        help_text="Fecha desde la que tiene efectos. Si vacío, se asume = reconocimiento.",
    )
    diagnostico_principal = models.CharField(max_length=255)
    diagnosticos_secundarios = models.TextField(
        blank=True,
        help_text="Uno por línea. Para v1.0 se normaliza en tabla aparte.",
    )

    grado_pct = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="% de discapacidad reconocido.",
    )
    puntos_factores_sociales = models.PositiveSmallIntegerField(default=0)
    puntos_movilidad_reducida = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="≥ 7 puntos otorga el reconocimiento de movilidad reducida.",
    )

    tipo_reconocimiento = models.CharField(
        max_length=16, choices=TipoReconocimiento.choices,
        default=TipoReconocimiento.PERMANENTE,
    )
    fecha_validez_hasta = models.DateField(
        null=True, blank=True,
        help_text="Fecha hasta la que es válido. Solo si tipo=revisable.",
    )
    tipo_reconocimiento_movilidad = models.CharField(
        max_length=16, choices=TipoReconocimiento.choices,
        blank=True,
        help_text="Tipo de reconocimiento específico del reconocimiento de movilidad.",
    )
    fecha_validez_movilidad_hasta = models.DateField(null=True, blank=True)

    vigente = models.BooleanField(
        default=True,
        help_text="Marcado automáticamente: solo el último activo es vigente.",
    )
    documento_pdf = models.FileField(
        upload_to="certificados_discapacidad/%Y/", null=True, blank=True,
        help_text="PDF del certificado escaneado. Solo accesible bajo permisos restringidos.",
    )
    notas = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Certificado de discapacidad"
        verbose_name_plural = "Certificados de discapacidad"
        ordering = ["-fecha_reconocimiento"]
        indexes = [models.Index(fields=["persona", "vigente"])]

    def __str__(self) -> str:
        return f"{self.grado_pct}% · {self.persona} · {self.fecha_reconocimiento}"


# ---------------------------------------------------------------------------
# Reconocimiento de dependencia (Ley 39/2006)
# ---------------------------------------------------------------------------


class ReconocimientoDependencia(models.Model):
    """Resolución de grado y nivel de dependencia (Ley 39/2006 / RD 174/2011).

    Histórico igual que el certificado de discapacidad.
    """

    class Grado(models.TextChoices):
        I = "I", "Grado I — Dependencia moderada"  # noqa: E741 — convención Ley 39/2006
        II = "II", "Grado II — Dependencia severa"
        III = "III", "Grado III — Gran dependencia"
        NO_DEPENDIENTE = "no_dependiente", "No dependiente"

    class TipoBeneficio(models.TextChoices):
        PLAZA_RESIDENCIAL = "plaza_residencial", "Plaza concertada residencial"
        PLAZA_CENTRO_DIA = "plaza_centro_dia", "Plaza concertada centro de día"
        SAD = "sad", "Servicio de ayuda a domicilio"
        TELEASISTENCIA = "teleasistencia", "Teleasistencia"
        PRESTACION_ECONOMICA = "prestacion_economica", "Prestación económica"
        OTROS = "otros", "Otros"
        SIN_BENEFICIO = "sin_beneficio", "Sin beneficio"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    persona = models.ForeignKey("personas.PersonaAtendida", on_delete=models.CASCADE,
        related_name="reconocimientos_dependencia",
    )
    grado = models.CharField(max_length=20, choices=Grado.choices)
    puntos_bvd = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="Puntuación BVD que sustenta el grado reconocido.",
    )
    tipo_dependencia = models.CharField(
        max_length=64, blank=True,
        help_text="P. ej. 'Física', 'Mental', 'Mixta'.",
    )

    fecha_solicitud = models.DateField(null=True, blank=True)
    fecha_resolucion = models.DateField()
    fecha_revision = models.DateField(
        null=True, blank=True,
        help_text="Próxima fecha de revisión obligatoria.",
    )

    tipo_beneficio = models.CharField(
        max_length=24, choices=TipoBeneficio.choices, default=TipoBeneficio.SIN_BENEFICIO,
    )
    servicio_concertado = models.CharField(
        max_length=255, blank=True,
        help_text="Servicio concreto donde se materializa el beneficio.",
    )

    vigente = models.BooleanField(default=True)
    documento_pdf = models.FileField(
        upload_to="reconocimientos_dependencia/%Y/", null=True, blank=True,
    )
    notas = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Reconocimiento de dependencia"
        verbose_name_plural = "Reconocimientos de dependencia"
        ordering = ["-fecha_resolucion"]
        indexes = [models.Index(fields=["persona", "vigente"])]

    def __str__(self) -> str:
        return f"{self.get_grado_display()} · {self.persona}"


# ---------------------------------------------------------------------------
# Información médica — DATOS DE CATEGORÍA ESPECIAL (RGPD art. 9)
# ---------------------------------------------------------------------------
#
# Permisos: solo profesionales con rol clínico (DUE, médico, psicólogo)
# y la propia persona y su figura de apoyo. Acceso siempre con bitácora.
# Retención: mientras dure la atención + 5 años (defensa legal).
# Base jurídica: ejecución de servicios sociosanitarios (RGPD 6.1.b) +
# consentimiento explícito para datos de salud (art. 9.2.a).
# ---------------------------------------------------------------------------



"""Modelo de datos · módulo "apoyo_y_avisos" (split de models.py para legibilidad).

Referencia: docs/modelo-datos/modelo_v0_1.md
"""
import uuid

from django.conf import settings
from django.db import models

# ---------------------------------------------------------------------------
# Centros, servicios y profesionales (contexto organizativo)
# ---------------------------------------------------------------------------

class MedidaDeApoyo(models.Model):
    """Medida de apoyo (Ley 8/2021).

    Obligatoria para cada persona atendida: 'sin medida' también es un valor explícito.
    """

    class Tipo(models.TextChoices):
        SIN_MEDIDA = "sin_medida", "Sin medida — Persona capaz"
        APOYO_VOLUNTARIO = "apoyo_voluntario", "Apoyo voluntario"
        APOYO_JUDICIAL = "apoyo_judicial", "Apoyo establecido judicialmente"
        APOYO_HECHO = "apoyo_hecho", "Apoyo de hecho"

    class SubtipoCuratela(models.TextChoices):
        NO_PROCEDE = "no_procede", "No procede"
        REPRESENTATIVA_TOTAL = "representativa_total", "Curatela representativa total"
        REPRESENTATIVA_PARCIAL = "representativa_parcial", "Curatela representativa parcial"
        ASISTENCIAL = "asistencial", "Curatela asistencial"
        DEFENSOR_JUDICIAL = "defensor_judicial", "Defensor judicial"
        GUARDA_HECHO = "guarda_hecho", "Guarda de hecho"

    persona = models.OneToOneField("personas.PersonaAtendida", on_delete=models.CASCADE, related_name="medida_apoyo",
    )
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.SIN_MEDIDA)
    subtipo_curatela = models.CharField(
        max_length=24, choices=SubtipoCuratela.choices,
        default=SubtipoCuratela.NO_PROCEDE,
        help_text="Subtipo concreto cuando el tipo es apoyo judicial.",
    )
    fecha_resolucion = models.DateField(null=True, blank=True)
    organo_judicial = models.CharField(
        max_length=255, blank=True,
        help_text="Órgano que dictó la resolución (p. ej. Juzgado 1ª Inst. Burgos nº 4).",
    )
    numero_procedimiento = models.CharField(max_length=64, blank=True)

    # Curatela: por persona física o por entidad
    es_curatela_entidad = models.BooleanField(
        default=False,
        help_text="Marcar si la curatela la ejerce una entidad (no persona física).",
    )
    persona_curadora = models.ForeignKey(
        "personas.PersonaContacto",
        on_delete=models.PROTECT, null=True, blank=True,
        related_name="curatelas_ejercidas",
        help_text="Persona física que ejerce la curatela. Vacío si es entidad.",
    )
    entidad_curadora = models.CharField(
        max_length=255, blank=True,
        help_text="Nombre de la entidad que ejerce la curatela cuando aplique.",
    )

    ambito_apoyos = models.TextField(
        blank=True,
        help_text="Descripción del alcance: qué decisiones, en qué ámbitos.",
    )
    ambito_capacidad_conservada = models.TextField(
        blank=True,
        help_text="Qué decisiones toma la persona por sí misma.",
    )
    vigente = models.BooleanField(default=True)
    revisado_at = models.DateField(null=True, blank=True)
    proxima_revision_at = models.DateField(
        null=True, blank=True,
        help_text="Próxima revisión judicial obligatoria (Ley 8/2021 art. 268: máx. 3 años).",
    )
    notas = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Medida de apoyo (Ley 8/2021)"
        verbose_name_plural = "Medidas de apoyo (Ley 8/2021)"

    def __str__(self) -> str:
        return f"{self.get_tipo_display()} · {self.persona}"


class FiguraDeApoyo(models.Model):
    """Persona o institución que presta apoyo bajo una MedidaDeApoyo."""

    medida = models.ForeignKey(
        MedidaDeApoyo, on_delete=models.CASCADE, related_name="figuras_apoyo",
    )
    contacto = models.ForeignKey("personas.PersonaContacto", on_delete=models.PROTECT, related_name="figuras_apoyo",
    )
    ambito = models.CharField(
        max_length=255,
        help_text="Ámbito concreto del apoyo prestado por esta figura.",
    )

    class Meta:
        verbose_name = "Figura de apoyo"
        verbose_name_plural = "Figuras de apoyo"

    def __str__(self) -> str:
        return f"{self.contacto} → {self.medida.persona}"


# ---------------------------------------------------------------------------
# Avisos automáticos de cambio de profesional (Protocolo Planes de Vida §9)
# ---------------------------------------------------------------------------


class AvisoCambioProfesional(models.Model):
    """Aviso disparado automáticamente cuando cambia el Gestor/a de Caso
    o la Persona de Referencia de una persona atendida.

    Lo genera ÁGORA vía signal en `personas.signals`. Va dirigido a Dirección
    para garantizar el traspaso y la continuidad descritos en el protocolo §9.
    """

    class TipoCambio(models.TextChoices):
        ALTA_GESTOR = "alta_gestor", "Alta de Gestor/a de Caso"
        CAMBIO_GESTOR = "cambio_gestor", "Cambio de Gestor/a de Caso"
        BAJA_GESTOR = "baja_gestor", "Baja de Gestor/a de Caso (sin reemplazo)"
        ALTA_REFERENCIA = "alta_referencia", "Alta de Persona de Referencia"
        CAMBIO_REFERENCIA = "cambio_referencia", "Cambio de Persona de Referencia"
        BAJA_REFERENCIA = "baja_referencia", "Baja de Persona de Referencia (sin reemplazo)"

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        EN_TRATAMIENTO = "en_tratamiento", "En tratamiento"
        RESUELTO = "resuelto", "Resuelto"
        DESCARTADO = "descartado", "Descartado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    persona = models.ForeignKey("personas.PersonaAtendida", on_delete=models.CASCADE, related_name="avisos_cambio_profesional",
    )
    tipo = models.CharField(max_length=24, choices=TipoCambio.choices)
    profesional_anterior = models.ForeignKey(
        "personas.Profesional", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="avisos_como_anterior",
    )
    profesional_nuevo = models.ForeignKey(
        "personas.Profesional", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="avisos_como_nuevo",
    )
    estado = models.CharField(max_length=16, choices=Estado.choices, default=Estado.PENDIENTE)
    detectado_at = models.DateTimeField(auto_now_add=True)
    resuelto_at = models.DateTimeField(null=True, blank=True)
    resuelto_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="avisos_resueltos",
    )
    notas_resolucion = models.TextField(blank=True)

    class Meta:
        verbose_name = "Aviso de cambio de profesional"
        verbose_name_plural = "Avisos de cambio de profesional"
        ordering = ["-detectado_at"]
        indexes = [
            models.Index(fields=["estado", "-detectado_at"]),
            models.Index(fields=["persona", "-detectado_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.get_tipo_display()} · {self.persona} · {self.detectado_at:%Y-%m-%d %H:%M}"


# ---------------------------------------------------------------------------
# Certificado de discapacidad — bloque jurídico-administrativo
# ---------------------------------------------------------------------------



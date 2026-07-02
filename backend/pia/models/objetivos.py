"""Plan de Vida — Fundación Aspanias.

Modelo alineado con el "Protocolo de elaboración, seguimiento y revisión de
Planes de Vida — Centros y Servicios, Fundación Aspanias".

Componentes principales:
- PlanDeVida: contenedor anual con gestor/a de caso, persona de referencia y estado.
- DocumentoPlanDeVida: los 5 documentos obligatorios (historia de vida, algo sobre mí,
  revisión de objetivos, plan de apoyo al proyecto de vida, proyecto de vida).
- Objetivo: objetivos personales reflejados en el plan, vinculables a intervenciones.
- CambioSignificativo: cambios detectados en salud, empleo, vivienda, rutinas, relaciones
  o participación social — clave para la revisión anual.

Mantengo `app_label = pia` para no romper migraciones; la URL pública es /planes-vida/.
"""
import uuid

from django.db import models

from personas.models import PersonaAtendida, Profesional


class Objetivo(models.Model):
    """Objetivo personal del Plan de Vida.

    En el protocolo no se prescriben ámbitos cerrados — se trabajan los que tienen
    sentido para la persona. Mantenemos catálogo orientativo, ampliable.
    """

    class Ambito(models.TextChoices):
        SALUD = "salud", "Salud"
        AUTONOMIA = "autonomia", "Autonomía"
        RELACIONES = "relaciones", "Relaciones"
        OCIO = "ocio", "Ocio y tiempo libre"
        FORMACION = "formacion", "Formación"
        EMPLEO = "empleo", "Empleo"
        VIVIENDA = "vivienda", "Vivienda"
        PARTICIPACION_SOCIAL = "participacion", "Participación social"
        ESPIRITUALIDAD = "espiritualidad", "Espiritualidad y valores"
        OTRO = "otro", "Otro"

    class Prioridad(models.TextChoices):
        ALTA = "alta", "Alta"
        MEDIA = "media", "Media"
        BAJA = "baja", "Baja"

    class Estado(models.TextChoices):
        PROPUESTO = "propuesto", "Propuesto"
        ACTIVO = "activo", "En curso"
        LOGRADO = "logrado", "Logrado"
        MANTENIMIENTO = "mantenimiento", "En mantenimiento"
        ABANDONADO = "abandonado", "Abandonado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan_vida = models.ForeignKey("pia.PlanDeVida", on_delete=models.CASCADE, related_name="objetivos",
    )
    ambito = models.CharField(max_length=16, choices=Ambito.choices)
    descripcion = models.TextField(
        help_text="En el lenguaje de la persona cuando aplique.",
    )
    indicador_logro = models.TextField(help_text="Cómo se mide el éxito.")
    apoyos_necesarios = models.TextField(blank=True)
    responsable_seguimiento = models.ForeignKey(
        Profesional, on_delete=models.PROTECT, related_name="objetivos_plan_vida",
        null=True, blank=True,
    )
    prioridad = models.CharField(max_length=8, choices=Prioridad.choices, default=Prioridad.MEDIA)
    estado = models.CharField(max_length=16, choices=Estado.choices, default=Estado.PROPUESTO)
    visible_en_panel = models.BooleanField(
        default=False,
        help_text="Si está visible en panel/corcho del centro (con consentimiento de la persona).",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Objetivo del Plan de Vida"
        verbose_name_plural = "Objetivos del Plan de Vida"
        ordering = ["ambito", "-prioridad"]

    def __str__(self) -> str:
        return f"{self.get_ambito_display()} · {self.descripcion[:60]}"


class RevisionObjetivo(models.Model):
    """Registro anual de seguimiento de un Objetivo del Plan de Vida.

    Refleja el formato real del documento "Revisión de objetivos" usado en
    Fundación Aspanias (cuatro columnas):
      - Objetivo (vínculo al Objetivo)
      - ¿Qué ha logrado hasta la fecha?
      - Si no lo ha conseguido, ¿cuál puede ser el motivo?
      - ¿Cómo podemos ayudarle a conseguirlo? Propuestas de apoyo.

    Una revisión por objetivo y anualidad. La acumulación de revisiones permite
    leer la trayectoria longitudinal del objetivo a lo largo de los años.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    objetivo = models.ForeignKey(
        Objetivo, on_delete=models.CASCADE, related_name="revisiones",
    )
    anualidad = models.PositiveSmallIntegerField(
        help_text="Año al que corresponde la revisión (2025, 2026...).",
    )
    fecha_revision = models.DateField()
    que_ha_logrado = models.TextField(
        blank=True,
        verbose_name="¿Qué ha logrado hasta la fecha?",
    )
    motivo_no_consecucion = models.TextField(
        blank=True,
        verbose_name="Si no lo ha conseguido, ¿cuál puede ser el motivo?",
    )
    propuesta_apoyos = models.TextField(
        blank=True,
        verbose_name="¿Cómo podemos ayudarle? Propuestas de apoyo",
    )
    realizada_por = models.ForeignKey(
        Profesional, on_delete=models.PROTECT, related_name="revisiones_objetivos",
        null=True, blank=True,
        help_text="Profesional que realiza la revisión (gestor/a de caso o persona de referencia).",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Revisión de objetivo"
        verbose_name_plural = "Revisiones de objetivos"
        ordering = ["-anualidad", "-fecha_revision"]
        unique_together = [("objetivo", "anualidad")]

    def __str__(self) -> str:
        return f"Revisión {self.anualidad} · {self.objetivo}"


class CambioSignificativo(models.Model):
    """Cambio significativo detectado entre revisiones anuales.

    El protocolo destaca seis ámbitos típicos donde se detectan cambios que
    obligan a actualizar el Plan de Vida.
    """

    class Ambito(models.TextChoices):
        SALUD = "salud", "Salud"
        EMPLEO = "empleo", "Empleo"
        CENTRO_VIVIENDA = "centro_vivienda", "Cambio de centro o vivienda"
        RUTINAS = "rutinas", "Rutinas"
        RELACIONES = "relaciones", "Relaciones"
        PARTICIPACION_SOCIAL = "participacion", "Participación social"
        OTRO = "otro", "Otro"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    persona = models.ForeignKey(
        PersonaAtendida, on_delete=models.CASCADE, related_name="cambios_significativos",
    )
    plan_vida = models.ForeignKey("pia.PlanDeVida", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="cambios_significativos",
        help_text="Plan de Vida vigente al detectar el cambio.",
    )
    ambito = models.CharField(max_length=24, choices=Ambito.choices)
    descripcion = models.TextField()
    fecha_deteccion = models.DateField()
    detectado_por = models.ForeignKey(
        Profesional, on_delete=models.PROTECT, related_name="cambios_detectados",
        null=True, blank=True,
        help_text="Suele ser la persona de referencia.",
    )
    requiere_actualizacion_plan = models.BooleanField(default=True)
    procesado = models.BooleanField(
        default=False,
        help_text="True cuando ya se ha actualizado el Plan de Vida con este cambio.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cambio significativo"
        verbose_name_plural = "Cambios significativos"
        ordering = ["-fecha_deteccion"]
        indexes = [models.Index(fields=["persona", "-fecha_deteccion"])]

    def __str__(self) -> str:
        return f"{self.get_ambito_display()} · {self.fecha_deteccion} · {self.persona}"


# ---------------------------------------------------------------------------
# Documento 1 — Historia de Vida (cuestionario narrativo)
# ---------------------------------------------------------------------------



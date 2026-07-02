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

from personas.models import Profesional


class DimensionCalidadVida(models.Model):
    """Dimensiones de Calidad de Vida (modelo Schalock & Verdugo).

    Catálogo confirmado por la plantilla oficial en blanco del documento
    "Plan de apoyo al proyecto de vida" (ANEXO 4 del protocolo Aspanias).
    """

    codigo = models.CharField(max_length=32, unique=True)
    nombre = models.CharField(max_length=128)
    descripcion = models.TextField(blank=True)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Dimensión de Calidad de Vida"
        verbose_name_plural = "Dimensiones de Calidad de Vida"
        ordering = ["orden"]

    def __str__(self) -> str:
        return self.nombre


# 8 dimensiones según el ANEXO 4 oficial del Plan de Apoyo.
DIMENSIONES_CDV_SCHALOCK = [
    ("autodeterminacion", "Autodeterminación", "Control personal, elección…", 1),
    ("bienestar_emocional", "Bienestar Emocional", "Felicidad, seguridad…", 2),
    ("bienestar_fisico", "Bienestar Físico", "Salud, nutrición, cuidados básicos…", 3),
    ("bienestar_material", "Bienestar Material", "Tener y disfrutar de pertenencias, tener empleo.", 4),
    ("relaciones", "Relaciones Interpersonales Significativas", "Amigos, familias…", 5),
    ("inclusion_social", "Inclusión Social", "Participar en la comunidad, ser conocido y aceptado.", 6),
    ("desarrollo_personal", "Desarrollo Personal", "Desarrollar habilidades y competencias, tener experiencias nuevas…", 7),
    ("derechos", "Derechos", "Libertades, intimidad, privacidad, dignidad, autonomía, derechos de ciudadanía…", 8),
]


class PlanDeApoyo(models.Model):
    """Documento 'Plan de apoyo al proyecto de vida' (Anexo 4 del protocolo Aspanias).

    Vincula los objetivos del Plan de Vida con las dimensiones de Calidad de Vida
    del modelo Schalock y describe los apoyos necesarios.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan_vida = models.OneToOneField("pia.PlanDeVida", on_delete=models.CASCADE, related_name="plan_apoyo",
    )
    fecha_realizacion = models.DateField(null=True, blank=True)
    realizado_por = models.ForeignKey(
        Profesional, on_delete=models.PROTECT, related_name="planes_apoyo",
        null=True, blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Plan de apoyo al proyecto de vida"
        verbose_name_plural = "Planes de apoyo al proyecto de vida"

    def __str__(self) -> str:
        return f"Plan de apoyo · {self.plan_vida}"


class EntradaPlanApoyo(models.Model):
    """Fila de la tabla del Plan de Apoyo (ANEXO 4): 9 columnas oficiales."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan_apoyo = models.ForeignKey(
        PlanDeApoyo, on_delete=models.CASCADE, related_name="entradas",
    )
    objetivo_vinculado = models.ForeignKey("pia.Objetivo", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="entradas_plan_apoyo",
    )
    titulo_objetivo = models.CharField(
        max_length=255,
        help_text="Texto del objetivo. Puede coincidir con `objetivo_vinculado.descripcion`.",
    )
    actividades = models.TextField(blank=True, help_text="Actividades para alcanzar el objetivo.")
    dimensiones_cdv = models.ManyToManyField(
        DimensionCalidadVida, related_name="entradas", blank=True,
        help_text="Dimensiones de Calidad de Vida (modelo Schalock).",
    )
    apoyo_que = models.TextField(blank=True, verbose_name="QUÉ (Apoyo)")
    apoyo_quien = models.TextField(blank=True, verbose_name="QUIÉN (Me apoya)")
    apoyo_cuando = models.TextField(blank=True, verbose_name="CUÁNDO (Me apoyan)")
    observaciones = models.TextField(blank=True)
    seguimiento_cuantitativo = models.TextField(blank=True)
    seguimiento_descriptivo = models.TextField(blank=True)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Entrada · Plan de apoyo"
        verbose_name_plural = "Entradas · Plan de apoyo"
        ordering = ["orden"]

    def __str__(self) -> str:
        return f"{self.titulo_objetivo[:60]} · {self.plan_apoyo}"


# ---------------------------------------------------------------------------
# Documento 5 — Proyecto de vida (bloques narrativos)
# ---------------------------------------------------------------------------



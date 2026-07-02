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


class AlgoSobreMi(models.Model):
    """Documento 'Algo sobre mí': ficha personal de aspectos funcionales y de vida.

    Una ficha por Plan de Vida. Las secciones temáticas son flexibles para
    permitir adaptación cuando llegue la plantilla en blanco real.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan_vida = models.OneToOneField("pia.PlanDeVida", on_delete=models.CASCADE, related_name="algo_sobre_mi",
    )
    fecha_actualizacion = models.DateField(null=True, blank=True)
    actualizado_por = models.ForeignKey(
        Profesional, on_delete=models.PROTECT, related_name="algo_sobre_mi_actualizados",
        null=True, blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Algo sobre mí"
        verbose_name_plural = "Algo sobre mí"

    def __str__(self) -> str:
        return f"Algo sobre mí · {self.plan_vida}"


class SeccionAlgoSobreMi(models.Model):
    """Sección temática de 'Algo sobre mí' (Movilidad, Higiene, Comunicación, etc.)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    documento = models.ForeignKey(
        AlgoSobreMi, on_delete=models.CASCADE, related_name="secciones",
    )
    codigo = models.CharField(max_length=32, help_text="Identificador estable (movilidad, higiene...).")
    titulo = models.CharField(max_length=128)
    contenido = models.TextField(blank=True)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Sección · Algo sobre mí"
        verbose_name_plural = "Secciones · Algo sobre mí"
        ordering = ["orden"]
        unique_together = [("documento", "codigo")]

    def __str__(self) -> str:
        return f"{self.titulo} · {self.documento}"


# Catálogo de secciones — extraído de la plantilla oficial en blanco
# del documento "Algo sobre mí" (Fundación Aspanias).
SECCIONES_ALGO_SOBRE_MI = [
    ("datos_personales", "Datos personales (situación legal, tutor, prestaciones)"),
    ("salud", "Salud y medicación"),
    ("alimentacion", "Alimentación e ingesta de líquidos"),
    ("sueno_continencia", "Sueño y continencia"),
    ("movilidad", "Movilidad"),
    ("higiene", "Higiene y cuidado personal"),
    ("autonomia_avd", "Autonomía en actividades de la vida diaria"),
    ("comunicacion", "Comunicación"),
    ("salud_mental", "Salud mental y diagnósticos"),
    ("desarrollo_personal", "Desarrollo personal, laboral y de ocio"),
    ("relaciones", "Relaciones interpersonales y espacios que habito"),
]


# ---------------------------------------------------------------------------
# Documento 4 — Plan de apoyo al proyecto de vida (ANEXO 4, plantilla oficial)
# ---------------------------------------------------------------------------



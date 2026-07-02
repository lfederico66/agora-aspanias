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


class ProyectoDeVida(models.Model):
    """Documento 'Proyecto de Vida' del Plan de Vida (plantilla oficial Aspanias).

    Tabla 13×5 del documento Word original con secciones:
    - Datos identificativos (cubiertos por PersonaAtendida + PlanDeVida).
    - Deseos y Metas (3 sueños).
    - Valores.
    - Lo que me gusta de mi día a día / Lo que NO me gusta.
    - Red de apoyos (naturales / profesionales / comunitarios).
    - Hitos · Mi Historia de Vida.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan_vida = models.OneToOneField("pia.PlanDeVida", on_delete=models.CASCADE, related_name="proyecto_vida",
    )
    fecha = models.DateField(null=True, blank=True)
    elaborado_por = models.ForeignKey(
        Profesional, on_delete=models.PROTECT, related_name="proyectos_vida",
        null=True, blank=True,
    )

    # Deseos y Metas — 3 sueños narrativos
    sueno_1 = models.TextField(blank=True, verbose_name="Sueño 1")
    sueno_2 = models.TextField(blank=True, verbose_name="Sueño 2")
    sueno_3 = models.TextField(blank=True, verbose_name="Sueño 3")

    # Valores personales
    valores = models.TextField(blank=True, verbose_name="Valores")

    # Lo que me gusta / no me gusta del día a día
    me_gusta_dia_a_dia = models.TextField(blank=True, verbose_name="Lo que me gusta de mi día a día")
    no_me_gusta_dia_a_dia = models.TextField(blank=True, verbose_name="Lo que NO me gusta de mi día a día")

    # Red de apoyos
    apoyos_naturales = models.TextField(blank=True, verbose_name="Apoyos naturales")
    apoyos_profesionales = models.TextField(blank=True, verbose_name="Apoyos profesionales")
    apoyos_comunitarios = models.TextField(blank=True, verbose_name="Apoyos comunitarios")

    # Hitos
    hitos_historia_vida = models.TextField(
        blank=True,
        verbose_name="Hitos · Mi Historia de Vida",
        help_text="Eventos importantes de la vida de la persona.",
    )

    publicado_en_repriss = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Proyecto de Vida"
        verbose_name_plural = "Proyectos de Vida"

    def __str__(self) -> str:
        return f"Proyecto de Vida · {self.plan_vida}"



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


class HistoriaDeVida(models.Model):
    """Documento 'Historia de Vida' del Plan de Vida.

    Cuestionario narrativo abierto que recoge la trayectoria personal de la
    persona atendida. Una historia por Plan de Vida (anualidad).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan_vida = models.OneToOneField("pia.PlanDeVida", on_delete=models.CASCADE, related_name="historia_vida",
    )
    fecha_recogida = models.DateField(null=True, blank=True)
    facilitador = models.ForeignKey(
        Profesional, on_delete=models.PROTECT, related_name="historias_facilitadas",
        null=True, blank=True,
        help_text="Profesional que facilita la conversación (suele ser persona de referencia).",
    )
    notas_generales = models.TextField(blank=True)
    texto_narrativo_final = models.TextField(
        blank=True,
        verbose_name="Historia de Vida (redacción final)",
        help_text="Narrativa final de la historia de vida tras la conversación con la persona.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Historia de Vida"
        verbose_name_plural = "Historias de Vida"

    def __str__(self) -> str:
        return f"Historia de Vida · {self.plan_vida}"


class RespuestaHistoriaVida(models.Model):
    """Respuesta narrativa a una pregunta del guion de Historia de Vida."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    historia = models.ForeignKey(
        HistoriaDeVida, on_delete=models.CASCADE, related_name="respuestas",
    )
    pregunta_codigo = models.CharField(max_length=16, help_text="Código estable (HV01, HV02...).")
    pregunta_texto = models.TextField()
    respuesta_texto = models.TextField(blank=True)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Respuesta · Historia de Vida"
        verbose_name_plural = "Respuestas · Historia de Vida"
        ordering = ["orden"]
        unique_together = [("historia", "pregunta_codigo")]

    def __str__(self) -> str:
        return f"{self.pregunta_codigo} · {self.pregunta_texto[:60]}"


# Catálogo de preguntas — guion oficial Aspanias para facilitar la Historia de Vida.
# El protocolo recalca: "No pretende ser un cuestionario ni entrevista, sino unas
# claves que el profesional tendrá en cuenta a la hora de orientar la conversación".
PREGUNTAS_HISTORIA_VIDA = [
    ("HV01", "Cómo es tu vida actualmente"),
    ("HV02", "¿Cómo es un día habitual en tu vida actual?"),
    ("HV03", "Qué cosas son importantes para la persona"),
    ("HV04", "Qué es lo que tiene más valor en su vida"),
    ("HV05", "Con qué disfruta. Qué cosas hacen que su vida merezca la pena"),
    ("HV06", "Qué es lo que más echarías de menos si no pudieras hacerlo"),
    ("HV07", "Cómo es un buen día y un mal día"),
    ("HV08", "Cómo era tu vida cuando eras niña/o"),
    ("HV09", "Recuerda actividades en las que disfrutabas cuando eras más joven. ¿Qué tipo de actividades hacía? ¿Qué le gustaba hacer? ¿Qué actividades extraescolares realizaba? ¿Cómo pasaba el tiempo libre? ¿Qué actividades de ocio realizaba? ¿Qué recuerdos guarda de sus amigos de juventud? Cuéntame alguna anécdota."),
    ("HV10", "¿Hacías alguna actividad de ocio con tu familia? Cuéntame algún momento que recuerdes disfrutando con tu familia"),
    ("HV11", "Recuerda algún momento de especial alegría en tu vida. ¿Cuál era la situación? ¿Qué hacías? ¿Quién estaba?"),
    ("HV12", "Qué te gustaba hacer. ¿En qué eres bueno/a?"),
    ("HV13", "¿Qué has estudiado, te gustaría seguir formándote? ¿En qué?"),
    ("HV14", "¿Es importante el trabajo para ti? ¿Has trabajado? ¿En qué? ¿En qué crees que estás más capacitado/a para trabajar?"),
    ("HV15", "¿En qué te gustaría trabajar si encontrases trabajo?"),
    ("HV16", "¿Dónde has estado de vacaciones o de viaje? ¿Y dónde te gustaría ir?"),
    ("HV17", "¿Hay algo que siempre quisiste hacer, pero que no has llegado a realizar nunca?"),
    ("HV18", "Según la gente que te conoce, ¿qué es lo que mejor se le da hacer? ¿Y según ella misma? ¿Qué cosas te gusta hacer ahora?"),
    ("HV19", "¿Hay momentos en los que consigues evadirte de tus problemas haciendo cosas que te gustan? Si es así, ¿cuáles?"),
    ("HV20", "Sé que ahora no es lo mismo que cuando eras joven, pero imagina por un momento que no existe ninguna barrera que te impida realizar aquello que te gustaría. ¿Qué harías? ¿Qué tipo de persona te gustaría ser? ¿Qué estarías haciendo ahora mismo?"),
    ("HV21", "¿Cuáles han sido los momentos más importantes de tu vida? ¿Qué recuerdos querrías volver a vivir, si pudieras?"),
]

# Claves metodológicas para el profesional (nota informativa, no respuestas).
CLAVES_RELACION_HISTORIA_VIDA = [
    "Interacción simétrica, es necesaria la humildad por parte de la persona de apoyo.",
    "Escuchar de una manera especial, estando en contacto y centrado en la persona.",
    "Mostrar cercanía de una manera natural.",
    "Expresar empatía, amor, amabilidad y transparencia.",
    "Aprender a no solucionar y validar incondicionalmente la experiencia de la persona.",
    "Actuar con conciencia (notando lo que experimentamos y compartiéndolo) y valentía.",
    "No centrar la conversación en problemas o enfermedades.",
]


# ---------------------------------------------------------------------------
# Documento 2 — Algo sobre mí (ficha personal por secciones)
# ---------------------------------------------------------------------------



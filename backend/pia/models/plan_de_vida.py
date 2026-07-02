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


class PlanDeVida(models.Model):
    """Plan de Vida anual de una persona atendida.

    Una persona puede tener un Plan de Vida por anualidad (2025, 2026, 2027...).
    Solo uno puede estar en estado vigente simultáneamente.
    """

    class Estado(models.TextChoices):
        EN_ELABORACION = "elaboracion", "En elaboración"
        VIGENTE = "vigente", "Vigente"
        EN_REVISION = "revision", "En revisión anual"
        ARCHIVADO = "archivado", "Archivado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    persona = models.ForeignKey(
        PersonaAtendida, on_delete=models.CASCADE, related_name="planes_vida",
    )
    anualidad = models.PositiveSmallIntegerField(
        help_text="Año de referencia (2025, 2026, 2027...).",
    )
    estado = models.CharField(max_length=16, choices=Estado.choices, default=Estado.EN_ELABORACION)

    gestor_caso = models.ForeignKey(
        Profesional,
        on_delete=models.PROTECT,
        related_name="planes_vida_gestionados",
        null=True, blank=True,
        verbose_name="Gestor/a de caso",
        help_text="Coordina elaboración, seguimiento y revisión. Máx. 30 casos por gestor/a.",
    )
    persona_referencia = models.ForeignKey(
        Profesional,
        on_delete=models.PROTECT,
        related_name="planes_vida_referencia",
        null=True, blank=True,
        verbose_name="Persona de referencia",
        help_text="Genera vínculo significativo y aporta información cotidiana.",
    )

    fecha_elaboracion = models.DateField(null=True, blank=True)
    fecha_revision = models.DateField(
        null=True, blank=True,
        help_text="Última revisión anual realizada.",
    )
    fecha_proxima_revision = models.DateField(
        null=True, blank=True,
        help_text="Próxima revisión anual prevista.",
    )
    fecha_prevista_realizacion = models.DateField(
        null=True, blank=True,
        help_text="Fecha planificada para realizar el Plan (distinto de la fecha real de elaboración).",
    )

    # Flags del Excel real "Registro PV por servicios"
    pv_realizado = models.BooleanField(
        default=False,
        help_text="¿El Plan de Vida está realizado? Equivalente a la columna 'PV realizado' del Excel actual.",
    )
    pv_revisado = models.BooleanField(
        default=False,
        help_text="¿El Plan de Vida ha sido revisado? Equivalente a la columna 'PV revisado'.",
    )
    estado_revision = models.CharField(
        max_length=24,
        choices=[
            ("en_plazo", "En plazo"),
            ("fuera_plazo", "Fuera de plazo"),
            ("pendiente", "Pendiente"),
        ],
        default="pendiente",
        help_text="Estado del cumplimiento de plazos de revisión anual.",
    )
    compartido_con_residencia_vivienda = models.BooleanField(
        default=False,
        help_text="Marca cuando el usuario tiene servicios en dos modalidades (p.ej. residencia + vivienda) y el PV se comparte entre ambas.",
    )

    firmado_persona_at = models.DateTimeField(null=True, blank=True)
    firmado_apoyo_at = models.DateTimeField(null=True, blank=True)

    visible_en_paneles = models.BooleanField(
        default=False,
        help_text="Voluntad de la persona usuaria: si autoriza compartir objetivos en paneles/corchos del centro.",
    )

    notas = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Plan de Vida"
        verbose_name_plural = "Planes de Vida"
        ordering = ["-anualidad"]
        unique_together = [("persona", "anualidad")]
        indexes = [
            models.Index(fields=["estado", "fecha_proxima_revision"]),
            models.Index(fields=["gestor_caso", "estado"]),
        ]

    def __str__(self) -> str:
        return f"Plan de Vida {self.anualidad} · {self.persona}"

    @property
    def documentos_completos(self) -> int:
        return self.documentos.exclude(estado=DocumentoPlanDeVida.Estado.PENDIENTE).count()

    @property
    def total_objetivos(self) -> int:
        return self.objetivos.count()

    @property
    def objetivos_logrados(self) -> int:
        from .objetivos import Objetivo  # lazy: objetivos depende de plan_de_vida
        return self.objetivos.filter(estado=Objetivo.Estado.LOGRADO).count()


class DocumentoPlanDeVida(models.Model):
    """Cada uno de los 5 documentos obligatorios del Plan de Vida.

    Según el protocolo:
    1. Historia de Vida
    2. Algo sobre mí
    3. Revisión de objetivos
    4. Plan de apoyo al proyecto de vida
    5. Proyecto de vida

    Los documentos vivos están en Teams/OneDrive (almacenamiento autorizado).
    Aquí registramos el estado, la versión y la URL al documento real.
    """

    class Tipo(models.TextChoices):
        HISTORIA_VIDA = "historia_vida", "Historia de Vida"
        ALGO_SOBRE_MI = "algo_sobre_mi", "Algo sobre mí"
        REVISION_OBJETIVOS = "revision_objetivos", "Revisión de objetivos"
        PLAN_APOYO = "plan_apoyo", "Plan de apoyo al proyecto de vida"
        PROYECTO_VIDA = "proyecto_vida", "Proyecto de vida"

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        EN_ELABORACION = "elaboracion", "En elaboración"
        COMPLETADO = "completado", "Completado"
        REVISADO = "revisado", "Revisado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan_vida = models.ForeignKey(
        PlanDeVida, on_delete=models.CASCADE, related_name="documentos",
    )
    tipo = models.CharField(max_length=24, choices=Tipo.choices)
    estado = models.CharField(max_length=16, choices=Estado.choices, default=Estado.PENDIENTE)
    url_almacenamiento = models.URLField(
        blank=True,
        help_text="Enlace a Teams / OneDrive / espacio compartido autorizado.",
        max_length=1024,
    )
    publicado_en_repriss = models.BooleanField(
        default=False,
        help_text="Solo aplica a 'Proyecto de Vida' y 'Plan de apoyo'. Dirección lo cuelga en REPRISS.",
    )
    fecha_completado = models.DateField(null=True, blank=True)
    notas = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Documento del Plan de Vida"
        verbose_name_plural = "Documentos del Plan de Vida"
        ordering = ["plan_vida", "tipo"]
        unique_together = [("plan_vida", "tipo")]

    def __str__(self) -> str:
        return f"{self.get_tipo_display()} · Plan {self.plan_vida.anualidad} · {self.plan_vida.persona}"



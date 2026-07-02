"""Patrones de turno reutilizables (M-V, rotativo residencial, antiestrés CD, etc.).

Un patrón es la plantilla cíclica que define qué turno (M/T/N/D) le toca
a un profesional cada día del ciclo. Al combinarlo con el calendario
laboral del centro + vacaciones + formación se obtiene el calendario
individual anual del profesional.
"""
import uuid

from django.db import models


class PatronTurno(models.Model):
    """Plantilla cíclica de turnos. Reutilizable entre profesionales y centros."""

    class CodigoTurno(models.TextChoices):
        MANANA = "M", "Mañana"
        TARDE = "T", "Tarde"
        NOCHE = "N", "Noche"
        PARTIDO = "P", "Partido"
        DESCANSO = "D", "Descanso"
        VEINTICUATRO = "24", "24 horas"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    nombre = models.CharField(max_length=64, unique=True)
    descripcion = models.TextField(blank=True)

    # Patrón cíclico
    ciclo_dias = models.PositiveSmallIntegerField(
        help_text="Duración del ciclo en días. 7 = semanal, 14 = quincenal.",
    )
    secuencia = models.JSONField(
        help_text='Lista de códigos de turno por día. Ej: ["M","M","T","T","N","N","D"].',
    )
    horas_por_turno = models.JSONField(
        default=dict,
        help_text='Horas que aporta cada código. Ej: {"M":8,"T":7,"N":10,"D":0}.',
    )

    # Marco de aplicación
    centros = models.ManyToManyField(
        "personas.Centro",
        blank=True,
        help_text="Centros donde aplica este patrón. Vacío = todos.",
    )
    horas_semana = models.PositiveSmallIntegerField(
        help_text="Horas semanales teóricas del patrón (40, 35, 24, etc.).",
    )

    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Patrón de turno"
        verbose_name_plural = "Patrones de turno"
        ordering = ["nombre"]

    def __str__(self) -> str:
        return self.nombre

    def turno_para_dia(self, dia_del_ciclo: int) -> str:
        """Devuelve el código de turno para `dia_del_ciclo` (0-based)."""
        if not self.secuencia:
            return self.CodigoTurno.DESCANSO
        return self.secuencia[dia_del_ciclo % self.ciclo_dias]


class AsignacionPatron(models.Model):
    """Asignación temporal de un patrón a un profesional.

    Un profesional puede cambiar de patrón a lo largo del tiempo (cambio de
    centro, reducción de jornada, etc.). Solo una asignación vigente por
    profesional en cada fecha.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    profesional = models.ForeignKey(
        "personas.Profesional",
        on_delete=models.PROTECT,
        related_name="asignaciones_patron",
    )
    patron = models.ForeignKey(
        PatronTurno, on_delete=models.PROTECT,
        related_name="asignaciones",
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(
        null=True, blank=True,
        help_text="Null = vigente.",
    )
    offset_inicio_ciclo = models.PositiveSmallIntegerField(
        default=0,
        help_text="Día del ciclo en que arranca el profesional el 'fecha_inicio'. "
                  "Permite que dos profesionales con el mismo patrón estén desfasados.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Asignación de patrón"
        verbose_name_plural = "Asignaciones de patrón"
        ordering = ["-fecha_inicio"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(fecha_fin__isnull=True) | models.Q(fecha_fin__gte=models.F("fecha_inicio")),
                name="asignacion_patron_fecha_valida",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.profesional.nombre_completo} · {self.patron.nombre}"

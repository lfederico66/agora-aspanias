"""Turnos asistenciales planificados en cada centro y fecha.

El cuadrante de turnos es lo que materializa qué profesionales cubren cada
franja del día en cada centro. Se genera aplicando un PatronTurno al
calendario laboral, y se ajusta puntualmente por sustituciones.
"""
import uuid

from django.conf import settings
from django.db import models


class Turno(models.Model):
    """Asignación de profesionales a una franja horaria de un centro y fecha."""

    class Franja(models.TextChoices):
        MANANA = "manana", "Mañana (07-15)"
        TARDE = "tarde", "Tarde (15-22)"
        NOCHE = "noche", "Noche (22-07)"
        PARTIDO = "partido", "Partido"
        VEINTICUATRO = "veinticuatro", "24 horas"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    centro = models.ForeignKey(
        "personas.Centro",
        on_delete=models.PROTECT,
        related_name="turnos",
    )
    fecha = models.DateField()
    franja = models.CharField(max_length=16, choices=Franja.choices)

    profesionales = models.ManyToManyField(
        "personas.Profesional",
        related_name="turnos",
        blank=True,
    )

    horas_efectivas = models.DecimalField(
        max_digits=4, decimal_places=2,
        default=0,
        help_text="Suma de horas efectivas que cubre el turno.",
    )

    notas = models.TextField(blank=True)

    es_refuerzo = models.BooleanField(
        default=False,
        help_text="Marca si el turno es excepcional (cobertura de sustituciones, etc.).",
    )

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="turnos_creados",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Turno"
        verbose_name_plural = "Turnos"
        ordering = ["fecha", "franja"]
        constraints = [
            models.UniqueConstraint(
                fields=["centro", "fecha", "franja"],
                name="turno_centro_fecha_franja_unico",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.centro.nombre} · {self.fecha} · {self.get_franja_display()}"

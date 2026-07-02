"""Vacaciones y ausencias del profesional.

ÁGORA gestiona la capa operativa (qué días no está disponible) a efectos de
turnos y cobertura. La fuente de verdad formal (cómputo legal, aprobaciones
RRHH, partes médicos firmados) es **SIGPER** cuando entre en producción.
"""
import uuid

from django.conf import settings
from django.db import models


class Vacacion(models.Model):
    """Ausencia del profesional (vacaciones, asuntos propios, IT, formación…).

    Campo `documentacion` y partes médicos en IT son **categoría especial
    art. 9 RGPD** y se cifran en reposo + acceso restringido a RRHH/Dirección.
    """

    class Tipo(models.TextChoices):
        VACACIONES = "vacaciones", "Vacaciones"
        ASUNTOS_PROPIOS = "asuntos_propios", "Asuntos propios"
        FORMACION = "formacion", "Formación"
        PERMISO_RETRIBUIDO = "permiso_retribuido", "Permiso retribuido"
        IT = "it", "Incapacidad temporal (IT)"
        IT_PROLONGADA = "it_prolongada", "IT prolongada"
        LACTANCIA = "lactancia", "Lactancia / maternidad"
        OTRO = "otro", "Otro"

    class Estado(models.TextChoices):
        SOLICITADA = "solicitada", "Solicitada"
        APROBADA = "aprobada", "Aprobada"
        RECHAZADA = "rechazada", "Rechazada"
        DISFRUTADA = "disfrutada", "Disfrutada"
        EN_CURSO = "en_curso", "En curso"
        ANULADA = "anulada", "Anulada"

    class Origen(models.TextChoices):
        MANUAL = "manual", "Manual"
        SIGPER = "sigper", "Sincronizada desde SIGPER"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    profesional = models.ForeignKey(
        "personas.Profesional",
        on_delete=models.PROTECT,
        related_name="vacaciones",
    )
    tipo = models.CharField(max_length=24, choices=Tipo.choices)
    estado = models.CharField(
        max_length=16, choices=Estado.choices,
        default=Estado.SOLICITADA,
    )

    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    motivo = models.TextField(
        blank=True,
        help_text="Opcional. Obligatorio si tipo=asuntos_propios/permiso_retribuido.",
    )

    aprobada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="vacaciones_aprobadas",
    )
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    motivo_rechazo = models.TextField(blank=True)

    # Cálculos
    dias_naturales = models.PositiveSmallIntegerField(default=0)
    dias_laborables = models.PositiveSmallIntegerField(default=0)

    # Sincronización
    origen = models.CharField(
        max_length=16, choices=Origen.choices,
        default=Origen.MANUAL,
    )
    referencia_sigper = models.CharField(max_length=64, blank=True)

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vacación / ausencia"
        verbose_name_plural = "Vacaciones y ausencias"
        ordering = ["-fecha_inicio"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(fecha_fin__gte=models.F("fecha_inicio")),
                name="vacacion_fecha_valida",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.profesional.nombre_completo} · {self.get_tipo_display()} "
            f"({self.fecha_inicio} → {self.fecha_fin})"
        )

    @property
    def en_curso(self) -> bool:
        from django.utils import timezone
        hoy = timezone.now().date()
        return self.fecha_inicio <= hoy <= self.fecha_fin and self.estado == self.Estado.APROBADA

    @property
    def es_categoria_especial_rgpd(self) -> bool:
        """Las IT son categoría especial art. 9 RGPD: acceso restringido."""
        return self.tipo in (self.Tipo.IT, self.Tipo.IT_PROLONGADA)

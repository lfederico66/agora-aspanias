"""Modelo de datos · módulo "alojamiento" (split de models.py para legibilidad).

Referencia: docs/modelo-datos/modelo_v0_1.md
"""
import uuid

from django.conf import settings
from django.db import models

# ---------------------------------------------------------------------------
# Centros, servicios y profesionales (contexto organizativo)
# ---------------------------------------------------------------------------

class Modulo(models.Model):
    """Agrupación física dentro de un centro residencial o vivienda.

    En residencias grandes: 'Módulo Norte', 'Planta 2', 'Unidad de convivencia A'.
    En viviendas pequeñas: puede ser único o coincidir con la vivienda entera.
    """

    centro = models.ForeignKey("personas.Centro", on_delete=models.CASCADE, related_name="modulos")
    codigo = models.CharField(max_length=32)
    nombre = models.CharField(max_length=128)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Módulo de centro"
        verbose_name_plural = "Módulos de centro"
        ordering = ["centro", "nombre"]
        unique_together = [("centro", "codigo")]

    def __str__(self) -> str:
        return f"{self.centro.codigo} · {self.nombre}"


class Habitacion(models.Model):
    """Habitación dentro de un módulo o directamente dentro de un centro pequeño."""

    class Tipo(models.TextChoices):
        INDIVIDUAL = "individual", "Individual"
        DOBLE = "doble", "Doble"
        TRIPLE = "triple", "Triple"
        CUADRUPLE = "cuadruple", "Cuádruple"

    centro = models.ForeignKey("personas.Centro", on_delete=models.CASCADE, related_name="habitaciones",
    )
    modulo = models.ForeignKey(
        Modulo, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="habitaciones",
        help_text="Opcional. Vacío si la vivienda no se divide en módulos.",
    )
    numero = models.CharField(
        max_length=16,
        help_text="Número o identificador (p. ej. '101', 'B-3', 'Verde').",
    )
    tipo = models.CharField(max_length=12, choices=Tipo.choices, default=Tipo.INDIVIDUAL)
    superficie_m2 = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Superficie útil en m². Útil para inspecciones JCyL.",
    )
    con_bano_propio = models.BooleanField(default=False)
    adaptada_movilidad_reducida = models.BooleanField(
        default=False,
        help_text="Habitación adaptada a movilidad reducida (PMR).",
    )
    observaciones = models.TextField(blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Habitación"
        verbose_name_plural = "Habitaciones"
        ordering = ["centro", "modulo", "numero"]
        unique_together = [("centro", "numero")]

    def __str__(self) -> str:
        prefix = f"{self.modulo.codigo}-" if self.modulo else ""
        return f"{self.centro.codigo} · Hab. {prefix}{self.numero}"


class Cama(models.Model):
    """Cama individual dentro de una habitación."""

    habitacion = models.ForeignKey(
        Habitacion, on_delete=models.CASCADE, related_name="camas",
    )
    identificador = models.CharField(
        max_length=8,
        help_text="Letra o número dentro de la habitación (A, B, 1, 2…).",
    )
    articulada = models.BooleanField(
        default=False, help_text="Cama articulada (geriátrica/eléctrica).",
    )
    barandillas = models.BooleanField(
        default=False,
        help_text="Con barandillas. Requiere registro como medida de sujeción si procede.",
    )
    grua_compatible = models.BooleanField(
        default=False, help_text="Compatible con grúa de transferencia.",
    )
    observaciones = models.TextField(blank=True)
    activa = models.BooleanField(
        default=True,
        help_text="Si está fuera de servicio (reparación, retirada) marcar False.",
    )

    class Meta:
        verbose_name = "Cama"
        verbose_name_plural = "Camas"
        ordering = ["habitacion", "identificador"]
        unique_together = [("habitacion", "identificador")]

    def __str__(self) -> str:
        return f"{self.habitacion} · Cama {self.identificador}"

    @property
    def ocupacion_actual(self):
        """Devuelve la `OcupacionCama` vigente para esta cama, o None."""
        return self.ocupaciones.filter(fecha_fin__isnull=True).first()

    @property
    def esta_libre(self) -> bool:
        return self.activa and self.ocupacion_actual is None


class OcupacionCama(models.Model):
    """Histórico de ocupación de una cama por una persona atendida.

    Constraints:
      - Una sola ocupación activa (`fecha_fin=NULL`) por persona simultáneamente.
      - Una sola ocupación activa por cama simultáneamente.

    El cierre de una ocupación (al cambiar de cama o salir del centro) se hace
    poniendo `fecha_fin` y `motivo_baja`. La nueva ocupación se crea como
    registro independiente.
    """

    class Motivo(models.TextChoices):
        INICIAL = "inicial", "Alta inicial"
        TRASLADO_INTERNO = "traslado_interno", "Traslado interno (otra cama/habitación)"
        REFORMA = "reforma", "Reforma en la habitación"
        CONVIVENCIA = "convivencia", "Cambio por convivencia"
        NECESIDADES_APOYO = "necesidades_apoyo", "Cambio por necesidades de apoyo"
        SALIDA = "salida", "Salida del centro"
        HOSPITALIZACION = "hospitalizacion", "Hospitalización prolongada"
        FALLECIMIENTO = "fallecimiento", "Fallecimiento"
        OTRO = "otro", "Otro"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    persona = models.ForeignKey("personas.PersonaAtendida", on_delete=models.CASCADE, related_name="ocupaciones_cama",
    )
    cama = models.ForeignKey(
        Cama, on_delete=models.PROTECT, related_name="ocupaciones",
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    motivo_alta = models.CharField(
        max_length=24, choices=Motivo.choices, default=Motivo.INICIAL,
    )
    motivo_baja = models.CharField(
        max_length=24, choices=Motivo.choices, blank=True,
        help_text="Requerido cuando se informa fecha_fin.",
    )
    observaciones = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="ocupaciones_cama_creadas",
    )

    class Meta:
        verbose_name = "Ocupación de cama"
        verbose_name_plural = "Ocupaciones de cama"
        ordering = ["-fecha_inicio"]
        indexes = [
            models.Index(fields=["persona", "-fecha_inicio"]),
            models.Index(fields=["cama", "-fecha_inicio"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["persona"],
                condition=models.Q(fecha_fin__isnull=True),
                name="unique_ocupacion_activa_por_persona",
            ),
            models.UniqueConstraint(
                fields=["cama"],
                condition=models.Q(fecha_fin__isnull=True),
                name="unique_ocupacion_activa_por_cama",
            ),
        ]

    def __str__(self) -> str:
        estado = "vigente" if self.fecha_fin is None else "histórica"
        return f"{self.persona} → {self.cama} ({estado})"



"""Indicadores y memoria automatizada.

Definición de indicadores con cálculo basado en consulta materializable, y
mediciones periódicas almacenadas para reporting y memoria anual.
"""
import uuid

from django.db import models

from personas.models import Centro


class Indicador(models.Model):
    class Unidad(models.TextChoices):
        PORCENTAJE = "porcentaje", "Porcentaje"
        RATIO = "ratio", "Ratio"
        ABSOLUTO = "absoluto", "Absoluto"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=32, unique=True)
    nombre = models.CharField(max_length=128)
    descripcion = models.TextField(blank=True)
    unidad = models.CharField(max_length=16, choices=Unidad.choices, default=Unidad.ABSOLUTO)
    objetivo_valor = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Valor diana del indicador (ej. ocupación ≥ 92%).",
    )
    requiere_anonimizacion = models.BooleanField(
        default=True,
        help_text="Si True, el exporte externo se hace pseudonimizado.",
    )
    formula = models.CharField(
        max_length=255, blank=True,
        help_text="Referencia a la función de cálculo (ej. 'agora.indicadores.calc.ocupacion').",
    )
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Indicador"
        verbose_name_plural = "Indicadores"
        ordering = ["codigo"]

    def __str__(self) -> str:
        return f"{self.codigo} · {self.nombre}"


class MedicionIndicador(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    indicador = models.ForeignKey(
        Indicador, on_delete=models.CASCADE, related_name="mediciones",
    )
    periodo = models.DateField(help_text="Primer día del periodo medido (mensual/trimestral).")
    centro = models.ForeignKey(
        Centro, on_delete=models.PROTECT, null=True, blank=True,
        related_name="mediciones",
        help_text="Null = global del grupo.",
    )
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    calculado_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Medición de indicador"
        verbose_name_plural = "Mediciones de indicadores"
        ordering = ["-periodo", "indicador"]
        unique_together = [("indicador", "periodo", "centro")]
        indexes = [models.Index(fields=["indicador", "-periodo"])]

    def __str__(self) -> str:
        scope = self.centro.nombre if self.centro else "Grupo"
        return f"{self.indicador.codigo} · {self.periodo:%Y-%m} · {scope} · {self.valor}"


class SnapshotPlanesVida(models.Model):
    """Foto periódica de los KPIs de Planes de Vida (reproduce hoja 'Historico')."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fecha = models.DateField(unique=True, help_text="Fecha del snapshot.")
    etiqueta = models.CharField(
        max_length=128, blank=True,
        help_text="Etiqueta libre (p.ej. 'cierre trimestre 2026Q2').",
    )
    total_usuarios = models.PositiveIntegerField(default=0)
    usuarios_fab = models.PositiveIntegerField(default=0)
    usuarios_aspaniasmerc = models.PositiveIntegerField(default=0)
    pv_realizados = models.PositiveIntegerField(default=0)
    pv_pendientes = models.PositiveIntegerField(default=0)
    pv_revisados = models.PositiveIntegerField(default=0)
    pv_fuera_plazo = models.PositiveIntegerField(default=0)
    desglose_centros = models.JSONField(default=dict, blank=True)
    creado_por = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="snapshots_pv",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Snapshot Planes de Vida"
        verbose_name_plural = "Snapshots Planes de Vida"
        ordering = ["-fecha"]

    def __str__(self) -> str:
        return f"Snapshot {self.fecha:%Y-%m-%d} · {self.total_usuarios} usuarios · {self.pv_realizados} PV"

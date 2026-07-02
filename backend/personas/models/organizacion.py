"""Modelo de datos · módulo "organizacion" (split de models.py para legibilidad).

Referencia: docs/modelo-datos/modelo_v0_1.md
"""
import uuid

from django.conf import settings
from django.db import models

# ---------------------------------------------------------------------------
# Centros, servicios y profesionales (contexto organizativo)
# ---------------------------------------------------------------------------

class Centro(models.Model):
    """Centro físico del grupo (Fuentecillas, Salas, Villadiego, etc.)."""

    class Corresponsable(models.TextChoices):
        FUNDACION = "fundacion_aspanias_burgos", "Fundación Aspanias Burgos"
        ASPANIASMERC = "aspaniasmerc", "Aspaniasmerc 2016 S.L.U."

    codigo = models.CharField(max_length=16, unique=True)
    nombre = models.CharField(max_length=128)
    corresponsable = models.CharField(max_length=32, choices=Corresponsable.choices)
    municipio = models.CharField(max_length=64, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Centro"
        verbose_name_plural = "Centros"
        ordering = ["nombre"]

    def __str__(self) -> str:
        return f"{self.nombre} ({self.get_corresponsable_display()})"

    @property
    def plazas_totales(self) -> int:
        """Suma de camas activas en el centro."""
        from .alojamiento import Cama  # lazy: alojamiento depende de organizacion
        return Cama.objects.filter(
            habitacion__centro=self, activa=True, habitacion__activa=True,
        ).count()

    @property
    def plazas_ocupadas(self) -> int:
        """Camas con ocupación vigente."""
        from .alojamiento import OcupacionCama  # lazy
        return OcupacionCama.objects.filter(
            cama__habitacion__centro=self, fecha_fin__isnull=True,
        ).count()

    @property
    def plazas_libres(self) -> int:
        return self.plazas_totales - self.plazas_ocupadas

    @property
    def porcentaje_ocupacion(self) -> float:
        total = self.plazas_totales
        if total == 0:
            return 0.0
        return round(100.0 * self.plazas_ocupadas / total, 1)


class Servicio(models.Model):
    """Tipo de servicio: residencia, centro de día, vivienda, SAD, CEE, etc."""

    class Tipo(models.TextChoices):
        RESIDENCIA = "residencia", "Residencia"
        CENTRO_DIA = "centro_dia", "Centro de día"
        VIVIENDA = "vivienda", "Vivienda"
        OCUPACIONAL = "ocupacional", "Centro ocupacional"
        SAD = "sad", "Servicio de ayuda a domicilio"
        CEE = "cee", "Centro Especial de Empleo"
        EMPLEO_APOYO = "empleo_apoyo", "Empleo con apoyo"
        INSERCION = "insercion", "Empresa de inserción"
        ORIENTACION = "orientacion", "Orientación laboral"

    codigo = models.CharField(max_length=32, unique=True)
    nombre = models.CharField(max_length=128)
    tipo = models.CharField(max_length=32, choices=Tipo.choices)

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ["nombre"]

    def __str__(self) -> str:
        return self.nombre


class Rol(models.Model):
    """Rol funcional del profesional (TS, DUE, TO, etc.)."""

    codigo = models.CharField(max_length=32, unique=True)
    nombre = models.CharField(max_length=128)

    class Meta:
        verbose_name = "Rol profesional"
        verbose_name_plural = "Roles profesionales"
        ordering = ["nombre"]

    def __str__(self) -> str:
        return self.nombre


class Profesional(models.Model):
    """Profesional del grupo con acceso a ÁGORA.

    Federado por SSO M365. Se sincroniza con `auth.User`.
    Puede ejercer como Gestor/a de Caso y/o Persona de Referencia de personas atendidas.
    El protocolo de Planes de Vida limita a 30 casos asignados por gestor/a.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="profesional",
    )
    nombre_completo = models.CharField(max_length=255)
    rol_principal = models.ForeignKey(
        Rol, on_delete=models.PROTECT, related_name="profesionales", null=True, blank=True,
    )
    centros_acceso = models.ManyToManyField(Centro, related_name="profesionales", blank=True)
    email_m365 = models.EmailField(unique=True)
    activo = models.BooleanField(default=True)
    puede_ser_gestor_caso = models.BooleanField(
        default=False,
        help_text="Habilitado para asumir el rol de Gestor/a de Caso en Planes de Vida.",
    )
    max_casos_asignados = models.PositiveSmallIntegerField(
        default=30,
        help_text="Tope de casos como Gestor/a de Caso. Protocolo: 30 máximo.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profesional"
        verbose_name_plural = "Profesionales"
        ordering = ["nombre_completo"]

    def __str__(self) -> str:
        return self.nombre_completo

    @property
    def casos_actuales_gestor(self) -> int:
        """Nº de personas activas con este profesional como Gestor/a de Caso."""
        return self.personas_como_gestor.filter(fecha_baja__isnull=True).count()

    @property
    def sobrepasa_ratio(self) -> bool:
        return self.casos_actuales_gestor > self.max_casos_asignados


# ---------------------------------------------------------------------------
# Persona atendida y entorno
# ---------------------------------------------------------------------------



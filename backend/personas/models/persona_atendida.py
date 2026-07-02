"""Modelo de datos · módulo "persona_atendida" (split de models.py para legibilidad).

Referencia: docs/modelo-datos/modelo_v0_1.md
"""
import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.fields import EncryptedCharField

from .organizacion import Centro

# ---------------------------------------------------------------------------
# Centros, servicios y profesionales (contexto organizativo)
# ---------------------------------------------------------------------------

class PersonaAtendida(models.Model):
    """Ficha única — entidad central del sistema."""

    class Sexo(models.TextChoices):
        MASCULINO = "M", "Masculino"
        FEMENINO = "F", "Femenino"
        OTRO = "X", "Otro"
        NO_INFORMA = "N", "No informa"

    class MotivoBaja(models.TextChoices):
        TRASLADO = "traslado", "Traslado a otro centro"
        FALLECIMIENTO = "fallecimiento", "Fallecimiento"
        VOLUNTARIA = "voluntaria", "Baja voluntaria"
        FIN_PROGRAMA = "fin_programa", "Finalización del programa"
        OTROS = "otros", "Otros"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo_interno = models.CharField(max_length=32, unique=True, db_index=True)
    nombre = models.CharField(max_length=64)
    apellido_1 = models.CharField(max_length=64)
    apellido_2 = models.CharField(max_length=64, blank=True)
    # En producción: cifrado a nivel aplicación. v0.1 deja el hueco con max_length.
    dni_nie = models.CharField(max_length=16, blank=True, unique=False, db_index=True)
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=1, choices=Sexo.choices, default=Sexo.NO_INFORMA)
    nacionalidad = models.CharField(max_length=2, default="ES", help_text="ISO 3166 alpha-2")

    direccion_calle = models.CharField(max_length=255, blank=True)
    direccion_cp = models.CharField(max_length=10, blank=True)
    direccion_municipio = models.CharField(max_length=128, blank=True)
    direccion_provincia = models.CharField(max_length=128, blank=True)

    # --- Datos administrativos sanitarios — cifrado Fernet a nivel BD (Fase 2.5.1) ---
    numero_seguridad_social = EncryptedCharField(
        max_length=20, blank=True,
        verbose_name="Nº Seguridad Social (NUSS)",
        help_text="NUSS. Categoría especial RGPD — cifrado en BD con Fernet (AES-128).",
    )
    numero_tarjeta_sanitaria = EncryptedCharField(
        max_length=20, blank=True,
        verbose_name="Nº Tarjeta Sanitaria (TSI)",
        help_text="TSI. Categoría especial RGPD — cifrado en BD con Fernet.",
    )
    tsi_caducidad = models.DateField(
        null=True, blank=True,
        help_text="Fecha de caducidad de la TSI; alerta automática 90 días antes.",
    )
    centro_salud = models.CharField(
        max_length=128, blank=True,
        help_text="Centro de salud asignado en la sanidad pública (SACYL).",
    )

    # --- Comunicación e idioma ---
    class FormaComunicacion(models.TextChoices):
        TELEFONICA = "telefonica", "Telefónica"
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        PRESENCIAL = "presencial", "Presencial (vía persona de referencia)"
        CERCA = "cerca", "CERCA (app familias)"

    forma_comunicacion_preferente = models.CharField(
        max_length=16, choices=FormaComunicacion.choices, blank=True,
        help_text="Vía preferente para contactar a la persona o su entorno.",
    )
    idioma_preferente = models.CharField(
        max_length=8, default="es", help_text="ISO 639-1 (es, en, fr...).",
    )
    usa_saac = models.BooleanField(
        default=False, verbose_name="Usa Sistema Aumentativo/Alternativo de Comunicación",
        help_text="Pictogramas, lengua de signos, comunicadores, etc.",
    )
    saac_notas = models.CharField(max_length=255, blank=True)

    corresponsable_principal = models.CharField(
        max_length=32,
        choices=Centro.Corresponsable.choices,
        help_text="Corresponsable RGPD bajo el que se inscribe el tratamiento principal.",
    )
    centro_referencia = models.ForeignKey("personas.Centro", on_delete=models.PROTECT, related_name="personas",
    )

    fecha_alta = models.DateField(help_text="Primera entrada en cualquier servicio del grupo.")
    fecha_baja = models.DateField(null=True, blank=True)
    motivo_baja = models.CharField(max_length=16, choices=MotivoBaja.choices, blank=True)

    # Figuras profesionales del Protocolo de Planes de Vida
    gestor_caso = models.ForeignKey(
        "personas.Profesional",
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name="personas_como_gestor",
        verbose_name="Gestor/a de Caso",
        help_text="Coordina el Plan de Vida, garantiza participación y traspaso.",
    )
    persona_referencia = models.ForeignKey(
        "personas.Profesional",
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name="personas_como_referencia",
        verbose_name="Persona de Referencia",
        help_text="Genera vínculo significativo y aporta información cotidiana.",
    )

    notas_relevantes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Persona atendida"
        verbose_name_plural = "Personas atendidas"
        ordering = ["apellido_1", "apellido_2", "nombre"]
        indexes = [
            models.Index(fields=["centro_referencia", "fecha_baja"]),
            models.Index(fields=["corresponsable_principal"]),
        ]

    def __str__(self) -> str:
        return f"{self.apellido_1} {self.apellido_2}, {self.nombre} ({self.codigo_interno})"

    @property
    def activa(self) -> bool:
        return self.fecha_baja is None

    @property
    def ocupacion_cama_actual(self):
        """`OcupacionCama` vigente, o None si la persona no está en residencia/vivienda."""
        return (
            self.ocupaciones_cama
            .filter(fecha_fin__isnull=True)
            .select_related(
                "cama__habitacion__modulo",
                "cama__habitacion__centro",
            )
            .first()
        )

    @property
    def ubicacion_residencial(self) -> str:
        """Texto legible 'Módulo X · Habitación Y · Cama Z' o cadena vacía."""
        oc = self.ocupacion_cama_actual
        if not oc:
            return ""
        cama = oc.cama
        hab = cama.habitacion
        partes = []
        if hab.modulo:
            partes.append(f"Módulo {hab.modulo.nombre}")
        partes.append(f"Habitación {hab.numero}")
        partes.append(f"Cama {cama.identificador}")
        return " · ".join(partes)


# ---------------------------------------------------------------------------
# Perfiles por colectivo (ficha base extensible)
# ---------------------------------------------------------------------------


class PerfilDI(models.Model):
    """Perfil para personas con discapacidad intelectual."""

    class TipoDI(models.TextChoices):
        LEVE = "leve", "DI leve"
        MODERADA = "moderada", "DI moderada"
        SEVERA = "severa", "DI severa"
        PROFUNDA = "profunda", "DI profunda"
        NO_VALORADA = "no_valorada", "No valorada"

    persona = models.ForeignKey(
        PersonaAtendida, on_delete=models.CASCADE, related_name="perfiles_di",
    )
    tipo_discapacidad = models.CharField(max_length=16, choices=TipoDI.choices)
    grado_discapacidad_pct = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    fecha_reconocimiento = models.DateField(null=True, blank=True)
    inicio_at = models.DateField()
    fin_at = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Perfil — Discapacidad intelectual"
        verbose_name_plural = "Perfiles — Discapacidad intelectual"
        ordering = ["-inicio_at"]

    def __str__(self) -> str:
        return f"DI {self.get_tipo_discapacidad_display()} · {self.persona}"


class PerfilMayor(models.Model):
    """Perfil para mayores dependientes."""

    class GradoDependencia(models.TextChoices):
        I = "I", "Grado I — Moderada"  # noqa: E741 — nombre convencional Ley 39/2006
        II = "II", "Grado II — Severa"
        III = "III", "Grado III — Gran dependencia"
        NO_VALORADO = "no_valorado", "No valorado"

    persona = models.ForeignKey(
        PersonaAtendida, on_delete=models.CASCADE, related_name="perfiles_mayor",
    )
    grado_dependencia = models.CharField(max_length=16, choices=GradoDependencia.choices)
    fecha_valoracion_bvd = models.DateField(null=True, blank=True)
    inicio_at = models.DateField()
    fin_at = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Perfil — Mayores dependientes"
        verbose_name_plural = "Perfiles — Mayores dependientes"
        ordering = ["-inicio_at"]

    def __str__(self) -> str:
        return f"Dep. {self.get_grado_dependencia_display()} · {self.persona}"


class PerfilInsercion(models.Model):
    """Perfil para itinerarios de inserción laboral."""

    class Programa(models.TextChoices):
        CEE = "cee", "Centro Especial de Empleo"
        EMPLEO_APOYO = "empleo_apoyo", "Empleo con apoyo"
        INSERCION = "insercion", "Empresa de inserción"
        ORIENTACION = "orientacion", "Orientación laboral"

    class NivelApoyo(models.TextChoices):
        BAJO = "bajo", "Bajo"
        MEDIO = "medio", "Medio"
        ALTO = "alto", "Alto"

    persona = models.ForeignKey(
        PersonaAtendida, on_delete=models.CASCADE, related_name="perfiles_insercion",
    )
    programa = models.CharField(max_length=16, choices=Programa.choices)
    entidad_empleadora = models.CharField(max_length=128, blank=True)
    puesto_actual = models.CharField(max_length=128, blank=True)
    nivel_apoyo_requerido = models.CharField(max_length=8, choices=NivelApoyo.choices)
    inicio_at = models.DateField()
    fin_at = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Perfil — Inserción laboral"
        verbose_name_plural = "Perfiles — Inserción laboral"
        ordering = ["-inicio_at"]

    def __str__(self) -> str:
        return f"{self.get_programa_display()} · {self.persona}"


# ---------------------------------------------------------------------------
# Servicio contratado (relación persona <-> centro <-> servicio + período)
# ---------------------------------------------------------------------------


class ServicioContratado(models.Model):
    """Vínculo temporal entre persona y servicio en un centro concreto."""

    persona = models.ForeignKey(
        PersonaAtendida, on_delete=models.CASCADE, related_name="servicios_contratados",
    )
    centro = models.ForeignKey("personas.Centro", on_delete=models.PROTECT)
    servicio = models.ForeignKey("personas.Servicio", on_delete=models.PROTECT)
    corresponsable = models.CharField(max_length=32, choices=Centro.Corresponsable.choices)
    inicio_at = models.DateField()
    fin_at = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Servicio contratado"
        verbose_name_plural = "Servicios contratados"
        ordering = ["-inicio_at"]
        indexes = [models.Index(fields=["persona", "fin_at"])]

    def __str__(self) -> str:
        return f"{self.servicio} en {self.centro} · {self.persona}"


# ---------------------------------------------------------------------------
# Entorno familiar y contactos
# ---------------------------------------------------------------------------



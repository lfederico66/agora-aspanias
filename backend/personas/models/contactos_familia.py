"""Modelo de datos · módulo "contactos_familia" (split de models.py para legibilidad).

Referencia: docs/modelo-datos/modelo_v0_1.md
"""
import uuid

from django.db import models

# ---------------------------------------------------------------------------
# Centros, servicios y profesionales (contexto organizativo)
# ---------------------------------------------------------------------------

class PersonaContacto(models.Model):
    """Persona del entorno: familiar, representante legal, contacto, etc."""

    class Relacion(models.TextChoices):
        MADRE = "madre", "Madre"
        PADRE = "padre", "Padre"
        HERMANO = "hermano", "Hermano/a"
        HIJO = "hijo", "Hijo/a"
        CONYUGE = "conyuge", "Cónyuge/Pareja"
        TUTOR = "tutor", "Tutor legal"
        CURADOR = "curador", "Curador"
        APOYO_VOLUNTARIO = "apoyo_voluntario", "Figura de apoyo voluntario"
        AMISTAD = "amistad", "Amistad"
        PROFESIONAL_EXTERNO = "profesional_externo", "Profesional externo"
        OTRO = "otro", "Otro"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=64)
    apellido_1 = models.CharField(max_length=64)
    apellido_2 = models.CharField(max_length=64, blank=True)
    fecha_nacimiento = models.DateField(
        null=True, blank=True,
        help_text="Opcional. Permite calcular edad y filtrar familiares mayores/menores.",
    )
    telefono_fijo = models.CharField(
        max_length=20, blank=True,
        help_text="Teléfono fijo de contacto. Cifrado en producción.",
    )
    movil = models.CharField(
        max_length=20, blank=True,
        help_text="Teléfono móvil — vía preferente para CERCA y emergencias.",
    )
    # Campo legacy 'telefono' renombrado a telefono_fijo. Para compatibilidad temporal,
    # se conserva como alias en la migración de datos (handled in 0002_datafix).
    telefono = models.CharField(
        max_length=20, blank=True,
        help_text="DEPRECATED — usar telefono_fijo o movil. Se elimina en v1.0.",
    )
    email = models.EmailField(blank=True)

    # Dirección postal (puede coincidir con la persona atendida o ser distinta)
    direccion_calle = models.CharField(max_length=255, blank=True)
    direccion_cp = models.CharField(max_length=10, blank=True)
    direccion_municipio = models.CharField(max_length=128, blank=True)
    direccion_provincia = models.CharField(max_length=128, blank=True)

    consentimiento_comunicacion = models.BooleanField(
        default=False,
        help_text="Consentimiento explícito para recibir comunicaciones (RGPD art. 6.1.a).",
    )
    fecha_consentimiento = models.DateField(null=True, blank=True)
    notas = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Persona de contacto"
        verbose_name_plural = "Personas de contacto"
        ordering = ["apellido_1", "apellido_2", "nombre"]

    def __str__(self) -> str:
        return f"{self.apellido_1} {self.apellido_2}, {self.nombre}"

    @property
    def telefono_principal(self) -> str:
        """Móvil si está informado; si no, fijo; si no, el campo legacy."""
        return self.movil or self.telefono_fijo or self.telefono or ""


class VinculoPersonaContacto(models.Model):
    """Relación tipada entre una persona atendida y un contacto."""

    persona = models.ForeignKey("personas.PersonaAtendida", on_delete=models.CASCADE, related_name="vinculos_contacto",
    )
    contacto = models.ForeignKey(
        PersonaContacto, on_delete=models.CASCADE, related_name="vinculos_persona",
    )
    relacion = models.CharField(max_length=32, choices=PersonaContacto.Relacion.choices)
    es_referencia_principal = models.BooleanField(
        default=False,
        help_text="Familiar principal — primero a contactar para temas no urgentes.",
    )
    es_emergencia = models.BooleanField(
        default=False,
        help_text="Persona de contacto en caso de emergencia 24h.",
    )
    orden_emergencia = models.PositiveSmallIntegerField(
        default=0,
        help_text="Orden de llamada en emergencias (0 = no aplica, 1 = primero, 2 = segundo...).",
    )
    notificable_cerca = models.BooleanField(
        default=False,
        help_text="Recibe notificaciones de la app CERCA (citas, intervenciones notificables).",
    )
    fecha_alta_cerca = models.DateField(
        null=True, blank=True,
        help_text="Fecha en que aceptó las notificaciones CERCA (consentimiento auditable).",
    )
    notas = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Vínculo persona-contacto"
        verbose_name_plural = "Vínculos persona-contacto"
        unique_together = [("persona", "contacto", "relacion")]

    def __str__(self) -> str:
        return f"{self.contacto} · {self.get_relacion_display()} de {self.persona}"


class NucleoFamiliar(models.Model):
    """Núcleo familiar como sujeto de seguimiento (no solo contacto)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre_referencia = models.CharField(max_length=128, help_text="Ej.: 'Familia García López'")
    persona_referencia = models.ForeignKey(
        PersonaContacto,
        on_delete=models.PROTECT,
        related_name="nucleos_referenciados",
        help_text="Cuidador principal o portavoz.",
    )
    personas_atendidas = models.ManyToManyField("personas.PersonaAtendida", related_name="nucleos_familiares", blank=True,
    )
    notas = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Núcleo familiar"
        verbose_name_plural = "Núcleos familiares"
        ordering = ["nombre_referencia"]

    def __str__(self) -> str:
        return self.nombre_referencia


# ---------------------------------------------------------------------------
# Ley 8/2021 — medidas de apoyo a la capacidad jurídica
# ---------------------------------------------------------------------------



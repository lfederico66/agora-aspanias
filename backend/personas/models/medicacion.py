"""Modelo de datos · módulo "medicacion" (split de models.py para legibilidad).

Referencia: docs/modelo-datos/modelo_v0_1.md
"""
import uuid

from django.conf import settings
from django.db import models

# ---------------------------------------------------------------------------
# Centros, servicios y profesionales (contexto organizativo)
# ---------------------------------------------------------------------------

class Medicamento(models.Model):
    """Catálogo de medicamentos. Compartido entre personas atendidas."""

    class Familia(models.TextChoices):
        OTRO = "otro", "Otro"
        ANALGESICO = "analgesico", "Analgésico"
        AINE = "aine", "AINE"
        ANTIBIOTICO = "antibiotico", "Antibiótico"
        ANTIDEPRESIVO = "antidepresivo", "Antidepresivo / ISRS"
        ANSIOLITICO = "ansiolitico", "Ansiolítico / benzodiacepina"
        ANTIPSICOTICO = "antipsicotico", "Antipsicótico"
        ANTIEPILEPTICO = "antiepileptico", "Antiepiléptico"
        ANTIHIPERTENSIVO = "antihipertensivo", "Antihipertensivo / IECA / ARA-II"
        DIURETICO = "diuretico", "Diurético"
        ANTICOAGULANTE = "anticoagulante", "Anticoagulante"
        ANTIARRITMICO = "antiarritmico", "Antiarrítmico"
        HIPOLIPEMIANTE = "hipolipemiante", "Hipolipemiante"
        ANTIDIABETICO = "antidiabetico", "Antidiabético oral / insulina"
        HORMONA_TIROIDEA = "hormona_tiroidea", "Hormona tiroidea"
        VITAMINA = "vitamina", "Vitamina / suplemento"
        LAXANTE = "laxante", "Laxante"
        PROTECTOR_GASTRICO = "protector_gastrico", "Protector gástrico / IBP"
        OFTALMOLOGICO = "oftalmologico", "Oftalmológico tópico"
        DERMATOLOGICO = "dermatologico", "Dermatológico tópico"

    class ViaAdministracion(models.TextChoices):
        ORAL = "oral", "Oral"
        SUBLINGUAL = "sublingual", "Sublingual"
        TOPICA = "topica", "Tópica"
        OFTALMICA = "oftalmica", "Oftálmica"
        OTICA = "otica", "Ótica"
        NASAL = "nasal", "Nasal"
        INHALADA = "inhalada", "Inhalada"
        SUBCUTANEA = "subcutanea", "Subcutánea"
        INTRAMUSCULAR = "intramuscular", "Intramuscular"
        INTRAVENOSA = "intravenosa", "Intravenosa"
        RECTAL = "rectal", "Rectal"
        VAGINAL = "vaginal", "Vaginal"

    nombre_comercial = models.CharField(max_length=128, db_index=True)
    principio_activo = models.CharField(max_length=128, blank=True, db_index=True)
    dosis = models.CharField(
        max_length=64,
        help_text="Dosis del envase (p. ej. '10 mg', '500 mg/5 ml', 'ampolla').",
    )
    familia = models.CharField(max_length=24, choices=Familia.choices, default=Familia.OTRO)
    via_administracion = models.CharField(
        max_length=16, choices=ViaAdministracion.choices, default=ViaAdministracion.ORAL,
    )
    activo = models.BooleanField(default=True, help_text="Si está disponible en el catálogo.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Medicamento (catálogo)"
        verbose_name_plural = "Medicamentos (catálogo)"
        ordering = ["nombre_comercial"]
        unique_together = [("nombre_comercial", "dosis")]

    def __str__(self) -> str:
        return f"{self.nombre_comercial} {self.dosis}"


class PautaMedicacion(models.Model):
    """Pauta de un medicamento prescrito a una persona en un período.

    Una persona puede tener varias pautas activas simultáneamente.
    El histórico se mantiene marcando `fecha_fin` y `activa=False`.
    El registro de cada toma individual NO va aquí: ese trazado lo
    gestiona el módulo Enfermería (M2 Fase 3).
    """

    class MotivoFinalizacion(models.TextChoices):
        FIN_TRATAMIENTO = "fin_tratamiento", "Fin del tratamiento"
        CAMBIO_PRINCIPIO = "cambio_principio", "Cambio a otro principio activo"
        REACCION_ADVERSA = "reaccion_adversa", "Reacción adversa"
        INEFICAZ = "ineficaz", "Ineficaz"
        DECISION_FAMILIAR = "decision_familiar", "Decisión familiar / persona"
        PROBLEMA_SALUD_RESUELTO = "problema_salud_resuelto", "Problema de salud resuelto"
        OTRO = "otro", "Otro"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    persona = models.ForeignKey("personas.PersonaAtendida", on_delete=models.CASCADE, related_name="pautas_medicacion",
    )
    medicamento = models.ForeignKey(
        Medicamento, on_delete=models.PROTECT, related_name="pautas",
    )

    # Dosificación D-C-N (desayuno · comida · cena). Permite fracciones (1/2, 1/4) por texto.
    dosis_desayuno = models.CharField(max_length=8, blank=True, help_text="P. ej. '1', '½', '0'.")
    dosis_comida = models.CharField(max_length=8, blank=True)
    dosis_cena = models.CharField(max_length=8, blank=True)
    dosis_acostarse = models.CharField(max_length=8, blank=True)
    dosis_si_precisa = models.BooleanField(default=False)
    pauta_especial = models.CharField(
        max_length=255, blank=True,
        help_text="Pautas no encajables en D-C-N (p. ej. 'el día 1 de cada mes').",
    )

    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    motivo_finalizacion = models.CharField(
        max_length=32, choices=MotivoFinalizacion.choices, blank=True,
    )

    prescriptor = models.CharField(
        max_length=128, blank=True,
        help_text="Médico/a o servicio que prescribe (MAP, Psiquiatría, etc.).",
    )
    problema_salud = models.ForeignKey("personas.ProblemaSalud", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="pautas_medicacion",
        help_text="Problema de salud que justifica la prescripción (opcional).",
    )
    activa = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="pautas_medicacion_creadas",
    )

    class Meta:
        verbose_name = "Pauta de medicación"
        verbose_name_plural = "Pautas de medicación"
        ordering = ["-fecha_inicio"]
        indexes = [
            models.Index(fields=["persona", "activa"]),
            models.Index(fields=["persona", "-fecha_inicio"]),
        ]

    def __str__(self) -> str:
        estado = "activa" if self.activa else "histórica"
        return f"{self.medicamento} → {self.persona} ({estado})"

    @property
    def dosificacion_texto(self) -> str:
        """Devuelve la dosificación en formato D-C-N legible."""
        partes = [
            self.dosis_desayuno or "0",
            self.dosis_comida or "0",
            self.dosis_cena or "0",
        ]
        base = "-".join(partes)
        if self.dosis_acostarse:
            base += f"-{self.dosis_acostarse}"
        if self.dosis_si_precisa:
            base += " (si precisa)"
        return base


# ---------------------------------------------------------------------------
# Alojamiento físico — Centro → Módulo → Habitación → Cama
# ---------------------------------------------------------------------------
#
# Solo aplica a servicios de tipo residencia y vivienda. Los centros de día,
# centros ocupacionales o CEE no usan esta jerarquía.
#
# Jerarquía:
#   - Modulo: agrupación dentro del centro (planta, unidad de convivencia,
#     ala). Opcional para viviendas pequeñas.
#   - Habitacion: con número, tipo (individual/doble/triple), m², baño propio.
#   - Cama: identificador A/B/1/2 dentro de la habitación.
#
# Ocupación: una persona puede cambiar de cama varias veces a lo largo del
# tiempo. OcupacionCama mantiene el histórico; solo una activa por persona
# y por cama simultáneamente (constraints).
# ---------------------------------------------------------------------------



"""Modelo de datos · módulo "clinico" (split de models.py para legibilidad).

Referencia: docs/modelo-datos/modelo_v0_1.md
"""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# ---------------------------------------------------------------------------
# Centros, servicios y profesionales (contexto organizativo)
# ---------------------------------------------------------------------------

class InformacionMedica(models.Model):
    """Datos clínicos estructurales (1-1 con PersonaAtendida).

    Solo profesionales con rol sanitario pueden ver/editar.
    """

    class GrupoSanguineo(models.TextChoices):
        DESCONOCIDO = "desconocido", "Desconocido / sin informar"
        A_POS = "A+", "A+"
        A_NEG = "A-", "A-"
        B_POS = "B+", "B+"
        B_NEG = "B-", "B-"
        AB_POS = "AB+", "AB+"
        AB_NEG = "AB-", "AB-"
        O_POS = "O+", "O+"
        O_NEG = "O-", "O-"

    persona = models.OneToOneField("personas.PersonaAtendida", on_delete=models.CASCADE, related_name="info_medica",
    )
    grupo_sanguineo = models.CharField(
        max_length=12, choices=GrupoSanguineo.choices,
        default=GrupoSanguineo.DESCONOCIDO,
    )
    vacunacion_permitida = models.BooleanField(
        default=True,
        help_text="Si NO, requiere explicación en notas (objeción, contraindicación).",
    )
    motivo_no_vacunacion = models.CharField(max_length=255, blank=True)
    contacto_medico_referencia = models.CharField(
        max_length=255, blank=True,
        help_text="Médico/a de referencia externo (HUBU, MAP, especialista).",
    )
    antecedentes_familiares = models.TextField(
        blank=True,
        help_text="Antecedentes médicos relevantes en la familia.",
    )

    # Dieta y alimentación
    tipo_dieta = models.CharField(
        max_length=128, blank=True,
        help_text="P. ej. 'Basal 1.800 kcal · baja en sal'.",
    )
    textura_alimentos = models.CharField(max_length=64, blank=True, default="Normal")
    textura_liquidos = models.CharField(max_length=64, blank=True, default="Normal")
    observaciones_alimentacion = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="info_medica_actualizadas",
    )

    class Meta:
        verbose_name = "Información médica"
        verbose_name_plural = "Información médica"

    def __str__(self) -> str:
        return f"Información médica · {self.persona}"


class Alergia(models.Model):
    """Alergia o intolerancia. Visible siempre que se abra la ficha."""

    class Tipo(models.TextChoices):
        MEDICAMENTOSA = "medicamentosa", "Medicamentosa"
        ALIMENTARIA = "alimentaria", "Alimentaria"
        AMBIENTAL = "ambiental", "Ambiental"
        CONTACTO = "contacto", "Por contacto"
        INTOLERANCIA = "intolerancia", "Intolerancia"
        OTRA = "otra", "Otra"

    class Gravedad(models.TextChoices):
        LEVE = "leve", "Leve"
        MODERADA = "moderada", "Moderada"
        GRAVE = "grave", "Grave"
        ANAFILACTICA = "anafilactica", "Anafiláctica"

    persona = models.ForeignKey("personas.PersonaAtendida", on_delete=models.CASCADE, related_name="alergias",
    )
    tipo = models.CharField(max_length=16, choices=Tipo.choices)
    sustancia = models.CharField(
        max_length=255,
        help_text="Sustancia o grupo (p. ej. 'AINEs grupo OXICAMS', 'frutos secos').",
    )
    reaccion = models.CharField(max_length=255, blank=True)
    gravedad = models.CharField(max_length=16, choices=Gravedad.choices, default=Gravedad.LEVE)
    fecha_diagnostico = models.DateField(null=True, blank=True)
    activa = models.BooleanField(default=True)
    notas = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Alergia / intolerancia"
        verbose_name_plural = "Alergias e intolerancias"
        ordering = ["-gravedad", "sustancia"]
        indexes = [models.Index(fields=["persona", "activa"])]

    def __str__(self) -> str:
        return f"{self.sustancia} ({self.get_gravedad_display()}) · {self.persona}"


class EnfermedadCronica(models.Model):
    """Patología crónica diagnosticada."""

    persona = models.ForeignKey("personas.PersonaAtendida", on_delete=models.CASCADE, related_name="enfermedades_cronicas",
    )
    nombre = models.CharField(max_length=255)
    fecha_diagnostico = models.DateField(null=True, blank=True)
    especialista_referente = models.CharField(max_length=255, blank=True)
    en_seguimiento = models.BooleanField(
        default=True,
        help_text="Marcar a False si se considera resuelta o estable sin seguimiento.",
    )
    notas = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Enfermedad crónica"
        verbose_name_plural = "Enfermedades crónicas"
        ordering = ["nombre"]

    def __str__(self) -> str:
        return f"{self.nombre} · {self.persona}"


class MedidaAntropometrica(models.Model):
    """Registro periódico de peso, talla, TA, pulso, temperatura."""

    persona = models.ForeignKey("personas.PersonaAtendida", on_delete=models.CASCADE, related_name="medidas_antropometricas",
    )
    fecha = models.DateField()
    peso_kg = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Peso en kilogramos.",
    )
    talla_cm = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="Talla en centímetros.",
    )
    imc = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True,
        help_text="Calculado automáticamente al guardar si peso y talla informados.",
    )
    tension_sistolica = models.PositiveSmallIntegerField(null=True, blank=True)
    tension_diastolica = models.PositiveSmallIntegerField(null=True, blank=True)
    pulso = models.PositiveSmallIntegerField(null=True, blank=True)
    temperatura = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True,
        help_text="Temperatura en grados Celsius.",
    )
    saturacion_o2 = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Saturación de O2 en %.",
    )
    glucemia = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="Glucemia capilar en mg/dl.",
    )
    notas = models.TextField(blank=True)
    registrado_por = models.ForeignKey("personas.Profesional", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="medidas_antropometricas_registradas",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Medida antropométrica"
        verbose_name_plural = "Medidas antropométricas"
        ordering = ["-fecha"]
        indexes = [models.Index(fields=["persona", "-fecha"])]

    def __str__(self) -> str:
        return f"{self.persona} · {self.fecha}"

    def save(self, *args, **kwargs):
        """Cálculo automático del IMC si peso y talla están informados."""
        if self.peso_kg and self.talla_cm:
            talla_m = float(self.talla_cm) / 100.0
            if talla_m > 0:
                self.imc = round(float(self.peso_kg) / (talla_m ** 2), 1)
        super().save(*args, **kwargs)


class Vacuna(models.Model):
    """Registro de una dosis administrada."""

    persona = models.ForeignKey("personas.PersonaAtendida", on_delete=models.CASCADE, related_name="vacunas",
    )
    vacuna = models.CharField(max_length=128, help_text="Nombre de la vacuna o pauta.")
    fecha = models.DateField()
    dosis = models.CharField(
        max_length=64, blank=True,
        help_text="P. ej. '1ª dosis', 'Refuerzo', 'Dosis única'.",
    )
    estacional = models.BooleanField(
        default=False, help_text="Marcar para gripe, COVID estacional, etc.",
    )
    lote = models.CharField(max_length=64, blank=True)
    centro_administracion = models.CharField(max_length=128, blank=True)
    notas = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Vacuna administrada"
        verbose_name_plural = "Vacunación"
        ordering = ["-fecha"]
        indexes = [models.Index(fields=["persona", "-fecha"])]

    def __str__(self) -> str:
        return f"{self.vacuna} · {self.fecha} · {self.persona}"


class CuidadoEnfermeria(models.Model):
    """Plan de cuidados estructurado por dimensiones (1-1 con PersonaAtendida).

    Documento vivo: se actualiza cuando cambian las necesidades.
    Histórico mediante auditoría (django-simple-history en v1.0).
    """

    persona = models.OneToOneField("personas.PersonaAtendida", on_delete=models.CASCADE, related_name="cuidados_enfermeria",
    )
    respiracion = models.TextField(blank=True, help_text="Oxigenoterapia, CPAP, observaciones.")
    audicion = models.TextField(blank=True, help_text="Audífonos, alteraciones, comunicación.")
    vision = models.TextField(blank=True, help_text="Gafas, ceguera parcial/total, ayudas.")
    alimentacion = models.TextField(blank=True, help_text="Autonomía, prótesis, ayudas técnicas.")
    sueno_descanso = models.TextField(blank=True, help_text="Horarios, alteraciones, medicación.")
    eliminacion = models.TextField(blank=True, help_text="Continencia, absorbente, sonda.")
    movilidad = models.TextField(blank=True, help_text="Marcha, silla de ruedas, transferencias.")
    autonomia_abvd = models.TextField(
        blank=True, verbose_name="Autonomía ABVD",
        help_text="Actividades básicas de la vida diaria: aseo, vestido, comer.",
    )
    conducta = models.TextField(blank=True, help_text="Patrones, alteraciones, manejo.")
    cuidados_piel = models.TextField(blank=True, help_text="Hidratación, lesiones, prevención UPP.")
    observaciones = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="cuidados_enfermeria_actualizados",
    )

    class Meta:
        verbose_name = "Cuidados de enfermería"
        verbose_name_plural = "Cuidados de enfermería"

    def __str__(self) -> str:
        return f"Cuidados de enfermería · {self.persona}"


class ProblemaSalud(models.Model):
    """Problema de salud puntual o recurrente bajo seguimiento."""

    class Estado(models.TextChoices):
        ABIERTO = "abierto", "Abierto"
        EN_SEGUIMIENTO = "en_seguimiento", "En seguimiento"
        RESUELTO = "resuelto", "Resuelto"
        DERIVADO = "derivado", "Derivado a especialista"

    persona = models.ForeignKey("personas.PersonaAtendida", on_delete=models.CASCADE, related_name="problemas_salud",
    )
    fecha_apertura = models.DateField()
    descripcion = models.CharField(max_length=255)
    tipo = models.CharField(
        max_length=64, blank=True,
        help_text="Especialidad médica (Cardiología, Salud mental, etc.).",
    )
    especialista = models.CharField(
        max_length=255, blank=True,
        help_text="Profesional externo que lleva el caso.",
    )
    responsable_interno = models.ForeignKey("personas.Profesional", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="problemas_salud_responsable",
        help_text="Profesional de ÁGORA que coordina el seguimiento.",
    )
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.ABIERTO)
    fecha_cierre = models.DateField(null=True, blank=True)
    motivo_cierre = models.CharField(max_length=255, blank=True)
    observaciones = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Problema de salud"
        verbose_name_plural = "Problemas de salud"
        ordering = ["-fecha_apertura"]
        indexes = [models.Index(fields=["persona", "estado"])]

    def __str__(self) -> str:
        return f"{self.descripcion} ({self.get_estado_display()}) · {self.persona}"


# ---------------------------------------------------------------------------
# Medicación — catálogo + pautas
# ---------------------------------------------------------------------------



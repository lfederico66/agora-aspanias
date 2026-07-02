"""Intervenciones y valoraciones.

Una intervención es cualquier actuación profesional documentada sobre una
persona atendida: consulta, sesión, entrevista familiar, evaluación, etc.
"""
import uuid

from django.db import models

from personas.models import PersonaAtendida, Profesional


class TipoIntervencion(models.Model):
    codigo = models.CharField(max_length=32, unique=True)
    nombre = models.CharField(max_length=128)
    descripcion = models.TextField(blank=True)
    color = models.CharField(
        max_length=16, default="slate",
        help_text="Tailwind color name para distinción visual.",
    )

    class Meta:
        verbose_name = "Tipo de intervención"
        verbose_name_plural = "Tipos de intervención"
        ordering = ["nombre"]

    def __str__(self) -> str:
        return self.nombre


class Intervencion(models.Model):
    class Confidencialidad(models.TextChoices):
        NORMAL = "normal", "Normal"
        RESTRINGIDA_CLINICA = "rest_clinica", "Restringida clínica"
        RESTRINGIDA_JURIDICA = "rest_juridica", "Restringida jurídica"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    persona = models.ForeignKey(
        PersonaAtendida, on_delete=models.CASCADE, related_name="intervenciones",
    )
    profesional = models.ForeignKey(
        Profesional, on_delete=models.PROTECT, related_name="intervenciones",
    )
    tipo = models.ForeignKey(
        TipoIntervencion, on_delete=models.PROTECT, related_name="intervenciones",
    )
    fecha_hora = models.DateTimeField(db_index=True)
    descripcion = models.TextField()
    objetivo_vinculado = models.ForeignKey(
        "pia.Objetivo",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="intervenciones",
    )
    confidencialidad = models.CharField(
        max_length=16, choices=Confidencialidad.choices, default=Confidencialidad.NORMAL,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Intervención"
        verbose_name_plural = "Intervenciones"
        ordering = ["-fecha_hora"]
        indexes = [models.Index(fields=["persona", "-fecha_hora"])]

    def __str__(self) -> str:
        return f"{self.fecha_hora:%Y-%m-%d %H:%M} · {self.tipo} · {self.persona}"


class Valoracion(models.Model):
    """Aplicación de una escala / prueba / instrumento de valoración a una persona.

    Categorización propuesta por Gerencia (jun 2026) — ver:
    docs/modelo-datos/decisiones/06_valoraciones_psicologicas.md
    """

    class Categoria(models.TextChoices):
        ADAPTATIVA = "adaptativa", "Escalas adaptativas"
        CALIDAD_VIDA = "calidad_vida", "Calidad de vida"
        INTELIGENCIA = "inteligencia", "Inteligencia"
        CONDUCTA = "conducta", "Conducta"
        PERSONALIDAD = "personalidad", "Personalidad"
        DETERIORO = "deterioro_cognitivo", "Deterioro cognitivo"
        SCREENING_TM = "screening_tm", "Screening trastornos mentales"
        DEPENDENCIA = "dependencia", "Dependencia / autonomía"

    class Instrumento(models.TextChoices):
        # Adaptativas
        ICAP = "icap", "ICAP — Inventario para la planificación"
        ABS_RC2 = "abs_rc2", "ABS-RC:2 — Conducta adaptativa residencial"
        # Calidad de vida
        SAN_MARTIN = "san_martin", "Escala San Martín"
        FUMAT = "fumat", "Escala FUMAT"
        INICO_FEAPS = "inico_feaps", "Escala INICO-FEAPS"
        # Inteligencia
        KBIT = "kbit", "K-BIT"
        RAVEN = "raven", "Matrices Progresivas de Raven"
        WISC_4 = "wisc_4", "WISC-4"
        # Conducta
        BBTA = "bbta", "BBTA"
        # Personalidad / Screening TM
        DSAH_II = "dsah_ii", "DSAH II"
        # Deterioro cognitivo
        CAMDEX_DS = "camdex_ds", "Camdex DS"
        MEC = "mec", "MEC — Mini-Examen Cognoscitivo"
        TEST_BARCELONA = "test_barcelona", "Test Barcelona"
        # Dependencia / autonomía (preexistentes)
        BVD = "bvd", "Baremo de Valoración de Dependencia (BVD)"
        SIS = "sis", "Supports Intensity Scale (SIS)"
        BARTHEL = "barthel", "Índice de Barthel"
        TINETTI = "tinetti", "Escala de Tinetti"
        MMSE = "mmse", "Mini-Mental (MMSE)"
        OTRO = "otro", "Otro"

    class Estado(models.TextChoices):
        BORRADOR = "borrador", "Borrador"
        COMPLETADA = "completada", "Completada"
        FIRMADA = "firmada", "Firmada"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    persona = models.ForeignKey(
        PersonaAtendida, on_delete=models.CASCADE, related_name="valoraciones",
    )

    categoria = models.CharField(
        max_length=24, choices=Categoria.choices,
        default=Categoria.DEPENDENCIA,
        help_text="Categorización clínica del instrumento (jun 2026).",
    )
    instrumento = models.CharField(max_length=20, choices=Instrumento.choices)
    fecha = models.DateField()

    # Datos polimórficos del instrumento (cada escala tiene su schema)
    respuestas = models.JSONField(
        default=dict, blank=True,
        help_text="Ítems del cuestionario completados. Schema según instrumento.",
    )
    puntuacion = models.JSONField(
        default=dict, blank=True,
        help_text="Puntuaciones brutas, percentiles, niveles. Schema según instrumento.",
    )
    conclusiones = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)

    aplicado_por = models.ForeignKey(
        Profesional, on_delete=models.PROTECT, related_name="valoraciones",
    )
    estado = models.CharField(
        max_length=12, choices=Estado.choices,
        default=Estado.BORRADOR,
    )
    firmada_por = models.ForeignKey(
        Profesional, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="valoraciones_firmadas",
    )
    fecha_firma = models.DateField(null=True, blank=True)
    pdf_generado = models.FileField(
        upload_to="valoraciones/%Y/%m/",
        null=True, blank=True,
        help_text="PDF A4 institucional ÁGORA generado tras la firma.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Valoración"
        verbose_name_plural = "Valoraciones"
        ordering = ["-fecha"]

    def __str__(self) -> str:
        return f"{self.get_instrumento_display()} · {self.fecha} · {self.persona}"

    @property
    def esta_firmada(self) -> bool:
        return self.estado == self.Estado.FIRMADA


class InformePsicologico(models.Model):
    """Informe psicológico clínico — Inicial o Evolutivo.

    Estructura basada en plantillas reales del área de Psicología (jun 2026).
    """

    class Tipo(models.TextChoices):
        INICIAL = "inicial", "Inicial"
        EVOLUTIVO = "evolutivo", "Evolutivo"

    class Estado(models.TextChoices):
        BORRADOR = "borrador", "Borrador"
        COMPLETADO = "completado", "Completado"
        FIRMADO = "firmado", "Firmado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    persona = models.ForeignKey(
        PersonaAtendida, on_delete=models.CASCADE, related_name="informes_psicologicos",
    )
    tipo = models.CharField(max_length=12, choices=Tipo.choices)
    fecha = models.DateField()

    # Estructura clínica polimórfica
    # Inicial: antecedentes, autonomía, conducta, caracterología, exploración psicopatológica, ubicación
    # Evolutivo: cambios en funciones cognitivas + conducta + emocional + dependencia + ICAP
    contenido = models.JSONField(
        default=dict, blank=True,
        help_text="Secciones del informe. Schema según tipo (inicial / evolutivo).",
    )

    profesional = models.ForeignKey(
        Profesional, on_delete=models.PROTECT, related_name="informes_psicologicos",
    )
    numero_colegiado = models.CharField(max_length=32, blank=True)

    estado = models.CharField(
        max_length=12, choices=Estado.choices,
        default=Estado.BORRADOR,
    )
    fecha_firma = models.DateField(null=True, blank=True)
    pdf_generado = models.FileField(
        upload_to="informes_psicologicos/%Y/%m/",
        null=True, blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Informe psicológico"
        verbose_name_plural = "Informes psicológicos"
        ordering = ["-fecha"]

    def __str__(self) -> str:
        return f"{self.get_tipo_display()} · {self.fecha} · {self.persona}"

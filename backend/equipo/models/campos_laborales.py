"""Campos laborales del Profesional (extensión 1-1 desde personas.Profesional).

Datos operativos asistenciales · jornada, horario, contrato.
Los datos maestros (alta, baja, salario, contrato real) son fuente de verdad
de EQUIPO (suite RRHH del grupo) cuando exista. Ver:
    docs/modelo-datos/decisiones/05_modulo_equipo_solapamiento.md
"""
import uuid

from django.db import models

from core.fields import EncryptedCharField


class CamposLaboralesProfesional(models.Model):
    """Atributos laborales asistenciales del profesional.

    Relación 1-1 con `personas.Profesional`. No duplica datos maestros que
    son responsabilidad de EQUIPO (contrato real, salario, antigüedad).
    """

    class TipoJornada(models.TextChoices):
        COMPLETA = "completa", "Completa"
        PARCIAL = "parcial", "Parcial"
        FIN_DE_SEMANA = "fin_de_semana", "Fin de semana"
        RELEVO = "relevo", "Relevo"

    class Horario(models.TextChoices):
        LV_MANANA = "lv_manana", "L-V mañana"
        LV_TARDE = "lv_tarde", "L-V tarde"
        ROTATIVO = "rotativo", "Rotativo M/T/N"
        NOCTURNO_FIJO = "nocturno_fijo", "Nocturno fijo"
        VEINTICUATRO = "veinticuatro", "24 horas (vivienda tutelada)"
        ANTI_ESTRES = "anti_estres", "Antiestrés CD"

    class TipoContrato(models.TextChoices):
        INDEFINIDO = "indefinido", "Indefinido"
        TEMPORAL = "temporal", "Temporal"
        OBRA_SERVICIO = "obra_servicio", "Obra y servicio"
        BOLSA = "bolsa", "Bolsa de refuerzo"
        FORMACION = "formacion", "Formación"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    profesional = models.OneToOneField(
        "personas.Profesional",
        on_delete=models.CASCADE,
        related_name="laboral",
        help_text="Profesional al que pertenecen estos datos laborales.",
    )

    # Datos administrativos mínimos (lo demás es EQUIPO)
    dni_cifrado = EncryptedCharField(max_length=64, blank=True)
    telefono_interno = models.CharField(max_length=16, blank=True)

    # Adscripción asistencial
    centro_principal = models.ForeignKey(
        "personas.Centro",
        on_delete=models.PROTECT,
        related_name="profesionales_principal",
        null=True, blank=True,
        help_text="Centro donde el profesional desarrolla la mayoría de su jornada.",
    )

    # Jornada
    tipo_jornada = models.CharField(
        max_length=16, choices=TipoJornada.choices,
        default=TipoJornada.COMPLETA,
    )
    horario_habitual = models.CharField(
        max_length=16, choices=Horario.choices,
        default=Horario.LV_MANANA,
    )

    # Contrato (solo etiqueta operativa; el contrato real está en EQUIPO)
    tipo_contrato = models.CharField(
        max_length=20, choices=TipoContrato.choices,
        default=TipoContrato.INDEFINIDO,
    )
    fecha_alta = models.DateField(null=True, blank=True)
    fecha_baja_grupo = models.DateField(
        null=True, blank=True,
        help_text="Si no es null, el profesional ya no trabaja en el grupo.",
    )

    # Procedencia / sincronización
    origen = models.CharField(
        max_length=16,
        choices=[("manual", "Manual"), ("equipo", "Sinc. EQUIPO"), ("sigper", "Sinc. SIGPER")],
        default="manual",
        help_text="Origen del registro. En Fase 5 vendrá de EQUIPO vía API.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Datos laborales del profesional"
        verbose_name_plural = "Datos laborales de profesionales"

    def __str__(self) -> str:
        return f"Datos laborales · {self.profesional.nombre_completo}"

    @property
    def en_activo(self) -> bool:
        return self.fecha_baja_grupo is None

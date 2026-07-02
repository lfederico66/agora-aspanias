"""Agenda multiprofesional.

Citas con una o varias personas atendidas y uno o varios profesionales.
"""
import uuid

from django.db import models

from personas.models import PersonaAtendida, Profesional


class Cita(models.Model):
    class Tipo(models.TextChoices):
        INDIVIDUAL = "individual", "Individual"
        FAMILIAR = "familiar", "Familiar"
        MULTIPRO = "multipro", "Multiprofesional"
        EXTERNA = "externa", "Externa (recurso externo)"

    class Estado(models.TextChoices):
        PROPUESTA = "propuesta", "Propuesta"
        CONFIRMADA = "confirmada", "Confirmada"
        REALIZADA = "realizada", "Realizada"
        CANCELADA = "cancelada", "Cancelada"
        NO_ASISTE = "no_asiste", "No asiste"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    persona = models.ForeignKey(
        PersonaAtendida, on_delete=models.CASCADE, related_name="citas",
    )
    profesionales = models.ManyToManyField(
        Profesional, related_name="citas", blank=True,
    )
    tipo = models.CharField(max_length=16, choices=Tipo.choices, default=Tipo.INDIVIDUAL)
    inicio = models.DateTimeField(db_index=True)
    fin = models.DateTimeField()
    ubicacion = models.CharField(max_length=255, blank=True)
    estado = models.CharField(max_length=16, choices=Estado.choices, default=Estado.PROPUESTA)
    notas = models.TextField(blank=True)
    notificada_a_familia = models.BooleanField(default=False)
    notificada_at = models.DateTimeField(null=True, blank=True)
    intervencion_resultante = models.ForeignKey(
        "intervenciones.Intervencion",
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name="cita_origen",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        ordering = ["inicio"]
        indexes = [models.Index(fields=["inicio", "fin"])]

    def __str__(self) -> str:
        return f"{self.inicio:%Y-%m-%d %H:%M} · {self.get_tipo_display()} · {self.persona}"

    @property
    def color_tailwind(self) -> str:
        return {
            self.Tipo.INDIVIDUAL: "blue",
            self.Tipo.FAMILIAR: "emerald",
            self.Tipo.MULTIPRO: "amber",
            self.Tipo.EXTERNA: "slate",
        }.get(self.tipo, "slate")

"""Señales de la app personas.

Implementa el §9 del Protocolo de Planes de Vida: cuando cambia el Gestor/a de
Caso o la Persona de Referencia de una persona atendida, ÁGORA genera un
AvisoCambioProfesional automáticamente para Dirección.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import AvisoCambioProfesional, PersonaAtendida

_PROFESIONALES_PREVIOS = {}


@receiver(pre_save, sender=PersonaAtendida)
def _capturar_profesionales_previos(sender, instance, **kwargs):
    """Antes de guardar, anota los profesionales actuales en BD si la persona ya existía."""
    if not instance.pk:
        return
    try:
        previo = PersonaAtendida.objects.only("gestor_caso_id", "persona_referencia_id").get(pk=instance.pk)
    except PersonaAtendida.DoesNotExist:
        return
    _PROFESIONALES_PREVIOS[instance.pk] = {
        "gestor_caso_id": previo.gestor_caso_id,
        "persona_referencia_id": previo.persona_referencia_id,
    }


@receiver(post_save, sender=PersonaAtendida)
def _generar_avisos_cambio_profesional(sender, instance, created, **kwargs):
    """Tras guardar, si los profesionales cambiaron, genera AvisoCambioProfesional."""
    previo = _PROFESIONALES_PREVIOS.pop(instance.pk, None)

    # Caso 1: alta nueva con profesional asignado
    if created:
        if instance.gestor_caso_id:
            AvisoCambioProfesional.objects.create(
                persona=instance,
                tipo=AvisoCambioProfesional.TipoCambio.ALTA_GESTOR,
                profesional_nuevo_id=instance.gestor_caso_id,
            )
        if instance.persona_referencia_id:
            AvisoCambioProfesional.objects.create(
                persona=instance,
                tipo=AvisoCambioProfesional.TipoCambio.ALTA_REFERENCIA,
                profesional_nuevo_id=instance.persona_referencia_id,
            )
        return

    if previo is None:
        return

    # Caso 2: cambio o baja de gestor/a
    if previo["gestor_caso_id"] != instance.gestor_caso_id:
        if instance.gestor_caso_id and previo["gestor_caso_id"]:
            tipo = AvisoCambioProfesional.TipoCambio.CAMBIO_GESTOR
        elif instance.gestor_caso_id:
            tipo = AvisoCambioProfesional.TipoCambio.ALTA_GESTOR
        else:
            tipo = AvisoCambioProfesional.TipoCambio.BAJA_GESTOR
        AvisoCambioProfesional.objects.create(
            persona=instance,
            tipo=tipo,
            profesional_anterior_id=previo["gestor_caso_id"],
            profesional_nuevo_id=instance.gestor_caso_id,
        )

    # Caso 3: cambio o baja de persona de referencia
    if previo["persona_referencia_id"] != instance.persona_referencia_id:
        if instance.persona_referencia_id and previo["persona_referencia_id"]:
            tipo = AvisoCambioProfesional.TipoCambio.CAMBIO_REFERENCIA
        elif instance.persona_referencia_id:
            tipo = AvisoCambioProfesional.TipoCambio.ALTA_REFERENCIA
        else:
            tipo = AvisoCambioProfesional.TipoCambio.BAJA_REFERENCIA
        AvisoCambioProfesional.objects.create(
            persona=instance,
            tipo=tipo,
            profesional_anterior_id=previo["persona_referencia_id"],
            profesional_nuevo_id=instance.persona_referencia_id,
        )

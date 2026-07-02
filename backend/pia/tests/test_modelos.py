"""Tests mínimos del Plan de Vida (protocolo Aspanias)."""
from datetime import date

import pytest

from personas.models import PersonaAtendida
from pia.models import PlanDeVida


@pytest.fixture
def persona_marta(db, centro_fab):
    return PersonaAtendida.objects.create(
        codigo_interno="FUE-2026-00001",
        nombre="Marta",
        apellido_1="González",
        apellido_2="Pérez",
        fecha_nacimiento=date(1985, 7, 11),
        corresponsable_principal=centro_fab.corresponsable,
        centro_referencia=centro_fab,
        fecha_alta=date(2018, 3, 14),
    )


@pytest.mark.django_db
class TestPlanDeVida:
    def test_estado_inicial_es_elaboracion(self, persona_marta, gestora_caso):
        pdv = PlanDeVida.objects.create(
            persona=persona_marta,
            anualidad=2026,
            gestor_caso=gestora_caso,
        )
        assert pdv.estado == PlanDeVida.Estado.EN_ELABORACION

    def test_dos_anualidades_distintas_misma_persona(self, persona_marta, gestora_caso):
        PlanDeVida.objects.create(persona=persona_marta, anualidad=2025, gestor_caso=gestora_caso)
        PlanDeVida.objects.create(persona=persona_marta, anualidad=2026, gestor_caso=gestora_caso)
        assert PlanDeVida.objects.filter(persona=persona_marta).count() == 2

    def test_str_incluye_anualidad(self, persona_marta, gestora_caso):
        pdv = PlanDeVida.objects.create(
            persona=persona_marta, anualidad=2026, gestor_caso=gestora_caso,
        )
        assert "2026" in str(pdv)

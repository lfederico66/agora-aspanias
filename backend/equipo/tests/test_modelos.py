"""Tests mínimos del módulo Equipo (Fase 2 backend · jun 2026).

Comprueba creación y propiedades básicas de los 6 modelos. No prueba flujos
de negocio completos (aprobaciones, generación de calendario individual);
eso se cubrirá en tests de servicios cuando se implementen.
"""
from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from equipo.models import (
    AsignacionPatron,
    CalendarioLaboral,
    CamposLaboralesProfesional,
    PatronTurno,
    Turno,
    Vacacion,
)
from personas.models import Centro, Profesional, Rol

User = get_user_model()


# ───────────────── Fixtures ─────────────────

@pytest.fixture
def centro(db):
    return Centro.objects.create(
        codigo="FUE",
        nombre="Residencia Fuentecillas",
        corresponsable=Centro.Corresponsable.FUNDACION,
    )


@pytest.fixture
def rol(db):
    return Rol.objects.create(codigo="gerocultora", nombre="Gerocultora")


@pytest.fixture
def profesional(db, rol):
    user = User.objects.create_user(
        username="mlopez", email="marta.lopez@aspanias.org",
    )
    return Profesional.objects.create(
        user=user,
        nombre_completo="López Pérez, Marta",
        rol_principal=rol,
        email_m365="marta.lopez@aspanias.org",
    )


# ───────────────── CamposLaboralesProfesional ─────────────────

def test_campos_laborales_creacion(profesional, centro):
    cl = CamposLaboralesProfesional.objects.create(
        profesional=profesional,
        centro_principal=centro,
        fecha_alta=date(2018, 3, 14),
    )
    assert cl.en_activo is True
    assert cl.tipo_jornada == CamposLaboralesProfesional.TipoJornada.COMPLETA
    assert str(cl) == "Datos laborales · López Pérez, Marta"


def test_campos_laborales_baja(profesional):
    cl = CamposLaboralesProfesional.objects.create(
        profesional=profesional,
        fecha_baja_grupo=date(2026, 1, 31),
    )
    assert cl.en_activo is False


# ───────────────── PatronTurno + AsignacionPatron ─────────────────

def test_patron_turno_secuencia(db):
    patron = PatronTurno.objects.create(
        nombre="Rotativo 7 días residencial",
        ciclo_dias=7,
        secuencia=["M", "M", "T", "T", "N", "N", "D"],
        horas_por_turno={"M": 8, "T": 7, "N": 10, "D": 0},
        horas_semana=38,
    )
    assert patron.turno_para_dia(0) == "M"
    assert patron.turno_para_dia(6) == "D"
    assert patron.turno_para_dia(7) == "M"  # ciclo
    assert patron.turno_para_dia(13) == "D"


def test_asignacion_patron_fecha_valida(db, profesional):
    patron = PatronTurno.objects.create(
        nombre="M-V Mañana",
        ciclo_dias=7,
        secuencia=["M"] * 5 + ["D", "D"],
        horas_semana=40,
    )
    asig = AsignacionPatron.objects.create(
        profesional=profesional,
        patron=patron,
        fecha_inicio=date(2026, 1, 1),
        fecha_fin=date(2026, 12, 31),
    )
    assert asig.fecha_fin > asig.fecha_inicio


# ───────────────── Vacacion ─────────────────

def test_vacacion_creacion(profesional):
    v = Vacacion.objects.create(
        profesional=profesional,
        tipo=Vacacion.Tipo.VACACIONES,
        fecha_inicio=date(2026, 9, 7),
        fecha_fin=date(2026, 9, 28),
        dias_naturales=22,
        dias_laborables=16,
    )
    assert v.estado == Vacacion.Estado.SOLICITADA
    assert v.es_categoria_especial_rgpd is False


def test_vacacion_it_categoria_especial(profesional):
    """Las IT son art. 9 RGPD (categoría especial)."""
    v = Vacacion.objects.create(
        profesional=profesional,
        tipo=Vacacion.Tipo.IT,
        fecha_inicio=date(2026, 5, 28),
        fecha_fin=date(2026, 7, 15),
    )
    assert v.es_categoria_especial_rgpd is True


def test_vacacion_fechas_invertidas_falla(profesional, db):
    with pytest.raises(IntegrityError):
        Vacacion.objects.create(
            profesional=profesional,
            tipo=Vacacion.Tipo.VACACIONES,
            fecha_inicio=date(2026, 8, 15),
            fecha_fin=date(2026, 8, 1),
        )


# ───────────────── Turno ─────────────────

def test_turno_unico_por_centro_fecha_franja(centro, profesional):
    t1 = Turno.objects.create(
        centro=centro,
        fecha=date(2026, 6, 20),
        franja=Turno.Franja.MANANA,
    )
    t1.profesionales.add(profesional)
    with pytest.raises(IntegrityError):
        Turno.objects.create(
            centro=centro,
            fecha=date(2026, 6, 20),
            franja=Turno.Franja.MANANA,
        )


# ───────────────── CalendarioLaboral ─────────────────

def test_calendario_laboral_aprobacion(centro):
    cal = CalendarioLaboral.objects.create(
        centro=centro,
        anio=2026,
        convenio=CalendarioLaboral.Convenio.RESIDENCIAS,
        jornada_anual_horas=1770,
        festivos=[
            {"fecha": "2026-01-01", "tipo": "nacional", "nombre": "Año Nuevo"},
            {"fecha": "2026-12-25", "tipo": "nacional", "nombre": "Navidad"},
        ],
    )
    assert cal.estado == CalendarioLaboral.Estado.BORRADOR
    assert cal.esta_firmado is False

    cal.estado = CalendarioLaboral.Estado.FIRMADO
    cal.fecha_firma_rlt = date(2025, 12, 2)
    cal.save()
    assert cal.esta_firmado is True


def test_calendario_centro_anio_unico(centro):
    CalendarioLaboral.objects.create(
        centro=centro, anio=2026,
        convenio=CalendarioLaboral.Convenio.DISCAPACIDAD,
        jornada_anual_horas=1752,
    )
    with pytest.raises(IntegrityError):
        CalendarioLaboral.objects.create(
            centro=centro, anio=2026,
            convenio=CalendarioLaboral.Convenio.DISCAPACIDAD,
            jornada_anual_horas=1752,
        )

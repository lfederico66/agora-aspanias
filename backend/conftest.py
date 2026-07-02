"""Fixtures compartidas para los tests de ÁGORA.

Convención: las fixtures aquí están pensadas para arrancar una BD limpia con
los objetos mínimos necesarios (centros, servicios, roles) para crear personas
atendidas en los tests.
"""
import pytest
from django.contrib.auth import get_user_model

from personas.models import Centro, Profesional, Rol, Servicio

User = get_user_model()


@pytest.fixture
def centro_fab(db):
    """Residencia Fuentecillas — centro residencial bajo Fundación Aspanias Burgos."""
    return Centro.objects.create(
        codigo="FUE",
        nombre="Residencia Fuentecillas",
        corresponsable=Centro.Corresponsable.FUNDACION,
        municipio="Burgos",
    )


@pytest.fixture
def centro_aspaniasmerc(db):
    """Centro de Día Río Arlanza — bajo Aspaniasmerc 2016."""
    return Centro.objects.create(
        codigo="ARL",
        nombre="Centro de Día Río Arlanza",
        corresponsable=Centro.Corresponsable.ASPANIASMERC,
        municipio="Burgos",
    )


@pytest.fixture
def servicio_residencia(db):
    return Servicio.objects.create(
        codigo="RES_DI",
        nombre="Residencia DI",
        tipo=Servicio.Tipo.RESIDENCIA,
    )


@pytest.fixture
def rol_ts(db):
    return Rol.objects.create(codigo="TS", nombre="Trabajo Social")


@pytest.fixture
def rol_to(db):
    return Rol.objects.create(codigo="TO", nombre="Terapia Ocupacional")


@pytest.fixture
def usuario_profesional(db):
    return User.objects.create_user(
        username="lmartinez",
        email="lucia.martinez@aspaniasburgos.com",
        password="dev-password-not-real",
    )


@pytest.fixture
def gestora_caso(db, usuario_profesional, rol_ts, centro_fab):
    """Profesional habilitada como Gestor/a de Caso."""
    prof = Profesional.objects.create(
        user=usuario_profesional,
        nombre_completo="Lucía Martínez",
        rol_principal=rol_ts,
        email_m365="lucia.martinez@aspaniasburgos.com",
        puede_ser_gestor_caso=True,
    )
    prof.centros_acceso.add(centro_fab)
    return prof

"""Tests de core.permissions — Fase 2.5.3."""
import pytest
from django.contrib.auth import get_user_model

from core.permissions import (
    ROLES_CON_ACCESO_CLINICO,
    ROLES_CON_ACCESO_JURIDICO,
    tiene_acceso_clinico,
    tiene_acceso_juridico,
)
from personas.models import Profesional, Rol

User = get_user_model()


@pytest.mark.django_db
class TestAccesoClinico:
    def test_anonimo_no_tiene_acceso(self):
        from django.contrib.auth.models import AnonymousUser
        assert tiene_acceso_clinico(AnonymousUser()) is False

    def test_superuser_tiene_acceso(self):
        u = User.objects.create_superuser(username="root", password="x")
        assert tiene_acceso_clinico(u) is True

    def test_due_tiene_acceso(self, centro_fab):
        u = User.objects.create_user(username="enfermera", password="x")
        rol = Rol.objects.create(codigo="DUE", nombre="Enfermería")
        Profesional.objects.create(
            user=u, nombre_completo="Beatriz Hernando",
            rol_principal=rol, email_m365="b@aspaniasburgos.com",
        )
        assert tiene_acceso_clinico(u) is True

    def test_trabajador_social_no_tiene_acceso_clinico(self, rol_ts):
        u = User.objects.create_user(username="ts", password="x")
        Profesional.objects.create(
            user=u, nombre_completo="María Ruiz",
            rol_principal=rol_ts, email_m365="m@aspaniasburgos.com",
        )
        assert tiene_acceso_clinico(u) is False

    def test_profesional_inactivo_no_tiene_acceso(self, centro_fab):
        u = User.objects.create_user(username="exenfermera", password="x")
        rol = Rol.objects.create(codigo="DUE", nombre="Enfermería")
        Profesional.objects.create(
            user=u, nombre_completo="X",
            rol_principal=rol, email_m365="x@aspaniasburgos.com",
            activo=False,
        )
        assert tiene_acceso_clinico(u) is False


@pytest.mark.django_db
class TestAccesoJuridico:
    def test_direccion_tiene_acceso(self, centro_fab):
        u = User.objects.create_user(username="director", password="x")
        rol = Rol.objects.create(codigo="DIRECCION", nombre="Dirección")
        Profesional.objects.create(
            user=u, nombre_completo="Federico Martínez",
            rol_principal=rol, email_m365="federico@aspaniasburgos.com",
        )
        assert tiene_acceso_juridico(u) is True

    def test_due_no_tiene_acceso_juridico(self):
        u = User.objects.create_user(username="enfermera2", password="x")
        rol = Rol.objects.create(codigo="DUE", nombre="Enfermería")
        Profesional.objects.create(
            user=u, nombre_completo="Y",
            rol_principal=rol, email_m365="y@aspaniasburgos.com",
        )
        assert tiene_acceso_juridico(u) is False


def test_catalogos_inmutables():
    """Verifica que los catálogos sean conjuntos congelados (no se modifican accidentalmente)."""
    assert isinstance(ROLES_CON_ACCESO_CLINICO, frozenset)
    assert isinstance(ROLES_CON_ACCESO_JURIDICO, frozenset)
    assert "DUE" in ROLES_CON_ACCESO_CLINICO
    assert "DIRECCION" in ROLES_CON_ACCESO_JURIDICO

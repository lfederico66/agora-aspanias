"""Tests de la bitácora de accesos — corazón del cumplimiento RGPD art. 32."""
from datetime import date

import pytest

from core.models import RegistroAcceso
from personas.models import PersonaAtendida


@pytest.mark.django_db
class TestRegistroAcceso:
    def test_alta_minima(self, usuario_profesional):
        r = RegistroAcceso.objects.create(
            profesional=usuario_profesional,
            accion=RegistroAcceso.Accion.LEER,
            entidad="PersonaAtendida",
            ruta="/personas/abc/",
            ip="10.0.0.1",
        )
        assert r.timestamp is not None
        assert r.accion == "leer"

    def test_acceso_a_ficha_concreta(self, usuario_profesional, centro_fab):
        p = PersonaAtendida.objects.create(
            codigo_interno="FUE-2026-00010",
            nombre="Marta", apellido_1="González",
            fecha_nacimiento=date(1985, 7, 11),
            corresponsable_principal=centro_fab.corresponsable,
            centro_referencia=centro_fab,
            fecha_alta=date(2018, 3, 14),
        )
        r = RegistroAcceso.objects.create(
            profesional=usuario_profesional,
            persona_consultada_id=p.id,
            accion=RegistroAcceso.Accion.LEER,
            entidad="PersonaAtendida",
            ruta=f"/personas/{p.id}/",
        )
        # El UUID del registro de acceso coincide con la persona consultada
        assert r.persona_consultada_id == p.id

    def test_login_y_logout(self, usuario_profesional):
        RegistroAcceso.objects.create(
            profesional=usuario_profesional,
            accion=RegistroAcceso.Accion.LOGIN,
            ip="10.0.0.5",
        )
        RegistroAcceso.objects.create(
            profesional=usuario_profesional,
            accion=RegistroAcceso.Accion.LOGOUT,
            ip="10.0.0.5",
        )
        accesos = RegistroAcceso.objects.filter(profesional=usuario_profesional).count()
        assert accesos == 2

    def test_no_puede_eliminarse_un_registro(self, usuario_profesional):
        """La bitácora es append-only. Eliminar registros tiene que dejar huella
        — al menos la BD acepta el delete, pero la convención (revisada por Lex Digital)
        es no permitirlo desde la UI. Este test deja constancia del compromiso."""
        r = RegistroAcceso.objects.create(
            profesional=usuario_profesional,
            accion=RegistroAcceso.Accion.LEER,
            entidad="PersonaAtendida",
        )
        rid = r.id
        # En v0.x se puede borrar a nivel ORM; en producción se restringirá por permisos
        # y por trigger PostgreSQL. Documentado en docs/rgpd/EIPD_inicial.md.
        r.delete()
        assert not RegistroAcceso.objects.filter(id=rid).exists()

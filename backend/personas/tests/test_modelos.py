"""Tests mínimos del modelo de personas (v0.12)."""
from datetime import date

import pytest
from django.db import IntegrityError

from personas.models import (
    Cama,
    CertificadoDiscapacidad,
    Habitacion,
    MedidaDeApoyo,
    Modulo,
    OcupacionCama,
    PersonaAtendida,
    ReconocimientoDependencia,
)


@pytest.mark.django_db
class TestPersonaAtendida:
    def test_alta_minima(self, centro_fab):
        p = PersonaAtendida.objects.create(
            codigo_interno="FUE-2026-00001",
            nombre="Marta",
            apellido_1="González",
            apellido_2="Pérez",
            fecha_nacimiento=date(1985, 7, 11),
            corresponsable_principal=centro_fab.corresponsable,
            centro_referencia=centro_fab,
            fecha_alta=date(2018, 3, 14),
        )
        assert p.activa is True
        assert "González" in str(p)

    def test_baja_marca_no_activa(self, centro_fab):
        p = PersonaAtendida.objects.create(
            codigo_interno="FUE-2026-00002",
            nombre="Antonio",
            apellido_1="Romero",
            apellido_2="Sanz",
            fecha_nacimiento=date(1972, 1, 5),
            corresponsable_principal=centro_fab.corresponsable,
            centro_referencia=centro_fab,
            fecha_alta=date(2019, 6, 1),
            fecha_baja=date(2026, 5, 15),
            motivo_baja=PersonaAtendida.MotivoBaja.TRASLADO,
        )
        assert p.activa is False

    def test_codigo_interno_es_unico(self, centro_fab):
        PersonaAtendida.objects.create(
            codigo_interno="FUE-2026-00099",
            nombre="X",
            apellido_1="Y",
            fecha_nacimiento=date(1980, 1, 1),
            corresponsable_principal=centro_fab.corresponsable,
            centro_referencia=centro_fab,
            fecha_alta=date(2020, 1, 1),
        )
        with pytest.raises(IntegrityError):
            PersonaAtendida.objects.create(
                codigo_interno="FUE-2026-00099",  # duplicado
                nombre="X2",
                apellido_1="Y2",
                fecha_nacimiento=date(1981, 1, 1),
                corresponsable_principal=centro_fab.corresponsable,
                centro_referencia=centro_fab,
                fecha_alta=date(2021, 1, 1),
            )


@pytest.mark.django_db
class TestMedidaApoyo:
    def test_persona_sin_medida_por_defecto(self, centro_fab):
        p = PersonaAtendida.objects.create(
            codigo_interno="FUE-2026-00003",
            nombre="Carmen",
            apellido_1="Martín",
            apellido_2="Olalla",
            fecha_nacimiento=date(1968, 11, 22),
            corresponsable_principal=centro_fab.corresponsable,
            centro_referencia=centro_fab,
            fecha_alta=date(2017, 4, 10),
        )
        # Una persona puede no tener medida creada todavía
        assert not hasattr(p, "medida_apoyo") or MedidaDeApoyo.objects.filter(persona=p).count() == 0

    def test_medida_apoyo_judicial_con_curatela(self, centro_fab):
        p = PersonaAtendida.objects.create(
            codigo_interno="FUE-2026-00004",
            nombre="Marta",
            apellido_1="González",
            fecha_nacimiento=date(1985, 7, 11),
            corresponsable_principal=centro_fab.corresponsable,
            centro_referencia=centro_fab,
            fecha_alta=date(2018, 3, 14),
        )
        m = MedidaDeApoyo.objects.create(
            persona=p,
            tipo=MedidaDeApoyo.Tipo.APOYO_JUDICIAL,
            subtipo_curatela=MedidaDeApoyo.SubtipoCuratela.REPRESENTATIVA_PARCIAL,
            fecha_resolucion=date(2022, 11, 18),
            organo_judicial="Juzgado 1ª Inst. Burgos nº 4",
        )
        assert m.vigente is True
        assert "Apoyo establecido judicialmente" in str(m)


@pytest.mark.django_db
class TestRatioGestoraCaso:
    def test_max_casos_es_30_por_defecto(self, gestora_caso):
        assert gestora_caso.max_casos_asignados == 30

    def test_no_sobrepasa_ratio_sin_personas(self, gestora_caso):
        assert gestora_caso.casos_actuales_gestor == 0
        assert gestora_caso.sobrepasa_ratio is False


@pytest.mark.django_db
class TestCertificadoDiscapacidad:
    def test_grado_valido(self, centro_fab):
        p = PersonaAtendida.objects.create(
            codigo_interno="FUE-2026-00005",
            nombre="Marta",
            apellido_1="González",
            fecha_nacimiento=date(1985, 7, 11),
            corresponsable_principal=centro_fab.corresponsable,
            centro_referencia=centro_fab,
            fecha_alta=date(2018, 3, 14),
        )
        cert = CertificadoDiscapacidad.objects.create(
            persona=p,
            fecha_reconocimiento=date(2004, 5, 22),
            diagnostico_principal="Discapacidad intelectual moderada",
            grado_pct=65,
            tipo_reconocimiento=CertificadoDiscapacidad.TipoReconocimiento.PERMANENTE,
        )
        assert cert.grado_pct == 65
        assert cert.vigente is True


@pytest.mark.django_db
class TestReconocimientoDependencia:
    def test_grado_ii(self, centro_fab):
        p = PersonaAtendida.objects.create(
            codigo_interno="FUE-2026-00006",
            nombre="Marta",
            apellido_1="González",
            fecha_nacimiento=date(1985, 7, 11),
            corresponsable_principal=centro_fab.corresponsable,
            centro_referencia=centro_fab,
            fecha_alta=date(2018, 3, 14),
        )
        r = ReconocimientoDependencia.objects.create(
            persona=p,
            grado=ReconocimientoDependencia.Grado.II,
            puntos_bvd=52,
            fecha_resolucion=date(2023, 4, 13),
            tipo_beneficio=ReconocimientoDependencia.TipoBeneficio.PLAZA_RESIDENCIAL,
        )
        assert "Grado II" in str(r)


@pytest.mark.django_db
class TestAlojamiento:
    def test_jerarquia_modulo_habitacion_cama(self, centro_fab):
        modulo = Modulo.objects.create(centro=centro_fab, codigo="N", nombre="Norte")
        hab = Habitacion.objects.create(
            centro=centro_fab, modulo=modulo, numero="24",
            tipo=Habitacion.Tipo.DOBLE, con_bano_propio=True, adaptada_movilidad_reducida=True,
        )
        cama_a = Cama.objects.create(habitacion=hab, identificador="A")
        cama_b = Cama.objects.create(habitacion=hab, identificador="B", articulada=True)

        assert hab.modulo == modulo
        assert cama_a.esta_libre is True
        assert cama_b.articulada is True

    def test_ocupacion_activa_unica_por_persona(self, centro_fab):
        """Una persona no puede tener 2 ocupaciones de cama activas a la vez."""
        modulo = Modulo.objects.create(centro=centro_fab, codigo="N", nombre="Norte")
        hab = Habitacion.objects.create(centro=centro_fab, modulo=modulo, numero="24", tipo=Habitacion.Tipo.DOBLE)
        cama_a = Cama.objects.create(habitacion=hab, identificador="A")
        cama_b = Cama.objects.create(habitacion=hab, identificador="B")

        p = PersonaAtendida.objects.create(
            codigo_interno="FUE-2026-00007",
            nombre="Marta", apellido_1="González",
            fecha_nacimiento=date(1985, 7, 11),
            corresponsable_principal=centro_fab.corresponsable,
            centro_referencia=centro_fab,
            fecha_alta=date(2018, 3, 14),
        )
        OcupacionCama.objects.create(persona=p, cama=cama_a, fecha_inicio=date(2024, 4, 11))
        with pytest.raises(IntegrityError):
            OcupacionCama.objects.create(persona=p, cama=cama_b, fecha_inicio=date(2026, 5, 1))

    def test_ubicacion_residencial_property(self, centro_fab):
        modulo = Modulo.objects.create(centro=centro_fab, codigo="N", nombre="Norte")
        hab = Habitacion.objects.create(centro=centro_fab, modulo=modulo, numero="24", tipo=Habitacion.Tipo.DOBLE)
        cama_b = Cama.objects.create(habitacion=hab, identificador="B", articulada=True)

        p = PersonaAtendida.objects.create(
            codigo_interno="FUE-2026-00008",
            nombre="Marta", apellido_1="González",
            fecha_nacimiento=date(1985, 7, 11),
            corresponsable_principal=centro_fab.corresponsable,
            centro_referencia=centro_fab,
            fecha_alta=date(2018, 3, 14),
        )
        OcupacionCama.objects.create(persona=p, cama=cama_b, fecha_inicio=date(2024, 4, 11))

        ubicacion = p.ubicacion_residencial
        assert "Norte" in ubicacion
        assert "24" in ubicacion
        assert "B" in ubicacion

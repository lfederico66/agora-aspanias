"""Cálculo en vivo de indicadores básicos sobre la base actual.

En v0.1 los indicadores se computan al vuelo. En M2 se materializarán en
MedicionIndicador con un job nocturno.
"""
from django.db.models import Count, Q

from personas.models import Centro, MedidaDeApoyo, PersonaAtendida


def panel_global() -> dict:
    activas = PersonaAtendida.objects.filter(fecha_baja__isnull=True)
    total = activas.count()

    # Distribución por colectivo (basado en perfiles activos)
    por_colectivo = {
        "di": activas.filter(perfiles_di__fin_at__isnull=True).distinct().count(),
        "mayor": activas.filter(perfiles_mayor__fin_at__isnull=True).distinct().count(),
        "insercion": activas.filter(perfiles_insercion__fin_at__isnull=True).distinct().count(),
    }
    por_colectivo["otros"] = max(0, total - sum(por_colectivo.values()))

    # Corresponsable
    por_corresponsable = dict(
        activas.values_list("corresponsable_principal")
        .annotate(n=Count("id"))
    )

    # Centros
    centros = (
        Centro.objects.filter(activo=True)
        .annotate(personas=Count("personas", filter=Q(personas__fecha_baja__isnull=True)))
        .order_by("-personas")
    )

    # Ley 8/2021
    por_medida = dict(
        MedidaDeApoyo.objects.values_list("tipo")
        .annotate(n=Count("id"))
    )

    return {
        "total": total,
        "por_colectivo": por_colectivo,
        "por_corresponsable": por_corresponsable,
        "centros": centros,
        "por_medida": por_medida,
    }


def kpis_planes_vida() -> dict:
    """Reproduce los indicadores de la hoja 'Datos Grupo Aspanias' del Excel."""
    from pia.models import PlanDeVida

    personas_activas = PersonaAtendida.objects.filter(fecha_baja__isnull=True)
    total_usuarios = personas_activas.count()
    def by_corresponsable(qs):
        return {
            "total": qs.count(),
            "fab": qs.filter(persona__corresponsable_principal="fundacion_aspanias_burgos").count(),
            "aspaniasmerc": qs.filter(persona__corresponsable_principal="aspaniasmerc").count(),
        }

    planes_activos = PlanDeVida.objects.filter(persona__fecha_baja__isnull=True)
    realizados = by_corresponsable(planes_activos.filter(pv_realizado=True))
    pendientes_realizar = by_corresponsable(planes_activos.filter(pv_realizado=False))
    revisados = by_corresponsable(planes_activos.filter(pv_revisado=True))
    fuera_plazo = by_corresponsable(planes_activos.filter(estado_revision="fuera_plazo"))

    # Desglose por centro — para cada KPI
    desglose_centros = []
    for c in Centro.objects.filter(activo=True).order_by("nombre"):
        personas_c = personas_activas.filter(centro_referencia=c).count()
        planes_c = planes_activos.filter(persona__centro_referencia=c)
        desglose_centros.append({
            "centro": c,
            "personas": personas_c,
            "realizados": planes_c.filter(pv_realizado=True).count(),
            "pendientes": planes_c.filter(pv_realizado=False).count(),
            "revisados": planes_c.filter(pv_revisado=True).count(),
            "fuera_plazo": planes_c.filter(estado_revision="fuera_plazo").count(),
        })

    return {
        "total_usuarios": total_usuarios,
        "usuarios_fab": personas_activas.filter(corresponsable_principal="fundacion_aspanias_burgos").count(),
        "usuarios_aspaniasmerc": personas_activas.filter(corresponsable_principal="aspaniasmerc").count(),
        "realizados": realizados,
        "pendientes_realizar": pendientes_realizar,
        "revisados": revisados,
        "fuera_plazo": fuera_plazo,
        "desglose_centros": desglose_centros,
    }


def carga_gestores_caso() -> list:
    """Reproduce la hoja 'Gestores de caso': gestores × centros con conteo de casos."""
    from personas.models import Profesional

    gestores = Profesional.objects.filter(puede_ser_gestor_caso=True, activo=True)
    centros = list(Centro.objects.filter(activo=True).order_by("nombre"))
    filas = []
    for g in gestores.order_by("nombre_completo"):
        casos_total = g.personas_como_gestor.filter(fecha_baja__isnull=True).count()
        # Lista ordenada paralela a `centros` (orden estable por nombre)
        valores_por_centro = [
            g.personas_como_gestor.filter(
                fecha_baja__isnull=True, centro_referencia=c,
            ).count()
            for c in centros
        ]
        filas.append({
            "gestor": g,
            "total": casos_total,
            "max": g.max_casos_asignados,
            "sobrepasa": casos_total > g.max_casos_asignados,
            "valores": valores_por_centro,
        })
    return {"filas": filas, "centros": centros}

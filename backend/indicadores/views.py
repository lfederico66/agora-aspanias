"""Vistas del cuadro de mando — Fase 2 M1.5.

Una única página con 4 pestañas Alpine.js:
- Cuadro general: panel macro del grupo (personas, centros, distribución, Ley 8/2021).
- Datos Grupo Aspanias · Planes de Vida: reproduce la hoja del Excel.
- Gestores de caso: ratio ≤ 30 casos por gestor/a.
- Histórico: tendencia mes a mes a partir de SnapshotPlanesVida.
"""
from datetime import date

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .calc import carga_gestores_caso, kpis_planes_vida, panel_global
from .models import SnapshotPlanesVida


@login_required
def cuadro_mando(request):
    """Vista principal con las 4 pestañas. Todos los datos en una query única."""
    panel = panel_global()
    kpis_pv = kpis_planes_vida()
    gestores = carga_gestores_caso()
    historico = (
        SnapshotPlanesVida.objects
        .order_by("-fecha")[:12]  # últimos 12 meses
    )

    # Cifras agregadas de gestores para chips arriba
    filas = gestores.get("filas", [])
    n_total = len(filas)
    n_sobre_ratio = sum(1 for f in filas if f["sobrepasa"])
    n_cerca_ratio = sum(1 for f in filas if not f["sobrepasa"] and f["total"] >= f["max"] - 5)
    n_ok = n_total - n_sobre_ratio - n_cerca_ratio

    return render(request, "indicadores/cuadro_mando.html", {
        "panel": panel,
        "kpis_pv": kpis_pv,
        "gestores": gestores,
        "historico": historico,
        "gestores_resumen": {
            "total": n_total,
            "ok": n_ok,
            "cerca_ratio": n_cerca_ratio,
            "sobre_ratio": n_sobre_ratio,
        },
        "tab_inicial": request.GET.get("tab", "general"),
        "ahora": date.today(),
    })


# Vistas alternativas accesibles directamente (compat con URLs antiguas + posibles enlaces externos)


@login_required
def kpis_pv(request):
    return render(request, "indicadores/kpis_pv.html", {"d": kpis_planes_vida()})


@login_required
def gestores_caso(request):
    return render(request, "indicadores/gestores_caso.html", carga_gestores_caso())

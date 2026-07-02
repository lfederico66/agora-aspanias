"""Vistas de agenda — Fase 2 M1.3.

Tres vistas con switcher común: Hoy (timeline vertical), Semana (5 columnas
Lun-Vie), Mes (cuadrícula tradicional). Todas comparten el cabezal de
controles y aceptan los mismos filtros (?persona=, ?centro=, ?profesional=).
"""
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from personas.models import PersonaAtendida

from .forms import CitaForm
from .models import Cita

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fecha_referencia(request) -> date:
    """Lee ?fecha=YYYY-MM-DD; si no hay, devuelve hoy."""
    raw = request.GET.get("fecha")
    if raw:
        try:
            return date.fromisoformat(raw)
        except ValueError:
            pass
    return timezone.localdate()


def _aplicar_filtros(qs, request):
    """Filtra el queryset de citas por ?persona, ?profesional, ?centro."""
    persona_id = request.GET.get("persona")
    if persona_id:
        qs = qs.filter(persona__id=persona_id)
    profesional_id = request.GET.get("profesional")
    if profesional_id:
        qs = qs.filter(profesionales__id=profesional_id)
    centro_codigo = request.GET.get("centro")
    if centro_codigo:
        qs = qs.filter(persona__centro_referencia__codigo=centro_codigo)
    return qs.distinct()


# ---------------------------------------------------------------------------
# Vista Hoy — timeline vertical de 8:00 a 20:00
# ---------------------------------------------------------------------------


@login_required
def vista_hoy(request):
    """Citas del día agrupadas en franjas horarias."""
    referencia = _fecha_referencia(request)
    citas = (
        _aplicar_filtros(
            Cita.objects
            .filter(inicio__date=referencia)
            .exclude(estado=Cita.Estado.CANCELADA)
            .select_related("persona")
            .prefetch_related("profesionales"),
            request,
        )
        .order_by("inicio")
    )

    # Resumen del día
    resumen = {
        "total": citas.count(),
        "individuales": sum(1 for c in citas if c.tipo == "individual"),
        "familiares": sum(1 for c in citas if c.tipo == "familiar"),
        "multipro": sum(1 for c in citas if c.tipo == "multipro"),
        "externas": sum(1 for c in citas if c.tipo == "externa"),
        "personas": len({c.persona_id for c in citas}),
        "notificables": sum(1 for c in citas if c.tipo == "familiar" or c.notificada_a_familia),
        "notificadas": sum(1 for c in citas if c.notificada_a_familia),
    }

    ahora = timezone.localtime()

    return render(request, "agenda/hoy.html", {
        "referencia": referencia,
        "citas": citas,
        "resumen": resumen,
        "ahora": ahora,
        "es_hoy_real": referencia == ahora.date(),
        "anterior": (referencia - timedelta(days=1)).isoformat(),
        "siguiente": (referencia + timedelta(days=1)).isoformat(),
        "hoy_iso": ahora.date().isoformat(),
    })


@login_required
def vista_semana(request):
    """Agenda semanal: lunes-viernes, todas las citas activas del grupo."""
    hoy = request.GET.get("fecha")
    if hoy:
        try:
            referencia = date.fromisoformat(hoy)
        except ValueError:
            referencia = timezone.localdate()
    else:
        referencia = timezone.localdate()
    inicio_semana = referencia - timedelta(days=referencia.weekday())
    fin_semana = inicio_semana + timedelta(days=5)
    citas = (
        Cita.objects
        .filter(inicio__date__gte=inicio_semana, inicio__date__lt=fin_semana)
        .exclude(estado=Cita.Estado.CANCELADA)
        .select_related("persona")
        .prefetch_related("profesionales")
        .order_by("inicio")
    )
    # Agrupar por día
    dias = []
    for offset in range(5):
        dia = inicio_semana + timedelta(days=offset)
        dias.append({
            "fecha": dia,
            "es_hoy": dia == timezone.localdate(),
            "citas": [c for c in citas if c.inicio.date() == dia],
        })
    return render(request, "agenda/semana.html", {
        "dias": dias,
        "inicio_semana": inicio_semana,
        "fin_semana": fin_semana - timedelta(days=1),
        "semana_anterior": (inicio_semana - timedelta(days=7)).isoformat(),
        "semana_siguiente": (inicio_semana + timedelta(days=7)).isoformat(),
        "hoy_iso": timezone.localdate().isoformat(),
    })


@login_required
def crear_cita(request):
    """Crea una cita nueva. Si llega `persona` en query, la pre-selecciona."""
    persona_id = request.GET.get("persona")
    initial = {}
    if persona_id:
        try:
            persona = PersonaAtendida.objects.get(pk=persona_id)
            initial["persona"] = persona
        except (PersonaAtendida.DoesNotExist, ValueError):
            pass
    if request.method == "POST":
        form = CitaForm(request.POST)
        if form.is_valid():
            cita = form.save()
            messages.success(request, f"Cita creada para {cita.persona}.")
            return redirect("agenda:semana")
    else:
        form = CitaForm(initial=initial)
    return render(request, "agenda/cita_form.html", {
        "form": form, "modo": "crear", "titulo": "Nueva cita",
    })


@login_required
def vista_mes(request):
    """Cuadrícula tipo calendario con conteo de citas por día."""
    referencia = _fecha_referencia(request)
    primer_dia = referencia.replace(day=1)

    # Calculamos el rango ampliado para llenar 6 semanas × 7 días
    # Primer día de la primera fila: el lunes anterior o igual al día 1
    inicio_grid = primer_dia - timedelta(days=primer_dia.weekday())
    fin_grid = inicio_grid + timedelta(days=42)  # 6 semanas

    citas = (
        _aplicar_filtros(
            Cita.objects
            .filter(inicio__date__gte=inicio_grid, inicio__date__lt=fin_grid)
            .exclude(estado=Cita.Estado.CANCELADA)
            .select_related("persona"),
            request,
        )
        .order_by("inicio")
    )

    # Agrupar por día
    por_dia = {}
    for c in citas:
        por_dia.setdefault(c.inicio.date(), []).append(c)

    # Construir 6 semanas × 7 días
    semanas = []
    hoy_real = timezone.localdate()
    for s in range(6):
        fila = []
        for d in range(7):
            dia = inicio_grid + timedelta(days=s * 7 + d)
            fila.append({
                "fecha": dia,
                "del_mes": dia.month == primer_dia.month,
                "es_hoy": dia == hoy_real,
                "es_finde": d >= 5,
                "citas": por_dia.get(dia, []),
            })
        semanas.append(fila)

    # Mes anterior / siguiente
    mes_anterior = (primer_dia - timedelta(days=1)).replace(day=1)
    if primer_dia.month == 12:
        mes_siguiente = primer_dia.replace(year=primer_dia.year + 1, month=1)
    else:
        mes_siguiente = primer_dia.replace(month=primer_dia.month + 1)

    return render(request, "agenda/mes.html", {
        "referencia": referencia,
        "primer_dia": primer_dia,
        "semanas": semanas,
        "total_mes": sum(1 for c in citas if c.inicio.date().month == primer_dia.month),
        "anterior": mes_anterior.isoformat(),
        "siguiente": mes_siguiente.isoformat(),
        "hoy_iso": hoy_real.isoformat(),
    })


@login_required
def editar_cita(request, cita_id):
    cita = get_object_or_404(Cita, pk=cita_id)
    if request.method == "POST":
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            messages.success(request, "Cita actualizada.")
            return redirect("agenda:semana")
    else:
        form = CitaForm(instance=cita)
    return render(request, "agenda/cita_form.html", {
        "form": form, "modo": "editar", "titulo": f"Editar cita · {cita.persona}",
        "cita": cita,
    })

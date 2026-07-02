"""Vistas de intervenciones y valoraciones — Fase 2 M1.4.

Timeline cronológico unificado por persona: intervenciones + valoraciones
ordenadas cronológicamente, con filtros por período, tipo y confidencialidad.
Vinculación visible a objetivos del Plan de Vida.
"""
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.permissions import puede_ver_intervencion
from personas.models import PersonaAtendida

from .forms import IntervencionForm, ValoracionForm
from .models import Intervencion, TipoIntervencion

# ---------------------------------------------------------------------------
# Timeline unificado intervenciones + valoraciones
# ---------------------------------------------------------------------------


@login_required
def lista_intervenciones(request, persona_id):
    """Timeline cronológico de una persona.

    Filtros:
      - ``desde``: ``30`` (defecto), ``90``, ``365``, ``todo``.
      - ``tipo``: código de TipoIntervencion para filtrar (opcional).
      - ``ver``: ``todo`` (defecto), ``intervenciones``, ``valoraciones``.
    """
    persona = get_object_or_404(PersonaAtendida, pk=persona_id)
    desde = request.GET.get("desde", "30")
    tipo_codigo = request.GET.get("tipo")
    ver = request.GET.get("ver", "todo")

    if desde == "90":
        dt = timezone.now() - timedelta(days=90)
    elif desde == "365":
        dt = timezone.now() - timedelta(days=365)
    elif desde == "todo":
        dt = None
    else:
        dt = timezone.now() - timedelta(days=30)

    intervenciones = persona.intervenciones.select_related(
        "profesional", "tipo", "objetivo_vinculado",
    )
    if dt is not None:
        intervenciones = intervenciones.filter(fecha_hora__gte=dt)
    if tipo_codigo:
        intervenciones = intervenciones.filter(tipo__codigo=tipo_codigo)

    # Filtrado por confidencialidad — Fase 2.5.4.
    # Las intervenciones restringidas (clínica/jurídica) solo las ven usuarios
    # con el rol correspondiente. Para los demás, las ocultamos del listado;
    # se podría mostrar como "fila restringida" pero por simplicidad y RGPD
    # las eliminamos del queryset.
    intervenciones = [i for i in intervenciones if puede_ver_intervencion(request.user, i)]

    valoraciones = persona.valoraciones.select_related("aplicado_por")
    if dt is not None:
        valoraciones = valoraciones.filter(fecha__gte=dt.date())

    # KPIs (intervenciones — ya es lista tras filtrado por confidencialidad)
    kpis = {
        "total": len(intervenciones),
        "valoraciones": valoraciones.count(),
        "vinculadas_objetivo": sum(1 for i in intervenciones if i.objetivo_vinculado_id),
        "restringidas": sum(
            1 for i in intervenciones
            if i.confidencialidad != Intervencion.Confidencialidad.NORMAL
        ),
    }

    # Unificar timeline cronológico (más reciente primero)
    timeline = []
    if ver != "valoraciones":
        for i in intervenciones:
            timeline.append({
                "tipo_item": "intervencion",
                "fecha": i.fecha_hora,
                "obj": i,
            })
    if ver != "intervenciones":
        for v in valoraciones:
            # Aseguramos datetime para ordenar junto con intervenciones
            dt_val = datetime.combine(v.fecha, datetime.min.time())
            dt_val = timezone.make_aware(dt_val) if timezone.is_naive(dt_val) else dt_val
            timeline.append({
                "tipo_item": "valoracion",
                "fecha": dt_val,
                "obj": v,
            })
    timeline.sort(key=lambda x: x["fecha"], reverse=True)

    # Catálogo de tipos para el filtro
    tipos = TipoIntervencion.objects.order_by("nombre")

    return render(request, "intervenciones/lista.html", {
        "persona": persona,
        "timeline": timeline,
        "kpis": kpis,
        "rango": desde,
        "tipo_actual": tipo_codigo or "",
        "ver_actual": ver,
        "tipos": tipos,
    })


@login_required
def crear_intervencion(request, persona_id):
    persona = get_object_or_404(PersonaAtendida, pk=persona_id)
    if request.method == "POST":
        form = IntervencionForm(request.POST, persona=persona)
        if form.is_valid():
            form.save()
            messages.success(request, "Intervención registrada.")
            return redirect("intervenciones:lista", persona_id=persona.id)
    else:
        form = IntervencionForm(persona=persona, initial={
            "persona": persona,
            "fecha_hora": timezone.now(),
        })
    return render(request, "intervenciones/intervencion_form.html", {
        "form": form, "persona": persona, "modo": "crear",
        "titulo": f"Nueva intervención · {persona.apellido_1}, {persona.nombre}",
    })


@login_required
def editar_intervencion(request, persona_id, intervencion_id):
    persona = get_object_or_404(PersonaAtendida, pk=persona_id)
    intervencion = get_object_or_404(Intervencion, pk=intervencion_id, persona=persona)
    if request.method == "POST":
        form = IntervencionForm(request.POST, instance=intervencion, persona=persona)
        if form.is_valid():
            form.save()
            messages.success(request, "Intervención actualizada.")
            return redirect("intervenciones:lista", persona_id=persona.id)
    else:
        form = IntervencionForm(instance=intervencion, persona=persona)
    return render(request, "intervenciones/intervencion_form.html", {
        "form": form, "persona": persona, "modo": "editar",
        "titulo": f"Editar intervención · {persona.apellido_1}, {persona.nombre}",
        "intervencion": intervencion,
    })


@login_required
def crear_valoracion(request, persona_id):
    persona = get_object_or_404(PersonaAtendida, pk=persona_id)
    if request.method == "POST":
        form = ValoracionForm(request.POST, persona=persona)
        if form.is_valid():
            form.save()
            messages.success(request, "Valoración registrada.")
            return redirect("personas:detalle", persona_id=persona.id)
    else:
        form = ValoracionForm(persona=persona, initial={
            "persona": persona, "fecha": timezone.localdate(),
        })
    return render(request, "intervenciones/valoracion_form.html", {
        "form": form, "persona": persona,
        "titulo": f"Nueva valoración · {persona.apellido_1}, {persona.nombre}",
    })

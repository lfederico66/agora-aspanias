"""Vistas de personas atendidas — Fase 2 M1.1.

La pieza central es ``detalle_persona``: una ficha con 5 pestañas (Resumen,
Datos personales, Información médica, Familiares, Medicación) implementada
con Alpine.js en el lado cliente. Los datos se cargan en una sola consulta
con select_related/prefetch_related para evitar N+1.
"""
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render

from core.permissions import tiene_acceso_clinico, tiene_acceso_juridico

from .forms import PersonaAtendidaForm
from .models import (
    Alergia,
    AvisoCambioProfesional,
    Cama,
    Centro,
    CertificadoDiscapacidad,
    EnfermedadCronica,
    Habitacion,
    MedidaAntropometrica,
    Modulo,
    OcupacionCama,
    PautaMedicacion,
    PersonaAtendida,
    ProblemaSalud,
    ReconocimientoDependencia,
    Vacuna,
    VinculoPersonaContacto,
)


@login_required
def lista_personas(request):
    """Listado con búsqueda HTMX por nombre, código o DNI."""
    q = (request.GET.get("q") or "").strip()
    qs = (
        PersonaAtendida.objects
        .select_related("centro_referencia", "gestor_caso", "persona_referencia")
        .filter(fecha_baja__isnull=True)
        .order_by("apellido_1", "apellido_2", "nombre")
    )
    if q:
        # Búsqueda case-insensitive en nombre completo o código
        qs = qs.filter(apellido_1__icontains=q) | qs.filter(
            nombre__icontains=q
        ) | qs.filter(codigo_interno__icontains=q)
        qs = qs.distinct()

    template = "personas/_lista_filas.html" if request.htmx else "personas/lista.html"
    return render(request, template, {"personas": qs, "q": q})


@login_required
def detalle_persona(request, persona_id):
    """Ficha completa con 5 pestañas.

    Una sola query con todos los related para evitar N+1. Los modelos
    de v0.11 (clínico, familia, medicación) y v0.12 (alojamiento) se
    cargan en bloque y se filtran en el template.
    """
    persona = get_object_or_404(
        PersonaAtendida.objects
        .select_related(
            "centro_referencia",
            "gestor_caso", "gestor_caso__rol_principal",
            "persona_referencia", "persona_referencia__rol_principal",
        )
        .prefetch_related(
            "perfiles_di",
            "perfiles_mayor",
            "perfiles_insercion",
            "servicios_contratados__centro",
            "servicios_contratados__servicio",
            Prefetch(
                "vinculos_contacto",
                queryset=VinculoPersonaContacto.objects.select_related("contacto"),
            ),
            Prefetch(
                "alergias",
                queryset=Alergia.objects.filter(activa=True).order_by("-gravedad", "sustancia"),
            ),
            Prefetch(
                "enfermedades_cronicas",
                queryset=EnfermedadCronica.objects.filter(en_seguimiento=True),
            ),
            Prefetch(
                "medidas_antropometricas",
                queryset=MedidaAntropometrica.objects.order_by("-fecha")[:6],
            ),
            Prefetch(
                "vacunas",
                queryset=Vacuna.objects.order_by("-fecha"),
            ),
            Prefetch(
                "problemas_salud",
                queryset=ProblemaSalud.objects.exclude(estado="resuelto").order_by("-fecha_apertura"),
            ),
            Prefetch(
                "pautas_medicacion",
                queryset=PautaMedicacion.objects
                    .select_related("medicamento")
                    .order_by("-activa", "-fecha_inicio"),
            ),
            Prefetch(
                "certificados_discapacidad",
                queryset=CertificadoDiscapacidad.objects.filter(vigente=True),
            ),
            Prefetch(
                "reconocimientos_dependencia",
                queryset=ReconocimientoDependencia.objects.filter(vigente=True),
            ),
            Prefetch(
                "ocupaciones_cama",
                queryset=OcupacionCama.objects
                    .select_related(
                        "cama", "cama__habitacion", "cama__habitacion__modulo",
                        "cama__habitacion__centro",
                    )
                    .order_by("-fecha_inicio"),
            ),
        ),
        pk=persona_id,
    )

    # Acceso a la medida de apoyo en OneToOne — try/except por si no existe aún
    try:
        medida_apoyo = persona.medida_apoyo
    except Exception:
        medida_apoyo = None

    # Acceso a la información médica (1-1) y cuidados (1-1)
    info_medica = getattr(persona, "info_medica", None)
    cuidados = getattr(persona, "cuidados_enfermeria", None)

    # Última valoración (BVD, ICAP, etc.)
    valoraciones_recientes = persona.valoraciones.select_related("aplicado_por").order_by("-fecha")[:5]

    # Ocupación actual de cama (la única vigente)
    ocupacion_actual = next(
        (o for o in persona.ocupaciones_cama.all() if o.fecha_fin is None),
        None,
    )

    # Flags de permisos clínicos/jurídicos — el template los usa para
    # ocultar las pestañas Información médica y Medicación a quien no tiene
    # rol clínico, y para ofuscar intervenciones jurídicas.
    puede_ver_clinica = tiene_acceso_clinico(request.user)
    puede_ver_juridica = tiene_acceso_juridico(request.user)

    # Si el usuario pide directamente una pestaña clínica sin permisos,
    # redirigimos al resumen.
    tab_inicial = request.GET.get("tab", "resumen")
    if tab_inicial in ("medica", "medicacion") and not puede_ver_clinica:
        tab_inicial = "resumen"

    contexto = {
        "persona": persona,
        "medida_apoyo": medida_apoyo,
        "info_medica": info_medica if puede_ver_clinica else None,
        "cuidados": cuidados if puede_ver_clinica else None,
        "valoraciones": valoraciones_recientes,
        "ocupacion_actual": ocupacion_actual,
        "tab_inicial": tab_inicial,
        "puede_ver_clinica": puede_ver_clinica,
        "puede_ver_juridica": puede_ver_juridica,
    }
    return render(request, "personas/detalle.html", contexto)


# ---------------------------------------------------------------------------
# Alta / edición de la ficha base (resto se edita por bloques HTMX)
# ---------------------------------------------------------------------------


def _generar_codigo_interno(centro, fecha_alta) -> str:
    """Genera CENTRO-AAAA-NNNNN buscando el siguiente número libre."""
    anio = (fecha_alta or date.today()).year
    prefijo = f"{centro.codigo}-{anio}-"
    qs = PersonaAtendida.objects.filter(codigo_interno__startswith=prefijo)
    siguiente = 1
    for c in qs.values_list("codigo_interno", flat=True):
        try:
            n = int(c.rsplit("-", 1)[-1])
            siguiente = max(siguiente, n + 1)
        except (ValueError, IndexError):
            continue
    return f"{prefijo}{siguiente:05d}"


@login_required
@transaction.atomic
def crear_persona(request):
    if request.method == "POST":
        form = PersonaAtendidaForm(request.POST)
        if form.is_valid():
            persona = form.save(commit=False)
            if not persona.codigo_interno:
                persona.codigo_interno = _generar_codigo_interno(
                    persona.centro_referencia, persona.fecha_alta,
                )
            persona.save()
            messages.success(request, f"Persona atendida creada: {persona}.")
            return redirect("personas:detalle", persona_id=persona.id)
    else:
        form = PersonaAtendidaForm(initial={"fecha_alta": date.today(), "nacionalidad": "ES"})
    return render(request, "personas/form.html", {
        "form": form,
        "modo": "crear",
        "titulo": "Nueva persona atendida",
    })


@login_required
@transaction.atomic
def editar_persona(request, persona_id):
    persona = get_object_or_404(PersonaAtendida, pk=persona_id)
    if request.method == "POST":
        form = PersonaAtendidaForm(request.POST, instance=persona)
        if form.is_valid():
            form.save()
            messages.success(request, "Ficha actualizada.")
            return redirect("personas:detalle", persona_id=persona.id)
    else:
        form = PersonaAtendidaForm(instance=persona)
    return render(request, "personas/form.html", {
        "form": form,
        "persona": persona,
        "modo": "editar",
        "titulo": f"Editar ficha · {persona.apellido_1}, {persona.nombre}",
    })


# ---------------------------------------------------------------------------
# Bandeja de avisos a Dirección (Protocolo Aspanias — cambios de gestora)
# ---------------------------------------------------------------------------


@login_required
def avisos_cambio_profesional(request):
    """Bandeja de Dirección con avisos pendientes y recientes.

    Protocolo Aspanias §9 — Notificación a Dirección de cambios de Gestor/a de
    Caso o Persona de Referencia. Permite filtrar por estado y muestra KPIs.
    """
    estado = request.GET.get("estado", "pendiente")
    qs = AvisoCambioProfesional.objects.select_related(
        "persona", "profesional_anterior", "profesional_nuevo", "resuelto_por",
    )
    if estado == "todos":
        avisos = qs
    else:
        avisos = qs.filter(estado=estado)

    # KPIs por estado (todos los avisos, no solo los filtrados)
    kpis = {
        "pendiente": qs.filter(estado=AvisoCambioProfesional.Estado.PENDIENTE).count(),
        "en_tratamiento": qs.filter(estado=AvisoCambioProfesional.Estado.EN_TRATAMIENTO).count(),
        "resuelto_mes": qs.filter(
            estado=AvisoCambioProfesional.Estado.RESUELTO,
            resuelto_at__gte=date.today().replace(day=1),
        ).count(),
        "total": qs.count(),
    }

    return render(request, "personas/avisos_cambio_profesional.html", {
        "avisos": avisos,
        "estado": estado,
        "kpis": kpis,
    })


@login_required
def resolver_aviso(request, aviso_id):
    """Marca un aviso como resuelto o descartado (acción HTMX desde la tarjeta).

    Espera POST con ``accion`` (resuelto | descartado | en_tratamiento) y
    opcionalmente ``notas``. Devuelve la tarjeta actualizada para sustituir
    in-place vía hx-swap="outerHTML".
    """
    aviso = get_object_or_404(AvisoCambioProfesional, pk=aviso_id)
    if request.method != "POST":
        return redirect("personas:avisos_cambio_profesional")

    accion = request.POST.get("accion", "")
    notas = request.POST.get("notas", "").strip()
    from django.utils import timezone as _tz

    estados_validos = {
        "resuelto": AvisoCambioProfesional.Estado.RESUELTO,
        "descartado": AvisoCambioProfesional.Estado.DESCARTADO,
        "en_tratamiento": AvisoCambioProfesional.Estado.EN_TRATAMIENTO,
    }
    if accion not in estados_validos:
        messages.error(request, "Acción no reconocida.")
        return redirect("personas:avisos_cambio_profesional")

    with transaction.atomic():
        aviso.estado = estados_validos[accion]
        if accion in ("resuelto", "descartado"):
            aviso.resuelto_at = _tz.now()
            aviso.resuelto_por = request.user if request.user.is_authenticated else None
        if notas:
            aviso.notas_resolucion = notas
        aviso.save()

    if request.headers.get("HX-Request"):
        # Devolver tarjeta individual (HTMX swap)
        return render(request, "personas/_aviso_tarjeta.html", {"a": aviso})

    messages.success(request, f"Aviso marcado como {aviso.get_estado_display().lower()}.")
    return redirect("personas:avisos_cambio_profesional")


# ---------------------------------------------------------------------------
# Mapa de ocupación — Fase 2 M1.7
# ---------------------------------------------------------------------------


@login_required
def mapa_ocupacion(request, centro_codigo=None):
    """Cuadrícula visual de módulos → habitaciones → camas de un centro.

    Si no se pasa centro, redirige al primer centro residencial activo.
    Selección de cama mediante Alpine.js en el lado cliente (panel lateral).
    """
    centros_residenciales = Centro.objects.filter(activo=True).order_by("nombre")

    if centro_codigo:
        centro = get_object_or_404(Centro, codigo=centro_codigo)
    else:
        # Sin parámetro: el primer centro con camas activas
        centro = (
            Centro.objects
            .filter(activo=True, habitaciones__camas__isnull=False)
            .distinct()
            .order_by("nombre")
            .first()
        )
        if not centro:
            return render(request, "personas/mapa_ocupacion.html", {
                "centro": None,
                "centros": centros_residenciales,
                "modulos": [],
                "kpis": {},
            })

    # Carga eficiente: módulos → habitaciones → camas → ocupación vigente
    ocupaciones_vigentes_prefetch = Prefetch(
        "ocupaciones",
        queryset=OcupacionCama.objects.filter(fecha_fin__isnull=True)
            .select_related("persona"),
        to_attr="ocupacion_vigente_lista",
    )
    camas_prefetch = Prefetch(
        "camas",
        queryset=Cama.objects.prefetch_related(ocupaciones_vigentes_prefetch).order_by("identificador"),
    )

    modulos = list(
        Modulo.objects
        .filter(centro=centro, activo=True)
        .prefetch_related(
            Prefetch(
                "habitaciones",
                queryset=Habitacion.objects
                    .filter(activa=True)
                    .prefetch_related(camas_prefetch)
                    .order_by("numero"),
            ),
        )
        .order_by("nombre")
    )
    # Habitaciones sin módulo (viviendas pequeñas)
    habitaciones_sueltas = list(
        Habitacion.objects
        .filter(centro=centro, modulo__isnull=True, activa=True)
        .prefetch_related(camas_prefetch)
        .order_by("numero")
    )

    # KPIs de ocupación del centro
    kpis = {
        "plazas_totales": centro.plazas_totales,
        "plazas_ocupadas": centro.plazas_ocupadas,
        "plazas_libres": centro.plazas_libres,
        "porcentaje_ocupacion": centro.porcentaje_ocupacion,
        "habitaciones_pmr": Habitacion.objects.filter(
            centro=centro, activa=True, adaptada_movilidad_reducida=True,
        ).count(),
        "habitaciones_total": Habitacion.objects.filter(centro=centro, activa=True).count(),
    }

    # Camas libres ahora (para sugerir asignación)
    camas_libres = (
        Cama.objects
        .filter(
            habitacion__centro=centro,
            habitacion__activa=True,
            activa=True,
        )
        .exclude(ocupaciones__fecha_fin__isnull=True)
        .select_related("habitacion__modulo")
        .order_by("habitacion__modulo__nombre", "habitacion__numero", "identificador")
    )

    # Movimientos recientes (últimas 5 ocupaciones que han empezado o terminado)
    movimientos = (
        OcupacionCama.objects
        .filter(cama__habitacion__centro=centro)
        .select_related("persona", "cama__habitacion__modulo")
        .order_by("-created_at")[:6]
    )

    return render(request, "personas/mapa_ocupacion.html", {
        "centro": centro,
        "centros": centros_residenciales,
        "modulos": modulos,
        "habitaciones_sueltas": habitaciones_sueltas,
        "kpis": kpis,
        "camas_libres": camas_libres,
        "movimientos": movimientos,
    })


# ---------------------------------------------------------------------------
# Cuidados de enfermería — bloque HTMX dentro de la pestaña Información médica
# (P1 pre-piloto · petición Dirección Fuentecillas). Solo rol clínico.
# ---------------------------------------------------------------------------


@login_required
@transaction.atomic
def cuidados_enfermeria(request, persona_id):
    """GET: fragmento lectura (o formulario con ?modo=editar). POST: guarda.

    La lectura y la escritura quedan en la bitácora vía middleware; el
    permiso clínico se comprueba aquí porque el fragmento viaja solo.
    """
    from django.core.exceptions import PermissionDenied

    from .forms import CuidadoEnfermeriaForm
    from .models import CuidadoEnfermeria

    if not tiene_acceso_clinico(request.user):
        raise PermissionDenied("Se requiere rol clínico para los cuidados de enfermería.")

    persona = get_object_or_404(PersonaAtendida, pk=persona_id)
    cuidados = CuidadoEnfermeria.objects.filter(persona=persona).first()

    if request.method == "POST":
        form = CuidadoEnfermeriaForm(request.POST, instance=cuidados)
        if form.is_valid():
            objeto = form.save(commit=False)
            objeto.persona = persona
            objeto.updated_by = request.user
            objeto.save()
            return render(request, "personas/_cuidados_enfermeria.html", {
                "persona": persona, "cuidados": objeto,
                "puede_ver_clinica": True, "guardado": True,
            })
    elif request.GET.get("modo") == "editar":
        form = CuidadoEnfermeriaForm(instance=cuidados)
    else:
        return render(request, "personas/_cuidados_enfermeria.html", {
            "persona": persona, "cuidados": cuidados, "puede_ver_clinica": True,
        })

    return render(request, "personas/_cuidados_enfermeria_form.html", {
        "persona": persona, "form": form,
    })


def _tz_now():
    from django.utils import timezone
    return timezone.now()


# ---------------------------------------------------------------------------
# Ficha básica de salud — documento imprimible para urgencias/hospital
# (P1 pre-piloto · petición Dirección Fuentecillas). Solo rol clínico.
# Exportación con motivo obligatorio registrado en bitácora.
# ---------------------------------------------------------------------------


@login_required
def ficha_salud(request, persona_id):
    from django.core.exceptions import PermissionDenied

    from core.models import RegistroAcceso

    if not tiene_acceso_clinico(request.user):
        raise PermissionDenied("Se requiere rol clínico para la ficha básica de salud.")

    persona = get_object_or_404(
        PersonaAtendida.objects
        .select_related("centro_referencia", "gestor_caso", "persona_referencia")
        .prefetch_related(
            Prefetch("alergias", queryset=Alergia.objects.filter(activa=True)
                     .order_by("-gravedad", "sustancia")),
            "enfermedades_cronicas",
            Prefetch("pautas_medicacion",
                     queryset=PautaMedicacion.objects.filter(activa=True)
                     .select_related("medicamento").order_by("medicamento__nombre_comercial")),
            Prefetch("vinculos_contacto",
                     queryset=VinculoPersonaContacto.objects.filter(es_emergencia=True)
                     .select_related("contacto").order_by("orden_emergencia")),
            "perfiles_mayor", "perfiles_di", "ocupaciones_cama__cama__habitacion__modulo",
        ),
        pk=persona_id,
    )

    motivo = (request.POST.get("motivo") or "").strip()
    motivo_otro = (request.POST.get("motivo_otro") or "").strip()
    if motivo == "Otro" and motivo_otro:
        motivo = f"Otro: {motivo_otro}"

    if request.method != "POST" or not motivo:
        return render(request, "personas/ficha_salud_motivo.html", {"persona": persona})

    RegistroAcceso.objects.create(
        profesional=request.user,
        persona_consultada_id=persona.id,
        accion=RegistroAcceso.Accion.EXPORTAR,
        entidad="FichaBasicaSalud",
        ruta=request.path,
        ip=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:512],
        motivo=motivo[:255],
    )

    ocupacion = next((o for o in persona.ocupaciones_cama.all() if o.fecha_fin is None), None)
    contexto = {
        "persona": persona,
        "info_medica": getattr(persona, "info_medica", None),
        "cuidados": getattr(persona, "cuidados_enfermeria", None),
        "medida_apoyo": getattr(persona, "medida_apoyo", None),
        "perfil_mayor": persona.perfiles_mayor.all().first(),
        "perfil_di": persona.perfiles_di.all().first(),
        "ocupacion": ocupacion,
        "motivo": motivo,
        "ahora": _tz_now(),
    }
    return render(request, "personas/ficha_salud.html", contexto)


# ---------------------------------------------------------------------------
# Datos base de la ficha — edición inline por bloque HTMX (P1 pre-piloto)
# ---------------------------------------------------------------------------


@login_required
@transaction.atomic
def editar_datos_base(request, persona_id):
    """GET: bloque lectura (o formulario con ?modo=editar). POST: guarda."""
    from .forms import DatosBaseForm

    persona = get_object_or_404(PersonaAtendida, pk=persona_id)

    if request.method == "POST":
        form = DatosBaseForm(request.POST, instance=persona)
        if form.is_valid():
            form.save()
            return render(request, "personas/_datos_base.html",
                          {"persona": persona, "guardado": True})
    elif request.GET.get("modo") == "editar":
        form = DatosBaseForm(instance=persona)
    else:
        return render(request, "personas/_datos_base.html", {"persona": persona})

    return render(request, "personas/_datos_base_form.html",
                  {"persona": persona, "form": form})

"""Helpers de RBAC: control de acceso por rol y por centro — Fase 2.5.3.

ÁGORA divide el acceso a la información en tres niveles:

1. **Acceso administrativo** (default): TS, Educador/a, Coord., Dirección.
   Ven la ficha base, agenda e intervenciones de confidencialidad normal.
2. **Acceso clínico**: DUE, médico/a, psicólogo/a, fisio. Además ven la
   información médica, alergias, antropometría, vacunas, cuidados, problemas
   de salud y pautas de medicación.
3. **Acceso jurídico**: solo Dirección o personal específicamente habilitado.
   Ve intervenciones con confidencialidad ``rest_juridica`` (sentencias, etc.).

Los roles se identifican por el ``Profesional.rol_principal.codigo``.
"""
from __future__ import annotations

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

# ---------------------------------------------------------------------------
# Catálogo canónico de roles (códigos de personas.Rol)
# ---------------------------------------------------------------------------

ROLES_CON_ACCESO_CLINICO = frozenset({
    "DUE",          # Diplomado/a Universitario/a en Enfermería
    "MEDICO", "MED",
    "PSI", "PSICOLOGO", "PSIQUIATRA",
    "FISIO",        # Fisioterapeuta (acceso parcial — antropometría)
})

ROLES_CON_ACCESO_JURIDICO = frozenset({
    "DIRECCION",
    "GERENCIA",
    "TS_JURIDICO",  # Trabajador/a social con habilitación jurídica
})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_profesional(user):
    """Devuelve el Profesional vinculado al user o None."""
    if not user or not user.is_authenticated:
        return None
    return getattr(user, "profesional", None)


def tiene_acceso_clinico(user) -> bool:
    """True si el usuario puede ver datos médicos (categoría especial RGPD 9)."""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    prof = _get_profesional(user)
    if not prof or not prof.activo or not prof.rol_principal:
        return False
    return prof.rol_principal.codigo.upper() in ROLES_CON_ACCESO_CLINICO


def tiene_acceso_juridico(user) -> bool:
    """True si el usuario puede ver intervenciones jurídicas restringidas."""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    prof = _get_profesional(user)
    if not prof or not prof.activo or not prof.rol_principal:
        return False
    return prof.rol_principal.codigo.upper() in ROLES_CON_ACCESO_JURIDICO


def puede_ver_intervencion(user, intervencion) -> bool:
    """¿Puede este usuario ver esta intervención según su confidencialidad?"""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    confidencialidad = getattr(intervencion, "confidencialidad", "normal")
    if confidencialidad == "normal":
        return True
    if confidencialidad == "rest_clinica":
        return tiene_acceso_clinico(user)
    if confidencialidad == "rest_juridica":
        return tiene_acceso_juridico(user)
    return False


def puede_ver_persona(usuario, persona) -> bool:
    """Devuelve True si el usuario puede ver la ficha de esta persona.

    Regla v0.1: el profesional debe tener acceso al centro de referencia de la
    persona, o ser superusuario, o pertenecer al grupo ``acceso_global``.
    """
    if not usuario or not usuario.is_authenticated:
        return False
    if usuario.is_superuser:
        return True
    prof = _get_profesional(usuario)
    if prof and persona:
        if prof.centros_acceso.filter(pk=persona.centro_referencia_id).exists():
            return True
    return usuario.groups.filter(name="acceso_global").exists()


# ---------------------------------------------------------------------------
# Decoradores para vistas
# ---------------------------------------------------------------------------


def requires_acceso_clinico(view_func):
    """Decorador para vistas que requieren acceso clínico."""

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not tiene_acceso_clinico(request.user):
            raise PermissionDenied(
                "Esta sección contiene datos de salud. Solo accesible para "
                "personal con rol clínico (DUE, médico/a, psicólogo/a)."
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def requires_acceso_juridico(view_func):
    """Decorador para vistas que requieren acceso jurídico."""

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not tiene_acceso_juridico(request.user):
            raise PermissionDenied(
                "Esta sección contiene información jurídica restringida. "
                "Solo accesible para Dirección o personal habilitado."
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def requiere_acceso_persona(view_func):
    """Decorador que aborta con 403 si el profesional no puede ver la persona.

    Espera que la vista reciba ``persona`` como kwarg (instancia)
    o que la vista resuelva ``request.persona`` previamente.
    """

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        persona = kwargs.get("persona") or getattr(request, "persona", None)
        if not puede_ver_persona(request.user, persona):
            raise PermissionDenied("Sin permiso para acceder a esta ficha.")
        return view_func(request, *args, **kwargs)

    return _wrapped

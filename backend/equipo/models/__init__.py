"""App `equipo` — módulo asistencial RRHH de ÁGORA.

Capa operativa para gestión de plantilla, vacaciones, turnos y calendarios
laborales del Grupo Social Aspanias. Frontera documentada con SIGPER y EQUIPO
en `docs/modelo-datos/decisiones/05_modulo_equipo_solapamiento.md`.
"""
from .calendario import CalendarioLaboral
from .campos_laborales import CamposLaboralesProfesional
from .patrones import AsignacionPatron, PatronTurno
from .turnos import Turno
from .vacaciones import Vacacion

__all__ = [
    "CalendarioLaboral",
    "CamposLaboralesProfesional",
    "AsignacionPatron",
    "PatronTurno",
    "Turno",
    "Vacacion",
]

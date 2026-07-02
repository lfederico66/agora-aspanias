"""Paquete models de la app personas.

Estructura modular tras el split de junio 2026 (deuda técnica D1 del análisis).
Cada archivo agrupa modelos por tema. El re-export aquí mantiene compatibilidad
con `from personas.models import PersonaAtendida` y similares.

Si se añade un modelo nuevo, hay que:
1. Añadirlo al archivo temático correspondiente
2. Re-exportarlo aquí
"""
from .alojamiento import (
    Cama,
    Habitacion,
    Modulo,
    OcupacionCama,
)
from .apoyo_y_avisos import (
    AvisoCambioProfesional,
    FiguraDeApoyo,
    MedidaDeApoyo,
)
from .clinico import (
    Alergia,
    CuidadoEnfermeria,
    EnfermedadCronica,
    InformacionMedica,
    MedidaAntropometrica,
    ProblemaSalud,
    Vacuna,
)
from .contactos_familia import (
    NucleoFamiliar,
    PersonaContacto,
    VinculoPersonaContacto,
)
from .discapacidad import (
    CertificadoDiscapacidad,
    ReconocimientoDependencia,
)
from .medicacion import (
    Medicamento,
    PautaMedicacion,
)
from .organizacion import (
    Centro,
    Profesional,
    Rol,
    Servicio,
)
from .persona_atendida import (
    PerfilDI,
    PerfilInsercion,
    PerfilMayor,
    PersonaAtendida,
    ServicioContratado,
)

__all__ = [
    "Centro",
    "Servicio",
    "Rol",
    "Profesional",
    "PersonaAtendida",
    "PerfilDI",
    "PerfilMayor",
    "PerfilInsercion",
    "ServicioContratado",
    "PersonaContacto",
    "VinculoPersonaContacto",
    "NucleoFamiliar",
    "MedidaDeApoyo",
    "FiguraDeApoyo",
    "AvisoCambioProfesional",
    "CertificadoDiscapacidad",
    "ReconocimientoDependencia",
    "InformacionMedica",
    "Alergia",
    "EnfermedadCronica",
    "MedidaAntropometrica",
    "Vacuna",
    "CuidadoEnfermeria",
    "ProblemaSalud",
    "Medicamento",
    "PautaMedicacion",
    "Modulo",
    "Habitacion",
    "Cama",
    "OcupacionCama",
]

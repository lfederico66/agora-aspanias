"""Paquete models de la app pia (Plan Individual de Atención).

Estructura modular tras el split de junio 2026 (deuda técnica D9).
"""
from .algo_sobre_mi import (
    AlgoSobreMi,
    SeccionAlgoSobreMi,
)
from .apoyos_y_dimensiones import (
    DimensionCalidadVida,
    EntradaPlanApoyo,
    PlanDeApoyo,
)
from .constantes import (
    CLAVES_RELACION_HISTORIA_VIDA,
    DIMENSIONES_CDV_SCHALOCK,
    PREGUNTAS_HISTORIA_VIDA,
    SECCIONES_ALGO_SOBRE_MI,
)
from .historia_de_vida import (
    HistoriaDeVida,
    RespuestaHistoriaVida,
)
from .objetivos import (
    CambioSignificativo,
    Objetivo,
    RevisionObjetivo,
)
from .plan_de_vida import (
    DocumentoPlanDeVida,
    PlanDeVida,
)
from .proyecto_de_vida import (
    ProyectoDeVida,
)

__all__ = [
    "PlanDeVida",
    "DocumentoPlanDeVida",
    "Objetivo",
    "RevisionObjetivo",
    "CambioSignificativo",
    "HistoriaDeVida",
    "RespuestaHistoriaVida",
    "AlgoSobreMi",
    "SeccionAlgoSobreMi",
    "DimensionCalidadVida",
    "PlanDeApoyo",
    "EntradaPlanApoyo",
    "ProyectoDeVida",
]

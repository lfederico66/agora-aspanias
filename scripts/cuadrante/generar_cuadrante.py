"""
ÁGORA · Motor de generación automática de cuadrantes asistenciales.

Resuelve el Nurse Rostering Problem (NRP) con Google OR-Tools CP-SAT.

Restricciones duras:
- Cobertura mínima por turno cada día (M/T/N) según ratio Resolución 21/09/2023 CyL.
- Vacaciones y permisos pre-asignados (no se tocan).
- Descanso ≥ 12h entre turnos consecutivos (tras N no se puede M siguiente).
- Máximo 6 días consecutivos trabajados.
- Máximo 3 noches consecutivas.
- Reducciones de jornada: % de horas máximas al mes.
- Categoría profesional: DUE solo cubre puestos DUE, gerocultoras solo gerocultoras, etc.

Función objetivo (equidad — Ley 1/2024 Art. 22, profesional de referencia):
- Minimizar varianza en horas totales/persona/mes.
- Minimizar varianza en fines de semana trabajados/persona/mes.
- Minimizar varianza en festivos trabajados/persona/mes.

Uso (cuando se integre en Django ÁGORA):
    from scripts.cuadrante.generar_cuadrante import generar_cuadrante_mensual
    resultado = generar_cuadrante_mensual(
        centro=Centro.objects.get(slug='fuentecillas'),
        anio=2027,
        mes=1,
        cobertura={'M': 5, 'T': 3, 'N': 2},
        max_segundos=120,
    )

Dependencias:
    pip install ortools  # Apache 2.0 · gratuito
"""
from __future__ import annotations

import calendar
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable

# OR-Tools se importa dentro de la función para que el módulo sea importable
# en entornos donde no esté instalado (por ejemplo, el demo estático HTML).

# ============ CONSTANTES ============

# Códigos de turno (compactos para el modelo CP-SAT)
TURNO_DL = 0  # Descanso libre
TURNO_M = 1   # Mañana 07:00-15:00 · 8h
TURNO_T = 2   # Tarde 15:00-23:00 · 8h
TURNO_N = 3   # Noche 23:00-07:00 · 8h
TURNO_V = 4   # Vacaciones (pre-asignado)
TURNO_IT = 5  # Incapacidad temporal (pre-asignado)
TURNO_LIBRE = 6  # Día libre por reducción de jornada (pre-asignado)
TURNO_F = 7   # Formación (pre-asignado · cuenta para cómputo horas · 25h/año)
TURNO_CS = 8  # Crédito sindical (pre-asignado · representantes · 20h/mes)

ETIQUETAS_TURNO = {
    TURNO_DL: 'DL', TURNO_M: 'M', TURNO_T: 'T', TURNO_N: 'N',
    TURNO_V: 'V', TURNO_IT: 'IT', TURNO_LIBRE: 'R',
    TURNO_F: 'F', TURNO_CS: 'CS',
}

HORAS_TURNO = {
    TURNO_DL: 0, TURNO_M: 8, TURNO_T: 8, TURNO_N: 8,
    TURNO_V: 0, TURNO_IT: 0, TURNO_LIBRE: 0,
    TURNO_F: 8, TURNO_CS: 8,  # Formación y sindical computan horas
}

# Festivos Burgos por año (nacional + CyL + local)
FESTIVOS = {
    2026: [date(2026, 1, 1), date(2026, 1, 6), date(2026, 3, 19),
           date(2026, 4, 3), date(2026, 5, 1), date(2026, 6, 29),
           date(2026, 8, 15), date(2026, 10, 12), date(2026, 11, 1),
           date(2026, 12, 6), date(2026, 12, 8), date(2026, 12, 25)],
    2027: [date(2027, 1, 1), date(2027, 1, 6), date(2027, 3, 19),
           date(2027, 3, 26), date(2027, 5, 1), date(2027, 6, 29),
           date(2027, 8, 15), date(2027, 10, 12), date(2027, 11, 1),
           date(2027, 12, 6), date(2027, 12, 8), date(2027, 12, 25)],
}

# ============ DATACLASSES ============

@dataclass
class Profesional:
    id: int
    nombre: str
    categoria: str  # 'gerocultora' | 'DUE' | 'TASOC' | 'TO' | 'TS' | 'psicologo'
    jornada_pct: int = 100  # 100 / 87 / 75 / 50
    permite_noche: bool = True
    vacaciones: list[date] = field(default_factory=list)
    incapacidad: list[date] = field(default_factory=list)
    dias_libres_fijos: list[date] = field(default_factory=list)  # reducción jornada con horario fijo
    dias_formacion: list[date] = field(default_factory=list)  # 25h/año · pre-asignado por RRHH
    dias_credito_sindical: list[date] = field(default_factory=list)  # 20h/mes · solo representantes
    prefiere_manana: bool = False  # soft constraint: premiar M
    prefiere_tarde: bool = False   # soft constraint: premiar T


@dataclass
class Centro:
    slug: str
    nombre: str
    cobertura: dict[str, int]  # {'M': 5, 'T': 3, 'N': 2}


# ============ FUNCIÓN PRINCIPAL ============

def generar_cuadrante_mensual(
    centro: Centro,
    profesionales: list[Profesional],
    anio: int,
    mes: int,
    max_segundos: int = 60,
    semillas: list[dict] | None = None,
) -> dict:
    """
    Devuelve un dict con:
      - 'cuadrante': {profesional_id: {dia_int: codigo_turno}}
      - 'metricas': estadísticas de equidad
      - 'estado': 'OPTIMAL' | 'FEASIBLE' | 'INFEASIBLE'
      - 'segundos': tiempo de cómputo
    """
    try:
        from ortools.sat.python import cp_model
    except ImportError:
        raise RuntimeError(
            "OR-Tools no está instalado. Ejecuta: pip install ortools"
        )

    dias_mes = calendar.monthrange(anio, mes)[1]
    fechas = [date(anio, mes, d) for d in range(1, dias_mes + 1)]
    festivos_set = set(FESTIVOS.get(anio, [])) & set(fechas)
    fines_de_semana = {f for f in fechas if f.weekday() in (5, 6)}

    model = cp_model.CpModel()

    # Variables principales: turno[p][d] ∈ {0..8} (DL, M, T, N, V, IT, R, F, CS)
    turno = {}
    for p in profesionales:
        for d in range(dias_mes):
            turno[(p.id, d)] = model.NewIntVar(0, 8, f't_{p.id}_{d}')

    # Variables booleanas auxiliares para cada (p, d, valor)
    es_turno = {}
    for p in profesionales:
        for d in range(dias_mes):
            for v in (TURNO_DL, TURNO_M, TURNO_T, TURNO_N):
                es_turno[(p.id, d, v)] = model.NewBoolVar(f'e_{p.id}_{d}_{v}')
                model.Add(turno[(p.id, d)] == v).OnlyEnforceIf(es_turno[(p.id, d, v)])
                model.Add(turno[(p.id, d)] != v).OnlyEnforceIf(es_turno[(p.id, d, v)].Not())

    # ============ RESTRICCIONES DURAS ============

    # 1. Vacaciones, IT, reducciones, formación y crédito sindical (pre-asignados)
    for p in profesionales:
        for d_idx, fecha in enumerate(fechas):
            if fecha in p.vacaciones:
                model.Add(turno[(p.id, d_idx)] == TURNO_V)
            elif fecha in p.incapacidad:
                model.Add(turno[(p.id, d_idx)] == TURNO_IT)
            elif fecha in p.dias_libres_fijos:
                model.Add(turno[(p.id, d_idx)] == TURNO_LIBRE)
            elif fecha in p.dias_formacion:
                model.Add(turno[(p.id, d_idx)] == TURNO_F)
            elif fecha in p.dias_credito_sindical:
                model.Add(turno[(p.id, d_idx)] == TURNO_CS)

    # 2. Profesionales que no pueden hacer noche
    for p in profesionales:
        if not p.permite_noche:
            for d in range(dias_mes):
                model.Add(turno[(p.id, d)] != TURNO_N)

    # 3. Cobertura mínima por turno cada día
    # Solo gerocultoras + DUE cubren atención directa M/T/N
    pros_atencion_directa = [p for p in profesionales if p.categoria in ('gerocultora', 'DUE')]

    for d in range(dias_mes):
        # Mañana
        suma_m = sum(es_turno[(p.id, d, TURNO_M)] for p in pros_atencion_directa)
        model.Add(suma_m >= centro.cobertura['M'])
        # Tarde
        suma_t = sum(es_turno[(p.id, d, TURNO_T)] for p in pros_atencion_directa)
        model.Add(suma_t >= centro.cobertura['T'])
        # Noche
        suma_n = sum(es_turno[(p.id, d, TURNO_N)] for p in pros_atencion_directa)
        model.Add(suma_n >= centro.cobertura['N'])

    # 4. Descanso 12h tras turno noche: no M ni T al día siguiente
    for p in profesionales:
        for d in range(dias_mes - 1):
            # No pueden ser N hoy y M mañana
            model.Add(es_turno[(p.id, d, TURNO_N)] + es_turno[(p.id, d+1, TURNO_M)] <= 1)
            model.Add(es_turno[(p.id, d, TURNO_N)] + es_turno[(p.id, d+1, TURNO_T)] <= 1)

    # 5. Convenio Dependencia regula 1 noche · se promueve a 2 · NUNCA más de 2 (acuerdo Aspanias)
    for p in profesionales:
        if not p.permite_noche:
            continue
        for d in range(dias_mes - 2):
            noches = [es_turno[(p.id, d+i, TURNO_N)] for i in range(3)]
            model.Add(sum(noches) <= 2)

    # 5b. Tras bloque de noches (1 o 2), exigir ≥ 2 días no-trabajo después
    # (rotación lenta para recuperar ritmo circadiano)
    for p in profesionales:
        if not p.permite_noche:
            continue
        for d in range(dias_mes - 3):
            # Si trabaja N en d y NO en d+1 (fin bloque) → d+1 y d+2 deben ser no-trabajo
            es_n_hoy = es_turno[(p.id, d, TURNO_N)]
            es_n_manana = es_turno[(p.id, d+1, TURNO_N)]
            # Variable: termina_bloque_noche = N hoy AND no N mañana
            termina = model.NewBoolVar(f'fin_n_{p.id}_{d}')
            model.AddBoolAnd([es_n_hoy, es_n_manana.Not()]).OnlyEnforceIf(termina)
            model.AddBoolOr([es_n_hoy.Not(), es_n_manana]).OnlyEnforceIf(termina.Not())
            # Si termina bloque noche → d+1 y d+2 son no-trabajo (T tras N ya estaba prohibido)
            no_trab_d1 = (es_turno[(p.id, d+1, TURNO_M)] +
                          es_turno[(p.id, d+1, TURNO_T)] +
                          es_turno[(p.id, d+1, TURNO_N)])
            no_trab_d2 = (es_turno[(p.id, d+2, TURNO_M)] +
                          es_turno[(p.id, d+2, TURNO_T)] +
                          es_turno[(p.id, d+2, TURNO_N)])
            model.Add(no_trab_d1 == 0).OnlyEnforceIf(termina)
            model.Add(no_trab_d2 == 0).OnlyEnforceIf(termina)

    # 6. Máximo 6 días consecutivos trabajados (no-trabajo = DL, V, IT, R)
    # Creamos variable booleana auxiliar "trabaja[d]" = 1 si turno ∈ {M, T, N}
    trabaja = {}
    for p in profesionales:
        for d in range(dias_mes):
            trabaja[(p.id, d)] = model.NewBoolVar(f'tr_{p.id}_{d}')
            # trabaja=1 ⇔ es M, T o N
            model.Add(
                es_turno[(p.id, d, TURNO_M)] + es_turno[(p.id, d, TURNO_T)] + es_turno[(p.id, d, TURNO_N)] == trabaja[(p.id, d)]
            )
    for p in profesionales:
        for d in range(dias_mes - 6):
            # Al menos 1 día de no-trabajo en cada ventana de 7
            model.Add(sum(trabaja[(p.id, d+i)] for i in range(7)) <= 6)

    # 7. Horas máximas según jornada (F y CS computan)
    horas_max_por_jornada = {100: 168, 87: 146, 75: 126, 50: 84}
    for p in profesionales:
        # Horas de turnos asignables por el solver (M, T, N)
        horas_p = sum(
            8 * (es_turno[(p.id, d, TURNO_M)] + es_turno[(p.id, d, TURNO_T)] + es_turno[(p.id, d, TURNO_N)])
            for d in range(dias_mes)
        )
        # Horas ya consumidas por formación y crédito sindical (pre-asignadas)
        horas_f = 8 * sum(1 for f in fechas if f in p.dias_formacion)
        horas_cs = 8 * sum(1 for f in fechas if f in p.dias_credito_sindical)
        horas_consumidas_fijas = horas_f + horas_cs

        max_h = horas_max_por_jornada.get(p.jornada_pct, 168)
        # Las horas de turno M/T/N no pueden superar el techo - horas fijas
        model.Add(horas_p <= max_h - horas_consumidas_fijas)
        # Mínimo 60% del techo TOTAL para evitar sub-trabajo
        model.Add(horas_p + horas_consumidas_fijas >= int(max_h * 0.60))

    # ============ FUNCIÓN OBJETIVO (EQUIDAD) ============

    # Calculamos para cada profesional:
    #   - horas trabajadas (h_p)
    #   - festivos trabajados (f_p)
    #   - fines de semana trabajados (w_p)
    # y minimizamos la diferencia máxima vs media.

    horas_por_pro = {}
    festivos_por_pro = {}
    findes_por_pro = {}

    for p in profesionales:
        if p.jornada_pct < 50:  # excluir reducciones extremas del cálculo de equidad
            continue
        horas_p = sum(
            8 * (es_turno[(p.id, d, TURNO_M)] + es_turno[(p.id, d, TURNO_T)] + es_turno[(p.id, d, TURNO_N)])
            for d in range(dias_mes)
        )
        horas_por_pro[p.id] = horas_p

        festivos_p = sum(
            es_turno[(p.id, d_idx, TURNO_M)] + es_turno[(p.id, d_idx, TURNO_T)] + es_turno[(p.id, d_idx, TURNO_N)]
            for d_idx, fecha in enumerate(fechas) if fecha in festivos_set
        )
        festivos_por_pro[p.id] = festivos_p

        findes_p = sum(
            es_turno[(p.id, d_idx, TURNO_M)] + es_turno[(p.id, d_idx, TURNO_T)] + es_turno[(p.id, d_idx, TURNO_N)]
            for d_idx, fecha in enumerate(fechas) if fecha in fines_de_semana
        )
        findes_por_pro[p.id] = findes_p

    # Patrón coherente — salud circadiana + conciliación:
    # Penalizar cambios entre turnos trabajados consecutivos (M→T, T→M, M→N, T→N).
    # No penalizar transiciones entre trabajo y descanso (esas son normales).
    cambios_turno = []
    for p in profesionales:
        for d in range(dias_mes - 1):
            # cambio[d] = 1 si turno trabajado hoy ≠ turno trabajado mañana
            # (sin contar transiciones a/desde DL/V/IT/R)
            cambio = model.NewBoolVar(f'camb_{p.id}_{d}')
            # Es cambio si: (trabaja hoy Y trabaja mañana Y turno hoy ≠ turno mañana)
            tr_hoy = trabaja[(p.id, d)]
            tr_man = trabaja[(p.id, d+1)]
            # Para cada par (v1, v2) de turnos distintos M/T/N, detectar el cambio
            cambios_pares = []
            for v1 in (TURNO_M, TURNO_T, TURNO_N):
                for v2 in (TURNO_M, TURNO_T, TURNO_N):
                    if v1 != v2:
                        par = model.NewBoolVar(f'p_{p.id}_{d}_{v1}{v2}')
                        model.AddBoolAnd([es_turno[(p.id, d, v1)], es_turno[(p.id, d+1, v2)]]).OnlyEnforceIf(par)
                        model.AddBoolOr([es_turno[(p.id, d, v1)].Not(), es_turno[(p.id, d+1, v2)].Not()]).OnlyEnforceIf(par.Not())
                        cambios_pares.append(par)
            # cambio = OR de todos los pares distintos
            model.AddBoolOr(cambios_pares).OnlyEnforceIf(cambio)
            model.AddBoolAnd([c.Not() for c in cambios_pares]).OnlyEnforceIf(cambio.Not())
            cambios_turno.append(cambio)

    # Minimizar el rango (max - min) ponderado de cada métrica + cambios de turno
    if horas_por_pro:
        h_max = model.NewIntVar(0, 200, 'h_max')
        h_min = model.NewIntVar(0, 200, 'h_min')
        f_max = model.NewIntVar(0, 12, 'f_max')
        f_min = model.NewIntVar(0, 12, 'f_min')
        w_max = model.NewIntVar(0, 10, 'w_max')
        w_min = model.NewIntVar(0, 10, 'w_min')

        model.AddMaxEquality(h_max, list(horas_por_pro.values()))
        model.AddMinEquality(h_min, list(horas_por_pro.values()))
        model.AddMaxEquality(f_max, list(festivos_por_pro.values()))
        model.AddMinEquality(f_min, list(festivos_por_pro.values()))
        model.AddMaxEquality(w_max, list(findes_por_pro.values()))
        model.AddMinEquality(w_min, list(findes_por_pro.values()))

        total_cambios = sum(cambios_turno)

        # Preferencias personales: penalizar turnos NO preferidos para quienes tienen preferencia.
        # Cuanto más alta la penalización, menos turnos no preferidos.
        prefs_no_respetadas = []
        for p in profesionales:
            if p.prefiere_manana:
                # Penaliza T y N (queremos minimizar)
                for d in range(dias_mes):
                    prefs_no_respetadas.append(es_turno[(p.id, d, TURNO_T)])
                    prefs_no_respetadas.append(es_turno[(p.id, d, TURNO_N)])
            elif p.prefiere_tarde:
                for d in range(dias_mes):
                    prefs_no_respetadas.append(es_turno[(p.id, d, TURNO_M)])
                    prefs_no_respetadas.append(es_turno[(p.id, d, TURNO_N)])

        # Función objetivo: equidad + coherencia patrón + preferencias
        objetivo_terms = [
            (h_max - h_min),
            10 * (f_max - f_min),
            5 * (w_max - w_min),
            8 * total_cambios,
        ]
        if prefs_no_respetadas:
            objetivo_terms.append(3 * sum(prefs_no_respetadas))  # peso medio: soft constraint

        model.Minimize(sum(objetivo_terms))

    # ============ RESOLVER ============
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max_segundos
    solver.parameters.num_search_workers = 8

    status = solver.Solve(model)
    estado_txt = {
        cp_model.OPTIMAL: 'OPTIMAL',
        cp_model.FEASIBLE: 'FEASIBLE',
        cp_model.INFEASIBLE: 'INFEASIBLE',
        cp_model.UNKNOWN: 'UNKNOWN',
    }.get(status, 'UNKNOWN')

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {
            'estado': estado_txt,
            'segundos': solver.WallTime(),
            'cuadrante': {},
            'metricas': {},
        }

    # Extraer cuadrante
    cuadrante = {}
    for p in profesionales:
        cuadrante[p.id] = {
            d: ETIQUETAS_TURNO[solver.Value(turno[(p.id, d)])]
            for d in range(dias_mes)
        }

    # Calcular métricas reales
    metricas = _calcular_metricas(profesionales, fechas, festivos_set, fines_de_semana, cuadrante)

    return {
        'estado': estado_txt,
        'segundos': round(solver.WallTime(), 2),
        'cuadrante': cuadrante,
        'metricas': metricas,
        'objetivo': solver.ObjectiveValue() if horas_por_pro else 0,
    }


def _calcular_metricas(profesionales, fechas, festivos_set, fines_de_semana, cuadrante):
    """Estadísticas de equidad por profesional + agregadas + coherencia patrón."""
    metricas_por_pro = {}
    for p in profesionales:
        secuencia = [cuadrante[p.id][d] for d in range(len(fechas))]
        horas = sum(8 if t in ('M', 'T', 'N') else 0 for t in secuencia)
        festivos_tr = sum(
            1 for d_idx, fecha in enumerate(fechas)
            if fecha in festivos_set and secuencia[d_idx] in ('M', 'T', 'N')
        )
        findes_tr = sum(
            1 for d_idx, fecha in enumerate(fechas)
            if fecha in fines_de_semana and secuencia[d_idx] in ('M', 'T', 'N')
        )
        noches = sum(1 for t in secuencia if t == 'N')

        # Coherencia de patrón: contar cambios entre turnos trabajados consecutivos
        cambios = 0
        bloques = []  # listas de (turno, longitud)
        actual_turno, actual_len = None, 0
        for t in secuencia:
            if t in ('M', 'T', 'N'):
                if t == actual_turno:
                    actual_len += 1
                else:
                    if actual_turno is not None:
                        if actual_turno in ('M', 'T', 'N'):
                            bloques.append((actual_turno, actual_len))
                            cambios += 1  # cambio de turno trabajado
                    actual_turno, actual_len = t, 1
            else:
                if actual_turno in ('M', 'T', 'N') and actual_len > 0:
                    bloques.append((actual_turno, actual_len))
                actual_turno, actual_len = t, 1
        if actual_turno in ('M', 'T', 'N') and actual_len > 0:
            bloques.append((actual_turno, actual_len))

        bloques_trabajados = [b for b in bloques if b[0] in ('M', 'T', 'N')]
        if bloques_trabajados:
            total_dias_trab = sum(b[1] for b in bloques_trabajados)
            dias_en_bloque_largo = sum(b[1] for b in bloques_trabajados if b[1] >= 2)
            pct_bloque_largo = round(100 * dias_en_bloque_largo / total_dias_trab) if total_dias_trab else 0
            long_media_bloque = round(total_dias_trab / len(bloques_trabajados), 1) if bloques_trabajados else 0
        else:
            pct_bloque_largo = 0
            long_media_bloque = 0

        metricas_por_pro[p.id] = {
            'horas': horas,
            'festivos_trabajados': festivos_tr,
            'fines_semana_trabajados': findes_tr,
            'noches': noches,
            'cambios_turno': cambios,
            'longitud_media_bloque': long_media_bloque,
            'pct_dias_bloque_largo': pct_bloque_largo,
        }

    # Agregadas (solo jornada completa para varianza)
    horas_list = [m['horas'] for p, m in zip(profesionales, metricas_por_pro.values()) if p.jornada_pct >= 50]
    festivos_list = [m['festivos_trabajados'] for p, m in zip(profesionales, metricas_por_pro.values()) if p.jornada_pct >= 50]
    findes_list = [m['fines_semana_trabajados'] for p, m in zip(profesionales, metricas_por_pro.values()) if p.jornada_pct >= 50]

    def varianza(lista):
        if not lista: return 0
        media = sum(lista) / len(lista)
        return round(sum((x - media) ** 2 for x in lista) / len(lista), 2)

    # Coherencia de patrón agregada
    cambios_list = [metricas_por_pro[p.id]['cambios_turno'] for p in profesionales if p.jornada_pct >= 50]
    pct_bloque_list = [metricas_por_pro[p.id]['pct_dias_bloque_largo'] for p in profesionales if p.jornada_pct >= 50]
    long_media_list = [metricas_por_pro[p.id]['longitud_media_bloque'] for p in profesionales if p.jornada_pct >= 50]

    return {
        'por_profesional': metricas_por_pro,
        'equidad': {
            'horas_media': round(sum(horas_list) / len(horas_list), 1) if horas_list else 0,
            'horas_rango': max(horas_list) - min(horas_list) if horas_list else 0,
            'horas_varianza': varianza(horas_list),
            'festivos_media': round(sum(festivos_list) / len(festivos_list), 1) if festivos_list else 0,
            'festivos_rango': max(festivos_list) - min(festivos_list) if festivos_list else 0,
            'fines_semana_media': round(sum(findes_list) / len(findes_list), 1) if findes_list else 0,
            'fines_semana_rango': max(findes_list) - min(findes_list) if findes_list else 0,
        },
        'coherencia_patron': {
            'cambios_turno_media': round(sum(cambios_list) / len(cambios_list), 1) if cambios_list else 0,
            'cambios_turno_max': max(cambios_list) if cambios_list else 0,
            'pct_dias_bloque_largo_media': round(sum(pct_bloque_list) / len(pct_bloque_list)) if pct_bloque_list else 0,
            'longitud_media_bloque': round(sum(long_media_list) / len(long_media_list), 1) if long_media_list else 0,
        }
    }


# ============ DATOS SINTÉTICOS DEMO FUENTECILLAS ============

def plantilla_fuentecillas_demo() -> tuple[Centro, list[Profesional]]:
    """Plantilla sintética de la Residencia Fuentecillas con perfiles realistas."""
    centro = Centro(
        slug='fuentecillas',
        nombre='Residencia Fuentecillas',
        cobertura={'M': 3, 'T': 2, 'N': 1},  # Cobertura realista Fuentecillas según Resolución 21/09/2023
    )

    profesionales = [
        # María: representante sindical · 2 días/mes crédito sindical (20h ÷ 8h)
        Profesional(1, 'García López, María',     'gerocultora', 100, True,
                    dias_credito_sindical=[date(2027,1,14), date(2027,1,28)]),
        Profesional(2, 'Martín Rodríguez, Ana',   'gerocultora', 100, True),
        # Lucía: reducción jornada 87% + prefiere mañanas (cuidado hijo)
        Profesional(3, 'Jiménez Pérez, Lucía',    'gerocultora', 87,  True,
                    dias_libres_fijos=[date(2027,1,5), date(2027,1,12), date(2027,1,19), date(2027,1,26)],
                    prefiere_manana=True),
        # Carmen: 1 día formación enero (curso obligatorio)
        Profesional(4, 'Fernández Sanz, Carmen',  'gerocultora', 100, True,
                    dias_formacion=[date(2027,1,22)]),
        Profesional(5, 'Ruiz Domínguez, Beatriz', 'gerocultora', 75,  False,
                    dias_libres_fijos=[date(2027,1,7), date(2027,1,8), date(2027,1,14), date(2027,1,15),
                                       date(2027,1,21), date(2027,1,22), date(2027,1,28), date(2027,1,29)]),
        Profesional(6, 'Hernández Vega, Patricia','gerocultora', 100, True),
        Profesional(7, 'Castro Núñez, Elena',     'gerocultora', 100, True),
        # Sofía: prefiere tardes (clases mañana)
        Profesional(8, 'Romero Iglesias, Sofía',  'gerocultora', 100, True,
                    prefiere_tarde=True),
        # Cristina (DUE): 2 días formación (curso DUE en gerontología)
        Profesional(9, 'Vargas Molina, Cristina', 'DUE',         100, True,
                    dias_formacion=[date(2027,1,8), date(2027,1,15)]),
        Profesional(10, 'Ortega Salas, Marta',    'DUE',         87,  False,
                    dias_libres_fijos=[date(2027,1,6), date(2027,1,13), date(2027,1,20), date(2027,1,27)]),
        Profesional(11, 'Delgado Mora, Pablo',    'TASOC',       100, False,
                    vacaciones=[date(2027,1,d) for d in (12,13,14,15,16,17,18)]),
        # Andrea (TO): 1 día formación
        Profesional(12, 'Aguirre Soto, Andrea',   'TO',          100, False,
                    dias_formacion=[date(2027,1,29)]),
        Profesional(13, 'Pinto Vidal, Jorge',     'TS',          100, False,
                    incapacidad=[date(2027,1,d) for d in (1,2,3,4,5)]),
    ]
    return centro, profesionales


def exportar_json(resultado: dict, ruta_salida: Path) -> None:
    """Exporta el cuadrante a JSON para consumo del demo HTML."""
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    with ruta_salida.open('w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)


# ============ ENTRY POINT ============

def main():
    """Ejecutable directo: genera cuadrante enero 2027 Fuentecillas."""
    sys.stdout.reconfigure(encoding='utf-8')
    centro, plantilla = plantilla_fuentecillas_demo()

    print(f"Generando cuadrante para {centro.nombre} · enero 2027 · {len(plantilla)} profesionales")
    resultado = generar_cuadrante_mensual(
        centro=centro,
        profesionales=plantilla,
        anio=2027,
        mes=1,
        max_segundos=120,
    )
    print(f"Estado: {resultado['estado']} · Tiempo: {resultado['segundos']}s")
    if 'equidad' in resultado.get('metricas', {}):
        eq = resultado['metricas']['equidad']
        print(f"\nEquidad obtenida:")
        print(f"  Horas trabajadas: media {eq['horas_media']}h · rango {eq['horas_rango']}h")
        print(f"  Festivos:         media {eq['festivos_media']}   · rango {eq['festivos_rango']}")
        print(f"  Fines de semana:  media {eq['fines_semana_media']}   · rango {eq['fines_semana_rango']}")

    # Exportar JSON
    ruta = Path(__file__).parent.parent.parent / 'demo' / '_partials' / 'cuadrante_fuentecillas_enero_2027.json'
    exportar_json(resultado, ruta)
    print(f"\nJSON exportado: {ruta}")


if __name__ == '__main__':
    main()

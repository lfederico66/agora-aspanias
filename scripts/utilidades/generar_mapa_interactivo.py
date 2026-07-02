"""Genera el HTML del tab Mapa de ocupacion con clickabilidad y panel lateral.

Cada cama abre un panel con datos de la persona y timeline de movimientos.
Reemplaza el bloque actual de <div x-show="tab === 'mapa'"> ... </div>.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

DEMO = Path(__file__).resolve().parent.parent / "demo"

# ============= Datos sinteticos de cada plaza =============
PERSONAS = {
    # Módulo A · Planta baja
    "A-11-1": {"iniciales": "JL", "nombre": "Sanz Ibáñez, José Luis", "edad": 52, "codigo": "FUE-2026-00002", "gestora": "Lucía Martínez", "ingreso": "12/03/2019", "modulo": "A", "habitacion": "11", "cama": "1", "alertas": [], "movimientos": [
        {"fecha": "12/03/2019", "tipo": "alta", "texto": "Alta inicial · procedente de domicilio familiar"},
        {"fecha": "08/06/2021", "tipo": "cambio", "texto": "Cambio temporal a hab. 13 (mantenimiento sanitario hab. 11)"},
        {"fecha": "22/06/2021", "tipo": "cambio", "texto": "Retorno a hab. 11 · cama 1"},
        {"fecha": "15/12/2024", "tipo": "obs", "texto": "Renovación de mobiliario"},
        {"fecha": "12/01/2026", "tipo": "valoracion", "texto": "Revisión PV anual realizada"},
    ]},
    "A-11-2": {"iniciales": "FA", "nombre": "Arnaiz Tudanca, Fernando", "edad": 38, "codigo": "FUE-2026-00008", "gestora": "Lucía Martínez", "ingreso": "04/09/2020", "modulo": "A", "habitacion": "11", "cama": "2", "alertas": [], "movimientos": [
        {"fecha": "04/09/2020", "tipo": "alta", "texto": "Alta inicial · procedente de domicilio familiar"},
        {"fecha": "10/04/2024", "tipo": "obs", "texto": "Compañero de cuarto cambiado · convive con José Luis"},
    ]},
    "A-12-1": {"iniciales": "MG", "nombre": "González Pérez, Marta", "edad": 34, "codigo": "FUE-2026-00001", "gestora": "Lucía Martínez", "ingreso": "12/09/2018", "modulo": "A", "habitacion": "12", "cama": "1", "alertas": ["⚠ PV vence 15/06"], "principal": True, "movimientos": [
        {"fecha": "12/09/2018", "tipo": "alta", "texto": "Alta inicial · procedente de domicilio familiar"},
        {"fecha": "04/03/2019", "tipo": "cambio", "texto": "Cambio interno cama 1 → cama 2 dentro de hab. 12"},
        {"fecha": "10/10/2020", "tipo": "cambio", "texto": "Retorno a cama 1 (preferencia personal)"},
        {"fecha": "01/02/2024", "tipo": "obs", "texto": "Alta complementaria CD Aspanias Puentesaúco"},
        {"fecha": "12/01/2026", "tipo": "valoracion", "texto": "Revisión PV anual realizada"},
        {"fecha": "28/05/2026", "tipo": "intervencion", "texto": "Última intervención psicología (Daniel Alonso)"},
    ]},
    "A-12-2": {"iniciales": "IS", "nombre": "Sáez de Antón, Inés", "edad": 37, "codigo": "FUE-2026-00005", "gestora": "Lucía Martínez", "ingreso": "20/05/2019", "modulo": "A", "habitacion": "12", "cama": "2", "alertas": [], "movimientos": [
        {"fecha": "20/05/2019", "tipo": "alta", "texto": "Alta inicial · traslado desde Residencia Quintanadueñas"},
        {"fecha": "10/06/2025", "tipo": "obs", "texto": "Visita familiar reanudada tras periodo de pausa"},
    ]},
    "A-13": {"iniciales": "EM", "nombre": "Manzanedo Olalla, Esther", "edad": 45, "codigo": "FUE-2026-00007", "gestora": "Daniel Alonso", "ingreso": "01/06/2017", "modulo": "A", "habitacion": "13", "cama": "indiv.", "alertas": [], "movimientos": [
        {"fecha": "01/06/2017", "tipo": "alta", "texto": "Alta inicial · habitación individual por necesidad de tranquilidad"},
        {"fecha": "14/03/2023", "tipo": "obs", "texto": "Petición renovada de habitación individual confirmada"},
    ]},
    "A-14-1": {"iniciales": "RM", "nombre": "Martín Cardeñoso, Roberto", "edad": 29, "codigo": "FUE-2026-00006", "gestora": "Pilar Renedo", "ingreso": "14/01/2022", "modulo": "A", "habitacion": "14", "cama": "1", "alertas": ["⚠ PV vence 22/06"], "movimientos": [
        {"fecha": "14/01/2022", "tipo": "alta", "texto": "Alta inicial · joven con familia colaboradora"},
    ]},
    "A-14-2": {"iniciales": "DC", "nombre": "Domínguez Cuesta, David", "edad": 31, "codigo": "FUE-2026-00009", "gestora": "Pilar Renedo", "ingreso": "23/08/2021", "modulo": "A", "habitacion": "14", "cama": "2", "alertas": [], "movimientos": [
        {"fecha": "23/08/2021", "tipo": "alta", "texto": "Alta inicial"},
    ]},
    "A-15-1": {"iniciales": "AM", "nombre": "Moreno Pascual, Ana", "edad": 28, "codigo": "FUE-2026-00003", "gestora": "Pilar Renedo", "ingreso": "12/07/2020", "modulo": "A", "habitacion": "15", "cama": "1", "alertas": [], "movimientos": [
        {"fecha": "12/07/2020", "tipo": "alta", "texto": "Alta inicial"},
        {"fecha": "20/04/2025", "tipo": "obs", "texto": "Modificación dieta por indicación médica"},
    ]},
    "A-15-2": {"iniciales": "TC", "nombre": "Cuadrado Tobar, Teresa", "edad": 56, "codigo": "FUE-2026-00010", "gestora": "Lucía Martínez", "ingreso": "08/05/2015", "modulo": "A", "habitacion": "15", "cama": "2", "alertas": [], "movimientos": [
        {"fecha": "08/05/2015", "tipo": "alta", "texto": "Alta inicial"},
    ]},
    "A-16": {"iniciales": "PV", "nombre": "Vergara Pino, Pablo", "edad": 42, "codigo": "FUE-2026-00011", "gestora": "Daniel Alonso", "ingreso": "02/11/2018", "modulo": "A", "habitacion": "16", "cama": "indiv.", "alertas": [], "movimientos": [
        {"fecha": "02/11/2018", "tipo": "alta", "texto": "Alta inicial · habitación individual"},
    ]},
    # Módulo B
    "B-21-1": {"iniciales": "CR", "nombre": "Rodríguez García, Carlos", "edad": 41, "codigo": "FUE-2026-00004", "gestora": "Daniel Alonso", "ingreso": "30/01/2020", "modulo": "B", "habitacion": "21", "cama": "1", "alertas": [], "movimientos": [
        {"fecha": "30/01/2020", "tipo": "alta", "texto": "Alta inicial"},
    ]},
    "B-21-2": {"iniciales": "VL", "nombre": "López Vela, Víctor", "edad": 33, "codigo": "FUE-2026-00012", "gestora": "Pilar Renedo", "ingreso": "17/04/2021", "modulo": "B", "habitacion": "21", "cama": "2", "alertas": [], "movimientos": [
        {"fecha": "17/04/2021", "tipo": "alta", "texto": "Alta inicial"},
    ]},
    "B-22-1": {"iniciales": "NB", "nombre": "Bermejo Núñez, Natalia", "edad": 39, "codigo": "FUE-2026-00013", "gestora": "Lucía Martínez", "ingreso": "05/08/2019", "modulo": "B", "habitacion": "22", "cama": "1", "alertas": [], "movimientos": [
        {"fecha": "05/08/2019", "tipo": "alta", "texto": "Alta inicial"},
    ]},
    "B-22-2": {"iniciales": "SO", "nombre": "Olmedo Sastre, Sonia", "edad": 27, "codigo": "FUE-2026-00014", "gestora": "Pilar Renedo", "ingreso": "11/02/2023", "modulo": "B", "habitacion": "22", "cama": "2", "alertas": [], "movimientos": [
        {"fecha": "11/02/2023", "tipo": "alta", "texto": "Alta inicial"},
    ]},
    "B-23": {"iniciales": "JR", "nombre": "Ruiz Jaen, Javier", "edad": 48, "codigo": "FUE-2026-00015", "gestora": "Daniel Alonso", "ingreso": "20/09/2016", "modulo": "B", "habitacion": "23", "cama": "indiv.", "alertas": [], "movimientos": [
        {"fecha": "20/09/2016", "tipo": "alta", "texto": "Alta inicial"},
    ]},
    "B-24-1": {"iniciales": "LA", "nombre": "Aguado Lara, Luis", "edad": 35, "codigo": "FUE-2026-00016", "gestora": "Lucía Martínez", "ingreso": "13/10/2020", "modulo": "B", "habitacion": "24", "cama": "1", "alertas": [], "movimientos": [
        {"fecha": "13/10/2020", "tipo": "alta", "texto": "Alta inicial"},
    ]},
    "B-24-2": {"iniciales": "CM", "nombre": "Manzano Castaño, Claudia", "edad": 30, "codigo": "FUE-2026-00017", "gestora": "Pilar Renedo", "ingreso": "06/03/2022", "modulo": "B", "habitacion": "24", "cama": "2", "alertas": [], "movimientos": [
        {"fecha": "06/03/2022", "tipo": "alta", "texto": "Alta inicial"},
    ]},
    "B-25-1": {"iniciales": "EG", "nombre": "Gil Estévez, Eduardo", "edad": 43, "codigo": "FUE-2026-00018", "gestora": "Daniel Alonso", "ingreso": "29/06/2018", "modulo": "B", "habitacion": "25", "cama": "1", "alertas": [], "movimientos": [
        {"fecha": "29/06/2018", "tipo": "alta", "texto": "Alta inicial"},
    ]},
    "B-25-2": {"iniciales": "RT", "nombre": "Torres Renedo, Raquel", "edad": 36, "codigo": "FUE-2026-00019", "gestora": "Lucía Martínez", "ingreso": "18/11/2019", "modulo": "B", "habitacion": "25", "cama": "2", "alertas": [], "movimientos": [
        {"fecha": "18/11/2019", "tipo": "alta", "texto": "Alta inicial"},
    ]},
    "B-26": {"iniciales": "PG", "nombre": "García Plaza, Pedro", "edad": 51, "codigo": "FUE-2026-00020", "gestora": "Daniel Alonso", "ingreso": "10/04/2014", "modulo": "B", "habitacion": "26", "cama": "indiv.", "alertas": [], "movimientos": [
        {"fecha": "10/04/2014", "tipo": "alta", "texto": "Alta inicial · residente más antiguo del módulo"},
    ]},
    # Módulo C
    "C-31-1": {"iniciales": "FT", "nombre": "Tudela Fernández, Fátima", "edad": 26, "codigo": "FUE-2026-00021", "gestora": "Pilar Renedo", "ingreso": "01/02/2024", "modulo": "C", "habitacion": "31", "cama": "1", "alertas": [], "movimientos": [
        {"fecha": "01/02/2024", "tipo": "alta", "texto": "Alta inicial · joven incorporación"},
    ]},
    "C-31-2": {"iniciales": "RC", "nombre": "Cárcamo Rojo, Roberto", "edad": 44, "codigo": "FUE-2026-00022", "gestora": "Lucía Martínez", "ingreso": "23/07/2017", "modulo": "C", "habitacion": "31", "cama": "2", "alertas": [], "movimientos": [
        {"fecha": "23/07/2017", "tipo": "alta", "texto": "Alta inicial"},
    ]},
    "C-32-1": {"iniciales": "MI", "nombre": "Iglesias Marín, María", "edad": 32, "codigo": "FUE-2026-00023", "gestora": "Pilar Renedo", "ingreso": "14/10/2021", "modulo": "C", "habitacion": "32", "cama": "1", "alertas": [], "movimientos": [
        {"fecha": "14/10/2021", "tipo": "alta", "texto": "Alta inicial"},
    ]},
    "C-32-2": {"libre": True, "modulo": "C", "habitacion": "32", "cama": "2", "movimientos": [
        {"fecha": "05/05/2026", "tipo": "baja", "texto": "Baja de Andrés Pérez (traslado a Residencia Quintanadueñas a petición familiar)"},
        {"fecha": "06/05/2026", "tipo": "obs", "texto": "Limpieza profunda y revisión de mobiliario"},
        {"fecha": "10/05/2026", "tipo": "obs", "texto": "Plaza disponible · candidata pendiente (lista de espera)"},
    ]},
    "C-33": {"iniciales": "AB", "nombre": "Bañuelos Antón, Andrea", "edad": 47, "codigo": "FUE-2026-00024", "gestora": "Daniel Alonso", "ingreso": "11/12/2015", "modulo": "C", "habitacion": "33", "cama": "indiv.", "alertas": [], "movimientos": [
        {"fecha": "11/12/2015", "tipo": "alta", "texto": "Alta inicial"},
    ]},
    "C-34-1": {"iniciales": "JV", "nombre": "Velasco Jiménez, Javier", "edad": 38, "codigo": "FUE-2026-00025", "gestora": "Lucía Martínez", "ingreso": "07/06/2018", "modulo": "C", "habitacion": "34", "cama": "1", "alertas": [], "movimientos": [
        {"fecha": "07/06/2018", "tipo": "alta", "texto": "Alta inicial"},
    ]},
    "C-34-2": {"iniciales": "BR", "nombre": "Reyes Bermúdez, Beatriz", "edad": 40, "codigo": "FUE-2026-00026", "gestora": "Pilar Renedo", "ingreso": "19/03/2020", "modulo": "C", "habitacion": "34", "cama": "2", "alertas": [], "movimientos": [
        {"fecha": "19/03/2020", "tipo": "alta", "texto": "Alta inicial"},
    ]},
    "C-35-1": {"iniciales": "NP", "nombre": "Prieto Núñez, Noelia", "edad": 33, "codigo": "FUE-2026-00027", "gestora": "Lucía Martínez", "ingreso": "25/09/2019", "modulo": "C", "habitacion": "35", "cama": "1", "alertas": [], "movimientos": [
        {"fecha": "25/09/2019", "tipo": "alta", "texto": "Alta inicial"},
    ]},
    "C-35-2": {"iniciales": "GO", "nombre": "Ortega Galán, Gabriel", "edad": 29, "codigo": "FUE-2026-00028", "gestora": "Daniel Alonso", "ingreso": "12/05/2022", "modulo": "C", "habitacion": "35", "cama": "2", "alertas": [], "movimientos": [
        {"fecha": "12/05/2022", "tipo": "alta", "texto": "Alta inicial"},
    ]},
    "C-36": {"iniciales": "XV", "nombre": "Vázquez Xavier, Xavi", "edad": 50, "codigo": "FUE-2026-00029", "gestora": "Daniel Alonso", "ingreso": "08/01/2013", "modulo": "C", "habitacion": "36", "cama": "indiv.", "alertas": [], "movimientos": [
        {"fecha": "08/01/2013", "tipo": "alta", "texto": "Alta inicial"},
    ]},
}


def nombre_breve(nombre_completo: str) -> str:
    """De 'González Pérez, Marta' -> 'Marta González'.
    De 'Sanz Ibáñez, José Luis' -> 'José Luis Sanz'.
    """
    if ',' not in nombre_completo:
        return nombre_completo
    apellidos, nombre = [x.strip() for x in nombre_completo.split(',', 1)]
    primer_apellido = apellidos.split()[0]  # primer token de los apellidos
    return f"{nombre} {primer_apellido}"


def render_plaza(codigo: str, datos: dict) -> str:
    """Renderiza una celda de plaza con clickabilidad."""
    libre = datos.get("libre", False)
    principal = datos.get("principal", False)

    if libre:
        clase = "rounded-md border-2 border-dashed border-blue-300 bg-blue-50 p-2 text-center cursor-pointer hover:shadow min-h-[64px] flex flex-col justify-center"
        contenido = f"""<p class="text-[10px] text-blue-700">Hab. {datos['habitacion']} · {datos['cama']}</p>
                        <p class="text-xs font-bold text-blue-700 mt-0.5">libre</p>"""
    elif principal:
        clase = "rounded-md border-2 border-emerald-500 bg-emerald-100 p-2 text-center cursor-pointer hover:shadow min-h-[64px] flex flex-col justify-center"
        contenido = f"""<p class="text-[10px] text-emerald-700">Hab. {datos['habitacion']} · {datos['cama']}</p>
                        <p class="text-[11px] font-semibold text-emerald-900 mt-0.5 leading-tight">{nombre_breve(datos['nombre'])}</p>"""
    else:
        clase = "rounded-md border border-emerald-300 bg-emerald-50 p-2 text-center cursor-pointer hover:shadow min-h-[64px] flex flex-col justify-center"
        contenido = f"""<p class="text-[10px] text-slate-500">Hab. {datos['habitacion']} · {datos['cama']}</p>
                        <p class="text-[11px] font-medium text-emerald-900 mt-0.5 leading-tight">{nombre_breve(datos['nombre'])}</p>"""

    return f'<div class="{clase}" @click="abrirPlaza(\'{codigo}\')">{contenido}</div>'


def render_modulo(letra: str, planta: str, plazas: list[str]) -> str:
    n_ocupadas = sum(1 for p in plazas if not PERSONAS[p].get("libre", False))
    n_libres = sum(1 for p in plazas if PERSONAS[p].get("libre", False))
    info = f"{len(plazas)} plazas · {n_ocupadas} ocupadas"
    if n_libres:
        info += f" · {n_libres} libre" + ("s" if n_libres > 1 else "")
    celdas = "\n                                ".join(render_plaza(p, PERSONAS[p]) for p in plazas)
    return f"""<div>
                            <div class="flex items-baseline justify-between mb-2">
                                <h4 class="text-xs font-semibold uppercase tracking-widest text-slate-700">Módulo {letra} · {planta}</h4>
                                <p class="text-xs text-slate-500">{info}</p>
                            </div>
                            <div class="grid gap-2 grid-cols-5">
                                {celdas}
                            </div>
                        </div>"""


PLAZAS_MODULO_A = ["A-11-1", "A-11-2", "A-12-1", "A-12-2", "A-13", "A-14-1", "A-14-2", "A-15-1", "A-15-2", "A-16"]
PLAZAS_MODULO_B = ["B-21-1", "B-21-2", "B-22-1", "B-22-2", "B-23", "B-24-1", "B-24-2", "B-25-1", "B-25-2", "B-26"]
PLAZAS_MODULO_C = ["C-31-1", "C-31-2", "C-32-1", "C-32-2", "C-33", "C-34-1", "C-34-2", "C-35-1", "C-35-2", "C-36"]


# Datos JSON para Alpine
datos_js = json.dumps(PERSONAS, ensure_ascii=False, indent=8)


# HTML completo del tab + panel + script
nuevo_tab = f"""                <!-- Tab Mapa de ocupación (default para residencias) -->
                <div x-show="tab === 'mapa'" class="p-5" x-data="mapaOcupacion()">
                    <div class="flex items-start justify-between flex-wrap gap-3 mb-4">
                        <div>
                            <h3 class="font-semibold">Mapa de ocupación · Residencia</h3>
                            <p class="text-xs text-slate-500 mt-0.5">30 plazas residenciales · 29 ocupadas · 1 libre · pulsa cualquier plaza para ver detalle</p>
                        </div>
                        <div class="flex items-center gap-3 text-xs">
                            <span class="flex items-center gap-1"><span class="inline-block w-3 h-3 rounded bg-emerald-500"></span>Ocupada</span>
                            <span class="flex items-center gap-1"><span class="inline-block w-3 h-3 rounded bg-blue-300"></span>Libre</span>
                            <span class="flex items-center gap-1"><span class="inline-block w-3 h-3 rounded bg-amber-400"></span>Reserva</span>
                            <span class="flex items-center gap-1"><span class="inline-block w-3 h-3 rounded bg-slate-200"></span>Fuera de servicio</span>
                        </div>
                    </div>

                    <!-- Modulos -->
                    <div class="space-y-5">
                        {render_modulo('A', 'Planta baja', PLAZAS_MODULO_A)}

                        {render_modulo('B', 'Primera planta', PLAZAS_MODULO_B)}

                        {render_modulo('C', 'Segunda planta', PLAZAS_MODULO_C)}
                    </div>

                    <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                        <p>Pulsa cualquier plaza para ver datos de la persona y movimientos</p>
                        <a href="mapa-ocupacion.html" class="text-emerald-700 hover:underline">Ver mapa completo →</a>
                    </div>

                    <!-- Panel lateral (drawer) con datos de la cama seleccionada -->
                    <div x-show="plazaSeleccionada !== null"
                         x-cloak
                         @keydown.escape.window="cerrarPanel()"
                         class="fixed inset-0 z-40 flex justify-end"
                         @click.self="cerrarPanel()">
                        <!-- Backdrop -->
                        <div class="absolute inset-0 bg-slate-900/30" @click="cerrarPanel()"></div>
                        <!-- Drawer -->
                        <div class="relative w-full max-w-md bg-white shadow-2xl overflow-y-auto"
                             x-transition:enter="transition ease-out duration-200"
                             x-transition:enter-start="translate-x-full"
                             x-transition:enter-end="translate-x-0">

                            <!-- Cabecera del drawer -->
                            <div class="sticky top-0 bg-white border-b border-slate-200 px-5 py-3 flex items-center justify-between">
                                <div>
                                    <p class="text-[10px] uppercase tracking-widest text-slate-500 font-semibold">Plaza</p>
                                    <h3 class="font-semibold text-base">Módulo <span x-text="plazaSeleccionada?.modulo"></span> · Hab. <span x-text="plazaSeleccionada?.habitacion"></span> · Cama <span x-text="plazaSeleccionada?.cama"></span></h3>
                                </div>
                                <button @click="cerrarPanel()" class="w-8 h-8 rounded-full hover:bg-slate-100 flex items-center justify-center text-slate-500">✕</button>
                            </div>

                            <!-- Plaza ocupada -->
                            <div x-show="!plazaSeleccionada?.libre" class="p-5 space-y-5">
                                <!-- Datos persona -->
                                <div>
                                    <p class="text-[10px] uppercase tracking-widest text-slate-500 font-semibold mb-2">Persona ocupante</p>
                                    <div class="flex items-start gap-3">
                                        <div class="w-14 h-14 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center text-lg font-semibold shrink-0" x-text="plazaSeleccionada?.iniciales"></div>
                                        <div class="flex-1 min-w-0">
                                            <p class="font-semibold text-slate-900" x-text="plazaSeleccionada?.nombre"></p>
                                            <p class="text-xs text-slate-500"><span x-text="plazaSeleccionada?.codigo"></span> · <span x-text="plazaSeleccionada?.edad"></span> años</p>
                                            <a href="persona-detalle.html" class="text-xs text-emerald-700 hover:underline mt-1 inline-block">Ver ficha completa →</a>
                                        </div>
                                    </div>

                                    <div class="mt-3 grid grid-cols-2 gap-x-4 gap-y-1.5 text-xs">
                                        <div><span class="text-slate-500">Gestor/a:</span> <span x-text="plazaSeleccionada?.gestora"></span></div>
                                        <div><span class="text-slate-500">Ingreso:</span> <span x-text="plazaSeleccionada?.ingreso"></span></div>
                                    </div>

                                    <template x-if="plazaSeleccionada?.alertas?.length">
                                        <div class="mt-3 p-2 rounded-md bg-amber-50 border border-amber-200">
                                            <template x-for="a in plazaSeleccionada.alertas">
                                                <p class="text-xs text-amber-800" x-text="a"></p>
                                            </template>
                                        </div>
                                    </template>
                                </div>

                                <!-- Timeline movimientos -->
                                <div>
                                    <p class="text-[10px] uppercase tracking-widest text-slate-500 font-semibold mb-2">Movimientos en esta plaza</p>
                                    <ol class="space-y-3 relative before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
                                        <template x-for="m in plazaSeleccionada?.movimientos || []" :key="m.fecha + m.texto">
                                            <li class="flex items-start gap-3 relative pl-1">
                                                <span class="w-4 h-4 rounded-full border-2 border-white shrink-0 mt-0.5 z-10"
                                                      :class="{{
                                                          'bg-emerald-500': m.tipo === 'alta',
                                                          'bg-rose-500': m.tipo === 'baja',
                                                          'bg-blue-500': m.tipo === 'cambio',
                                                          'bg-amber-400': m.tipo === 'obs',
                                                          'bg-purple-500': m.tipo === 'valoracion',
                                                          'bg-slate-400': m.tipo === 'intervencion'
                                                      }}"></span>
                                                <div class="flex-1 min-w-0">
                                                    <p class="text-[11px] text-slate-500" x-text="m.fecha"></p>
                                                    <p class="text-sm text-slate-800" x-text="m.texto"></p>
                                                </div>
                                            </li>
                                        </template>
                                    </ol>
                                </div>

                                <!-- Acciones -->
                                <div class="pt-4 border-t border-slate-100 space-y-2">
                                    <button class="w-full rounded-lg bg-emerald-700 text-white px-3 py-2 text-sm font-medium hover:bg-emerald-800">+ Registrar movimiento</button>
                                    <div class="grid grid-cols-2 gap-2">
                                        <button class="rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs text-slate-700 hover:border-emerald-400">Reasignar plaza</button>
                                        <button class="rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs text-slate-700 hover:border-emerald-400">Fuera de servicio</button>
                                    </div>
                                </div>
                            </div>

                            <!-- Plaza libre -->
                            <div x-show="plazaSeleccionada?.libre" x-cloak class="p-5 space-y-5">
                                <div class="rounded-lg bg-blue-50 border border-blue-200 p-4">
                                    <p class="text-sm font-semibold text-blue-900">Plaza disponible</p>
                                    <p class="text-xs text-blue-700 mt-1">Esta cama está libre y puede asignarse a una nueva persona.</p>
                                </div>

                                <div>
                                    <p class="text-[10px] uppercase tracking-widest text-slate-500 font-semibold mb-2">Últimos movimientos</p>
                                    <ol class="space-y-3 relative before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
                                        <template x-for="m in plazaSeleccionada?.movimientos || []" :key="m.fecha + m.texto">
                                            <li class="flex items-start gap-3 relative pl-1">
                                                <span class="w-4 h-4 rounded-full border-2 border-white shrink-0 mt-0.5 z-10"
                                                      :class="{{
                                                          'bg-rose-500': m.tipo === 'baja',
                                                          'bg-amber-400': m.tipo === 'obs'
                                                      }}"></span>
                                                <div class="flex-1 min-w-0">
                                                    <p class="text-[11px] text-slate-500" x-text="m.fecha"></p>
                                                    <p class="text-sm text-slate-800" x-text="m.texto"></p>
                                                </div>
                                            </li>
                                        </template>
                                    </ol>
                                </div>

                                <div class="pt-4 border-t border-slate-100">
                                    <button class="w-full rounded-lg bg-emerald-700 text-white px-3 py-2 text-sm font-medium hover:bg-emerald-800">+ Asignar persona</button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <script>
                    function mapaOcupacion() {{
                        return {{
                            plazaSeleccionada: null,
                            datos: {datos_js},
                            abrirPlaza(codigo) {{
                                this.plazaSeleccionada = this.datos[codigo];
                            }},
                            cerrarPanel() {{
                                this.plazaSeleccionada = null;
                            }}
                        }}
                    }}
                    </script>
                </div>"""


# Reemplazar en centro-detalle.html
ruta = DEMO / "centro-detalle.html"
contenido = ruta.read_text(encoding="utf-8")

# Patrón: capturar todo el bloque <div x-show="tab === 'mapa'"... hasta </div> que cierra antes del tab equipo
patron = re.compile(
    r'                <!-- Tab Mapa de ocupación.*?</div>\s*(?=\n\s*<!-- Tab Equipo)',
    re.DOTALL,
)

matches = patron.findall(contenido)
print(f"Encontrados {len(matches)} bloques del tab mapa")
if not matches:
    print("ERROR: no encontré el bloque a sustituir")
    exit(1)

nuevo_contenido = patron.sub(nuevo_tab + "\n", contenido)
ruta.write_text(nuevo_contenido, encoding="utf-8")
print(f"Tab mapa reemplazado con {len(PERSONAS)} plazas interactivas")

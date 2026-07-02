"""Propagar la nueva UX (sidebar fijo + breadcrumb) al resto de la demo.

Estrategia:
1. Extraer el contenido interior de <main> de cada HTML antiguo.
2. Reenvolver con el nuevo shell (sidebar de 5 items + breadcrumb sticky + search modal).
3. Mantener el título y los scripts (Tailwind, Alpine, fuentes).
4. Sustituir index.html / centro-detalle.html / persona-detalle.html con los 3 prototipos ya validados.
5. Eliminar agenda.html (redirect obsoleto) y los prototipo-*.html.
6. Actualizar enlaces internos: agenda.html -> agenda-hoy.html.

No se tocan: bienvenida.html, documento-*.html (intencionalmente sin sidebar).
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

DEMO = Path(__file__).resolve().parent.parent / "demo"

# =========================================================================
# Configuración por página
# =========================================================================
# clave: nombre del archivo
# valor: dict con titulo, activo (item sidebar), breadcrumb (HTML), acciones (HTML, opcional)

NO_TOCAR = {
    "bienvenida.html",
    "documento-algo-sobre-mi.html",
    "documento-historia-vida.html",
    "documento-plan-apoyo.html",
    "documento-proyecto-vida.html",
    "documento-revision-objetivos.html",
}

SUSTITUIR_CON_PROTOTIPO = {
    "index.html": "prototipo-inicio.html",
    "centro-detalle.html": "prototipo-centro.html",
    "persona-detalle.html": "prototipo-persona.html",
}

PAGINAS: dict[str, dict[str, str]] = {
    "centros.html": {
        "titulo": "Centros · ÁGORA",
        "activo": "centros",
        "breadcrumb": '<a href="index.html" class="hover:text-emerald-700">Inicio</a> <span class="mx-1">›</span> <span class="text-slate-700">Centros</span>',
        "acciones": "",
    },
    "personas-lista.html": {
        "titulo": "Personas atendidas · ÁGORA",
        "activo": "personas",
        "breadcrumb": '<a href="index.html" class="hover:text-emerald-700">Inicio</a> <span class="mx-1">›</span> <span class="text-slate-700">Personas atendidas</span>',
        "acciones": '<a href="#" class="rounded-lg bg-emerald-700 text-white px-3 py-1.5 text-xs font-medium hover:bg-emerald-800">+ Nueva persona</a>',
    },
    "pia-detalle.html": {
        "titulo": "Plan de Vida · ÁGORA",
        "activo": "personas",
        "breadcrumb": '<a href="index.html" class="hover:text-emerald-700">Inicio</a> <span class="mx-1">›</span> <a href="centros.html" class="hover:text-emerald-700">Centros</a> <span class="mx-1">›</span> <a href="centro-detalle.html" class="hover:text-emerald-700">Fuentecillas</a> <span class="mx-1">›</span> <a href="persona-detalle.html" class="hover:text-emerald-700">González Pérez, Marta</a> <span class="mx-1">›</span> <span class="text-slate-700">Plan de Vida</span>',
        "acciones": "",
    },
    "intervenciones.html": {
        "titulo": "Intervenciones · ÁGORA",
        "activo": "personas",
        "breadcrumb": '<a href="index.html" class="hover:text-emerald-700">Inicio</a> <span class="mx-1">›</span> <a href="persona-detalle.html" class="hover:text-emerald-700">González Pérez, Marta</a> <span class="mx-1">›</span> <span class="text-slate-700">Intervenciones</span>',
        "acciones": '<a href="nueva-intervencion.html" class="rounded-lg bg-emerald-700 text-white px-3 py-1.5 text-xs font-medium hover:bg-emerald-800">+ Intervención</a>',
    },
    "nueva-intervencion.html": {
        "titulo": "Nueva intervención · ÁGORA",
        "activo": "personas",
        "breadcrumb": '<a href="index.html" class="hover:text-emerald-700">Inicio</a> <span class="mx-1">›</span> <a href="intervenciones.html" class="hover:text-emerald-700">Intervenciones</a> <span class="mx-1">›</span> <span class="text-slate-700">Nueva intervención</span>',
        "acciones": "",
    },
    "nueva-valoracion.html": {
        "titulo": "Nueva valoración · ÁGORA",
        "activo": "personas",
        "breadcrumb": '<a href="index.html" class="hover:text-emerald-700">Inicio</a> <span class="mx-1">›</span> <a href="persona-detalle.html" class="hover:text-emerald-700">González Pérez, Marta</a> <span class="mx-1">›</span> <span class="text-slate-700">Nueva valoración</span>',
        "acciones": "",
    },
    "nueva-cita.html": {
        "titulo": "Nueva cita · ÁGORA",
        "activo": "agenda",
        "breadcrumb": '<a href="index.html" class="hover:text-emerald-700">Inicio</a> <span class="mx-1">›</span> <a href="agenda-hoy.html" class="hover:text-emerald-700">Agenda</a> <span class="mx-1">›</span> <span class="text-slate-700">Nueva cita</span>',
        "acciones": "",
    },
    "agenda-hoy.html": {
        "titulo": "Agenda · Hoy · ÁGORA",
        "activo": "agenda",
        "breadcrumb": '<a href="index.html" class="hover:text-emerald-700">Inicio</a> <span class="mx-1">›</span> <span class="text-slate-700">Agenda</span>',
        "acciones": '<a href="nueva-cita.html" class="rounded-lg bg-emerald-700 text-white px-3 py-1.5 text-xs font-medium hover:bg-emerald-800">+ Nueva cita</a> <a href="agenda-imprimir.html" class="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:border-emerald-400">🖨 Imprimir</a>',
    },
    "agenda-semana.html": {
        "titulo": "Agenda · Semana · ÁGORA",
        "activo": "agenda",
        "breadcrumb": '<a href="index.html" class="hover:text-emerald-700">Inicio</a> <span class="mx-1">›</span> <a href="agenda-hoy.html" class="hover:text-emerald-700">Agenda</a> <span class="mx-1">›</span> <span class="text-slate-700">Semana</span>',
        "acciones": '<a href="nueva-cita.html" class="rounded-lg bg-emerald-700 text-white px-3 py-1.5 text-xs font-medium hover:bg-emerald-800">+ Nueva cita</a>',
    },
    "agenda-mes.html": {
        "titulo": "Agenda · Mes · ÁGORA",
        "activo": "agenda",
        "breadcrumb": '<a href="index.html" class="hover:text-emerald-700">Inicio</a> <span class="mx-1">›</span> <a href="agenda-hoy.html" class="hover:text-emerald-700">Agenda</a> <span class="mx-1">›</span> <span class="text-slate-700">Mes</span>',
        "acciones": '<a href="nueva-cita.html" class="rounded-lg bg-emerald-700 text-white px-3 py-1.5 text-xs font-medium hover:bg-emerald-800">+ Nueva cita</a>',
    },
    "agenda-imprimir.html": {
        "titulo": "Agenda · Imprimir · ÁGORA",
        "activo": "agenda",
        "breadcrumb": '<a href="index.html" class="hover:text-emerald-700">Inicio</a> <span class="mx-1">›</span> <a href="agenda-hoy.html" class="hover:text-emerald-700">Agenda</a> <span class="mx-1">›</span> <span class="text-slate-700">Imprimir</span>',
        "acciones": "",
    },
    "mapa-ocupacion.html": {
        "titulo": "Mapa de ocupación · ÁGORA",
        "activo": "centros",
        "breadcrumb": '<a href="index.html" class="hover:text-emerald-700">Inicio</a> <span class="mx-1">›</span> <a href="centros.html" class="hover:text-emerald-700">Centros</a> <span class="mx-1">›</span> <a href="centro-detalle.html" class="hover:text-emerald-700">Fuentecillas</a> <span class="mx-1">›</span> <span class="text-slate-700">Mapa de ocupación</span>',
        "acciones": "",
    },
    "avisos-direccion.html": {
        "titulo": "Avisos a Dirección · ÁGORA",
        "activo": "inicio",
        "breadcrumb": '<a href="index.html" class="hover:text-emerald-700">Inicio</a> <span class="mx-1">›</span> <span class="text-slate-700">Avisos a Dirección</span>',
        "acciones": "",
    },
    "indicadores.html": {
        "titulo": "Tablero · Indicadores · ÁGORA",
        "activo": "tablero",
        "breadcrumb": '<a href="index.html" class="hover:text-emerald-700">Inicio</a> <span class="mx-1">›</span> <span class="text-slate-700">Tablero · Indicadores</span>',
        "acciones": "",
    },
    "control-pv.html": {
        "titulo": "Tablero · Control PV · ÁGORA",
        "activo": "tablero",
        "breadcrumb": '<a href="index.html" class="hover:text-emerald-700">Inicio</a> <span class="mx-1">›</span> <a href="indicadores.html" class="hover:text-emerald-700">Tablero</a> <span class="mx-1">›</span> <span class="text-slate-700">Control PV</span>',
        "acciones": "",
    },
    "control-pv-salas.html": {
        "titulo": "Control PV · Salas · ÁGORA",
        "activo": "tablero",
        "breadcrumb": '<a href="index.html" class="hover:text-emerald-700">Inicio</a> <span class="mx-1">›</span> <a href="indicadores.html" class="hover:text-emerald-700">Tablero</a> <span class="mx-1">›</span> <a href="control-pv.html" class="hover:text-emerald-700">Control PV</a> <span class="mx-1">›</span> <span class="text-slate-700">Salas de los Infantes</span>',
        "acciones": "",
    },
    "gestores-caso.html": {
        "titulo": "Tablero · Gestores de caso · ÁGORA",
        "activo": "tablero",
        "breadcrumb": '<a href="index.html" class="hover:text-emerald-700">Inicio</a> <span class="mx-1">›</span> <a href="indicadores.html" class="hover:text-emerald-700">Tablero</a> <span class="mx-1">›</span> <span class="text-slate-700">Gestores de caso</span>',
        "acciones": "",
    },
    "aspanias-cifras.html": {
        "titulo": "Aspanias en cifras · ÁGORA",
        "activo": "inicio",
        "breadcrumb": '<a href="index.html" class="hover:text-emerald-700">Inicio</a> <span class="mx-1">›</span> <span class="text-slate-700">Aspanias en cifras</span>',
        "acciones": "",
    },
    "editar-algo-sobre-mi.html": {
        "titulo": "Editar Algo sobre mí · ÁGORA",
        "activo": "personas",
        "breadcrumb": '<a href="persona-detalle.html" class="hover:text-emerald-700">González Pérez, Marta</a> <span class="mx-1">›</span> <a href="pia-detalle.html" class="hover:text-emerald-700">Plan de Vida</a> <span class="mx-1">›</span> <span class="text-slate-700">Editar Algo sobre mí</span>',
        "acciones": "",
    },
    "editar-historia-vida.html": {
        "titulo": "Editar Historia de vida · ÁGORA",
        "activo": "personas",
        "breadcrumb": '<a href="persona-detalle.html" class="hover:text-emerald-700">González Pérez, Marta</a> <span class="mx-1">›</span> <a href="pia-detalle.html" class="hover:text-emerald-700">Plan de Vida</a> <span class="mx-1">›</span> <span class="text-slate-700">Editar Historia de vida</span>',
        "acciones": "",
    },
    "editar-plan-apoyo.html": {
        "titulo": "Editar Plan de apoyo · ÁGORA",
        "activo": "personas",
        "breadcrumb": '<a href="persona-detalle.html" class="hover:text-emerald-700">González Pérez, Marta</a> <span class="mx-1">›</span> <a href="pia-detalle.html" class="hover:text-emerald-700">Plan de Vida</a> <span class="mx-1">›</span> <span class="text-slate-700">Editar Plan de apoyo</span>',
        "acciones": "",
    },
    "editar-proyecto-vida.html": {
        "titulo": "Editar Proyecto de vida · ÁGORA",
        "activo": "personas",
        "breadcrumb": '<a href="persona-detalle.html" class="hover:text-emerald-700">González Pérez, Marta</a> <span class="mx-1">›</span> <a href="pia-detalle.html" class="hover:text-emerald-700">Plan de Vida</a> <span class="mx-1">›</span> <span class="text-slate-700">Editar Proyecto de vida</span>',
        "acciones": "",
    },
    "editar-revision-objetivos.html": {
        "titulo": "Editar Revisión de objetivos · ÁGORA",
        "activo": "personas",
        "breadcrumb": '<a href="persona-detalle.html" class="hover:text-emerald-700">González Pérez, Marta</a> <span class="mx-1">›</span> <a href="pia-detalle.html" class="hover:text-emerald-700">Plan de Vida</a> <span class="mx-1">›</span> <span class="text-slate-700">Editar Revisión de objetivos</span>',
        "acciones": "",
    },
}

# =========================================================================
# Helpers para el sidebar
# =========================================================================

def _item_sidebar(href: str, icono: str, texto: str, activo: str, slug: str, badge_html: str = "") -> str:
    """Devuelve un <a> del sidebar con la clase 'activo' si corresponde."""
    if activo == slug:
        return (
            f'<a href="{href}" class="flex items-center gap-3 px-3 py-2 rounded-lg bg-emerald-50 text-emerald-800 font-medium border-l-4 border-emerald-700 -ml-1 pl-2">'
            f'<span class="text-lg">{icono}</span><span class="text-sm">{texto}</span>{badge_html}</a>'
        )
    return (
        f'<a href="{href}" class="flex items-center gap-3 px-3 py-2 rounded-lg text-slate-700 hover:bg-slate-50 hover:text-emerald-700">'
        f'<span class="text-lg">{icono}</span><span class="text-sm">{texto}</span>{badge_html}</a>'
    )


def _construir_sidebar(activo: str) -> str:
    items = [
        _item_sidebar("index.html",          "🏠", "Inicio",   activo, "inicio"),
        _item_sidebar("centros.html",        "🏢", "Centros",  activo, "centros",  '<span class="ml-auto text-[10px] text-slate-400">15</span>'),
        _item_sidebar("personas-lista.html", "👥", "Personas", activo, "personas", '<span class="ml-auto text-[10px] text-slate-400">383</span>'),
        _item_sidebar("agenda-hoy.html",     "📅", "Agenda",   activo, "agenda"),
        _item_sidebar("indicadores.html",    "📊", "Tablero",  activo, "tablero"),
    ]
    return "\n            ".join(items)


# =========================================================================
# Plantilla del shell
# =========================================================================
SHELL = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>__TITULO__</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script defer src="alpine.min.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>body{font-family:'Inter',-apple-system,system-ui,sans-serif}[x-cloak]{display:none!important}</style>
</head>
<body class="bg-slate-50 text-slate-900 antialiased">

<div class="bg-amber-50 border-b border-amber-200 text-amber-900 text-center text-[11px] py-1">🎯 <span class="font-medium">Demo de presentación</span> · todos los datos son ficticios</div>

<div class="flex min-h-screen" x-data="{ userMenu: false }">

    <aside class="w-60 shrink-0 bg-white border-r border-slate-200 flex flex-col sticky top-0 h-screen">
        <div class="px-5 py-5 border-b border-slate-100">
            <a href="index.html" class="flex items-center gap-2.5">
                <div class="w-9 h-9 rounded-lg bg-emerald-700 text-white flex items-center justify-center shadow-sm">
                    <svg viewBox="0 0 40 40" class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M 7 35 L 20 7 L 33 35"/><path d="M 12 24 L 28 24"/><circle cx="20" cy="5.5" r="1.6" fill="currentColor" stroke="none"/></svg>
                </div>
                <div class="leading-tight">
                    <p class="text-base font-semibold tracking-tight">ÁGORA</p>
                    <p class="text-[10px] text-slate-500">Grupo Social Aspanias</p>
                </div>
            </a>
        </div>
        <nav class="flex-1 px-3 py-4 space-y-0.5">
            __SIDEBAR_ITEMS__
            <div class="pt-4 mt-4 border-t border-slate-100">
                <p class="px-3 mb-1 text-[10px] uppercase tracking-widest text-slate-400 font-semibold">Acciones</p>
                <button onclick="document.dispatchEvent(new CustomEvent('agora-search'))" class="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-slate-700 hover:bg-slate-50 hover:text-emerald-700">
                    <span class="text-lg">🔎</span><span class="text-sm">Buscar</span>
                    <kbd class="ml-auto px-1.5 py-0.5 bg-slate-100 border border-slate-200 rounded text-[9px] text-slate-500">Ctrl+K</kbd>
                </button>
                <a href="avisos-direccion.html" class="flex items-center gap-3 px-3 py-2 rounded-lg text-slate-700 hover:bg-slate-50 hover:text-emerald-700">
                    <span class="text-lg">🔔</span><span class="text-sm">Avisos</span>
                    <span class="ml-auto text-[10px] px-1.5 rounded-full bg-amber-200 text-amber-900 font-bold">3</span>
                </a>
            </div>
        </nav>
        <div class="px-3 py-3 border-t border-slate-100 relative">
            <button @click="userMenu = !userMenu" class="w-full flex items-center gap-2.5 p-2 rounded-lg hover:bg-slate-50">
                <div class="w-9 h-9 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center text-sm font-semibold shrink-0">FM</div>
                <div class="leading-tight text-left flex-1 min-w-0">
                    <p class="text-sm font-medium truncate">Federico Martínez</p>
                    <p class="text-[10px] text-slate-500 truncate">Gerencia</p>
                </div>
                <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="m6 9 6 6 6-6"/></svg>
            </button>
            <div x-show="userMenu" x-cloak @click.outside="userMenu = false" class="absolute bottom-full left-3 right-3 mb-1 rounded-lg border border-slate-200 bg-white shadow-lg py-1 z-20">
                <a href="personas-lista.html?mio=1" class="block px-3 py-1.5 text-sm text-emerald-700 hover:bg-emerald-50 font-medium">⭐ Mis personas</a>
                <a href="#" class="block px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50">Mi perfil</a>
                <a href="#" class="block px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50">Preferencias</a>
                <div class="border-t border-slate-100 my-1"></div>
                <a href="#" class="block px-3 py-1.5 text-sm text-rose-700 hover:bg-rose-50">Cerrar sesión</a>
            </div>
        </div>
    </aside>

    <main class="flex-1 min-w-0">
        <div class="bg-white border-b border-slate-200 px-8 py-2.5 sticky top-0 z-10 flex items-center justify-between gap-4">
            <nav class="text-xs text-slate-500 truncate">__BREADCRUMB__</nav>
            <div class="flex items-center gap-2 shrink-0">__ACCIONES__</div>
        </div>
        <div class="px-8 py-6 max-w-7xl">
__CONTENIDO__
        </div>
    </main>
</div>

<div x-data="{ open: false }" x-cloak @keydown.window.ctrl.k.prevent="open = true" @keydown.window.meta.k.prevent="open = true" @agora-search.window="open = true" @keydown.escape.window="open = false" x-show="open" class="fixed inset-0 z-50 flex items-start justify-center pt-24 px-4 bg-slate-900/40 backdrop-blur-sm" @click.self="open = false">
    <div class="w-full max-w-xl rounded-2xl bg-white shadow-2xl overflow-hidden">
        <div class="flex items-center gap-3 px-5 py-4 border-b border-slate-200">
            <span class="text-xl">🔎</span>
            <input type="text" autofocus placeholder="Buscar persona, centro, cita..." class="flex-1 outline-none text-base">
            <kbd class="px-1.5 py-0.5 bg-slate-100 border border-slate-300 rounded text-[10px] text-slate-500">esc</kbd>
        </div>
    </div>
</div>

</body>
</html>
"""


# =========================================================================
# Extracción de contenido
# =========================================================================
PATRON_MAIN = re.compile(r"<main[^>]*>(.*?)</main>", re.DOTALL | re.IGNORECASE)


def extraer_contenido_main(html: str) -> str | None:
    """Extrae el contenido dentro de <main>...</main>."""
    m = PATRON_MAIN.search(html)
    if not m:
        return None
    contenido = m.group(1).strip()
    # Quitar el wrapper "mx-auto max-w-7xl px-6 py-8" si existe, porque nuestro shell ya lo tiene
    contenido = re.sub(
        r'^<div class="mx-auto max-w-7xl px-\d+ py-\d+[^"]*"[^>]*>',
        "",
        contenido,
    )
    if contenido.endswith("</div>"):
        contenido = contenido[: -len("</div>")].rstrip()
    return contenido


# =========================================================================
# Procesamiento
# =========================================================================
def procesar_archivo(nombre: str, config: dict) -> bool:
    ruta = DEMO / nombre
    if not ruta.exists():
        print(f"  [ERROR] no existe: {nombre}")
        return False
    html_viejo = ruta.read_text(encoding="utf-8")
    contenido = extraer_contenido_main(html_viejo)
    if contenido is None:
        print(f"  [SKIP] {nombre}: no se encontró <main>")
        return False
    sidebar = _construir_sidebar(config["activo"])
    nuevo = (
        SHELL
        .replace("__TITULO__", config["titulo"])
        .replace("__SIDEBAR_ITEMS__", sidebar)
        .replace("__BREADCRUMB__", config["breadcrumb"])
        .replace("__ACCIONES__", config.get("acciones", ""))
        .replace("__CONTENIDO__", contenido)
    )
    ruta.write_text(nuevo, encoding="utf-8")
    return True


def main() -> None:
    print(f"=== Aplicando nueva UX a la demo ({DEMO}) ===\n")

    # Paso 1: aplicar shell a cada página
    print(f"[1/4] Aplicando shell a {len(PAGINAS)} páginas...")
    aciertos = 0
    for nombre, config in PAGINAS.items():
        if procesar_archivo(nombre, config):
            aciertos += 1
            print(f"  [OK] {nombre}")
    print(f"\n  Total: {aciertos}/{len(PAGINAS)} páginas reenvueltas.\n")

    # Paso 2: sustituir las 3 con los prototipos
    print(f"[2/4] Sustituyendo 3 páginas con prototipos consolidados...")
    for destino, origen in SUSTITUIR_CON_PROTOTIPO.items():
        ruta_origen = DEMO / origen
        ruta_destino = DEMO / destino
        if ruta_origen.exists():
            shutil.copy2(ruta_origen, ruta_destino)
            print(f"  [OK] {origen} -> {destino}")
        else:
            print(f"  [ERROR] no existe el prototipo {origen}")
    print()

    # Paso 3: eliminar prototipos + agenda.html (redirect)
    print(f"[3/4] Limpiando archivos obsoletos...")
    a_borrar = ["agenda.html"] + list(SUSTITUIR_CON_PROTOTIPO.values())
    for nombre in a_borrar:
        ruta = DEMO / nombre
        if ruta.exists():
            ruta.unlink()
            print(f"  [OK] borrado: {nombre}")
    print()

    # Paso 4: actualizar enlaces agenda.html -> agenda-hoy.html
    print(f"[4/4] Actualizando enlaces internos agenda.html -> agenda-hoy.html...")
    n_cambios = 0
    for ruta in DEMO.glob("*.html"):
        contenido = ruta.read_text(encoding="utf-8")
        nuevo = re.sub(r'href="agenda\.html"', 'href="agenda-hoy.html"', contenido)
        if nuevo != contenido:
            ruta.write_text(nuevo, encoding="utf-8")
            n_cambios += 1
    print(f"  Archivos modificados: {n_cambios}\n")

    print("=== Hecho ===")


if __name__ == "__main__":
    main()

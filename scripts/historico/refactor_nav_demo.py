"""Refactor masivo de la nav en demo/ — UX paquete completo.

Reemplaza la nav plana antigua por la nueva nav con desplegables agrupados
(Atención / Operativa / Gestión) + búsqueda Ctrl+K + menú de usuario con
"Mis personas".

Se ejecuta una sola vez. No tocar las páginas ya editadas a mano
(index.html, centros.html, agenda.html redirect).
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "demo"

NAV_VIEJA_RE = re.compile(
    r'<nav class="flex items-center gap-6 text-sm">.*?</nav>\s*</div>\s*</header>',
    re.DOTALL,
)
HEADER_PATRON = re.compile(
    r'<header class="bg-white border-b border-slate-200 shadow-sm( no-print)?">'
)

NAV_NUEVA = '''<nav class="flex items-center gap-1 text-sm" @click.outside="open = null">
                <div class="relative">
                    <button @click="open = open === 'atencion' ? null : 'atencion'" class="px-3 py-2 rounded text-slate-700 hover:bg-slate-50 hover:text-emerald-700 flex items-center gap-1">🛏 Atención <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="m6 9 6 6 6-6"/></svg></button>
                    <div x-show="open === 'atencion'" x-cloak class="absolute left-0 mt-1 w-56 rounded-lg border border-slate-200 bg-white shadow-lg py-1 z-10">
                        <a href="centros.html" class="block px-3 py-2 text-slate-700 hover:bg-slate-50">Centros</a>
                        <a href="personas-lista.html" class="block px-3 py-2 text-slate-700 hover:bg-slate-50">Personas atendidas</a>
                        <a href="pia-detalle.html" class="block px-3 py-2 text-slate-700 hover:bg-slate-50">Plan de Vida</a>
                        <a href="intervenciones.html" class="block px-3 py-2 text-slate-700 hover:bg-slate-50">Intervenciones</a>
                        <a href="nueva-valoracion.html" class="block px-3 py-2 text-slate-700 hover:bg-slate-50">Valoraciones</a>
                    </div>
                </div>
                <div class="relative">
                    <button @click="open = open === 'operativa' ? null : 'operativa'" class="px-3 py-2 rounded text-slate-700 hover:bg-slate-50 hover:text-emerald-700 flex items-center gap-1">📅 Operativa <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="m6 9 6 6 6-6"/></svg></button>
                    <div x-show="open === 'operativa'" x-cloak class="absolute left-0 mt-1 w-56 rounded-lg border border-slate-200 bg-white shadow-lg py-1 z-10">
                        <a href="agenda.html" class="block px-3 py-2 text-slate-700 hover:bg-slate-50">Agenda</a>
                        <a href="mapa-ocupacion.html" class="block px-3 py-2 text-slate-700 hover:bg-slate-50">Mapa de ocupación</a>
                        <a href="avisos-direccion.html" class="flex items-center justify-between px-3 py-2 text-slate-700 hover:bg-slate-50"><span>Avisos a Dirección</span><span class="text-[10px] px-1.5 rounded-full bg-amber-200 text-amber-900 font-bold">3</span></a>
                    </div>
                </div>
                <div class="relative">
                    <button @click="open = open === 'gestion' ? null : 'gestion'" class="px-3 py-2 rounded text-slate-700 hover:bg-slate-50 hover:text-emerald-700 flex items-center gap-1">📊 Gestión <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="m6 9 6 6 6-6"/></svg></button>
                    <div x-show="open === 'gestion'" x-cloak class="absolute left-0 mt-1 w-56 rounded-lg border border-slate-200 bg-white shadow-lg py-1 z-10">
                        <a href="indicadores.html" class="block px-3 py-2 text-slate-700 hover:bg-slate-50">Indicadores</a>
                        <a href="control-pv.html" class="block px-3 py-2 text-slate-700 hover:bg-slate-50">Control PV</a>
                        <a href="gestores-caso.html" class="block px-3 py-2 text-slate-700 hover:bg-slate-50">Gestores de caso</a>
                    </div>
                </div>
                <button onclick="document.dispatchEvent(new CustomEvent('agora-search'))" class="ml-2 inline-flex items-center gap-2 rounded border border-slate-300 bg-slate-50 px-3 py-1.5 text-xs text-slate-500 hover:border-emerald-400">🔎 Buscar… <kbd class="px-1 py-0.5 bg-white border border-slate-300 rounded text-[10px]">Ctrl+K</kbd></button>
                <div class="relative ml-2 pl-3 border-l border-slate-200">
                    <button @click="open = open === 'user' ? null : 'user'" class="flex items-center gap-2.5">
                        <div class="w-9 h-9 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center text-sm font-semibold">FM</div>
                        <div class="leading-tight text-left"><p class="text-sm font-medium text-slate-900">Federico Martínez M.</p><p class="text-[11px] text-slate-500">Gerencia · Dir. Centros y Servicios</p></div>
                    </button>
                    <div x-show="open === 'user'" x-cloak class="absolute right-0 mt-1 w-56 rounded-lg border border-slate-200 bg-white shadow-lg py-1 z-10">
                        <a href="personas-lista.html?mio=1" class="block px-3 py-2 text-emerald-700 hover:bg-emerald-50 font-medium">⭐ Mis personas</a>
                        <a href="#" class="block px-3 py-2 text-slate-700 hover:bg-slate-50">Mi perfil</a>
                        <a href="#" class="block px-3 py-2 text-slate-700 hover:bg-slate-50">Mis preferencias</a>
                        <div class="border-t border-slate-100 my-1"></div>
                        <a href="#" class="block px-3 py-2 text-rose-700 hover:bg-rose-50">Cerrar sesión</a>
                    </div>
                </div>
            </nav>
        </div>
    </header>

    <div x-data="{ open: false }" x-cloak @keydown.window.ctrl.k.prevent="open = true" @keydown.window.meta.k.prevent="open = true" @agora-search.window="open = true" @keydown.escape.window="open = false" x-show="open" class="fixed inset-0 z-50 flex items-start justify-center pt-24 px-4 bg-slate-900/40 backdrop-blur-sm" @click.self="open = false">
        <div class="w-full max-w-xl rounded-2xl bg-white shadow-2xl overflow-hidden">
            <div class="flex items-center gap-3 px-5 py-4 border-b border-slate-200">
                <span class="text-2xl">🔎</span>
                <input type="text" autofocus placeholder="Buscar persona, centro, intervención, cita..." class="flex-1 outline-none text-base">
                <kbd class="px-1.5 py-0.5 bg-slate-100 border border-slate-300 rounded text-[10px] text-slate-500">esc</kbd>
            </div>
            <div class="max-h-96 overflow-y-auto py-2">
                <p class="px-5 py-2 text-xs uppercase tracking-wide text-slate-400">Sugerencias rápidas</p>
                <a href="persona-detalle.html" class="flex items-center gap-3 px-5 py-2.5 hover:bg-slate-50"><div class="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center text-xs font-semibold">MG</div><div class="flex-1"><p class="text-sm font-medium">González Pérez, Marta</p><p class="text-xs text-slate-500">FUE-2026-00001 · Fuentecillas</p></div></a>
                <a href="centros.html" class="flex items-center gap-3 px-5 py-2.5 hover:bg-slate-50"><div class="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center">🏠</div><div class="flex-1"><p class="text-sm font-medium">Ver todos los centros</p><p class="text-xs text-slate-500">13 centros · 383 personas</p></div></a>
                <a href="agenda.html" class="flex items-center gap-3 px-5 py-2.5 hover:bg-slate-50"><div class="w-8 h-8 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center">📅</div><div class="flex-1"><p class="text-sm font-medium">Agenda del día</p><p class="text-xs text-slate-500">4 citas hoy</p></div></a>
                <a href="indicadores.html" class="flex items-center gap-3 px-5 py-2.5 hover:bg-slate-50"><div class="w-8 h-8 rounded-lg bg-rose-100 text-rose-700 flex items-center justify-center">📊</div><div class="flex-1"><p class="text-sm font-medium">Cuadro de mando</p><p class="text-xs text-slate-500">Indicadores en vivo</p></div></a>
            </div>
        </div>
    </div>'''


def add_xdata(m: re.Match) -> str:
    no_print = m.group(1) or ""
    return f'<header class="bg-white border-b border-slate-200 shadow-sm{no_print}" x-data="{{ open: null }}">'


EXCLUIR = {"index.html", "agenda.html", "centros.html"}


def main():
    paginas = 0
    for p in sorted(ROOT.glob("*.html")):
        if p.name in EXCLUIR:
            continue
        t = p.read_text(encoding="utf-8")
        if not NAV_VIEJA_RE.search(t):
            continue
        # 1) Alpine.js
        if "alpine.min.js" not in t:
            t = t.replace(
                '<script src="https://cdn.tailwindcss.com"></script>',
                '<script src="https://cdn.tailwindcss.com"></script>\n    <script defer src="alpine.min.js"></script>',
                1,
            )
        # 2) x-cloak en body style
        if "[x-cloak]" not in t:
            t = t.replace(
                "body{font-family:'Inter',-apple-system,system-ui,sans-serif}",
                "body{font-family:'Inter',-apple-system,system-ui,sans-serif}[x-cloak]{display:none!important}",
                1,
            )
        # 3) x-data en header
        t = HEADER_PATRON.sub(add_xdata, t, count=1)
        # 4) Reemplazar la nav vieja
        t = NAV_VIEJA_RE.sub(NAV_NUEVA, t, count=1)
        p.write_text(t, encoding="utf-8")
        paginas += 1
        print(f"OK: {p.name}")
    print(f"\nTotal: {paginas} páginas con nueva nav.")


if __name__ == "__main__":
    main()

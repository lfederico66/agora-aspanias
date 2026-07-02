"""
Refactor del sidebar: agrupar 9 ítems planos en 4 bloques (Atención/Operativa/Análisis/Sistema)
+ añadir selector de rol visible para demo.

Reemplaza el bloque <nav class="flex-1 px-3 py-4 space-y-0.5"> ... </nav> entero,
preservando qué ítem estaba activo (clase bg-emerald-50 con border-l-4).
"""
import sys, re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# Mapa: href → identificador del item para detectar el activo
ITEMS = {
    'index.html':            ('🏠', 'Inicio',              None,  None),
    'agenda-hoy.html':       ('📅', 'Agenda',              None,  None),
    'personas-lista.html':   ('👥', 'Personas atendidas',  '417', 'slate'),
    'incidencias-fis.html':  ('🚨', 'Incidencias FIS',     '3',   'rose'),
    'centros.html':          ('🏢', 'Centros',             '18',  'slate'),
    'profesionales.html':    ('🩺', 'Equipo',              '187', 'slate'),
    'caja-centro.html':      ('💰', 'Caja y bolsillos',    None,  None),
    'facturacion.html':      ('💼', 'Facturación',         None,  None),
    'indicadores.html':      ('📊', 'Tablero',             None,  None),
    'aspanias-cifras.html':  ('📈', 'En cifras',           None,  None),
    'avisos-direccion.html': ('🔔', 'Avisos',              '3',   'amber'),
    'bienvenida.html':       ('🎓', 'Tour guiado',         None,  None),
    'hoja-ruta.html':        ('🗺',  'Hoja de ruta',        None,  None),
}

# Páginas del módulo Equipo: el item activo siempre será 'profesionales.html'
PAGINAS_EQUIPO = {'profesionales.html','vacaciones.html','turnos.html','calendario-laboral.html','patrones-turno.html','profesional-detalle.html'}
# Páginas de Personas:
PAGINAS_PERSONAS = {'personas-lista.html','persona-detalle.html','pia-detalle.html','intervenciones.html','nueva-intervencion.html','nueva-valoracion.html','gestores-caso.html','control-pv.html','control-pv-salas.html'} | set(f'editar-{x}.html' for x in ['historia-vida','plan-apoyo','proyecto-vida','revision-objetivos','algo-sobre-mi'])
# Páginas de Centros:
PAGINAS_CENTROS = {'centros.html','centro-detalle.html','mapa-ocupacion.html'}
# Páginas de Agenda:
PAGINAS_AGENDA = {'agenda-hoy.html','agenda-semana.html','agenda-mes.html','agenda-imprimir.html','nueva-cita.html'}
# Páginas de Incidencias:
PAGINAS_INCIDENCIAS = {'incidencias-fis.html','nueva-ficha-fis.html'}
# Páginas Caja/Facturación:
PAGINAS_CAJA = {'caja-centro.html'}
PAGINAS_FACT = {'facturacion.html','factura-detalle.html'}


def item_activo_de(nombre):
    """Devuelve la URL del item del sidebar que debe quedar activo según la página actual."""
    if nombre == 'index.html': return 'index.html'
    if nombre in PAGINAS_AGENDA: return 'agenda-hoy.html'
    if nombre in PAGINAS_PERSONAS: return 'personas-lista.html'
    if nombre in PAGINAS_INCIDENCIAS: return 'incidencias-fis.html'
    if nombre in PAGINAS_CENTROS: return 'centros.html'
    if nombre in PAGINAS_EQUIPO: return 'profesionales.html'
    if nombre in PAGINAS_CAJA: return 'caja-centro.html'
    if nombre in PAGINAS_FACT: return 'facturacion.html'
    if nombre == 'indicadores.html': return 'indicadores.html'
    if nombre == 'aspanias-cifras.html': return 'aspanias-cifras.html'
    if nombre == 'avisos-direccion.html': return 'avisos-direccion.html'
    if nombre == 'bienvenida.html': return 'bienvenida.html'
    if nombre == 'hoja-ruta.html': return 'hoja-ruta.html'
    return None


def render_item(href, activo, mostrar_indice=True):
    icono, label, badge, color = ITEMS[href]
    activo_clase = (
        'flex items-center gap-3 px-3 py-2 rounded-lg bg-emerald-50 text-emerald-800 font-medium border-l-4 border-emerald-700 -ml-1 pl-2'
        if href == activo else
        'flex items-center gap-3 px-3 py-2 rounded-lg text-slate-700 hover:bg-slate-50 hover:text-emerald-700'
    )
    badge_html = ''
    if badge:
        if color == 'rose':
            badge_html = f'<span class="ml-auto text-[10px] px-1.5 rounded-full bg-rose-200 text-rose-900 font-bold">{badge}</span>'
        elif color == 'amber':
            badge_html = f'<span class="ml-auto text-[10px] px-1.5 rounded-full bg-amber-200 text-amber-900 font-bold">{badge}</span>'
        elif href == activo:
            badge_html = f'<span class="ml-auto text-[10px] text-emerald-700 font-semibold">{badge}</span>'
        else:
            badge_html = f'<span class="ml-auto text-[10px] text-slate-400">{badge}</span>'
    return f'<a href="{href}" class="{activo_clase}"><span class="text-lg">{icono}</span><span class="text-sm">{label}</span>{badge_html}</a>'


def render_grupo(titulo, items_lista, activo, primero=False):
    items_html = '\n                '.join(render_item(h, activo) for h in items_lista)
    encabezado = f'<p class="px-3 mb-1 text-[10px] uppercase tracking-widest text-slate-400 font-semibold">{titulo}</p>'
    if primero:
        return f'<div>\n                {encabezado}\n                {items_html}\n            </div>'
    return f'<div class="pt-3 mt-2 border-t border-slate-100">\n                {encabezado}\n                {items_html}\n            </div>'


def construir_nav(activo):
    """Genera el bloque <nav>...</nav> nuevo."""
    return (
        '<nav class="flex-1 px-3 py-4 space-y-2 overflow-y-auto">\n'
        '            <!-- Trabajo diario -->\n'
        '            ' + render_grupo('Trabajo diario', ['index.html','agenda-hoy.html'], activo, primero=True) + '\n\n'
        '            <!-- Atención -->\n'
        '            ' + render_grupo('Atención', ['personas-lista.html','incidencias-fis.html'], activo) + '\n\n'
        '            <!-- Operativa -->\n'
        '            ' + render_grupo('Operativa', ['centros.html','profesionales.html','caja-centro.html','facturacion.html'], activo) + '\n\n'
        '            <!-- Análisis -->\n'
        '            ' + render_grupo('Análisis', ['indicadores.html','aspanias-cifras.html'], activo) + '\n\n'
        '            <!-- Sistema -->\n'
        '            <div class="pt-3 mt-2 border-t border-slate-100">\n'
        '                <p class="px-3 mb-1 text-[10px] uppercase tracking-widest text-slate-400 font-semibold">Sistema</p>\n'
        '                <button onclick="document.dispatchEvent(new CustomEvent(\'agora-search\'))" class="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-slate-700 hover:bg-slate-50 hover:text-emerald-700"><span class="text-lg">🔎</span><span class="text-sm">Buscar</span><kbd class="ml-auto px-1.5 py-0.5 bg-slate-100 border border-slate-200 rounded text-[9px] text-slate-500">Ctrl+K</kbd></button>\n'
        '                ' + render_item('avisos-direccion.html', activo) + '\n'
        '                ' + render_item('bienvenida.html', activo) + '\n'
        '                ' + render_item('hoja-ruta.html', activo) + '\n'
        '            </div>\n'
        '        </nav>'
    )


def render_selector_rol():
    """Bloque selector de rol — visible en demo, indica vista actual."""
    return (
        '<!-- Selector de rol (vista demo · Regla 2 gobernanza) -->\n'
        '        <div class="px-3 pt-2 pb-1">\n'
        '            <label class="block text-[9px] uppercase tracking-widest text-slate-400 font-semibold mb-1 px-1">Viendo como</label>\n'
        '            <select onchange="document.cookie=\'agora_rol=\'+this.value+\';path=/\'; location.reload();" class="w-full px-2 py-1.5 text-xs rounded-lg border border-amber-300 bg-amber-50 text-amber-900 font-medium focus:outline-none focus:ring-2 focus:ring-amber-200">\n'
        '                <option value="gerencia">🎩 Gerencia (Federico)</option>\n'
        '                <option value="direccion_centro">🏢 Dirección de centro</option>\n'
        '                <option value="gestor_caso">📋 Gestor/a de caso</option>\n'
        '                <option value="profesional">🩺 Profesional</option>\n'
        '                <option value="rrhh">📑 RRHH</option>\n'
        '                <option value="familia">👨‍👩‍👧 Familia (CERCA)</option>\n'
        '            </select>\n'
        '        </div>'
    )


def aplicar(ruta):
    nombre = ruta.name
    activo = item_activo_de(nombre)
    if activo is None:
        return False, 'sin item de sidebar'
    c = ruta.read_text(encoding='utf-8')
    if '<aside' not in c:
        return False, 'sin <aside>'

    nuevo_nav = construir_nav(activo)
    # Reemplazar el bloque <nav class="flex-1 px-3 py-4 space-y-0.5"> ... </nav>
    pat = re.compile(r'<nav class="flex-1 px-3 py-4 space-y-0\.5[^"]*"[^>]*>.*?</nav>', re.DOTALL)
    m = pat.search(c)
    if not m:
        return False, 'no localiza <nav> sidebar'
    c_nuevo = c[:m.start()] + nuevo_nav + c[m.end():]

    # Añadir selector de rol justo antes del bloque del usuario (footer del aside)
    if 'Selector de rol (vista demo' not in c_nuevo:
        # buscar el div del usuario al final del aside
        pat_user = re.compile(r'(\s*<div class="px-3 py-3 border-t border-slate-100[^"]*"[^>]*>)')
        m2 = pat_user.search(c_nuevo)
        if m2:
            c_nuevo = c_nuevo[:m2.start()] + '\n        ' + render_selector_rol() + c_nuevo[m2.start():]

    if c_nuevo != c:
        ruta.write_text(c_nuevo, encoding='utf-8')
        return True, f'activo={activo}'
    return False, 'sin cambios'


def main():
    demo = Path('demo')
    htmls = sorted(demo.glob('*.html'))
    ok, ko = 0, 0
    for h in htmls:
        cambio, info = aplicar(h)
        if cambio:
            ok += 1
        else:
            ko += 1
            print(f'  ?  {h.name} → {info}')
    print(f'\n=== Resumen ===')
    print(f'  Modificadas: {ok}')
    print(f'  Sin cambios: {ko}')


if __name__ == '__main__':
    main()

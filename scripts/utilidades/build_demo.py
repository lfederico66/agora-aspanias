"""
build_demo.py — Build de la demo HTML estática.

Tras editar el sidebar canónico, datos institucionales o un HTML, ejecutar:
    python scripts/utilidades/build_demo.py

El script hace 2 cosas:

  1. **Inyecta el sidebar canónico** (demo/_partials/sidebar.html) en cada HTML
     de demo/, ajustando qué item queda activo según la página.

  2. **Sustituye tokens {{nombre}}** por los valores de demo/_partials/datos.json.
     Tokens disponibles: {{centros}}, {{personas_atendidas}}, {{profesionales}},
     {{incidencias_fis_pendientes}}, {{avisos_direccion_pendientes}}.

Cada cambio futuro del sidebar = 1 archivo + 1 comando.
Cada cambio de cifras institucionales = 1 archivo + 1 comando.
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# Mapa: archivo HTML → item activo del sidebar
# Las páginas de un módulo activan su item raíz (p.ej. profesional-detalle activa profesionales.html)
MAPA_ACTIVO = {
    'index.html': 'index.html',
    'agenda-hoy.html': 'agenda-hoy.html',
    'agenda-semana.html': 'agenda-hoy.html',
    'agenda-mes.html': 'agenda-hoy.html',
    'agenda-imprimir.html': 'agenda-hoy.html',
    'nueva-cita.html': 'agenda-hoy.html',
    'personas-lista.html': 'personas-lista.html',
    'persona-detalle.html': 'personas-lista.html',
    'ficha-salud-pdf.html': 'personas-lista.html',
    'pia-detalle.html': 'personas-lista.html',
    'intervenciones.html': 'personas-lista.html',
    'nueva-intervencion.html': 'personas-lista.html',
    'nueva-valoracion.html': 'personas-lista.html',
    'gestores-caso.html': 'personas-lista.html',
    'control-pv.html': 'personas-lista.html',
    'control-pv-salas.html': 'personas-lista.html',
    'editar-historia-vida.html': 'personas-lista.html',
    'editar-plan-apoyo.html': 'personas-lista.html',
    'editar-proyecto-vida.html': 'personas-lista.html',
    'editar-revision-objetivos.html': 'personas-lista.html',
    'editar-algo-sobre-mi.html': 'personas-lista.html',
    'valoraciones-listado.html': 'valoraciones-listado.html',
    'valoracion-icap.html': 'valoraciones-listado.html',
    'valoracion-fumat.html': 'valoraciones-listado.html',
    'valoracion-san-martin.html': 'valoraciones-listado.html',
    'valoracion-inico-feaps.html': 'valoraciones-listado.html',
    'valoracion-abs-rc2.html': 'valoraciones-listado.html',
    'informe-psicologico-inicial.html': 'valoraciones-listado.html',
    'informe-psicologico-evolutivo.html': 'valoraciones-listado.html',
    'incidencias-fis.html': 'incidencias-fis.html',
    'nueva-ficha-fis.html': 'incidencias-fis.html',
    'centros.html': 'centros.html',
    'centro-detalle.html': 'centros.html',
    'mapa-ocupacion.html': 'centros.html',
    'area-empleo.html': 'area-empleo.html',
    'area-ocio.html': 'area-ocio.html',
    'profesionales.html': 'profesionales.html',
    'profesional-detalle.html': 'profesionales.html',
    'vacaciones.html': 'profesionales.html',
    'turnos.html': 'profesionales.html',
    'calendario-laboral.html': 'profesionales.html',
    'patrones-turno.html': 'profesionales.html',
    'caja-centro.html': 'caja-centro.html',
    'facturacion.html': 'facturacion.html',
    'indicadores.html': 'indicadores.html',
    'aspanias-cifras.html': 'aspanias-cifras.html',
    'documentos.html': 'documentos.html',
    'avisos-direccion.html': 'avisos-direccion.html',
    'bienvenida.html': 'bienvenida.html',
    'hoja-ruta.html': 'hoja-ruta.html',
    'peticiones-trabajo-social.html': 'hoja-ruta.html',
    'ficha-derivacion.html': 'personas-lista.html',
    'informe-social.html': 'personas-lista.html',
    'comunicacion-baja.html': 'personas-lista.html',
    'documentos-persona.html': 'personas-lista.html',
    'ratio-centro.html': 'centros.html',
    'cuadrante-motor.html': 'centros.html',
    'manual-uso.html': 'manual-uso.html',
}

PAT_INACTIVO = 'class="flex items-center gap-3 px-3 py-2 rounded-lg text-slate-700 hover:bg-slate-50 hover:text-emerald-700"'
PAT_ACTIVO = 'class="flex items-center gap-3 px-3 py-2 rounded-lg bg-emerald-50 text-emerald-800 font-medium border-l-4 border-emerald-700 -ml-1 pl-2"'


def aplicar_activo(sidebar_html: str, item_activo: str) -> str:
    """Marca un item como activo en el sidebar."""
    # Sustituir solo el item correspondiente
    patron = rf'<a href="{re.escape(item_activo)}" class="flex items-center gap-3 px-3 py-2 rounded-lg text-slate-700 hover:bg-slate-50 hover:text-emerald-700">'
    reemplazo = f'<a href="{item_activo}" class="flex items-center gap-3 px-3 py-2 rounded-lg bg-emerald-50 text-emerald-800 font-medium border-l-4 border-emerald-700 -ml-1 pl-2">'
    nuevo = re.sub(patron, reemplazo, sidebar_html, count=1)

    # Si el item tiene badge (span ml-auto), cambiar color del badge a emerald si era slate-400
    # Solo el badge del item activo
    activo_open = reemplazo
    if activo_open in nuevo:
        idx = nuevo.index(activo_open)
        fin = nuevo.index('</a>', idx)
        bloque = nuevo[idx:fin]
        bloque_nuevo = bloque.replace(
            '<span class="ml-auto text-[10px] text-slate-400">',
            '<span class="ml-auto text-[10px] text-emerald-700 font-semibold">',
            1,
        )
        nuevo = nuevo[:idx] + bloque_nuevo + nuevo[fin:]
    return nuevo


def cargar_datos(demo: Path) -> dict:
    """Lee demo/_partials/datos.json y devuelve dict {token: valor} para sustituir."""
    datos_path = demo / '_partials' / 'datos.json'
    if not datos_path.exists():
        print(f'Aviso: {datos_path} no existe, sin sustitución de tokens')
        return {}
    raw = json.loads(datos_path.read_text(encoding='utf-8'))
    # Filtrar claves que empiezan por '_' (metainfo)
    return {k: v for k, v in raw.items() if not k.startswith('_')}


def sustituir_tokens(texto: str, datos: dict) -> tuple[str, int]:
    """Sustituye {{token}} por el valor de datos. Devuelve (texto, num_reemplazos)."""
    total = 0
    for token, valor in datos.items():
        marca = '{{' + token + '}}'
        n = texto.count(marca)
        if n:
            texto = texto.replace(marca, str(valor))
            total += n
    return texto, total


def main():
    demo = Path('demo')
    partial_path = demo / '_partials' / 'sidebar.html'
    if not partial_path.exists():
        print(f'ERROR: no se encuentra {partial_path}')
        sys.exit(1)

    # Cargar datos institucionales para sustitución de tokens
    datos = cargar_datos(demo)
    if datos:
        print(f'Datos cargados ({len(datos)} tokens): {", ".join(datos.keys())}')

    sidebar_canonico = partial_path.read_text(encoding='utf-8')

    # Sustituir tokens del sidebar canónico antes de inyectarlo
    if datos:
        sidebar_canonico, n = sustituir_tokens(sidebar_canonico, datos)
        if n:
            print(f'Tokens resueltos en sidebar canónico: {n}')

    # El partial tiene: <nav>...</nav>\n\n        <!-- Footer usuario -->\n        <!-- Selector de rol -->...</div>
    # Lo dividimos en nav y selector para poder localizar la inserción exacta
    m_nav = re.search(r'<nav class="flex-1 px-3 py-4 space-y-2 overflow-y-auto">.*?</nav>',
                      sidebar_canonico, re.DOTALL)
    nav_canonico = m_nav.group(0)
    selector_canonico = sidebar_canonico[m_nav.end():].strip()

    # Patrones de detección en los HTML existentes
    re_nav_existente = re.compile(
        r'<nav class="flex-1 px-3 py-4 space-y-2 overflow-y-auto">.*?</nav>',
        re.DOTALL,
    )
    re_selector_existente = re.compile(
        r'<!-- Selector de rol \(vista demo · Regla 2 gobernanza\) -->\s*<div class="px-3 pt-2 pb-1">.*?</div>',
        re.DOTALL,
    )

    aplicados = 0
    no_localizados = []
    sin_mapa = []

    for ruta in sorted(demo.glob('*.html')):
        nombre = ruta.name
        if nombre.startswith('_'):
            continue
        if nombre not in MAPA_ACTIVO:
            sin_mapa.append(nombre)
            continue

        item_activo = MAPA_ACTIVO[nombre]
        nav_con_activo = aplicar_activo(nav_canonico, item_activo)

        c = ruta.read_text(encoding='utf-8')
        original = c

        # 1. Reemplazar nav existente
        if re_nav_existente.search(c):
            c = re_nav_existente.sub(lambda _: nav_con_activo, c, count=1)
        else:
            no_localizados.append(f'{nombre}: sin <nav>')
            continue

        # 2. Reemplazar selector de rol (si existe)
        if re_selector_existente.search(c):
            # El partial conserva el comentario "Footer usuario" + selector. Usamos solo el selector
            sel_partial = re.search(
                r'<!-- Selector de rol \(vista demo · Regla 2 gobernanza\) -->\s*<div class="px-3 pt-2 pb-1">.*?</div>',
                selector_canonico, re.DOTALL,
            ).group(0)
            c = re_selector_existente.sub(lambda _: sel_partial, c, count=1)

        # 3. Sustituir tokens {{nombre}} con los valores de datos.json
        if datos:
            c, _ = sustituir_tokens(c, datos)

        if c != original:
            ruta.write_text(c, encoding='utf-8')
            aplicados += 1

    print(f'Sidebar reinjetado en {aplicados} archivos')
    if no_localizados:
        print(f'\nSin <nav> localizable ({len(no_localizados)}):')
        for s in no_localizados:
            print(f'  - {s}')
    if sin_mapa:
        print(f'\nSin entrada en MAPA_ACTIVO ({len(sin_mapa)}):')
        for s in sin_mapa:
            print(f'  - {s}')

    # Verificación: confirmar que existe 1 item activo por HTML
    print('\nVerificación de coherencia (1 item activo por archivo):')
    errores = 0
    for ruta in sorted(demo.glob('*.html')):
        if ruta.name.startswith('_'):
            continue
        c = ruta.read_text(encoding='utf-8')
        # Contar items activos en el <nav>
        m = re_nav_existente.search(c)
        if not m:
            continue
        n_activos = m.group(0).count('bg-emerald-50 text-emerald-800 font-medium border-l-4 border-emerald-700')
        if n_activos != 1:
            errores += 1
            print(f'  ! {ruta.name}: {n_activos} items activos (debe ser 1)')

    if errores == 0:
        print('  OK · 1 item activo por archivo')
    else:
        print(f'\n  TOTAL ERRORES: {errores}')
        sys.exit(2)


if __name__ == '__main__':
    main()

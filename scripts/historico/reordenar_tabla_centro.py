"""Reordena la tabla de personas en centro-detalle.html alfabéticamente + paginación clara."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
import re

ruta = Path(__file__).resolve().parent.parent / 'demo' / 'centro-detalle.html'
contenido = ruta.read_text(encoding='utf-8')

# === 1. Reordenar las 5 filas alfabéticamente ===
patron_fila = re.compile(r'<tr class="hover:bg-emerald-50/40[^"]*"\s+onclick="location\.href=\'persona-detalle\.html\'">.*?</tr>', re.DOTALL)
filas_actuales = patron_fila.findall(contenido)
print(f'Filas detectadas: {len(filas_actuales)}')

# Extraer apellido de cada fila para ordenar
def primer_apellido(fila):
    m = re.search(r'([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)\s+[A-ZÁÉÍÓÚÑ]', fila)
    return m.group(1) if m else 'Z'

filas_ordenadas = sorted(filas_actuales, key=primer_apellido)
print('Orden alfabético:')
for f in filas_ordenadas:
    m = re.search(r'([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+ [A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:, [A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)?(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)?)', f)
    if m: print(f'  - {m.group(1)}')

# Reemplazar el bloque entero. Identificamos el <tbody> y reemplazamos las filas
patron_tbody = re.compile(r'(<tbody class="divide-y divide-slate-100">)(.*?)(</tbody>)', re.DOTALL)
m = patron_tbody.search(contenido)
if not m:
    print('ERROR: no se encontró tbody')
    sys.exit(1)

nuevo_tbody = m.group(1) + '\n                            ' + '\n                            '.join(filas_ordenadas) + '\n                        ' + m.group(3)
contenido = patron_tbody.sub(nuevo_tbody, contenido)
print('Tabla reordenada A-Z')

# === 2. Actualizar contadores en la cabecera y footer de la tabla ===
contenido = contenido.replace(
    '<p class="text-xs text-slate-500 mt-0.5">48 personas · busca por nombre, código o aplica filtros</p>',
    '<p class="text-xs text-slate-500 mt-0.5">48 personas · ordenadas alfabéticamente por apellidos</p>',
)

# === 3. Sustituir el footer "Mostrando 5 de 48 personas" + paginación simple por una versión rica ===
nueva_pag = '''<div class="px-5 py-3 border-t border-slate-200 flex items-center justify-between flex-wrap gap-3 text-xs">
                    <p class="text-slate-600">
                        <strong class="text-slate-900">Mostrando 1 – 5</strong> de <strong class="text-slate-900">48 personas</strong> · ordenadas A → Z
                    </p>
                    <div class="flex items-center gap-1" x-data="{ paginaCentro: 1 }">
                        <button @click="paginaCentro = 1" :disabled="paginaCentro === 1" :class="paginaCentro === 1 ? 'text-slate-300' : 'text-slate-600 hover:border-emerald-400'" class="px-2 py-1 rounded border border-slate-300" title="Primera">«</button>
                        <button @click="if (paginaCentro > 1) paginaCentro--" :class="paginaCentro === 1 ? 'text-slate-300' : 'text-slate-600 hover:border-emerald-400'" class="px-2 py-1 rounded border border-slate-300">‹</button>
                        <button @click="paginaCentro = 1" :class="paginaCentro === 1 ? 'bg-emerald-700 text-white' : 'bg-white border border-slate-300'" class="w-7 h-7 rounded font-medium">1</button>
                        <button @click="paginaCentro = 2" :class="paginaCentro === 2 ? 'bg-emerald-700 text-white' : 'bg-white border border-slate-300 hover:border-emerald-400'" class="w-7 h-7 rounded font-medium">2</button>
                        <button @click="paginaCentro = 3" :class="paginaCentro === 3 ? 'bg-emerald-700 text-white' : 'bg-white border border-slate-300 hover:border-emerald-400'" class="w-7 h-7 rounded font-medium">3</button>
                        <button @click="paginaCentro = 4" :class="paginaCentro === 4 ? 'bg-emerald-700 text-white' : 'bg-white border border-slate-300 hover:border-emerald-400'" class="w-7 h-7 rounded font-medium">4</button>
                        <span class="px-1 text-slate-400">…</span>
                        <button @click="paginaCentro = 10" :class="paginaCentro === 10 ? 'bg-emerald-700 text-white' : 'bg-white border border-slate-300 hover:border-emerald-400'" class="w-7 h-7 rounded font-medium">10</button>
                        <button @click="paginaCentro++" class="px-2 py-1 rounded border border-slate-300 text-slate-600 hover:border-emerald-400">›</button>
                        <button @click="paginaCentro = 10" class="px-2 py-1 rounded border border-slate-300 text-slate-600 hover:border-emerald-400" title="Última">»</button>
                    </div>
                </div>'''

# Reemplazar el footer actual de la tabla (Mostrando 5 de 48...)
patron_footer = re.compile(
    r'<div class="px-5 py-2\.5 border-t border-slate-200 flex items-center justify-between text-xs">.*?</div>\s*</section>',
    re.DOTALL
)
contenido = patron_footer.sub(nueva_pag + '\n            </section>', contenido)
print('Paginación enriquecida')

# === 4. Añadir bloque de salto alfabético ANTES del cierre de </section> de la tabla ===
# Esto va dentro de la sección de la tabla, entre el footer de paginación y </section>
# Mejor lo añado DESPUÉS de </section> de la tabla, como sección separada
seccion_alfabetica = '''

            <!-- Salto alfabético dentro del centro -->
            <section class="rounded-xl border border-slate-200 bg-white p-3">
                <div class="flex items-center gap-3 flex-wrap">
                    <p class="text-[10px] uppercase tracking-widest text-slate-500 font-semibold shrink-0">Saltar a apellido:</p>
                    <div class="flex flex-wrap gap-1">
LETRAS_CENTRO
                    </div>
                </div>
            </section>'''

letras_html = ''
# Las letras presentes en las 48 personas de Fuentecillas: A, B, C, D, E, F, G, I, M, N, O, P, R, S, T, V, X
letras_con_personas = set('ABCDEFGIMNOPRSTVX')
for letra in 'ABCDEFGHIJKLMNÑOPQRSTUVWXYZ':
    if letra == 'G':  # primera letra activa por defecto (González)
        clase = 'bg-emerald-700 text-white'
    elif letra in letras_con_personas:
        clase = 'bg-white border border-slate-300 hover:border-emerald-400 text-slate-700'
    else:
        clase = 'bg-slate-50 border border-slate-100 text-slate-300 cursor-not-allowed'
    letras_html += f'                        <button class="w-7 h-7 rounded font-medium text-[11px] {clase}">{letra}</button>\n'

seccion_alfabetica = seccion_alfabetica.replace('LETRAS_CENTRO', letras_html.rstrip())

# Insertar después del </section> de la tabla (que es donde antes habia </section>)
# Buscar la primera </section> después del </tbody>
# Mejor: insertar antes de la sección de tabs "Sección secundaria"
contenido = contenido.replace(
    '<!-- Sección secundaria: tabs (Mapa / Equipo / Información / Avisos / Documentos) -->',
    seccion_alfabetica.lstrip('\n') + '\n\n            <!-- Sección secundaria: tabs (Mapa / Equipo / Información / Avisos / Documentos) -->',
)
print('Salto alfabético añadido')

ruta.write_text(contenido, encoding='utf-8')
print('OK: centro-detalle.html actualizado')

"""Rediseña personas-lista.html con: orden alfabético, 5 por página, total, buscador prominente."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
import re

ruta = Path(__file__).resolve().parent.parent / 'demo' / 'personas-lista.html'
contenido = ruta.read_text(encoding='utf-8')

NUEVO = '''<div class="px-8 py-6 max-w-7xl space-y-5" x-data="{ pagina: 1, totalPaginas: 77, filtro: 'todas', orden: 'alfabetico', mostrarFiltros: false }">

            <!-- Cabecera -->
            <header class="flex items-end justify-between flex-wrap gap-3">
                <div>
                    <div class="flex items-center gap-3">
                        <h1 class="text-2xl font-semibold tracking-tight">Personas atendidas</h1>
                        <span class="text-xs px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-medium">383 activas</span>
                    </div>
                    <p class="text-sm text-slate-500 mt-1">Ficha única para los cuatro colectivos del grupo · ordenadas alfabéticamente por apellidos</p>
                </div>
                <div class="flex items-center gap-2">
                    <button class="rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs text-slate-700 hover:border-emerald-400">⤓ Exportar Excel</button>
                </div>
            </header>

            <!-- Buscador grande + acciones -->
            <section class="rounded-xl border border-slate-200 bg-white p-4 space-y-3">
                <div class="flex items-center gap-2 flex-wrap">
                    <div class="relative flex-1 min-w-[280px]">
                        <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-lg">🔎</span>
                        <input type="search" placeholder="Buscar por nombre, apellidos, código ÁGORA, NIF o teléfono…" class="w-full pl-11 pr-10 py-2.5 rounded-lg border border-slate-300 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 outline-none text-sm">
                        <kbd class="absolute right-3 top-1/2 -translate-y-1/2 px-1.5 py-0.5 bg-slate-100 border border-slate-300 rounded text-[10px] text-slate-500">Ctrl+K</kbd>
                    </div>
                    <button @click="mostrarFiltros = !mostrarFiltros" class="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 hover:border-emerald-400 flex items-center gap-1.5">
                        <span>⚙</span> Filtros avanzados
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="m6 9 6 6 6-6"/></svg>
                    </button>
                    <a href="#" class="rounded-lg bg-emerald-700 text-white px-3 py-2 text-sm font-medium hover:bg-emerald-800">+ Nueva persona</a>
                </div>

                <div class="flex gap-2 flex-wrap items-center">
                    <span class="text-xs text-slate-500 mr-1">Colectivo:</span>
                    <button @click="filtro='todas'" :class="filtro==='todas' ? 'bg-slate-900 text-white' : 'bg-white border border-slate-200 hover:border-emerald-300 text-slate-700'" class="rounded-full px-3 py-1 text-xs font-medium">Todas <span class="opacity-70">(383)</span></button>
                    <button @click="filtro='di'" :class="filtro==='di' ? 'bg-emerald-700 text-white' : 'bg-white border border-slate-200 hover:border-emerald-300 text-slate-700'" class="rounded-full px-3 py-1 text-xs">Discapacidad intelectual <span class="opacity-70">(213)</span></button>
                    <button @click="filtro='mayores'" :class="filtro==='mayores' ? 'bg-emerald-700 text-white' : 'bg-white border border-slate-200 hover:border-emerald-300 text-slate-700'" class="rounded-full px-3 py-1 text-xs">Mayores dependientes <span class="opacity-70">(60)</span></button>
                    <button @click="filtro='insercion'" :class="filtro==='insercion' ? 'bg-emerald-700 text-white' : 'bg-white border border-slate-200 hover:border-emerald-300 text-slate-700'" class="rounded-full px-3 py-1 text-xs">Inserción laboral <span class="opacity-70">(22)</span></button>
                    <button @click="filtro='menores'" :class="filtro==='menores' ? 'bg-emerald-700 text-white' : 'bg-white border border-slate-200 hover:border-emerald-300 text-slate-700'" class="rounded-full px-3 py-1 text-xs">Menores DI <span class="opacity-70">(24)</span></button>
                    <button @click="filtro='familias'" :class="filtro==='familias' ? 'bg-emerald-700 text-white' : 'bg-white border border-slate-200 hover:border-emerald-300 text-slate-700'" class="rounded-full px-3 py-1 text-xs">Familias <span class="opacity-70">(64)</span></button>
                </div>

                <div x-show="mostrarFiltros" x-cloak class="pt-3 border-t border-slate-100 grid gap-3 md:grid-cols-4">
                    <div>
                        <label class="text-[10px] uppercase tracking-widest text-slate-500 font-semibold">Centro</label>
                        <select class="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm">
                            <option>Todos los centros</option>
                            <option>Residencia Fuentecillas</option>
                            <option>Residencia Aspanias Puentesaúco</option>
                            <option>Residencia Aspanias Quintanadueñas</option>
                            <option>Residencia Aspanias Salas</option>
                            <option>Residencia Río Arlanza</option>
                            <option>Residencia Santa María</option>
                            <option>CD Aspanias Puentesaúco</option>
                            <option>CD Aspanias Quintanadueñas</option>
                            <option>CD Aspanias Salas</option>
                            <option>C. Multiactividad V. Aleixandre</option>
                            <option>CD Asistencial Quintanadueñas</option>
                            <option>CD Asistencial Salas</option>
                            <option>Áreas de Vivienda</option>
                            <option>Servicio Puentes</option>
                            <option>Colegio EE Puentesaúco</option>
                        </select>
                    </div>
                    <div>
                        <label class="text-[10px] uppercase tracking-widest text-slate-500 font-semibold">Estado PV</label>
                        <select class="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm">
                            <option>Todos los estados</option>
                            <option>Al día</option>
                            <option>Próximo a vencer (28 días)</option>
                            <option>Atrasado</option>
                            <option>Sin PV registrado</option>
                        </select>
                    </div>
                    <div>
                        <label class="text-[10px] uppercase tracking-widest text-slate-500 font-semibold">Edad</label>
                        <select class="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm">
                            <option>Cualquier edad</option>
                            <option>0-17 (menores)</option>
                            <option>18-30</option>
                            <option>31-50</option>
                            <option>51-65</option>
                            <option>+65 (mayores)</option>
                        </select>
                    </div>
                    <div>
                        <label class="text-[10px] uppercase tracking-widest text-slate-500 font-semibold">Modalidad</label>
                        <select class="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm">
                            <option>Cualquier modalidad</option>
                            <option>Residencial</option>
                            <option>Centro de día</option>
                            <option>Vivienda tutelada</option>
                            <option>Solo familias</option>
                        </select>
                    </div>
                </div>

                <div class="flex items-center justify-between flex-wrap gap-2 text-xs">
                    <div class="flex items-center gap-1 flex-wrap">
                        <span class="text-slate-500 mr-1">Atajos:</span>
                        <a href="#" class="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-medium">⭐ Mi cartera (27)</a>
                        <a href="#" class="px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 hover:bg-slate-200">Con cita esta semana (43)</a>
                        <a href="#" class="px-2 py-0.5 rounded-full bg-amber-100 text-amber-800">PV próximo a vencer (8)</a>
                        <a href="#" class="px-2 py-0.5 rounded-full bg-rose-100 text-rose-800">Alertas activas (3)</a>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-slate-500">Ordenar por:</span>
                        <select x-model="orden" class="rounded border border-slate-300 bg-white px-2 py-1 text-xs">
                            <option value="alfabetico">Apellidos A → Z</option>
                            <option value="alfabetico_inv">Apellidos Z → A</option>
                            <option value="reciente">Más recientes</option>
                            <option value="antiguos">Más antiguos</option>
                            <option value="edad_asc">Edad ascendente</option>
                            <option value="edad_desc">Edad descendente</option>
                        </select>
                    </div>
                </div>
            </section>

            <!-- Tabla -->
            <section class="rounded-xl border border-slate-200 bg-white overflow-hidden">

                <div class="px-5 py-3 border-b border-slate-200 flex items-center justify-between text-xs">
                    <p class="text-slate-600"><strong class="text-slate-900">Mostrando 1 – 5</strong> de <strong class="text-slate-900">383 personas</strong> · ordenadas por apellidos A → Z</p>
                    <div class="flex items-center gap-2">
                        <label class="text-slate-500">Por página:</label>
                        <select class="rounded border border-slate-300 bg-white px-2 py-0.5">
                            <option selected>5</option>
                            <option>10</option>
                            <option>25</option>
                            <option>50</option>
                        </select>
                    </div>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead class="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                            <tr>
                                <th class="px-5 py-2.5 text-left font-medium">Persona</th>
                                <th class="px-5 py-2.5 text-left font-medium">Código ÁGORA</th>
                                <th class="px-5 py-2.5 text-left font-medium">Edad</th>
                                <th class="px-5 py-2.5 text-left font-medium">Modalidad</th>
                                <th class="px-5 py-2.5 text-left font-medium">Gestor/a</th>
                                <th class="px-5 py-2.5 text-left font-medium">Estado PV</th>
                                <th class="px-5 py-2.5 text-right font-medium">Próx. cita</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-100">
                            <tr class="hover:bg-emerald-50/40 cursor-pointer" onclick="location.href='persona-detalle.html'">
                                <td class="px-5 py-3 font-medium">
                                    <div class="flex items-center gap-3">
                                        <div class="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center text-xs font-semibold">AL</div>
                                        <div>
                                            <p>Aguado Lara, Luis</p>
                                            <p class="text-[11px] text-slate-500">Residencia Aspanias Puentesaúco · DI</p>
                                        </div>
                                    </div>
                                </td>
                                <td class="px-5 py-3 text-xs text-slate-500 font-mono">PUE-2020-00018</td>
                                <td class="px-5 py-3 text-slate-600">35</td>
                                <td class="px-5 py-3"><span class="text-xs px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-800">🛏 Residencia</span></td>
                                <td class="px-5 py-3 text-slate-600">Carmen Saiz</td>
                                <td class="px-5 py-3"><span class="text-xs px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">Al día</span></td>
                                <td class="px-5 py-3 text-right text-xs text-slate-500">Jue 11:00</td>
                            </tr>
                            <tr class="hover:bg-emerald-50/40 cursor-pointer" onclick="location.href='persona-detalle.html'">
                                <td class="px-5 py-3 font-medium">
                                    <div class="flex items-center gap-3">
                                        <div class="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center text-xs font-semibold">AM</div>
                                        <div>
                                            <p>Antolín Robles, Mercedes</p>
                                            <p class="text-[11px] text-slate-500">Residencia Río Arlanza · Mayores</p>
                                        </div>
                                    </div>
                                </td>
                                <td class="px-5 py-3 text-xs text-slate-500 font-mono">ARL-2018-00007</td>
                                <td class="px-5 py-3 text-slate-600">62</td>
                                <td class="px-5 py-3"><span class="text-xs px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-800">🛏 Residencia</span></td>
                                <td class="px-5 py-3 text-slate-600">Mercedes Antolín</td>
                                <td class="px-5 py-3"><span class="text-xs px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">Al día</span></td>
                                <td class="px-5 py-3 text-right text-xs text-slate-500">—</td>
                            </tr>
                            <tr class="hover:bg-emerald-50/40 cursor-pointer" onclick="location.href='persona-detalle.html'">
                                <td class="px-5 py-3 font-medium">
                                    <div class="flex items-center gap-3">
                                        <div class="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center text-xs font-semibold">AT</div>
                                        <div>
                                            <p>Arnaiz Tudanca, Fernando</p>
                                            <p class="text-[11px] text-slate-500">Residencia Fuentecillas · DI</p>
                                        </div>
                                    </div>
                                </td>
                                <td class="px-5 py-3 text-xs text-slate-500 font-mono">FUE-2020-00008</td>
                                <td class="px-5 py-3 text-slate-600">38</td>
                                <td class="px-5 py-3"><span class="text-xs px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-800">🛏 Residencia</span></td>
                                <td class="px-5 py-3 text-slate-600">Lucía Martínez</td>
                                <td class="px-5 py-3"><span class="text-xs px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">Al día</span></td>
                                <td class="px-5 py-3 text-right text-xs text-slate-500">Lun 10:30</td>
                            </tr>
                            <tr class="hover:bg-emerald-50/40 cursor-pointer" onclick="location.href='persona-detalle.html'">
                                <td class="px-5 py-3 font-medium">
                                    <div class="flex items-center gap-3">
                                        <div class="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center text-xs font-semibold">BA</div>
                                        <div>
                                            <p>Bañuelos Antón, Andrea</p>
                                            <p class="text-[11px] text-slate-500">Residencia Fuentecillas · DI</p>
                                        </div>
                                    </div>
                                </td>
                                <td class="px-5 py-3 text-xs text-slate-500 font-mono">FUE-2015-00024</td>
                                <td class="px-5 py-3 text-slate-600">47</td>
                                <td class="px-5 py-3"><span class="text-xs px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-800">🛏 Residencia</span></td>
                                <td class="px-5 py-3 text-slate-600">Daniel Alonso</td>
                                <td class="px-5 py-3"><span class="text-xs px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">Al día</span></td>
                                <td class="px-5 py-3 text-right text-xs text-slate-500">—</td>
                            </tr>
                            <tr class="hover:bg-emerald-50/40 cursor-pointer" onclick="location.href='persona-detalle.html'">
                                <td class="px-5 py-3 font-medium">
                                    <div class="flex items-center gap-3">
                                        <div class="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center text-xs font-semibold">BN</div>
                                        <div>
                                            <p>Bermejo Núñez, Natalia <span title="También en Servicio Puentes" class="text-[10px] text-blue-700 ml-1">+1 servicio</span></p>
                                            <p class="text-[11px] text-slate-500">Residencia Fuentecillas + Servicio Puentes · DI</p>
                                        </div>
                                    </div>
                                </td>
                                <td class="px-5 py-3 text-xs text-slate-500 font-mono">FUE-2019-00013</td>
                                <td class="px-5 py-3 text-slate-600">39</td>
                                <td class="px-5 py-3">
                                    <div class="flex items-center gap-1 flex-wrap">
                                        <span class="text-xs px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-800">🛏 Resid.</span>
                                        <span class="text-xs px-2 py-0.5 rounded-full bg-amber-100 text-amber-800">🌞 Inserc.</span>
                                    </div>
                                </td>
                                <td class="px-5 py-3 text-slate-600">Lucía Martínez</td>
                                <td class="px-5 py-3"><span class="text-xs px-2 py-0.5 rounded-full bg-amber-100 text-amber-800">Vence 28/06</span></td>
                                <td class="px-5 py-3 text-right text-xs text-slate-500">Mié 09:30</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="px-5 py-3 border-t border-slate-200 flex items-center justify-between flex-wrap gap-3 text-sm">
                    <p class="text-slate-600 text-xs">
                        <strong class="text-slate-900">Página <span x-text="pagina">1</span></strong> de <strong class="text-slate-900">77</strong> · <span class="text-slate-500">Mostrando 1 – 5 de 383 personas</span>
                    </p>
                    <div class="flex items-center gap-1">
                        <button @click="pagina = 1" :disabled="pagina === 1" :class="pagina === 1 ? 'text-slate-300 cursor-not-allowed' : 'text-slate-600 hover:border-emerald-400'" class="px-2.5 py-1 rounded border border-slate-300" title="Primera">«</button>
                        <button @click="if (pagina > 1) pagina--" :disabled="pagina === 1" :class="pagina === 1 ? 'text-slate-300 cursor-not-allowed' : 'text-slate-600 hover:border-emerald-400'" class="px-2.5 py-1 rounded border border-slate-300">‹ Anterior</button>
                        <button @click="pagina = 1" :class="pagina === 1 ? 'bg-emerald-700 text-white' : 'bg-white border border-slate-300 hover:border-emerald-400'" class="w-8 h-7 rounded text-xs font-medium">1</button>
                        <button @click="pagina = 2" :class="pagina === 2 ? 'bg-emerald-700 text-white' : 'bg-white border border-slate-300 hover:border-emerald-400'" class="w-8 h-7 rounded text-xs font-medium">2</button>
                        <button @click="pagina = 3" :class="pagina === 3 ? 'bg-emerald-700 text-white' : 'bg-white border border-slate-300 hover:border-emerald-400'" class="w-8 h-7 rounded text-xs font-medium">3</button>
                        <button @click="pagina = 4" :class="pagina === 4 ? 'bg-emerald-700 text-white' : 'bg-white border border-slate-300 hover:border-emerald-400'" class="w-8 h-7 rounded text-xs font-medium">4</button>
                        <span class="px-1 text-slate-400">…</span>
                        <button @click="pagina = 77" :class="pagina === 77 ? 'bg-emerald-700 text-white' : 'bg-white border border-slate-300 hover:border-emerald-400'" class="w-10 h-7 rounded text-xs font-medium">77</button>
                        <button @click="if (pagina < 77) pagina++" class="text-slate-600 hover:border-emerald-400 px-2.5 py-1 rounded border border-slate-300">Siguiente ›</button>
                        <button @click="pagina = 77" class="text-slate-600 hover:border-emerald-400 px-2.5 py-1 rounded border border-slate-300" title="Última">»</button>
                    </div>
                </div>
            </section>

            <!-- Letras alfabéticas (jump rápido) -->
            <section class="rounded-xl border border-slate-200 bg-white p-4">
                <p class="text-[10px] uppercase tracking-widest text-slate-500 font-semibold mb-2">Saltar a la letra</p>
                <div class="flex flex-wrap gap-1">
LETRAS_PLACEHOLDER
                </div>
            </section>

        '''

# Generar las letras dinámicamente
letras_html = ''
for letra in 'ABCDEFGHIJKLMNÑOPQRSTUVWXYZ':
    if letra == 'A':
        clase = 'bg-emerald-700 text-white'
    else:
        clase = 'bg-white border border-slate-300 hover:border-emerald-400 text-slate-700'
    letras_html += f'                    <button class="w-7 h-7 rounded font-medium text-xs {clase}">{letra}</button>\n'

NUEVO = NUEVO.replace('LETRAS_PLACEHOLDER', letras_html.rstrip())

patron = re.compile(r'(<div class="px-8 py-6 max-w-7xl">)(.*?)(\s*</main>)', re.DOTALL)
m = patron.search(contenido)
if not m:
    print("ERROR: bloque no encontrado")
    sys.exit(1)

nuevo_html = patron.sub(lambda mm: NUEVO + mm.group(3), contenido)
ruta.write_text(nuevo_html, encoding='utf-8')
print('OK: personas-lista.html reescrita')

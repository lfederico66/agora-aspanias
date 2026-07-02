"""Rellena los 4 tabs vacíos de persona-detalle.html con contenido real."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
import re

ruta = Path(__file__).resolve().parent.parent / 'demo' / 'persona-detalle.html'
contenido = ruta.read_text(encoding='utf-8')

# Helper para envolver con encabezado expandido
def envolver(tab_id, icono, nombre, html_interno):
    return f'''<div x-show="expandido || tab === '{tab_id}'" x-cloak class="space-y-5" :class="expandido ? 'mt-6' : ''">
                <h2 x-show="expandido" x-cloak class="text-lg font-semibold tracking-tight pt-4 mt-2 border-t-2 border-emerald-200"><span class="text-xl">{icono}</span> {nombre}</h2>
                {html_interno}
            </div>'''


# === TAB INTERVENCIONES Y VALORACIONES ===
TAB_INTER = '''
                <!-- KPIs -->
                <section class="grid gap-3 grid-cols-2 md:grid-cols-4">
                    <div class="rounded-xl border border-slate-200 bg-white p-4">
                        <p class="text-xs text-slate-500">Intervenciones (año)</p>
                        <p class="mt-0.5 text-3xl font-light">142</p>
                        <p class="text-[10px] text-slate-400">12 esta semana</p>
                    </div>
                    <div class="rounded-xl border border-slate-200 bg-white p-4">
                        <p class="text-xs text-slate-500">Última valoración</p>
                        <p class="mt-0.5 text-lg font-semibold leading-tight">12/01/2026</p>
                        <p class="text-[10px] text-slate-400">Schalock — anual</p>
                    </div>
                    <div class="rounded-xl border border-amber-200 bg-amber-50 p-4">
                        <p class="text-xs text-amber-700">Pendiente</p>
                        <p class="mt-0.5 text-lg font-semibold leading-tight text-amber-800">BVD 2026</p>
                        <p class="text-[10px] text-amber-700">vence 30/06</p>
                    </div>
                    <div class="rounded-xl border border-slate-200 bg-white p-4">
                        <p class="text-xs text-slate-500">Profesionales activos</p>
                        <p class="mt-0.5 text-3xl font-light">5</p>
                        <p class="text-[10px] text-slate-400">TS, TO, Psi, DUE, Méd.</p>
                    </div>
                </section>

                <!-- Acciones -->
                <div class="flex items-center justify-between gap-3 flex-wrap">
                    <div class="flex items-center gap-2 flex-wrap text-xs">
                        <span class="text-slate-500">Filtrar:</span>
                        <a href="#" class="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-medium">Todo (142)</a>
                        <a href="#" class="px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">Intervenciones (128)</a>
                        <a href="#" class="px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">Valoraciones (14)</a>
                        <a href="#" class="px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">Psicología (32)</a>
                        <a href="#" class="px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">TO (45)</a>
                        <a href="#" class="px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">DUE (28)</a>
                    </div>
                    <div class="flex items-center gap-2">
                        <a href="nueva-valoracion.html" class="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs text-slate-700 hover:border-emerald-400">+ Valoración</a>
                        <a href="nueva-intervencion.html" class="rounded-lg bg-emerald-700 text-white px-3 py-1.5 text-xs font-medium hover:bg-emerald-800">+ Intervención</a>
                    </div>
                </div>

                <!-- Timeline -->
                <section class="rounded-xl border border-slate-200 bg-white overflow-hidden">
                    <div class="px-5 py-3 border-b border-slate-200">
                        <h2 class="text-sm font-semibold">Timeline cronológico</h2>
                        <p class="text-xs text-slate-500 mt-0.5">Últimos 30 días · 12 movimientos</p>
                    </div>
                    <ol class="divide-y divide-slate-100">
                        <li class="px-5 py-3 hover:bg-slate-50">
                            <div class="flex items-start gap-3">
                                <div class="w-9 h-9 rounded-full bg-purple-100 text-purple-700 flex items-center justify-center text-xs font-semibold shrink-0">DA</div>
                                <div class="flex-1">
                                    <div class="flex items-center gap-2 flex-wrap">
                                        <p class="text-xs text-slate-500">29/05/2026 · 17:00 · 45 min</p>
                                        <span class="text-[10px] px-1.5 py-0.5 rounded-full bg-purple-100 text-purple-800">Psicología</span>
                                    </div>
                                    <p class="mt-0.5 font-medium">Sesión semanal de gestión emocional · Daniel Alonso</p>
                                    <p class="text-sm text-slate-600 mt-1">Avance significativo identificando emociones en sí misma. Trabajado con tarjetas de emociones. Estable en estado de ánimo. Próxima sesión: continuar con regulación.</p>
                                </div>
                            </div>
                        </li>
                        <li class="px-5 py-3 hover:bg-slate-50">
                            <div class="flex items-start gap-3">
                                <div class="w-9 h-9 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-xs font-semibold shrink-0">PR</div>
                                <div class="flex-1">
                                    <div class="flex items-center gap-2 flex-wrap">
                                        <p class="text-xs text-slate-500">27/05/2026 · 11:00 · 60 min</p>
                                        <span class="text-[10px] px-1.5 py-0.5 rounded-full bg-blue-100 text-blue-800">Terapia Ocupacional</span>
                                    </div>
                                    <p class="mt-0.5 font-medium">Taller de cocina · Pilar Renedo</p>
                                    <p class="text-sm text-slate-600 mt-1">Ha completado receta básica de tortilla con apoyo verbal. Demuestra autonomía en preparación de ingredientes. Manejo de utensilios eléctricos: requiere supervisión.</p>
                                </div>
                            </div>
                        </li>
                        <li class="px-5 py-3 hover:bg-slate-50">
                            <div class="flex items-start gap-3">
                                <div class="w-9 h-9 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-xs font-semibold shrink-0">LM</div>
                                <div class="flex-1">
                                    <div class="flex items-center gap-2 flex-wrap">
                                        <p class="text-xs text-slate-500">21/05/2026 · 10:30 · 30 min</p>
                                        <span class="text-[10px] px-1.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800">Trabajo Social</span>
                                    </div>
                                    <p class="mt-0.5 font-medium">Reunión con la madre · Lucía Martínez</p>
                                    <p class="text-sm text-slate-600 mt-1">Revisamos avances del trimestre. La madre solicita más sesiones de cocina (lo hablado en última visita). Acordamos refuerzo en taller los viernes. Estado emocional familiar estable.</p>
                                </div>
                            </div>
                        </li>
                        <li class="px-5 py-3 hover:bg-slate-50 bg-amber-50/30">
                            <div class="flex items-start gap-3">
                                <div class="w-9 h-9 rounded-full bg-amber-100 text-amber-700 flex items-center justify-center text-xs font-semibold shrink-0">⚕</div>
                                <div class="flex-1">
                                    <div class="flex items-center gap-2 flex-wrap">
                                        <p class="text-xs text-slate-500">18/05/2026 · 09:00</p>
                                        <span class="text-[10px] px-1.5 py-0.5 rounded-full bg-amber-100 text-amber-800">VALORACIÓN · Schalock</span>
                                    </div>
                                    <p class="mt-0.5 font-medium">Escala Schalock & Verdugo · 8 dimensiones de calidad de vida</p>
                                    <p class="text-sm text-slate-600 mt-1">Puntuación global: 84/120. Dimensiones fuertes: relaciones interpersonales (97), bienestar emocional (94). Dimensión a mejorar: autodeterminación (62). Equipo: Lucía Martínez + Daniel Alonso.</p>
                                </div>
                            </div>
                        </li>
                        <li class="px-5 py-3 hover:bg-slate-50">
                            <div class="flex items-start gap-3">
                                <div class="w-9 h-9 rounded-full bg-rose-100 text-rose-700 flex items-center justify-center text-xs font-semibold shrink-0">MJ</div>
                                <div class="flex-1">
                                    <div class="flex items-center gap-2 flex-wrap">
                                        <p class="text-xs text-slate-500">12/05/2026 · 09:30 · 15 min</p>
                                        <span class="text-[10px] px-1.5 py-0.5 rounded-full bg-rose-100 text-rose-800">Enfermería</span>
                                    </div>
                                    <p class="mt-0.5 font-medium">Toma de constantes mensual · M. José Castro (DUE)</p>
                                    <p class="text-sm text-slate-600 mt-1">TA 118/72 mmHg · FC 76 lpm · Peso 64,5 kg · SpO₂ 98%. Sin incidencias. Próxima toma: 12/06.</p>
                                </div>
                            </div>
                        </li>
                    </ol>
                    <div class="px-5 py-3 border-t border-slate-200 text-center text-xs">
                        <a href="intervenciones.html" class="text-emerald-700 hover:underline">Ver las 142 intervenciones del año →</a>
                    </div>
                </section>
'''

# === TAB FAMILIA Y ENTORNO ===
TAB_FAMILIA = '''
                <section class="grid gap-5 lg:grid-cols-3">
                    <!-- Contactos familiares -->
                    <div class="lg:col-span-2 rounded-xl border border-slate-200 bg-white overflow-hidden">
                        <div class="px-5 py-3 border-b border-slate-100 flex items-center justify-between">
                            <h2 class="text-sm font-semibold">👨‍👩‍👦 Familia y referentes</h2>
                            <button class="text-xs text-emerald-700 hover:underline">+ Añadir contacto</button>
                        </div>
                        <ul class="divide-y divide-slate-100">
                            <li class="px-5 py-3 flex items-start gap-3">
                                <div class="w-10 h-10 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center text-sm font-semibold shrink-0">CP</div>
                                <div class="flex-1">
                                    <div class="flex items-center gap-2 flex-wrap">
                                        <p class="font-medium">Carmen Pérez Llamas</p>
                                        <span class="text-[10px] px-1.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800">★ Madre · referente principal</span>
                                    </div>
                                    <p class="text-xs text-slate-500 mt-0.5">68 años · vive en Burgos · jubilada · curadora representativa</p>
                                    <div class="mt-1 flex items-center gap-3 text-xs">
                                        <span>📞 6── ── ── ──</span>
                                        <span>✉ c.perez@────.es</span>
                                        <span>📍 C/ ──── 12, 3ºA · Burgos</span>
                                    </div>
                                </div>
                                <div class="text-xs text-slate-500">Última visita<br><strong class="text-slate-700">25/05/2026</strong></div>
                            </li>
                            <li class="px-5 py-3 flex items-start gap-3">
                                <div class="w-10 h-10 rounded-full bg-slate-100 text-slate-700 flex items-center justify-center text-sm font-semibold shrink-0">AG</div>
                                <div class="flex-1">
                                    <div class="flex items-center gap-2 flex-wrap">
                                        <p class="font-medium">Antonio González Sáez</p>
                                        <span class="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-100 text-slate-700">Hermano</span>
                                    </div>
                                    <p class="text-xs text-slate-500 mt-0.5">42 años · vive en Madrid · contacto secundario</p>
                                    <div class="mt-1 flex items-center gap-3 text-xs">
                                        <span>📞 6── ── ── ──</span>
                                        <span>✉ a.gonzalez@────.com</span>
                                    </div>
                                </div>
                                <div class="text-xs text-slate-500">Última visita<br><strong class="text-slate-700">25/12/2025</strong></div>
                            </li>
                            <li class="px-5 py-3 flex items-start gap-3 opacity-70">
                                <div class="w-10 h-10 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center text-sm font-semibold shrink-0">MG</div>
                                <div class="flex-1">
                                    <div class="flex items-center gap-2 flex-wrap">
                                        <p class="font-medium line-through">Manuel González Sáez</p>
                                        <span class="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-100 text-slate-600">✝ Padre · fallecido 2019</span>
                                    </div>
                                    <p class="text-xs text-slate-500 mt-0.5">Mantenido en histórico</p>
                                </div>
                            </li>
                        </ul>
                    </div>

                    <!-- Medidas de apoyo -->
                    <aside class="rounded-xl border border-slate-200 bg-white p-5">
                        <h2 class="text-sm font-semibold mb-2">⚖ Medidas de apoyo · Ley 8/2021</h2>
                        <div class="rounded-lg bg-emerald-50 border border-emerald-200 p-3 text-sm">
                            <p class="font-semibold text-emerald-900">Curatela representativa</p>
                            <p class="text-xs text-emerald-800 mt-1">Vigente desde 14/03/2023</p>
                        </div>
                        <dl class="mt-3 space-y-2 text-xs">
                            <div>
                                <dt class="text-slate-500">Figura de apoyo</dt>
                                <dd class="font-medium">Carmen Pérez (madre)</dd>
                            </div>
                            <div>
                                <dt class="text-slate-500">Ámbito</dt>
                                <dd>Patrimonial + decisiones sanitarias mayores</dd>
                            </div>
                            <div>
                                <dt class="text-slate-500">Resolución judicial</dt>
                                <dd class="font-mono text-[11px]">Juzgado 1ª Inst. nº 4 Burgos · auto 412/2023</dd>
                            </div>
                            <div>
                                <dt class="text-slate-500">Próxima revisión</dt>
                                <dd class="text-amber-700 font-medium">14/03/2026 (vencida · iniciar tramitación)</dd>
                            </div>
                        </dl>
                    </aside>
                </section>

                <!-- Persona de referencia / entorno -->
                <section class="rounded-xl border border-slate-200 bg-white p-5">
                    <h2 class="text-sm font-semibold mb-3">🤝 Persona de referencia en el centro</h2>
                    <div class="flex items-center gap-3 p-3 rounded-lg bg-slate-50 border border-slate-200">
                        <div class="w-12 h-12 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-sm font-semibold">PR</div>
                        <div class="flex-1">
                            <p class="font-medium">Pilar Renedo Llanos</p>
                            <p class="text-xs text-slate-500">Terapeuta Ocupacional · designada por Marta el 02/02/2024</p>
                        </div>
                        <button class="text-xs text-emerald-700 hover:underline">Cambiar</button>
                    </div>
                    <p class="text-[11px] text-slate-500 mt-2">La persona de referencia es elegida por la propia persona atendida. Acompaña los hitos importantes del Plan de Vida y es interlocutora preferente con la familia.</p>
                </section>
'''

# === TAB MÉDICO Y MEDICACIÓN ===
TAB_MEDICO = '''
                <section class="grid gap-5 lg:grid-cols-3">
                    <!-- Datos clínicos esenciales -->
                    <div class="rounded-xl border-2 border-rose-200 bg-rose-50 p-4 space-y-2">
                        <h3 class="text-sm font-semibold text-rose-900">⚠ Información crítica</h3>
                        <dl class="space-y-1.5 text-sm">
                            <div>
                                <dt class="text-xs text-rose-700 font-medium">Alergias</dt>
                                <dd class="text-rose-900 font-semibold">Penicilina · AINE (verificado 2023)</dd>
                            </div>
                            <div>
                                <dt class="text-xs text-rose-700 font-medium">Grupo sanguíneo</dt>
                                <dd>A Rh+</dd>
                            </div>
                            <div>
                                <dt class="text-xs text-rose-700 font-medium">Restricciones dietéticas</dt>
                                <dd>Sin lactosa · evitar frutos secos</dd>
                            </div>
                        </dl>
                    </div>
                    <!-- Diagnósticos -->
                    <div class="lg:col-span-2 rounded-xl border border-slate-200 bg-white p-5">
                        <h3 class="text-sm font-semibold mb-3">🩺 Diagnósticos activos</h3>
                        <ul class="space-y-2 text-sm">
                            <li class="flex items-start gap-3 p-2 rounded-lg bg-slate-50">
                                <span class="font-mono text-xs text-slate-500 mt-0.5">F71.9</span>
                                <div class="flex-1">
                                    <p class="font-medium">Discapacidad intelectual moderada</p>
                                    <p class="text-xs text-slate-500">Diagnóstico principal · confirmado en informe 2009 · INSS</p>
                                </div>
                            </li>
                            <li class="flex items-start gap-3 p-2 rounded-lg bg-slate-50">
                                <span class="font-mono text-xs text-slate-500 mt-0.5">G40.9</span>
                                <div class="flex-1">
                                    <p class="font-medium">Epilepsia focal</p>
                                    <p class="text-xs text-slate-500">Controlada con medicación · última crisis 2022</p>
                                </div>
                            </li>
                            <li class="flex items-start gap-3 p-2 rounded-lg bg-slate-50">
                                <span class="font-mono text-xs text-slate-500 mt-0.5">F41.1</span>
                                <div class="flex-1">
                                    <p class="font-medium">Trastorno de ansiedad generalizada</p>
                                    <p class="text-xs text-slate-500">En seguimiento por psicología · medicación en pauta</p>
                                </div>
                            </li>
                        </ul>
                    </div>
                </section>

                <!-- Medicación actual -->
                <section class="rounded-xl border border-slate-200 bg-white overflow-hidden">
                    <div class="px-5 py-3 border-b border-slate-200 flex items-center justify-between">
                        <h3 class="text-sm font-semibold">💊 Medicación activa · 3 pautas</h3>
                        <button class="rounded-lg bg-emerald-700 text-white px-3 py-1 text-xs font-medium hover:bg-emerald-800">+ Nueva pauta</button>
                    </div>
                    <div class="overflow-x-auto">
                        <table class="w-full text-sm">
                            <thead class="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                                <tr>
                                    <th class="px-5 py-2 text-left font-medium">Medicamento</th>
                                    <th class="px-5 py-2 text-left font-medium">Pauta</th>
                                    <th class="px-5 py-2 text-left font-medium">Indicación</th>
                                    <th class="px-5 py-2 text-left font-medium">Prescriptor</th>
                                    <th class="px-5 py-2 text-left font-medium">Inicio</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100">
                                <tr>
                                    <td class="px-5 py-2.5 font-medium">Levetiracetam 500 mg</td>
                                    <td class="px-5 py-2.5">1-0-1 (oral) con comida</td>
                                    <td class="px-5 py-2.5 text-slate-600">Epilepsia</td>
                                    <td class="px-5 py-2.5 text-xs text-slate-500">Dra. Pérez (Neurología HUBU)</td>
                                    <td class="px-5 py-2.5 text-xs">14/02/2018</td>
                                </tr>
                                <tr>
                                    <td class="px-5 py-2.5 font-medium">Escitalopram 10 mg</td>
                                    <td class="px-5 py-2.5">1-0-0 (oral, mañana)</td>
                                    <td class="px-5 py-2.5 text-slate-600">Ansiedad</td>
                                    <td class="px-5 py-2.5 text-xs text-slate-500">Dr. Ruiz (Médico centro)</td>
                                    <td class="px-5 py-2.5 text-xs">22/09/2023</td>
                                </tr>
                                <tr>
                                    <td class="px-5 py-2.5 font-medium">Vitamina D₃ 1000 UI</td>
                                    <td class="px-5 py-2.5">0-1-0 (oral, comida)</td>
                                    <td class="px-5 py-2.5 text-slate-600">Suplemento</td>
                                    <td class="px-5 py-2.5 text-xs text-slate-500">Dr. Ruiz</td>
                                    <td class="px-5 py-2.5 text-xs">10/01/2025</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </section>

                <!-- Próximas citas y consultas externas -->
                <section class="grid gap-5 md:grid-cols-2">
                    <div class="rounded-xl border border-slate-200 bg-white p-5">
                        <h3 class="text-sm font-semibold mb-3">📅 Consultas externas próximas</h3>
                        <ul class="space-y-2 text-sm">
                            <li class="flex items-center justify-between p-2 rounded bg-slate-50">
                                <div>
                                    <p class="font-medium">Neurología · revisión anual</p>
                                    <p class="text-xs text-slate-500">HUBU · Dra. Pérez</p>
                                </div>
                                <div class="text-right">
                                    <p class="text-sm font-medium">18/06/2026</p>
                                    <p class="text-xs text-slate-500">11:30</p>
                                </div>
                            </li>
                            <li class="flex items-center justify-between p-2 rounded bg-slate-50">
                                <div>
                                    <p class="font-medium">Ginecología · seguimiento</p>
                                    <p class="text-xs text-slate-500">CS Burgos Norte · Dra. Martín</p>
                                </div>
                                <div class="text-right">
                                    <p class="text-sm font-medium">02/07/2026</p>
                                    <p class="text-xs text-slate-500">09:00</p>
                                </div>
                            </li>
                        </ul>
                    </div>
                    <div class="rounded-xl border border-slate-200 bg-white p-5">
                        <h3 class="text-sm font-semibold mb-3">🏥 Últimas hospitalizaciones</h3>
                        <ul class="space-y-2 text-sm text-slate-600">
                            <li class="border-l-2 border-slate-300 pl-3 py-1">
                                <p class="font-medium text-slate-900">Crisis epiléptica · observación 24h</p>
                                <p class="text-xs">HUBU · 18-19/03/2022 · alta sin secuelas</p>
                            </li>
                            <li class="border-l-2 border-slate-300 pl-3 py-1">
                                <p class="font-medium text-slate-900">Apendicectomía urgente</p>
                                <p class="text-xs">HUBU · 07-09/11/2019 · sin complicaciones</p>
                            </li>
                        </ul>
                    </div>
                </section>
'''

# === TAB DOCUMENTOS ===
TAB_DOCS = '''
                <section class="rounded-xl border border-slate-200 bg-white overflow-hidden">
                    <div class="px-5 py-3 border-b border-slate-200 flex items-center justify-between flex-wrap gap-2">
                        <div>
                            <h2 class="text-sm font-semibold">📎 Documentos del expediente</h2>
                            <p class="text-xs text-slate-500 mt-0.5">23 documentos · ordenados por fecha de subida</p>
                        </div>
                        <div class="flex items-center gap-2">
                            <select class="rounded border border-slate-300 bg-white px-2 py-1 text-xs">
                                <option>Todas las categorías</option>
                                <option>Consentimientos</option>
                                <option>Documentación legal</option>
                                <option>Informes médicos</option>
                                <option>Informes externos</option>
                                <option>Imágenes / fotografías</option>
                                <option>Familia</option>
                            </select>
                            <button class="rounded-lg bg-emerald-700 text-white px-3 py-1 text-xs font-medium hover:bg-emerald-800">⤒ Subir documento</button>
                        </div>
                    </div>
                    <ul class="divide-y divide-slate-100 text-sm">
                        <li class="px-5 py-3 flex items-center gap-3 hover:bg-slate-50">
                            <span class="text-2xl shrink-0">📄</span>
                            <div class="flex-1">
                                <p class="font-medium">Consentimiento RGPD · tratamiento de datos sociosanitarios</p>
                                <p class="text-xs text-slate-500">Firmado por Carmen Pérez (curadora) · 12/01/2026 · vigente</p>
                            </div>
                            <span class="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">Vigente</span>
                            <span class="text-xs text-slate-500">PDF · 0,8 MB</span>
                        </li>
                        <li class="px-5 py-3 flex items-center gap-3 hover:bg-slate-50">
                            <span class="text-2xl shrink-0">📄</span>
                            <div class="flex-1">
                                <p class="font-medium">Consentimiento fotografías y comunicación</p>
                                <p class="text-xs text-slate-500">Firmado por Carmen Pérez · 12/01/2026 · renovación anual</p>
                            </div>
                            <span class="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">Vigente</span>
                            <span class="text-xs text-slate-500">PDF · 0,4 MB</span>
                        </li>
                        <li class="px-5 py-3 flex items-center gap-3 hover:bg-slate-50">
                            <span class="text-2xl shrink-0">⚖</span>
                            <div class="flex-1">
                                <p class="font-medium">Auto judicial · medida de apoyo (curatela representativa)</p>
                                <p class="text-xs text-slate-500">Juzgado 1ª Inst. nº 4 Burgos · 14/03/2023</p>
                            </div>
                            <span class="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">Legal</span>
                            <span class="text-xs text-slate-500">PDF · 1,2 MB</span>
                        </li>
                        <li class="px-5 py-3 flex items-center gap-3 hover:bg-slate-50">
                            <span class="text-2xl shrink-0">📋</span>
                            <div class="flex-1">
                                <p class="font-medium">Reconocimiento grado de discapacidad 65 %</p>
                                <p class="text-xs text-slate-500">Junta de Castilla y León · revisión 2024</p>
                            </div>
                            <span class="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">Administrativo</span>
                            <span class="text-xs text-slate-500">PDF · 0,6 MB</span>
                        </li>
                        <li class="px-5 py-3 flex items-center gap-3 hover:bg-slate-50">
                            <span class="text-2xl shrink-0">📋</span>
                            <div class="flex-1">
                                <p class="font-medium">Dependencia · Grado II</p>
                                <p class="text-xs text-slate-500">Resolución BVD · Junta CyL · 2022</p>
                            </div>
                            <span class="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">Administrativo</span>
                            <span class="text-xs text-slate-500">PDF · 0,5 MB</span>
                        </li>
                        <li class="px-5 py-3 flex items-center gap-3 hover:bg-slate-50">
                            <span class="text-2xl shrink-0">🏥</span>
                            <div class="flex-1">
                                <p class="font-medium">Informe neurología · revisión anual epilepsia</p>
                                <p class="text-xs text-slate-500">HUBU · Dra. Pérez · 14/06/2025</p>
                            </div>
                            <span class="text-[10px] px-2 py-0.5 rounded-full bg-rose-100 text-rose-800">Médico</span>
                            <span class="text-xs text-slate-500">PDF · 2,1 MB</span>
                        </li>
                        <li class="px-5 py-3 flex items-center gap-3 hover:bg-slate-50">
                            <span class="text-2xl shrink-0">🎓</span>
                            <div class="flex-1">
                                <p class="font-medium">Informe escolar histórico · Colegio EE Puentesaúco</p>
                                <p class="text-xs text-slate-500">Cierre escolaridad 18 años · 2010</p>
                            </div>
                            <span class="text-[10px] px-2 py-0.5 rounded-full bg-amber-100 text-amber-800">Histórico</span>
                            <span class="text-xs text-slate-500">PDF · 3,4 MB</span>
                        </li>
                        <li class="px-5 py-3 flex items-center gap-3 hover:bg-slate-50">
                            <span class="text-2xl shrink-0">📸</span>
                            <div class="flex-1">
                                <p class="font-medium">Carpeta de fotografías autorizadas · 2026</p>
                                <p class="text-xs text-slate-500">14 fotos · uso interno y memoria anual</p>
                            </div>
                            <span class="text-[10px] px-2 py-0.5 rounded-full bg-blue-100 text-blue-800">Imágenes</span>
                            <span class="text-xs text-slate-500">14 archivos</span>
                        </li>
                    </ul>
                    <div class="px-5 py-3 border-t border-slate-200 flex items-center justify-between text-xs">
                        <p class="text-slate-600"><strong>Mostrando 1 – 8</strong> de <strong>23 documentos</strong></p>
                        <a href="#" class="text-emerald-700 hover:underline">Ver todos →</a>
                    </div>
                </section>

                <!-- Aviso retención -->
                <section class="rounded-xl bg-slate-50 border border-slate-200 p-3 text-xs text-slate-600">
                    <p>🗄 <strong>Política de retención RGPD</strong>: los documentos del expediente se conservan según el plazo legal específico de cada tipo (consentimientos: 5 años tras finalización del servicio; documentación médica: 15 años; resoluciones judiciales: permanente). Cada subida queda registrada en la bitácora.</p>
                </section>
'''

# === Reemplazos en el contenido ===
def reemplazar_tab(html_archivo, tab_id, icono, nombre, html_nuevo):
    patron = re.compile(
        rf'<div x-show="expandido \|\| tab === \'{tab_id}\'"[^>]*>.*?</div>(?=\s*<!-- )',
        re.DOTALL
    )
    bloque = envolver(tab_id, icono, nombre, html_nuevo)
    nuevo, n = patron.subn(bloque, html_archivo)
    print(f'  Tab "{tab_id}": {n} reemplazo(s)')
    return nuevo

contenido = reemplazar_tab(contenido, 'inter', '📝', 'Intervenciones y valoraciones', TAB_INTER)
contenido = reemplazar_tab(contenido, 'familia', '👨‍👩‍👦', 'Familia y entorno', TAB_FAMILIA)
contenido = reemplazar_tab(contenido, 'medico', '⚕️', 'Médico y medicación', TAB_MEDICO)

# Para docs, el patrón es ligeramente diferente (no hay <!-- después)
patron_docs = re.compile(
    r"<div x-show=\"expandido \|\| tab === 'docs'\"[^>]*>.*?</div>",
    re.DOTALL
)
bloque_docs = envolver('docs', '📎', 'Documentos', TAB_DOCS)
contenido, n = patron_docs.subn(bloque_docs, contenido, count=1)
print(f'  Tab "docs": {n} reemplazo(s)')

ruta.write_text(contenido, encoding='utf-8')
print('\nOK: 4 tabs rellenados con contenido sintético')

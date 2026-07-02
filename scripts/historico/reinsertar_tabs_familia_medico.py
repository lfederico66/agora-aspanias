"""Reinsertar tabs familia y medico que se borraron en el script anterior."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

ruta = Path(__file__).resolve().parent.parent / 'demo' / 'persona-detalle.html'
contenido = ruta.read_text(encoding='utf-8')

TAB_FAMILIA = """<div x-show="expandido || tab === 'familia'" x-cloak class="space-y-5" :class="expandido ? 'mt-6' : ''">
                <h2 x-show="expandido" x-cloak class="text-lg font-semibold tracking-tight pt-4 mt-2 border-t-2 border-emerald-200"><span class="text-xl">👨‍👩‍👦</span> Familia y entorno</h2>

                <section class="grid gap-5 lg:grid-cols-3">
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
                                    </div>
                                </div>
                                <div class="text-xs text-slate-500 text-right">Última visita<br><strong class="text-slate-700">25/05/2026</strong></div>
                            </li>
                            <li class="px-5 py-3 flex items-start gap-3">
                                <div class="w-10 h-10 rounded-full bg-slate-100 text-slate-700 flex items-center justify-center text-sm font-semibold shrink-0">AG</div>
                                <div class="flex-1">
                                    <div class="flex items-center gap-2 flex-wrap">
                                        <p class="font-medium">Antonio González Sáez</p>
                                        <span class="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-100 text-slate-700">Hermano</span>
                                    </div>
                                    <p class="text-xs text-slate-500 mt-0.5">42 años · vive en Madrid · contacto secundario</p>
                                </div>
                                <div class="text-xs text-slate-500 text-right">Última visita<br><strong class="text-slate-700">25/12/2025</strong></div>
                            </li>
                            <li class="px-5 py-3 flex items-start gap-3 opacity-70">
                                <div class="w-10 h-10 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center text-sm font-semibold shrink-0">MG</div>
                                <div class="flex-1">
                                    <div class="flex items-center gap-2 flex-wrap">
                                        <p class="font-medium line-through">Manuel González Sáez</p>
                                        <span class="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-100 text-slate-600">✝ Padre · fallecido 2019</span>
                                    </div>
                                </div>
                            </li>
                        </ul>
                    </div>

                    <aside class="rounded-xl border border-slate-200 bg-white p-5">
                        <h2 class="text-sm font-semibold mb-2">⚖ Medidas de apoyo · Ley 8/2021</h2>
                        <div class="rounded-lg bg-emerald-50 border border-emerald-200 p-3 text-sm">
                            <p class="font-semibold text-emerald-900">Curatela representativa</p>
                            <p class="text-xs text-emerald-800 mt-1">Vigente desde 14/03/2023</p>
                        </div>
                        <dl class="mt-3 space-y-2 text-xs">
                            <div><dt class="text-slate-500">Figura de apoyo</dt><dd class="font-medium">Carmen Pérez (madre)</dd></div>
                            <div><dt class="text-slate-500">Ámbito</dt><dd>Patrimonial + decisiones sanitarias mayores</dd></div>
                            <div><dt class="text-slate-500">Resolución judicial</dt><dd class="font-mono text-[11px]">Juzgado 1ª Inst. nº 4 Burgos · auto 412/2023</dd></div>
                            <div><dt class="text-slate-500">Próxima revisión</dt><dd class="text-amber-700 font-medium">14/03/2026 (vencida)</dd></div>
                        </dl>
                    </aside>
                </section>

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
                </section>
            </div>"""

TAB_MEDICO = """<div x-show="expandido || tab === 'medico'" x-cloak class="space-y-5" :class="expandido ? 'mt-6' : ''">
                <h2 x-show="expandido" x-cloak class="text-lg font-semibold tracking-tight pt-4 mt-2 border-t-2 border-emerald-200"><span class="text-xl">⚕️</span> Médico y medicación</h2>

                <section class="grid gap-5 lg:grid-cols-3">
                    <div class="rounded-xl border-2 border-rose-200 bg-rose-50 p-4 space-y-2">
                        <h3 class="text-sm font-semibold text-rose-900">⚠ Información crítica</h3>
                        <dl class="space-y-1.5 text-sm">
                            <div><dt class="text-xs text-rose-700 font-medium">Alergias</dt><dd class="text-rose-900 font-semibold">Penicilina · AINE</dd></div>
                            <div><dt class="text-xs text-rose-700 font-medium">Grupo sanguíneo</dt><dd>A Rh+</dd></div>
                            <div><dt class="text-xs text-rose-700 font-medium">Restricciones</dt><dd>Sin lactosa · evitar frutos secos</dd></div>
                        </dl>
                    </div>
                    <div class="lg:col-span-2 rounded-xl border border-slate-200 bg-white p-5">
                        <h3 class="text-sm font-semibold mb-3">🩺 Diagnósticos activos</h3>
                        <ul class="space-y-2 text-sm">
                            <li class="flex items-start gap-3 p-2 rounded-lg bg-slate-50"><span class="font-mono text-xs text-slate-500 mt-0.5">F71.9</span><div class="flex-1"><p class="font-medium">Discapacidad intelectual moderada</p><p class="text-xs text-slate-500">Confirmado en informe 2009 · INSS</p></div></li>
                            <li class="flex items-start gap-3 p-2 rounded-lg bg-slate-50"><span class="font-mono text-xs text-slate-500 mt-0.5">G40.9</span><div class="flex-1"><p class="font-medium">Epilepsia focal</p><p class="text-xs text-slate-500">Controlada · última crisis 2022</p></div></li>
                            <li class="flex items-start gap-3 p-2 rounded-lg bg-slate-50"><span class="font-mono text-xs text-slate-500 mt-0.5">F41.1</span><div class="flex-1"><p class="font-medium">Trastorno de ansiedad generalizada</p><p class="text-xs text-slate-500">En seguimiento por psicología</p></div></li>
                        </ul>
                    </div>
                </section>

                <section class="rounded-xl border border-slate-200 bg-white overflow-hidden">
                    <div class="px-5 py-3 border-b border-slate-200 flex items-center justify-between">
                        <h3 class="text-sm font-semibold">💊 Medicación activa · 3 pautas</h3>
                        <button class="rounded-lg bg-emerald-700 text-white px-3 py-1 text-xs font-medium hover:bg-emerald-800">+ Nueva pauta</button>
                    </div>
                    <div class="overflow-x-auto">
                        <table class="w-full text-sm">
                            <thead class="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                                <tr><th class="px-5 py-2 text-left font-medium">Medicamento</th><th class="px-5 py-2 text-left font-medium">Pauta</th><th class="px-5 py-2 text-left font-medium">Indicación</th><th class="px-5 py-2 text-left font-medium">Prescriptor</th><th class="px-5 py-2 text-left font-medium">Inicio</th></tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100">
                                <tr><td class="px-5 py-2.5 font-medium">Levetiracetam 500 mg</td><td class="px-5 py-2.5">1-0-1 (oral)</td><td class="px-5 py-2.5 text-slate-600">Epilepsia</td><td class="px-5 py-2.5 text-xs text-slate-500">Dra. Pérez (HUBU)</td><td class="px-5 py-2.5 text-xs">14/02/2018</td></tr>
                                <tr><td class="px-5 py-2.5 font-medium">Escitalopram 10 mg</td><td class="px-5 py-2.5">1-0-0 (oral, mañana)</td><td class="px-5 py-2.5 text-slate-600">Ansiedad</td><td class="px-5 py-2.5 text-xs text-slate-500">Dr. Ruiz (centro)</td><td class="px-5 py-2.5 text-xs">22/09/2023</td></tr>
                                <tr><td class="px-5 py-2.5 font-medium">Vitamina D₃ 1000 UI</td><td class="px-5 py-2.5">0-1-0 (oral, comida)</td><td class="px-5 py-2.5 text-slate-600">Suplemento</td><td class="px-5 py-2.5 text-xs text-slate-500">Dr. Ruiz</td><td class="px-5 py-2.5 text-xs">10/01/2025</td></tr>
                            </tbody>
                        </table>
                    </div>
                </section>

                <section class="grid gap-5 md:grid-cols-2">
                    <div class="rounded-xl border border-slate-200 bg-white p-5">
                        <h3 class="text-sm font-semibold mb-3">📅 Consultas externas próximas</h3>
                        <ul class="space-y-2 text-sm">
                            <li class="flex items-center justify-between p-2 rounded bg-slate-50"><div><p class="font-medium">Neurología · revisión anual</p><p class="text-xs text-slate-500">HUBU · Dra. Pérez</p></div><div class="text-right"><p class="text-sm font-medium">18/06/2026</p><p class="text-xs text-slate-500">11:30</p></div></li>
                            <li class="flex items-center justify-between p-2 rounded bg-slate-50"><div><p class="font-medium">Ginecología · seguimiento</p><p class="text-xs text-slate-500">CS Burgos Norte</p></div><div class="text-right"><p class="text-sm font-medium">02/07/2026</p><p class="text-xs text-slate-500">09:00</p></div></li>
                        </ul>
                    </div>
                    <div class="rounded-xl border border-slate-200 bg-white p-5">
                        <h3 class="text-sm font-semibold mb-3">🏥 Últimas hospitalizaciones</h3>
                        <ul class="space-y-2 text-sm text-slate-600">
                            <li class="border-l-2 border-slate-300 pl-3 py-1"><p class="font-medium text-slate-900">Crisis epiléptica · observación 24h</p><p class="text-xs">HUBU · 18-19/03/2022</p></li>
                            <li class="border-l-2 border-slate-300 pl-3 py-1"><p class="font-medium text-slate-900">Apendicectomía</p><p class="text-xs text-slate-500">HUBU · 07-09/11/2019</p></li>
                        </ul>
                    </div>
                </section>
            </div>"""

# Insertar antes del tab bolsillo
marca = "<div x-show=\"expandido || tab === 'bolsillo'\""
idx = contenido.find(marca)
if idx == -1:
    print("ERROR: no se encontró tab bolsillo")
    sys.exit(1)

# Detectar indentación
start_linea = contenido.rfind('\n', 0, idx) + 1
indent = contenido[start_linea:idx]

inserto = TAB_FAMILIA + '\n\n' + indent + TAB_MEDICO + '\n\n' + indent
contenido_nuevo = contenido[:idx] + inserto + contenido[idx:]
ruta.write_text(contenido_nuevo, encoding='utf-8')
print('OK: tabs familia y medico reinsertados antes del tab bolsillo')

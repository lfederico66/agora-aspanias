"""Añade el flujo Generar factura a facturacion.html."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
import re

ruta = Path(__file__).resolve().parent.parent / 'demo' / 'facturacion.html'
contenido = ruta.read_text(encoding='utf-8')

# 1. Añadir generarModal al x-data raíz
if 'generarModal:' not in contenido:
    contenido = re.sub(
        r"(<div class=\"flex min-h-screen\" x-data=\"\{[^}]*?)nuevoServ: false,",
        r"\1nuevoServ: false, generarModal: false,",
        contenido,
        count=1
    )
    print('  [OK] x-data ampliado con generarModal')

# 2. Añadir botón "Generar factura" en cabecera, antes del "+ Servicio extraordinario"
boton_servicio_anterior = '<button @click="nuevoServ = true" class="rounded-lg bg-emerald-700 text-white px-3 py-1.5 text-xs font-medium hover:bg-emerald-800">+ Servicio extraordinario</button>'
boton_servicio_nuevo = (
    '<button @click="generarModal = true" class="rounded-lg bg-emerald-700 text-white px-3 py-1.5 text-xs font-medium hover:bg-emerald-800">📄 Generar factura</button>\n'
    '                <button @click="nuevoServ = true" class="rounded-lg border border-emerald-700 text-emerald-700 px-3 py-1.5 text-xs font-medium hover:bg-emerald-50">+ Servicio extraordinario</button>'
)
if boton_servicio_anterior in contenido:
    contenido = contenido.replace(boton_servicio_anterior, boton_servicio_nuevo, 1)
    print('  [OK] Botón "Generar factura" añadido en cabecera')

# 3. Filas de facturas emitidas clicables
contenido = re.sub(
    r'<tr class="hover:bg-slate-50">(\s*<td class="px-4 py-2 font-mono text-xs">F-2026/)',
    r"""<tr class="hover:bg-slate-50 cursor-pointer" onclick="location.href='factura-detalle.html'">\1""",
    contenido
)
print('  [OK] Filas de facturas emitidas clicables')

# 4. Modal "Generar factura"
modal = """    <!-- Modal Generar factura -->
    <div x-show="generarModal" x-cloak class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm px-4" @click.self="generarModal = false">
        <div class="w-full max-w-2xl rounded-2xl bg-white shadow-2xl overflow-hidden max-h-[90vh] overflow-y-auto">
            <div class="px-5 py-3 border-b border-slate-200 flex items-center justify-between sticky top-0 bg-white z-10">
                <h3 class="font-semibold">📄 Generar factura mensual</h3>
                <button @click="generarModal = false" class="w-7 h-7 rounded-full hover:bg-slate-100 text-slate-500">✕</button>
            </div>
            <div class="p-5 space-y-4 text-sm">

                <div class="grid gap-3 md:grid-cols-3">
                    <label class="block">
                        <span class="text-xs font-medium text-slate-700">Centro</span>
                        <select x-model="centroSel" class="mt-0.5 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-emerald-500 text-sm">
                            <option value="fuentecillas">Residencia Fuentecillas</option>
                            <option value="puentesauco">Residencia Puentesaúco</option>
                            <option value="quintanaduenas">Residencia Quintanadueñas</option>
                            <option value="salas">Residencia Salas</option>
                            <option value="rio-arlanza">Residencia Río Arlanza</option>
                            <option value="santa-maria">Residencia Santa María</option>
                            <option value="v-aleixandre">C. Multiactividad V. Aleixandre</option>
                            <option value="areas-vivienda">Áreas de Vivienda</option>
                            <option value="colegio-puentesauco">Colegio EE Puentesaúco</option>
                        </select>
                    </label>
                    <label class="block">
                        <span class="text-xs font-medium text-slate-700">Persona</span>
                        <select class="mt-0.5 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-emerald-500 text-sm">
                            <option value="">— Selecciona persona —</option>
                            <template x-for="p in personasPorCentro[centroSel] || []" :key="p">
                                <option x-text="p" :value="p"></option>
                            </template>
                        </select>
                    </label>
                    <label class="block">
                        <span class="text-xs font-medium text-slate-700">Periodo</span>
                        <select class="mt-0.5 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-emerald-500 text-sm">
                            <option>Junio 2026 (en curso)</option>
                            <option>Mayo 2026</option>
                            <option>Abril 2026</option>
                            <option>Personalizado…</option>
                        </select>
                    </label>
                </div>

                <div class="rounded-lg border border-slate-200 bg-slate-50 p-4">
                    <p class="text-[10px] uppercase tracking-widest text-slate-500 font-semibold mb-2">Previsualización (cálculo automático)</p>
                    <div class="space-y-1.5 text-sm">
                        <div class="flex items-center justify-between">
                            <span>Plaza concertada (30 días · 29,28 €/día)</span>
                            <span class="font-medium">878,50 €</span>
                        </div>
                        <div class="flex items-center justify-between text-slate-600">
                            <span>+ Acompañamiento médico (2,5 h · 03/06)</span>
                            <span>35,50 €</span>
                        </div>
                        <div class="flex items-center justify-between text-slate-600">
                            <span>+ Podología (02/06)</span>
                            <span>15,00 €</span>
                        </div>
                        <div class="flex items-center justify-between text-slate-600">
                            <span>+ Kilometraje (24 km · 03/06)</span>
                            <span>6,00 €</span>
                        </div>
                        <div class="pt-2 mt-2 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500">
                            <span>IVA (exento art. 20 LIVA)</span>
                            <span>— €</span>
                        </div>
                        <div class="pt-2 border-t-2 border-slate-300 flex items-center justify-between font-bold text-emerald-700">
                            <span>TOTAL FACTURA</span>
                            <span class="text-lg">935,00 €</span>
                        </div>
                    </div>
                </div>

                <div class="grid gap-3 md:grid-cols-2">
                    <label class="block">
                        <span class="text-xs font-medium text-slate-700">Forma de pago</span>
                        <select class="mt-0.5 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-emerald-500 text-sm">
                            <option>Domiciliación SEPA</option>
                            <option>Transferencia</option>
                            <option>Efectivo (ventanilla)</option>
                        </select>
                    </label>
                    <label class="block">
                        <span class="text-xs font-medium text-slate-700">Fecha de emisión</span>
                        <input type="date" value="2026-06-05" class="mt-0.5 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-emerald-500 text-sm">
                    </label>
                </div>

                <div class="rounded-lg bg-blue-50 border border-blue-200 p-3 text-xs text-blue-800">
                    💡 Al generar, se creará la factura en estado <strong>Borrador</strong>. Podrás revisarla antes de marcarla como Emitida. La emisión definitiva queda registrada en bitácora.
                </div>
            </div>
            <div class="px-5 py-3 border-t border-slate-200 flex items-center justify-end gap-2 bg-white sticky bottom-0">
                <button @click="generarModal = false" class="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm text-slate-700 hover:border-emerald-400">Cancelar</button>
                <button @click="generarModal = false; toast = '📄 Factura F-2026/06/0042 generada en borrador'; mostrarToast = true; setTimeout(() => mostrarToast = false, 3000); setTimeout(() => window.open('factura-detalle.html', '_blank'), 600)" class="rounded-lg bg-emerald-700 text-white px-4 py-2 text-sm font-medium hover:bg-emerald-800">📄 Generar y previsualizar</button>
            </div>
        </div>
    </div>

"""

# Insertar el modal justo después del cierre del modal "nuevoServ"
# Buscar el patrón: </div> </div> seguido del modal de búsqueda Ctrl+K
patron = re.compile(r'(</div>\s*</div>\s*\n)(\s*<!-- Toast)', re.DOTALL)
m = patron.search(contenido)
if m:
    nuevo = contenido[:m.end(1)] + modal + contenido[m.end(1):]
    contenido = nuevo
    print('  [OK] Modal "Generar factura" insertado antes del toast')
else:
    # Plan B: buscar antes de </div> </div> <!-- Búsqueda
    patron2 = re.compile(r'(</div>\s*</div>\s*\n)(\s*</div>\s*\n+<div x-data="\{ open: false \}")', re.DOTALL)
    m2 = patron2.search(contenido)
    if m2:
        contenido = contenido[:m2.end(1)] + modal + contenido[m2.end(1):]
        print('  [OK] Modal insertado antes del cierre del flex (plan B)')
    else:
        print('  [ERROR] No se pudo insertar el modal automáticamente')

ruta.write_text(contenido, encoding='utf-8')

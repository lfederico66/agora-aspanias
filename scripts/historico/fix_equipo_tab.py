"""Reescribe la sección Equipo de centro-detalle.html con cards clickables."""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ruta = Path('demo/centro-detalle.html')
c = ruta.read_text(encoding='utf-8')

inicio = c.find('<div x-show="tab === \'equipo\'')
fin_grid = c.find('<div class="mt-4 pt-3 border-t border-slate-100', inicio)

print(f'Inicio tab equipo: {inicio}')
print(f'Inicio pie:       {fin_grid}')

card = (
    '<a href="profesional-detalle.html" class="flex items-center gap-3 p-3 rounded-lg border border-slate-100 hover:bg-emerald-50/40 hover:border-emerald-200 transition">'
    '<div class="w-10 h-10 rounded-full {ring} flex items-center justify-center text-xs font-semibold shrink-0">{ini}</div>'
    '<div class="flex-1 min-w-0"><p class="text-sm font-medium truncate">{nombre}</p>'
    '<p class="text-xs text-slate-500 truncate">{rol}</p></div>'
    '<span class="text-[10px] px-1.5 py-0.5 rounded-full {badge} shrink-0">{badge_txt}</span>'
    '</a>'
)

profes = [
    ('LM', 'Lucía Martínez Andrés',     'Coordinadora · Trabajadora Social', 'bg-emerald-100 text-emerald-800', 'bg-emerald-100 text-emerald-800', '★ Coord.'),
    ('AR', 'Dr. Antonio Ruiz',          'Médico',                            'bg-slate-100 text-slate-700',     'bg-emerald-100 text-emerald-800', 'En activo'),
    ('MJ', 'M. José Castro',            'DUE · Enfermería',                  'bg-slate-100 text-slate-700',     'bg-emerald-100 text-emerald-800', 'En activo'),
    ('DA', 'Daniel Alonso',             'Psicólogo',                         'bg-slate-100 text-slate-700',     'bg-emerald-100 text-emerald-800', 'En activo'),
    ('PR', 'Pilar Renedo',              'Terapeuta Ocupacional',             'bg-slate-100 text-slate-700',     'bg-sky-100 text-sky-800',         '🏖 Vac.'),
    ('SN', 'Sergio Núñez',              'Fisioterapeuta',                    'bg-slate-100 text-slate-700',     'bg-emerald-100 text-emerald-800', 'En activo'),
    ('LP', 'López Pérez, Marta',        'Gerocultora · Gestora caso',        'bg-emerald-100 text-emerald-800', 'bg-rose-100 text-rose-800',       '⚕ IT'),
    ('RS', 'Ruiz Sánchez, Ana',         'Gerocultora',                       'bg-slate-100 text-slate-700',     'bg-emerald-100 text-emerald-800', 'En activo'),
    ('CM', 'Cano Martín, Rosa',         'Gerocultora',                       'bg-slate-100 text-slate-700',     'bg-amber-100 text-amber-800',     '+4 h extra'),
    ('GL', 'García López, Inés',        'Gerocultora',                       'bg-slate-100 text-slate-700',     'bg-emerald-100 text-emerald-800', 'En activo'),
    ('PC', 'Pérez Calderón, A.',        'Gerocultora · turno tarde',         'bg-slate-100 text-slate-700',     'bg-emerald-100 text-emerald-800', 'En activo'),
    ('BS', 'Bárcena Sanz, R.',          'Dirección de centro',               'bg-slate-100 text-slate-700',     'bg-emerald-100 text-emerald-800', '★ Dir.'),
    ('+1', '+ 1 profesional más',       'Personal apoyo (sustitución)',      'bg-slate-100 text-slate-700',     'bg-slate-100 text-slate-700',     'Refuerzo'),
]

cards_html = '\n                        '.join(
    card.format(ini=ini, nombre=n, rol=r, ring=ring, badge=badge, badge_txt=bt)
    for ini, n, r, ring, badge, bt in profes
)

nuevo_bloque = (
    '<div x-show="tab === \'equipo\'" x-cloak class="p-5">\n'
    '                    <!-- Barra de acceso al módulo Equipo -->\n'
    '                    <div class="mb-4 flex items-center justify-between p-3 rounded-lg border border-emerald-200 bg-emerald-50/60">\n'
    '                        <div>\n'
    '                            <p class="text-sm font-semibold text-emerald-900">🧑‍💼 Plantilla del centro</p>\n'
    '                            <p class="text-xs text-emerald-800">14 profesionales · 11 en activo · 1 vacaciones · 1 IT · 1 refuerzo</p>\n'
    '                        </div>\n'
    '                        <div class="flex gap-2">\n'
    '                            <a href="vacaciones.html" class="px-3 py-1.5 text-xs rounded border border-emerald-300 bg-white text-emerald-800 hover:bg-emerald-100 font-medium">🏖 Vacaciones</a>\n'
    '                            <a href="turnos.html" class="px-3 py-1.5 text-xs rounded border border-emerald-300 bg-white text-emerald-800 hover:bg-emerald-100 font-medium">🕒 Turnos</a>\n'
    '                            <a href="profesionales.html" class="px-3 py-1.5 text-xs rounded bg-emerald-700 text-white hover:bg-emerald-800 font-medium">Ver todos →</a>\n'
    '                        </div>\n'
    '                    </div>\n'
    '                    <div class="grid gap-3 md:grid-cols-2">\n'
    '                        ' + cards_html + '\n'
    '                    </div>\n'
    '                    '
)

c_nuevo = c[:inicio] + nuevo_bloque + c[fin_grid:]
ruta.write_text(c_nuevo, encoding='utf-8')
print(f'OK reescrito · {len(profes)} cards clickables · barra superior con accesos directos')

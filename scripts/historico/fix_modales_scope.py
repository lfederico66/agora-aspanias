"""Mueve los modales que usan variables del x-data raíz dentro del scope."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
import re

DEMO = Path(__file__).resolve().parent.parent / 'demo'

# Para cada archivo, identificar los modales y moverlos
# Estrategia: encontrar bloques x-show="VAR" donde VAR es una variable del x-data raíz
# y mover el bloque entero antes del cierre del </div> raíz

ARCHIVOS_VARS = {
    'caja-centro.html': ['arqueoModal'],
    'facturacion.html': ['nuevoServ'],
}

for archivo_nombre, variables in ARCHIVOS_VARS.items():
    ruta = DEMO / archivo_nombre
    contenido = ruta.read_text(encoding='utf-8')

    for var in variables:
        # Buscar el modal completo: <div x-show="VAR" ...>...</div> al mismo nivel de indentación
        # Como tienen profundidad variable, buscamos hasta el </div> que tenga el mismo
        # punto de indentación que el <div> de apertura

        # Patrón más simple: comentario "<!-- Modal" antes del bloque
        patron_modal_con_comentario = re.compile(
            rf'(<!-- [^>]*odal[^>]* -->\s*)?<div x-show="{re.escape(var)}"[^>]*>.*?(?=\n\n)',
            re.DOTALL
        )
        # No funcionará bien sin parser HTML real. Mejor uso un balanceo simple:

        # Buscar inicio del modal
        m_inicio = re.search(rf'<div x-show="{re.escape(var)}"', contenido)
        if not m_inicio:
            print(f'  [SKIP] {archivo_nombre}: x-show="{var}" no encontrado')
            continue

        # Buscar comentario justo antes del modal
        inicio_modal = m_inicio.start()
        # Buscar hacia atrás un <!-- comentario --> en la misma indentación
        antes = contenido[:inicio_modal]
        m_comment = re.search(r'<!--[^>]*odal[^>]*-->\s*$', antes, re.MULTILINE)
        if m_comment:
            inicio_modal = m_comment.start()

        # Buscar el cierre del modal: balanceo de divs
        # Empezamos en m_inicio.start() y avanzamos contando <div> y </div>
        depth = 0
        i = m_inicio.start()
        n = len(contenido)
        # Avanzar hasta encontrar el primer <div, lo cuenta como abierto
        while i < n:
            if contenido[i:i+5] == '<div ' or contenido[i:i+4] == '<div':
                depth += 1
                # Saltar hasta el cierre del tag <div ...>
                j = contenido.find('>', i)
                if j == -1: break
                i = j + 1
            elif contenido[i:i+6] == '</div>':
                depth -= 1
                if depth == 0:
                    fin_modal = i + 6
                    break
                i += 6
            else:
                i += 1
        else:
            print(f'  [ERROR] {archivo_nombre}: no se encontró fin del modal de "{var}"')
            continue

        modal_completo = contenido[inicio_modal:fin_modal]

        # Eliminar el modal de su posición
        contenido_sin_modal = contenido[:inicio_modal] + contenido[fin_modal:]
        # Limpiar líneas en blanco extra
        contenido_sin_modal = re.sub(r'\n\n\n+', '\n\n', contenido_sin_modal)

        # Localizar el cierre del flex min-h-screen (es el </div> que viene tras </main>)
        m_cierre = re.search(r'</main>\s*</div>', contenido_sin_modal)
        if not m_cierre:
            print(f'  [ERROR] {archivo_nombre}: no se encontró </main></div> raíz')
            continue

        # Insertar el modal ANTES de ese </div> de cierre (es decir, después de </main>)
        pos_insert = m_cierre.start() + len('</main>')
        nuevo = (
            contenido_sin_modal[:pos_insert]
            + '\n\n    ' + modal_completo + '\n'
            + contenido_sin_modal[pos_insert:]
        )

        contenido = nuevo
        print(f'  [OK] {archivo_nombre}: modal "{var}" movido dentro del scope x-data raíz')

    ruta.write_text(contenido, encoding='utf-8')

print('\nHecho')

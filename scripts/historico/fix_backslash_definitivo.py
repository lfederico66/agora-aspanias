"""Fix definitivo: eliminar todos los backslash + apóstrofe en atributos HTML."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

DEMO = Path(__file__).resolve().parent.parent / 'demo'
PATRON = chr(92) + chr(39)  # \' literal de 2 caracteres
REPLACE = chr(39)             # '

total = 0
for archivo in sorted(DEMO.glob('*.html')):
    contenido = archivo.read_text(encoding='utf-8')
    n = contenido.count(PATRON)
    if n:
        nuevo = contenido.replace(PATRON, REPLACE)
        archivo.write_text(nuevo, encoding='utf-8')
        total += n
        print(f'  [OK] {archivo.name}: {n}')

print(f'\nTotal: {total}')

# Verificación final
print('\nVerificación: archivos que aún contienen el patrón:')
for archivo in DEMO.glob('*.html'):
    c = archivo.read_text(encoding='utf-8')
    n = c.count(PATRON)
    if n:
        print(f'  AÚN HAY {n} en {archivo.name}')

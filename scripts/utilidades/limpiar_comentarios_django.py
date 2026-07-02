"""Eliminar comentarios de plantilla Django {# ... #} de los HTMLs estáticos.

En Django, {# comentario #} es válido. En HTML puro NO se interpreta y aparece
como texto literal en la página renderizada.

Convierte cada {# ... #} en comentario HTML <!-- ... --> (o lo elimina si esta
en una linea sola, para no dejar lineas en blanco).
"""
from __future__ import annotations

import re
from pathlib import Path

DEMO = Path(__file__).resolve().parent.parent / "demo"

# Patrón: captura {# texto #} (no greedy), con o sin saltos de línea internos
PATRON = re.compile(r"\{#\s*(.*?)\s*#\}", re.DOTALL)


def procesar_archivo(ruta: Path) -> int:
    contenido = ruta.read_text(encoding="utf-8")
    original = contenido
    # Convertir {# texto #} -> <!-- texto -->
    nuevo = PATRON.sub(lambda m: f"<!-- {m.group(1)} -->", contenido)
    if nuevo != original:
        # Contar reemplazos
        n = len(PATRON.findall(original))
        ruta.write_text(nuevo, encoding="utf-8")
        return n
    return 0


def main() -> None:
    archivos = sorted(DEMO.glob("*.html"))
    print(f"[*] Demo dir: {DEMO}")
    print(f"[*] {len(archivos)} HTMLs a revisar\n")
    afectados = 0
    total = 0
    for archivo in archivos:
        n = procesar_archivo(archivo)
        if n:
            afectados += 1
            total += n
            print(f"[OK] {archivo.name}: {n} comentarios convertidos")
    print(f"\n[*] Archivos modificados: {afectados}/{len(archivos)}")
    print(f"[*] Comentarios reemplazados: {total}")


if __name__ == "__main__":
    main()

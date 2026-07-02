"""Elimina breadcrumbs duplicados que quedaron del contenido viejo de cada pagina.

El shell nuevo ya pone un breadcrumb sticky arriba. Las paginas viejas tenian
ANTES su propio breadcrumb interno tipo:

    <nav class="text-xs text-slate-500">
        <a href="index.html" class="hover:text-emerald-700">Inicio</a>
        <span class="mx-1">>=</span>
        <span class="text-slate-700">Centros</span>
    </nav>

Esto ahora aparece duplicado. Lo elimino: solo dejo el del shell.
"""
from __future__ import annotations

import re
from pathlib import Path

DEMO = Path(__file__).resolve().parent.parent / "demo"

# Patron del breadcrumb VIEJO (dentro del main, no en el shell sticky)
# Caracteristica: <nav class="text-xs text-slate-500"> con <a href="index.html"> dentro
PATRON_NAV_VIEJO = re.compile(
    r'<nav class="text-xs text-slate-500">\s*<a href="index\.html"[^>]*>Inicio</a>.*?</nav>',
    re.DOTALL,
)


def procesar_archivo(ruta: Path) -> int:
    contenido = ruta.read_text(encoding="utf-8")
    # El patron solo machea breadcrumbs ANTIGUOS (sin 'truncate'). El del shell
    # tiene "text-slate-500 truncate" y por tanto NO entra en este regex.
    # Cualquier coincidencia aqui es un duplicado a eliminar.
    matches = list(PATRON_NAV_VIEJO.finditer(contenido))
    if not matches:
        return 0
    nuevo = contenido
    for m in reversed(matches):
        nuevo = nuevo[: m.start()] + nuevo[m.end():]
    if nuevo != contenido:
        ruta.write_text(nuevo, encoding="utf-8")
        return len(matches)
    return 0


def main() -> None:
    print("=== Limpiando breadcrumbs duplicados ===\n")
    total = 0
    for archivo in sorted(DEMO.glob("*.html")):
        n = procesar_archivo(archivo)
        if n:
            total += n
            print(f"  [OK] {archivo.name}: {n} breadcrumb(s) duplicado(s) eliminado(s)")
    print(f"\nTotal eliminados: {total}")


if __name__ == "__main__":
    main()

"""Refactor masivo: actualizar "13 centros" -> "15 centros" en toda la demo.

Tambien arregla otras variantes:
- "13 centros" -> "15 centros"
- "13</span><span>centros</span>" (raro) -> "15</span><span>centros</span>"
- Cifras: "13" cuando claramente refiere a centros (precaucion: solo si esta junto a "centros")

Ejecutar:
    python scripts/refactor_centros_count.py
"""
from __future__ import annotations

import re
from pathlib import Path

DEMO_DIR = Path(__file__).resolve().parent.parent / "demo"

# (regex, reemplazo, descripcion)
REGLAS = [
    (re.compile(r"13\s+centros"), "15 centros", '"13 centros" -> "15 centros"'),
    # En aspanias-cifras.html aparece "13" como cifra dentro de un <p> al lado de "Centros" como label
    # Es delicado, hacemos por contexto: " 13 " entre tags p y con "Centros" cerca
    (re.compile(r">13<(?=[^>]*>\s*Centros)"), ">15<", '"13" -> "15" en KPIs (Centros)'),
]


def procesar_archivo(ruta: Path) -> tuple[int, list[str]]:
    """Devuelve (cambios_totales, lista_descripcion)."""
    contenido = ruta.read_text(encoding="utf-8")
    original = contenido
    detalles = []
    for patron, reemplazo, desc in REGLAS:
        nuevo, n = patron.subn(reemplazo, contenido)
        if n:
            detalles.append(f"  - {desc}: {n} cambios")
            contenido = nuevo
    if contenido != original:
        ruta.write_text(contenido, encoding="utf-8")
    return (len(detalles) > 0, detalles)


def main() -> None:
    archivos = sorted(DEMO_DIR.glob("*.html"))
    print(f"[*] Demo dir: {DEMO_DIR}")
    print(f"[*] {len(archivos)} HTMLs a revisar\n")
    afectados = 0
    for archivo in archivos:
        cambio, detalles = procesar_archivo(archivo)
        if cambio:
            afectados += 1
            print(f"[OK] {archivo.name}")
            for d in detalles:
                print(d)
    print(f"\n[*] Total archivos modificados: {afectados}/{len(archivos)}")


if __name__ == "__main__":
    main()

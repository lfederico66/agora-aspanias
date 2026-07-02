"""Refactor de nombres de centros antiguos -> reales en la demo.

NO toca:
- demo/centros.html (ya rehecho a mano)
- demo/aspanias-cifras.html (ya editado a mano: SVG, KPI, lista 15)

Mapeo OLD -> NEW (segun la estructura oficial del Grupo Social Aspanias):
"""
from __future__ import annotations

from pathlib import Path

DEMO_DIR = Path(__file__).resolve().parent.parent / "demo"

EXCLUIR = {"centros.html", "aspanias-cifras.html"}

# Orden importa: primero los mas largos para no romper subcadenas
MAPEO: list[tuple[str, str]] = [
    # Variantes residencias y viviendas (mas especificas primero)
    ("Vivienda San Pedro y San Felices", "Áreas de Vivienda"),
    ("San Pedro y San Felices",          "Áreas de Vivienda"),
    ("Residencia Fuentecillas",          "Centro Integral Fuentecillas"),
    ("Vivienda Villadiego",              "Residencia Santa María"),
    ("Vivienda Lara",                    "Residencia Quintanadueñas"),

    # Centros ocupacionales y de día antiguos
    ("CO Las Calzadas",                  "C. Multiactividad V. Aleixandre"),
    ("CD Las Calzadas",                  "CD Aspanias Puentesaúco"),
    ("CD Río Arlanza",                   "CD Aspanias Quintanadueñas"),
    ("Centro Promoción Personal Salas",  "CD Aspanias Salas"),
    ("Promoción Personal Salas",         "CD Aspanias Salas"),

    # Inserción
    ("CISA Inserción",                   "Servicio Puentes"),
    ("CISA EMPLEA",                      "U. Asistencial Salas"),
    ("Asociación Aspanias",              "U. Asistencial Quintanadueñas"),
    ("Programa Familias",                "Colegio EE Puentesaúco"),
]


def procesar_archivo(ruta: Path) -> int:
    contenido = ruta.read_text(encoding="utf-8")
    original = contenido
    n_total = 0
    for viejo, nuevo in MAPEO:
        if viejo in contenido:
            n = contenido.count(viejo)
            contenido = contenido.replace(viejo, nuevo)
            n_total += n
    if contenido != original:
        ruta.write_text(contenido, encoding="utf-8")
    return n_total


def main() -> None:
    archivos = sorted(
        f for f in DEMO_DIR.glob("*.html")
        if f.name not in EXCLUIR
    )
    print(f"[*] Demo dir: {DEMO_DIR}")
    print(f"[*] Excluidos: {sorted(EXCLUIR)}")
    print(f"[*] {len(archivos)} HTMLs a revisar\n")
    afectados = 0
    total_cambios = 0
    for archivo in archivos:
        n = procesar_archivo(archivo)
        if n:
            afectados += 1
            total_cambios += n
            print(f"[OK] {archivo.name}: {n} sustituciones")
    print(f"\n[*] Archivos modificados: {afectados}/{len(archivos)}")
    print(f"[*] Sustituciones totales: {total_cambios}")


if __name__ == "__main__":
    main()

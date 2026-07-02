"""Rebrand SIPAS → ÁGORA.

Aplica reemplazos controlados en todos los archivos del repo, registrando
qué cambia y dónde. NO renombra archivos ni carpetas — eso se hace aparte
con `git mv` o `Move-Item` para conservar trazabilidad.

Uso:
    python scripts/rebrand_sipas_to_agora.py             # modo dry-run
    python scripts/rebrand_sipas_to_agora.py --apply     # aplica cambios
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# ----- Configuración -----

ROOT = Path(__file__).resolve().parent.parent

# Extensiones a procesar (texto)
EXTENSIONS = {
    ".md", ".html", ".py", ".txt", ".bat", ".cfg", ".toml",
    ".yml", ".yaml", ".json", ".ini", ".env", ".env.example",
    ".css", ".js",
}

# Directorios a excluir
EXCLUDE_DIRS = {
    "__pycache__", ".git", "node_modules", "staticfiles", "media",
    ".venv", "venv", ".idea", ".vscode", "_tmp",
}

# Reemplazos (orden importa — los más largos primero)
REEMPLAZOS_GLOBALES = [
    # Frase larga: nombre completo
    (
        "Sistema de Información de Personas Atendidas",
        "Atención y Gestión Operativa para Residentes y Atendidos",
    ),
    # Acrónimo en mayúsculas — siempre seguro
    ("SIPAS", "ÁGORA"),
]

# Reemplazos solo en .py (imports del paquete config)
REEMPLAZOS_PYTHON = [
    ("sipas.settings", "agora.settings"),
    ("sipas.urls", "agora.urls"),
    ("sipas.wsgi", "agora.wsgi"),
    ("sipas.asgi", "agora.asgi"),
    ("'sipas'", "'agora'"),
    ('"sipas"', '"agora"'),
]


def es_archivo_procesable(p: Path) -> bool:
    if not p.is_file():
        return False
    if p.suffix not in EXTENSIONS:
        return False
    for parte in p.parts:
        if parte in EXCLUDE_DIRS:
            return False
    # No tocar el propio script de migración
    if p.name == "rebrand_sipas_to_agora.py":
        return False
    return True


def aplicar_reemplazos(texto: str, archivo: Path) -> tuple[str, list[tuple[str, str, int]]]:
    """Aplica reemplazos al texto, devuelve nuevo texto + lista de (orig, nuevo, n_aplicados)."""
    log = []
    nuevo = texto
    reglas = list(REEMPLAZOS_GLOBALES)
    if archivo.suffix == ".py":
        reglas = REEMPLAZOS_PYTHON + reglas
    for orig, dest in reglas:
        n = nuevo.count(orig)
        if n > 0:
            nuevo = nuevo.replace(orig, dest)
            log.append((orig, dest, n))
    return nuevo, log


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Aplica los cambios. Sin esta flag es dry-run.")
    args = parser.parse_args()

    archivos_tocados = 0
    sustituciones_totales = 0
    detalle = []

    for p in ROOT.rglob("*"):
        if not es_archivo_procesable(p):
            continue
        try:
            texto = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                texto = p.read_text(encoding="cp1252")
            except Exception as e:
                print(f"  [SKIP] {p.relative_to(ROOT)} — encoding: {e}")
                continue

        nuevo, log = aplicar_reemplazos(texto, p)
        if not log:
            continue

        rel = p.relative_to(ROOT)
        n_arch = sum(n for _, _, n in log)
        archivos_tocados += 1
        sustituciones_totales += n_arch
        detalle.append((rel, log))

        if args.apply:
            p.write_text(nuevo, encoding="utf-8")

    accion = "APLICADO" if args.apply else "DRY-RUN"
    print(f"\n[{accion}] {archivos_tocados} archivos modificados, {sustituciones_totales} sustituciones.")
    print()
    for rel, log in detalle:
        total = sum(n for _, _, n in log)
        print(f"  {rel} ({total})")
        for orig, dest, n in log:
            print(f"     {n}x  '{orig[:50]}' -> '{dest[:50]}'")
    if not args.apply:
        print("\nEjecuta con --apply para aplicar los cambios.")


if __name__ == "__main__":
    main()

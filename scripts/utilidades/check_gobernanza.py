"""
check_gobernanza.py — Linter de las 3 reglas de gobernanza UX (CLAUDE.md).

Uso:
    python scripts/utilidades/check_gobernanza.py            # check + reporte
    python scripts/utilidades/check_gobernanza.py --strict   # warnings como errores
    python scripts/utilidades/check_gobernanza.py --fix      # inserta @rol con valor por defecto

Reglas validadas:
  R1 — 7±2: bloques de tabs <nav> con border-b-2 no superan 7 elementos sin agrupación.
  R2 — Usuario único: cada HTML demo declara `<!-- @rol: ... -->` en las primeras 30 líneas.
  R3 — Sin acentos: nombres de archivos .py/.ps1/.sh no contienen acentos.

Salida:
  exit 0 — sin errores (warnings permitidos)
  exit 1 — al menos 1 error (o warning con --strict)

Integrado en CI (.github/workflows/ci.yml) como step del job demo.
"""
import argparse
import re
import sys
import unicodedata
from pathlib import Path

# Forzar UTF-8 en stdout (cp1252 por defecto en Windows)
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


# Roles canónicos (deben coincidir con docs/MAPA_ROLES.md)
ROLES_CANONICOS = {
    'gerencia', 'direccion_centro', 'gestor_caso',
    'profesional', 'rrhh', 'familia',
}


def _esta_en(carpeta: str, ruta: Path) -> bool:
    return any(part == carpeta for part in ruta.parts)


# ──────────────────────────────────────────────────────────────────
# R1 — 7±2
# ──────────────────────────────────────────────────────────────────
def revisar_r1_tabs(demo: Path) -> list[dict]:
    """Detecta bloques <nav> con > 7 items <a>/<button> sin agrupación interna."""
    errores = []
    re_nav_block = re.compile(
        r'<nav[^>]*class="[^"]*flex[^"]*-mb-px[^"]*"[^>]*>(.*?)</nav>',
        re.DOTALL,
    )
    re_item = re.compile(r'<(?:a|button)[^>]*class="[^"]*border-b-2[^"]*"', re.DOTALL)

    for ruta in sorted(demo.glob('*.html')):
        if ruta.name.startswith('_'):
            continue
        c = ruta.read_text(encoding='utf-8')
        for m in re_nav_block.finditer(c):
            bloque = m.group(1)
            items = re_item.findall(bloque)
            if len(items) > 7:
                # Permitir si hay agrupación (separadores tipo <span class="text-slate-300">|</span>)
                tiene_agrupacion = (
                    '<details' in bloque
                    or 'role="group"' in bloque
                    or bloque.count('<span class="text-slate-300">|</span>') >= 1
                )
                if not tiene_agrupacion:
                    errores.append({
                        'tipo': 'error',
                        'regla': 'R1 (7±2)',
                        'archivo': str(ruta.relative_to(demo.parent)),
                        'mensaje': f'bloque de tabs con {len(items)} items, '
                                   f'agrupar antes de superar 7',
                    })
    return errores


# ──────────────────────────────────────────────────────────────────
# R2 — usuario único (@rol)
# ──────────────────────────────────────────────────────────────────
def revisar_r2_rol(demo: Path, fix: bool = False) -> list[dict]:
    """Cada HTML demo debe tener `<!-- @rol: ... -->` en las primeras 30 líneas."""
    warnings = []
    re_rol = re.compile(r'<!--\s*@rol\s*:\s*([\w_,\s]+?)\s*-->')

    for ruta in sorted(demo.glob('*.html')):
        if ruta.name.startswith('_'):
            continue
        # Documentos imprimibles (PDFs) no requieren @rol — son artefactos generados
        if 'documento-' in ruta.name or 'factura-detalle' in ruta.name or 'calendario-individual-pdf' in ruta.name:
            continue
        c = ruta.read_text(encoding='utf-8')
        primeras = '\n'.join(c.splitlines()[:30])
        m = re_rol.search(primeras)
        if not m:
            if fix:
                # Insertar @rol gerencia por defecto justo después de <!DOCTYPE html>
                if '<!DOCTYPE html>' in c:
                    c = c.replace(
                        '<!DOCTYPE html>',
                        '<!-- @rol: gerencia -->\n<!DOCTYPE html>',
                        1,
                    )
                    ruta.write_text(c, encoding='utf-8')
                    warnings.append({
                        'tipo': 'fix',
                        'regla': 'R2 (@rol)',
                        'archivo': str(ruta.relative_to(demo.parent)),
                        'mensaje': 'insertado @rol gerencia (revisar y ajustar)',
                    })
            else:
                warnings.append({
                    'tipo': 'warning',
                    'regla': 'R2 (@rol)',
                    'archivo': str(ruta.relative_to(demo.parent)),
                    'mensaje': 'falta `<!-- @rol: ... -->` en las primeras 30 líneas',
                })
        else:
            roles_declarados = {r.strip() for r in m.group(1).split(',')}
            no_canonicos = roles_declarados - ROLES_CANONICOS
            if no_canonicos:
                warnings.append({
                    'tipo': 'error',
                    'regla': 'R2 (@rol)',
                    'archivo': str(ruta.relative_to(demo.parent)),
                    'mensaje': f'rol(es) no canónico(s): {", ".join(sorted(no_canonicos))}',
                })
    return warnings


# ──────────────────────────────────────────────────────────────────
# R3 — sin acentos en nombres de archivo de código
# ──────────────────────────────────────────────────────────────────
def revisar_r3_acentos(root: Path) -> list[dict]:
    """Nombres de archivo .py/.ps1/.sh no deben contener caracteres no-ASCII."""
    errores = []
    # Solo dentro del repo (saltar _PARA_REVISAR, dist, .venv, etc.)
    saltar = {'_PARA_REVISAR', 'dist', '.venv', '__pycache__', 'node_modules', '.git'}

    for ext in ('*.py', '*.ps1', '*.sh', '*.bat'):
        for p in root.rglob(ext):
            if any(part in saltar for part in p.parts):
                continue
            nombre = p.name
            normalizado = unicodedata.normalize('NFD', nombre)
            sin_acentos = ''.join(c for c in normalizado if not unicodedata.combining(c))
            if nombre != sin_acentos or any(ord(c) > 127 for c in nombre):
                errores.append({
                    'tipo': 'error',
                    'regla': 'R3 (acentos)',
                    'archivo': str(p.relative_to(root)),
                    'mensaje': f'nombre con caracteres no-ASCII; renombrar a "{sin_acentos}"',
                })
    return errores


# ──────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--strict', action='store_true',
                        help='warnings cuentan como errores')
    parser.add_argument('--fix', action='store_true',
                        help='inserta @rol gerencia donde falte')
    parser.add_argument('--root', type=Path, default=Path.cwd())
    args = parser.parse_args()

    root = args.root.resolve()
    demo = root / 'demo'

    hallazgos = []
    hallazgos.extend(revisar_r1_tabs(demo))
    hallazgos.extend(revisar_r2_rol(demo, fix=args.fix))
    hallazgos.extend(revisar_r3_acentos(root))

    errores = [h for h in hallazgos if h['tipo'] == 'error']
    warnings = [h for h in hallazgos if h['tipo'] == 'warning']
    fixes = [h for h in hallazgos if h['tipo'] == 'fix']

    if fixes:
        print(f'\n🔧 FIXES aplicados ({len(fixes)}):')
        for h in fixes:
            print(f'  + [{h["regla"]}] {h["archivo"]}: {h["mensaje"]}')

    if errores:
        print(f'\n❌ ERRORES ({len(errores)}):')
        for h in errores:
            print(f'  ! [{h["regla"]}] {h["archivo"]}: {h["mensaje"]}')

    if warnings:
        print(f'\n⚠ WARNINGS ({len(warnings)}):')
        for h in warnings[:20]:
            print(f'  · [{h["regla"]}] {h["archivo"]}: {h["mensaje"]}')
        if len(warnings) > 20:
            print(f'  · ... y {len(warnings) - 20} más')

    print(f'\n━━━ Resumen ━━━')
    print(f'  Errores:  {len(errores)}')
    print(f'  Warnings: {len(warnings)}')
    if args.fix:
        print(f'  Fixes:    {len(fixes)}')

    if errores or (args.strict and warnings):
        sys.exit(1)

    print('\n✓ Gobernanza UX: OK')


if __name__ == '__main__':
    main()

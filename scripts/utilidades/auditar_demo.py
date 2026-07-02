"""Auditoria exhaustiva de la demo: detecta inconsistencias visuales y de contenido."""
from __future__ import annotations

import re
from pathlib import Path
from collections import defaultdict

DEMO = Path(__file__).resolve().parent.parent / "demo"
HTMLS = sorted(DEMO.glob("*.html"))

INFORME: dict[str, list[str]] = defaultdict(list)


def add(archivo: str, problema: str) -> None:
    INFORME[archivo].append(problema)


# === Checks ===
patron_href = re.compile(r'href="([a-z0-9_-]+\.html)(?:\?[^"]*)?"')
patron_django_comment = re.compile(r"\{#|#\}|\{%|%\}")
patron_djvar = re.compile(r"\{\{[^}]*\}\}")
patron_acentos_rotos = re.compile(r"Ã©|Ã³|Ã¡|Ãº|Ã±|Ã­|Â°")
patron_aria_role = re.compile(r"\brole\s*=\s*\"")

existentes = {f.name for f in HTMLS}

for archivo in HTMLS:
    contenido = archivo.read_text(encoding="utf-8")
    nombre = archivo.name

    # 1. Django comments residuales
    if patron_django_comment.search(contenido):
        add(nombre, "Restos de sintaxis Django {# %} sin convertir")

    # 2. Variables Django sin renderizar
    if patron_djvar.search(contenido):
        add(nombre, "Variables {{ ... }} sin renderizar")

    # 3. Acentos rotos UTF-8
    if patron_acentos_rotos.search(contenido):
        add(nombre, "Acentos mal codificados (Ã©, Ã³, etc.)")

    # 4. Enlaces rotos
    destinos = set(patron_href.findall(contenido))
    rotos = destinos - existentes
    for r in rotos:
        add(nombre, f"Enlace roto -> {r} (no existe)")

    # 5. Falta cargar Alpine
    if "x-data" in contenido and "alpine.min.js" not in contenido and "alpinejs.org" not in contenido:
        add(nombre, "Usa x-data pero NO carga Alpine.js")

    # 6. CDN externo bloqueable (jsdelivr, unpkg)
    if "cdn.jsdelivr.net" in contenido or "unpkg.com" in contenido:
        add(nombre, "Carga JS desde CDN bloqueable (jsdelivr/unpkg)")

    # 7. Falta Tailwind
    if "tailwindcss.com" not in contenido and "tailwind" not in contenido:
        add(nombre, "No carga TailwindCSS")

    # 8. Restos de marca antigua
    if "SIPAS" in contenido:
        add(nombre, 'Marca antigua "SIPAS" sin migrar a ÁGORA')

    # 9. Restos de cifras antiguas
    if re.search(r"\b13 centros\b", contenido):
        add(nombre, '"13 centros" -> debe ser "15 centros"')

    # 10. Restos de centros antiguos
    centros_obsoletos = [
        "San Pedro y San Felices", "CO Las Calzadas", "CD Las Calzadas",
        "Vivienda Lara", "Vivienda Villadiego", "CISA Inserción",
        "Centro Promoción Personal", "Programa Familias",
    ]
    for c in centros_obsoletos:
        if c in contenido:
            add(nombre, f'Centro obsoleto: "{c}"')

    # 11. <title> presente
    if not re.search(r"<title>.*?</title>", contenido, re.IGNORECASE | re.DOTALL):
        add(nombre, "Falta <title>")

    # 12. UTF-8 declarado
    if 'charset="UTF-8"' not in contenido and "charset=utf-8" not in contenido.lower():
        add(nombre, "Falta declaración charset UTF-8")

    # 13. Etiqueta html cerrada
    if not contenido.rstrip().endswith("</html>"):
        add(nombre, "No termina con </html>")

    # 14. <main> presente (UX consistency)
    if "<main" not in contenido and nombre not in ("agenda-imprimir.html",):
        add(nombre, "No tiene <main> (problema de accesibilidad)")

    # 15. Páginas con sidebar: deben tener sidebar (<aside) o estar excluidas
    paginas_sin_sidebar = {
        "bienvenida.html",
        "documento-algo-sobre-mi.html", "documento-historia-vida.html",
        "documento-plan-apoyo.html", "documento-proyecto-vida.html",
        "documento-revision-objetivos.html",
    }
    if nombre not in paginas_sin_sidebar and "<aside" not in contenido:
        add(nombre, "Falta el sidebar nuevo (<aside>)")

    # 16. Páginas con sidebar: deben tener breadcrumb sticky
    if nombre not in paginas_sin_sidebar and "Inicio</a>" not in contenido and ">Inicio<" not in contenido:
        add(nombre, "Falta breadcrumb con enlace a Inicio")

    # 17. Comparar contenido sospechoso: clases incompletas Tailwind tipo `class="text-`
    if re.search(r'class="[^"]*\bbg-\s', contenido) or re.search(r'class="[^"]*\btext-\s', contenido):
        add(nombre, "Clase Tailwind incompleta")


# === Reporte ===
print(f"=== AUDITORIA DEMO ({len(HTMLS)} archivos) ===\n")
if not INFORME:
    print("[OK] Sin problemas detectados.\n")
else:
    total = sum(len(v) for v in INFORME.values())
    print(f"[!] {total} problemas en {len(INFORME)} archivos\n")
    for archivo in sorted(INFORME):
        print(f"--- {archivo} ---")
        for p in INFORME[archivo]:
            print(f"  - {p}")
        print()

# === Listas adicionales ===
# Páginas referenciadas y huerfanas
todos_destinos = set()
for archivo in HTMLS:
    contenido = archivo.read_text(encoding="utf-8")
    todos_destinos.update(patron_href.findall(contenido))

huerfanos = existentes - todos_destinos - {"index.html"}  # index es entrada
if huerfanos:
    print("PAGINAS HUERFANAS (no enlazadas desde ninguna otra):")
    for h in sorted(huerfanos):
        print(f"  - {h}")

"""Pseudonimizador del Excel "Registro PV por servicios. Global Grupo Aspanias.xlsx".

Lee el Excel original (con datos personales reales), sustituye TODOS los nombres
de personas atendidas y profesionales por nombres ficticios consistentes
(mismo nombre real → mismo nombre ficticio en TODAS las hojas), y guarda una
nueva versión "_PSEUDO.xlsx" segura para pruebas, importación y demo.

NUNCA se sube nada al repo. El Excel original debe estar fuera del repositorio.

Uso:
    python scripts/pseudonimizar_excel_pv.py "C:\\ruta\\Registro PV ... .xlsx"

Produce:
    C:\\ruta\\Registro PV ... _PSEUDO.xlsx   (al lado del original)

Requisitos: openpyxl, faker

Algoritmo:
1. Identifica columnas que llevan nombres en cada hoja (heurística: cabeceras
   "Usuario/a", "Gestor/a de caso", "Persona de referencia", "Responsable").
2. Recoge todos los valores únicos de esas columnas.
3. Genera un mapeo determinista: nombre_real → nombre_ficticio (Faker es_ES).
   El mapeo es coherente entre hojas: si "María Ocio" aparece en 3 hojas,
   se sustituye por el mismo ficticio (p.ej. "Ana López") en las tres.
4. Reescribe el Excel con los nombres sustituidos. Mantiene todo lo demás
   intacto (fechas, SÍ/NO, columnas, formato).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    from openpyxl import load_workbook
except ImportError:
    print("Falta openpyxl. Instálalo con: pip install openpyxl", file=sys.stderr)
    sys.exit(1)

try:
    from faker import Faker
except ImportError:
    print("Falta faker. Instálalo con: pip install faker", file=sys.stderr)
    sys.exit(1)


# Cabeceras (case-insensitive, ignora tildes parcialmente) cuyos valores son
# nombres de personas a pseudonimizar.
CABECERAS_PERSONAS = [
    "usuario/a",
    "usuario",
    "gestor/a de caso",
    "gestor de caso",
    "persona de referencia",
    "responsable",
]


def normaliza_cabecera(texto: str) -> str:
    if not isinstance(texto, str):
        return ""
    t = texto.strip().lower()
    # Quitar acentos básicos
    sust = str.maketrans("áéíóúñü", "aeiounu")
    return t.translate(sust)


def buscar_columnas_nombres(ws) -> list[tuple[int, int]]:
    """Devuelve [(row, col)] de cabeceras detectadas como columnas-de-nombre.

    Mira las primeras 12 filas buscando cabeceras conocidas.
    """
    hits = []
    for r_idx, row in enumerate(ws.iter_rows(values_only=False), start=1):
        if r_idx > 12:
            break
        for c_idx, cell in enumerate(row, start=1):
            val = cell.value
            if isinstance(val, str):
                norm = normaliza_cabecera(val)
                if any(norm == h or h in norm for h in CABECERAS_PERSONAS):
                    hits.append((r_idx, c_idx))
    return hits


def es_nombre_de_persona(texto: str) -> bool:
    """Heurística simple: cadena con >= 2 palabras alfabéticas, no SI/NO/fechas/cabeceras conocidas."""
    if not isinstance(texto, str):
        return False
    t = texto.strip()
    if len(t) < 5:
        return False
    NO_SON_NOMBRE = {
        "SI", "NO", "SÍ", "NA", "N/A", "-",
        "EN PLAZO", "FUERA DE PLAZO", "PENDIENTE",
    }
    if t.upper() in NO_SON_NOMBRE:
        return False
    # Lista negra explícita de cabeceras de tabla y rótulos del Excel.
    CABECERAS_CONOCIDAS = {
        "usuario/a", "usuario", "gestor/a de caso", "gestor de caso",
        "persona de referencia", "responsable",
        "pv realizado", "pv revisado",
        "¿está en teams?", "está en teams", "esta en teams",
        "¿está en repriss?", "está en repriss", "esta en repriss",
        "fecha prevista realización pv", "fecha prevista realizacion pv",
        "fecha revisión pv", "fecha revision pv",
        "estado revisión", "estado revision",
        "usuario/a compartido con residencia /viv",
        "usuario/a compartido con residencia /vivienda",
        "usuario compartido con residencia vivienda",
        "centro/servicio", "centro servicio", "fecha",
        "registro de control de proyectos de vida por servicio",
        "registro de control de proyectos de vida",
        "nº de casos", "número de casos", "numero de casos",
        "gestor de caso",
        "fuera de plazo", "en plazo", "en revisión", "en revision",
        "datos globales pv grupo aspanias",
        "datos grupo aspanias",
        "total fab", "total aspaniamerc",
    }
    if t.lower() in CABECERAS_CONOCIDAS:
        return False
    # Si tiene dígitos, probablemente no es nombre
    if re.search(r"\d", t):
        return False
    palabras = re.findall(r"[A-Za-zÁÉÍÓÚÑÜáéíóúñü]+", t)
    if len(palabras) < 2:
        return False
    # Excluir cadenas con interrogación o paréntesis (suelen ser preguntas/títulos)
    if "?" in t or "¿" in t:
        return False
    return True


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    ruta_in = Path(sys.argv[1])
    if not ruta_in.exists():
        print(f"ERROR: No existe: {ruta_in}", file=sys.stderr)
        sys.exit(1)
    if ruta_in.suffix.lower() != ".xlsx":
        print(f"ERROR: Solo .xlsx. Recibido: {ruta_in.suffix}", file=sys.stderr)
        sys.exit(1)

    ruta_out = ruta_in.with_name(ruta_in.stem + "_PSEUDO.xlsx")
    if ruta_out.exists():
        print(f"ERROR: Ya existe destino: {ruta_out}. Borralo o renombralo primero.", file=sys.stderr)
        sys.exit(1)

    fake = Faker("es_ES")
    Faker.seed(42)  # Reproducible

    # Cargamos el archivo (preservando estilos y fórmulas como texto)
    wb = load_workbook(ruta_in)

    # PASE 1 — recolectar todos los nombres únicos
    print("[1/3] Identificando nombres a pseudonimizar...")
    nombres_unicos: set[str] = set()
    columnas_por_hoja: dict[str, list[int]] = {}

    for sh in wb.sheetnames:
        ws = wb[sh]
        cabeceras = buscar_columnas_nombres(ws)
        if not cabeceras:
            continue
        # Para cada cabecera detectada, marcamos esa columna
        cols = sorted({c for _, c in cabeceras})
        columnas_por_hoja[sh] = cols
        # Recoger valores
        for row in ws.iter_rows(values_only=False):
            for col in cols:
                if col - 1 < len(row):
                    val = row[col - 1].value
                    if es_nombre_de_persona(val):
                        nombres_unicos.add(val.strip())

    print(f"   {len(nombres_unicos)} nombres únicos detectados")

    # PASE 2 — generar mapeo determinista
    mapeo: dict[str, str] = {}
    nombres_usados: set[str] = set()
    for original in sorted(nombres_unicos):
        # Determinar si es nombre completo de persona o nombre + apellidos.
        # Usamos Faker para generar uno nuevo. Aseguramos unicidad.
        intentos = 0
        while True:
            nuevo = fake.name()
            if nuevo not in nombres_usados:
                nombres_usados.add(nuevo)
                mapeo[original] = nuevo
                break
            intentos += 1
            if intentos > 20:
                mapeo[original] = nuevo + str(intentos)
                break

    # PASE 3a — reescribir las columnas detectadas (sustitución exacta del valor)
    print(f"[2/3] Sustituyendo en {len(columnas_por_hoja)} hojas...")
    n_sustituciones = 0
    for sh, cols in columnas_por_hoja.items():
        ws = wb[sh]
        for row in ws.iter_rows(values_only=False):
            for col in cols:
                if col - 1 < len(row):
                    celda = row[col - 1]
                    val = celda.value
                    if isinstance(val, str) and val.strip() in mapeo:
                        celda.value = mapeo[val.strip()]
                        n_sustituciones += 1

    # PASE 3b — barrido completo de TODAS las celdas: si una celda contiene
    # un nombre completo del mapeo como subcadena (por ejemplo en notas
    # libres), lo sustituimos. También barremos por palabras sueltas
    # (apellidos o nombres cortos) cuando son inequívocos (>= 5 letras).
    nombres_completos = sorted(mapeo.keys(), key=len, reverse=True)
    # Palabras del castellano que NUNCA queremos sustituir aunque coincidan con apellido.
    PALABRAS_COMUNES_SAFE = {
        "revisión", "revision", "plazo", "fuera", "estado", "fecha", "centro",
        "servicio", "responsable", "usuario", "persona", "gestor", "caso",
        "realizado", "revisado", "prevista", "realización", "realizacion",
        "compartido", "residencia", "vivienda", "datos", "globales", "grupo",
        "casos", "número", "numero", "total", "control", "registro", "proyectos",
        "vida", "servicios",
    }
    palabras_individuales = {}
    for original, nuevo in mapeo.items():
        for palabra_orig, palabra_nueva in zip(original.split(), nuevo.split()):
            if len(palabra_orig) >= 5 and palabra_orig.lower() not in PALABRAS_COMUNES_SAFE:
                palabras_individuales[palabra_orig] = palabra_nueva

    import re
    n_sub_full = 0
    n_sub_word = 0
    for sh in wb.sheetnames:
        ws = wb[sh]
        for row in ws.iter_rows(values_only=False):
            for celda in row:
                val = celda.value
                if not isinstance(val, str) or not val.strip():
                    continue
                # Saltar si ya fue sustituido en pase 3a (su valor ya es ficticio)
                if val.strip() in mapeo.values():
                    continue
                nuevo_val = val
                cambiado = False
                # Sustituir nombres completos como subcadena
                for original in nombres_completos:
                    if original in nuevo_val:
                        nuevo_val = nuevo_val.replace(original, mapeo[original])
                        cambiado = True
                # Sustituir palabras individuales con frontera de palabra
                for palabra_orig, palabra_nueva in palabras_individuales.items():
                    patron = r"\b" + re.escape(palabra_orig) + r"\b"
                    if re.search(patron, nuevo_val, re.IGNORECASE):
                        nuevo_val = re.sub(patron, palabra_nueva, nuevo_val, flags=re.IGNORECASE)
                        cambiado = True
                if cambiado:
                    celda.value = nuevo_val
                    n_sub_word += 1
    n_sustituciones += n_sub_word
    if n_sub_word:
        print(f"   {n_sub_word} sustituciones adicionales en celdas libres")

    # Guardar
    wb.save(ruta_out)
    print(f"[3/3] {n_sustituciones} sustituciones realizadas.")
    print(f"OK · Archivo pseudonimizado: {ruta_out}")
    print()
    print("RECUERDA:")
    print(f"  1. Borrar/mover a SharePoint cifrado el original: {ruta_in.name}")
    print(f"  2. El archivo _PSEUDO contiene NOMBRES FICTICIOS, seguro para pruebas.")
    print(f"  3. NUNCA subas el original al repositorio git.")


if __name__ == "__main__":
    main()

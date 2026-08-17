"""
cruzar_ixis_registro_pv.py — Cruce de la exportación IxisSocialGest con el
Registro PV por servicios para asignar centro físico a cada persona.

Uso:
    python scripts/utilidades/cruzar_ixis_registro_pv.py <ixis.xlsx> <registro_pv.xlsx> <salida.xlsx>

Método de cruce:
  - Clave = conjunto ordenado de palabras del nombre completo, normalizado
    (mayúsculas, sin tildes, sin puntuación). Independiente del formato
    "Apellidos, Nombre" vs "Nombre Apellidos".
  - Una persona puede aparecer en varias hojas del Registro PV (p. ej.
    Residencia + Centro de Día): se concatenan todos sus centros.

Salida: copia del Ixis con dos columnas nuevas:
  - "Centro (Registro PV)" — centro(s) del cruce, o vacío si no hay coincidencia.
  - "Cruce" — EXACTO / MULTIPLE / NO ENCONTRADO.

RGPD: el script no imprime ningún dato personal — solo estadísticas agregadas.
La salida debe escribirse SIEMPRE en la carpeta segura de migración.
"""
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

from openpyxl import load_workbook, Workbook

HOJAS_AUXILIARES = {"Datos Grupo Aspanias", "Gestores de caso", "Historico"}
FILA_NOMBRE_CENTRO = 4   # fila con "Centro/Servicio:" + nombre oficial
COL_NOMBRE_CENTRO = 3
FILA_CABECERA_PV = 7     # fila de cabecera de datos en cada hoja de centro
COL_USUARIO_PV = 2       # columna "Usuario/a"

FILA_CABECERA_IXIS = 2   # fila de cabecera en la exportación Ixis
COL_APELLIDOS_IXIS = 1
COL_NOMBRE_IXIS = 2


def normalizar(texto: str) -> tuple:
    """Nombre → tupla ordenada de palabras sin tildes ni puntuación."""
    t = unicodedata.normalize("NFD", texto)
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = t.upper()
    for ch in ",.;:-_/()":
        t = t.replace(ch, " ")
    palabras = [p for p in t.split() if len(p) > 1]  # descarta iniciales sueltas
    return tuple(sorted(palabras))


def cargar_mapa_pv(ruta_pv: Path) -> dict:
    """clave-nombre → set de centros donde aparece la persona."""
    wb = load_workbook(ruta_pv, read_only=True, data_only=True)
    mapa = defaultdict(set)
    for hoja in wb.sheetnames:
        if hoja in HOJAS_AUXILIARES:
            continue
        ws = wb[hoja]
        filas = list(ws.iter_rows(values_only=True))
        # nombre oficial del centro (fila 4, col 3); si no, el nombre de la hoja
        centro = hoja
        if len(filas) >= FILA_NOMBRE_CENTRO:
            val = filas[FILA_NOMBRE_CENTRO - 1][COL_NOMBRE_CENTRO - 1]
            if val and str(val).strip():
                centro = str(val).strip()
        for fila in filas[FILA_CABECERA_PV:]:
            if len(fila) < COL_USUARIO_PV:
                continue
            usuario = fila[COL_USUARIO_PV - 1]
            if usuario is None:
                continue
            texto = str(usuario).strip()
            # descartar totales, notas y celdas no-nombre
            if not texto or any(c.isdigit() for c in texto) or len(texto) < 5:
                continue
            clave = normalizar(texto)
            if len(clave) >= 2:
                mapa[clave].add(centro)
    return dict(mapa)


def cruzar(ruta_ixis: Path, ruta_pv: Path, ruta_salida: Path) -> None:
    mapa = cargar_mapa_pv(ruta_pv)
    print(f"Registro PV: {len(mapa)} personas distintas en hojas de centro")

    wb_in = load_workbook(ruta_ixis, read_only=True, data_only=True)
    ws_in = wb_in[wb_in.sheetnames[0]]

    # --- Pasada 0: leer todas las filas del Ixis y calcular sus claves ---
    filas_datos = []   # (celdas, clave)
    cabecera = None
    for idx, fila in enumerate(ws_in.iter_rows(values_only=True), 1):
        if idx < FILA_CABECERA_IXIS:
            continue  # título del export
        celdas = list(fila)
        if idx == FILA_CABECERA_IXIS:
            cabecera = celdas
            continue
        if not any(c is not None and str(c).strip() for c in celdas):
            continue
        apellidos = str(celdas[COL_APELLIDOS_IXIS - 1] or "").strip()
        nombre = str(celdas[COL_NOMBRE_IXIS - 1] or "").strip()
        filas_datos.append((celdas, normalizar(f"{apellidos} {nombre}")))

    if cabecera is None:
        raise SystemExit("No se encontró la cabecera del Ixis — revisar formato")

    # --- Pasada 1: match exacto de clave ---
    claves_exactas = set(mapa) & {clave for _, clave in filas_datos}

    # --- Pasada 2: match por subconjunto (PV con 1 apellido vs Ixis con 2) ---
    # Solo se acepta si el emparejamiento es único EN AMBAS direcciones.
    pv_pendientes = [k for k in mapa if k not in claves_exactas and len(k) >= 2]
    ixis_pendientes = [clave for _, clave in filas_datos
                       if clave not in claves_exactas and len(clave) >= 2]

    candidatos_por_ixis = defaultdict(list)   # clave ixis -> claves PV compatibles
    candidatos_por_pv = defaultdict(list)     # clave PV -> claves ixis compatibles
    for kpv in pv_pendientes:
        spv = set(kpv)
        for kix in set(ixis_pendientes):
            if spv <= set(kix) or set(kix) <= spv:
                candidatos_por_ixis[kix].append(kpv)
                candidatos_por_pv[kpv].append(kix)

    probables = {}   # clave ixis -> clave PV (único en ambas direcciones)
    ambiguos = {}    # clave ixis -> lista claves PV candidatas
    for kix, kpvs in candidatos_por_ixis.items():
        kpvs_unicos = list(dict.fromkeys(kpvs))
        if len(kpvs_unicos) == 1 and len(set(candidatos_por_pv[kpvs_unicos[0]])) == 1:
            probables[kix] = kpvs_unicos[0]
        else:
            ambiguos[kix] = kpvs_unicos

    # --- Escritura ---
    wb_out = Workbook()
    ws_out = wb_out.active
    ws_out.title = "IxisSocialGest + centro"
    ws_out.append(cabecera + ["Centro (Registro PV)", "Cruce"])

    stats = {"EXACTO": 0, "MULTIPLE": 0, "PROBABLE": 0, "AMBIGUO": 0, "NO ENCONTRADO": 0}
    for celdas, clave in filas_datos:
        if clave in claves_exactas:
            centros = mapa[clave]
            resultado = "EXACTO" if len(centros) == 1 else "MULTIPLE"
            valor = " + ".join(sorted(centros))
        elif clave in probables:
            centros = mapa[probables[clave]]
            resultado = "PROBABLE"
            valor = " + ".join(sorted(centros))
        elif clave in ambiguos:
            resultado = "AMBIGUO"
            todos = sorted({c for kpv in ambiguos[clave] for c in mapa[kpv]})
            valor = " ? ".join(todos)
        else:
            resultado = "NO ENCONTRADO"
            valor = ""
        stats[resultado] += 1
        ws_out.append(celdas + [valor, resultado])

    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    wb_out.save(ruta_salida)

    pv_sin_uso = len(pv_pendientes) - len(set(probables.values()))
    print(f"Personas en Ixis: {len(filas_datos)}")
    print(f"  EXACTO (1 centro):          {stats['EXACTO']}")
    print(f"  MULTIPLE (>1 centro):       {stats['MULTIPLE']}")
    print(f"  PROBABLE (subconjunto):     {stats['PROBABLE']}")
    print(f"  AMBIGUO (revisar a mano):   {stats['AMBIGUO']}")
    print(f"  NO ENCONTRADO en PV:        {stats['NO ENCONTRADO']}")
    print(f"Personas del PV sin asignar a Ixis: {pv_sin_uso}")
    print(f"Salida: {ruta_salida}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    cruzar(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))

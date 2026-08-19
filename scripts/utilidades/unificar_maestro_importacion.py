"""
unificar_maestro_importacion.py — Consolida en un único Excel maestro los datos
de migración a ÁGORA: base IxisSocialGest (con centro del cruce PV) + DNI/TSS +
diagnósticos + contactos familiares.

Uso:
    python scripts/utilidades/unificar_maestro_importacion.py \
        <ixis_con_centro.xlsx> <dni_tss.xlsx> <diagnosticos.xlsx> <contactos.xlsx> <salida.xlsx>

Garantías de fiabilidad:
  1. Cruce primario por DNI normalizado (cuando ambas partes lo tienen);
     secundario por nombre normalizado; tercero por subconjunto de nombre
     único en ambas direcciones (PROBABLE).
  2. Los conflictos entre fuentes NUNCA se sobrescriben: se conservan ambos
     valores y se marca la columna "Conflicto ...".
  3. Toda fila de origen queda contabilizada: o casa con el maestro o aparece
     en la hoja "Excepciones" con su motivo.
  4. Hoja "Resumen" con procedencia, fecha y estadísticas del proceso.
  5. La consola solo muestra estadísticas agregadas — nunca datos personales.
"""
import sys
import unicodedata
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

from openpyxl import Workbook, load_workbook


# ---------- normalización ----------

def normalizar_nombre(texto: str) -> tuple:
    t = unicodedata.normalize("NFD", texto or "")
    t = "".join(c for c in t if unicodedata.category(c) != "Mn").upper()
    for ch in ",.;:-_/()":
        t = t.replace(ch, " ")
    return tuple(sorted(p for p in t.split() if len(p) > 1))


def normalizar_dni(valor) -> str:
    if valor is None:
        return ""
    t = str(valor).upper()
    return "".join(c for c in t if c.isalnum())


def como_texto(valor) -> str:
    if valor is None:
        return ""
    if isinstance(valor, (datetime, date)):
        return valor.strftime("%d/%m/%Y")
    return str(valor).strip()


def normalizar_fecha(valor) -> str:
    """Fecha en cualquier formato habitual → 'dd/mm/aaaa' ('' si no parsea)."""
    if valor is None:
        return ""
    if isinstance(valor, (datetime, date)):
        return valor.strftime("%d/%m/%Y")
    texto = str(valor).strip().split()[0] if str(valor).strip() else ""
    for sep in ("-", "/", "."):
        partes = texto.split(sep)
        if len(partes) == 3 and all(p.isdigit() for p in partes):
            if len(partes[0]) == 4:      # aaaa-mm-dd
                a, m, d = partes
            else:                        # dd-mm-aaaa
                d, m, a = partes
            try:
                return date(int(a), int(m), int(d)).strftime("%d/%m/%Y")
            except ValueError:
                return ""
    return ""


# ---------- lectura de fuentes ----------

def leer_filas(ruta: Path, fila_cabecera: int, col_apellidos: int, col_nombre: int,
               columnas: dict) -> list:
    """Devuelve [{campo: valor}, ...] con 'clave' (nombre) y '_fila' añadidos."""
    wb = load_workbook(ruta, read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]
    registros = []
    for idx, fila in enumerate(ws.iter_rows(values_only=True), 1):
        if idx <= fila_cabecera:
            continue
        ap = como_texto(fila[col_apellidos - 1] if len(fila) >= col_apellidos else None)
        nom = como_texto(fila[col_nombre - 1] if len(fila) >= col_nombre else None)
        if not ap and not nom:
            continue
        reg = {"_fila": idx, "_apellidos": ap, "_nombre": nom,
               "clave": normalizar_nombre(f"{ap} {nom}")}
        for campo, col in columnas.items():
            reg[campo] = fila[col - 1] if len(fila) >= col else None
        registros.append(reg)
    return registros


# ---------- cruce ----------

def emparejar(registros: list, indice_nombre: dict, indice_dni: dict,
              campo_dni: str | None) -> tuple:
    """Devuelve (asignaciones {idx_base: (registro, metodo)}, excepciones [...])."""
    asignaciones = {}
    excepciones = []
    pendientes = []

    for reg in registros:
        # 1) por DNI
        if campo_dni:
            dni = normalizar_dni(reg.get(campo_dni))
            if dni and dni in indice_dni and len(indice_dni[dni]) == 1:
                asignaciones.setdefault(indice_dni[dni][0], (reg, "DNI"))
                continue
        # 2) por nombre exacto
        base_idx = indice_nombre.get(reg["clave"])
        if base_idx is not None and len(base_idx) == 1:
            asignaciones.setdefault(base_idx[0], (reg, "NOMBRE"))
            continue
        if base_idx is not None and len(base_idx) > 1:
            excepciones.append((reg, "nombre duplicado en Ixis — asignar a mano"))
            continue
        pendientes.append(reg)

    # 3) por subconjunto único en ambas direcciones
    candidatos_reg = defaultdict(list)
    candidatos_base = defaultdict(list)
    claves_base = [(k, v) for k, v in indice_nombre.items() if len(k) >= 2]
    for reg in pendientes:
        s = set(reg["clave"])
        if len(s) < 2:
            excepciones.append((reg, "nombre demasiado corto"))
            continue
        for kbase, idxs in claves_base:
            if s <= set(kbase) or set(kbase) <= s:
                candidatos_reg[id(reg)].append((kbase, idxs))
                candidatos_base[kbase].append(id(reg))
    for reg in pendientes:
        cands = candidatos_reg.get(id(reg), [])
        if len(cands) == 1 and len(set(candidatos_base[cands[0][0]])) == 1 \
                and len(cands[0][1]) == 1:
            asignaciones.setdefault(cands[0][1][0], (reg, "PROBABLE"))
        elif len(cands) == 0:
            excepciones.append((reg, "sin coincidencia en Ixis"))
        else:
            excepciones.append((reg, f"ambiguo ({len(cands)} candidatos)"))
    return asignaciones, excepciones


# ---------- principal ----------

def unificar(ruta_base, ruta_dni, ruta_diag, ruta_cont, ruta_salida):
    # Base: Ixis con centro (cabecera fila 1: es la salida del cruce anterior)
    wb = load_workbook(ruta_base, read_only=True, data_only=True)
    ws = wb.active
    filas = list(ws.iter_rows(values_only=True))
    cabecera_base = list(filas[0])
    base = []
    for f in filas[1:]:
        if not any(c is not None and str(c).strip() for c in f):
            continue
        base.append(list(f))

    indice_nombre = defaultdict(list)
    indice_dni = defaultdict(list)
    for i, f in enumerate(base):
        clave = normalizar_nombre(f"{como_texto(f[0])} {como_texto(f[1])}")
        indice_nombre[clave].append(i)
        dni = normalizar_dni(f[16])  # col 17 "Documento"
        if dni:
            indice_dni[dni].append(i)

    fuentes = {
        "DNI-TSS": dict(
            registros=leer_filas(ruta_dni, 1, 1, 2, {
                "F.Nacimiento (DNI-TSS)": 3, "NIF (DNI-TSS)": 4,
                "Caducidad DNI": 5, "% Disc (DNI-TSS)": 6,
                "Grado dep (DNI-TSS)": 7, "BVD": 8, "ICAP (fecha/valor)": 9,
                "Tarjeta sanitaria (TSI)": 10, "Nº Seguridad Social": 11,
            }),
            campo_dni="NIF (DNI-TSS)",
        ),
        "Diagnósticos": dict(
            registros=leer_filas(ruta_diag, 2, 3, 4, {
                "Referencia/Expediente": 5, "Diagnóstico principal": 6,
                "Diagnóstico secundario": 7, "Fecha validez diagnóstico": 8,
                "% Disc (Diagnósticos)": 9, "Puntos discapacidad (PD)": 10,
                "Puntos factores sociales (PFS)": 11,
                "Puntos movilidad reducida (PMR)": 12, "Puntos 3ª persona (P3P)": 13,
            }),
            campo_dni=None,
        ),
        "Contactos": dict(
            registros=leer_filas(ruta_cont, 2, 3, 4, {
                "Persona de contacto": 5, "Teléfono contacto": 6,
                "Dirección contacto": 7, "Forma de comunicación": 8,
                "Fecha incorporación entidad": 9,
            }),
            campo_dni=None,
        ),
    }

    resultado_fuentes = {}
    for nombre, cfg in fuentes.items():
        asig, exc = emparejar(cfg["registros"], indice_nombre, indice_dni,
                              cfg["campo_dni"])
        resultado_fuentes[nombre] = dict(asignaciones=asig, excepciones=exc,
                                         total=len(cfg["registros"]),
                                         columnas=[c for c in cfg["registros"][0]
                                                   if not c.startswith("_") and c != "clave"]
                                         if cfg["registros"] else [])

    # ---------- escribir maestro ----------
    out = Workbook()
    hoja = out.active
    hoja.title = "Maestro"

    columnas_extra = []
    for nombre, res in resultado_fuentes.items():
        columnas_extra += res["columnas"] + [f"Cruce {nombre}"]
    columnas_conflicto = ["Conflicto DNI", "Conflicto F.Nacimiento", "Conflicto % Disc"]
    hoja.append(cabecera_base + columnas_extra + columnas_conflicto)

    stats_conflictos = {c: 0 for c in columnas_conflicto}
    for i, f in enumerate(base):
        fila_out = list(f)
        conflictos = {c: "" for c in columnas_conflicto}
        for nombre, res in resultado_fuentes.items():
            par = res["asignaciones"].get(i)
            if par:
                reg, metodo = par
                fila_out += [reg.get(c) for c in res["columnas"]] + [metodo]
                if nombre == "DNI-TSS":
                    dni_base = normalizar_dni(f[16])
                    dni_fuente = normalizar_dni(reg.get("NIF (DNI-TSS)"))
                    if dni_base and dni_fuente and dni_base != dni_fuente:
                        conflictos["Conflicto DNI"] = "SÍ"
                    fn_base = normalizar_fecha(f[10])
                    fn_fuente = normalizar_fecha(reg.get("F.Nacimiento (DNI-TSS)"))
                    if fn_base and fn_fuente and fn_base != fn_fuente:
                        conflictos["Conflicto F.Nacimiento"] = "SÍ"
                if nombre == "Diagnósticos":
                    d_base = como_texto(f[8]).replace("%", "").strip()
                    d_fuente = como_texto(reg.get("% Disc (Diagnósticos)")).replace("%", "").strip()
                    if d_base and d_fuente and d_base != d_fuente:
                        conflictos["Conflicto % Disc"] = "SÍ"
            else:
                fila_out += [None] * len(res["columnas"]) + [""]
        for c in columnas_conflicto:
            if conflictos[c]:
                stats_conflictos[c] += 1
        hoja.append(fila_out + [conflictos[c] for c in columnas_conflicto])

    # ---------- hoja excepciones ----------
    hoja_exc = out.create_sheet("Excepciones")
    hoja_exc.append(["Fuente", "Fila origen", "Apellidos", "Nombre", "Motivo"])
    for nombre, res in resultado_fuentes.items():
        for reg, motivo in res["excepciones"]:
            hoja_exc.append([nombre, reg["_fila"], reg["_apellidos"],
                             reg["_nombre"], motivo])

    # ---------- hoja resumen ----------
    hoja_res = out.create_sheet("Resumen")
    hoja_res.append(["Generado", datetime.now().strftime("%d/%m/%Y %H:%M")])
    hoja_res.append(["Base", str(ruta_base), f"{len(base)} personas"])
    hoja_res.append([])
    hoja_res.append(["Fuente", "Filas", "Casadas DNI", "Casadas nombre",
                     "Probables", "Excepciones"])
    print(f"Base Ixis: {len(base)} personas")
    for nombre, res in resultado_fuentes.items():
        met = defaultdict(int)
        for _, (reg, metodo) in res["asignaciones"].items():
            met[metodo] += 1
        fila = [nombre, res["total"], met["DNI"], met["NOMBRE"], met["PROBABLE"],
                len(res["excepciones"])]
        hoja_res.append(fila)
        print(f"{nombre}: {res['total']} filas · DNI {met['DNI']} · "
              f"nombre {met['NOMBRE']} · probable {met['PROBABLE']} · "
              f"excepciones {len(res['excepciones'])}")
    hoja_res.append([])
    for c, n in stats_conflictos.items():
        hoja_res.append([c, n])
        print(f"{c}: {n}")

    Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)
    out.save(ruta_salida)
    print(f"Salida: {ruta_salida}")


if __name__ == "__main__":
    if len(sys.argv) != 6:
        raise SystemExit(__doc__)
    unificar(*[Path(p) for p in sys.argv[1:]])

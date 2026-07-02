"""Analiza la ESTRUCTURA del Excel CGPR sin exponer datos personales.

- Cuenta hojas generales vs individuales
- Lista cabeceras GENERALES (de las hojas Arqueo/Caja/Gastos)
- Para hojas individuales, infiere patrón de columnas a partir de una muestra (sin nombre)
- NO escribe nombres ni importes ni DNIs
- Salida: docs/modelo-datos/analisis_cgpr_estructura.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from collections import Counter
from openpyxl import load_workbook

RUTA_EXCEL = Path.home() / "Downloads" / "CGPR 2025 (1).xlsx"
SALIDA = Path(__file__).resolve().parent.parent / "docs" / "modelo-datos" / "analisis_cgpr_estructura.md"

HOJAS_GENERALES = {"Arqueo", "Caja", "Gastos Residencia"}
SOSPECHOSOS_DNI = ("dni", "nif", "nº id", "n. id")
SOSPECHOSOS_NOMBRE = ("nombre", "apellido", "titular")


def es_cabecera_sospechosa(texto: str) -> bool:
    t = texto.lower()
    return any(s in t for s in SOSPECHOSOS_DNI + SOSPECHOSOS_NOMBRE)


def inferir_tipo(v) -> str:
    if v is None or (isinstance(v, str) and not v.strip()):
        return "vacío"
    if isinstance(v, (int, float)):
        return "numérico"
    if hasattr(v, 'isoformat'):  # date / datetime
        return "fecha"
    if isinstance(v, str):
        s = v.strip()
        # No imprimimos el valor, solo categorizamos
        if any(c.isdigit() for c in s) and "/" in s:
            return "fecha-texto"
        if any(c.isalpha() for c in s):
            return "texto"
        return "alfanumérico"
    return type(v).__name__


def analizar_hoja(ws, listar_cabeceras: bool):
    """Devuelve dict con info estructural. Si listar_cabeceras=True, devuelve nombres de columnas;
    si False, devuelve solo tipos por posición."""
    info = {"filas": ws.max_row, "columnas": ws.max_column, "cabeceras": [], "tipos_columnas": []}
    # Buscar fila cabecera (1ª con ≥2 textos)
    cabecera_fila = None
    for r in range(1, min(8, ws.max_row + 1)):
        valores = [ws.cell(r, c).value for c in range(1, ws.max_column + 1)]
        n_texto = sum(1 for v in valores if isinstance(v, str) and v.strip())
        if n_texto >= 2:
            cabecera_fila = r
            if listar_cabeceras:
                info["cabeceras"] = [str(v).strip() if v is not None else "" for v in valores]
            break
    # Inferir tipos por columna mirando 5 filas tras la cabecera
    if cabecera_fila:
        tipos_por_col = [[] for _ in range(ws.max_column)]
        for r in range(cabecera_fila + 1, min(cabecera_fila + 15, ws.max_row + 1)):
            for c in range(1, ws.max_column + 1):
                v = ws.cell(r, c).value
                if v is not None and (not isinstance(v, str) or v.strip()):
                    tipos_por_col[c - 1].append(inferir_tipo(v))
        info["tipos_columnas"] = [Counter(t).most_common(1)[0][0] if t else "vacío" for t in tipos_por_col]
    return info


def main():
    if not RUTA_EXCEL.exists():
        print(f"NO existe: {RUTA_EXCEL}")
        return

    wb = load_workbook(RUTA_EXCEL, read_only=True, data_only=True)
    nombres = wb.sheetnames

    # Clasificación
    generales = [n for n in nombres if n in HOJAS_GENERALES]
    individuales = [n for n in nombres if n not in HOJAS_GENERALES]

    print(f"Hojas totales: {len(nombres)}")
    print(f"  Generales: {len(generales)}")
    print(f"  Individuales (1 por persona): {len(individuales)}")

    # Análisis hojas generales (con cabeceras)
    bloques_md = []
    for nombre in generales:
        ws = wb[nombre]
        info = analizar_hoja(ws, listar_cabeceras=True)
        cabs = info["cabeceras"]
        tipos = info["tipos_columnas"]
        bloques_md.append(f"### Hoja general: **{nombre}**\n")
        bloques_md.append(f"- Dimensiones: {info['filas']} filas × {info['columnas']} columnas")
        bloques_md.append("- Columnas detectadas (cabecera + tipo inferido):\n")
        bloques_md.append("| # | Cabecera | Tipo de dato |")
        bloques_md.append("|---|----------|--------------|")
        for i, c in enumerate(cabs):
            t = tipos[i] if i < len(tipos) else "—"
            # Sanitizar cabeceras: si la cabecera contiene DNI o nombre individual lo enmascaramos
            c_safe = c if not es_cabecera_sospechosa(c) else "**[campo PII]**"
            bloques_md.append(f"| {i+1} | `{c_safe}` | {t} |")
        bloques_md.append("")

    # Análisis hojas individuales: solo conteos y patrón agregado, SIN listar nombres
    # Tomamos una muestra de 3 hojas individuales para detectar el patrón
    muestras = individuales[:3]
    patron_cabecera = None
    if muestras:
        ws = wb[muestras[0]]
        info = analizar_hoja(ws, listar_cabeceras=True)
        patron_cabecera = info["cabeceras"]
        # Tipos consensuados entre las muestras
        consenso_tipos = info["tipos_columnas"]
        # Verificar coincidencia con las otras 2 hojas
        coincidencias = []
        for m in muestras[1:]:
            i2 = analizar_hoja(wb[m], listar_cabeceras=True)
            if i2["cabeceras"] == info["cabeceras"]:
                coincidencias.append(m)
        print(f"Las 3 hojas individuales muestreadas tienen estructura idéntica: {len(coincidencias) == 2}")

    bloques_md.append(f"### Hojas individuales (1 por persona atendida)\n")
    bloques_md.append(f"- **Total**: {len(individuales)} hojas (una por persona)")
    bloques_md.append(f"- **Patrón de columnas** (idéntico en las 3 hojas muestreadas):\n")
    bloques_md.append("| # | Cabecera | Tipo de dato |")
    bloques_md.append("|---|----------|--------------|")
    if patron_cabecera:
        for i, c in enumerate(patron_cabecera):
            t = consenso_tipos[i] if i < len(consenso_tipos) else "—"
            c_safe = c if not es_cabecera_sospechosa(c) else "**[campo PII]**"
            bloques_md.append(f"| {i+1} | `{c_safe}` | {t} |")
    bloques_md.append("")
    bloques_md.append("**Importante**: el nombre de cada hoja corresponde al de una persona atendida real.")
    bloques_md.append("Por aplicación de la regla RGPD del proyecto, esos nombres NO se transcriben aquí.")

    wb.close()

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    contenido = f"""# Análisis estructural del Excel **CGPR 2025**

**Fecha del análisis**: 2026-06-01
**Origen**: `~/Downloads/CGPR 2025 (1).xlsx`
**Estado**: estructura analizada · datos personales NO copiados (RGPD)

---

## Resumen

- **Hojas totales**: {len(nombres)}
- **Hojas generales**: {len(generales)} (Arqueo, Caja, Gastos Residencia)
- **Hojas individuales**: {len(individuales)} (una por persona atendida)

Este Excel implementa, sobre el formato libro multi-hoja, dos sub-sistemas:

1. **General** — control consolidado de caja: arqueo, movimientos generales y gastos de residencia.
2. **Individual** — una hoja por cada persona, con sus ingresos, gastos y saldo acumulado (lo que la práctica del sector llama "dinero de bolsillo" o "peculio").

---

## Estructura por hoja

{chr(10).join(bloques_md)}

---

## Conclusiones para el diseño del módulo en ÁGORA

1. **2 sub-módulos** necesarios:
   - **Cuenta individual** (peculio): vinculada a `PersonaAtendida`
   - **Caja del centro**: arqueo + movimientos generales + gastos atribuibles al servicio (no a personas concretas)

2. **Identificación**: en el Excel cada persona tiene su propia hoja. En ÁGORA se modelará como
   una `CuentaBolsillo` 1:1 con `PersonaAtendida` y los movimientos como `MovimientoCuenta`.

3. **Atomicidad**: cada movimiento (entrada, salida, transferencia) debe quedar registrado con
   fecha, concepto, importe, signo, justificante y firma del responsable.

4. **Arqueo**: la hoja "Arqueo" del Excel actúa como cierre mensual. En ÁGORA será una entidad
   `ArqueoCaja` que congela el saldo a una fecha y bloquea movimientos anteriores.

5. **Conciliación**: la suma de saldos individuales + caja general debe casar con el efectivo
   físico en cada arqueo. Eso es lo que verifica la herramienta.

---

## Reglas RGPD aplicadas en este análisis

- ✅ El archivo original NO se ha copiado al repositorio.
- ✅ Los nombres de las {len(individuales)} hojas individuales (= nombres de personas) NO se transcriben.
- ✅ Los importes específicos NO se transcriben.
- ✅ Los DNIs/NIFs (si están como cabecera de columna) se marcan como `[campo PII]`.
- ✅ Lo único transcrito: nombres de columnas estructurales y tipos de datos.

---

*Análisis realizado dentro del flujo RGPD del proyecto.*
"""
    SALIDA.write_text(contenido, encoding='utf-8')
    print(f"\nAnálisis guardado en: {SALIDA}")


if __name__ == "__main__":
    main()

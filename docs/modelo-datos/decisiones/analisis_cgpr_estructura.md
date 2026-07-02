# Análisis estructural del Excel **CGPR 2025**

**Fecha del análisis**: 2026-06-01
**Origen**: Excel externo (no entra al repositorio)
**Estado**: Estructura analizada · datos personales NO copiados (RGPD)

---

## Resumen

| Categoría | Cifra |
|---|---|
| **Hojas totales** | 126 |
| **Hojas generales** | 3 (Arqueo · Caja · Gastos Residencia) |
| **Hojas individuales** | 123 (una por persona atendida) |

El Excel está estructurado como un libro contable multi-hoja con dos sub-sistemas:

1. **General** — control consolidado de caja: arqueo mensual, movimientos generales de caja y gastos imputables al centro (no atribuibles a una persona concreta).
2. **Individual** — una hoja por cada persona, con sus movimientos (ingresos / gastos) y el saldo acumulado de su **peculio** o **dinero de bolsillo**.

---

## Estructura común (sin transcribir valores)

Todas las hojas tienen una **cabecera administrativa** en filas 1-2 con metadatos del libro (entidad, área, tipo de cuenta) y un **listado de movimientos** debajo. Las cabeceras de tabla típicas en este tipo de libro son:

| Posición típica | Campo | Tipo |
|---|---|---|
| 1 | Fecha del movimiento | fecha |
| 2 | Concepto / descripción | texto |
| 3 | Ingreso (entrada) | numérico € |
| 4 | Gasto (salida) | numérico € |
| 5 | Saldo acumulado | numérico € |
| 6 | Referencia / justificante | texto |
| 7 | Observaciones | texto |

En la **hoja Arqueo** la estructura es de resumen, no de movimientos:

| Columna | Campo | Tipo |
|---|---|---|
| 1 | Nomencl. (código corto) | texto |
| 2 | **[campo PII: nombre persona]** | texto |
| 3 | Saldo | numérico € |
| 4 | Observaciones | texto |

---

## Conclusiones para el diseño del módulo en ÁGORA

### 2 sub-módulos necesarios

#### A) **Cuenta de bolsillo (peculio individual)** — vinculada a `PersonaAtendida`

Cada persona tiene su cuenta. Movimientos: entradas (pensión, paga familiar, transferencia) y salidas (gastos personales, retiradas). Saldo calculado.

#### B) **Caja del centro** — vinculada a `Centro`

Caja física del centro para gastos imputables al servicio (compras compartidas, gastos comunes). Tiene los mismos campos de movimiento pero sin vinculación a persona.

### Vinculación con `ArqueoMensual`

Cada mes (o periodo configurable) se cierra un **arqueo**:

- Snapshot de saldos individuales a fecha concreta
- Snapshot de la caja del centro
- Conciliación con el efectivo físico real
- Una vez cerrado, **los movimientos del periodo quedan bloqueados** (solo el rol Administración puede desbloquear)

---

## Pendiente para implementar

- [ ] Modelos: `CuentaBolsillo`, `MovimientoBolsillo`, `CajaCentro`, `MovimientoCaja`, `ArqueoMensual`
- [ ] Vistas: tab "Dinero de bolsillo" en ficha de persona; página "Caja del centro"; pantalla de arqueo
- [ ] Permisos por rol: solo Administración y coordinador del centro pueden modificar movimientos
- [ ] Bitácora: cada movimiento queda registrado en bitácora con usuario, IP, timestamp y motivo
- [ ] Importador del Excel actual → ÁGORA (1 vez, en migración inicial)

---

## Reglas RGPD aplicadas en este análisis

- ✅ El archivo Excel original NO se ha copiado al repositorio
- ✅ Los nombres de las 123 hojas individuales NO se transcriben
- ✅ Los importes específicos NO se transcriben (ni siquiera de muestra)
- ✅ Los DNIs/NIFs (si están como campo) se marcan como `[campo PII]`
- ✅ Lo único transcrito: estructura agregada del libro, conteos y conclusiones de diseño

---

*Análisis realizado dentro del flujo RGPD del proyecto.*

# Auditoría de datos Excel ↔ ÁGORA — pre-piloto

**Cuándo**: semana 6 del pre-piloto (lunes-martes, 12-13 oct 2026).
**Quién la ejecuta**: Federico + Lucía Martínez + Innovación Aspanias.
**Objetivo**: medir la coincidencia entre el Excel actual y ÁGORA en las
3 personas migradas, para validar el criterio go/no-go de **≥ 95 %**.

---

## 1. Por qué esta auditoría

Durante 4 semanas el equipo ha hecho doble carga. Necesitamos saber:

1. Si lo que se introdujo en ÁGORA refleja fielmente lo que está en Excel.
2. Dónde se rompió la coincidencia (¿errores de tipeo? ¿campos mal mapeados?
   ¿formación insuficiente?).
3. Si el modelo de datos cubre la realidad o hay vacíos.

Sin esto no podemos decir al Patronato "ÁGORA está listo".

---

## 2. Alcance

Solo las **3 personas migradas** en el pre-piloto. Para cada una de ellas
verificamos **6 dimensiones de datos**:

| # | Dimensión | Origen Excel | Destino ÁGORA |
|---|---|---|---|
| 1 | Identificación básica | Pestaña "Personas" del Excel · 6 campos | `PersonaAtendida` |
| 2 | Plan de Vida | Pestaña "PV [centro]" · 12 columnas | `PlanDeVida` + `DocumentoPlanDeVida` |
| 3 | Información médica | Carpeta papel + Odoo legado · 8 bloques | `InformacionMedica` + `Alergia` + `EnfermedadCronica` |
| 4 | Medicación | Hoja medicación del Odoo · n filas | `PautaMedicacion` |
| 5 | Familiares | Lista contactos Odoo | `PersonaContacto` + `VinculoPersonaContacto` |
| 6 | Alojamiento | Plano del centro + Excel ocupación | `OcupacionCama` |

---

## 3. Procedimiento paso a paso

### Para cada persona:

#### Paso 1 — Identificación (15 min)
- Imprimir la pestaña Personas del Excel filtrada por código de persona.
- Imprimir la pestaña "Datos personales" de ÁGORA (botón 🖨 Imprimir).
- Comparar campo a campo con bolígrafo rojo.
- Anotar cada divergencia en `discrepancias_persona_<N>.md`.

**Campos críticos a verificar**:
- Nombre, apellidos, fecha nacimiento, DNI/NIE
- Dirección postal completa
- NUSS, TSI (descifrar desde admin Django)
- Fecha alta, centro de referencia, corresponsable

#### Paso 2 — Plan de Vida (30 min)
- Imprimir el Plan de Vida desde Word (formato actual).
- Imprimir el Plan de Vida desde ÁGORA (pestaña Plan de Vida → botón
  imprimir cada uno de los 5 documentos).
- Comparar **palabra por palabra** (no solo cifras):
  - Historia de Vida: 21 preguntas/pistas oficiales
  - Algo sobre mí: 11 secciones
  - Plan de Apoyo: 9 columnas
  - Revisión de objetivos
  - Proyecto de Vida: 8 bloques narrativos
- Verificar que el **gestor de caso** y la **persona de referencia** son los
  correctos.
- Verificar que los **objetivos** activos coinciden y tienen el ámbito
  Schalock correcto.

#### Paso 3 — Información médica (20 min)
*Solo si la auditora tiene rol clínico (DUE de Fuentecillas).*

- Sacar de la carpeta de papel:
  - Listado de alergias
  - Listado de enfermedades crónicas
  - Última antropometría
  - Cartilla de vacunación
- Comparar con la pestaña "Información médica" de ÁGORA.
- Verificar especialmente:
  - **Alergias graves o anafilácticas** — error aquí es crítico.
  - **Antropometría con histórico** — los últimos 6 meses deben coincidir.
  - **Vacunación COVID y gripe** — al menos las dos últimas dosis.

#### Paso 4 — Medicación (25 min)
*Solo DUE.*

- Sacar la hoja de medicación actual del Odoo legado.
- Comparar con la pestaña "Medicación" de ÁGORA:
  - Lista de pautas **activas** coincidente.
  - Dosificación D-C-N correcta.
  - Prescriptor identificado.
  - Histórico de pautas finalizadas mes corriente.
- Si una persona tiene **alergia medicamentosa** registrada, verificar que
  ningún medicamento del grupo prohibido está en la pauta. **Si lo está,
  parar la auditoría y elevar a Dirección.**

#### Paso 5 — Familiares (10 min)
- Listado de contactos del Odoo + libreta de la coordinación.
- Comparar con pestaña "Familiares" de ÁGORA:
  - Cada familiar registrado con parentesco correcto
  - Teléfonos: móvil y fijo separados (en ÁGORA hay dos campos; en Odoo
    suele estar en uno solo — esto es esperable, anotar como "diferencia
    estructural OK")
  - Flag CERCA marcado donde corresponde
  - Persona curadora identificada si hay medida Ley 8/2021

#### Paso 6 — Alojamiento (10 min)
- Para personas en residencia/vivienda, verificar:
  - Centro · Módulo · Habitación · Cama actual coinciden con el plano físico
  - Histórico de cambios desde el alta (si los hubo)
  - Datos PMR y articulada correctos

---

## 4. Plantilla de discrepancias

Para cada divergencia encontrada, anotar:

```
PERSONA: ___ (código FUE-2026-XXXXX)
DIMENSIÓN: ___ (1-6)
CAMPO: ___ (p. ej. "Dirección postal" o "Alergia OXICAMS")

VALOR EN EXCEL/Odoo:
___________________________________________

VALOR EN ÁGORA:
___________________________________________

GRAVEDAD:
[ ] Crítico (afecta atención · datos sanitarios o jurídicos)
[ ] Mayor (datos incorrectos visibles)
[ ] Menor (formato, capitalización, espacios)

CAUSA APARENTE:
[ ] Error de tipeo en doble carga
[ ] Campo no mapeado en el modelo
[ ] Información ambigua en el origen
[ ] Otra: __________

ACCIÓN:
[ ] Corregir ÁGORA inmediatamente
[ ] Corregir tras pre-piloto
[ ] Cambiar el modelo (Fase 2.5+ refresh)
[ ] Aceptar como diferencia estructural
```

Archivar en `datos/feedback/discrepancias/persona_N_dimension_X.md`.

---

## 5. Cálculo del % de coincidencia

Cada dimensión se valora **por campo** (no por persona):

| Dimensión | Nº campos a verificar | Peso |
|---|---|---|
| Identificación | 12 | 15 % |
| Plan de Vida | 50 (los 5 documentos sumados) | 30 % |
| Información médica | 25 | 20 % |
| Medicación | 10 + N pautas | 20 % |
| Familiares | 5 × N familiares | 10 % |
| Alojamiento | 4 | 5 % |

**Fórmula**:

```
% coincidencia global = SUMA por dimensión de
    (campos OK / total campos) × peso de la dimensión
```

**Umbral go/no-go**: ≥ 95 %.

**Discrepancias críticas (gravedad: Crítico)**: tolerancia **CERO**. Una sola
crítica = no-go automático hasta resolverla.

---

## 6. Resultado de la auditoría

Se documenta en `docs/fase3/resultado_auditoria.md` (privado, sin nombres
reales) con:

1. Tabla resumen del % por persona y por dimensión.
2. Total de discrepancias por gravedad.
3. Lista de discrepancias críticas (si las hay) y plan de resolución.
4. Recomendación a Federico: go / no-go / extender pre-piloto.

---

## 7. Anonimización al cerrar

Una vez finalizado el pre-piloto y antes de archivar:

- Las hojas de comparación en papel se **destruyen** (confidencialidad).
- Los archivos digitales se **anonimizan** (sustituir nombres por códigos
  FUE-A, FUE-B, FUE-C) antes de subirlos al repositorio.
- Las discrepancias estructurales que requieran cambio del modelo se llevan
  al backlog de Fase 4 sin datos personales asociados.

---

*Procedimiento de auditoría v0.1 · 2026-05-19 · Federico Martínez +
Innovación Aspanias.*

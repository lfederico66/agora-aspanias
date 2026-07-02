# Modelo de datos ÁGORA — v0.3 (incorpora plantilla "Revisión de objetivos")

**Estado**: alineado con la plantilla Excel real de Fundación Aspanias `modelo revisión objetivos 2025.xlsx`.
**Fecha**: 2026-05-13
**Sustituye a**: `modelo_v0_2.md` (cambio incremental, no rupturista).

> Esta versión añade `RevisionObjetivo` para registrar el seguimiento narrativo anual de cada objetivo del Plan de Vida, reproduciendo el formato de cuatro columnas que se usa hoy en papel/Excel en los centros.

---

## Plantilla original analizada

Excel: `modelo revisión objetivos 2025 (1).xlsx`, hoja única, 28 filas × 12 columnas.

**Cabecera del documento**:
- Título: "PROYECTO DE VIDA. Seguimiento de los deseos logrados"
- Nombre y apellidos · Fecha
- Persona de referencia · Gestor de Caso

**Tabla** (filas 11-28, 4 columnas con celdas combinadas de 3 columnas cada una):

| Objetivos | ¿Qué ha logrado hasta la fecha? | No lo ha conseguido ¿Cuál puede ser el motivo? | ¿Cómo podemos ayudarle a conseguirlo? Propuestas de apoyo. Qué se necesita |
|---|---|---|---|

6 filas vacías para escribir.

---

## Cambio en el modelo

Mi v0.2 ya tenía `Objetivo` con `descripcion`, `indicador_logro`, `apoyos_necesarios` y `estado`. Faltaba **el seguimiento narrativo anual** — los tres campos narrativos del Excel y la separación por año.

Decisión: **no mover esos campos al `Objetivo`** porque un objetivo puede vivir varios años con revisiones sucesivas y se perdería la trayectoria longitudinal. Se modelan como entidad propia.

### Nueva entidad `RevisionObjetivo`

| Campo | Tipo | Notas |
|---|---|---|
| `objetivo` | FK Objetivo | El objetivo revisado. |
| `anualidad` | int | Año de la revisión. Único con `objetivo`. |
| `fecha_revision` | date | Fecha real de la revisión. |
| `que_ha_logrado` | text | Columna 2 del Excel. |
| `motivo_no_consecucion` | text | Columna 3 del Excel. |
| `propuesta_apoyos` | text | Columna 4 del Excel. |
| `realizada_por` | FK Profesional | Gestor/a de caso o persona de referencia. |
| `created_at`, `updated_at` | timestamp | Auditoría. |

Restricción: `unique_together = (objetivo, anualidad)` — una sola revisión por año y objetivo. Las revisiones acumuladas componen la trayectoria.

---

## Vista imprimible nueva

URL pública: `/planes-vida/persona/<id>/revision-objetivos/<anualidad>/`

Plantilla: [`backend/templates/pia/revision_objetivos.html`](../../backend/templates/pia/revision_objetivos.html).

- **A4 horizontal** (`@page { size: A4 landscape }`).
- Cabecera con título, nombre y apellidos, fecha, persona de referencia, gestor/a — replica el Excel.
- Tabla de 4 columnas con cabeceras verdes corporativas (`#1e6b4b`).
- Botón "🖨 Imprimir" oculto al imprimir.
- Si no hay objetivos todavía, muestra fila vacía con mensaje.

Permite **sustituir nativamente la plantilla Excel** que usan hoy los gestores/as. Cuando el Excel legado se retire (decisión validada por Federico el 2026-05-13), ÁGORA genera este documento directamente.

---

## Implicaciones en el resto del sistema

- **Admin Django**: `RevisionObjetivo` accesible directamente y como inline en `Objetivo`.
- **Datos sintéticos**: cada objetivo del plan tiene ahora una revisión generada coherente con su estado (textos distintos según `logrado/activo/mantenimiento/propuesto/abandonado`).
- **Bitácora**: la ruta nueva ya queda cubierta por el regex `/planes-vida/`.
- **Plan de Vida**: la página del plan enlaza ahora directamente al documento imprimible.

---

## Próximo paso natural

Cuando me confirmes el formato exacto de los otros documentos del protocolo, replico el mismo esquema:

1. ~~Revisión de objetivos~~ — hecho con este Excel.
2. Historia de Vida — pendiente plantilla real.
3. Algo sobre mí — pendiente plantilla real.
4. Plan de apoyo al proyecto de vida — pendiente plantilla real.
5. Proyecto de vida — pendiente plantilla real.

Pásame las plantillas en Excel/Word cuando las tengas y los modelo con la misma lógica (cabecera consistente + tabla narrativa + vista imprimible que reemplace al original).

---

*Modelo v0.3 — generado 2026-05-13 tras analizar `modelo revisión objetivos 2025 (1).xlsx`.*

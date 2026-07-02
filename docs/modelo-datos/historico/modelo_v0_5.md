# Modelo de datos ÁGORA — v0.5 (Plan de Vida limpio, sin estructuras inferidas)

**Estado**: 5 documentos del Protocolo Planes de Vida modelados como contenedores. La estructura interna concreta (preguntas, secciones, columnas, bloques) queda **pendiente de la plantilla en blanco oficial** validada por Dirección de Centros y Servicios.
**Fecha**: 2026-05-13
**Sustituye a**: `modelo_v0_4.md`.

> Federico solicitó **no tener en cuenta** el contenido inspeccionado en los 4 documentos rellenados con datos personales. Esta versión retira todo lo que se había inferido de ellos.

---

## Cambios respecto a v0.4

| Aspecto v0.4 | Estado en v0.5 |
|---|---|
| `PREGUNTAS_HISTORIA_VIDA` con 9 preguntas | **Lista vacía**. A rellenar cuando llegue el guion oficial. |
| `SECCIONES_ALGO_SOBRE_MI` con 11 secciones | **Lista vacía**. A rellenar cuando llegue la plantilla oficial. |
| `DimensionCalidadVida` + `DIMENSIONES_CDV_SCHALOCK` (8 dimensiones Schalock) | **Modelo y catálogo eliminados**. A reconstruir si se valida marco oficial. |
| `EntradaPlanApoyo` con 9 columnas concretas (apoyo_qué/quién/cuándo, seguimiento, etc.) y M2M a dimensiones | **Reducida a campos genéricos**: `titulo_objetivo`, `contenido` (texto libre), `objetivo_vinculado`. |
| `ProyectoDeVida` con 7 bloques narrativos (mi pasado, mi presente, etc.) | **Reducido a un único campo** `contenido` texto libre. |
| Datos sintéticos con respuestas, secciones y entradas rellenadas | **Solo contenedores vacíos**: se crea la fila por plan pero sin contenidos derivados. |

---

## Estado actual de los 5 documentos

| Doc | Nombre | Modelo en ÁGORA | Estructura interna |
|---|---|---|---|
| 1 | Historia de Vida | `HistoriaDeVida` + `RespuestaHistoriaVida` (genérico) | Pendiente plantilla oficial |
| 2 | Algo sobre mí | `AlgoSobreMi` + `SeccionAlgoSobreMi` (genérico) | Pendiente plantilla oficial |
| 3 | Revisión de objetivos | `RevisionObjetivo` (4 columnas) | ✅ Validada con plantilla en blanco recibida |
| 4 | Plan de apoyo al proyecto de vida | `PlanDeApoyo` + `EntradaPlanApoyo` (genérico) | Pendiente plantilla oficial |
| 5 | Proyecto de vida | `ProyectoDeVida` (contenido libre) | Pendiente plantilla oficial |

---

## Por qué este replanteamiento

El protocolo PDF oficial (recibido el primer día) define **los nombres de los 5 documentos** y el flujo, pero **no detalla la estructura interna** de cada uno. La información estructural que tenía (preguntas, columnas, dimensiones) procedía de la inspección de documentos rellenados con datos personales reales, cuya **fiabilidad no estaba garantizada** y cuyo uso para modelar ÁGORA plantea dudas:

- Pueden ser versiones antiguas no oficiales.
- Pueden ser variaciones que un centro adoptó sobre la plantilla común.
- No están firmadas como "estándar Aspanias".

Federico ha decidido **no inferir el modelo a partir de esos documentos personales**, lo que es coherente con la prudencia RGPD (no usar datos categoría especial ni siquiera como referencia estructural) y con buenas prácticas de software (no fijar un modelo basado en una muestra de un caso).

---

## Implicaciones prácticas

### Lo que sigue funcionando

- Plan de Vida completo (cabecera con gestor/a, persona de referencia, anualidad, estado).
- Los 5 documentos como contenedores: se pueden crear, listar, editar desde el admin.
- Vistas imprimibles A4 ya enlazadas desde el Plan de Vida, con cabecera y placeholder cuando no hay contenido.
- Revisión de objetivos (documento 3) funcional al 100% — su plantilla sí está validada.

### Lo que requiere la plantilla oficial

- Estructura interna de los 4 documentos restantes.
- Catálogos de preguntas/secciones/columnas.
- Reglas de validación específicas (campos obligatorios, formatos).

### Lo que está OK hacer ya

- Probar el flujo: crear persona → asignar gestor/a → generar Plan de Vida → marcar documentos como completados.
- Validar con Dirección de Centros y Servicios el flujo de revisión anual.
- Documentar el procedimiento operativo.

---

## Próximo paso

Cuando Dirección de Centros y Servicios entregue las **plantillas en blanco oficiales** (cuatro documentos restantes), modelar la estructura interna concreta de cada uno y restablecer:
- Catálogo de preguntas de Historia de Vida.
- Catálogo de secciones de Algo sobre mí.
- Columnas y catálogos del Plan de Apoyo (con o sin Schalock — a confirmar).
- Bloques narrativos del Proyecto de Vida.

---

*Modelo v0.5 — generado 2026-05-13. Refleja la decisión de no inferir estructura a partir de documentos personales rellenados.*

# Modelo de datos ÁGORA — v0.4 (Plan de Vida completo, 5 documentos)

**Estado**: 5 documentos del Protocolo Planes de Vida modelados. Pendiente afinar Historia de Vida, Algo sobre mí, Plan de Apoyo y Proyecto de Vida con las **plantillas en blanco oficiales** (no recibidas todavía limpias).
**Fecha**: 2026-05-13
**Sustituye a**: `modelo_v0_3.md`.

> v0.3 cubría "Revisión de objetivos" (el único con plantilla en blanco recibida).
> v0.4 añade los **otros 4 documentos** con modelo conservador, suficiente para arrancar pero pendiente de afinar.

---

## Estado actual de los 5 documentos

| Doc | Nombre | Plantilla recibida | Modelo en ÁGORA | Vista imprimible |
|---|---|---|---|---|
| 1 | Historia de Vida | ❌ (la versión recibida contenía datos personales) | `HistoriaDeVida` + `RespuestaHistoriaVida` (9 preguntas del guion del protocolo) | `/planes-vida/persona/<id>/historia-vida/<anualidad>/` |
| 2 | Algo sobre mí | ✅ Estructura visible (DNI, Tutor, Movilidad, Higiene, Comunicación) — pendiente plantilla completa | `AlgoSobreMi` + `SeccionAlgoSobreMi` (11 secciones orientativas) | `/planes-vida/persona/<id>/algo-sobre-mi/<anualidad>/` |
| 3 | Revisión de objetivos | ✅ Excel limpio recibido (v0.3) | `RevisionObjetivo` (4 columnas, 1 por objetivo y anualidad) | `/planes-vida/persona/<id>/revision-objetivos/<anualidad>/` |
| 4 | Plan de apoyo al proyecto de vida | ✅ Estructura visible (8 dimensiones Schalock + tabla 9 columnas) — pendiente plantilla limpia | `PlanDeApoyo` + `DimensionCalidadVida` (8 dimensiones Schalock) + `EntradaPlanApoyo` (9 columnas) | `/planes-vida/persona/<id>/plan-apoyo/<anualidad>/` |
| 5 | Proyecto de vida | ❌ (la versión recibida contenía contenido personal de la persona) | `ProyectoDeVida` con bloques narrativos (mi pasado, mi presente, sueños, apoyos, relaciones, día a día, otros) | `/planes-vida/persona/<id>/proyecto-vida/<anualidad>/` |

---

## Catálogos creados

### Preguntas de Historia de Vida (`PREGUNTAS_HISTORIA_VIDA`)

Tomadas literalmente del guion del Protocolo Aspanias visto en la inspección estructural:
1. HV01 · Momento de especial alegría.
2. HV02 · Qué te gustaba hacer / en qué eres bueno.
3. HV03 · Qué has estudiado / te gustaría seguir formándote.
4. HV04 · En qué te gustaría trabajar.
5. HV05 · Dónde has estado de vacaciones / dónde te gustaría ir.
6. HV06 · Algo que siempre quisiste hacer.
7. HV07 · Momentos en los que consigues evadirte.
8. HV08 · Imagina que no existe barrera.
9. HV09 · Momentos más importantes de tu vida.

### Secciones de Algo sobre mí (`SECCIONES_ALGO_SOBRE_MI`)

Orientativas — afinar con la plantilla en blanco oficial: identificación, movilidad, higiene, comunicación, alimentación, descanso y sueño, salud y medicación, relaciones, ocio y gustos, preferencias y rutinas, otros aspectos relevantes.

### Dimensiones de Calidad de Vida — Modelo Schalock (`DIMENSIONES_CDV_SCHALOCK`)

Las 8 dimensiones del modelo de Schalock & Verdugo, tal como aparecen en el "Anexo 4 · Plan de Apoyo":
1. Autodeterminación.
2. Bienestar Emocional.
3. Bienestar Físico.
4. Bienestar Material.
5. Relaciones Interpersonales Significativas.
6. Inclusión Social.
7. Desarrollo Personal.
8. Derechos.

---

## URL pattern

Acceso a documentos imprimibles desde la página del Plan de Vida:

```
/planes-vida/persona/<id>/                           → Detalle Plan de Vida (con enlaces a los 5 documentos)
/planes-vida/persona/<id>/historia-vida/<año>/       → Documento 1 imprimible
/planes-vida/persona/<id>/algo-sobre-mi/<año>/       → Documento 2 imprimible
/planes-vida/persona/<id>/revision-objetivos/<año>/  → Documento 3 imprimible (definitivo, plantilla validada)
/planes-vida/persona/<id>/plan-apoyo/<año>/          → Documento 4 imprimible
/planes-vida/persona/<id>/proyecto-vida/<año>/       → Documento 5 imprimible
/planes-vida/persona/<id>/panel/                     → Panel objetivos visibles (protocolo §6)
```

---

## Pendientes para v0.5

1. **Plantillas en blanco oficiales** (sin datos rellenados) de Historia de Vida, Algo sobre mí, Plan de Apoyo y Proyecto de Vida. Cuando lleguen:
   - Afinar etiquetas exactas de secciones en `Algo sobre mí`.
   - Confirmar bloques narrativos del `Proyecto de Vida` (¿mi pasado/presente/futuro? ¿otras secciones?).
   - Validar las preguntas de `Historia de Vida` (las 9 actuales son una inferencia razonable, podrían ser más o ligeramente distintas).
   - Confirmar la cabecera "ANEXO 4" del Plan de Apoyo (campos exactos).
2. **Edición desde la web**: por ahora los 4 documentos solo se editan desde el admin Django. Formularios HTMX en M2.
3. **Versionado por anualidad real**: ahora se crea 1 documento por plan. En el futuro: histórico longitudinal navegable.
4. **Firma electrónica** del Proyecto de Vida y del Plan de Apoyo (los 2 que van a REPRISS).
5. **Importador del Excel `ficha seguimiento objetivos`**: estructura coincide con `RevisionObjetivo`, el importador del Excel legado ya lo cubre con pequeño ajuste de columnas.

---

## Datos sintéticos generados

Cada Plan de Vida sintético tiene ahora:
- Historia de Vida con 9 respuestas narrativas.
- Algo sobre mí con 11 secciones.
- Plan de Apoyo con tantas entradas como objetivos, vinculadas a 1-3 dimensiones de Calidad de Vida.
- Proyecto de Vida con 6 bloques narrativos.
- Plan de Vida + Documentos genéricos (los 5 del protocolo, ya en v0.2).
- Revisiones de objetivos (v0.3) y Cambios significativos (v0.2).

Para arrancar el entorno con todos los datos sintéticos cargados: `make datos-sinteticos` desde la raíz.

---

*Modelo v0.4 — generado 2026-05-13 tras intentar procesar el ZIP `Proyecto de vida.zip`. Estructura conservadora, suficiente para arrancar el piloto, pendiente de afinar con plantillas en blanco oficiales.*

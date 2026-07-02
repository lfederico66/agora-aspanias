# Modelo de datos ÁGORA — v0.6 (4 de 5 documentos validados con plantillas oficiales)

**Estado**: 4 de los 5 documentos del Plan de Vida ya modelados con **plantilla oficial Aspanias** en blanco. Solo Historia de Vida queda pendiente.
**Fecha**: 2026-05-13
**Sustituye a**: `modelo_v0_5.md`.

> Federico entregó las plantillas en blanco oficiales. Tres archivos resultaron realmente limpios (Algo sobre mí, Plan de Apoyo, Proyecto de Vida); uno conserva respuestas rellenadas (Historia de Vida). Para los tres limpios, modelo definitivo con la estructura validada. Para Historia de Vida, contenedor genérico hasta nueva entrega.

---

## Estado actual de los 5 documentos

| Doc | Nombre | Plantilla recibida | Modelo en ÁGORA | Vista imprimible |
|---|---|---|---|---|
| 1 | Historia de Vida | ❌ aún rellenada (12 párrafos narrativos) | `HistoriaDeVida` + `RespuestaHistoriaVida` (sin catálogo de preguntas) | Placeholder hasta plantilla limpia |
| 2 | **Algo sobre mí** | ✅ **Plantilla oficial validada** | `AlgoSobreMi` + 11 secciones temáticas oficiales | A4 portrait con 11 secciones |
| 3 | Revisión de objetivos | ✅ Excel limpio (v0.3) | `RevisionObjetivo` (4 columnas) | A4 landscape |
| 4 | **Plan de Apoyo (Anexo 4)** | ✅ **Plantilla oficial validada** | `PlanDeApoyo` + `DimensionCalidadVida` (8 Schalock) + `EntradaPlanApoyo` (9 columnas) | A4 landscape |
| 5 | **Proyecto de Vida** | ✅ **Plantilla oficial validada** | `ProyectoDeVida` con 8 bloques narrativos oficiales | A4 portrait |

---

## Cambios respecto a v0.5

| Aspecto v0.5 | v0.6 |
|---|---|
| `SECCIONES_ALGO_SOBRE_MI = []` | 11 secciones de la plantilla oficial: Datos personales, Salud, Alimentación, Sueño y continencia, Movilidad, Higiene, Autonomía AVD, Comunicación, Salud mental, Desarrollo personal, Relaciones. |
| `DimensionCalidadVida` eliminado | **Reincorporado** con las 8 dimensiones Schalock oficiales del ANEXO 4. |
| `EntradaPlanApoyo` con `contenido` libre | **9 columnas oficiales**: actividades, dimensiones_cdv (M2M), apoyo_que/quien/cuando, observaciones, seguimiento cuantitativo/descriptivo. |
| `ProyectoDeVida.contenido` libre | **8 campos narrativos oficiales**: sueno_1, sueno_2, sueno_3, valores, me_gusta_dia_a_dia, no_me_gusta_dia_a_dia, apoyos_naturales, apoyos_profesionales, apoyos_comunitarios, hitos_historia_vida. |
| Plantillas imprimibles con placeholder | **Plantillas oficiales reales** para Algo sobre mí, Plan de Apoyo y Proyecto de Vida (Django + demo HTML). |
| Datos sintéticos sin documentos | Crea contenedor + estructura vacía: 11 secciones de Algo sobre mí + 1 entrada por objetivo en Plan de Apoyo + dimensiones Schalock cargadas. |

---

## Estructura oficial de cada documento

### Documento 2 · Algo sobre mí (11 secciones)

1. Datos personales (situación legal, tutor, prestaciones)
2. Salud y medicación
3. Alimentación e ingesta de líquidos
4. Sueño y continencia
5. Movilidad
6. Higiene y cuidado personal
7. Autonomía en actividades de la vida diaria
8. Comunicación
9. Salud mental y diagnósticos
10. Desarrollo personal, laboral y de ocio
11. Relaciones interpersonales y espacios que habito

### Documento 4 · Plan de Apoyo al Proyecto de Vida (ANEXO 4)

**Cabecera**: Nombre · Apellidos · Edad · Profesional de referencia · Gestor/a de caso · Fecha de realización.

**Dimensiones de Calidad de Vida** (modelo Schalock & Verdugo, 8 dimensiones):
1. Autodeterminación (control personal, elección)
2. Bienestar Emocional (felicidad, seguridad)
3. Bienestar Físico (salud, nutrición, cuidados básicos)
4. Bienestar Material (pertenencias, empleo)
5. Relaciones Interpersonales Significativas (amigos, familias)
6. Inclusión Social (comunidad, aceptación)
7. Desarrollo Personal (habilidades, experiencias nuevas)
8. Derechos (libertades, intimidad, privacidad, dignidad, autonomía, ciudadanía)

**Tabla 9 columnas**: OBJETIVOS · ACTIVIDADES · DIMENSIONES CdV · QUÉ (Apoyo) · QUIÉN (Me apoya) · CUÁNDO (Me apoyan) · OBSERVACIONES · SEGUIMIENTO CUANTITATIVO · SEGUIMIENTO DESCRIPTIVO.

### Documento 5 · Proyecto de Vida (8 bloques)

1. **Deseos y Metas**: Sueño 1, Sueño 2, Sueño 3
2. **Valores**
3. **Lo que me gusta de mi día a día**
4. **Lo que NO me gusta de mi día a día**
5. **Red de apoyos**:
   - Apoyos naturales (familia, amigos)
   - Apoyos profesionales (equipo del centro)
   - Apoyos comunitarios (parroquia, vecinos, voluntariado)
6. **Hitos · Mi Historia de Vida**

Publicable en REPRISS por Dirección.

---

## URLs oficiales

```
/planes-vida/persona/<id>/                           → Detalle Plan de Vida con enlaces a los 5 documentos
/planes-vida/persona/<id>/historia-vida/<año>/       → Documento 1 imprimible (placeholder)
/planes-vida/persona/<id>/algo-sobre-mi/<año>/       → Documento 2 imprimible (oficial)
/planes-vida/persona/<id>/revision-objetivos/<año>/  → Documento 3 imprimible (oficial)
/planes-vida/persona/<id>/plan-apoyo/<año>/          → Documento 4 imprimible (oficial)
/planes-vida/persona/<id>/proyecto-vida/<año>/       → Documento 5 imprimible (oficial)
/planes-vida/persona/<id>/panel/                     → Panel §6 (objetivos visibles)
```

---

## Pendiente para v0.7

- **Historia de Vida**: cuando se reciba la plantilla en blanco realmente vacía (sin las 12 respuestas narrativas que aún incluye), incorporar el catálogo de preguntas oficial y completar `PREGUNTAS_HISTORIA_VIDA`.
- **Edición desde la web** (no solo desde admin) de los 3 documentos oficiales: formularios HTMX en M2.
- **Importador del Excel "ficha seguimiento de objetivos"**: ya cubierto por `RevisionObjetivo`, pendiente verificar mapeo de columnas si el formato evoluciona.

---

*Modelo v0.6 — generado 2026-05-13 tras verificar que 4 de 5 plantillas oficiales en blanco están limpias y modelar su estructura definitiva.*

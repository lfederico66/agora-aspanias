# Modelo de datos ÁGORA — v0.7 (Plan de Vida COMPLETO, 5/5 documentos oficiales)

**Estado**: ✅ **Los 5 documentos del Plan de Vida modelados con plantilla oficial Aspanias**. Hito completado.
**Fecha**: 2026-05-13
**Sustituye a**: `modelo_v0_6.md`.

> Federico aclaró que los párrafos largos que mi detector marcaba como "respuestas rellenadas" en Historia de Vida son en realidad las **preguntas/pistas del guion oficial**, no respuestas de la persona. Verificación posterior confirmó cero datos personales en el documento (sin DNI, sin nombres reales, sin teléfonos, sin fechas concretas).

---

## Estado actual de los 5 documentos

| Doc | Nombre | Plantilla recibida | Modelo en ÁGORA | Vista imprimible |
|---|---|---|---|---|
| 1 | **Historia de Vida** | ✅ Guion oficial validado (v0.7) | `HistoriaDeVida` + 21 `RespuestaHistoriaVida` + `texto_narrativo_final` | A4 portrait con guion + claves metodológicas |
| 2 | Algo sobre mí | ✅ Plantilla oficial validada (v0.6) | `AlgoSobreMi` + 11 secciones temáticas | A4 portrait |
| 3 | Revisión de objetivos | ✅ Excel limpio validado (v0.3) | `RevisionObjetivo` (4 columnas, 1 por objetivo y anualidad) | A4 landscape |
| 4 | Plan de Apoyo (Anexo 4) | ✅ Plantilla oficial validada (v0.6) | `PlanDeApoyo` + `DimensionCalidadVida` (8 Schalock) + `EntradaPlanApoyo` (9 cols) | A4 landscape |
| 5 | Proyecto de Vida | ✅ Plantilla oficial validada (v0.6) | `ProyectoDeVida` con 8 bloques narrativos oficiales | A4 portrait |

---

## Cambios respecto a v0.6

| Aspecto v0.6 | v0.7 |
|---|---|
| `PREGUNTAS_HISTORIA_VIDA = []` | **21 preguntas/pistas oficiales** del guion Aspanias. |
| Plantilla Historia de Vida con placeholder | **Plantilla oficial completa**: introducción metodológica, claves de relación profesional-persona (7 claves), 21 preguntas, redacción final. |
| Demo Historia de Vida como "Contenedor listo" | **Funcional** (chip verde) con ejemplo completo de las 21 preguntas en la demo. |
| Modelo `HistoriaDeVida` sin texto final | Añadido campo `texto_narrativo_final` para la redacción final del documento tras la conversación. |
| Datos sintéticos sin respuestas | Cada plan genera las **21 preguntas vacías** del guion oficial listas para rellenar. |
| Nueva constante `CLAVES_RELACION_HISTORIA_VIDA` | Catálogo de las 7 claves metodológicas que se muestran en cabecera del documento. |

---

## Guion oficial Historia de Vida (21 preguntas)

Conforme al protocolo Aspanias, **no es un cuestionario rígido**: son pistas para generar diálogo centrado en lo importante para la persona. El profesional puede usar las que considere oportunas.

1. Cómo es tu vida actualmente
2. ¿Cómo es un día habitual en tu vida actual?
3. Qué cosas son importantes para la persona
4. Qué es lo que tiene más valor en su vida
5. Con qué disfruta. Qué cosas hacen que su vida merezca la pena
6. Qué es lo que más echarías de menos si no pudieras hacerlo
7. Cómo es un buen día y un mal día
8. Cómo era tu vida cuando eras niña/o
9. Recuerda actividades en las que disfrutabas cuando eras más joven (con sub-preguntas)
10. ¿Hacías alguna actividad de ocio con tu familia?
11. Recuerda algún momento de especial alegría en tu vida
12. Qué te gustaba hacer. ¿En qué eres bueno/a?
13. ¿Qué has estudiado, te gustaría seguir formándote? ¿En qué?
14. ¿Es importante el trabajo para ti? ¿Has trabajado?
15. ¿En qué te gustaría trabajar si encontrases trabajo?
16. ¿Dónde has estado de vacaciones o de viaje? ¿Y dónde te gustaría ir?
17. ¿Hay algo que siempre quisiste hacer, pero que no has llegado a realizar nunca?
18. Según la gente que te conoce, ¿qué es lo que mejor se le da hacer?
19. ¿Hay momentos en los que consigues evadirte de tus problemas?
20. Imagina que no existe ninguna barrera... ¿Qué harías?
21. ¿Cuáles han sido los momentos más importantes de tu vida?

## Claves metodológicas oficiales (7 claves)

Para guiar la relación profesional ↔ persona durante la entrevista de Historia de Vida:

1. Interacción simétrica, humildad de la persona de apoyo.
2. Escuchar de manera especial, centrado en la persona.
3. Mostrar cercanía de manera natural.
4. Expresar empatía, amor, amabilidad y transparencia.
5. No solucionar y validar incondicionalmente.
6. Actuar con conciencia y valentía.
7. No centrar la conversación en problemas o enfermedades.

---

## Hito alcanzado: 5/5 documentos del protocolo modelados

```
Historia de Vida       → ✅ oficial (21 preguntas + claves + narrativa final)
Algo sobre mí          → ✅ oficial (11 secciones)
Revisión de objetivos  → ✅ oficial (4 columnas)
Plan de Apoyo          → ✅ oficial (8 dimensiones Schalock + 9 columnas)
Proyecto de Vida       → ✅ oficial (8 bloques narrativos)
```

**ÁGORA está listo para acoger los Planes de Vida reales de Aspanias.** Los profesionales pueden:
1. Crear personas atendidas desde la web.
2. Asignar gestor/a de caso y persona de referencia (con avisos automáticos al cambiar).
3. Generar el Plan de Vida anual con los 5 documentos.
4. Imprimir cualquiera de los 5 documentos en formato A4 oficial.

---

## Para v0.8 (próximo paso lógico)

- **Edición desde la web** (no solo desde admin) de cualquiera de los 5 documentos. Formularios HTMX por sección con autoguardado.
- **Firma electrónica** del Proyecto de Vida y Plan de Apoyo antes de publicar en REPRISS.
- **Importador del Excel "ficha seguimiento de objetivos"** del legado para migrar datos históricos.

---

*Modelo v0.7 — generado 2026-05-13. Plan de Vida completo y alineado con protocolo oficial Aspanias.*

# Modelo de datos ÁGORA — v0.8 (edición web operativa de los 5 documentos)

**Estado**: ✅ Los profesionales pueden **introducir y editar los 5 documentos del Plan de Vida desde la propia web** (sin admin de Django).
**Fecha**: 2026-05-13
**Sustituye a**: `modelo_v0_7.md`.

> Federico solicitó: "¿cómo introduzco datos en el Plan de Vida?". Hasta v0.7 solo se podía desde el admin. v0.8 añade formularios web Django + Tailwind para que cualquier profesional con SSO M365 introduzca y edite los datos del Plan de Vida directamente.

---

## Nuevas rutas de edición

```
/planes-vida/persona/<id>/historia-vida/<año>/editar/      → Editor de Historia de Vida (21 preguntas + redacción final)
/planes-vida/persona/<id>/algo-sobre-mi/<año>/editar/      → Editor de Algo sobre mí (11 secciones)
/planes-vida/persona/<id>/revision-objetivos/<año>/editar/ → Editor de Revisión de Objetivos (1 por objetivo, 4 campos)
/planes-vida/persona/<id>/plan-apoyo/<año>/editar/         → Editor del Plan de Apoyo (filas con 9 columnas + dimensiones)
/planes-vida/persona/<id>/proyecto-vida/<año>/editar/      → Editor de Proyecto de Vida (8 bloques narrativos)
```

Cada vista imprimible tiene ahora un botón **✎ Editar** junto al de Imprimir, para alternar entre lectura y edición sin pasar por el admin.

---

## Patrón técnico

- **ModelForm + InlineFormSet** estándar de Django para cada documento.
- Plantillas Tailwind consistentes en `backend/templates/pia/editar_*.html`.
- Auto-creación de contenedores vacíos al entrar al editor si no existen (`_get_or_create_historia`, `_get_or_create_algo`).
- Para Historia de Vida y Algo sobre mí: las preguntas/secciones del catálogo oficial vienen pre-creadas, el profesional solo rellena las respuestas/contenidos.
- Para Plan de Apoyo: las dimensiones de Calidad de Vida se eligen con `CheckboxSelectMultiple` (multiselección de las 8 Schalock).
- Plan de Apoyo permite **añadir nuevas entradas** y **marcar para eliminar**.
- Revisión de Objetivos: un formulario por cada objetivo del plan, con `prefix` único.

---

## Validaciones automáticas

- La bitácora `core.RegistroAcceso` registra cada acceso a las rutas `/planes-vida/...` (incluidas las de edición) — sin tocar nada, ya estaba cubierto por el regex.
- El middleware sigue capturando POST como acción "editar".
- Las señales de `personas.signals` ya detectan cambios de gestor/a y persona de referencia desde cualquier edición de PersonaAtendida.

---

## Lo que NO está aún

- **Autoguardado HTMX** al perder foco en cada campo: ahora hay un botón "Guardar" al final del formulario. HTMX lo dejamos para una iteración posterior si lo necesitas.
- **Firma electrónica** dentro del editor del Proyecto de Vida (es una pieza distinta, M3).
- **Edición concurrente**: no hay bloqueo si dos profesionales editan el mismo documento simultáneamente. Para v1 con piloto de un solo gestor/a por persona, no es problema crítico.

---

## Para v0.9

- Autoguardado HTMX por campo.
- Edición inline desde la propia vista imprimible (sin cambiar de página).
- Comentarios entre profesionales sobre cada sección.

---

*Modelo v0.8 — generado 2026-05-13. Edición web operativa de los 5 documentos del Plan de Vida.*

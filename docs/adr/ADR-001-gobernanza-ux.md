# ADR-001 — Gobernanza UX y reglas vinculantes del repositorio

**Estado**: Aceptado
**Fecha**: 2026-06-05
**Decisor**: Federico Martínez · Gerencia
**Contexto**: Auditoría de organización al cerrar el módulo Equipo (45 páginas, 88 tareas completadas)

---

## Problema

Durante la construcción de ÁGORA (mayo-junio 2026) la arquitectura ha crecido sin gobernanza explícita:

- Sidebar principal con 9 ítems planos sin agrupación
- Duplicidades de navegación: Tablero ↔ En cifras, Agenda ↔ Turnos ↔ Calendario laboral
- Pestañas internas inflándose (persona 7 tabs, profesional 7, centro 5)
- Iconos repetidos (📊 ×2, tres iconos de tiempo)
- Botones de acción dispersos sin pauta consistente
- 45 HTMLs sin clasificación clara de quién los ve
- Documentos imprimibles sueltos sin agrupación

El riesgo de seguir sin reglas es que cada módulo nuevo añade complejidad linealmente y la curva de aprendizaje del usuario final se hace insostenible.

---

## Decisión

Se adoptan **3 reglas de gobernanza UX vinculantes** para todo el repositorio, documentadas en `CLAUDE.md` §"Reglas de gobernanza UX" y operativizadas en `docs/MAPA_ROLES.md` y `docs/GLOSARIO.md`.

### Regla 1 — 7±2 (Miller)
Ningún menú, sidebar, lista de tabs, sección de acciones o sub-sección supera **7 elementos** sin agrupación visible.

**Operativización**:
- Sidebar agrupado en 4-5 bloques (Atención · Operativa · Análisis · Sistema)
- Tabs internas de más de 7 elementos → refactorizar con sub-pestañas o secciones plegables
- Cabeceras de botones de más de 5 acciones → menú "Más" con dropdown

### Regla 2 — Usuario único
Cada nueva pantalla declara explícitamente qué rol(es) la verá. Si no aplica a un rol, no aparece en su sidebar.

**Operativización**:
- 6 roles canónicos definidos en `docs/MAPA_ROLES.md`
- Cada template Django: comentario `{# @rol: gerencia, direccion_centro #}` al inicio
- Cada HTML de demo: comentario `<!-- @rol: ... -->` al inicio del `<body>`
- Sidebar adaptativo según rol
- Selector de rol visible en demo (cookie `agora_rol`)

### Regla 3 — No antes de
Antes de añadir una funcionalidad nueva, comprobar 4 puntos:
1. Existencia previa en otro módulo (no duplicar)
2. Solapamiento con SIGPER, EQUIPO, CERCA (documentar frontera)
3. Profundidad: aplicar Regla 1
4. Aplicabilidad por rol: aplicar Regla 2

---

## Consecuencias

### Positivas
- Curva de aprendizaje gestionada por rol (cada usuario ve solo lo suyo)
- Crecimiento del producto controlado
- Cumplimiento RGPD por capacidad (minimización + tutela Ley 8/2021)
- Documentación de fronteras con proyectos hermanos
- Onboarding nuevo equipo más simple

### Negativas / a vigilar
- Más burocracia antes de añadir features
- Requiere disciplina en revisión de cambios (PRs)
- La demo crece en complejidad técnica (cookies, condicionales por rol)
- Tiempo invertido en refactor que no añade funcionalidad nueva

### Coste estimado del refactor inicial
- Tier 1 (quick wins): ~45 min
- Tier 2 (reorganización media): ~2 h
- Tier 3 (refactor estructural): ~3 h
- **Total**: ~6 h aplicado en sesión 2026-06-05

---

## Alternativas consideradas

1. **No hacer nada y seguir añadiendo** — descartado, riesgo de inmanejabilidad antes de Q1 2027.
2. **Reescribir desde cero con design system completo** — desproporcionado, demora pre-piloto.
3. **Sólo Tier 1 (quick wins)** — insuficiente, no resuelve el problema de roles ni duplicidades.

---

## Seguimiento

- Auditoría trimestral del cumplimiento de las 3 reglas
- Revisión obligatoria de cada PR contra estas reglas
- ADR-002 a definir: design tokens (botones, colores, espaciados)
- ADR-003 a definir: política de pestañas (cuándo crear nueva tab vs sub-sección)

---

*Este ADR es revisable. Cualquier modificación requiere ADR-002+ que explícitamente lo enmiende.*

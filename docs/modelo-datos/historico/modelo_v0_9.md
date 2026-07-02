# Modelo de datos ÁGORA — v0.9 (apps M1 completas + importador legado)

**Estado**: ✅ Apps **Agenda**, **Intervenciones** y **Valoraciones** editables desde la web. Importador del Excel legado funcional con generador de plantilla y guía operativa.
**Fecha**: 2026-05-18
**Sustituye a**: `modelo_v0_8.md`.

> Hito M1 completo: ya no queda funcionalidad nuclear del piloto que solo se pueda usar desde el admin de Django. Cualquier profesional con SSO M365 puede crear y editar Citas, Intervenciones, Valoraciones y los 5 documentos del Plan de Vida desde la web.

---

## Lo nuevo en v0.9

### Apps M1 editables desde la web

| Funcionalidad | Antes (v0.8) | Ahora (v0.9) |
|---|---|---|
| Crear/editar **Cita** | Solo admin Django | Formulario web en `/agenda/nueva/` y `/agenda/<id>/editar/` + botón "+ Nueva cita" en vista semanal |
| Crear/editar **Intervención** | Solo admin Django | Formulario web en `/intervenciones/persona/<id>/nueva/` + vínculo opcional a Objetivo del Plan de Vida vigente + botón "+ Nueva intervención" en historial |
| Registrar **Valoración** (BVD, ICAP, SIS, Barthel, Tinetti, MMSE…) | Solo admin Django | Formulario web en `/intervenciones/persona/<id>/valoracion/nueva/` + bloque de últimas valoraciones en la ficha de persona |

### Importador del Excel legado

- Comando `python manage.py importar_excel_planes_vida` con dos modos:
  - **Generar plantilla**: `--generar-plantilla salida/plantilla.xlsx` produce un .xlsx con hojas "Seguimiento" e "Instrucciones" listo para que el gestor/a rellene con los datos del Excel actual.
  - **Importar**: `ruta.xlsx --anualidad 2026 [--dry-run]` carga los datos en ÁGORA dentro de una transacción atómica.
- Crea/actualiza `PlanDeVida` + `DocumentoPlanDeVida` por anualidad.
- Vincula automáticamente Gestor/a de Caso y Persona de Referencia por email M365.
- Reporta personas sin encontrar y errores sin abortar el resto.
- Documentación operativa completa: [`docs/migracion/excel_legado.md`](../migracion/excel_legado.md).

---

## Rutas nuevas

```
/agenda/                                                      → vista semanal (existía)
/agenda/nueva/                                                → ➕ formulario crear cita
/agenda/<uuid>/editar/                                        → ➕ formulario editar cita

/intervenciones/persona/<id>/                                 → historial (existía)
/intervenciones/persona/<id>/nueva/                           → ➕ formulario nueva intervención
/intervenciones/persona/<id>/<uuid>/editar/                   → ➕ formulario editar intervención
/intervenciones/persona/<id>/valoracion/nueva/                → ➕ formulario nueva valoración
```

---

## Vínculos cruzados nuevos

- **Intervención ↔ Objetivo PIA**: al crear una intervención, el desplegable de "Objetivo vinculado" filtra solo objetivos del Plan de Vida **vigente** de esa persona. Garantiza que el seguimiento longitudinal de un objetivo (qué se ha hecho a lo largo del año) se construye automáticamente.
- **Cita ↔ Persona**: al pulsar "Agenda semanal" desde la ficha de una persona, se pasa el `id` por query string para pre-seleccionarla al crear cita.
- **Valoración ↔ Ficha persona**: las últimas 5 valoraciones aparecen como bloque lateral en la ficha + botón directo "+ Nueva valoración".

---

## Pendiente para v1.0 (post-Patronato 10 junio)

| Bloque | Estado |
|---|---|
| Despliegue real en servidor Aspanias Burgos | ⏳ Sistemas Aspanias |
| SSO M365 funcional con credenciales reales | ⏳ Sistemas + Entra ID |
| Pentest pre-piloto | ⏳ contratar externo |
| Firma electrónica Plan de Vida (M2) | ⏳ alcance pendiente |
| Migración real del Excel legado | ✅ herramienta lista, falta el archivo real |
| Plan de Apoyo: autoguardado HTMX por campo | ⏳ M2 |

---

## Backlog post-piloto (Q1 2027 o posterior)

- **Módulo de control económico personal** de las personas atendidas (hucha/caja por persona, gastos de bolsillo, rendición anual al juzgado Ley 8/2021). Requiere Fase 0 propia con Lex Digital.
- **Integración ResiPlus** (historia clínica con prescripción farmacológica).
- **Facturación detallada** y conciliación con A3 (M3).

---

*Modelo v0.9 — generado 2026-05-18. Cierre del M1 funcional.*

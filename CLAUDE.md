# ÁGORA — Convenciones del repositorio

Este archivo es de lectura obligatoria al inicio de cada sesión de trabajo sobre ÁGORA. Define cómo se trabaja en este repositorio.

---

## Identidad del proyecto

- **Nombre**: ÁGORA — Atención y Gestión Operativa para Residentes y Atendidos.
- **Entidad**: Grupo Social Aspanias (Fundación Aspanias Burgos + Aspaniasmerc 2016 S.L.U. + Fundación CISA + Asociación Aspanias + CISA EMPLEA).
- **Documento maestro**: `PROYECTO_ÁGORA.md`.
- **Sponsor**: Federico Martínez — Gerencia.

---

## Stack obligatorio

- **Backend + frontend**: Django 5 + HTMX + Alpine.js + TailwindCSS.
- **Python**: 3.11+.
- **Base de datos**: PostgreSQL 16 desde día 1. No SQLite ni siquiera en desarrollo (usar Docker Compose con Postgres local).
- **Auth profesionales**: SSO Microsoft 365 (Entra ID).
- **Auth familias**: federada con CERCA (no propia).
- **Despliegue**: Docker Compose en VM Ubuntu 24.04 sobre Hyper-V.

No introducir nuevas dependencias sin justificación explícita y aprobación.

---

## RGPD — reglas duras

**Cualquier cambio de modelo de datos, vista o exportación debe revisarse contra estas reglas:**

1. **Solo datos sintéticos en el repositorio.** Prohibido subir nombres, DNI, teléfonos o documentos reales. Fixtures con datos generados.
2. **Bitácora de accesos**: toda lectura de ficha de persona atendida debe quedar registrada con usuario, IP, timestamp y motivo cuando proceda.
3. **Minimización**: no añadir campos "por si acaso". Cada campo debe tener finalidad documentada.
4. **Cifrado en reposo**: la BD productiva irá cifrada. Las credenciales de cifrado nunca al repositorio.
5. **Retención**: aplicar política de conservación documentada en `docs/rgpd/`. No borrar datos sin pasar por el flujo aprobado.
6. **Tutela (Ley 8/2021)**: cualquier vista que muestre datos de la persona debe respetar el ámbito de la medida de apoyo registrada. Diseñar permisos por capacidad, no solo por rol.
7. **Datos de menores**: doble consentimiento (representante + persona si mayor de 14 años) y campos de aviso visibles en la ficha.

---

## Reglas de gobernanza UX

**Vinculantes desde 2026-06-05. Aplican a cualquier vista, página, pestaña o menú nuevo del repositorio.**

### Regla 1 — 7±2 (Miller)
Ningún menú, sidebar, lista de tabs o sección de acciones puede superar **7 elementos** sin agrupación visible. Si una sección llega a 7, antes de añadir un octavo se **refactoriza con encabezados o grupos plegables**. Aplica a:
- Sidebar principal
- Pestañas de un módulo
- Botones de acción en una cabecera
- Sub-secciones dentro de una pestaña

### Regla 2 — Usuario único
Cada nueva pantalla declara explícitamente **qué rol(es) la verán**. Si no aplica a un rol, no debe aparecer en su sidebar ni ser accesible por URL para ese rol. Los roles canónicos del sistema son:

| Rol | Capacidad |
|---|---|
| `gerencia` | Vista total del grupo, decisión estratégica, Patronato |
| `direccion_centro` | Su centro: personas, equipo, calendario, caja, FIS |
| `gestor_caso` | Sus personas asignadas: PV, intervenciones, agenda |
| `profesional` | Su agenda, su calendario, sus personas, sus formaciones |
| `rrhh` | Vacaciones, calendario laboral, plantilla, nóminas |
| `familia` | Solo su persona referenciada vía CERCA |

Declarar como comentario al inicio de cada template Django y al inicio de cada HTML de la demo: `<!-- @rol: gerencia, direccion_centro -->`.

### Regla 3 — No antes de
**Antes de añadir una funcionalidad nueva**, comprobar:
1. ¿Ya existe en otro módulo? Si sí, enlazar/reutilizar, no duplicar.
2. ¿Solapa con un proyecto del grupo (SIGPER, EQUIPO, CERCA)? Si sí, documentar la frontera en `docs/modelo-datos/decision_*.md` antes de implementar.
3. ¿Genera una pestaña nueva en algún módulo? Aplicar Regla 1 antes de añadir.
4. ¿Aplica a todos los roles? Si no, aplicar Regla 2.

Sin estas tres comprobaciones, no se introduce código nuevo.

---

## Convenciones de código

- **Idioma**:
  - **Entidades y campos del dominio sociosanitario en español**: `PersonaAtendida`, `MedidaDeApoyo`, `PlanIndividualAtencion`, `Intervencion`, `nombre`, `apellido_1`, `corresponsable_principal`. El dominio jurídico-social es local; traducir distorsiona.
  - **Atributos técnicos y de auditoría en inglés**: `created_at`, `updated_at`, `is_active`, `user`.
  - **Comentarios, `verbose_name`, docstrings y mensajes de UI siempre en español**.
- **Naming Django**: `app/models.py` con un modelo principal por archivo cuando sean grandes (`PersonaAtendida`, `PlanIndividualAtencion`, `Intervencion`, `Cita`, `Valoracion`).
- **Migrations**: una migración por cambio funcional. No squash hasta Fase 2.
- **Vistas**: HTMX-first. No SPA, no React. Vistas server-side render con fragmentos HTMX para interacciones.
- **Estilos**: TailwindCSS exclusivamente. Sin CSS custom salvo casos justificados. CDN aceptable en v0.1; build con `django-tailwind` en v1.0.
- **Tests**: `pytest-django`. Test de modelo + test de vista mínimos por cada feature.

---

## Convenciones git

- Repositorio aún no inicializado. Cuando se inicialice:
  - Rama principal: `main`.
  - Ramas de feature: `feat/<modulo>-<descripcion-corta>`.
  - Commits en español, formato Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`).
  - PRs revisados antes de merge cuando haya equipo.
- `.gitignore` debe excluir: `.env`, `*.sqlite3`, `media/`, `staticfiles/`, datos reales en `datos/`.

---

## Estructura prevista

```
agora-aspanias/
├── PROYECTO_ÁGORA.md          # documento maestro
├── CLAUDE.md                  # este archivo
├── README.md                  # quickstart
├── docs/
│   ├── fase0/                 # decisiones y actas Fase 0
│   ├── modelo-datos/          # ER, diccionario de entidades
│   └── rgpd/                  # EIPD, RAT, política conservación
├── backend/                   # proyecto Django (Fase 1)
│   ├── agora/                 # config (settings, urls)
│   ├── personas/              # ficha persona atendida
│   ├── pia/                   # Plan Individual de Atención
│   ├── intervenciones/        # historial cronológico
│   ├── agenda/                # citas multiprofesionales
│   ├── indicadores/           # cuadro de mando, memoria
│   └── core/                  # auth, RBAC, bitácora, helpers
├── frontend/                  # plantillas, static, tailwind config
├── datos/                     # fixtures sintéticos
│   └── sinteticos/
├── scripts/                   # utilidades (carga inicial, exportes)
└── infraestructura/           # docker-compose, reverse proxy
```

---

## Modo de trabajo con Claude

- **Validación progresiva**: al cerrar cada bloque o decisión, resumir y pedir OK a Federico.
- **Recomendaciones razonadas**: máximo 3 opciones cuando haya que decidir, con recomendación.
- **Invocar agentes del sistema Aspanias** cuando el ámbito lo requiera:
  - `aspanias-operaciones` — modelo PIA, protocolos, AICP.
  - `aspanias-administracion` — RGPD, retención, inspecciones.
  - `aspanias-rrhh` — agenda multiprofesional, roles, ratios.
  - `aspanias-okr` — indicadores y memoria.
  - `aspanias-direccion` — decisiones estratégicas, gobernanza.
  - `asesor-juridico-tercer-sector` — base jurídica, Ley 8/2021, contratos con DPO externo.
  - `tercer-sector-financiero` — viabilidad, facturación M3.
- **No tocar Odoo** (`preaspanias.integrodoo.com`) desde este repositorio. Es sistema legado con plan de salida a definir.

---

## Fases del proyecto

- **Fase 0** — Decisiones de alcance, stack, gobernanza (cerrada 2026-05-13, pendiente validación formal).
- **Fase 1** — Modelo de datos + scaffolding Django + EIPD inicial.
- **Fase 2** — Módulos M1: ficha, PIA, agenda, indicadores.
- **Fase 3** — Pre-piloto con equipo asistencial (sept 2026, objetivo).
- **Fase 4** — Piloto Centro Fuentecillas (Q1 2027, objetivo).
- **Fase 5** — Despliegue progresivo al resto del grupo.

---

*Convenciones v0.1 — vigentes desde 2026-05-13. Actualizar cuando cambien decisiones de Fase 0.*

---

## gstack
Use /browse from gstack for all web browsing. Never use mcp__claude-in-chrome__* tools.
Available skills: /office-hours, /plan-ceo-review, /plan-eng-review, /plan-design-review,
/design-consultation, /design-shotgun, /design-html, /review, /ship, /land-and-deploy,
/canary, /benchmark, /browse, /open-gstack-browser, /qa, /qa-only, /design-review,
/setup-browser-cookies, /setup-deploy, /setup-gbrain, /sync-gbrain, /retro, /investigate,
/document-release, /document-generate, /codex, /cso, /autoplan, /pair-agent, /careful, /freeze,
/guard, /unfreeze, /gstack-upgrade, /learn.

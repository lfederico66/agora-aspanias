# ÁGORA — Índice de documentación

**Última actualización**: 2026-06-15 (reorganización aplicada por skill `ordenador-archivos`)
**Estado del proyecto**: Demo Fase 4 · pre-piloto Fuentecillas Q1 2027

---

## Estructura del repositorio

```
agora-aspanias/
├── README.md  CLAUDE.md  PROYECTO_AGORA.md  Makefile
├── backend/                ← código Django (sin cachés Python)
├── datos/                  ← fixtures sintéticos
├── demo/                   ← 46 HTMLs estáticos (la demo de Netlify)
├── dist/                   ← artefactos build
│   ├── actual/             ← ZIP entregable vigente
│   └── historico/          ← versiones antiguas
├── docs/                   ← este árbol (ver abajo)
├── infraestructura/        ← docker-compose, conf nginx, scripts deploy
└── scripts/                ← utilidades + one-shots históricos
    ├── README.md           ← índice de scripts
    ├── utilidades/         ← reutilizables
    └── historico/          ← one-shots ya consumidos
```

## Estructura de `docs/`

```
docs/
├── INDEX.md                    ← este archivo
├── GLOSARIO.md                 ← términos del dominio
├── MAPA_ROLES.md               ← 6 roles + matriz visibilidad
├── adr/                        ← Architecture Decision Records
│   └── ADR-001-gobernanza-ux.md
├── fases/                      ← decisiones y entregables por fase
│   ├── fase0/                  ← cierre Fase 0, kickoff, decisiones fundacionales
│   ├── fase1/                  ← cierre Fase 1
│   ├── fase3/                  ← pre-piloto Fuentecillas
│   └── fase4/                  ← piloto Q1 2027
├── modelo-datos/
│   ├── modelo_actual.md        ← versión viva
│   ├── CHANGELOG.md            ← cronología de versiones
│   ├── decisiones/             ← decisiones de diseño numeradas
│   │   ├── 01_dinero_bolsillo.md
│   │   ├── 02_facturacion_servicios_extras.md
│   │   ├── 03_fis_incidencias.md
│   │   ├── 04_servicios_multiples.md
│   │   ├── 05_modulo_equipo_solapamiento.md
│   │   └── analisis_cgpr_estructura.md
│   └── historico/              ← modelo_v0_1 .. v0_11
├── migracion/                  ← excel legado, importadores
├── operaciones/                ← despliegue interno
└── rgpd/                       ← EIPD, RAT, art. 26
```

---

## Cronología de decisiones clave

| Fecha | Documento | Tipo | Impacto |
|---|---|---|---|
| 2026-05-13 | `fases/fase0/` (varios) | Fundacional | Cierre Fase 0 |
| 2026-05-20 | `modelo-datos/decisiones/analisis_cgpr_estructura.md` | Análisis Excel | Módulo dinero bolsillo |
| 2026-05-22 | `modelo-datos/decisiones/01_dinero_bolsillo.md` | Modelo | Caja + bolsillos |
| 2026-05-25 | `modelo-datos/decisiones/02_facturacion_servicios_extras.md` | Modelo | Facturación |
| 2026-05-28 | `modelo-datos/decisiones/03_fis_incidencias.md` | Modelo | FIS |
| 2026-06-01 | `modelo-datos/decisiones/04_servicios_multiples.md` | Modelo | Múltiples servicios por persona |
| 2026-06-05 | `modelo-datos/decisiones/05_modulo_equipo_solapamiento.md` | Frontera | ÁGORA ↔ SIGPER ↔ EQUIPO |
| 2026-06-05 | `adr/ADR-001-gobernanza-ux.md` | Arquitectura | 3 reglas UX vinculantes |
| 2026-06-05 | `MAPA_ROLES.md` | Roles | 6 roles canónicos |
| 2026-06-05 | `GLOSARIO.md` | Terminología | Términos dominio |
| 2026-06-15 | `scripts/utilidades/reorganizacion_log.csv` | Repo | Reorganización física aplicada |

---

## Mapa de módulos · qué decisión cubre cada uno

| Módulo | Decisiones relacionadas |
|---|---|
| **Personas atendidas** (PIA, PV, intervenciones) | `fases/fase0/`, `modelo-datos/historico/` (v0.1-v0.7), `modelo_actual.md` |
| **Centros** | `fases/fase0/`, `decisiones/04_servicios_multiples.md` |
| **Equipo** (profesionales, vacaciones, turnos, calendario) | `decisiones/05_modulo_equipo_solapamiento.md`, `adr/ADR-001-gobernanza-ux.md` |
| **Caja y bolsillos** | `decisiones/analisis_cgpr_estructura.md`, `decisiones/01_dinero_bolsillo.md` |
| **Facturación** | `decisiones/02_facturacion_servicios_extras.md` |
| **Incidencias FIS** | `decisiones/03_fis_incidencias.md` |
| **Agenda** | `modelo-datos/historico/modelo_v0_4.md` |

---

## Reglas vinculantes del repo

Documentadas en `CLAUDE.md` y `adr/ADR-001-gobernanza-ux.md`. Aplicables a cualquier cambio nuevo:

1. **Regla 7±2** — Ningún menú/tab/sección supera 7 elementos sin agrupación.
2. **Regla usuario único** — Cada pantalla declara qué rol(es) la ven.
3. **Regla no-antes-de** — Antes de añadir, comprobar duplicidad, solapamiento, profundidad y rol.

---

## Proyectos hermanos del Grupo Social Aspanias

| Proyecto | Misión | Frontera con ÁGORA |
|---|---|---|
| **ÁGORA** | CRM sociosanitario · personas atendidas | Este repo |
| **SIGPER** | Gestión permisos/licencias (Fundación) | ÁGORA solo lectura de ausencias |
| **CERCA** | Comunicación familias/usuarios | ÁGORA cede ficha persona vía API |
| **SIPAS** | CRM sociosanitario (proyecto previo) | Reemplazado por ÁGORA |
| **EQUIPO** | Suite RRHH tipo Bizneo (9 módulos) | ÁGORA solo capa asistencial |
| **SIECP** | (fase 0 cerrada) | — |
| **Incidencias** (app Next.js) | App ligera de incidencias internas | — |

---

## Cómo revertir la reorganización de junio 2026

Si algo no convence, hay un script de reversión generado automáticamente:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/utilidades/deshacer_reorganizacion.ps1
```

El log completo de movimientos está en `scripts/utilidades/reorganizacion_log.csv`.

---

*Mantener este índice al día. Actualizar cuando se añada una decisión, módulo o frontera.*

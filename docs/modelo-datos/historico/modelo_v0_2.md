# Modelo de datos ÁGORA — v0.2 (alineado con Protocolo Planes de Vida)

**Estado**: borrador alineado con el "Protocolo de elaboración, seguimiento y revisión de Planes de Vida — Centros y Servicios, Fundación Aspanias".
**Fecha**: 2026-05-13
**Sustituye a**: `modelo_v0_1.md` (los cambios principales se documentan al final).

> Esta versión incorpora el procedimiento real de Fundación Aspanias para los Planes de Vida. Lo que en v0.1 llamábamos "Plan Individual de Atención (PIA / AICP)" pasa a denominarse **Plan de Vida**, conforme a la terminología institucional.

---

## Cambios respecto a v0.1

| Aspecto | v0.1 | v0.2 (Protocolo Aspanias) |
|---|---|---|
| Nombre del plan | Plan Individual de Atención (PIA) | **Plan de Vida** |
| Estructura | Modelo único con objetivos | **5 documentos** + objetivos + cambios significativos |
| Documentos | — | Historia de Vida · Algo sobre mí · Revisión de objetivos · Plan de apoyo al proyecto de vida · Proyecto de vida |
| Versionado | Por número de versión (v1, v2, v3) | **Por anualidad** (2025, 2026, 2027…) |
| Periodicidad | Semestral | **Anual** (revisión obligatoria) |
| Figuras profesionales | Solo "responsable PIA" | **Gestor/a de Caso + Persona de Referencia** (dos roles distintos) |
| Ratio profesional | No modelado | **30 casos máximo por Gestor/a** |
| Almacenamiento documental | Azure Blob | **Teams / OneDrive** + REPRISS para Proyecto de Vida y Plan de apoyo |
| Cambios significativos | No modelados | Entidad propia: salud, empleo, centro/vivienda, rutinas, relaciones, participación social |
| Visibilidad de objetivos | Privada | **Opcional en paneles/corchos** del centro, con consentimiento de la persona |
| Cambios de profesionales | No modelados | Protocolo de traspaso para gestor/a y persona de referencia |

---

## Entidades nuevas o modificadas

### 1. `PlanDeVida` (sustituye a `PlanIndividualAtencion`)

| Campo | Tipo | Notas |
|---|---|---|
| `persona` | FK PersonaAtendida | |
| `anualidad` | int | Año del plan: 2025, 2026, 2027… Único por persona+anualidad. |
| `estado` | enum | en_elaboración · vigente · en_revisión · archivado |
| `gestor_caso` | FK Profesional | Coordina el plan. Sujeto a ratio ≤ 30. |
| `persona_referencia` | FK Profesional | Genera vínculo significativo. |
| `fecha_elaboracion` | date | |
| `fecha_revision` | date | Última revisión anual. |
| `fecha_proxima_revision` | date | Anual obligatoria. |
| `firmado_persona_at`, `firmado_apoyo_at` | datetime | Firmas. |
| `visible_en_paneles` | bool | Voluntad de la persona usuaria. |

### 2. `DocumentoPlanDeVida` (nueva)

Una entrada por cada uno de los **5 documentos del protocolo**, con su estado, URL al almacenamiento (Teams/OneDrive) y bandera de publicación en REPRISS cuando aplica.

| Tipo | Publicado en REPRISS |
|---|---|
| Historia de Vida | No |
| Algo sobre mí | No |
| Revisión de objetivos | No |
| Plan de apoyo al proyecto de vida | **Sí** (Dirección lo cuelga) |
| Proyecto de vida | **Sí** (Dirección lo cuelga) |

### 3. `Objetivo` (sustituye a `ObjetivoPIA`)

Sin cambios estructurales mayores. Se añade:

- `visible_en_panel` (bool): si el objetivo concreto está visible en paneles del centro.
- Estado adicional: `mantenimiento` (objetivo logrado que requiere refuerzo).
- Ámbito `participacion_social` (presente en el protocolo).

### 4. `CambioSignificativo` (nueva)

Permite registrar entre revisiones anuales los cambios que pueden obligar a actualizar el Plan.

| Campo | Tipo | Notas |
|---|---|---|
| `persona` | FK PersonaAtendida | |
| `plan_vida` | FK PlanDeVida | Plan vigente al detectar el cambio. |
| `ambito` | enum | salud · empleo · centro_vivienda · rutinas · relaciones · participacion_social · otro |
| `descripcion` | text | |
| `fecha_deteccion` | date | |
| `detectado_por` | FK Profesional | Normalmente la persona de referencia. |
| `requiere_actualizacion_plan` | bool | |
| `procesado` | bool | True cuando el plan ya se ha actualizado en consecuencia. |

### 5. Ajustes a `PersonaAtendida`

Se añaden dos campos:

- `gestor_caso` (FK Profesional) — coordinador del Plan de Vida.
- `persona_referencia` (FK Profesional) — figura de vínculo significativo.

### 6. Ajustes a `Profesional`

Se añaden:

- `puede_ser_gestor_caso` (bool) — habilitación.
- `max_casos_asignados` (int, default 30) — tope del protocolo.
- Property `casos_actuales_gestor` y `sobrepasa_ratio` — control de carga.

---

## Almacenamiento documental

- **Teams / OneDrive**: ubicación principal de los 5 documentos vivos. URL almacenada en `DocumentoPlanDeVida.url_almacenamiento`.
- **Organización por anualidades** (2025/, 2026/, 2027/…) — coherente con el protocolo.
- **REPRISS**: Dirección publica ahí el "Proyecto de Vida" y el "Plan de apoyo al proyecto de vida". ÁGORA solo refleja el indicador `publicado_en_repriss`.

> El protocolo menciona también un **Excel compartido** de seguimiento. ÁGORA lo sustituye nativamente con el listado de Planes de Vida + filtros por gestor/a, estado y próxima revisión. El Excel queda obsoleto cuando ÁGORA entre en producción.

---

## Implicaciones para el resto del modelo

- `Intervencion.objetivo_vinculado` ahora apunta a `pia.Objetivo` (no a `ObjetivoPIA`).
- La bitácora `core.RegistroAcceso` registra acceso a `/planes-vida/...` (renombrada la ruta).
- En la ficha de persona se muestran explícitamente Gestor/a de Caso y Persona de Referencia — son información de cabecera, no detalle.

---

## Decisiones validadas con Dirección (2026-05-13)

1. **Nomenclatura**: "Plan de Vida" — confirmado.
2. **Aviso automático de cambio de profesional**: dispara ÁGORA (implementado vía signal en `personas/signals.py` → `AvisoCambioProfesional`; bandeja en `/personas/avisos-cambio-profesional/`).
3. **Excel compartido legado**: se retira cuando ÁGORA entre en producción. Importador disponible: `python manage.py importar_excel_planes_vida ruta.xlsx --anualidad 2026 [--dry-run]`. Columnas esperables documentadas en el comando; ajustar al Excel real cuando se reciba.
4. **REPRISS**: fuera del alcance v1. ÁGORA solo refleja el indicador `publicado_en_repriss`; Dirección sigue subiéndolo manualmente.
5. **Paneles visuales (Protocolo §6)**: ÁGORA genera formato A4 imprimible. Ruta `/planes-vida/persona/<id>/panel/`. Solo accesible si la persona ha autorizado (`plan.visible_en_paneles=True`) y solo muestra los objetivos marcados con `visible_en_panel=True`.

---

*Modelo v0.2 — generado 2026-05-13 tras revisar el "Protocolo de elaboración, seguimiento y revisión de Planes de Vida" entregado por Federico.*

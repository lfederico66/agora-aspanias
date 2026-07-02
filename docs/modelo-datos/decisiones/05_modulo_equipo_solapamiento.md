# Decisión — Módulo Equipo (profesionales + vacaciones + turnos) en ÁGORA

**Fecha**: 2026-06-05
**Decisor**: Federico Martínez — Gerencia
**Ámbito**: Grupo Social Aspanias
**Estado**: Aprobado por Gerencia · pendiente alinear con responsables de SIGPER y EQUIPO

---

## 1. Decisión

ÁGORA incorpora un módulo **Equipo** con tres bloques: **Profesionales**, **Vacaciones y ausencias** y **Turnos**, inspirado visualmente en Bizneo (referencias compartidas por Gerencia: `bizneo.com/gestor-vacaciones` y `bizneo.com/gestion-turnos`).

El módulo nace con **doble lectura**:

| Capa | Vive en | Razón |
|---|---|---|
| Operativa asistencial (quién cubre qué turno, quién está hoy en el centro, sustituciones) | **ÁGORA** | La cobertura del centro afecta directamente a la atención de la persona y al PIA. |
| Gestión laboral formal (solicitar permisos, cómputo legal de días, calendario anual, aprobaciones de RRHH) | **SIGPER** (vacaciones/permisos) + **EQUIPO** (suite tipo Bizneo) | Es competencia de RRHH y excede la misión sociosanitaria de ÁGORA. |

---

## 2. Solapamiento con proyectos en curso

Quedan vivos los tres proyectos:

- **ÁGORA** — CRM sociosanitario (este repo). Añade módulo Equipo en modo **operativo**.
- **SIGPER** — Sistema de Gestión de Permisos y Licencias (Fundación Aspanias Burgos, sustituye Excel de permutas).
- **EQUIPO** — Suite tipo Bizneo, 9 módulos, todo el grupo.

### Regla de no duplicación

1. **Datos maestros del profesional** (alta, baja, contrato, salario, antigüedad) → **EQUIPO** será fuente de verdad cuando exista. Mientras tanto, ÁGORA mantiene los campos mínimos asistenciales.
2. **Solicitud y aprobación de vacaciones / permisos** → **SIGPER** será fuente de verdad cuando esté en producción. Mientras tanto, ÁGORA permite registrar ausencias pero solo a efectos de planificación operativa.
3. **Planificación de turnos** → discutible: ÁGORA tiene buen contexto (sabe ratios, sabe ocupación). Decisión provisional: ÁGORA gestiona los turnos asistenciales del centro; EQUIPO lo recoge a efectos contables.

### Sincronización futura

- API REST bidireccional entre ÁGORA ↔ SIGPER ↔ EQUIPO. Profesional dado de alta en EQUIPO → aparece en ÁGORA. Vacación aprobada en SIGPER → bloquea turnos en ÁGORA.
- A definir en Fase 5 (despliegue 2027-2029). Hasta entonces, sincronización por exportación Excel.

---

## 3. Modelo de datos (avance)

### `Profesional`
- `nombre`, `apellido_1`, `apellido_2`
- `dni_cifrado` (Fernet AES-128, como NUSS/TSI)
- `email_corporativo`, `telefono_interno`
- `rol` (FK a `RolProfesional`: enfermera, auxiliar, psicóloga, TS, terapeuta ocupacional, fisio, gerocultora, monitor, etc.)
- `centros` (M2M a `Centro`, un profesional puede estar adscrito a varios)
- `centro_principal` (FK)
- `tipo_jornada` (completa / parcial / fines de semana)
- `horario_habitual` (M-V / turnos rotativos / nocturno / 24 h)
- `fecha_alta`, `fecha_baja_grupo` (nullable)
- `gestor_de_caso` (boolean) — ¿está habilitado como gestor/a de caso?
- `personas_asignadas` (M2M a `PersonaAtendida` cuando es gestor de caso, ya existe en modelo actual)
- `is_active` (bool)

### `Vacacion`
- `profesional` (FK)
- `fecha_inicio`, `fecha_fin`
- `tipo` (vacaciones / asuntos propios / formación / permiso retribuido / IT / IT-prolongada / otro)
- `estado` (solicitada / aprobada / rechazada / disfrutada)
- `motivo` (texto libre, opcional)
- `aprobada_por` (FK a User, nullable)
- `dias_naturales`, `dias_laborables` (calculados)
- `documentacion` (FK a Adjunto, ej. parte médico para IT) — RGPD art. 9
- `origen` (manual / sigper) — para discriminar cuando llegue de SIGPER

### `Turno`
- `centro` (FK)
- `fecha`
- `franja` (mañana / tarde / noche / partido / 24 h)
- `profesionales` (M2M)
- `notas`
- `creado_por`, `created_at`, `updated_at`

### `PlantillaTurno`
- `nombre`
- `centro` (FK, nullable si es plantilla del grupo)
- `definicion_json` — patrón semanal (turnos × días × roles requeridos)

---

## 4. RGPD y permisos

Aplica el mismo régimen que personas atendidas:
- **Bitácora**: cada lectura de ficha de profesional queda registrada.
- **Cifrado**: DNI, IBAN y datos sensibles (parte de IT) cifrados en reposo.
- **Tutela**: los partes de IT son **categoría especial** (art. 9 RGPD). Solo accesible a RRHH, Dirección de centro y profesional afectado.
- **Minimización**: ÁGORA NO almacena nómina, IRPF ni Seguridad Social (eso es de EQUIPO).
- **Retención**: 4 años tras la baja del profesional (Estatuto de los Trabajadores).

---

## 5. Roadmap de implementación

| Fase | Bloque | Estado |
|---|---|---|
| **Fase 4.1** (Q1 2027, junto al piloto Fuentecillas) | Profesionales: alta, listado, ficha individual, asignación a centro | A maquetar ahora |
| **Fase 4.2** | Vacaciones operativas: registro de ausencias del centro, calendario mensual | A maquetar ahora |
| **Fase 4.3** | Turnos: plantilla del centro + planificación semanal | A maquetar ahora |
| **Fase 5.1** (2027-2028) | Integración con SIGPER (cuando exista) | Pendiente |
| **Fase 5.2** (2028-2029) | Integración con EQUIPO (suite RRHH) | Pendiente |

---

## 6. Riesgo asumido

> Patrón Federico — calendario vs alcance: «mantener fecha y asumir riesgo; dejar constancia documental y paralelizar».

Riesgo identificado: **duplicación funcional con SIGPER y EQUIPO**.
Mitigación: este documento + regla de no duplicación + API de sincronización en Fase 5.

---

*Documento v1.0 · vigente desde 2026-06-05 · revisión obligatoria al cierre de Fase 0 de SIGPER y EQUIPO.*

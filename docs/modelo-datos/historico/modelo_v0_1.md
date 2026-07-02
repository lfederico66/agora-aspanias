# Modelo de datos ÁGORA — v0.1

**Estado**: borrador inicial para validación funcional por Dirección de Centros y Servicios + Operaciones/Calidad
**Fecha**: 2026-05-13
**Próxima revisión**: v1.0 antes del 15 junio 2026

> Este modelo es la **primera propuesta** que cubre los cuatro colectivos con una **ficha base extensible por perfiles**, evitando tablas paralelas por colectivo. Pendiente de validación funcional.

---

## 1. Principios de diseño

1. **Ficha base única + perfiles**: una sola tabla `PersonaAtendida` con los datos comunes, ampliada por perfiles específicos (`PerfilDI`, `PerfilMayor`, `PerfilInsercion`). Una persona puede tener varios perfiles a lo largo del tiempo (un usuario de centro de día puede pasar a CEE).
2. **Familia como sujeto**: `NucleoFamiliar` es un tipo de "Persona" alternativo, no solo un contacto de otra ficha. Permite seguimiento de programas de respiro y apoyo familiar.
3. **Centros como contexto, no como dueños**: un dato pertenece a una **persona**, no a un centro. El centro determina el ámbito de acceso (RBAC), no la propiedad del dato.
4. **Cotitularidad RGPD modelada**: cada persona atendida se asocia a uno de los dos corresponsables (Fundación Aspanias Burgos o Aspaniasmerc 2016 S.L.U.) según la naturaleza jurídica del servicio. Las anotaciones registran al corresponsable que las realiza.
5. **Ley 8/2021 first-class**: `MedidaDeApoyo` es entidad obligatoria, no campo opcional. Sin medida también es un valor explícito.
6. **Histórico longitudinal**: todas las entidades clave (perfiles, valoraciones, planes, medicación) son temporales — con `inicio_at` y `fin_at`, no se sobrescriben.
7. **Bitácora separada del modelo de negocio**: tabla `RegistroAcceso` independiente, no triggers en cada modelo.

---

## 2. Entidades núcleo

### 2.1 `PersonaAtendida` (ficha única)

| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID | PK |
| `codigo_interno` | string | Código humano-legible, único, p.ej. "AB-2026-00045" |
| `nombre`, `apellido_1`, `apellido_2` | string | |
| `dni_nie` | string nullable | Cifrado a nivel aplicación. Único cuando informado |
| `fecha_nacimiento` | date | |
| `sexo` | enum | M / F / X / no_informa |
| `nacionalidad` | string | ISO 3166 |
| `foto` | FK Documento | Con consentimiento específico |
| `direccion_actual` | embedded | Calle, CP, municipio, provincia |
| `corresponsable_principal` | enum | `fundacion_aspanias_burgos` / `aspaniasmerc` — gobierno RGPD |
| `centro_referencia` | FK Centro | Centro del que depende administrativamente |
| `fecha_alta` | date | Primera entrada en cualquier servicio del grupo |
| `fecha_baja` | date nullable | Cierre de la relación con el grupo |
| `motivo_baja` | enum nullable | |
| `notas_relevantes` | text | Información transversal corta, no historia social |
| `creado_at`, `actualizado_at` | timestamp | Auditoría |

### 2.2 `PerfilDI` (discapacidad intelectual)

| Campo | Tipo | Notas |
|---|---|---|
| `persona` | FK PersonaAtendida | |
| `tipo_discapacidad` | enum | DI leve / DI moderada / DI severa / DI profunda / no_valorada |
| `grado_discapacidad_pct` | int nullable | Grado oficial reconocido |
| `fecha_reconocimiento` | date nullable | |
| `servicios_activos` | M2M ServicioContratado | Residencia, centro día, vivienda, ocupacional |
| `inicio_at`, `fin_at` | date | Período de vigencia del perfil |

### 2.3 `PerfilMayor` (mayores dependientes)

| Campo | Tipo | Notas |
|---|---|---|
| `persona` | FK PersonaAtendida | |
| `grado_dependencia` | enum | I / II / III / no_valorado |
| `fecha_valoracion_bvd` | date nullable | |
| `cuidador_principal_externo` | FK PersonaContacto nullable | Si vive en domicilio |
| `servicios_activos` | M2M ServicioContratado | Residencia, SAD |
| `inicio_at`, `fin_at` | date | |

### 2.4 `PerfilInsercion` (inserción laboral)

| Campo | Tipo | Notas |
|---|---|---|
| `persona` | FK PersonaAtendida | |
| `programa` | enum | CEE / empleo_apoyo / empresa_insercion / orientacion |
| `entidad_empleadora` | FK Entidad nullable | CISA, CISA EMPLEA, externa |
| `puesto_actual` | string nullable | |
| `nivel_apoyo_requerido` | enum | bajo / medio / alto |
| `inicio_at`, `fin_at` | date | |

### 2.5 `NucleoFamiliar` (familia como sujeto)

| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID | |
| `nombre_referencia` | string | "Familia García López" |
| `persona_referencia` | FK PersonaContacto | Cuidador principal o portavoz |
| `programas_activos` | M2M ProgramaApoyo | Respiro, escuela familias, etc. |
| `personas_atendidas` | M2M PersonaAtendida | Vínculo con personas usuarias del grupo |

### 2.6 `PersonaContacto` (terceros relacionados)

Familiares, representantes legales, contactos de emergencia, profesionales externos.

| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID | |
| `nombre`, `apellido_1`, `apellido_2` | string | |
| `relacion_con_persona` | M2M con `Relacion` | "madre", "hermano", "tutor", "amistad apoyo", "MAP" |
| `telefono`, `email` | string nullable | |
| `consentimiento_comunicacion` | bool + fecha | |

### 2.7 `MedidaDeApoyo` (Ley 8/2021)

Entidad obligatoria por cada `PersonaAtendida`, incluyendo el valor "sin medida".

| Campo | Tipo | Notas |
|---|---|---|
| `persona` | FK PersonaAtendida | |
| `tipo` | enum | sin_medida / apoyo_voluntario / apoyo_judicial / apoyo_hecho |
| `fecha_resolucion` | date nullable | |
| `documento_resolucion` | FK Documento nullable | Sentencia, escritura |
| `figuras_apoyo` | M2M FiguraApoyo | Personas/instituciones que prestan apoyo |
| `ambito_apoyos` | text | Descripción del alcance: qué decisiones, en qué ámbitos |
| `ambito_capacidad_conservada` | text | Qué decisiones toma la persona por sí misma |
| `vigente` | bool | |
| `revisado_at` | date | Revisión periódica obligatoria |

---

## 3. Atención y seguimiento

### 3.1 `PlanIndividualAtencion` (PIA / AICP)

| Campo | Tipo | Notas |
|---|---|---|
| `persona` | FK PersonaAtendida | |
| `version` | int | v1, v2... |
| `objetivos` | M2M ObjetivoPIA | |
| `revisado_at` | date | Próxima revisión |
| `aprobado_por` | FK Profesional | |
| `firma_persona` | FK FirmaElectronica nullable | |
| `firma_apoyo` | FK FirmaElectronica nullable | Si aplica Ley 8/2021 |
| `inicio_at`, `fin_at` | date | |

### 3.2 `ObjetivoPIA`

| Campo | Tipo | Notas |
|---|---|---|
| `pia` | FK PlanIndividualAtencion | |
| `ambito` | enum | salud, autonomía, relaciones, ocio, formación, empleo, vivienda, espiritualidad |
| `descripcion` | text | En lenguaje de la persona cuando aplique |
| `indicador_logro` | text | Cómo se mide |
| `apoyos_necesarios` | text | |
| `responsable_seguimiento` | FK Profesional | |
| `prioridad` | enum | |
| `estado` | enum | propuesto / activo / logrado / abandonado |

### 3.3 `Intervencion` (registro cronológico)

| Campo | Tipo | Notas |
|---|---|---|
| `persona` | FK PersonaAtendida | |
| `profesional` | FK Profesional | |
| `tipo` | FK TipoIntervencion | "consulta médica", "sesión TO", "entrevista familiar"... |
| `fecha_hora` | datetime | |
| `descripcion` | text | Texto libre estructurado por plantilla |
| `documentos` | M2M Documento | |
| `vinculada_a_objetivo` | FK ObjetivoPIA nullable | |
| `confidencialidad` | enum | normal / restringida_clinica / restringida_juridica |

### 3.4 `Valoracion` (instrumentos)

| Campo | Tipo | Notas |
|---|---|---|
| `persona` | FK PersonaAtendida | |
| `instrumento` | enum | BVD / ICAP / SIS / Tinetti / Barthel / Mini-mental / ... |
| `fecha` | date | |
| `puntuacion` | JSON | Estructura según instrumento |
| `aplicado_por` | FK Profesional | |
| `documento_adjunto` | FK Documento nullable | |

---

## 4. Agenda y operativa

### 4.1 `Profesional`

| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID | Federado por SSO M365 |
| `nombre_completo` | string | |
| `rol_principal` | FK Rol | Trabajadora social, psicóloga, TO, DUE, monitor, fisio... |
| `centros_acceso` | M2M Centro | Centros a los que tiene acceso |
| `email_m365` | string | SSO |
| `activo` | bool | |

### 4.2 `Cita`

| Campo | Tipo | Notas |
|---|---|---|
| `persona` | FK PersonaAtendida | |
| `profesionales` | M2M Profesional | Multiprofesional |
| `tipo` | enum | individual / familiar / multipro / externa |
| `inicio`, `fin` | datetime | |
| `ubicacion` | string | |
| `estado` | enum | propuesta / confirmada / cancelada / realizada |
| `notas` | text | |
| `notificada_a_familia` | bool | Vía CERCA |
| `intervencion_resultante` | FK Intervencion nullable | |

### 4.3 `Centro` y `ServicioContratado`

`Centro` (Fuentecillas, Lara Río Arlanza, Salas, Villadiego, etc.) y `Servicio` (residencia, día, vivienda, ocupacional, SAD, CEE) modelados como entidades separadas. `ServicioContratado` relaciona persona + centro + servicio + período + corresponsable.

---

## 5. Documental y firmas

### 5.1 `Documento`

| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID | |
| `tipo` | enum | informe médico, consentimiento, sentencia, foto, etc. |
| `azure_blob_url` | string | URL firmada con expiración |
| `subido_por` | FK Profesional | |
| `subido_at` | datetime | |
| `personas_vinculadas` | M2M PersonaAtendida | |
| `confidencialidad` | enum | igual que Intervencion |
| `consentimiento_vigente` | bool | Para fotos/vídeos |

### 5.2 `FirmaElectronica`

| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID | |
| `documento_firmado` | FK Documento | |
| `firmante_persona` | FK PersonaAtendida nullable | |
| `firmante_contacto` | FK PersonaContacto nullable | Representante |
| `firmante_profesional` | FK Profesional nullable | |
| `tipo_firma` | enum | simple_con_evidencia / autofirma / fnmt |
| `evidencia` | JSON | IP, timestamp, OTP, hash |

---

## 6. Indicadores

### 6.1 `Indicador` (definición)

| Campo | Tipo | Notas |
|---|---|---|
| `codigo` | string | |
| `nombre` | string | |
| `descripcion` | text | |
| `unidad` | enum | porcentaje / ratio / absoluto |
| `formula` | string | Definición SQL/Python referenciable |
| `requiere_anonimizacion` | bool | True para exportes externos |

### 6.2 `MedicionIndicador`

| Campo | Tipo | Notas |
|---|---|---|
| `indicador` | FK Indicador | |
| `periodo` | date | Mes/trimestre |
| `centro` | FK Centro nullable | Null si grupo |
| `valor` | decimal | |
| `calculado_at` | datetime | |

---

## 7. Bitácora y auditoría

### 7.1 `RegistroAcceso`

| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID | |
| `profesional` | FK Profesional | |
| `persona_consultada` | FK PersonaAtendida | |
| `accion` | enum | leer / editar / exportar / firmar |
| `entidad` | string | Modelo afectado |
| `ip` | string | |
| `user_agent` | string | |
| `motivo` | string nullable | Cuando se requiere justificación |
| `timestamp` | datetime | |

Tabla **append-only**, retención mínima 24 meses, copia separada en almacenamiento WORM si es posible.

---

## 8. Lo que **no** modela v0.1

- Prescripción farmacológica detallada (se valora integración ResiPlus en Fase 2).
- Facturación detallada (M3).
- Comunicación con familia (vive en CERCA — ÁGORA solo dispara `notificacion_a_familia` en `Cita`).
- Datos de RRHH del profesional (vive en SIGPER + A3).

---

## 9. Validación pendiente

Antes de v1.0 (15 junio 2026), debe ser validado por:

- **Dirección de Centros y Servicios**: completitud de perfiles y servicios, propiedad funcional.
- **Operaciones/Calidad**: encaje con AICP, Norma Libera-Care, IAPA, conciertos.
- **DPO / asesoría jurídica**: minimización, Ley 8/2021, encaje con EIPD.
- **RRHH**: roles profesionales y ámbitos de acceso por centro.

---

*Modelo v0.1 — punto de partida para la conversación funcional. Cambios mayores esperables tras revisión de Operaciones.*

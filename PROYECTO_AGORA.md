# PROYECTO ÁGORA

**Atención y Gestión Operativa para Residentes y Atendidos — Grupo Social Aspanias**

CRM sociosanitario para el seguimiento integral de las personas atendidas por el grupo: usuarios con discapacidad intelectual, mayores dependientes, personas en itinerarios de inserción laboral y sus familias/entorno.

---

## 1. Datos generales

| Campo | Valor |
|---|---|
| Nombre del proyecto | ÁGORA — Atención y Gestión Operativa para Residentes y Atendidos |
| Sponsor | Federico Martínez — Gerencia Grupo Social Aspanias |
| Fecha cierre Fase 0 | 2026-05-13 |
| Responsable del tratamiento RGPD | **Cotitularidad** Fundación Aspanias Burgos + Aspaniasmerc 2016 S.L.U. (requiere acuerdo de corresponsabilidad art. 26 RGPD) |
| Repositorio local | `C:\Users\fmartinez\OneDrive - Aspanias\Escritorio\PROYECTOS_TRABAJO\agora-aspanias\` |
| Dominio previsto | `agora.aspaniasburgos.com` |
| Sistema de referencia | Odoo CRM (preaspanias.integrodoo.com) — **a sustituir** completamente por ÁGORA. Plan de migración obligatorio. |

---

## 2. Por qué ÁGORA

Aspanias dispone hoy de un Odoo (`preaspanias.integrodoo.com`) que cubre parcialmente la relación con personas atendidas, pero:

- No está modelado para el ciclo de atención sociosanitaria (PIA, AICP, valoraciones de dependencia, planes de apoyos).
- No integra los cuatro colectivos del grupo bajo una ficha única (DI, mayores, inserción laboral, familias).
- No conecta con la gobernanza de datos del grupo (SSO M365, política RGPD interna, retención).
- Mantenerlo implica dependencia de partner Odoo y un modelo de datos genérico que no encaja con la operativa real de los centros.

ÁGORA es un **CRM propio sociosanitario**, alineado con el stack tecnológico ya validado en SIGPER y CERCA (Django + HTMX), reutilizable como núcleo de información de personas para el grupo.

---

## 3. Alcance v1 (validado Fase 0)

### Colectivos cubiertos

Los **cuatro colectivos** desde el inicio, en módulos diferenciados que comparten ficha única:

1. **Discapacidad intelectual** — usuarios de residencia, centro de día, vivienda, ocupacional (Fundación Aspanias Burgos).
2. **Mayores dependientes** — usuarios de los centros sociosanitarios rurales (Salas de los Infantes, Villadiego — Aspaniasmerc 2016 S.L.U.).
3. **Inserción laboral** — usuarios en itinerarios CEE (Fundación CISA) y empleo con apoyo (CISA EMPLEA).
4. **Familias y entorno** — cuidadores principales y núcleo familiar como sujeto del seguimiento, no solo como contacto.

> **Implicación de modelar los cuatro a la vez**: el modelo de datos común debe diseñarse cuidadosamente para que la ficha sea reutilizable sin acoplar lógica de un colectivo a otro. Riesgo principal de Fase 1: sobreingeniería del modelo. Mitigación: extender ficha base con perfiles por colectivo, no con tablas paralelas.

### Funcionalidades MVP

| Módulo | Descripción | Prioridad |
|---|---|---|
| **Ficha única de persona atendida** | Datos identificativos, contactos, núcleo familiar, representante legal (Ley 8/2021), documentos, historial cronológico de intervenciones de cualquier profesional. | M1 |
| **Plan Individual de Atención (PIA)** | Modelo AICP: objetivos personales, indicadores de logro, revisiones periódicas, firma del usuario/familia/representante. Integra Norma Libera-Care. | M1 |
| **Agenda multiprofesional** | Calendario compartido entre trabajadora social, psicóloga, terapeuta ocupacional, DUE, monitor, fisioterapeuta. Notificaciones a familia. | M1 |
| **Indicadores y memoria automatizada** | Cuadro de mando con ocupación, ratios, indicadores de calidad asistencial. Exportación para memoria anual, IAPA y justificación de conciertos. | M1 |
| Valoración y dependencia | Registro de BVD, ICAP, otros instrumentos. Histórico longitudinal. | M2 |
| Gestión documental con firma electrónica | Consentimientos informados, autorizaciones, integrado con CERCA para la firma desde familia. | M2 |
| Facturación de concierto / privados | Generación de cobros y conciliación. Solo si financiero lo confirma viable vs A3. | M3 |

---

## 4. Decisiones de Fase 0

### 4.1 Tecnología (validada con Federico 2026-05-13)

- **Backend + frontend**: Django 5 + HTMX + Alpine.js + TailwindCSS (mismo stack que SIGPER y CERCA).
- **Base de datos**: PostgreSQL 16 **desde v1** (no SQLite). Justificación: volumen previsto >300 personas con histórico largo + necesidad de búsqueda full-text + integraciones desde día 1.
- **Autenticación profesionales**: SSO Microsoft 365 (Entra ID) vía `django-allauth` o `django-microsoft-auth` con MSAL.
- **Autenticación familias/usuarios**: vía CERCA (no autenticación propia, federación con la plataforma de comunicación de familias). Pendiente confirmar acoplamiento técnico.
- **Móvil**: PWA instalable sobre la misma app (no nativa).
- **Almacenamiento documental**: Azure Blob Storage (zona UE) con URLs firmadas — alineado con CERCA.

### 4.2 Infraestructura

- **Servidor**: mismo servidor físico de Aspanias Burgos que SIECP/SIGPER/CERCA. Windows Server + Hyper-V.
- **VM**: Ubuntu 24.04 LTS con Docker Compose, separada de SIGPER y CERCA.
- **Reverse proxy + SSL**: Traefik o Nginx + Let's Encrypt.
- **Backups**: cifrados, retención 90 días en línea + 7 años offline (por exigencia de historia social).

### 4.3 RGPD — núcleo del proyecto

ÁGORA trata **datos de categoría especial del art. 9 RGPD** de forma masiva (salud, discapacidad, datos de menores, opiniones de profesionales sobre el usuario) **y** **datos sujetos a medidas de apoyo a la capacidad jurídica (Ley 8/2021)**.

Requisitos no negociables ya en Fase 0:

- **EIPD (Evaluación de Impacto en Protección de Datos)** obligatoria antes del piloto.
- **RAT (Registro de Actividades de Tratamiento)** específico: "Seguimiento de personas atendidas — ÁGORA".
- **Base jurídica**: misión de interés público + ejecución de contrato/concierto + consentimiento para tratamientos accesorios (multimedia, comunicaciones a terceros).
- **Cifrado en reposo** de la BD (PostgreSQL + cifrado de disco).
- **Cifrado en tránsito** (HTTPS obligatorio, HSTS).
- **Bitácora de accesos** persistente con retención mínima de 24 meses: quién accede a qué ficha y cuándo.
- **Control de accesos por rol y por centro** (un profesional de Salas no ve fichas de Burgos salvo autorización explícita).
- **Minimización**: solo se registra la información necesaria para la atención. No diagnósticos completos en texto libre; usar codificación CIE-10 o equivalente cuando proceda.
- **Política de conservación**:
  - Datos de salud: lo mínimo imprescindible.
  - Historia social: 7 años tras baja (consultar normativa CyL específica).
  - Bitácora de accesos: 24 meses.
  - Logs técnicos: 12 meses.
- **Derechos ARSULIPO** (acceso, rectificación, supresión, oposición, limitación, portabilidad): formulario en la app + flujo interno con DPO.

### 4.4 Ley 8/2021 — capacidad jurídica

Modelado obligatorio en la ficha de persona atendida:

- **Tipo de medida de apoyo**: voluntaria, judicial, de hecho, sin medida.
- **Representante legal o figura de apoyo**: datos completos, sentencia/notaría que la respalda, alcance.
- **Ámbitos en los que la persona conserva capacidad** (no se asume incapacidad general).
- **Consentimiento informado adaptado**: en lectura fácil cuando proceda, registrado con versión y fecha. Distinguir consentimiento de la persona, consentimiento del representante y consentimiento informado para tratamiento sanitario (Ley 41/2002).

### 4.5 Gobernanza del proyecto

- **Sponsor**: Gerencia — **Federico Martínez Miguel**.
- **Propietario funcional**: **Dirección de Centros y Servicios** del Grupo Social Aspanias — **Federico Martínez Miguel** (doble rol confirmado 2026-05-13).
- **Comité de seguimiento**: Gerencia/Dirección de Centros y Servicios + Operaciones/Calidad + Administración + DPO + RRHH (representación profesional).
- **Validación clínica/social**: equipos asistenciales de cada centro piloto antes del despliegue.
- **Aprobación final v1**: Patronato Fundación Aspanias Burgos + Consejo Aspaniasmerc (necesario ambos por cotitularidad RGPD).

### 4.5.1 Interlocutores externos y equipos asignados (confirmado 2026-05-13)

| Función | Asignación |
|---|---|
| Asesoría jurídica RGPD (EIPD + acuerdo cotitularidad) | **Lex Digital** (especialista RGPD sociosanitario) |
| DPO | **Pendiente de designación** — Lex Digital como candidato a DPO externo interino |
| Desarrollo funcional | **Innovación Aspanias** (equipo interno) |
| Desarrollo técnico, infraestructura y despliegue | **Sistemas Aspanias** (equipo interno) |
| Senior externo de apoyo | **No previsto** — riesgo asumido en R7 |

### 4.5.2 Aprobación de órganos de gobierno

- **Convocatoria**: 10 de junio de 2026 — Patronato extraordinario Fundación Aspanias Burgos + Consejo de Administración Aspaniasmerc 2016 S.L.U.
- **Documentos a elevar**: acta Fase 0, EIPD inicial, acuerdo de cotitularidad art. 26 RGPD, presupuesto Fase 1-2.
- **Hito previo no negociable**: borradores cerrados por Lex Digital antes del 5 junio 2026 para revisión interna.

### 4.6 Centro piloto y calendario

- **Centro piloto**: Centro Fuentecillas — confirmado.
- **Hito objetivo**: **piloto Q3 2026** (validado por Gerencia 2026-05-13).
- **Alcance del piloto Q3 2026**: MVP completo (ficha + PIA + agenda + indicadores) sobre los cuatro colectivos, con sustitución del Odoo y cotitularidad RGPD operativa.
- **Decisión de Gerencia (2026-05-13)**: ante la tensión calendario/alcance, **se mantiene fecha y alcance asumiendo riesgo de ejecución**. Se descarta el recorte de MVP propuesto.

#### Riesgos formalmente asumidos por Gerencia

| Riesgo | Probabilidad | Impacto | Mitigación obligatoria |
|---|---|---|---|
| Incumplimiento de fecha Q3 2026 por bloqueante legal (acuerdo cotitularidad / EIPD) | Alta | Alto | Iniciar redacción de borradores en paralelo a Fase 1 técnica, no en serie. Reuniones DPO + jurídico semanales desde semana 1. |
| Calidad insuficiente del MVP por compresión de plazos | Alta | Alto | Equipo de desarrollo dedicado a tiempo completo. Validación funcional semanal por Dirección de Centros y Servicios. No introducir funcionalidades fuera del MVP M1 bajo ningún concepto. |
| Migración de datos desde Odoo no completada a tiempo | Media | Alto | Carga inicial limitada a maestros (personas atendidas + datos identificativos), no histórico de intervenciones. Histórico se importa post-piloto o se referencia desde Odoo en consulta read-only durante 6 meses. |
| Resistencia de equipos asistenciales por curva de aprendizaje insuficiente | Media | Alto | Pre-piloto técnico mínimo en julio 2026 con 3-4 profesionales de Fuentecillas. Formación obligatoria 2 semanas antes del go-live. |
| Falta de aprobación de Patronato + Consejo Aspaniasmerc a tiempo para cotitularidad | Media | Crítico | Llevar el acuerdo de cotitularidad al primer Patronato y Consejo disponibles (junio 2026 como máximo). |
| Salida de calidad insuficiente comprometiendo la confianza institucional | Media | Crítico | Criterios de "go/no-go" formales antes del piloto: EIPD firmada, acuerdo cotitularidad firmado, MVP funcional con 5 fichas reales validadas, bitácora de accesos operativa. Sin estos cuatro hitos, no se arranca piloto aunque haya fecha. |
| **R7** — Capacidad de ejecución solo con equipo interno (sin senior externo) | Media | Alto | Refuerzo de revisiones de código entre Innovación Aspanias y Sistemas Aspanias. Pair programming en módulos críticos. Auditoría técnica externa de un único punto (revisión arquitectura + seguridad) antes del piloto. Posibilidad de incorporar refuerzo externo puntual si en revisión 15 julio se detecta retraso. |
| **R8** — DPO sin designar a 4 semanas del Patronato | Alta | Crítico | Solicitar a Lex Digital asunción de DPO externo interino antes del 20 mayo 2026. Iniciar selección de DPO definitivo en paralelo. Sin DPO firmando, no se eleva la EIPD al Patronato. |

#### Plan de ejecución paralela (no secuencial)

Para hacer viable Q3 2026, **todos los bloques arrancan simultáneamente** desde la semana 20 de 2026 (semana del 11 de mayo, en curso):

- **Bloque legal/RGPD**: borrador EIPD + borrador acuerdo cotitularidad + aprobación órganos de gobierno. Hito: firmas antes del 30 junio 2026.
- **Bloque modelo de datos**: modelo v0.1 → validación con Dirección de Centros y Servicios → v1.0 antes del 15 junio 2026.
- **Bloque técnico**: scaffolding Django + SSO M365 + RBAC + bitácora desde mayo. Desarrollo MVP entre junio y agosto.
- **Bloque organizativo**: identificación de equipo piloto Fuentecillas, plan de formación, comunicación interna.
- **Bloque migración**: análisis del modelo de datos Odoo y mapeo a ÁGORA desde junio. Ejecución de carga maestros en agosto.

**Criterio de go/no-go al piloto** (1 septiembre 2026 como tarde): si alguno de los cuatro hitos críticos (EIPD, acuerdo cotitularidad firmado, MVP funcional, bitácora operativa) no está cerrado, **se aplaza el piloto** sin reabrir esta decisión.

### 4.7 Cotitularidad RGPD (art. 26 RGPD) — implicaciones

Decisión validada 2026-05-13: cotitularidad real entre Fundación Aspanias Burgos y Aspaniasmerc 2016 S.L.U.

Obliga a producir antes del piloto:
- **Acuerdo de corresponsables del tratamiento** (art. 26 RGPD) firmado por ambas entidades, con:
  - Reparto de obligaciones (quién atiende derechos ARSULIPO, quién notifica brechas, quién mantiene RAT).
  - Punto de contacto único para personas interesadas.
  - Información a las personas atendidas sobre la cotitularidad.
- **Aprobación por Patronato** (Fundación Aspanias Burgos) **y Consejo de Administración** (Aspaniasmerc).
- **RAT con dos responsables** declarados ante la AEPD si es necesario.
- **DPO único o coordinación** entre DPOs si los hay separados.

---

## 5. Lo que ÁGORA **no** es (anti-alcance)

Para evitar deriva, en v1 ÁGORA **no cubre**:

- Gestión de personal de Aspanias (eso es SIGPER y A3).
- Comunicación con familias (eso es CERCA — ÁGORA se conecta a CERCA).
- Evaluación de competencias profesionales (eso es SIECP).
- Facturación general del grupo (A3).
- Historia clínica completa con prescripción farmacológica (se valorará integración con ResiPlus en Fase 2, no sustitución).
- Gestión de listas de espera y captación comercial — no se modela como CRM comercial, sino como CRM asistencial.

---

## 6. Riesgos identificados en Fase 0

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Sobreingeniería del modelo de datos por cubrir 4 colectivos | Alto | Diseñar ficha base + perfiles, no tablas paralelas. Revisar con operaciones en Fase 1. |
| Coexistencia con Odoo durante migración | Medio | Definir cuanto antes plan de retirada del Odoo o ámbito de cohabitación. |
| RGPD y Ley 8/2021 mal modeladas | Alto | DPO involucrado desde Fase 1. EIPD antes de cualquier carga real. |
| Resistencia de profesionales (otro sistema más) | Medio | Pre-piloto con equipo asistencial. UX por encima de exhaustividad documental. |
| Acoplamiento técnico con CERCA antes de que CERCA esté maduro | Medio | Definir API de federación de identidades como contrato versionado. |
| Datos sensibles en repositorio durante desarrollo | Crítico | Solo datos sintéticos. Política `.gitignore` estricta. Fixtures sin nombres reales. |

---

## 7. Próximos pasos (Fase 1)

1. **Validación de Fase 0** con Federico (este documento) — pendiente.
2. **EIPD inicial** con DPO antes de empezar a modelar — invocar `aspanias-administracion` + `asesor-juridico-tercer-sector`.
3. **Modelo de datos v0.1** — invocar `aspanias-operaciones` para PIA/AICP y `aspanias-rrhh` para roles profesionales.
4. **Scaffolding Django** — repositorio inicial con SSO M365 funcional sobre datos sintéticos.
5. **Definición de indicadores v1** — invocar `aspanias-okr` para alinear con cuadro de mando del grupo.
6. **Plan de migración o cohabitación con Odoo** — decisión gerencial antes de Fase 2.

---

## 8. Documentos relacionados

- `CLAUDE.md` — convenciones del repositorio.
- `docs/fase0/` — actas y materiales de Fase 0.
- `docs/modelo-datos/` — diagramas ER y diccionario de entidades (a producir en Fase 1).
- `docs/rgpd/` — EIPD, RAT, política de conservación (a producir en Fase 1).

---

*Documento maestro v0.1 — generado 2026-05-13. Pendiente de validación formal por Gerencia.*

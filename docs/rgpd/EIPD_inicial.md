# Evaluación de Impacto en Protección de Datos (EIPD) — ÁGORA

**Versión**: 0.2 (cierre Fase 1 — pendiente revisión Lex Digital)
**Fecha**: 2026-05-19 (v0.2) · 2026-05-13 (v0.1 inicial)

## Historial de cambios

| Versión | Fecha | Cambios | Origen |
|---|---|---|---|
| 0.1 | 2026-05-13 | Borrador técnico inicial sobre 15 modelos | Fase 0 |
| 0.2 | 2026-05-19 | Añade modelos clínicos (v0.11) y de alojamiento (v0.12). Riesgos nuevos R11–R13. | Cierre Fase 1 |
**Asesoría externa designada**: **Lex Digital** (encargada de la versión final y revisión jurídica)
**DPO firmante**: pendiente de designación (Lex Digital como candidato a DPO externo interino)
**Estado**: pendiente de revisión por Lex Digital y validación por corresponsables
**Base normativa**: art. 35 RGPD; LOPDGDD (LO 3/2018); Guía AEPD sobre EIPD; Ley 8/2021
**Hito de entrega**: borrador cerrado por Lex Digital antes del **5 junio 2026** para elevación al Patronato Fundación Aspanias Burgos y Consejo Aspaniasmerc el **10 junio 2026**.

> Este documento es un **borrador técnico de partida** para la EIPD. Será completado, ajustado y aprobado por Lex Digital como asesoría jurídica RGPD del proyecto. No sustituye a la EIPD formal firmada por el DPO.

---

## 1. Datos del tratamiento

| Campo | Valor |
|---|---|
| Denominación | "Seguimiento de personas atendidas — ÁGORA" |
| Responsables del tratamiento | **Cotitularidad** (art. 26 RGPD): Fundación Aspanias Burgos + Aspaniasmerc 2016 S.L.U. |
| Encargado del tratamiento | El propio Grupo Social Aspanias para el desarrollo y mantenimiento. Encargos a terceros (Azure, proveedor email/SMS) con contrato 28 RGPD. |
| DPO | Pendiente de designación. **Lex Digital** propuesto como DPO externo interino mientras no haya DPO definitivo. |
| Naturaleza | Sistema de información sociosanitario interno para la atención y seguimiento de personas usuarias |
| Punto de contacto único | Por designar |

---

## 2. Necesidad de EIPD

**Sí, obligatoria**, por concurrir múltiples criterios del art. 35.3 RGPD y lista AEPD:

- Tratamiento a **gran escala** de datos de categoría especial (art. 9 RGPD): salud, discapacidad.
- Tratamiento de datos de **personas vulnerables**: personas con discapacidad intelectual, mayores dependientes, personas con medidas de apoyo a la capacidad jurídica (Ley 8/2021).
- **Observación o seguimiento sistemático** de las personas atendidas.
- **Evaluación o puntuación** de personas (valoraciones funcionales, BVD, ICAP, planes individualizados).
- **Tratamiento de datos de menores** previsibles (familias con menores de edad).
- **Combinación de fuentes** de datos (centro + familia + administración + entidades del grupo).
- **Uso de tecnologías nuevas o innovadoras** dentro de la organización (sustitución de Odoo).

---

## 3. Categorías de personas e información

### 3.1 Interesados

- Personas usuarias del grupo (cuatro colectivos).
- Familiares, tutores, representantes legales y figuras de apoyo.
- Profesionales de los centros (en su rol de autores de las anotaciones).
- Terceros: profesionales sanitarios externos, técnicos de la administración.

### 3.2 Categorías de datos tratados

| Categoría | Detalle | Categoría especial |
|---|---|---|
| Identificativos | Nombre, DNI/NIE, fecha nacimiento, sexo, foto, domicilio, contacto | No |
| Familiares y entorno | Núcleo familiar, cuidadores, representantes legales | No |
| Académicos y laborales | Itinerarios formativos, situación laboral (relevante en inserción) | No |
| Económicos | Tarifa, situación de copago, datos para concierto | No |
| Salud — base | Grado de discapacidad, dependencia, grupo sanguíneo, contacto médico | **Sí — art. 9** |
| Salud — clínicos (v0.11) | Alergias, enfermedades crónicas, problemas de salud en curso | **Sí — art. 9** |
| Salud — antropometría (v0.11) | Peso, talla, IMC, TA, pulso, temperatura, saturación O2, glucemia (histórico) | **Sí — art. 9** |
| Salud — vacunación (v0.11) | Pauta de vacunas administradas, fecha, lote | **Sí — art. 9** |
| Salud — cuidados (v0.11) | Plan de cuidados de enfermería estructurado en 10 dimensiones | **Sí — art. 9** |
| Medicación (v0.11) | Catálogo + pautas activas e históricas con dosificación D-C-N | **Sí — art. 9** |
| Documentación administrativa sanitaria | NUSS, TSI, fecha caducidad TSI, centro de salud | **Sí — art. 9** (cifrado obligatorio) |
| Alojamiento físico (v0.12) | Módulo, habitación, cama actual + histórico de ocupaciones | **No es art. 9** pero **sensible**: revela vínculos íntimos (compañeros de habitación, hospitalizaciones) |
| Origen racial/étnico | Solo si imprescindible para acción específica (no por defecto) | **Sí — art. 9** |
| Datos sobre capacidad jurídica | Medidas de apoyo, alcance, sentencia/notaría, persona curadora | Sensibles — Ley 8/2021 |
| Familiares y entorno (v0.11) | Familiares vinculados con teléfonos, dirección, parentesco, flag notificable CERCA | No (datos identificativos de terceros) |
| Datos de profesionales | Roles, accesos, anotaciones autoradas | No |

---

## 4. Finalidades y base jurídica

| Finalidad | Base jurídica (art. 6 RGPD) | Habilitación art. 9 |
|---|---|---|
| Atención sociosanitaria y registro de intervenciones | Misión interés público + ejecución contrato/concierto | art. 9.2.h (asistencia social y sanitaria) y art. 9.2.b (prestación social) |
| Plan Individual de Atención (AICP) | Misión interés público | art. 9.2.h |
| Agenda multiprofesional | Misión interés público | art. 9.2.h |
| Indicadores y memoria automatizada | Obligación legal (justificación conciertos, IAPA) e interés legítimo | Pseudonimización/anonimización obligatoria |
| Comunicación con familia (via CERCA) | Consentimiento o ejecución de contrato | art. 9.2.h |
| Investigación o estadísticas | Interés público | art. 9.2.j + Disp. Adic. 17ª LOPDGDD |

**No se trata por consentimiento** para finalidades asistenciales — esto evita que la retirada del consentimiento bloquee la atención. El consentimiento se reserva a tratamientos accesorios (multimedia, comunicaciones).

---

## 5. Análisis de necesidad y proporcionalidad

- **Necesidad**: la finalidad asistencial requiere registrar el historial sociosanitario para garantizar la continuidad de la atención, la coordinación entre profesionales y el cumplimiento de los conciertos y normativa autonómica.
- **Proporcionalidad**: cada campo del modelo debe estar justificado por una finalidad. Eliminar campos "por si acaso". Los datos sensibles (medicación, episodios) se limitan al personal asistencial implicado, no a toda la organización.
- **Minimización**:
  - No diagnósticos en texto libre — codificación CIE-10 o equivalente cuando proceda.
  - Datos de salud limitados a lo imprescindible para la atención.
  - Documentos sanitarios externos solo si necesarios.

---

## 6. Análisis de riesgos para los derechos y libertades

| # | Riesgo | Probabilidad | Gravedad | Riesgo residual con medidas |
|---|---|---|---|---|
| 1 | Acceso indebido por personal sin necesidad funcional | Media | Alta | Bajo con RBAC + bitácora |
| 2 | Tratamiento más allá del ámbito de capacidad jurídica de la persona | Media | Alta | Bajo con modelado Ley 8/2021 |
| 3 | Fuga de documentos sanitarios | Baja | Alta | Bajo con cifrado + URLs firmadas |
| 4 | Reidentificación de personas en informes y memoria | Media | Alta | Bajo con anonimización agregada |
| 5 | Acceso por terceros vía vulnerabilidad técnica (web) | Baja | Crítica | Medio — requiere pentest pre-piloto |
| 6 | Pérdida de control con encargado externo (Azure) | Baja | Alta | Bajo con contrato 28 RGPD + zona UE |
| 7 | Brecha y notificación tardía | Baja | Alta | Bajo con protocolo brechas <72h |
| 8 | Ejercicio de derechos ARSULIPO mal canalizado (cotitularidad) | Media | Media | Bajo con punto contacto único |
| 9 | Tratamiento de menores sin doble consentimiento | Media | Alta | Bajo con flujo doble consentimiento |
| 10 | Conservación más allá del plazo (datos en backups eternos) | Media | Media | Bajo con política de retención técnica |
| 11 | Inferencia de vínculos íntimos a partir de compañeros de habitación | Media | Media | Bajo con permisos por centro + bitácora reforzada en mapa de ocupación |
| 12 | Error en pauta de medicación que provoque daño (alergia no consultada) | Baja | **Crítica** | Bajo con alerta visible siempre + bloqueo si alergia documentada + bitácora médica |
| 13 | NUSS/TSI extraídos en exportación a Excel | Media | Alta | Bajo con cifrado a nivel campo + bloqueo en exportes a quien no es admin |

---

## 7. Medidas técnicas y organizativas

### 7.1 Técnicas

- **Cifrado en tránsito** (HTTPS, HSTS obligatorio).
- **Cifrado en reposo**: BD PostgreSQL con cifrado de disco; documentos en Azure Blob con cifrado a nivel servicio.
- **Control de acceso**: SSO M365 con MFA obligatorio para profesionales. RBAC por rol y por centro.
- **Bitácora de accesos**: registro persistente de cada lectura de ficha, con usuario, IP, timestamp y motivo cuando aplique. Retención mínima 24 meses.
- **Segregación**: la BD de ÁGORA no comparte tablas con SIGPER ni con CERCA — solo federa identidades.
- **Backups cifrados** con prueba de restauración trimestral.
- **Pentest** previo al piloto y revisión anual.
- **Pseudonimización** en exportaciones de indicadores.
- **URLs firmadas con expiración** para acceso a documentos en Azure Blob.

### 7.2 Organizativas

- Acuerdo de cotitularidad art. 26 RGPD firmado y publicado.
- RAT actualizado y accesible.
- Cláusulas informativas en lectura fácil en la primera entrada de cualquier persona atendida.
- Política de conservación documentada y aplicada automáticamente.
- Procedimiento de brechas con plazo <72h.
- Formación obligatoria del personal con acceso al sistema.
- Procedimiento de derechos ARSULIPO con punto único de contacto.
- Revisión anual de la EIPD.

---

## 8. Capacidad jurídica (Ley 8/2021)

Aspecto crítico y diferencial de ÁGORA frente a un CRM generalista:

- La ficha de la persona atendida registra:
  - Tipo de medida de apoyo (voluntaria, judicial, de hecho, sin medida).
  - Representante legal o figura de apoyo, con datos completos y referencia a sentencia/notaría.
  - **Alcance** de la medida — ámbitos en los que se necesita apoyo y ámbitos en los que la persona conserva capacidad. Esto rige los permisos de visualización y firma en la app.
  - Consentimiento informado adaptado, registrado con versión y fecha.
- **Por defecto se presume capacidad** — no se asume incapacidad general.
- Los **derechos ARSULIPO** los ejerce la persona, con apoyo si así está establecido. No los ejerce automáticamente el representante.

---

## 9. Conclusión preliminar

Con las medidas técnicas y organizativas previstas, los riesgos residuales se mantienen en nivel bajo o medio (R5 hasta pentest). El tratamiento es **proporcionado** y **lícito**, y puede arrancarse el piloto siempre que se cumplan los criterios go/no-go acordados:

1. EIPD finalizada y firmada por DPO.
2. Acuerdo cotitularidad firmado y aprobado por ambos órganos de gobierno.
3. MVP funcional verificado con 5 fichas reales.
4. Bitácora operativa.
5. Pentest sin hallazgos críticos abiertos.

---

## 10. Documentos a producir como anexo

- Cláusula informativa en lectura fácil y en versión estándar.
- Procedimiento de derechos ARSULIPO (cotitularidad).
- Procedimiento de brechas.
- Política de conservación con plazos por categoría de dato.
- Contratos 28 RGPD con Azure, Microsoft 365 (M365 Business), proveedor SMS.
- Acuerdo art. 26 RGPD (ver `acuerdo_cotitularidad_art26.md`).

---

*Borrador v0.1 — pendiente de revisión por DPO. Documento de partida para la conversación con jurídico, no documento final.*

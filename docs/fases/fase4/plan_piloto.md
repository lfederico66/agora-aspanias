# Plan detallado del piloto Fuentecillas — Fase 4

**Centro**: Residencia Fuentecillas (62 personas atendidas)
**Ventana objetivo**: enero – marzo 2027 (Q1)
**Sponsor**: Federico Martínez — Gerencia
**Coordinación in situ**: Lucía Martínez (TO · Coord. Fuentecillas)
**Versión**: 0.1 (borrador post-pre-piloto)

> Este plan **solo se activa si Fase 3 (pre-piloto) cierra con GO** en el
> informe del 23 de octubre de 2026. Si el resultado fue *GO con condiciones*,
> estas se incorporan al checklist de arranque del piloto.

---

## 1. Diferencia entre pre-piloto y piloto

| Aspecto | Pre-piloto (Fase 3) | Piloto (Fase 4) |
|---|---|---|
| Duración | 6 semanas | 12 semanas (1 trimestre) |
| Personas atendidas | 3 voluntarias | **Las 62 de Fuentecillas** |
| Profesionales | Equipo voluntario (8) | Todo el equipo de Fuentecillas (≈ 18) |
| Doble carga | Sí (Excel + ÁGORA) | **NO** — ÁGORA es la fuente única |
| Excel del grupo | Sigue siendo la fuente real | Pasa a solo lectura · histórico |
| Decisiones operativas | Solo del equipo | Toda la gestión del centro |
| Reporte a Patronato | Informe único al cierre | Reporte trimestral oficial |

En el piloto **se abandona el Excel**. Es el cambio cualitativo.

---

## 2. Condiciones que deben cumplirse antes del arranque

Checklist obligatorio. **No se arranca el piloto si alguno falla**.

| Condición | Responsable | Estado |
|---|---|---|
| Informe de pre-piloto cerrado con GO | Federico | ☐ |
| 8/8 criterios go/no-go cumplidos en el pre-piloto | Federico + Lex Digital | ☐ |
| Lex Digital firma la EIPD definitiva | Lex Digital | ☐ |
| Acuerdo art. 26 RGPD firmado por ambos órganos | Patronato + Consejo | ☐ |
| Aplicación registrada en Entra ID con MFA obligatorio | Sistemas Aspanias | ☐ |
| VM Hyper-V en producción con backups verificados | Sistemas Aspanias | ☐ |
| Migración masiva validada en seco con los datos de Fuentecillas | Innovación Aspanias | ☐ |
| Formación a las 10 personas del equipo que no participaron en pre-piloto | Federico + Lucía | ☐ |
| Comunicación a las 62 personas y a sus familias completada | Lucía + equipo | ☐ |
| Plan de contingencia documentado y comunicado | Federico | ☐ |
| Acta del Patronato autorizando el arranque del piloto | Patronato | ☐ |

---

## 3. Calendario · 12 semanas

### Fase A · Preparación (4 semanas previas · diciembre 2026)

| Sem | Actividad | Quién |
|---|---|---|
| -4 | Migración masiva del Excel "Registro PV" a ÁGORA en entorno staging | Innovación + Sistemas |
| -3 | Verificación manual de 62 fichas migradas (muestreo) | Lucía + María Ruiz |
| -3 | Sesiones de formación (4 sesiones × 2h) para el equipo completo | Federico + Lucía |
| -2 | Comunicación a las 62 familias por carta institucional | Federico |
| -2 | Recogida de consentimientos informados (los que no se obtuvieron en pre-piloto) | Equipo |
| -1 | Auditoría final de datos · simulacro de incidente | Federico + Lex Digital |
| -1 | Acta de arranque firmada por Federico + Lucía + Sistemas Aspanias | Todos |

### Fase B · Piloto en producción (12 semanas · ene-mar 2027)

| Sem | Hito | Métrica clave |
|---|---|---|
| 1 | **Día 1 (lun. 11 ene 2027)**: ÁGORA es la fuente única. Excel pasa a solo lectura | Acceso de los 18 profesionales OK |
| 2 | Primera reunión de seguimiento Federico ↔ Lucía | Cero incidencias críticas |
| 3 | Primera generación de KPIs desde ÁGORA (sustituye Excel "Datos Grupo") | Cifras coincidentes con Excel histórico |
| 4 | Primer informe mensual · revisión con Lex Digital | EIPD continúa válida |
| 5 | Recogida de feedback estructurado al equipo | NPS interno ≥ 7/10 |
| 6 | **Punto medio · revisión intermedia** con Patronato (informe) | Iremos / continuar / parar |
| 8 | Primera reunión multipro de revisión PIA usando ÁGORA | Acta generada desde ÁGORA |
| 9 | Generación del primer **Informe Trimestral a la Junta de Castilla y León** desde ÁGORA | Informe aceptado |
| 10 | Evaluación coste/beneficio operativa | Tiempo ahorrado en gestión |
| 11 | Auditoría completa de datos por Lex Digital | Cero hallazgos críticos |
| 12 | **Cierre del piloto** · informe trimestral al Patronato + decisión sobre Fase 5 | GO / EXTENDER / NO-GO |

---

## 4. Migración masiva — procedimiento

La migración del Excel «Registro PV» y del Odoo legado se hace **en
diciembre 2026**, antes del arranque del piloto.

### 4.1 Origen → destino

| Origen | Volumen estimado | Destino ÁGORA |
|---|---|---|
| Excel «Registro PV» (hoja Fuentecillas) | 62 filas | `PersonaAtendida` + `PlanDeVida` |
| Carpetas papel (alergias, vacunas) | 62 expedientes | `Alergia` + `Vacuna` + escaneo en `media/` |
| Odoo legado (medicación, episodios) | ≈ 600 registros | `PautaMedicacion` + `ProblemaSalud` |
| Excel ocupación (plano del centro) | 64 camas | `Modulo` + `Habitacion` + `Cama` + `OcupacionCama` |
| Listado familias | ≈ 180 contactos | `PersonaContacto` + `VinculoPersonaContacto` |

### 4.2 Importador

Reutilizamos el comando `importar_excel_registro_pv` ya validado en seco
(Fase 1) más:

- Comando nuevo `importar_alergias_vacunas` (Fase 2.5 + retoque) para los
  datos clínicos en carpeta papel.
- Comando `importar_medicacion_odoo` (futuro) — si se decide migrar también
  la medicación del Odoo legado. Si es muy frágil, **alternativa**: empezar
  el piloto con la medicación introducida a mano por enfermería en los
  primeros 14 días (criterio de Lucía).

### 4.3 Validación post-migración (manual)

Lucía + María Ruiz toman **una muestra aleatoria de 10 personas** (≈ 16 %)
y verifican manualmente que los datos coinciden. Si la muestra revela
>2 errores graves, se repite la migración.

### 4.4 Acta de migración

Firmada por Federico + Lucía + Sistemas Aspanias antes del día 1 del piloto.
Sirve como evidencia para auditorías futuras.

---

## 5. Comunicación a las 62 personas atendidas y sus familias

Se reutilizan las plantillas de Fase 3 (`carta_familias.md` +
`clausula_lectura_facil.md` + `consentimiento_informado.md`) con dos
diferencias:

1. La carta menciona explícitamente que **el Excel deja de usarse**.
2. El consentimiento es **definitivo** (no pre-piloto). La retirada
   sigue siendo posible pero requiere volver al Excel (informar bien).

**Calendario de envío**: las 62 cartas salen en bloque la **semana -2** del
piloto (≈ 28 diciembre 2026). Plazo para devolver el consentimiento: 10
días naturales.

**Recogida en persona**: las familias que prefieran firmar en mano lo
hacen en la visita habitual al centro.

**Si una familia NO firma a los 10 días**:
- Federico llama personalmente para resolver dudas.
- Si tras la llamada sigue sin firmar, se les ofrece una sesión presencial
  con Lex Digital.
- Si finalmente rechaza, **la persona se gestiona solo desde Excel**
  durante el piloto. NO se la incluye en ÁGORA.

> Aspirar a ≥ 95 % de consentimientos antes del día 1. <95 % obliga a
> reevaluar el calendario con Lex Digital.

---

## 6. Plan de contingencia y rollback

### 6.1 Escenarios

| # | Escenario | Probabilidad | Acción |
|---|---|---|---|
| C1 | ÁGORA cae (servidor down) > 2 h en horario laboral | Baja | Volver al Excel temporalmente · Sistemas Aspanias diagnostica · Innovación implementa fix |
| C2 | BD corrupta o datos perdidos | Muy baja | Restauración desde último backup diario (3:00 AM) · pérdida máxima 24 h · comunicar a Lex Digital |
| C3 | Brecha RGPD detectada | Muy baja, crítica | Protocolo de respuesta < 72 h: notificación AEPD · informe a Patronato · evaluación de notificación a interesados |
| C4 | Rechazo masivo del equipo (más de 5 profesionales no usan la herramienta) | Baja | Reunión inmediata Federico + Lucía · pausa de 1 semana para escuchar y ajustar · si no se resuelve, vuelta al Excel + replanteo |
| C5 | Bug que impide editar el Plan de Vida | Media (es complejo) | Hotfix de Innovación Aspanias en < 4 h laborales · entretanto usar Word como en pre-piloto · documentar |
| C6 | Una persona atendida cambia de centro durante el piloto | Media | Marcar baja en ÁGORA · transferir documentación · informar al centro destino |

### 6.2 Rollback total

Si las cosas van muy mal (≥ 2 escenarios críticos simultáneos, o decisión
del Patronato), el rollback completo:

```
Semana 0:  Decisión formal de rollback
Semana 1:  Activar Excel como fuente de verdad otra vez
            Volcar a Excel los datos posteriores a la migración
            Notificar a las 62 familias del cambio
Semana 2:  ÁGORA queda en modo solo lectura como histórico
            Postmortem documentado: qué falló, qué aprendemos
Semana 3:  Replanteamiento: ¿vamos a Fase 2.5+ o paramos el proyecto?
```

Acto seguido se convoca al Patronato extraordinariamente para informar.

---

## 7. Métricas de seguimiento del piloto

Las publica Federico **mensualmente** en `docs/fase4/informes_mensuales/`:

### 7.1 Adopción y uso

- Profesionales que acceden cada día (% sobre los 18)
- Personas atendidas con ficha actualizada en los últimos 30 días (% sobre 62)
- Intervenciones registradas/día (objetivo ≥ 10 con 18 profesionales)
- Citas creadas en ÁGORA / total citas reales (objetivo ≥ 95 %)

### 7.2 Calidad de datos

- Coincidencia Excel histórico ↔ ÁGORA producción (objetivo ≥ 98 %)
- Discrepancias detectadas y resueltas
- Datos faltantes (campos obligatorios vacíos)

### 7.3 RGPD

- Accesos sin motivo registrado (objetivo: cero)
- Solicitudes de derechos ARSULIPO recibidas
- Brechas o incidentes (objetivo: cero)

### 7.4 Operativa y negocio

- Tiempo de generación del informe trimestral (objetivo: <1 día vs 1 semana del Excel)
- Reducción de incidencias en revisiones PIA (cualitativo)
- NPS interno del equipo (objetivo: ≥ 7/10)

---

## 8. Riesgos identificados y mitigaciones

| # | Riesgo | Probab. | Impacto | Mitigación |
|---|---|---|---|---|
| R1 | Resistencia de profesionales que no participaron en pre-piloto | Media | Alto | Formación dedicada + Lucía como puente · Federico responde personalmente las primeras semanas |
| R2 | Migración del Odoo legado con datos inconsistentes | Alta | Medio | Empezar con medicación a mano · migrar Odoo después |
| R3 | Familias rechazan consentimiento masivamente (>20 %) | Baja | Crítico | Trabajo previo en Asociación Aspanias · explicación clara |
| R4 | Volumen real supera capacidad del servidor | Baja | Medio | Pruebas de carga en staging · alertas en monitorización |
| R5 | Federico no está disponible 1-2 semanas (enfermedad, viaje) | Media | Alto | Suplencia formal: María Ruiz como sponsor delegada · acta de delegación |
| R6 | Cambio normativo CyL durante el piloto (Ley 3/2024 nuevo reglamento) | Baja | Medio | Lex Digital monitoriza · ajustes ágiles |
| R7 | Pérdida de un certificado SSL en el medio del piloto | Baja | Bajo | Renovación automática + alerta 30 días antes |

---

## 9. Gobernanza del piloto

| Periodicidad | Reunión | Quién |
|---|---|---|
| Diaria (informal) | Coordinación operativa | Lucía + Federico (15 min) |
| Semanal | Reunión de seguimiento equipo Fuentecillas | Lucía + equipo (1 h) |
| Quincenal | Reunión técnica con Innovación Aspanias | Federico + Innovación (1 h) |
| Mensual | Informe a Patronato + Consejo | Federico (escrito · sin reunión) |
| Punto medio (sem 6) | Revisión intermedia con Patronato | Federico ante Patronato (30 min) |
| Final (sem 12) | Informe trimestral oficial + decisión Fase 5 | Federico + Lex Digital ante Patronato |

---

## 10. Decisión final · go a Fase 5 (despliegue al grupo)

Al cierre del piloto (semana 12) se decide:

| Recomendación | Significado |
|---|---|
| **GO** | Arrancar Fase 5 con el calendario previsto (Salas + Vivienda San Pedro Q3 2027 → resto hasta 2029) |
| **GO con ajustes** | Arrancar Fase 5 con los X cambios prioritarios implementados primero |
| **EXTENDER** | Prolongar el piloto 1 trimestre más (Q2 2027) · Fase 5 retrasa Q4 2027 |
| **NO-GO** | Volver a Fase 2.5 o replantear el proyecto · Excel sigue siendo fuente única |

La decisión se toma con el **informe trimestral** y el **voto cualitativo
del equipo de Fuentecillas** (≥ 13/18 a favor para considerar GO).

---

## 11. Comunicación externa durante el piloto

Aspectos a tener en cuenta:

1. **A otros centros del Grupo**: información periódica (newsletter interna
   mensual) de cómo va el piloto. Sin presión: cuando ÁGORA esté maduro,
   irán llegando. Genera expectativa positiva.

2. **A familias del grupo (asociadas a Aspanias)**: comunicación general
   en la asamblea de la Asociación Aspanias del primer trimestre 2027.
   Se explica que es piloto, no compromiso de generalización.

3. **A la Junta de Castilla y León (concierto)**: comunicación formal
   por escrito al inicio del piloto. ÁGORA cumple con su exigencia de
   trazabilidad. Mostrar disposición a auditoría si lo solicitan.

4. **A prensa**: NO se hace ruido externo durante el piloto. Si va bien,
   nota de prensa al cierre.

5. **A redes sociales Aspanias**: nada hasta cierre exitoso del piloto.
   Si se decide comunicar, lo hace el equipo de Comunicación con
   plantilla institucional.

---

## 12. Documentos auxiliares (a producir en Q4 2026)

- [ ] `docs/fase4/checklist_arranque.md` — checklist firmable de las 11 condiciones de §2
- [ ] `docs/fase4/protocolo_brechas.md` — protocolo de respuesta a incidente RGPD <72h
- [ ] `docs/fase4/plantilla_informe_mensual.md` — para los informes mensuales al Patronato
- [ ] `docs/fase4/acta_arranque.md` — modelo de acta de arranque del día 1
- [ ] `docs/fase4/informe_trimestral_jcyl.md` — modelo del primer informe trimestral
- [ ] `docs/fase4/postmortem.md` — plantilla de postmortem si hubiera rollback

---

## 13. Calendario macro hasta el cierre del piloto

| Hito | Fecha |
|---|---|
| Cierre Fase 3 pre-piloto · informe go/no-go | 23 oct 2026 |
| Si GO: arranque preparación Fase 4 | Nov 2026 |
| Migración masiva en staging | Dic 2026 |
| Formación al equipo completo | Dic 2026 |
| Comunicación a las 62 familias | Sem -2 (28 dic 2026) |
| **Día 1 del piloto en producción** | Lun 11 ene 2027 |
| Revisión intermedia con Patronato | Sem 6 (≈ 22 feb 2027) |
| Cierre piloto · informe trimestral | Sem 12 (≈ 4 abr 2027) |
| Decisión sobre Fase 5 | Patronato siguiente (abril 2027) |

---

*Plan de piloto v0.1 · 2026-05-19 · Federico Martínez (sponsor).*

*Este documento se revisa y actualiza tras el informe del pre-piloto
(23 oct 2026) antes de su activación formal.*

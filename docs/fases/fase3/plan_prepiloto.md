# Plan detallado del pre-piloto — Fase 3

**Centro**: Residencia Fuentecillas
**Duración**: 6 semanas
**Ventana objetivo**: 7 sept – 16 oct 2026
**Sponsor**: Federico Martínez — Gerencia
**Coordinación in situ**: Lucía Martínez (TO · Coord. Fuentecillas)
**Versión**: 0.1 (borrador para validación con equipo)

---

## 1. Por qué un pre-piloto

Antes del piloto en producción (Fase 4, Q1 2027), necesitamos seis semanas en
las que el equipo de Fuentecillas **use ÁGORA en paralelo al Excel actual**.
La meta no es sustituir todavía — es:

1. Detectar lo que falla en el uso real (UX, datos, formación).
2. Medir cuánto tiempo cuesta cada tarea respecto al Excel.
3. Verificar que el modelo de datos cubre todos los casos reales.
4. Validar que las personas atendidas y sus familias están informadas y de
   acuerdo conforme al RGPD.
5. Construir confianza del equipo en la herramienta — lo más importante.

> Si al cabo de 6 semanas el equipo NO está cómodo, no avanzamos a Fase 4.
> Volveremos a iterar. Es mejor prolongar 2 meses que romper el piloto.

---

## 2. Equipo participante

| Rol | Persona | Dedicación pre-piloto |
|---|---|---|
| **Coordinación Fuentecillas** | Lucía Martínez (TO) | 4 h/semana |
| **Gestora de Caso** | María Ruiz (TS) | 3 h/semana |
| **Enfermería** | Beatriz Hernando (DUE) | 3 h/semana |
| **Psicología** | Carlos García López (Psi) | 2 h/semana |
| **Educación** | Inés Rojo + Andrés Diez | 2 h/semana cada uno |
| **Sponsor + Dirección** | Federico Martínez | 1 reunión semanal |
| **Soporte técnico** | Innovación Aspanias (1 persona dedicada) | 4 h/semana |
| **Asesoría RGPD** | Lex Digital | 1 sesión inicial + on-demand |

Total: ≈ 20 h/semana repartidas. Encajan dentro de su jornada habitual sin
horas extra (excepto las 2 sesiones de formación que sí son adicionales).

---

## 3. Calendario · 6 semanas

### Semana 1 · 7-11 sept · Formación y arranque

| Día | Actividad | Quién | Horas |
|---|---|---|---|
| Lun mañana | **Sesión formación 1**: filosofía ÁGORA + ficha persona | Todos + Federico | 2 h |
| Lun tarde | Crear cuenta SSO M365 + primer acceso | Cada profesional | 30 min |
| Mar | Práctica: cada uno abre la ficha de 3 personas reales | Individual | 1 h |
| Mié mañana | **Sesión formación 2**: Plan de Vida + Agenda | Todos | 2 h |
| Jue | Práctica: registrar 2 intervenciones reales | Individual | 30 min |
| Vie | **Reunión cierre semana 1** + recogida feedback inicial | Todos + Federico | 1 h |

**Material entregado**: manual rápido (1 página por módulo) + URL acceso + chuleta del SSO.

**Objetivo de la semana**: nadie se atasca al entrar. Todos saben dónde están las cosas.

---

### Semana 2 · 14-18 sept · Doble carga arrancando

Empieza la rutina de doble carga: lo que se anota en Excel **también** se anota en ÁGORA.

| Tarea cotidiana | Quién | Frecuencia |
|---|---|---|
| Crear cita en agenda | Recepción + cada profesional | Cada vez que se agende |
| Registrar intervención | Profesional que la realiza | Mismo día |
| Anotar valoración (BVD, ICAP) | Profesional aplicador | Día de la valoración |
| Modificar pauta de medicación | DUE | Cada cambio |
| Apunte de problema de salud nuevo | DUE / coordinación | Cuando ocurra |

Doble carga **NO incluye** todavía:
- Plan de Vida (lo abordamos en semana 3)
- Datos administrativos sanitarios (NUSS/TSI) — los importamos al final
- Familiares — se van añadiendo poco a poco

**Reunión viernes 18/09 · 1 h**: ¿qué ha costado más? ¿qué falla? ¿qué cambiaría?

---

### Semana 3 · 21-25 sept · Plan de Vida

| Día | Actividad | Quién |
|---|---|---|
| Lun | **Sesión formación 3**: los 5 documentos del Plan de Vida en ÁGORA | María Ruiz (TS) + Lucía |
| Mar-Jue | Migrar 3 Planes de Vida activos a ÁGORA (los más recientes) | Lucía + María |
| Vie | Imprimir los 3 Planes desde ÁGORA y comparar con el documento Word actual | Lucía + Federico |

**Objetivo**: validar que el Plan de Vida en ÁGORA reproduce fielmente el formato del Protocolo Aspanias y se puede imprimir como hoy.

**Reunión viernes 25/09 · 1 h**: ajustes solicitados al Plan de Vida.

---

### Semana 4 · 28 sept – 2 oct · Familiares y comunicación CERCA

| Día | Actividad |
|---|---|
| Lun-Mar | Añadir familiares de las 3 personas migradas. Marcar quién recibe CERCA. |
| Mié | **Comunicación a las familias**: enviar carta institucional (anexo 1) + cláusula informativa en lectura fácil a las 3 personas atendidas |
| Jue | Sesión con Lex Digital: validar que el consentimiento informado está bien recogido |
| Vie | **Reunión cierre semana 4** |

**Hito**: las 3 personas atendidas del pre-piloto y sus familias están informadas del tratamiento de datos en ÁGORA. Firma del consentimiento informado adaptado.

---

### Semana 5 · 5-9 oct · Refinamiento e iteración

Esta semana NO hay actividad nueva: se trabaja sobre lo recopilado en las 4
semanas anteriores.

| Actividad | Quién |
|---|---|
| Recoger los 15-20 cambios solicitados en reuniones de feedback | Federico + Innovación |
| Priorizar: top 5 críticos · resto a backlog | Federico |
| Implementar y desplegar los 5 críticos | Innovación Aspanias |
| Re-formar al equipo sobre los cambios (sesión corta) | Federico |
| Continuar doble carga | Equipo |

**Reunión viernes 9/10 · 1 h**: ¿los 5 cambios han resuelto los problemas? ¿qué queda?

---

### Semana 6 · 12-16 oct · Validación final y go/no-go

| Día | Actividad |
|---|---|
| Lun-Mar | **Auditoría de datos**: comparar Excel ↔ ÁGORA. Coincidencia esperada ≥ 95 % |
| Mié | **Validación clínica** (sesión con DUE + Psicología): ¿la información médica es correcta y útil? |
| Jue | **Validación jurídica** (sesión con Lex Digital): ¿la bitácora registra todo? ¿la confidencialidad funciona? |
| Vie | **Reunión final con el equipo** (2 h): decisión go/no-go conjunta. Voto cualitativo de cada profesional. |

**Entregables al cierre**:
- Informe de pre-piloto (8-10 páginas) con datos, feedback y conclusión.
- Lista de cambios pendientes priorizados.
- Decisión formal: ¿pasamos a Fase 4 piloto?

---

## 4. Materiales de formación

Documentos a producir en agosto, antes del arranque:

| Material | Formato | Quién lo prepara |
|---|---|---|
| Manual rápido por módulo (5 hojas: persona, plan de vida, agenda, indicadores, control PV) | PDF imprimible | Federico + Innovación |
| Vídeo de 5 min "Tour por ÁGORA" | MP4 corporativo | Federico |
| Chuleta SSO Microsoft 365 (cómo entrar) | 1 hoja A4 | Sistemas Aspanias |
| Tarjetón con la URL + QR para móvil | Tarjeta | Federico |
| Cláusula informativa en lectura fácil para personas atendidas | Documento simplificado con pictogramas | Lex Digital + equipo Fuentecillas |
| Carta institucional a familias | Documento Word con membrete | Federico + Comunicación |

---

## 5. Plantilla de feedback semanal

Cada reunión de viernes recoge esta plantilla en menos de 15 minutos:

```
SEMANA: ___
PROFESIONAL: ___

1. ¿Cuántas veces has usado ÁGORA esta semana?
   [ ] Diario · [ ] 3-4 veces · [ ] 1-2 veces · [ ] Ninguna

2. Tiempo dedicado a doble carga estimado:
   ___ minutos/día

3. Lo que MÁS te ha funcionado:
   _____________________________________

4. Lo que MENOS te ha funcionado:
   _____________________________________

5. ¿Qué cambiarías si pudieras?
   _____________________________________

6. ¿Recomendarías seguir adelante?  (1 = no · 5 = totalmente)
   [ ] 1  [ ] 2  [ ] 3  [ ] 4  [ ] 5

7. Comentarios libres:
   _____________________________________
```

Las plantillas semanales se archivan en `datos/feedback/semana_NN/`.

---

## 6. Criterios go/no-go para Fase 4

Para pasar al piloto en Q1 2027 deben cumplirse **todos** estos criterios:

| Criterio | Umbral | Cómo se mide |
|---|---|---|
| **Adopción del equipo** | ≥ 80 % del equipo usa ÁGORA diariamente en semana 6 | Pregunta 1 de la plantilla |
| **Coincidencia de datos** | Excel ↔ ÁGORA coinciden ≥ 95 % en las 3 personas migradas | Auditoría manual semana 6 |
| **Tiempo de doble carga** | ≤ 15 minutos extra al día por profesional | Pregunta 2 |
| **Plan de Vida imprimible** | El PDF generado por ÁGORA equivale al Word actual | Validación visual semana 3 |
| **RGPD validado** | Lex Digital firma la conformidad | Sesión semana 6 |
| **Bitácora operativa** | Cada lectura de ficha aparece en `RegistroAcceso` | Auditoría jueves semana 6 |
| **Voto cualitativo** | Mayoría del equipo (≥ 5/8) recomienda seguir | Voto viernes semana 6 |
| **Cero brechas RGPD** | Ningún incidente con datos reales durante 6 semanas | Verificación Federico |

**Si falla alguno**:
- 1-2 criterios marginales: prolongar el pre-piloto 2-4 semanas, atender los fallos.
- 3+ criterios o "voto cualitativo" negativo: parar Fase 4, replantear y volver a Fase 2.5 o 3.

---

## 7. Riesgos identificados y mitigaciones

| # | Riesgo | Probabilidad | Mitigación |
|---|---|---|---|
| R1 | El equipo rechaza la doble carga por fatiga | Media | Reuniones semanales para escuchar. Reducir alcance si hace falta. |
| R2 | Excel y ÁGORA divergen y nadie sabe cuál es la verdad | Alta | Excel es la fuente única hasta el final de Fase 3. ÁGORA es "copia espejo". |
| R3 | Una persona atendida o familia rechaza el tratamiento en ÁGORA | Media | Se les excluye del pre-piloto. Suficientes voluntarios entre las 62 de Fuentecillas. |
| R4 | Bug crítico que para la herramienta | Baja | Innovación Aspanias responde en < 4 h laborales. Backups diarios. |
| R5 | Brecha RGPD (acceso indebido a datos reales) | Muy baja pero crítica | Protocolo de respuesta documentado. Notificación AEPD < 72 h. Federico es punto único. |
| R6 | Lucía o Federico se enferman / vacaciones | Media | Backup nominado: María Ruiz (TS) como coord. suplente. Sesiones en remoto si hace falta. |

---

## 8. Comunicación a personas atendidas y familias

Antes de que cualquier dato real entre en ÁGORA, las 3 personas atendidas
del pre-piloto y sus familias deben:

1. **Recibir la carta institucional** con explicación del proyecto y el
   periodo de pre-piloto (semana 4, lunes).
2. **Leer la cláusula informativa en lectura fácil** (con pictogramas) — la
   persona atendida y, si procede, su figura de apoyo.
3. **Firmar el consentimiento informado adaptado** ante la persona de
   referencia o la gestora de caso (semana 4, miércoles-jueves).
4. **Saber que pueden retirarlo en cualquier momento**. Si lo hacen, se les
   excluye del pre-piloto sin consecuencias en la atención.

> ⚠️ Si alguna persona o familia no firma, NO se la incluye. Tenemos 62
> personas en Fuentecillas; encontrar 3 voluntarias es factible.

---

## 9. Personas atendidas candidatas para el pre-piloto

Criterios de selección (Federico + Lucía deciden en agosto):

- Persona con **capacidad jurídica plena** o medida de apoyo voluntaria
  (más sencillo legalmente).
- Familia **colaboradora** y con disposición a participar.
- **Variedad** entre las 3: idealmente DI + Mayor dependiente + perfil mixto.
- Plan de Vida **vigente y reciente** (no más de 12 meses) para tener material.

Los nombres concretos se acuerdan con Lucía y se documentan en
`docs/fase3/personas_candidatas.md` (privado, no en repo público).

---

## 10. Calendario macro hasta Q1 2027 piloto

| Hito | Fecha |
|---|---|
| Validación formal Fase 0 por Patronato | 10/06/2026 |
| Fin Fase 2 + endurecimiento técnico | Sept 2026 |
| Despliegue VM Sistemas Aspanias | Agosto 2026 |
| **Pre-piloto (Fase 3)** | 7 sept – 16 oct 2026 |
| Informe de pre-piloto + decisión go/no-go | 23/10/2026 |
| Si go: **arranque piloto Fuentecillas** | Q1 2027 (enero-marzo) |
| Si no-go: nueva iteración Fase 2.5/3 | Otoño-invierno 2026 |

---

## 11. Documentos auxiliares (a producir)

- [ ] `docs/fase3/manual_uso_rapido.pdf` — manual de 5 hojas
- [ ] `docs/fase3/carta_familias.md` — carta institucional + tarjetón
- [ ] `docs/fase3/clausula_lectura_facil.md` — cláusula con pictogramas
- [ ] `docs/fase3/consentimiento_informado.md` — formulario para firmar
- [ ] `docs/fase3/auditoria_datos_excel_vs_agora.md` — procedimiento de auditoría
- [ ] `docs/fase3/personas_candidatas.md` — selección concreta (privado)
- [ ] `docs/fase3/informe_prepiloto.md` — plantilla del informe final

Los iremos creando antes del arranque, en agosto 2026.

---

## 12. Próximo paso

Validar este plan con:
1. Lucía Martínez (coordinación Fuentecillas) — sesión 30 min
2. María Ruiz (gestora de caso) — sesión 30 min
3. Innovación Aspanias — sesión 1 h
4. Lex Digital — sesión 1 h (RGPD)

Una vez validado por las 4 partes, **bloquear las 6 semanas en agenda** de
todo el equipo y comunicar al resto del centro.

---

*Plan de pre-piloto v0.1 — 2026-05-19 · Federico Martínez (sponsor)*

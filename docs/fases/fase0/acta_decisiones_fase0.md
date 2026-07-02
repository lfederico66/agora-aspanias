# Acta de decisiones — Fase 0 ÁGORA

**Proyecto**: ÁGORA — Atención y Gestión Operativa para Residentes y Atendidos
**Fecha**: 2026-05-13
**Decisor**: Federico Martínez — Gerencia Grupo Social Aspanias
**Tipo de documento**: acta institucional para protección de la decisión gerencial

---

## 1. Objeto del acta

Dejar constancia formal de las decisiones tomadas por Gerencia al cerrar la Fase 0 del proyecto ÁGORA, incluyendo aquellas decisiones en las que Gerencia opta por mantener el compromiso de calendario o de alcance asumiendo riesgos identificados explícitamente.

Este documento se incorpora a la documentación que se elevará al Patronato de la Fundación Aspanias Burgos y al Consejo de Administración de Aspaniasmerc 2016 S.L.U. para la aprobación de la cotitularidad RGPD y del despliegue del piloto.

---

## 2. Decisiones tomadas

### 2.1 Alcance del CRM

- El CRM cubrirá **los cuatro colectivos del grupo** desde la primera versión: discapacidad intelectual, mayores dependientes, inserción laboral, familias y entorno.
- El MVP del piloto incluirá: ficha única, Plan Individual de Atención (PIA/AICP), agenda multiprofesional e indicadores/memoria automatizada.

### 2.2 Stack tecnológico

- Django 5 + HTMX + Alpine.js + TailwindCSS + PostgreSQL 16, con SSO Microsoft 365 para profesionales y federación con CERCA para familias. Stack coherente con SIGPER y CERCA.

### 2.3 Relación con el Odoo legado

- Decisión: **sustituir** completamente el Odoo `preaspanias.integrodoo.com`. Se descarta la cohabitación prolongada.
- Implicación: se requiere plan de migración de datos antes del piloto.

### 2.4 Centro piloto

- Centro Fuentecillas (Burgos), aprovechando sinergias con CERCA.

### 2.5 Propietario funcional

- **Dirección de Centros y Servicios** del Grupo Social Aspanias asume la propiedad funcional del sistema y la validación operativa.
- **Titular**: Federico Martínez Miguel, en doble rol con la Gerencia del Grupo (confirmado 2026-05-13).

### 2.6 Régimen RGPD

- **Cotitularidad** entre **Fundación Aspanias Burgos** y **Aspaniasmerc 2016 S.L.U.** conforme al artículo 26 del RGPD.
- Obliga a la firma de acuerdo de corresponsables, a la aprobación de ambos órganos de gobierno y a un punto de contacto único para las personas interesadas.

### 2.7 Calendario y asunción de riesgo

- **Decisión gerencial**: mantener el hito de **piloto en Q3 2026** sin recortar el MVP, asumiendo formalmente los riesgos de ejecución identificados.
- Gerencia ha sido informada por escrito de las tres alternativas con menor riesgo (recorte de MVP, MVP ultra-mínimo, aplazamiento a Q4 2026) y opta por mantener el compromiso original.

---

## 3. Riesgos identificados y formalmente asumidos por Gerencia

| Nº | Riesgo | Mitigación obligatoria |
|---|---|---|
| R1 | Incumplimiento de fecha por bloqueante legal (cotitularidad / EIPD) | Borradores en paralelo a Fase 1 técnica desde semana 20-2026. Reuniones DPO + jurídico semanales. |
| R2 | Calidad insuficiente del MVP por compresión de plazos | Equipo dedicado. Validación semanal por Dirección de Centros y Servicios. Congelación de alcance. |
| R3 | Migración Odoo no completada a tiempo | Carga inicial limitada a maestros. Histórico en lectura desde Odoo hasta 6 meses post-piloto. |
| R4 | Resistencia de equipos asistenciales | Pre-piloto técnico julio 2026. Formación obligatoria 2 semanas previas. |
| R5 | Falta de aprobación de Patronato + Consejo a tiempo | Convocatoria al primer Patronato y Consejo disponibles (junio 2026). |
| R6 | Salida con calidad insuficiente que comprometa confianza institucional | Criterios go/no-go formales: EIPD firmada, acuerdo cotitularidad firmado, MVP funcional con 5 fichas validadas, bitácora operativa. |
| R7 | Capacidad limitada del equipo interno (Innovación Aspanias + Sistemas Aspanias, sin senior externo) | Revisiones cruzadas entre equipos. Auditoría externa puntual de arquitectura y seguridad antes del piloto. Refuerzo externo puntual si en revisión de 15 julio se detecta retraso. |
| R8 | DPO definitivo sin designar a 4 semanas del Patronato del 10 junio | Asunción de DPO externo interino por Lex Digital antes del 20 mayo 2026. Selección de DPO definitivo en paralelo. Sin DPO firmando, no se eleva la EIPD al Patronato. |

---

## 4. Criterios go/no-go al piloto

Acordados formalmente. Si al **1 de septiembre de 2026** alguno de los siguientes hitos no está cerrado, **se aplaza el piloto** sin reabrir esta decisión ni renegociar el alcance:

1. EIPD firmada por DPO y aprobada por ambos responsables.
2. Acuerdo de cotitularidad art. 26 RGPD firmado por Fundación Aspanias Burgos y Aspaniasmerc 2016 S.L.U.
3. MVP funcional verificado con al menos 5 fichas reales de Fuentecillas.
4. Bitácora de accesos operativa, con prueba de lectura ante incidente simulado.

Este acuerdo previo evita decisiones de continuidad bajo presión y protege la calidad del despliegue.

---

## 5. Compromisos de Gerencia

Para que el calendario Q3 2026 sea ejecutable, Gerencia se compromete a:

- Asignar **equipo de desarrollo dedicado** a tiempo completo desde la semana 20-2026.
- Designar **interlocutor único** desde Dirección de Centros y Servicios para validación funcional semanal.
- Convocar **Patronato extraordinario** y **Consejo de Aspaniasmerc** en junio 2026 para aprobar la cotitularidad.
- Habilitar **presupuesto** para DPO/jurídico externo si es necesario para EIPD y acuerdo de cotitularidad.
- **Decidir en menos de 48 horas** cualquier bloqueo operativo que llegue a Gerencia desde el proyecto.

---

## 6. Calendario institucional

- **Elevación a órganos de gobierno**: **10 de junio de 2026** — Patronato extraordinario Fundación Aspanias Burgos + Consejo de Administración Aspaniasmerc 2016 S.L.U. Convocatoria confirmada por Gerencia.
- **Revisión de hito**: 15 julio 2026 (mitad del recorrido). Si dos o más mitigaciones no están en marcha, Gerencia reevalúa el calendario.
- **Decisión go/no-go**: 1 septiembre 2026.

## 7. Interlocutores confirmados (2026-05-13)

| Función | Asignación |
|---|---|
| Sponsor + Propietario funcional | Federico Martínez Miguel (Gerencia + Dirección de Centros y Servicios) |
| Asesoría jurídica RGPD | Lex Digital |
| DPO | Pendiente — Lex Digital como candidato a DPO externo interino |
| Desarrollo funcional | Innovación Aspanias (interno) |
| Desarrollo técnico, infraestructura, despliegue | Sistemas Aspanias (interno) |

---

## 8. Firmas

| Cargo | Nombre | Fecha | Firma |
|---|---|---|---|
| Gerencia Grupo Social Aspanias | Federico Martínez Miguel | 2026-05-13 | (pendiente) |
| Dirección de Centros y Servicios | Federico Martínez Miguel | 2026-05-13 | (pendiente) |
| DPO externo interino | Lex Digital (pendiente confirmación) | | |

---

*Acta v1.0 — preparada para validación formal y elevación a órganos de gobierno.*

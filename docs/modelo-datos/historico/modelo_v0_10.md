# Modelo de datos ÁGORA — v0.10 (integración del Excel real del grupo)

**Estado**: ✅ ÁGORA reproduce nativamente las **3 capas** del Excel "Registro PV por servicios. Global Grupo Aspanias.xlsx": (1) tabla de control por centro, (2) KPIs globales del grupo, (3) carga de gestores/as. Más snapshot histórico.
**Fecha**: 2026-05-18
**Sustituye a**: `modelo_v0_9.md`.

> Federico aportó el Excel real que hoy llevan los responsables de cada uno de los 13 centros del grupo. Analizado y replicado en ÁGORA sin perder ninguna funcionalidad. Excel pseudonimizado disponible para pruebas.

---

## Lo nuevo en v0.10

### 1. Pseudonimizador del Excel real

Script `scripts/pseudonimizar_excel_pv.py` que toma el Excel original (con ~383 personas y ~30 profesionales reales) y produce una versión `_PSEUDO.xlsx` con nombres ficticios consistentes entre las 16 hojas. **2137 sustituciones en una sola pasada**, mapeo determinista (mismo real → mismo ficticio en todas las hojas).

Permite trabajar con datos realistas sin riesgo RGPD durante pruebas, demo y desarrollo del importador.

### 2. Ampliación de `PlanDeVida` (4 campos nuevos)

Para reproducir las columnas del Excel actual:

```python
fecha_prevista_realizacion = DateField    # fecha planificada
pv_realizado = BooleanField               # columna 'PV realizado'
pv_revisado = BooleanField                # columna 'PV revisado'
estado_revision = TextChoices(en_plazo / fuera_plazo / pendiente)
compartido_con_residencia_vivienda = BooleanField
```

Visible en admin Django + filtrable en cuadros de mando.

### 3. Vista "Control PV por servicios"

URL: `/planes-vida/control/` (tablero de centros) y `/planes-vida/control/<codigo>/` (detalle por centro).

Reproduce la **hoja por servicio** del Excel actual: tabla con 12 columnas (Usuario, Gestor, Persona referencia, PV realizado SI/NO, PV revisado SI/NO, ¿En Teams?, ¿En REPRISS?, Fecha prevista, Fecha revisión, Estado revisión, Compartido). Estilo verde corporativo Aspanias.

**Esto sustituye nativamente al Excel** cuando ÁGORA entre en producción.

### 4. Vista KPIs Plan de Vida

URL: `/indicadores/planes-vida/`.

Reproduce la **hoja "Datos Grupo Aspanias"**:
- 5 KPIs grandes: Total usuarios, PV realizados, PV pendientes, PV revisados, Fuera de plazo.
- Desglose por corresponsable (FAB vs Aspaniasmerc).
- Tabla con desglose por cada uno de los 13 centros con enlaces directos al control por servicio.

Cálculo en vivo en `indicadores/calc.py::kpis_planes_vida()`.

### 5. Vista Carga de gestores/as de caso

URL: `/indicadores/gestores-caso/`.

Reproduce la **hoja "Gestores de caso"**:
- Tabla con gestores × centros con conteo de casos por centro.
- Alerta visual cuando alguien sobrepasa los **30 casos** del protocolo §2.3.
- Cabecera en verde corporativo.

### 6. Modelo `SnapshotPlanesVida` + comando

Reproduce la **hoja "Histórico"** del Excel — guarda foto periódica de los KPIs para comparar evolución temporal.

```bash
python manage.py generar_snapshot_planes_vida --etiqueta "Cierre 2026Q2"
```

Idempotente por día. Almacena: total usuarios, FAB/Aspaniasmerc, PV realizados/pendientes/revisados/fuera_plazo + desglose JSON por centro.

Pensado para ejecutarse:
- Trimestralmente como cron (con `manage.py runserver` no, con scheduler externo o cron de Linux).
- Manualmente al cierre de cada anualidad.

---

## Mapeo Excel actual → ÁGORA

| En el Excel | En ÁGORA |
|---|---|
| 13 hojas por centro/servicio | Vista `/planes-vida/control/<codigo>/` |
| Cabecera (Centro, Responsable, Fecha) | Campos del `Centro` + `PlanDeVida.fecha_revision` |
| Columna Usuario/a | `PersonaAtendida.nombre` + `apellido_1` + `apellido_2` |
| Columna Gestor/a de caso | `PersonaAtendida.gestor_caso` (FK Profesional) |
| Columna Persona de referencia | `PersonaAtendida.persona_referencia` (FK Profesional) |
| Columna PV realizado | `PlanDeVida.pv_realizado` |
| Columna PV revisado | `PlanDeVida.pv_revisado` |
| Columna ¿En Teams? | Cualquier `DocumentoPlanDeVida.url_almacenamiento` rellena |
| Columna ¿En REPRISS? | Cualquier `DocumentoPlanDeVida.publicado_en_repriss=True` |
| Columna Fecha prevista realización PV | `PlanDeVida.fecha_prevista_realizacion` |
| Columna Fecha revisión PV | `PlanDeVida.fecha_revision` |
| Columna Estado revisión | `PlanDeVida.estado_revision` |
| Columna Compartido | `PlanDeVida.compartido_con_residencia_vivienda` |
| Hoja "Datos Grupo Aspanias" | Vista `/indicadores/planes-vida/` |
| Hoja "Gestores de caso" | Vista `/indicadores/gestores-caso/` |
| Hoja "Histórico" | `SnapshotPlanesVida` + comando trimestral |

---

## Mapeo de centros (preliminar — pendiente confirmación)

El Excel revela los 13 servicios reales del grupo. Hay que confirmar qué corresponsable RGPD aplica a cada uno:

| Excel | Probable centro ÁGORA | Corresponsable propuesto |
|---|---|---|
| Res. Quint. (Residencia Quintanadueñas) | RES_QUINT | FAB |
| CD Quint. (Centro Día Quintanadueñas) | CD_QUINT | FAB |
| Vicente Aleixandre | VICENTE | FAB |
| Puentesauco (RHP) | RES_PUENTESAUCO | Aspaniasmerc |
| Salas | SAL | Aspaniasmerc |
| Fuentecillas | FUE | FAB |
| Puentes (Vida Independiente) | PUENTES | FAB |
| CD Puentesauco | CD_PUENTESAUCO | Aspaniasmerc |
| Río Arlanza | LAR | FAB |
| Santa María | SANTA_M | ? |
| Viviendas Puentesauco | VIV_PUENTESAUCO | ? |
| Viviendas Asociación | VIV_ASOC | ? |
| Viviendas Fuentecillas | VIV_FUE | FAB |

Pendiente que Federico confirme el corresponsable de cada uno antes del despliegue real.

---

## Implicaciones operativas

Cuando ÁGORA entre en producción:
1. **El Excel "Registro PV por servicios" deja de mantenerse**. Los responsables actualizan los datos directamente en ÁGORA (formulario web de Plan de Vida con los flags nuevos).
2. Los **KPIs y la hoja de carga de gestores** se calculan automáticamente — ya no hace falta consolidar manualmente cada cierre.
3. El **histórico** se genera con un comando programable, sin perder la traza de evolución que el Excel guardaba a mano.
4. La **bitácora** registra cada cambio en los flags, lo que mejora la auditoría respecto al Excel.

---

## Pendiente

| Bloque | Estado |
|---|---|
| Importador del Excel pseudonimizado con la nueva estructura (13 hojas → 13 centros) | ⏳ próxima sesión |
| Exportación a Excel del control PV (para compatibilidad mientras dure transición) | ⏳ M2 |
| Confirmación del mapeo de centros con sus corresponsables | ⏳ Federico |
| Datos sintéticos: poblar `pv_realizado`, `pv_revisado`, `estado_revision` aleatoriamente | ⏳ próximo `cargar_datos_sinteticos` |

---

*Modelo v0.10 — generado 2026-05-18. ÁGORA sustituye nativamente al Excel global del grupo.*

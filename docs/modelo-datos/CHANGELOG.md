# Modelo de datos — Changelog

Cronología de cambios en el modelo de datos de ÁGORA.
El estado vivo está en `modelo_actual.md`. Las versiones anteriores se conservan en `historico/`.

| Versión | Fecha | Cambio principal |
|---|---|---|
| v0.1 | 2026-05-13 | Modelo inicial post Fase 0 · entidades núcleo (`PersonaAtendida`, `Centro`, `PIA`) |
| v0.2 | 2026-05-14 | + `MedidaDeApoyo`, `CorresponsablePrincipal` (Ley 8/2021) |
| v0.3 | 2026-05-15 | + `Familiar`, `PersonaDeReferencia` |
| v0.4 | 2026-05-16 | + Agenda · `Cita`, `TipoCita` |
| v0.5 | 2026-05-17 | + Intervenciones · `Intervencion`, `TipoIntervencion`, `Valoracion` |
| v0.6 | 2026-05-18 | + Plan de Vida · `PlanDeVida`, `RevisionObjetivos` |
| v0.7 | 2026-05-19 | + Indicadores · `SnapshotPlanesVida`, KPIs |
| v0.8 | 2026-05-20 | + Bitácora append-only (trigger PG) |
| v0.9 | 2026-05-22 | + Importador Excel registro PV |
| v0.10 | 2026-05-25 | + Excel real integrado · `PlanDeVida.estado_revision`, `compartido`, etc. |
| v0.11 | 2026-05-28 | + Clínico · `InformacionMedica`, `Medicamento`, `PautaMedicacion`, `Familiar` |
| v0.12 | 2026-06-01 | + Alojamiento físico · `Modulo`, `Habitacion`, `Cama`, `OcupacionCama` |
| v0.13 | 2026-06-15 | + **App `equipo/`** · `CamposLaboralesProfesional` (OneToOne), `PatronTurno`, `AsignacionPatron`, `Vacacion`, `Turno`, `CalendarioLaboral` |
| v0.14 | 2026-06-16 | + **Módulo Valoraciones psicológicas** · ampliación `Valoracion` (categoría + 13 instrumentos + JSON respuestas/puntuación + estado/firma/PDF) · nuevo modelo `InformePsicologico` (inicial/evolutivo) |
| v0.14.1 | 2026-06-16 | + **Formularios rellenables CdV**: FUMAT (57 ítems) y San Martín (95 ítems) cumplimentables online con cálculo automático PD→PE, percentil e Índice de Calidad de Vida. ICAP pendiente (PDF escaneado, requiere OCR). |
| v0.14.2 | 2026-06-16 | + **INICO-FEAPS** (72 ítems × 2 versiones heteroinforme + autoinforme con baremos diferenciados) y **ABS-RC:2** (18 dominios · 91 ítems · hoja de captura PD con cálculo de totales). 4 escalas operativas, 5/13 catálogo. |
| v0.14.3 | 2026-06-16 | + **ICAP** completo vía OCR (Tesseract 5.5 español sobre PDF escaneado del cuadernillo Bruininks et al.) · 77 ítems literales de Conducta Adaptativa (4 secciones · 0-3) + 8 categorías de Problemas de Conducta (Frec 0-5 × Grav 0-4) + Secciones A-I del protocolo · cálculo de los 4 Índices de Problemas (IIPC/IAPC/IEPC/IGPC) + Nivel de Servicio ICAP (1-9). 5 escalas operativas, 6/13 catálogo. |
| **actual** | **vigente** | Ver `modelo_actual.md` |

## Próximos hitos previstos

| Próx. versión | Cambio previsto | Estado |
|---|---|---|
| ~~v0.13~~ | ~~+ `Profesional`, `PatronTurno`, `Vacacion`, `Turno`, `CalendarioLaboral` (módulo Equipo)~~ | ✅ **Implementado 2026-06-15**. App `equipo/` operativa con 6 modelos + 10 tests pasando. |
| v0.14 | + `CuentaBolsillo`, `MovimientoBolsillo`, `CajaCentro`, `ArqueoMensual` (módulo Caja) | Decisión aprobada en `decisiones/01_dinero_bolsillo.md`. Implementación pendiente. |
| v0.15 | + `TipoServicio`, `TarifaVigente`, `ServicioPrestado`, `FacturaMensual` (módulo Facturación) | Decisión aprobada en `decisiones/02_facturacion_servicios_extras.md`. Implementación pendiente. |
| v0.16 | + `VarianteFIS`, `AmbitoFIS`, `ActividadFIS`, `IncidenciaFIS`, `AdjuntoFIS` (módulo FIS) | Decisión aprobada en `decisiones/03_fis_incidencias.md`. Implementación pendiente. |

## Cómo funciona

1. Cada versión es un snapshot del modelo en `modelo_v0_X.md`.
2. La versión viva está siempre en `modelo_actual.md` (sin sufijo).
3. Las **decisiones de diseño** que motivan cambios viven en `decisiones/` con prefijo numerado.
4. Para añadir una nueva versión: copia `modelo_actual.md` a `historico/modelo_v0_X.md`, actualiza `modelo_actual.md` con los cambios, añade una fila aquí arriba.

# Decisión 08 — Backlog de sincronización demo → Django

**Fecha**: 25/06/2026 · **Estado**: aprobado por Gerencia · **Revisión**: quincenal hasta pre-piloto

---

## Contexto

Entre el 10 y el 25 de junio de 2026 la demo estática ha incorporado funcionalidad validada
con los equipos (Laura Villa · dirección Fuentecillas, Uxue Guerrero · Trabajo Social,
equipo de Psicología) que **no existe todavía en el backend Django** (última versión
implementada: v0.12 + Fase 2.5.x). Este documento inventaría esa brecha y la prioriza
respecto al calendario: **pre-piloto septiembre 2026 · piloto Fuentecillas Q1 2027**.

Criterio de priorización (validado por Gerencia): ante tensión calendario/alcance se
mantiene la fecha del pre-piloto y se recorta alcance, dejando constancia aquí.

---

## Estado actual del backend (lo que YA existe en Django)

| App | Cobertura |
|---|---|
| `personas` | PersonaAtendida completa (v0.11) + InformacionMedica + Familiar + Medicamento/Pauta + alojamiento físico + form crear/editar + cifrado NUSS/TSI + permisos clínicos |
| `pia` | PlanDeVida con campos del Excel real + Control PV por servicios + KPIs + snapshot |
| `intervenciones` | Intervencion + Valoracion (registro genérico) + timeline |
| `agenda` | Cita + vistas Hoy/Semana/Mes |
| `indicadores` | Cuadro de mando 4 pestañas |
| `equipo` | 6 modelos (turnos, vacaciones, calendario, patrones) |
| `core` | Auth SSO, RBAC, bitácora append-only (trigger PostgreSQL) |

---

## Brecha demo → Django, priorizada

### P1 · Imprescindible para el pre-piloto (julio-agosto 2026)

| # | Funcionalidad validada en demo | Trabajo Django | Estimación |
|---|---|---|---|
| 1.1 | **Cuidados de enfermería** (8 bloques) + antecedentes/intervenciones quirúrgicas en ficha | Ampliar `InformacionMedica` o modelo 1-1 `PlanCuidados` + migración + form + fragmento HTMX | 2-3 días |
| 1.2 | **Ficha básica de salud PDF** (petición Laura Villa — uso en urgencias) | Vista `ficha_salud_pdf` con plantilla print + registro en bitácora con motivo | 1-2 días |
| 1.3 | **Edición inline de ficha persona** (modo editar con banner RGPD) | Ya existe form 2.5.5 — añadir campos nuevos + parcial HTMX por sección | 2 días |
| 1.4 | **FIS · módulo incidencias** (bandeja + nueva ficha + estados) | App `incidencias` nueva: modelo FIS + flujo a Dirección (decisión 03 ya redactada) | 4-5 días |
| 1.5 | **Valoraciones rutinarias** (ICAP · FUMAT · San Martín · Calidad de vida, decisión equipo 23/06) | Modelos ItemEscala/Respuesta + cálculo percentiles + informe PDF. Empezar por FUMAT (57 ítems, la más corta) | 5-8 días |

**Subtotal P1: ~15-20 días** → viable en julio-agosto con foco.

### P2 · Para el piloto Fuentecillas (Q1 2027)

| # | Funcionalidad | Trabajo Django | Estimación |
|---|---|---|---|
| 2.1 | Permutas de turno + saldo horario + horas médicas cod. 23 (feedback Laura 17/06) | Modelos Permuta + SaldoHorario en `equipo` + flujo aceptación compañera → V.º B.º dirección | 4-5 días |
| 2.2 | Cuadrante OR-Tools integrado (el motor ya es Python real) | Modelo Cuadrante + comando de generación + vista de publicación | 4-6 días |
| 2.3 | Dinero de bolsillo (arqueos inmutables — decisión 01) | App `bolsillo`: Movimiento + Arqueo + firmas | 4-5 días |
| 2.4 | Espacios de Trabajo Social (ficha derivación, informe social, comunicación de baja) | Modelos + forms + PDF (peticiones Uxue 17/06) | 4-5 días |

### P3 · Post-piloto (2027)

| # | Funcionalidad | Nota |
|---|---|---|
| 3.1 | Áreas transversales Empleo (2 CEE, 13 líneas) y Ocio/Cultura/Deporte | Requiere decisión de frontera con proyecto EQUIPO — documentar antes (Regla 3) |
| 3.2 | Facturación (decisión 02) | Puede convivir con proceso actual |
| 3.3 | Ratio del centro (Resolución 21/09/2023) | Calculadora demo suficiente por ahora |
| 3.4 | Resto de escalas psicológicas (ABS-RC:2, INICO-FEAPS autoinforme…) | Según demanda de casos puntuales |

---

## Regla de trabajo desde hoy

**Toda pantalla nueva de la demo genera en el mismo día su línea en este backlog.**
La demo sigue siendo la herramienta de validación rápida, pero la brecha queda siempre
inventariada y estimada. Revisión quincenal de prioridades con Gerencia.

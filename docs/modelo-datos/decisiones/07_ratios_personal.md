# Decisión 07 · Ratios de personal y cálculo de plantilla

**Fecha**: 2026-06-17
**Estado**: Aprobada
**Sponsor**: Federico Martínez · Gerencia

---

## Marco normativo aplicable

### Resolución 21 sept 2023 — Gerencia Servicios Sociales CyL
**BOCYL 29/09/2023** · Vigencia obligatoria desde **01/10/2023** para centros concertados.

#### B.2 · Ratio conjunta (residencias 24h con ≥60% G2/G3)
> *Para los centros residenciales que por sí mismos o complementariamente con centros de día garanticen la ATENCIÓN COMPLETA 24 HORAS AL DÍA y que cuenten con el 60% o más de usuarios con reconocimiento de grado de dependencia 2 o 3, la ratio conjunta de profesionales de atención directa y de profesionales técnicos deberá ser, en jornadas completas contratadas, el resultado de multiplicar en número de usuarios que tenga el centro en cada momento multiplicado por el factor 0,50.*

```
RATIO CONJUNTA = nº usuarios × 0,50
```

#### B.3.1 · Gestor de caso
> *Se deberá contar con un profesional técnico con formación universitaria, gestor de caso de un máximo de 30 personas usuarias de residencia o de centro de día.*

```
GESTORES = ceil(nº usuarios / 30)
```

#### B.3.4 · Ratios atención directa diurna (suma por grado)
> *La ratio de profesionales de atención directa DURANTE EL HORARIO DIURNO SERÁ la suma, en jornadas completas contratadas, del resultado de multiplicar en número de usuarios de cada tipología por su propio factor.*

| Grado dependencia · modalidad | Factor |
|---|---:|
| Grado 0 o 1 · moderado/ligero | **0,066** |
| Grado 2 · dependiente severo | **0,125** |
| Grado 3 · gran dependiente | **0,200** |

```
ATENCIÓN DIRECTA DIURNA = (G0-1 × 0,066) + (G2 × 0,125) + (G3 × 0,200)
```

> Se tendrá en cuenta el primer decimal del resultado.

### Ley 1/2024 CyL — Apoyo al proyecto de vida
**BOE-A-2024-4289** del 05/03/2024.

Prestaciones esenciales que el sistema de servicios sociales debe garantizar:

| Prestación | Destinatarios |
|---|---|
| **Apoyo para la activación del proyecto de vida** | Dificultades funcionales, psicosociales o vulnerabilidad social |
| **Asistencia personal** | Personas con discapacidad en situación de dependencia |
| **Apoyo a la capacidad jurídica** | Conforme a Ley 8/2021 (curatela, guarda de hecho) |

Prestación NO esencial: apoyo familiar para la promoción de la autonomía personal.

**Metodología (Art. 22)**: trabajo cooperativo + profesional de referencia (interlocución, seguimiento, coordinación) + profesional de gestión + profesional de atención directa.

### Ley 2/2013 CyL — Igualdad de Oportunidades
Marco general de derechos. Establece el principio de **inclusión** y **continuidad de cuidados**.

### Convención ONU 2006 (art. 19)
Derecho a vivir de forma independiente y a ser incluido en la comunidad.

---

## Decisión técnica para ÁGORA

### Mínimo legal exigible

```python
def minimo_legal_exigible(centro):
    b34 = sum_atencion_directa_diurna(centro.usuarios_por_grado)
    if centro.atencion_24h and centro.pct_g2_g3 >= 60:
        b2 = centro.plazas * 0.50
        return max(ceil(b34), ceil(b2))
    return ceil(b34)
```

### Coeficiente de complejidad (propio ÁGORA)

El **mínimo legal** captura el grado de dependencia pero NO captura otros factores que aumentan la carga asistencial. ÁGORA introduce un coeficiente 0-100 con ponderación interna:

| Variable | Peso | Origen del dato |
|---|---:|---|
| Problemas de conducta graves | 30 | ICAP sección E · ABS-RC:2 Parte 2 |
| Cuidados sanitarios complejos (≥5 pautas activas) | 25 | PautaMedicacion |
| Movilidad reducida / silla de ruedas | 20 | InformacionMedica.movilidad |
| Conductas autolesivas / heteroagresivas | 25 | ICAP autolesivo + heteroagresividad |

```
RATIO RECOMENDADA = MÍNIMO LEGAL × (1 + COEFICIENTE / 100)
```

Esta ratio recomendada **no obliga** pero permite a la dirección del centro defender frente a Junta CyL una plantilla por encima del mínimo legal cuando el perfil real lo requiera.

### Distribución por turno

Estándar del sector sociosanitario:

| Turno | % plantilla | Horario | Justificación |
|---|---:|---|---|
| Mañana | 55% | 07:00-15:00 | Pico AVD: aseo, comida, terapias, salidas |
| Tarde | 30% | 15:00-23:00 | Actividades, merienda, ocio, cena |
| Noche | 15% | 23:00-07:00 | Supervisión + atención puntual |

---

## Implicaciones en el modelo de datos

| Modelo | Cambio | Fase |
|---|---|---|
| `Centro` | + campo `atencion_24h` (bool) | v0.15 |
| `PersonaAtendida` | + `grado_dependencia` mapeado a (0, 1, 2, 3) | ya existe |
| Nuevo modelo `RatioCalculo` | snapshot mensual: mínimo legal, recomendado ÁGORA, plantilla actual, coeficiente complejidad | v0.15 |
| Nuevo modelo `JustificacionPlantilla` | PDF para Junta CyL con datos auditados | v0.15 |

---

## Trazabilidad

- Fuentes: `RESOLU~1.PDF` (FSIE CyL), `Ley+22013.pdf`, `BOE-A-2024-4289.pdf`, `CAP+07+ACT+20.pdf` recibidas 17/06/2026.
- Maqueta funcional: `demo/ratio-centro.html`.
- Próxima validación: Operaciones + Dirección Fuentecillas (Sprint 2 implementación backend).

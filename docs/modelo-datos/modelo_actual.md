# Modelo de datos v0.12 — Alojamiento físico

**Estado**: v0.12 · pendiente de migración · pendiente validación de Federico.
**Origen del cambio**: requerimiento expreso de Federico — "aquellas personas que tengan servicios de residencia o vivienda deberán tener identificado el módulo, la habitación y la cama".
**Sustituye / amplía**: v0.11.

---

## Resumen

Se añade la jerarquía de **alojamiento físico** para servicios residenciales y de vivienda. Solo aplica a esos servicios; los centros de día, ocupacionales, CEE o inserción laboral **no** usan este bloque.

```
Centro ──┬── Módulo (opcional) ──┬── Habitación ──┬── Cama ──┬── OcupacionCama (histórico)
                                                              │
                                                              └──► PersonaAtendida (vigente: ocupacion_cama_actual)
```

---

## Modelos nuevos (4)

### `Modulo`
- FK a `Centro`
- `codigo` único por centro, `nombre`, `descripcion`
- Agrupación física: planta, ala, unidad de convivencia
- Opcional: viviendas pequeñas pueden no tener módulos
- Inspecciones JCyL: el modelo de unidades de convivencia (Ley 3/2024 CyL) encaja aquí

### `Habitacion`
- FK a `Centro` (siempre) + FK a `Modulo` (opcional)
- `numero` único por centro (p. ej. "101", "B-3", "Verde")
- Tipo: individual / doble / triple / cuádruple
- `superficie_m2`, `con_bano_propio`, `adaptada_movilidad_reducida` (PMR)

### `Cama`
- FK a `Habitacion`
- `identificador` único por habitación (A, B, 1, 2…)
- Atributos físicos: `articulada`, `barandillas`, `grua_compatible`
- `activa` (False si está fuera de servicio)
- Property `ocupacion_actual` y `esta_libre`

### `OcupacionCama`
- FK persona + FK cama + fecha_inicio + fecha_fin
- `motivo_alta` y `motivo_baja` (9 choices: inicial, traslado interno, reforma, convivencia, necesidades apoyo, salida, hospitalización, fallecimiento, otro)
- **Constraints DB**:
  - Una sola ocupación activa por persona (`UniqueConstraint` con `Q(fecha_fin__isnull=True)`)
  - Una sola ocupación activa por cama
- Histórico completo: nunca se borran ocupaciones, se cierran con `fecha_fin`

---

## Ampliaciones

### `PersonaAtendida`
Nuevas properties (sin campos DB):
- `ocupacion_cama_actual` — query optimizado con select_related para evitar N+1
- `ubicacion_residencial` — texto "Módulo X · Habitación Y · Cama Z" listo para UI

### `Centro`
Properties de ocupación útiles para Indicadores y Control PV:
- `plazas_totales` — camas activas
- `plazas_ocupadas` — con ocupación vigente
- `plazas_libres`
- `porcentaje_ocupacion` (0-100, una decimal)

---

## Casos de uso cubiertos

1. **Saber dónde duerme una persona ahora**:
   `persona.ocupacion_cama_actual` → cama + habitación + módulo + centro

2. **Cambiar a una persona de cama**:
   - Cerrar ocupación actual: `fecha_fin = hoy`, `motivo_baja`
   - Crear nueva `OcupacionCama` con `motivo_alta = TRASLADO_INTERNO`

3. **Histórico de habitaciones de una persona**:
   `persona.ocupaciones_cama.order_by('-fecha_inicio')`

4. **Ocupación de un centro**:
   - `centro.plazas_libres` — para alta de nueva persona
   - `centro.porcentaje_ocupacion` — para cuadro de mando

5. **Saber quién comparte habitación con quién**:
   ```python
   compañeros = OcupacionCama.objects.filter(
       cama__habitacion=hab,
       fecha_fin__isnull=True,
   ).exclude(persona=p)
   ```

6. **Listado de camas libres**:
   ```python
   Cama.objects.filter(
       activa=True, habitacion__activa=True
   ).exclude(
       ocupaciones__fecha_fin__isnull=True
   )
   ```

---

## Consideraciones operativas

### Sujeciones físicas (Norma Libera-Care)
- `Cama.barandillas = True` **no** equivale a "sujeción". Las barandillas pueden tener finalidad asistencial sin restricción.
- Cuando una cama con barandillas se usa como medida de sujeción, se registra como tal en el módulo de Sujeciones (Fase 3 · M2), que apunta a esta cama.

### Inspecciones y Ley 3/2024 CyL
- Unidades de convivencia: máx. 12-15 personas → se modela con `Modulo`
- Plazo 2029 para adecuar arquitectura → ÁGORA facilita la auditoría con `centro.porcentaje_ocupacion` y por módulo

### Privacidad RGPD
- "Quién comparte habitación con quién" es dato sensible (riesgo de inferir condición sociosanitaria)
- Acceso restringido al rol asistencial del propio centro
- Bitácora obligatoria al consultar mapas de ocupación entre centros

### Demo
- `persona-detalle.html` muestra el dato en 3 sitios:
  1. Línea bajo el nombre en el banner: "FUE-2026-00001 · Residencia Fuentecillas · 🛏 Módulo Norte · Hab. 24 · Cama B"
  2. En el resumen rápido: bloque con compañera de habitación
  3. En "Datos personales y discapacidad": tarjeta con histórico de ocupación

---

## Tareas pendientes

1. Vista de **mapa de ocupación** por centro (cuadrícula de habitaciones/camas con colores)
2. Comando `cargar_datos_sinteticos`: generar módulos/habitaciones/camas para los centros residenciales de demo
3. Validación: al asignar `PersonaAtendida.centro_referencia` a un centro residencial, exigir crear `OcupacionCama` antes de fin de jornada (warning, no bloqueante)
4. Indicador de ocupación en el cuadro de mando general (`indicadores.html`)
5. Permiso especial para "mover persona de cama" — operación delicada que pide motivo

---

*v0.12 — 2026-05-19*

# Modelo de datos v0.11 — Ficha clínica, familia y medicación

**Estado**: v0.11 · pendiente de migración · pendiente validación de Federico.
**Origen del cambio**: análisis de la estructura del Odoo legado a partir de los exports de campo proporcionados (datos personales, médicos, familiares y medicamentos). Se reproduce la estructura, **no los datos** — RGPD.
**Sustituye / amplía**: v0.10.

---

## Resumen

La ficha de persona atendida pasa de tener una única vista plana a estar organizada en **5 pestañas**:

| Pestaña UI | Bloques de datos | Modelos implicados |
|---|---|---|
| Resumen | identificación rápida, accesos, notas | `PersonaAtendida` |
| Datos personales y discapacidad | datos administrativos sanitarios, certificado de discapacidad, reconocimiento de dependencia, medidas de apoyo Ley 8/2021 | `PersonaAtendida`, `CertificadoDiscapacidad`, `ReconocimientoDependencia`, `MedidaDeApoyo` |
| Información médica | datos clínicos básicos, alergias, enfermedades crónicas, antropometría, vacunación, cuidados de enfermería, problemas de salud | `InformacionMedica`, `Alergia`, `EnfermedadCronica`, `MedidaAntropometrica`, `Vacuna`, `CuidadoEnfermeria`, `ProblemaSalud` |
| Familiares | familiares con datos completos, marca CERCA, contacto emergencia, figura de apoyo | `PersonaContacto`, `VinculoPersonaContacto`, `FiguraDeApoyo` |
| Medicación | catálogo de medicamentos, pautas activas e histórico | `Medicamento`, `PautaMedicacion` |

---

## Modelos NUEVOS

### 1. `CertificadoDiscapacidad`
- FK a `PersonaAtendida` (histórico — varios por persona)
- `grado_pct`, `puntos_factores_sociales`, `puntos_movilidad_reducida`
- `tipo_reconocimiento` (permanente / revisable), `fecha_validez_hasta`
- `diagnostico_principal` + `diagnosticos_secundarios` (texto, normalizar en v1.0)
- `documento_pdf` (acceso restringido)
- Flag `vigente` — solo uno activo por persona

### 2. `ReconocimientoDependencia`
- FK a `PersonaAtendida` (histórico)
- `grado` (I/II/III/no dependiente), `puntos_bvd`, `tipo_dependencia`
- Fechas: solicitud, resolución, próxima revisión
- `tipo_beneficio` (plaza residencial, centro día, SAD, teleasistencia, prestación económica)
- `servicio_concertado` (texto descriptivo)

### 3. `InformacionMedica` (1-1)
- Grupo sanguíneo (choices)
- `vacunacion_permitida` + `motivo_no_vacunacion`
- Contacto médico de referencia externo
- Antecedentes familiares
- Bloque dieta: tipo, textura alimentos, textura líquidos, observaciones
- **Datos de categoría especial RGPD art. 9** — acceso solo a rol clínico

### 4. `Alergia`
- Tipos: medicamentosa, alimentaria, ambiental, contacto, intolerancia, otra
- Gravedad: leve / moderada / grave / anafiláctica
- Visible **siempre** que cualquier profesional abra la ficha (alerta de seguridad)

### 5. `EnfermedadCronica`
- Nombre, fecha diagnóstico, especialista referente, en seguimiento

### 6. `MedidaAntropometrica`
- Peso, talla, IMC (auto-calculado), TA sistólica/diastólica, pulso, temperatura, saturación O2, glucemia
- Histórico por fecha — un registro por toma
- Registrado por: FK a `Profesional`

### 7. `Vacuna`
- Vacuna, fecha, dosis, estacional (bool), lote, centro de administración

### 8. `CuidadoEnfermeria` (1-1)
- Documento vivo estructurado en 10 dimensiones:
  - respiración, audición, visión, alimentación, sueño y descanso,
    eliminación, movilidad, autonomía ABVD, conducta, cuidados de la piel
- Histórico vía `updated_at` + `updated_by`; en v1.0 con `django-simple-history`

### 9. `ProblemaSalud`
- Problema clínico bajo seguimiento, con tipo, especialista externo y responsable interno
- Estado: abierto / en seguimiento / resuelto / derivado
- FK opcional desde `PautaMedicacion` (justifica la prescripción)

### 10. `Medicamento` (catálogo compartido)
- Nombre comercial, principio activo, dosis, familia farmacológica, vía administración
- 20 familias farmacológicas predefinidas
- 12 vías de administración predefinidas
- Único por `(nombre_comercial, dosis)`

### 11. `PautaMedicacion`
- FK persona + FK medicamento
- Dosificación **D-C-N + acostarse + si precisa** en columnas separadas (mejor que el "1/2-0-1/2" del Odoo legado)
- `pauta_especial` para casos no encajables (p. ej. "el día 1 de cada mes")
- Fechas inicio/fin, motivo finalización (7 choices), prescriptor
- FK opcional a `ProblemaSalud` (trazabilidad clínica)
- **No** registra cada toma individual — eso es módulo Enfermería (M2 Fase 3)
- Propiedad `dosificacion_texto` para presentación legible

---

## Modelos AMPLIADOS

### `PersonaAtendida`
- `numero_seguridad_social` (NUSS, cifrado)
- `numero_tarjeta_sanitaria` (TSI, cifrado)
- `tsi_caducidad` (alerta automática 90 días antes — v1.0)
- `centro_salud` (SACYL)
- `forma_comunicacion_preferente` (telefónica / email / SMS / presencial / CERCA)
- `idioma_preferente` (ISO 639-1)
- `usa_saac` + `saac_notas` (Sistema Aumentativo/Alternativo de Comunicación)

### `PersonaContacto`
- `fecha_nacimiento`
- `telefono_fijo` + `movil` (separados; el legacy `telefono` se mantiene deprecado y se elimina en v1.0)
- Dirección postal completa (4 campos)
- Propiedad `telefono_principal` (móvil > fijo > legacy)

### `VinculoPersonaContacto`
- `es_emergencia` + `orden_emergencia` (1, 2, 3… para escalado)
- `notificable_cerca` + `fecha_alta_cerca` (consentimiento auditable)

### `MedidaDeApoyo` (Ley 8/2021)
- `subtipo_curatela` (representativa total/parcial, asistencial, defensor judicial, guarda de hecho)
- `organo_judicial` + `numero_procedimiento`
- `es_curatela_entidad` (bool) — si la ejerce una entidad en lugar de persona física
- `persona_curadora` (FK a `PersonaContacto`)
- `entidad_curadora` (texto, cuando aplique)
- `proxima_revision_at` (Ley 8/2021 art. 268: revisión máx. cada 3 años)

---

## Consideraciones RGPD

### Categoría especial (art. 9 RGPD)
Los siguientes modelos contienen **datos de salud**:
- `InformacionMedica`, `Alergia`, `EnfermedadCronica`, `MedidaAntropometrica`,
  `Vacuna`, `CuidadoEnfermeria`, `ProblemaSalud`, `Medicamento`, `PautaMedicacion`

Implicaciones:
1. **Acceso restringido por rol clínico** (DUE, médico, psicólogo) + la propia persona y su figura de apoyo
2. **Bitácora obligatoria** (art. 32) en cada lectura
3. **Cifrado en reposo** de NUSS, TSI y campos clínicos sensibles
4. **Consentimiento explícito** (art. 9.2.a) en alta + base jurídica de prestación de servicios sociosanitarios (art. 6.1.b + 9.2.h)
5. **Retención**: durante la atención + 5 años (defensa legal). Documentado en `docs/rgpd/retencion.md` (pendiente).
6. **EIPD**: este bloque obliga a actualizar la EIPD inicial (lo recoge Lex Digital).

### Minimización
Cada nuevo campo tiene `help_text` documentando su finalidad. Si un campo no es necesario para el servicio sociosanitario, debe eliminarse antes de pasar a producción.

### Documentos sensibles
- `CertificadoDiscapacidad.documento_pdf` y `ReconocimientoDependencia.documento_pdf`
  van a `media/` con permisos restringidos. Ruta privada, no servida estáticamente.

---

## Migración

Como aún no se ha generado la `0001_initial.py`, todos estos cambios entran
en la **migración inicial** cuando se ejecute `makemigrations personas`.

Si la migración inicial ya existiera, este cambio sería una migración nueva
funcional (no squash hasta Fase 2, según CLAUDE.md).

---

## Tareas pendientes (no incluidas en este cambio)

1. Formularios HTML (`personas/forms.py`) para las 4 pestañas nuevas
2. Vistas HTMX para edición inline (`personas/views.py`)
3. Templates Django (`templates/personas/persona_detalle.html` con tabs)
4. Permisos granulares por rol clínico (signals + middleware) — toca `core/`
5. Cifrado de NUSS y TSI a nivel aplicación (django-cryptography o equivalente)
6. Comando de carga sintética actualizado (`cargar_datos_sinteticos`) con los nuevos modelos
7. Tests pytest mínimos por cada modelo nuevo
8. EIPD actualizada (responsable: Lex Digital + administración Aspanias)

---

*v0.11 — 2026-05-19*

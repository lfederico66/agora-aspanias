# Módulo FIS — Fichas de Intervención y Seguimiento (Incidencias)

**Fecha**: 2026-06-04
**Fuente**: `Informe_Integracion_FIS_Agora.pdf` v1.0 (Gerencia + Sistemas N. Olmos)
**Estado**: Validada · pendiente de implementar en backend
**Sustituye**: formulario móvil FIS actual (variantes naranja / verde / morado)

---

## 1. Decisión

Integrar el FIS como **módulo de Incidencias** de cada centro dentro de ÁGORA, con:

- **Acceso muy visible** en la cabecera del inicio del centro (un solo clic para alta).
- **Modelo de datos común** con variantes por tipo de centro (color naranja/verde/morado).
- **Ciclo de vida completo**: Abierta → En curso → Cerrada.
- **Vinculación automática** al usuario y al centro/ámbito.
- **Notificación al responsable** cuando se abre una incidencia de salud crítica.

## 2. Alcance · centros y variantes

| Centro / servicio | Tipo | Variante |
|---|---|---|
| Centro de día Quintanadueñas | Centro de día | 🟧 Naranja (día) |
| A mi ritmo | CD ocupacional | 🟧 Naranja (día) |
| Centro de día Puentesaúco | Centro de día | 🟧 Naranja (= CD QD) |
| Vicente Aleixandre | CD multiactividad | 🟧 Naranja (= CD QD) |
| Residencia Puentesaúco | Residencia | 🟩 Verde (residencia) |
| Residencia Fuentecillas | Residencia | 🟩 Verde (residencia) |
| Servicio Puentes | Residencia | 🟩 Verde |
| Unidad asistencial (Quintanadueñas, Salas) | Residencia/UA | 🟩 Verde |
| Viviendas Asocia · Fuentecillas · Vida Independiente · Áreas | Viviendas | 🟪 Morado (vivienda) |
| AGC | Pendiente confirmar | — |

## 3. Modelo Django

```python
class VarianteFIS(models.TextChoices):
    DIA = "DIA", "Centro de día / ocupacional (naranja)"
    RESIDENCIA = "RES", "Residencia / U. asistencial (verde)"
    VIVIENDA = "VIV", "Vivienda (morado)"

class TurnoFIS(models.TextChoices):
    MAÑANA = "MAN", "Mañana"
    TARDE = "TAR", "Tarde"
    NOCHE = "NOC", "Noche"
    DIA = "DIA", "Día"

class EstadoIncidencia(models.TextChoices):
    ABIERTA = "ABI", "Abierta"
    EN_CURSO = "CUR", "En curso"
    CERRADA = "CER", "Cerrada"

class TipoActividadPIA(models.TextChoices):
    PROFESIONAL = "PROF", "Actividad profesional"
    INDIVIDUAL = "IND", "Atención/Actividad individual"
    GRUPAL = "GRP", "Actividad grupal"


class AmbitoFIS(models.Model):
    """Talleres, áreas, direcciones de vivienda… parametrizado por centro."""
    centro = models.ForeignKey("personas.Centro", on_delete=models.PROTECT,
                              related_name="ambitos_fis")
    codigo = models.CharField(max_length=30)
    nombre = models.CharField(max_length=200)
    activo = models.BooleanField(default=True)


class ActividadFIS(models.Model):
    """Catálogo maestro de actividades/tareas. Marcable por tipo de centro."""
    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=200)
    aplica_dia = models.BooleanField(default=False)
    aplica_residencia = models.BooleanField(default=False)
    aplica_vivienda = models.BooleanField(default=False)
    es_salud = models.BooleanField(default=False,
        help_text="Si es 'Salud · Detección, Incidente, Accidente' u otra crítica → notificación automática")
    activo = models.BooleanField(default=True)


class IncidenciaFIS(models.Model):
    """Ficha de Intervención y Seguimiento (FIS) integrada como incidencia."""
    centro = models.ForeignKey("personas.Centro", on_delete=models.PROTECT,
                              related_name="incidencias_fis")
    variante = models.CharField(max_length=3, choices=VarianteFIS.choices)
    fecha = models.DateField(default=timezone.now)
    turno = models.CharField(max_length=3, choices=TurnoFIS.choices, blank=True,
        help_text="Obligatorio en residencias y viviendas. Vacío en CD.")
    ambito = models.ForeignKey(AmbitoFIS, on_delete=models.PROTECT)

    # Vínculo al usuario (puede estar vacío en CD si la actividad es grupal genérica)
    usuario = models.ForeignKey("personas.PersonaAtendida",
                                on_delete=models.PROTECT, null=True, blank=True,
                                related_name="incidencias_fis")
    participantes = models.ManyToManyField("personas.PersonaAtendida",
                                          blank=True,
                                          related_name="incidencias_fis_participadas")

    actividades = models.ManyToManyField(ActividadFIS, related_name="incidencias")

    deteccion = models.TextField(help_text="Descripción de lo detectado / de la incidencia")
    intervencion = models.TextField(blank=True, help_text="Actuación realizada")
    valoracion = models.CharField(max_length=200, blank=True)

    actividad_pia = models.BooleanField(default=False, verbose_name="¿Es actividad del PIA?")
    tipo_actividad_pia = models.CharField(max_length=4,
                                          choices=TipoActividadPIA.choices,
                                          blank=True)

    # Ciclo de vida
    estado = models.CharField(max_length=3, choices=EstadoIncidencia.choices,
                              default=EstadoIncidencia.ABIERTA)
    motivo_cierre = models.TextField(blank=True)
    cerrada_en = models.DateTimeField(null=True, blank=True)
    cerrada_por = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.PROTECT, null=True,
                                    related_name="incidencias_cerradas")

    # Auditoría
    creada_por = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.PROTECT,
                                   related_name="incidencias_creadas")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AdjuntoFIS(models.Model):
    incidencia = models.ForeignKey(IncidenciaFIS, on_delete=models.CASCADE,
                                   related_name="adjuntos")
    archivo = models.FileField(upload_to="fis/%Y/%m/")
    descripcion = models.CharField(max_length=200, blank=True)
    subido_por = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
```

## 4. Permisos por rol (RF-09, RGPD art. 9)

| Rol | Crear | Ver | Editar estado | Recibir avisos | Cierre | Catálogo |
|---|---|---|---|---|---|---|
| Profesional asistencial | ✓ su centro | ✓ su centro | ✗ | si está asignado | ✗ | ✗ |
| Coordinador/a del centro | ✓ | ✓ su centro | ✓ | ✓ | ✓ | ✗ |
| Calidad / Operaciones | ✗ | ✓ todos (lectura) | ✗ | ✗ | ✗ | ✗ |
| Administración / Sistemas | ✓ | ✓ todos | ✓ | ✗ | ✓ | ✓ edita |
| Gerencia | ✗ | ✓ todos (cuadro de mando) | ✗ | escala salud | ✗ | ✗ |

## 5. RGPD (datos de salud · categoría especial art. 9)

- ✅ Minimización · solo lo necesario para la intervención y su seguimiento
- ✅ Control de acceso por rol y centro · acceso a datos de salud solo personal autorizado
- ✅ Bitácora obligatoria · usuario, IP, timestamp, operación
- ✅ Cifrado en tránsito y en reposo
- ✅ Inclusión en el RAT y revisión por el DPO
- ✅ Política de conservación conforme normativa sociosanitaria CyL

## 6. Implementación en la demo

Como adelanto visual antes de la implementación en backend:

- `centro-detalle.html` → **bloque destacado** en la cabecera (color por variante)
- `incidencias-fis.html` → **bandeja del centro** con filtros y ciclo de vida
- `nueva-ficha-fis.html` → **formulario** con variantes por color
- Sidebar → ítem **🚨 Incidencias FIS**

## 7. Plan de implementación (Fase 3 — pre-piloto sept 2026)

| # | Tarea | Esfuerzo |
|---|---|---|
| 1 | Modelo Django + migración (6 modelos) | 2 días |
| 2 | Importar catálogos de actividades por centro | 1 día |
| 3 | Importar ámbitos vigentes desde cada centro | 1 día |
| 4 | Vistas: bandeja por centro + formulario por variante | 4 días |
| 5 | Widget de inicio del centro (bloque destacado) | 1 día |
| 6 | Ciclo de vida + notificaciones salud crítica | 2 días |
| 7 | Cuadro de mando agregado (Calidad / Gerencia) | 2 días |
| 8 | Tests + EIPD ampliada (datos salud cat. especial) | 2 días |
| 9 | Mobile responsive (alta desde móvil como FIS actual) | 1 día |
| **Total** | | **~16 días** |

## 8. Decisiones / datos pendientes

- [ ] Confirmar si AGC utiliza el FIS y su variante
- [ ] Recoger plantillas vigentes de cada centro (Fase 0)
- [ ] Validar catálogo único de ACTIVIDADES Y TAREAS (consolidar)
- [ ] Definir valores de VALORACIÓN
- [ ] Criterios de notificación automática: qué tipos avisan y a quién (escalar salud crítica)
- [ ] Política de conservación con el DPO

---

*Basado en informe FIS v1.0 (Gerencia + Sistemas) 4/6/2026.*

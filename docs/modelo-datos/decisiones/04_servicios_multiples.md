# Decisión de modelo: servicios múltiples por persona

**Fecha**: 2026-06-01
**Decisor**: Federico Martínez (Gerencia)
**Estado**: Validada — pendiente de implementar en backend

---

## Contexto

Hasta ahora, el modelo `PersonaAtendida` tenía una sola relación con `Centro`
(campo FK obligatorio). La práctica real del Grupo Social Aspanias muestra
que una misma persona puede recibir servicio en varios centros simultáneamente:

- **Ejemplo 1**: Persona reside en *Residencia Puentesaúco* (DI) y por
  la mañana acude al *Centro de Día Quintanadueñas* para
  actividades ocupacionales.
- **Ejemplo 2**: Persona que vive en *Áreas de Vivienda* (vivienda tutelada)
  y asiste al *Centro Multiactividad V. Aleixandre* entre semana.
- **Ejemplo 3** (caso de Marta González en la demo): Residencia en *Centro
  Integral Fuentecillas* + Centro de día complementario en *CD Aspanias
  Puentesaúco*.

## Decisión

Cambiar la relación `PersonaAtendida ↔ Centro` de **1:N a M:N**, mediante una
tabla intermedia `ServicioAsignado` con metadatos.

### Nuevo modelo `ServicioAsignado`

```python
class Modalidad(models.TextChoices):
    RESIDENCIAL = "RES", "Residencial"
    CENTRO_DIA = "CD", "Centro de día"
    CENTRO_DIA_ASIST = "CDA", "Centro de día asistencial"
    VIVIENDA = "VIV", "Vivienda tutelada"
    EDUCATIVO = "EDU", "Centro educativo"
    INSERCION = "INS", "Inserción / autonomía"

class TipoVinculo(models.TextChoices):
    PRINCIPAL = "PRINC", "Principal"
    COMPLEMENTARIO = "COMPL", "Complementario"


class ServicioAsignado(models.Model):
    persona = models.ForeignKey(
        "personas.PersonaAtendida",
        on_delete=models.CASCADE,
        related_name="servicios",
        verbose_name="persona atendida",
    )
    centro = models.ForeignKey(
        "personas.Centro",
        on_delete=models.PROTECT,
        related_name="servicios_asignados",
        verbose_name="centro",
    )
    modalidad = models.CharField(
        max_length=5,
        choices=Modalidad.choices,
        verbose_name="modalidad",
    )
    vinculo = models.CharField(
        max_length=6,
        choices=TipoVinculo.choices,
        default=TipoVinculo.PRINCIPAL,
        help_text="Marca si es el servicio principal (1 por persona) o complementario",
    )
    fecha_alta = models.DateField(verbose_name="fecha de alta en el servicio")
    fecha_baja = models.DateField(
        null=True, blank=True,
        verbose_name="fecha de baja",
        help_text="Si está vacío, el servicio sigue activo",
    )
    horario_descripcion = models.CharField(
        max_length=255, blank=True,
        help_text="Ej: 'L-V 09:00-17:00' o 'estancia 24h'",
    )

    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="servicios_creados",
        null=True,
    )

    class Meta:
        verbose_name = "servicio asignado"
        verbose_name_plural = "servicios asignados"
        constraints = [
            # Solo 1 servicio PRINCIPAL activo por persona
            models.UniqueConstraint(
                fields=["persona"],
                condition=models.Q(vinculo="PRINC", fecha_baja__isnull=True),
                name="unico_servicio_principal_activo",
            ),
            # No solapamiento de servicios idénticos
            models.UniqueConstraint(
                fields=["persona", "centro", "modalidad"],
                condition=models.Q(fecha_baja__isnull=True),
                name="sin_duplicar_servicio_activo",
            ),
        ]
```

### Cambios en `PersonaAtendida`

- **Eliminar** los campos `centro` (FK directo) y `modalidad` (CharField).
- **Mantener** los datos de alojamiento físico (`Modulo`/`Habitacion`/`Cama`)
  que ya existen, pero asociarlos al servicio **principal residencial**, no
  a la persona directamente.

### Cambios en `Centro`

Añadir un campo `tipos_servicio` (M2M con un nuevo catálogo) para indicar
qué modalidades ofrece. Por ejemplo:

- **Residencia Fuentecillas** → ofrece `RES` + `CD` (residencia +
  centro de día bajo el mismo techo).
- **Residencia Río Arlanza** → solo `RES`.
- **CD Puentesaúco** → solo `CD`.
- **CD Asistencial Quintanadueñas** → solo `CDA`.

## Implicaciones en vistas e indicadores

| Vista                         | Cambio                                                                                                                |
|-------------------------------|------------------------------------------------------------------------------------------------------------------------|
| Ficha de persona              | Mostrar lista de servicios asignados (no un único centro). Resaltar el principal.                                     |
| Detalle de centro             | Listar las personas con un servicio en ese centro. Si el centro ofrece varias modalidades (Fuentecillas), permitir filtrar. |
| Mapa de ocupación             | Cuenta solo plazas residenciales (modalidad `RES`). El % de ocupación se calcula sobre las plazas físicas (camas).   |
| Cuadro de mando               | `Personas atendidas` = personas únicas (DISTINCT). `Servicios prestados` = suma de servicios activos. Diferenciar.   |
| Control PV por servicio       | El PV es **por persona**, no por servicio. Una persona con 2 servicios sigue teniendo 1 PV.                          |
| Importador Excel              | El campo `Centro` del Excel histórico se mapea al servicio principal. Se generan servicios complementarios manualmente. |

## Migración de datos

1. **Crear** modelo `ServicioAsignado`.
2. **Backfill**: para cada `PersonaAtendida` con `centro` definido, crear un
   `ServicioAsignado` con `vinculo=PRINC`, `modalidad` derivada del tipo
   actual del centro, `fecha_alta=fecha_ingreso` y `fecha_baja=null`.
3. **Eliminar** los campos `centro` y `modalidad` de `PersonaAtendida` (una
   vez verificado que el backfill cubre 100% de las personas).
4. **Generar fixture** de ejemplos de personas con 2 servicios (5-10 casos
   en datos sintéticos para validar la UI).

## Impacto en RGPD / bitácora

- Cada `ServicioAsignado` debe quedar registrado en la bitácora cuando se
  crea, modifica o se da de baja.
- El permiso de acceso a la persona se calcula como `OR` de los permisos
  de acceso a sus servicios activos. Es decir: si un profesional tiene
  acceso al *CD Puentesaúco*, puede ver la ficha de Marta (que está allí)
  aunque su residencia principal sea Fuentecillas.

## Pendiente para implementar

- [ ] Crear app o modelo `servicios/` con `ServicioAsignado` (decidir si
      va en `personas/` o en una nueva app).
- [ ] Migración con backfill.
- [ ] Actualizar formularios admin / formularios web de alta de persona.
- [ ] Reescribir vista `centro_detalle` para filtrar por modalidad.
- [ ] Reescribir vista `persona_detalle` para mostrar lista de servicios.
- [ ] Tests de modelo (constraints + casos de uso).
- [ ] Documentar en EIPD el nuevo flujo de datos.

---

*Documento generado en sesión de diseño 2026-06-01 con Federico.*

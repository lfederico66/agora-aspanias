# Módulo "Facturación y servicios extraordinarios" — propuesta

**Fecha**: 2026-06-04
**Origen**: Informe del Departamento Económico Financiero (Sonia Ureta, Dori González) sobre la carpeta FAB/2026
**Estado**: propuesta · pendiente de validación por Federico + Económico-Financiero
**Sustituye**: archivos Excel `01.2026.xlsx` a `12.2026.xlsx` y carpetas Intecum / Agusto

---

## 1. Resumen ejecutivo

El Dpto. Económico-Financiero gestiona hoy con **un libro Excel mensual** la facturación de:

| Hoja | Contenido | Centros implicados |
|---|---|---|
| **FAB-GNRAL** | Facturación habitual (plaza) | Todos |
| **SPAP-PUENTES** | Facturación Puentesaúco | Puentesaúco |
| **SPAP)** | Facturación adicional | — |
| **ATT EXTRA FUENTEC** | Servicios extras Fuentecillas | Fuentecillas |
| **ATT EXTRA VIV.** | Servicios extras viviendas | Áreas de Vivienda |
| **ATT EXTRA G3** | Servicios extras Resi Puentesaúco | Residencia Puentesaúco |
| **ATT EXTRA SALAS** | Servicios extras Salas | Resi y CD Salas |
| **ATT EXTRA QTÑAS** | Servicios extras Quintanadueñas | Resi/CD/UA Quintanadueñas |
| **EDUCACION** | Comedor / transporte / madrugadores | Colegio EE Puentesaúco |
| **AGUSTO-INTECUM** | Facturación específica | Intecum + Agusto |

Total: **10 hojas × 12 meses × varios años** = mucho Excel · mucha posibilidad de error.

---

## 2. Análisis crítico del proceso actual

| Problema | Impacto |
|---|---|
| Hojas Excel separadas por centro y mes | Doble entrada de datos · sin centralización |
| Sin catálogo de servicios homologado | Cada centro usa nombres propios → conciliación manual |
| Sin trazabilidad de quién registró cada servicio | No hay bitácora · pérdida de evidencia |
| Tarifas hardcoded en celdas | Cambio de tarifa = revisar mes × centro |
| Conciliación FAB-GNRAL + ATT EXTRA manual | Lento y propenso a omisiones |
| Sin export a SAGE / Contaplus / lo que use Económico | Doble trabajo en factura final |

---

## 3. Encaje con el módulo existente "Caja y bolsillos"

Los dos módulos NO son lo mismo, son complementarios:

| Módulo | Qué controla | A quién factura |
|---|---|---|
| **Caja y bolsillos** (ya hecho) | Efectivo físico del centro + peculio individual | Sin facturación · solo conciliación interna |
| **Facturación** (esta propuesta) | Servicios prestados al usuario | Familia / Administración Pública / mutua |

Comparten: vinculación a `PersonaAtendida` + `Centro`. Pero los importes circulan por canales distintos.

---

## 4. Modelo Django propuesto

```python
class UnidadMedida(models.TextChoices):
    HORA = "H", "Hora"
    KILOMETRO = "KM", "Kilómetro"
    DIA = "D", "Día"
    MES = "M", "Mes"
    VIAJE = "V", "Viaje ida-vuelta"
    UNIDAD = "U", "Unidad (fijo)"

class TipoServicio(models.Model):
    """Catálogo de servicios facturables · parametrizado por centro."""
    centro = models.ForeignKey(
        "personas.Centro", on_delete=models.PROTECT,
        related_name="tipos_servicio",
    )
    codigo = models.CharField(max_length=20, help_text="Código corto interno")
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    unidad = models.CharField(max_length=2, choices=UnidadMedida.choices)
    es_extraordinario = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "tipo de servicio"
        constraints = [
            models.UniqueConstraint(
                fields=["centro", "codigo"],
                name="codigo_unico_por_centro",
            ),
        ]


class TarifaVigente(models.Model):
    """Histórico de tarifas por tipo de servicio."""
    tipo_servicio = models.ForeignKey(
        TipoServicio, on_delete=models.PROTECT,
        related_name="tarifas",
    )
    importe = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    motivo = models.TextField(blank=True, help_text="Revisión anual / acuerdo Junta CyL...")

    class Meta:
        ordering = ["-fecha_inicio"]


class ServicioPrestado(models.Model):
    """Cada registro de servicio facturable a una persona."""
    persona = models.ForeignKey(
        "personas.PersonaAtendida", on_delete=models.PROTECT,
        related_name="servicios_facturados",
    )
    centro = models.ForeignKey(
        "personas.Centro", on_delete=models.PROTECT,
    )
    tipo_servicio = models.ForeignKey(
        TipoServicio, on_delete=models.PROTECT,
    )
    fecha = models.DateField()
    descripcion = models.CharField(max_length=255, blank=True,
        help_text="Ej.: 'Endocrino HUBU 05/06/2026'")
    unidades = models.DecimalField(max_digits=8, decimal_places=2)
    tarifa_aplicada = models.DecimalField(max_digits=10, decimal_places=2,
        help_text="Tarifa snapshot al registrar")
    importe = models.DecimalField(max_digits=10, decimal_places=2,
        help_text="unidades × tarifa, calculado")
    observaciones = models.TextField(blank=True)

    # Estado de facturación
    factura = models.ForeignKey(
        "FacturaMensual", on_delete=models.PROTECT, null=True, blank=True,
        related_name="servicios",
    )

    # Auditoría
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FacturaMensual(models.Model):
    """Factura consolidada por persona y mes (habitual + extraordinarios)."""
    persona = models.ForeignKey("personas.PersonaAtendida", on_delete=models.PROTECT)
    centro = models.ForeignKey("personas.Centro", on_delete=models.PROTECT)
    periodo_inicio = models.DateField()
    periodo_fin = models.DateField()
    importe_habitual = models.DecimalField(max_digits=10, decimal_places=2)
    importe_extraordinarios = models.DecimalField(max_digits=10, decimal_places=2)
    importe_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(
        max_length=10,
        choices=[("BORR", "Borrador"), ("CERR", "Cerrada"), ("EMIT", "Emitida"), ("PAG", "Pagada")],
        default="BORR",
    )
    cuenta_bancaria_destino = models.CharField(max_length=34, blank=True,
        help_text="IBAN de la persona o representante legal")
    fichero_emitido_url = models.URLField(blank=True,
        help_text="Enlace al fichero contable generado (SAGE / Contaplus)")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["persona", "periodo_inicio", "periodo_fin"],
                name="factura_unica_por_persona_y_periodo",
            ),
        ]
```

---

## 5. Pantallas propuestas

### 5.1 Nuevo tab en `centro-detalle.html`: "💼 Facturación"
- KPI mes en curso: nº servicios extraordinarios · importe total · pendientes de facturar
- Tabla mensual de servicios extras del centro (filtros: persona, tipo, fecha)
- Botón "+ Nuevo servicio extraordinario" (catálogo desplegable del propio centro)
- Mini-catálogo del centro con sus tarifas vigentes y enlace a edición

### 5.2 Nueva sección global "Facturación" (sidebar, rol Administración)
- **Mensual**: cuadrícula meses × centros con totales facturados
- **Catálogo de servicios**: edición de tipos y tarifas (por centro)
- **Conciliación**: vista que cruza FAB-GNRAL + ATT EXTRA por usuario
- **Exportación**: genera el Excel en el formato que necesita Sonia/Dori
  (compatibilidad con el flujo actual mientras se valida)

### 5.3 Sub-tab en `persona-detalle.html`
Dentro del tab "💰 Dinero de bolsillo" → un segundo sub-tab "💼 Facturación del mes" con los servicios prestados que se le facturarán.

---

## 6. Catálogo inicial de servicios (sembrar al implantar)

Extraído del informe:

| Centro | Servicio | Unidad | Tarifa (≈) |
|---|---|---|---|
| Todos | Acompañamiento médico | Hora | 14-15 € |
| Todos | Acompañamiento a urgencias | Hora | 14,20 € |
| Todos | Acompañamiento a juzgados | Hora | (a definir) |
| Salas | Endocrino, Ecografía, Radiografía, Otorrino, Salud Mental, Neumología | Hora + km | variable |
| Todos | Kilometraje | Viaje | 25 € |
| Todos | Viaje ida-vuelta | Viaje | 80,96 € |
| Fuentecillas | Podología | Sesión | 15 € |
| Quintanadueñas | Atención fin de semana / cierre | Día | variable |
| Todos | Pago delegado | Unidad | variable |
| Colegio Puentesaúco | Comedor | Mes o día | 95 € / 6 € |
| Colegio Puentesaúco | Transporte | Mes | 75 € |
| Colegio Puentesaúco | Madrugadores | Mes o día | 25 € / 4 € |
| Colegio Puentesaúco | Continuadores | Mes o día | mismo |

---

## 7. Permisos y RGPD

| Rol | Ver servicios | Registrar servicios | Cerrar factura | Editar catálogo |
|---|---|---|---|---|
| Coordinador/a del centro | ✓ su centro | ✓ | ✗ | ✗ |
| Profesional asistencial | — | ✓ (de su sesión) | ✗ | ✗ |
| Administración (Sonia, Dori) | ✓ todos | ✓ | ✓ | ✓ |
| Familia | ✓ su familiar (resumen) | ✗ | ✗ | ✗ |

- Cada movimiento queda en **bitácora** (usuario, IP, timestamp).
- Los importes son **datos personales sensibles** (revelan capacidad económica).
- La EIPD se amplía con un capítulo "Tratamiento de datos económicos de facturación".
- La conservación se ajusta a la **normativa fiscal**: 6 años para libros y facturas (LGT 66 → 4 años + 2 prevención).

---

## 8. Encaje en el calendario del proyecto

| Fase | Cuándo | Qué se aborda |
|---|---|---|
| Fase 3 (pre-piloto, sept 2026) | **Reunión con Sonia + Dori** para confirmar requisitos exactos · validar catálogo | — |
| Fase 4 (piloto Fuentecillas Q1 2027) | NO incluir todavía · el piloto se centra en atención asistencial | — |
| **Fase 4.5 (Q2-Q3 2027)** | **Implementación del módulo Facturación** · pruebas en Fuentecillas | Modelos + vistas + importador FAB.xlsx |
| Fase 5 (despliegue 2027-29) | Extender a todos los centros | Catálogo por centro · sustitución de Excel |

Justificación: incorporar la facturación en el piloto Q1 2027 multiplica el riesgo del piloto. Es mejor consolidar la parte asistencial primero, demostrar valor, y entonces incorporar el módulo económico.

---

## 9. Recomendación

**SÍ incorporar el módulo, pero como Fase 4.5** (Q2-Q3 2027), no antes.

Razones:
1. ✅ **Necesidad real demostrada**: el Dpto. Económico-Financiero ya identifica las ineficiencias y pide la solución.
2. ✅ **Encaja con el modelo de datos** de ÁGORA (PersonaAtendida + Centro ya existen).
3. ✅ **Reduce errores** y aporta trazabilidad para auditoría.
4. ⚠️ **Aumenta el alcance** del proyecto y requiere integración con software contable (SAGE/Contaplus). Hay que mapear el flujo end-to-end con Sonia/Dori antes.
5. ⚠️ **No es prioritario para el Patronato 10/06**: el piloto Fuentecillas Q1 2027 es lo que se aprueba ahora.

---

## 10. Plan de implementación (cuando llegue Fase 4.5)

| # | Tarea | Esfuerzo |
|---|---|---|
| 1 | Reunión con Sonia + Dori para detalle del flujo end-to-end | 0,5 día |
| 2 | Modelos Django (5 modelos) + migración | 2 días |
| 3 | Importador FAB.xlsx → ÁGORA (1 vez, en migración inicial) | 2 días |
| 4 | Tab "Facturación" en centro-detalle | 2 días |
| 5 | Sección global "Facturación" para Administración | 3 días |
| 6 | Exportador al formato Excel actual (compatibilidad) | 1 día |
| 7 | Permisos por rol + bitácora | 1 día |
| 8 | Tests + EIPD ampliada | 2 días |
| **Total** | | **~14 días** |

---

## 11. Pendientes para Federico

- [ ] Validar la propuesta global con Sonia Ureta y Dori González
- [ ] Confirmar el calendario (Fase 4.5 — Q2 2027)
- [ ] ¿Existe software contable actual que ÁGORA debe alimentar? (SAGE, Contaplus, A3…)
- [ ] ¿La facturación de **Intecum** y **Agusto** la maneja Aspanias o son entidades separadas?
- [ ] ¿Los IBAN de cuenta bancaria están todos centralizados en algún lugar o se piden caso a caso?

---

*Análisis basado en el informe del Dpto. Económico-Financiero (4/6/2026). Sin acceso al Excel real (RGPD).*

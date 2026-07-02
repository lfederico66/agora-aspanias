# Módulo "Dinero de bolsillo" — propuesta de diseño

**Fecha**: 2026-06-01
**Origen**: Excel CGPR 2025 (gestión actual manual)
**Estado**: propuesta · pendiente de validación por Federico
**Sustituye**: `CGPR 2025.xlsx` y libros similares de los demás centros

---

## Objetivo

Digitalizar la gestión del **dinero de bolsillo** (peculio) de las personas atendidas y la **caja del centro**, con conciliación periódica y trazabilidad de cada movimiento.

## Alcance funcional

### 1. Cuenta individual (peculio) — por persona

| Campo | Tipo | Notas |
|---|---|---|
| Fecha movimiento | date | Obligatorio |
| Concepto | text | Catálogo + libre |
| Ingreso (€) | decimal | uno de los dos |
| Gasto (€) | decimal | uno de los dos |
| Saldo acumulado | decimal | calculado |
| Justificante | file/img | foto del tique o factura |
| Categoría | choice | Aseo · Ocio · Ropa · Tabaco · Familia · Otros |
| Registrado por | FK User | obligatorio |
| Observaciones | text | libre |

### 2. Caja del centro — por centro

Movimientos generales no atribuibles a una persona (compras comunes, reposiciones, gastos del centro). Mismos campos pero sin `PersonaAtendida`.

### 3. Arqueo mensual

- Cierre periódico (mensual por defecto, configurable)
- Foto de saldos individuales + caja del centro
- Comparación con **efectivo físico** introducido por el responsable
- **Diferencia** → si ≠ 0, motivo obligatorio y se firma digitalmente
- Una vez cerrado: bloqueo de movimientos del periodo (rol Administración puede reabrir)

### 4. Permisos

| Rol | Ver propio | Ver todos | Crear movimiento | Cerrar arqueo |
|---|---|---|---|---|
| Profesional asistencial | ✓ (de su persona) | ✗ | ✓ con visto bueno | ✗ |
| Coordinador/a centro | ✓ | ✓ (su centro) | ✓ | ✓ |
| Administración | ✓ | ✓ todos | ✓ | ✓ + reapertura |
| Familia / referente legal | ✓ (su familiar) | ✗ | ✗ | ✗ |

## Modelo Django

```python
class CuentaBolsillo(models.Model):
    """Cuenta de peculio de una persona atendida (1:1)."""
    persona = models.OneToOneField(
        "personas.PersonaAtendida",
        on_delete=models.CASCADE,
        related_name="cuenta_bolsillo",
    )
    activa = models.BooleanField(default=True)
    saldo_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_apertura = models.DateField()
    notas = models.TextField(blank=True)

    @property
    def saldo_actual(self):
        from django.db.models import Sum
        ingresos = self.movimientos.aggregate(Sum("ingreso"))["ingreso__sum"] or 0
        gastos = self.movimientos.aggregate(Sum("gasto"))["gasto__sum"] or 0
        return self.saldo_inicial + ingresos - gastos


class CategoriaMovimiento(models.TextChoices):
    ASEO = "ASE", "Aseo personal"
    OCIO = "OCI", "Ocio y salidas"
    ROPA = "ROP", "Ropa y calzado"
    TABACO = "TAB", "Tabaco"
    FAMILIA = "FAM", "Familia (transferencia)"
    PENSION = "PEN", "Pensión / paga"
    SANIDAD = "SAN", "Farmacia / sanidad"
    OTROS = "OTR", "Otros"


class MovimientoBolsillo(models.Model):
    """Cada entrada o salida de la cuenta de una persona."""
    cuenta = models.ForeignKey(
        CuentaBolsillo, on_delete=models.PROTECT, related_name="movimientos"
    )
    fecha = models.DateField()
    concepto = models.CharField(max_length=200)
    categoria = models.CharField(max_length=3, choices=CategoriaMovimiento.choices)
    ingreso = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gasto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    justificante = models.ImageField(upload_to="bolsillo/%Y/%m/", null=True, blank=True)
    observaciones = models.TextField(blank=True)

    # Auditoría
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="movimientos_registrados",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Cierre de arqueo: si está vinculado a un arqueo cerrado, el movimiento es inmutable
    arqueo = models.ForeignKey(
        "ArqueoMensual", on_delete=models.PROTECT, null=True, blank=True,
        related_name="movimientos_bolsillo",
    )

    class Meta:
        ordering = ["-fecha", "-created_at"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(ingreso__gte=0) & models.Q(gasto__gte=0),
                name="bolsillo_importes_no_negativos",
            ),
            models.CheckConstraint(
                check=(models.Q(ingreso__gt=0) & models.Q(gasto=0)) |
                      (models.Q(ingreso=0) & models.Q(gasto__gt=0)),
                name="bolsillo_solo_uno_de_ingreso_o_gasto",
            ),
        ]


class CajaCentro(models.Model):
    """Caja física del centro."""
    centro = models.OneToOneField(
        "personas.Centro", on_delete=models.CASCADE, related_name="caja",
    )
    saldo_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    activa = models.BooleanField(default=True)


class MovimientoCaja(models.Model):
    """Movimientos de la caja del centro (no atribuibles a una persona)."""
    caja = models.ForeignKey(
        CajaCentro, on_delete=models.PROTECT, related_name="movimientos"
    )
    fecha = models.DateField()
    concepto = models.CharField(max_length=200)
    ingreso = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gasto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    justificante = models.ImageField(upload_to="caja/%Y/%m/", null=True, blank=True)
    observaciones = models.TextField(blank=True)
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    arqueo = models.ForeignKey(
        "ArqueoMensual", on_delete=models.PROTECT, null=True, blank=True,
        related_name="movimientos_caja",
    )


class ArqueoMensual(models.Model):
    """Cierre periódico de cuentas con conciliación física."""
    centro = models.ForeignKey("personas.Centro", on_delete=models.PROTECT)
    periodo_inicio = models.DateField()
    periodo_fin = models.DateField()
    saldo_caja_libro = models.DecimalField(max_digits=10, decimal_places=2)
    saldo_caja_fisico = models.DecimalField(max_digits=10, decimal_places=2)
    suma_bolsillos_libro = models.DecimalField(max_digits=10, decimal_places=2)
    suma_bolsillos_fisico = models.DecimalField(max_digits=10, decimal_places=2)
    diferencia = models.DecimalField(max_digits=10, decimal_places=2)
    motivo_diferencia = models.TextField(blank=True)

    cerrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
    )
    cerrado_en = models.DateTimeField()
    reabierto = models.BooleanField(default=False)
    reabierto_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True,
        related_name="arqueos_reabiertos",
    )
    motivo_reapertura = models.TextField(blank=True)

    class Meta:
        ordering = ["-periodo_fin"]
        constraints = [
            models.UniqueConstraint(
                fields=["centro", "periodo_inicio", "periodo_fin"],
                name="arqueo_unico_por_centro_periodo",
            ),
        ]
```

## Vistas

### Tab nuevo en `persona-detalle.html`: **"💰 Dinero de bolsillo"**

- KPI grandes: Saldo actual · Ingresos del mes · Gastos del mes
- Tabla de movimientos (los 20 últimos por defecto, paginada)
- Filtros: por categoría, rango fechas, tipo (ingreso/gasto)
- Botón **+ Nuevo movimiento** con formulario (fecha · concepto · categoría · ingreso/gasto · justificante)
- Cuando el movimiento está vinculado a un arqueo cerrado, aparece bloqueado (icono candado)

### Nueva página: **`caja-centro.html`**

Vista accesible desde el centro (botón en `centro-detalle.html`) o desde el sidebar como atajo de Administración:

- Estado actual de la caja: saldo · última actualización
- Tabla de movimientos del centro
- Tabla resumen de saldos individuales del centro (todos los bolsillos de personas del centro)
- Botón **🔒 Cerrar arqueo del periodo** → abre asistente

### Asistente de arqueo (modal o página)

1. Confirma periodo (mes en curso por defecto)
2. Muestra saldo libro de la caja + saldos individuales
3. Pide importes físicos contados (caja + sumatorio de bolsillos)
4. Calcula diferencia · si ≠ 0 pide motivo obligatorio
5. Firma digital + cierre

## Bitácora y RGPD

- Cada movimiento queda en bitácora con: usuario · IP · timestamp · operación (alta/edición/anulación)
- Las cantidades son **datos personales** (revelan capacidad económica) → permiso por rol estricto
- Los justificantes (fotos de tique) **no pueden contener** nada que identifique más allá de la persona ya identificada
- En la EIPD se añade un capítulo "Tratamiento de datos económicos del peculio"

## Importación inicial

Para migrar de Excel a ÁGORA en la puesta en marcha:

- Comando `import_cgpr <archivo>.xlsx <centro_id>`
- Crea `CuentaBolsillo` para cada hoja individual del libro
- Crea `MovimientoBolsillo` para cada fila de movimiento
- Crea `CajaCentro` + `MovimientoCaja` para las hojas generales
- Genera un `ArqueoMensual` consolidado a fecha de migración

## Plan

| # | Tarea | Esfuerzo |
|---|---|---|
| 1 | Maqueta HTML tab "Dinero de bolsillo" en persona | 1 día |
| 2 | Maqueta HTML página "Caja del centro" | 1 día |
| 3 | Modelos Django + migración | 1 día |
| 4 | Vistas + formularios HTMX | 3 días |
| 5 | Asistente de arqueo | 2 días |
| 6 | Comando de importación CGPR.xlsx | 2 días |
| 7 | Permisos por rol + bitácora | 1 día |
| 8 | Tests | 2 días |
| 9 | Doc EIPD ampliada | 0,5 día |

**Total estimado: ~14 días** para implementación completa.

---

*Documento para validación.*

# Migración del Excel "Registro PV por servicios" del Grupo Aspanias

Documento operativo para el equipo de **Sistemas Aspanias + Innovación Aspanias** que ejecutará la importación cuando ÁGORA esté desplegado.

---

## 1. Archivos involucrados

- **Original**: `Registro PV por servicios. Global Grupo Aspanias.xlsx` (debe vivir en SharePoint corporativo cifrado, **NO** en `Downloads/`).
- **Pseudonimizado**: `Registro PV por servicios. Global Grupo Aspanias_PSEUDO.xlsx` (para pruebas y desarrollo, datos ficticios).
- **Pseudonimizador**: `scripts/pseudonimizar_excel_pv.py`.
- **Importador**: `python manage.py importar_excel_registro_pv ...`.
- **Prueba en seco**: `python scripts/prueba_seco_importador.py "ruta.xlsx"`.

---

## 2. Flujo de migración recomendado

### Paso 1 — Pre-validación en seco

Sin tocar la base de datos, revisar qué importaría:

```bash
python scripts/prueba_seco_importador.py "ruta\\al\\Registro_PSEUDO.xlsx"
```

Output esperado: tabla con 13 centros, conteo de personas por hoja, PV realizados, profesionales únicos. Si los números encajan razonablemente con la hoja "Datos Grupo Aspanias" del Excel, pasar al siguiente paso.

### Paso 2 — Importación simulada en BD (`--dry-run`)

Con Docker arrancado y ÁGORA funcionando:

```bash
docker compose -f infraestructura/docker-compose.yml exec web \
  python manage.py importar_excel_registro_pv \
  "/data/Registro_PSEUDO.xlsx" --anualidad 2026 --dry-run
```

Reporte de:
- Centros creados / existentes
- Personas atendidas creadas / actualizadas
- Profesionales creados
- Planes de Vida creados / actualizados
- Errores

### Paso 3 — Importación real

Solo cuando el dry-run reporte 0 errores y números coherentes:

```bash
docker compose -f infraestructura/docker-compose.yml exec web \
  python manage.py importar_excel_registro_pv \
  "/data/Registro_PSEUDO.xlsx" --anualidad 2026
```

Tras la importación:
1. Abrir `/personas/` y verificar lista poblada.
2. Abrir `/planes-vida/control/` y verificar los 13 centros con sus datos.
3. Abrir `/indicadores/planes-vida/` y comparar con la hoja "Datos Grupo Aspanias" del Excel.

### Paso 4 — Snapshot inicial

```bash
docker compose -f infraestructura/docker-compose.yml exec web \
  python manage.py generar_snapshot_planes_vida --etiqueta "Snapshot inicial post-importación"
```

Esto crea el primer registro histórico, equivalente a la hoja "Histórico" del Excel.

---

## 3. Mapeo de centros

| Hoja Excel | Código ÁGORA | Nombre canonico | Corresponsable |
|---|---|---|---|
| Res. Quint. | RES_QUINT | Residencia y UA Quintanadueñas | FAB |
| CD Quint. | CD_QUINT | Centro Ocupacional Quintanadueñas | FAB |
| Vicente Aleixandre | VICENTE | Centro Multiactividad Vicente Aleixandre | FAB |
| Puentesauco | RES_PUENTESAUCO | Residencia Puentesauco (RHP) | Aspaniasmerc |
| Salas | SAL | Residencia y Centro de Día Salas | Aspaniasmerc |
| Fuentecillas | FUE | Centro Mayores Fuentecillas | FAB |
| Puentes | PUENTES | Servicio de Vida Independiente | FAB |
| CD Puentesauco | CD_PUENTESAUCO | Centro Ocupacional Puentesauco | Aspaniasmerc |
| Río Arlanza | LAR | Residencia Río Arlanza | FAB |
| Santa Mª | SANTA_M | Residencia Santa María | FAB |
| Viviendas Puentesauco | VIV_PUENTESAUCO | Viviendas Puentesauco | Aspaniasmerc |
| Viviendas Asociación | VIV_ASOC | Viviendas Asociación | FAB |
| Viviendas Fuentecillas | VIV_FUE | Viviendas Fuentecillas | FAB |

⚠ **Pendiente de confirmación gerencial** los corresponsables de: Santa María, Viviendas Puentesauco, Viviendas Asociación.

---

## 4. Hallazgos a tener en cuenta

Detectados durante la prueba en seco (2026-05-18) contra el archivo pseudonimizado:

### 4.1 Duplicación entre servicios
Una misma persona aparece en varias hojas (residencia + centro de día + vivienda). El importador deduplica por **nombre + primer apellido**.
- Total filas en las 13 hojas: 673
- Personas únicas estimadas: ~614 (parser) / 383 (según "Datos Grupo Aspanias")
- La diferencia entre 614 y 383 sugiere que algunas personas tienen variantes de nombre/grafía entre hojas. Conviene revisar las dudas manualmente tras la importación.

### 4.2 Columna "Estado revisión"
No tiene formato uniforme entre centros:
- Algunos centros la usan con valores "En plazo / Fuera de plazo / Pendiente".
- Otros centros la usan para anotar **fechas concretas** (próxima revisión).
- Algunos contienen **notas libres** ("SE TRASLADA A [persona] 1/12/25").

El importador interpreta:
- Texto que contiene "fuera" → `estado_revision = fuera_plazo`
- Texto que contiene "plazo" → `estado_revision = en_plazo`
- Cualquier otra cosa → `estado_revision = pendiente`

**Consecuencia**: el indicador "PV fuera de plazo" puede salir bajo en la primera importación. Tras la importación, los gestores deben **rellenar manualmente el campo** en ÁGORA para que cuadre con el Excel.

### 4.3 Profesionales únicos
El parser detecta 250 nombres únicos en columnas de Gestor/a o Persona de Referencia.
- 30 son los gestores principales (según hoja "Gestores de caso").
- 220 son personas de referencia (no aparecen en esa hoja).

Todos se crearían como `Profesional` con email autogenerado tipo `nombre.apellido@aspaniasburgos.com`. **Antes del SSO M365 real, esos emails son placeholder** — habrá que sincronizarlos con los emails reales de Entra ID al desplegar.

### 4.4 Filas inválidas
Detectadas 3 filas con nombre incompleto (una palabra). Se descartan automáticamente. Reportarlas a Dirección para que las complete antes de re-importar.

---

## 5. Lista de verificación post-importación

Marcar manualmente tras ejecutar la importación real:

- [ ] `/personas/` muestra ~383 personas activas
- [ ] `/planes-vida/control/` muestra los 13 centros con datos coherentes
- [ ] `/indicadores/planes-vida/` reporta KPIs comparables a la hoja "Datos Grupo Aspanias"
- [ ] `/indicadores/gestores-caso/` muestra ~30 gestores con su carga
- [ ] Bitácora `/admin/core/registroacceso/` registra la acción de importación masiva
- [ ] Snapshot inicial creado con la etiqueta de fecha

---

## 6. Rollback

Si algo va mal:
- El comando entero corre dentro de una **transacción atómica** Django. Si falla en mitad, hace `rollback` automático.
- Con `--dry-run`, además se fuerza el rollback al final.
- Para deshacer una importación exitosa que después se demuestra incorrecta: `python manage.py flush` borra **toda** la BD (peligroso) o restaurar desde backup.

Recomendación: **antes de cada importación real**, hacer backup de la BD con `pg_dump` y guardarlo cifrado.

---

*Documento v1.0 — generado tras la prueba en seco del parser. Actualizar cuando se ejecute la primera importación real en producción.*

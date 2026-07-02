# Migración del Excel legado de Planes de Vida a ÁGORA

Este documento describe cómo migrar el Excel compartido que hoy usan los gestores/as de caso (§7 del protocolo) al sistema ÁGORA.

---

## 1. Resumen

El protocolo indica que existe un **Excel compartido** con:
- Centros
- Gestores/as
- Estado del plan
- Fecha de revisión
- Alertas de renovación

ÁGORA incluye un **comando de importación** que toma ese Excel y crea/actualiza Planes de Vida (anualidad indicada) con los datos correspondientes, vinculándolos a personas atendidas y profesionales ya existentes en ÁGORA.

> El Excel legado se mantiene operativo en paralelo a ÁGORA solo hasta cerrar el piloto. Tras el go-live, **ÁGORA es la fuente única**.

---

## 2. Flujo recomendado

### Paso 1 — Generar plantilla en blanco
```bash
python manage.py importar_excel_planes_vida --generar-plantilla salida/plantilla_agora.xlsx
```

Esto produce un archivo `.xlsx` con dos hojas:
- **Seguimiento**: cabeceras con estilo + fila 2 de ejemplo en gris cursiva.
- **Instrucciones**: tabla descriptiva de cada columna + comando de uso al final.

### Paso 2 — Rellenar con datos del Excel actual
El/la gestor/a abre la plantilla, **borra la fila 2 de ejemplo** y copia/pega los datos del Excel existente respetando las cabeceras esperadas.

### Paso 3 — Importación simulada (`--dry-run`)
```bash
python manage.py importar_excel_planes_vida ruta/al/excel.xlsx --anualidad 2026 --dry-run
```

Esto reporta cuántos planes se crearían/actualizarían, cuántas personas faltan en ÁGORA, y los errores. **No toca la base de datos.**

### Paso 4 — Importación real
```bash
python manage.py importar_excel_planes_vida ruta/al/excel.xlsx --anualidad 2026
```

Crea/actualiza dentro de una transacción atómica. Si algo falla, no queda nada a medias.

---

## 3. Formato esperado del Excel

Hoja **"Seguimiento"** con cabeceras en fila 1 (orden no importa) y una fila por persona desde la fila 2.

| Columna | Obligatoria | Formato | Descripción |
|---|---|---|---|
| `codigo_persona` | Sí | `FUE-2026-00001` | Código interno ÁGORA de la persona. Debe existir previamente en ÁGORA. |
| `centro` | Sí | `FUE` / `LAR` / `SAL` / `VIL` / `CEE` | Código corto del centro. |
| `gestor_email` | Sí | `gestora@aspaniasburgos.com` | Email M365 del Gestor/a de Caso (Protocolo §2.1). |
| `referencia_email` | Sí | `referencia@aspaniasburgos.com` | Email M365 de la Persona de Referencia (Protocolo §2.2). |
| `estado` | Sí | `vigente` / `en_revision` / `en_elaboracion` / `archivado` | Estado actual del Plan. |
| `fecha_revision` | No | `dd/mm/aaaa` o `aaaa-mm-dd` | Última revisión anual realizada. |
| `proxima_revision` | No | `dd/mm/aaaa` o `aaaa-mm-dd` | Próxima revisión prevista. |
| `alerta` | No | Texto libre | Alertas, observaciones, renovación pendiente. |
| `doc_historia_vida` | No | URL | Enlace al documento 1 en Teams/OneDrive. |
| `doc_algo_sobre_mi` | No | URL | Enlace al documento 2. |
| `doc_revision_objetivos` | No | URL | Enlace al documento 3. |
| `doc_plan_apoyo` | No | URL | Enlace al documento 4. |
| `doc_proyecto_vida` | No | URL | Enlace al documento 5. |

---

## 4. Qué hace el importador

Por cada fila del Excel:
1. Busca la persona por `codigo_persona`. Si no existe → cuenta en "sin persona" y continúa.
2. Busca el gestor/a y persona de referencia por email M365. Si no existen → quedan como `null` (Dirección los asignará después).
3. **Crea o actualiza** el `PlanDeVida` para la anualidad indicada con estado, fechas, alertas y profesionales.
4. Si hay URLs de documentos, crea/actualiza `DocumentoPlanDeVida` por cada uno marcándolos como `COMPLETADO` y publicados en REPRISS si son Proyecto de Vida o Plan de Apoyo.

---

## 5. Prerrequisitos

Antes de ejecutar el importador, asegurarse de que en ÁGORA existen:
- ✅ **Personas atendidas** con su `codigo_interno` correcto.
- ✅ **Centros** dados de alta con su código (`FUE`, `LAR`, `SAL`, `VIL`, `CEE`).
- ✅ **Profesionales** (Gestores/as y Personas de Referencia) con su email M365 registrado.

Los tres se cargan con `cargar_datos_sinteticos` en demo. En producción se cargarán con SSO M365 al primer login + alta manual desde el admin o desde el formulario `/personas/nueva/`.

---

## 6. ⚠ RGPD — buenas prácticas

- El Excel legado contiene **datos personales reales** (DNI, nombres, salud).
- **NO** subir nunca el Excel al repositorio git.
- Procesar desde una **ruta local fuera del repo**, idealmente desde una carpeta cifrada.
- Tras la importación exitosa, mover el Excel a **archivo histórico cifrado** (SharePoint corporativo con cifrado en reposo). Mantenerlo en `Downloads/` o `Escritorio/` no es aceptable.
- La importación queda registrada en la **bitácora** de ÁGORA (cada movimiento masivo aparece como acción del usuario que ejecutó el comando).

---

## 7. Plan de retirada del Excel legado

Una vez la importación sea exitosa y los profesionales empiecen a editar Planes de Vida directamente en ÁGORA:

1. **Mes 1 (julio 2026)**: ÁGORA y Excel conviven; ÁGORA es opcional.
2. **Mes 2 (agosto 2026)**: cualquier dato nuevo entra solo en ÁGORA. Excel queda en modo "solo lectura".
3. **Mes 3 (septiembre 2026, go-live piloto)**: Excel se archiva. ÁGORA es la fuente única.
4. **Diciembre 2026**: tras 3 meses de funcionamiento sin incidencias, se elimina el Excel del SharePoint compartido (queda copia en archivo histórico cifrado mínimo 7 años por retención sociosanitaria).

---

*Documento v1.0 — generado tras la implementación del importador en ÁGORA v0.9.*

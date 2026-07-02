# scripts/ — Índice

Dos subcarpetas con propósitos distintos:

## `utilidades/` — Scripts reutilizables

| Script | Para qué sirve |
|---|---|
| `build_demo.py` | **★ Sistema de includes para sidebar + tokens**. Inyecta `demo/_partials/sidebar.html` en los 38 HTMLs y sustituye `{{tokens}}` desde `demo/_partials/datos.json`. Editar el sidebar o las cifras institucionales = 1 archivo + 1 comando. |
| `check_gobernanza.py` | **★ Linter de las 3 reglas UX** (CLAUDE.md): R1 7±2 en tabs · R2 `@rol` declarado por HTML · R3 sin acentos en código. Integrado en CI. Modo `--fix` inserta `@rol gerencia` por defecto. |
| `auditar_demo.py` | Revisa coherencia de los HTMLs de `demo/` (sidebar, breadcrumbs, scripts). Útil tras refactors. |
| `pseudonimizar_excel_pv.py` | Anonimiza un Excel del Registro PV antes de subirlo al repo (RGPD). |
| `prueba_seco_importador.py` | Ejecuta el importador en modo `dry-run` contra un Excel pseudonimizado. |
| `generar_mapa_interactivo.py` | Construye el SVG del mapa de ocupación de un centro residencial. |
| `analizar_cgpr_estructura.py` | Análisis sanitizado de la estructura de un Excel CGPR (sin datos personales). |
| `limpiar_comentarios_django.py` | Convierte comentarios `{# ... #}` Django en `<!-- -->` HTML para vistas estáticas. |
| `lanzar_claude.bat` | Atajo Windows para abrir Claude Code en el repo. |
| `arranque_local.md` | Pasos rápidos para arrancar el entorno local. |
| `reorganizacion_log.csv` | Log de la reorganización de junio 2026 (aplicada por la skill ordenador-archivos). |
| `deshacer_reorganizacion.ps1` | Script generado automáticamente que revierte la reorganización si fuera necesario. |

## `historico/` — One-shots ya consumidos

Scripts puntuales ejecutados durante refactors del demo. **Ya cumplieron su función** y se conservan como referencia. **No hace falta volver a ejecutarlos** salvo que se necesite reproducir el mismo cambio en una rama nueva.

Categorías:

- `fix_*.py` — parches puntuales (backslashes, breadcrumbs, modales, etc.)
- `refactor_*.py` — refactors estructurales (sidebar v2, nombres de centros, conteos, nav)
- `rebrand_sipas_to_agora.py` — cambio de nombre SIPAS → ÁGORA (mayo 2026)
- `reinsertar_tabs_familia_medico.py`, `rellenar_tabs_persona.py`, `redisenar_personas_lista.py` — adaptaciones puntuales de la ficha persona
- `aplicar_shell_ux.py`, `add_generar_factura.py`, `reordenar_tabla_centro.py` — ediciones masivas one-shot

## `reorganizar_repo.ps1`

Script de la reorganización aplicada por la skill `ordenador-archivos` (jun 2026). Se conserva en la raíz de `scripts/` para que sea reejecutable si se necesita.

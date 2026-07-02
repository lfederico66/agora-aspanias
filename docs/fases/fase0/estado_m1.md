# Estado del MVP M1 — informe para comité del viernes

**Fecha**: 2026-05-13
**Hito objetivo**: piloto Centro Fuentecillas, Q3 2026.

## Qué hay funcional en código (Django, no solo mockup)

| Módulo | Estado | Vista usuario |
|---|---|---|
| Personas atendidas (ficha única + 4 perfiles + Ley 8/2021 + familia) | ✅ Implementado | `/personas/` |
| Plan Individual de Atención (PIA / AICP) | ✅ Implementado | `/pia/persona/<id>/` |
| Historial de intervenciones | ✅ Implementado con filtro por rango | `/intervenciones/persona/<id>/` |
| Agenda multiprofesional semanal | ✅ Implementado con navegación semana | `/agenda/` |
| Cuadro de mando de indicadores | ✅ Implementado con cálculo en vivo | `/indicadores/` |
| Bitácora de accesos (art. 32 RGPD) | ✅ Operativa, registra automático las 5 rutas | admin: `/admin/core/registroacceso/` |
| Admin Django para los 12 modelos M1 | ✅ Listo con inlines, filtros y búsqueda | `/admin/` |
| Datos sintéticos extendidos (personas + PIA + intervenciones + citas + indicadores) | ✅ Comando `cargar_datos_sinteticos` | `make datos-sinteticos` |

## Qué queda para piloto Q3 2026

1. **SSO Microsoft 365** real (esquema configurado, falta registrar la app en Entra ID y rellenar credenciales).
2. **RBAC operativo por centro** (esqueleto en `core/permissions.py`, falta integrar con vistas y plantillas).
3. **Cifrado de DNI/NIE a nivel aplicación** (campo presente, lógica de cifrado pendiente).
4. **Firma electrónica del PIA** (modelo lo soporta, integración pendiente).
5. **Migración de datos del Odoo legado** (mapeo pendiente — bloqueante para sustitución completa).
6. **Notificación a familia vía CERCA** (flag operativo, integración con CERCA pendiente).
7. **Tailwind con build en lugar de CDN** (rendimiento + offline).
8. **Pentest pre-piloto**.

## Lo que esto significa para el Patronato del 10 junio

Cuando elevemos al Patronato + Consejo Aspaniasmerc, podremos enseñar:

- La **demo HTML estática** ([demo/index.html](../../demo/index.html)) para fijar visión sin necesidad de Docker.
- El **modelo de datos completo** ya implementado y migrable.
- El **cuadro de mando funcional** que genera indicadores reales sobre la base.
- El **registro de bitácora** ya operativo (R6 mitigado).
- Que ÁGORA no es un PowerPoint, es código que se levanta con `make up`.

## Próximas decisiones que necesitamos cerrar en el comité del viernes

1. Quién es el referente nominal en Innovación Aspanias y en Sistemas Aspanias.
2. Dónde vive el repositorio git (GitHub privado / GitLab interno / servidor propio).
3. Quién lidera la conversación de migración Odoo → ÁGORA.
4. Confirmación de Lex Digital sobre DPO externo interino.

## Comando para que Sistemas Aspanias arranque y vea M1 funcional

```bash
cd agora-aspanias
copy backend\.env.example backend\.env
notepad backend\.env  (cambiar DJANGO_SECRET_KEY a un valor aleatorio largo)
make up
make makemigrations
make migrate
make createsuperuser
make datos-sinteticos
```

Navegar a:
- http://localhost:8000 — inicio con los cinco módulos.
- http://localhost:8000/personas/ — listado de 20 personas sintéticas.
- http://localhost:8000/agenda/ — agenda de la semana con 40-80 citas.
- http://localhost:8000/indicadores/ — cuadro de mando real.
- http://localhost:8000/admin/ — administración completa.
- http://localhost:8000/admin/core/registroacceso/ — bitácora ya con accesos registrados.

# ÁGORA — Backend

Aplicación Django 5 del Atención y Gestión Operativa para Residentes y Atendidos del Grupo Social Aspanias.

## Arranque rápido con Docker

```bash
# Desde la raíz del repo
cp backend/.env.example backend/.env
# Editar backend/.env con los secretos locales

make up
make migrate
make createsuperuser
make datos-sinteticos
```

App disponible en http://localhost:8000

## Estructura de apps

| App | Responsabilidad | Estado v0.1 |
|---|---|---|
| `sipas/` | Configuración del proyecto (settings, urls, wsgi) | Funcional |
| `core/` | Bitácora de accesos, middleware RBAC, helpers de seguridad | Funcional |
| `personas/` | Ficha única, perfiles por colectivo, familia, centros, profesionales, medidas de apoyo (Ley 8/2021) | Modelo completo |
| `pia/` | Plan Individual de Atención y objetivos AICP | Stub |
| `intervenciones/` | Historial cronológico de intervenciones y valoraciones | Stub |
| `agenda/` | Citas multiprofesionales | Stub |
| `indicadores/` | Cuadro de mando y memoria automatizada | Stub |

## Stack

- Python 3.11+ · Django 5
- PostgreSQL 16 (no SQLite, ni siquiera en local)
- HTMX + Alpine.js + TailwindCSS (CDN en v0.1, build en v1.0)
- SSO Microsoft 365 vía `django-allauth`
- Docker Compose para entorno local

## Recordatorios RGPD (lectura obligada)

- **Solo datos sintéticos** en el repositorio. Cero datos reales, ni en fixtures ni en pruebas locales.
- Toda lectura de ficha genera un registro en la bitácora (`core.RegistroAcceso`).
- Permisos por **rol + centro** (RBAC). Un profesional de Salas no ve fichas de Burgos sin autorización explícita.
- La medida de apoyo (Ley 8/2021) condiciona qué se puede mostrar y firmar — no es solo informativa.

Ver `docs/rgpd/EIPD_inicial.md` y `CLAUDE.md` en la raíz para el detalle.

# ÁGORA

**Atención y Gestión Operativa para Residentes y Atendidos** — Grupo Social Aspanias.

CRM sociosanitario para el seguimiento integral de personas atendidas: discapacidad intelectual, mayores dependientes, inserción laboral y familias. Sustituye al Excel «Registro PV» y al Odoo legado.

## Estado del proyecto

| Fase | Estado | Fecha |
|---|---|---|
| **Fase 0** Decisiones | ✅ Cerrada · pendiente validación Patronato | 2026-05-13 |
| **Fase 1** Modelo + andamiaje | ✅ Cerrada técnicamente | 2026-05-19 |
| **Fase 2** Módulos M1 | ⏳ A iniciar tras Patronato 10/06/2026 | — |
| **Fase 3** Pre-piloto | Previsto Mar–May 2027 | — |
| **Fase 4** Piloto Fuentecillas | Q1 2027 · objetivo | — |
| **Fase 5** Despliegue al grupo | 2027–2029 | — |

## Stack

Django 5 · HTMX · Alpine.js · TailwindCSS · PostgreSQL 16 · SSO Microsoft 365 (Entra ID) · Docker Compose · Ubuntu 24.04.

---

## Quickstart de desarrollo

### Prerrequisitos

- Python 3.11+
- Docker Desktop (para PostgreSQL local)
- Git

### Pasos

```bash
# 1. Clonar y entrar al repo
git clone <url-del-repo> agora-aspanias
cd agora-aspanias

# 2. Variables de entorno
cp backend/.env.example backend/.env
# Edita backend/.env y rellena al menos DJANGO_SECRET_KEY (cualquier cadena larga aleatoria).

# 3. Levantar la base de datos PostgreSQL local
docker compose -f infraestructura/docker-compose.yml up -d db

# 4. Instalar dependencias Python (recomendado en venv)
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
# .venv\Scripts\activate            # Windows PowerShell
pip install -r backend/requirements.txt

# 5. Aplicar migraciones
cd backend
python manage.py migrate

# 6. Datos sintéticos para desarrollo (20 personas ficticias)
python manage.py cargar_datos_sinteticos

# 7. Crear superusuario y arrancar
python manage.py createsuperuser
python manage.py runserver
```

Acceso: <http://localhost:8000/admin/>

### Levantar todo con docker compose

```bash
docker compose -f infraestructura/docker-compose.yml up
```

Web en <http://localhost:8000/>, BD en `localhost:5432` (usuario `agora`, BD `agora`).

---

## Tests y CI

```bash
cd backend
pip install -r requirements-dev.txt   # pytest + ruff
pytest                                # 27 tests · backend completo
pytest -k "personas"                  # solo personas
ruff check .                          # lint
ruff check . --fix                    # auto-arreglar
```

### CI/CD (GitHub Actions)

Workflow `.github/workflows/ci.yml` ejecuta en cada push/PR:

1. **`backend`** — `ruff check` + `pytest`. Falla si hay lint o tests rotos.
2. **`demo`** — Ejecuta `scripts/utilidades/build_demo.py`, verifica que no hay diff (sidebar sincronizado en el repo) y empaqueta `dist/actual/AGORA-demo-para-netlify.zip`.
3. **`release`** — Solo en push a `main`. Crea GitHub Release con tag `demo-YYYY-MM-DD-HHMM` y adjunta el ZIP listo para Netlify.

El workflow se activa cuando el repo se conecte a GitHub. Mientras tanto los mismos comandos funcionan en local.

---

## Demo institucional

Demo HTML estática en `demo/`. Se sirve sin servidor:

- Doble clic en `demo/index.html`, o
- Subir el contenido de `demo/` a Netlify (drag & drop) para tener URL pública.

Páginas clave:

- `index.html` — portada simplificada
- `bienvenida.html` — tour guiado de 5 pasos (recomendado para nuevos)
- `aspanias-cifras.html` — infografía institucional para Patronato
- `persona-detalle.html` — ficha de persona con 5 pestañas
- `agenda.html` → `agenda-hoy.html` — agenda multiprofesional
- `mapa-ocupacion.html` — cuadrícula de habitaciones y camas

---

## Documentación

| Documento | Contenido |
|---|---|
| [PROYECTO_AGORA.md](PROYECTO_AGORA.md) | Documento maestro (alcance, stack, gobernanza) |
| [CLAUDE.md](CLAUDE.md) | Convenciones del repositorio |
| `docs/fase0/` | Actas y materiales de Fase 0 |
| `docs/fase1/cierre_fase1.md` | Cierre técnico de Fase 1 |
| `docs/modelo-datos/modelo_v0_*.md` | Iteraciones del modelo de datos (12 versiones) |
| `docs/rgpd/EIPD_inicial.md` | Evaluación de Impacto en Protección de Datos (v0.2) |
| `docs/rgpd/acuerdo_cotitularidad_art26.md` | Acuerdo de doble corresponsabilidad |
| `docs/migracion/` | Plan de migración del Excel y Odoo legado |

---

## Estructura del repo

```
agora-aspanias/
├── PROYECTO_AGORA.md          # documento maestro
├── CLAUDE.md                  # convenciones
├── README.md                  # este archivo
├── docs/                      # documentación por fases
├── backend/                   # proyecto Django
│   ├── agora/                 # config (settings, urls, wsgi)
│   ├── personas/              # ficha persona atendida
│   ├── pia/                   # Plan de Vida (protocolo Aspanias)
│   ├── intervenciones/        # historial cronológico
│   ├── agenda/                # citas multiprofesionales
│   ├── indicadores/           # cuadro de mando
│   └── core/                  # bitácora RGPD, middleware
├── demo/                      # demo HTML estática (36 páginas)
├── datos/sinteticos/          # fixtures con datos ficticios
├── scripts/                   # utilidades (importadores, pseudonimizador)
└── infraestructura/           # docker-compose, Dockerfile
```

---

## RGPD — antes de tocar nada

Leer `docs/rgpd/EIPD_inicial.md` (sección 7). Recordatorio operativo:

1. **Solo datos sintéticos en el repositorio.** Nunca DNI, nombres reales, teléfonos reales.
2. Cada lectura de ficha queda en bitácora (`core.RegistroAcceso`).
3. Datos médicos = categoría especial art. 9 RGPD. Acceso restringido a rol clínico.
4. Doble corresponsabilidad RGPD entre Fundación Aspanias Burgos y Aspaniasmerc 2016.

Cualquier duda jurídica → **Lex Digital**.

---

## Contacto

**Federico Martínez** — Gerencia Grupo Social Aspanias
gerencia@aspaniasburgos.com · 947 23 85 62
> Despliegue continuo activo desde 25/08/2026: cada push a `main` publica la demo automáticamente en Netlify (configuración en `netlify.toml`).

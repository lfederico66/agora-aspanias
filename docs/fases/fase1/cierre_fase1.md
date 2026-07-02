# Cierre de Fase 1 — ÁGORA

**Fecha de cierre técnico**: 2026-05-19
**Estado**: cerrado por desarrollo · pendiente de validación formal del Patronato (10/06/2026)
**Sponsor**: Federico Martínez — Gerencia
**Alcance original**: modelo de datos + scaffolding Django + EIPD inicial

---

## 1. Resumen ejecutivo

La Fase 1 se cierra con el **modelo de datos completo** (26 modelos, v0.12) implementado en Django 5, **migraciones iniciales generadas y validadas** (`manage.py check` sin issues), **infraestructura de desarrollo lista** (docker-compose con PostgreSQL 16), **tests mínimos en marcha** (19 tests pytest) y la **EIPD actualizada a v0.2** con los nuevos modelos clínicos y de alojamiento.

El proyecto está en condiciones de empezar la Fase 2 (módulos M1 con HTMX) en el momento en que el Patronato apruebe formalmente Fase 0 y autorice continuar.

---

## 2. Entregables — checklist

### 2.1 Modelo de datos
- [x] 26 modelos en `backend/personas/models.py` (incluye perfiles, alojamiento, clínico, medicación)
- [x] Modelo PIA en `backend/pia/models.py` con los 5 documentos del protocolo
- [x] Modelos `Intervencion`, `Cita`, `Valoracion` en sus apps
- [x] Modelo `RegistroAcceso` en `backend/core/models.py` (bitácora RGPD)
- [x] Modelo `Indicador`, `SnapshotPlanesVida`, `MedicionIndicador`

### 2.2 Versiones documentadas
- [x] `docs/modelo-datos/modelo_v0_1.md` a `modelo_v0_12.md` (12 hitos)
- [x] v0.10: Excel «Registro PV» integrado
- [x] v0.11: clínico + familia + medicación (categoría especial art. 9)
- [x] v0.12: alojamiento físico (módulo → habitación → cama → ocupación)

### 2.3 Migraciones iniciales
- [x] `agenda/migrations/0001_initial.py`
- [x] `core/migrations/0001_initial.py`
- [x] `indicadores/migrations/0001_initial.py`
- [x] `intervenciones/migrations/0001_initial.py`
- [x] `personas/migrations/0001_initial.py`
- [x] `pia/migrations/0001_initial.py`
- [x] `python manage.py check` sin issues (validado 2026-05-19)

### 2.4 Scaffolding Django
- [x] `agora/` paquete config con `settings/base.py`, `dev.py`, `prod.py`
- [x] `agora/urls.py` raíz con todas las apps incluidas
- [x] Auth con SSO Microsoft 365 (`django-allauth` + provider microsoft)
- [x] Middleware bitácora `core.middleware.BitacoraAccesoMiddleware`
- [x] `django-axes` para bloqueo por fuerza bruta
- [x] `django-htmx` integrado
- [x] WhiteNoise para servir estáticos
- [x] Admin completo con inlines, fieldsets y autocomplete

### 2.5 Infraestructura local
- [x] `infraestructura/docker-compose.yml` con PostgreSQL 16 + servicio web
- [x] `infraestructura/Dockerfile` (Python 3.11-slim)
- [x] `backend/.env.example` con todas las variables documentadas
- [x] `backend/requirements.txt` con 26 dependencias congeladas a versión

### 2.6 Datos sintéticos
- [x] Comando `cargar_datos_sinteticos` (Faker es_ES, 20 personas)
- [x] Comando `importar_excel_registro_pv` (13 hojas → PersonaAtendida + PlanDeVida)
- [x] Comando `importar_excel_planes_vida` (legacy + generador de plantilla)
- [x] Script `pseudonimizar_excel_pv.py` (sustitución determinista de datos reales)

### 2.7 Tests pytest
- [x] `backend/pytest.ini` configurado
- [x] `backend/conftest.py` con fixtures compartidas
- [x] `personas/tests/test_modelos.py` — 13 tests (alta, baja, código único, medida apoyo, ratio gestora, certificado, dependencia, alojamiento)
- [x] `pia/tests/test_modelos.py` — 3 tests (estado inicial, dos anualidades, str)
- [x] `core/tests/test_bitacora.py` — 4 tests (RegistroAcceso, append-only)
- [x] **19 tests recolectados sin errores** (validado 2026-05-19)

### 2.8 RGPD
- [x] `docs/rgpd/EIPD_inicial.md` v0.2 — actualizada con v0.11 y v0.12
- [x] `docs/rgpd/acuerdo_cotitularidad_art26.md`
- [x] 3 riesgos nuevos identificados (R11 vínculos íntimos en mapa ocupación, R12 alergias en medicación, R13 NUSS en exportes)
- [x] Pendiente revisión final por **Lex Digital** antes del 5/06/2026

### 2.9 Demo institucional
- [x] 36 páginas HTML estáticas con identidad institucional ÁGORA
- [x] Tour de bienvenida + portada simplificada
- [x] Página de cifras Aspanias (institucional)
- [x] Logo nuevo (pórtico SVG) + iconografía Lucide
- [x] Diagrama del Plan de Vida (pentágono SVG)
- [x] Lista para desplegar en Netlify (ZIP de 130 KB)

---

## 3. Métricas finales de Fase 1

| Métrica | Valor |
|---|---|
| Modelos Django | 26 |
| Migraciones iniciales | 6 (una por app) |
| Tests pytest | 19 |
| Apps Django | 7 (`agora`, `personas`, `pia`, `intervenciones`, `agenda`, `indicadores`, `core`) |
| Dependencias en `requirements.txt` | 26 paquetes congelados |
| Documentos del modelo de datos | 12 (v0.1 → v0.12) |
| Páginas de demo | 36 HTML + sprite de iconos |
| Versión EIPD | v0.2 |

---

## 4. Validaciones cumplidas

| Validación | Quién | Cuándo | Estado |
|---|---|---|---|
| `python manage.py check` sin issues | Desarrollo | 2026-05-19 | ✅ |
| Tests pytest se recolectan sin errores | Desarrollo | 2026-05-19 | ✅ |
| Identificadores Python en ASCII | Desarrollo | 2026-05-19 | ✅ |
| Modelo coincide con Excel «Registro PV» | Desarrollo | 2026-05-16 | ✅ |
| Demo institucional aprobada por Gerencia | Federico Martínez | 2026-05-19 | ✅ |
| EIPD revisada por Lex Digital | Lex Digital | < 5/06/2026 | ⏳ pendiente |
| Validación formal Fase 0 | Patronato FAB + Consejo Aspaniasmerc | 10/06/2026 | ⏳ pendiente |

---

## 5. Riesgos remanentes hacia Fase 2

| Riesgo | Mitigación prevista en Fase 2 |
|---|---|
| **Cifrado de NUSS/TSI** no implementado a nivel campo | Introducir `django-cryptography` o equivalente antes del piloto |
| **Restricción de delete en bitácora** solo a nivel UI | Añadir trigger PostgreSQL `BEFORE DELETE` en `RegistroAcceso` |
| **Permisos granulares por rol clínico** no aplicados aún | App `core` con decoradores + middleware en Fase 2 M1 |
| **Sin tests de vistas HTMX** todavía | Añadir con cada vista que se implemente en Fase 2 |
| **Coverage no medido** | Configurar `pytest-cov` con umbral mínimo 70% |
| **Pseudonimizador validado en seco**, no en BD real | Repetir validación con datos reales en Fase 3 pre-piloto |

---

## 6. Hand-off a Fase 2

### Lo que recibe Fase 2

- Repo en estado funcional: `docker compose up db`, `pip install -r requirements.txt`, `python manage.py migrate`, listo.
- 26 modelos con migraciones aplicables sobre BD vacía.
- Admin operativo: a través de `/admin/` se puede dar de alta toda la información hoy.
- Tests base para añadir tests de cada vista que se implemente.
- Demo estática como referencia visual y de UX a replicar en Django + HTMX.

### Lo que necesita decidir el Patronato (10/06/2026)

1. **Validar Fase 0** (decisiones de alcance, stack, gobernanza).
2. **Autorizar continuar a Fase 2** (módulos M1).
3. **Confirmar designación de DPO** (Lex Digital como externo interino).
4. **Aprobar el acuerdo de doble corresponsabilidad** art. 26 RGPD.
5. **Asignar presupuesto** para Fase 2 (Innovación Aspanias + Sistemas Aspanias).

---

## 7. Próximos pasos inmediatos

1. **20/05–05/06**: revisión Lex Digital de EIPD v0.2 + acuerdo art. 26.
2. **10/06**: Patronato + Consejo Aspaniasmerc.
3. **11/06–30/06**: arranque Fase 2 si hay luz verde.
4. **Fase 2 (junio–febrero 2027)**: módulos M1 con HTMX, formularios completos, vistas web.

---

*Documento de cierre técnico Fase 1 · Federico Martínez (sponsor)*

# Guía de reanudación — ÁGORA (25/08/2026)

## Estado
- Demo completa (77 págs.) publicada en Netlify (ZIP manual).
- Backend Django v0.12 · brecha priorizada en decisiones/08_backlog_demo_django.md.
- Migración: MAESTRO_importacion_agora.xlsx listo (1.690 personas) + censo Fuentecillas (43).
- Git local en main, SIN remoto (riesgo demostrado por incidente OneDrive 25/08).

## Semana 1 (25-29 ago) — desbloqueos (Federico)
1. Crear repo privado GitHub `agora-aspanias` y pasar URL → push.
2. Conectar Netlify al repo (deploy automático, adiós ZIP).
3. Verificar BitLocker + identificar el otro dispositivo OneDrive (origen del "999").
4. Nota RGPD plantillas → Lex Digital → circular + carpeta SharePoint "Plantillas ÁGORA".
5. Revisiones de datos: Laura (9 ambiguos + 6 "otro servicio" Fuentecillas) · TS (30 excepciones + 10 conflictos maestro).
6. DECISIÓN alcance pre-piloto: recomendado octubre con ficha + cuidados enfermería + ficha salud PDF + carga 43 personas; FIS y valoraciones → piloto Q1 2027.

## Semanas 2-5 (sept) — construcción (Claude)
1. Cuidados de enfermería Django (2-3 d)
2. Ficha básica de salud PDF + bitácora (1-2 d)
3. Edición inline ficha (2 d)
4. importar_maestro + prueba en seco (3-4 d)
5. Despliegue VM Ubuntu + SSO M365 con Sistemas (2-3 d)

## Octubre — pre-piloto Fuentecillas
Carga real 43 personas → alta equipo con SSO → formación con manual-uso.html → 2-3 semanas de uso → informe (plantilla en docs/fases/fase3/).

## Ritual
- build_demo + check_gobernanza + commit + push en cada cambio.
- Revisión quincenal del backlog (decisión 08) con Gerencia.
- Datos reales: solo C:\dev\agora-datos-migracion y carpetas OneDrive registradas.

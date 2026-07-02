# Kickoff ÁGORA — Innovación Aspanias + Sistemas Aspanias

**Fecha**: jueves 14 de mayo de 2026
**Duración**: 90 minutos
**Convoca**: Federico Martínez Miguel (Gerencia / Dirección de Centros y Servicios)
**Lugar**: sede Aspanias Burgos (o Teams)

---

## Asistentes obligatorios

- Federico Martínez Miguel — Gerencia / Dirección de Centros y Servicios (sponsor).
- Responsable de Innovación Aspanias — propietario funcional del producto.
- Responsable de Sistemas Aspanias — propietario técnico (infraestructura, despliegue).
- 1 perfil de desarrollo de Innovación Aspanias.
- 1 perfil de operaciones de Sistemas Aspanias.

## Materiales a llevar

1. **Carpeta `agora-aspanias/` en USB o ruta de red compartida** (todo el repositorio).
2. **Demo abierta en navegador**: `demo/index.html` (ya navegable, sin instalación).
3. Documento maestro: [PROYECTO_ÁGORA.md](../../PROYECTO_ÁGORA.md).
4. Calendario operativo: [calendario_a_patronato.md](calendario_a_patronato.md).
5. Acta de Fase 0: [acta_decisiones_fase0.md](acta_decisiones_fase0.md).
6. Modelo de datos: [modelo_v0_1.md](../modelo-datos/modelo_v0_1.md).

---

## Orden del día

### 1 · Apertura y contexto (10 min)
- Por qué ÁGORA: necesidad de sustituir el Odoo `preaspanias.integrodoo.com` con un CRM sociosanitario propio.
- Compromiso institucional: Patronato + Consejo Aspaniasmerc el **10 de junio**. Piloto Q3 2026.
- Decisión de Gerencia de mantener fecha y alcance asumiendo riesgo (acta Fase 0, riesgos R1-R8).

### 2 · Recorrido por la demo (15 min)
Abrir `demo/index.html` y mostrar:
- Pantalla de inicio con los cinco módulos del MVP.
- Listado de personas atendidas con los cuatro colectivos representados.
- Ficha de Marta González (DI, apoyo judicial Ley 8/2021).
- PIA con objetivos AICP por ámbito.
- Agenda multiprofesional semanal con notificación a familias vía CERCA.
- Historial de intervenciones con timeline y filtros.
- Cuadro de mando con KPIs y exportación para memoria/IAPA.

> **Mensaje clave**: la demo es lo que vamos a construir, no lo que ya está construido. Sirve para fijar el "qué" antes de empezar el "cómo".

### 3 · Asignación de responsabilidades (15 min)

| Bloque | Innovación Aspanias | Sistemas Aspanias |
|---|---|---|
| Producto funcional (modelo, vistas, flujos) | **Propietario** | Apoya |
| Infraestructura (Docker, PostgreSQL, despliegue) | — | **Propietario** |
| SSO Microsoft 365 (Entra ID) | — | **Propietario** |
| Bitácora, RBAC, seguridad | Apoya | **Propietario** |
| Modelo de datos v1.0 | **Propietario** | Apoya en BD |
| Datos sintéticos y carga | **Propietario** | — |
| Integración con CERCA (federación) | **Propietario** | Apoya |
| Migración Odoo → ÁGORA | Compartido | Compartido |
| Validación funcional semanal | Apoya | — |

Quién toma cada hito del calendario semanal — fijar interlocutores nominales hoy.

### 4 · Acuerdos técnicos críticos (20 min)

Decisiones que no se reabren después del kickoff:

- **Stack**: Django 5 + HTMX + Alpine + Tailwind + PostgreSQL 16. **Cerrado.**
- **Autenticación**: SSO M365 para profesionales. Familias vía CERCA. **Cerrado.**
- **Almacenamiento documental**: Azure Blob Storage UE. **Cerrado.**
- **Idioma del código**: entidades del dominio en español (`PersonaAtendida`, `MedidaDeApoyo`), atributos técnicos en inglés (`created_at`). **Cerrado.**
- **Datos sintéticos únicamente** durante todo el desarrollo. **Cerrado y no negociable.**
- **PostgreSQL desde día 1, no SQLite**. **Cerrado.**
- **Registro git**: por confirmar — ¿GitHub privado del grupo, GitLab interno, o repositorio en servidor Aspanias? Decisión hoy.
- **Sistema de CI**: ¿GitHub Actions, GitLab CI o sin CI en v0.1? Decisión hoy.
- **Convenciones de commits y PRs**: Conventional Commits + revisión obligatoria entre Innovación y Sistemas. Confirmar hoy.

### 5 · Validación primer arranque técnico (15 min)
Sistemas Aspanias muestra en vivo:
- `make up` con Docker funcionando.
- `make migrate` aplicando el modelo de datos.
- `make datos-sinteticos` cargando 20 personas.
- Acceso a http://localhost:8000 y al admin `/admin/`.
- Acceso a la bitácora de accesos.

Si el arranque falla, **detener kickoff** y dedicar el resto a resolverlo. Sin arranque limpio hoy no se puede pretender entregar nada en junio.

### 6 · Riesgos y mitigaciones (10 min)
Repaso breve de los riesgos asumidos en acta Fase 0:
- R7: equipo solo-interno. **Decisión hoy**: ¿quién es el sustituto del responsable de Sistemas y de Innovación si alguno tiene una baja >1 semana?
- R8: DPO sin designar. **Acción Federico**: gestión con Lex Digital esta misma semana.
- R3: migración Odoo. **Decisión hoy**: ¿quién pide acceso de lectura a Integrodoo y obtiene la estructura de datos del Odoo legado?

### 7 · Próximos hitos y cierre (5 min)
- Comité semanal: viernes 16 mayo 12:00. Recurrente todos los viernes.
- Antes del comité, cada bloque entrega su "definition of done" para la semana 21.
- Compromiso de Sistemas: SSO M365 funcional en local antes del viernes 22 mayo.
- Compromiso de Innovación: modelo de datos v1.0 con observaciones de Operaciones antes del 29 mayo.

---

## Salida esperada del kickoff

1. Tres nombres concretos para los tres roles operativos clave: responsable Innovación, responsable Sistemas, persona referente para validación funcional.
2. Repositorio git **creado** y con primer push hoy (no esta semana).
3. Arranque limpio del entorno Docker validado en al menos un equipo.
4. Decisiones abiertas (registro git, CI) cerradas.
5. Próximas tres reuniones agendadas en calendarios.
6. Esta acta de kickoff firmada por los tres asistentes principales.

---

## Notas — Federico

- No leer la documentación durante la reunión. Está leída. La reunión es para alinear y decidir.
- Si surge una decisión técnica que no cierra en 5 minutos, anotarla y resolverla **antes del comité del viernes**, no en la propia reunión.
- Si alguien propone ampliar alcance o cambiar stack, recordar el riesgo R6 del acta y aplazar la discusión al primer comité.
- La demo es para alinear visión, no para discutir colores ni textos. Cualquier ajuste cosmético → backlog.

---

*Guion v1.0 — para uso en la reunión del 14 mayo 2026.*

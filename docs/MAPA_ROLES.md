# ÁGORA — Mapa de roles y permisos por capacidad

**Vinculante. Cada nueva vista declara su rol(es) destinatario(s).**

Aplicación de la **Regla 2 de gobernanza** (CLAUDE.md): si una pantalla no aplica a un rol, no aparece en su sidebar ni es accesible por URL para ese rol.

---

## 6 roles canónicos

### 🎩 Gerencia
- **Persona ejemplo**: Federico Martínez
- **Ámbito**: total grupo
- **Ve**: todo
- **Decide**: estratégico, Patronato, aperturas/cierres
- **Sidebar**: Inicio · Agenda (suya) · Personas · Incidencias FIS · Centros · Equipo · Caja · Facturación · Tablero · En cifras · Avisos · Tour · Hoja de ruta

### 🏢 Dirección de centro
- **Persona ejemplo**: Bárcena Sanz, Roberto (Res. Fuentecillas)
- **Ámbito**: su centro
- **Ve**: personas atendidas del centro · equipo del centro · caja del centro · FIS del centro · agenda del centro · turnos · calendario laboral del centro
- **Decide**: operativa diaria del centro, sustituciones, aprobaciones vacaciones
- **No ve**: facturación grupo · tablero institucional grupo · cifras grupo · datos de otros centros
- **Sidebar reducido**: Inicio · Agenda · Personas (su centro) · FIS (su centro) · Mi centro · Equipo (de su centro) · Caja · Avisos

### 📋 Gestor/a de caso
- **Persona ejemplo**: López Pérez, Marta (gerocultora con 3 personas asignadas)
- **Ámbito**: sus personas asignadas (M2M)
- **Ve**: solo las personas de las que es gestor de caso · sus intervenciones · sus PIA · sus PV
- **Decide**: actualización PV (anual), intervenciones, avisos a Dirección
- **No ve**: otras personas atendidas · plantilla · caja · facturación · calendario laboral
- **Sidebar mínimo**: Inicio · Agenda · Mis personas · Avisos

### 🩺 Profesional
- **Persona ejemplo**: Renedo, Pilar (Terapeuta Ocupacional)
- **Ámbito**: su agenda + su calendario + las personas con las que trabaja
- **Ve**: su calendario individual · su agenda · sus pluses · personas del centro (lectura limitada según función)
- **Decide**: nada estructural; solicita vacaciones, marca su agenda
- **No ve**: caja · facturación · tablero · plantilla · datos económicos
- **Sidebar mínimo**: Inicio · Mi agenda · Mi calendario · Personas (lectura) · Solicitar ausencia

### 📑 RRHH
- **Persona ejemplo**: Ureta Ramos, Sonia (Dirección Administración)
- **Ámbito**: todo el grupo en lo laboral
- **Ve**: plantilla completa · vacaciones de todos · calendarios laborales aprobados · turnos · patrones · IT
- **Decide**: aprobaciones definitivas, parte de IT, sincronización con SIGPER/EQUIPO
- **No ve**: personas atendidas individuales · clínico
- **Sidebar específico**: Inicio · Plantilla · Vacaciones (todos) · Turnos · Calendarios · Patrones · Formación

### 👨‍👩‍👧 Familia
- **Persona ejemplo**: hijo/a de Ruiz Jiménez, Asunción
- **Ámbito**: solo su persona referenciada
- **Acceso**: vía CERCA (no acceso directo a ÁGORA)
- **Ve**: ficha persona (limitada), bolsillo, citas, comunicación con gestor de caso
- **Decide**: comunicación, consentimientos, lectura de informes
- **No ve**: nada operativo de plantilla, caja del centro, otras personas

---

## Matriz de visibilidad por módulo

| Módulo | Gerencia | Direc. centro | Gestor caso | Profesional | RRHH | Familia |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| Inicio | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Agenda (propia) | ✅ | ✅ | ✅ | ✅ | ✅ | parcial |
| Personas atendidas | grupo | su centro | suyas | lectura | ❌ | la suya |
| Incidencias FIS | grupo | su centro | suyas | crear | ❌ | ❌ |
| Centros | todos | el suyo | el suyo | el suyo | ❌ | el suyo |
| Equipo · Profesionales | todos | su centro | ❌ | ❌ | todos | ❌ |
| Equipo · Vacaciones | todos | su centro | la suya | la suya | todos | ❌ |
| Equipo · Turnos | todos | su centro | ❌ | el suyo | todos | ❌ |
| Equipo · Calendario laboral | todos | su centro | ❌ | el suyo | todos | ❌ |
| Equipo · Patrones | todos | lectura | ❌ | ❌ | edición | ❌ |
| Caja y bolsillos | todos | su centro | ❌ | ❌ | ❌ | bolsillo suyo |
| Facturación | todos | su centro | ❌ | ❌ | ❌ | la suya |
| Tablero (interno) | total | su centro | ❌ | ❌ | KPIs RRHH | ❌ |
| En cifras (público) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Avisos | todos | su centro | suyos | suyos | RRHH | ❌ |

---

## Implementación técnica

### Marca en plantillas (Django)
Cada template Django debe declarar al inicio:

```django
{# @rol: gerencia, direccion_centro #}
{% extends "base.html" %}
```

El template `base.html` lee el rol del usuario autenticado y decide qué bloques del sidebar mostrar.

### Marca en demo (HTML estático)
Cada HTML de la demo lleva un comentario al inicio del `<body>`:

```html
<!-- @rol: gerencia, direccion_centro -->
```

### Cookie en demo
La demo usa `document.cookie = "agora_rol=..."` para simular el cambio de rol sin auth real. En producción, viene del SSO Microsoft 365.

---

## Reglas duras

1. **Bitácora obligatoria** — cualquier acceso a ficha persona queda registrado con usuario + IP + timestamp + motivo (CLAUDE.md §RGPD).
2. **Tutela (Ley 8/2021)** — el ámbito de la medida de apoyo registrada limita qué datos puede ver el corresponsable. Diseñar permisos por **capacidad**, no solo por rol.
3. **Menores** — doble consentimiento si > 14 años + aviso visible.
4. **Cifrado** — DNI, NUSS, TSI, partes de IT siempre cifrados en reposo.
5. **Retención** — política documentada en `docs/rgpd/`.

---

*Actualizar cuando se añada un rol, un módulo nuevo o cambie una capacidad legal.*

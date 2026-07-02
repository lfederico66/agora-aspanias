# Acceso del equipo al piloto ÁGORA

**Centro**: Residencia Fuentecillas
**Periodo**: Q1 2027
**Profesionales con acceso**: ≈ 18
**Sponsor**: Federico Martínez — Gerencia
**Versión**: 0.1 (borrador para Sistemas Aspanias)

---

## 1. Decisión de despliegue

### 1.1 Tres opciones evaluadas

| Aspecto | A · VM Hyper-V interna | B · Azure España | C · Híbrido (interno + VPN) |
|---|---|---|---|
| Quién opera | Sistemas Aspanias | Microsoft (encargado del tratamiento) + Sistemas Aspanias | Sistemas Aspanias |
| URL | `agora.aspaniasburgos.com` → IP interna | `agora.aspaniasburgos.com` → IP Azure | igual A |
| Acceso desde casa / móvil profesional | Solo VPN del grupo | Posible directo con MFA | Sí, con VPN |
| Coste recurrente | 0 € (VM ya existente) | 80-150 €/mes (4 vCPU + 8 GB + backup gestionado) | 0 € adicional |
| Disponibilidad | Buena (depende de Hyper-V interno) | 99,9 % SLA Azure | Buena |
| Backups | Cron + NAS interno | Snapshots automáticos | Cron + NAS interno |
| Soberanía RGPD | 100 % infra Aspanias | Microsoft España (UE) con contrato 28 RGPD | 100 % infra Aspanias |
| Tiempo de montaje | 2-3 h | 4-5 h | 2-3 h + VPN |

### 1.2 Decisión adoptada

**Opción A · VM Hyper-V interna**.

Razones:
- Cero coste adicional.
- Soberanía total sobre los datos.
- Documentación ya completa (`docs/operaciones/despliegue_interno.md`).
- Suficiente para el horario laboral del centro durante el piloto.
- Si después se necesita acceso externo, se añade VPN sin cambiar la
  arquitectura.

**Plan B** (si Sistemas Aspanias no puede montar la VM a tiempo o si surge
problema): activar opción B (Azure España) en una semana. Documentar
condiciones de activación en una addenda al cierre del pre-piloto.

---

## 2. Quiénes acceden al piloto

El equipo asistencial completo de Residencia Fuentecillas + Federico +
soporte técnico. Aproximadamente **18 profesionales** (cifra concreta a
confirmar en diciembre 2026):

| Rol | Personas estimadas | Acceso clínico |
|---|---|---|
| Dirección / coordinación | 2 (Federico + Lucía) | Sí + jurídico |
| Trabajo Social (TS) | 2 | No (administrativo) |
| Terapia Ocupacional (TO) | 2 | No |
| Enfermería (DUE) | 3 (turnos) | **Sí** |
| Auxiliares | 5 (turnos) | Acceso administrativo · ver intervenciones |
| Educadores | 2 | No |
| Psicología (compartida con CO) | 1 | **Sí** |
| Médico/a externo (consulta) | 1 (acceso puntual) | **Sí** |
| Soporte técnico Innovación Aspanias | 1 | Superuser limitado |

> Los roles se asignan en `personas.Profesional.rol_principal`. La tabla
> `core.permissions.ROLES_CON_ACCESO_CLINICO` (Fase 2.5.3) define quién
> ve la pestaña Información médica y Medicación.

---

## 3. Procedimiento de alta de profesionales (sem -3)

Para cada uno de los 18 profesionales:

### Paso 1 — Sistemas Aspanias (Entra ID)

1. Verificar que tiene **cuenta M365 activa** del grupo (`@aspaniasburgos.com`).
2. Asignarla al grupo Entra ID **`agora-usuarios-fuentecillas`**.
3. Verificar **MFA obligatorio** (Authenticator instalado).
4. Si es nueva alta: provisión completa antes de la semana -2.

### Paso 2 — Federico (admin ÁGORA)

1. Acceder a `https://agora.aspaniasburgos.com/admin/`.
2. Crear `auth.User` (si no se ha creado por allauth en su primer login).
3. Crear `personas.Profesional` vinculado al user:
   - `nombre_completo`
   - `email_m365` = email Aspanias
   - `rol_principal` (asignar Rol existente, p. ej. DUE)
   - `centros_acceso` → marcar **Residencia Fuentecillas**
   - `puede_ser_gestor_caso` = sí, si aplica
4. Verificar que el rol concede el nivel de acceso correcto consultando
   `core/permissions.py`.

### Paso 3 — Mail de bienvenida

Federico envía mail institucional (plantilla en §6).

### Paso 4 — Sesión presencial primer acceso

Lucía bloquea **15 minutos por profesional** entre la semana -1 y el día 1.
Se hace en sala con un portátil del centro. Objetivo:

1. Login con SSO M365 + MFA.
2. Acceso a la portada → verifica que aparecen los módulos correctos.
3. Entrar a una ficha de prueba (la suya como profesional o una persona
   atendida que ya esté).
4. Verificar que **solo ve las pestañas a las que tiene permiso**.
5. Mostrar dónde está el manual rápido y el contacto de soporte.

---

## 4. Plantilla de mail institucional al profesional

> **De**: Federico Martínez Miguel <gerencia@aspaniasburgos.com>
> **Para**: [nombre.profesional]@aspaniasburgos.com
> **Asunto**: ÁGORA — acceso al piloto Fuentecillas
>
> Hola [nombre],
>
> Como te comenté en la sesión de formación, el lunes **11 de enero arrancamos
> el piloto de ÁGORA en Residencia Fuentecillas**. A partir de ese día, la
> información de las personas que atendemos se gestiona en este nuevo sistema
> y el Excel actual pasa a histórico.
>
> Acceso:
>
> **URL** → `https://agora.aspaniasburgos.com`
> **Usuario** → tu correo de Aspanias
> **Contraseña** → la habitual de Microsoft 365
> **Segundo factor** → tu Microsoft Authenticator (igual que ahora)
>
> Te he asignado el rol **[rol]**. Eso significa que ves la información
> [descripción breve · p. ej. "administrativa y la pestaña Familiares, pero
> no los datos médicos detallados ni la medicación"].
>
> Antes del lunes 11, **Lucía Martínez** te bloqueará un hueco de 15 minutos
> para que entres por primera vez con ella al lado. Aprovéchalo: las dudas
> tontas son las que más nos hacen perder tiempo si no las preguntamos.
>
> Lleva contigo:
>
> 1. El **manual rápido** (te lo dejamos impreso en el office).
> 2. Tu **móvil** con el Authenticator activo.
>
> Si algo falla, escríbeme directamente o llama al teléfono de soporte que
> aparece en el manual.
>
> Gracias por entrar en esto. Lo vas a notar.
>
> Un abrazo,
>
> Federico

---

## 5. Chuleta SSO en una hoja A4

> **ÁGORA · Cómo entrar**
>
> 1. Abre **Edge** o **Chrome**.
> 2. Ve a `https://agora.aspaniasburgos.com`.
> 3. Pulsa **"Entrar con Microsoft 365"**.
> 4. Pon tu correo de Aspanias.
> 5. Pon la contraseña habitual.
> 6. Confirma en el Authenticator del móvil.
>
> ¡Listo!
>
> ---
>
> **Si algo falla:**
>
> - **No me deja entrar** → comprueba contraseña. Si sigue, ext. 230.
> - **No tengo Authenticator** → ext. 230 (Sistemas Aspanias).
> - **Veo la portada pero falla algo dentro** → ext. 220 (Lucía).
>
> ---
>
> **Recuerda:**
>
> - Cierra sesión al salir, sobre todo en equipos compartidos.
> - No compartas tu contraseña con nadie.
> - Cada acceso queda registrado (es bueno).
> - El manual rápido completo está en el office.

(Hoja maquetada por Comunicación con plantilla institucional Aspanias.)

---

## 6. Niveles de soporte

| Nivel | Quién | Qué resuelve | Cómo se contacta |
|---|---|---|---|
| **L1 · Acceso e infra** | Sistemas Aspanias | SSO, contraseñas, MFA, conectividad, VM caída | Ext. 230 · `sistemas@aspaniasburgos.com` |
| **L2 · Aplicación** | Innovación Aspanias | Bug, error de aplicación, datos inconsistentes, formulario que falla | `innovacion@aspaniasburgos.com` |
| **L3 · Funcional y decisión** | Federico Martínez | Cualquier duda de criterio, RGPD, comunicación a familia, decisión operativa | Móvil directo · gerencia@aspaniasburgos.com |
| **Coordinación in situ** | Lucía Martínez (TO) | Uso día a día, formación entre pares, dudas operativas | Ext. 220 |
| **Jurídico** | Lex Digital | Cualquier cuestión RGPD compleja, ejercicio de derechos ARSULIPO | A través de Federico |

### Tiempos de respuesta comprometidos durante el piloto

| Severidad | Ejemplo | Tiempo |
|---|---|---|
| **Crítico** | ÁGORA caída, brecha RGPD, datos corruptos | < 2 h laborales |
| **Alto** | Bug que bloquea un flujo principal | < 4 h laborales |
| **Medio** | Bug menor, problema de UX | < 24 h |
| **Bajo** | Duda, sugerencia | < 48 h |

Fuera de horario laboral, solo el **crítico**: línea de Federico.

---

## 7. Acceso desde fuera del centro

### 7.1 Desde móvil profesional dentro de Wi-Fi corporativa
Acceso directo a `https://agora.aspaniasburgos.com` desde el navegador.

### 7.2 Desde casa o fuera de la red Aspanias
Requiere **VPN corporativa Aspanias**:

1. Conectar VPN del grupo (procedimiento estándar Sistemas Aspanias).
2. Acceder a la URL.

Si el piloto revela que **muchos profesionales usan ÁGORA desde casa**
(p. ej. registrar lo que pasó en una visita), valorar en Fase 5 publicar
el sistema en una IP semi-pública con MFA reforzado.

### 7.3 Desde dispositivos personales
**Permitido** mientras se respete:
- Login con cuenta institucional + MFA.
- No descargar nada localmente.
- Cierre de sesión al terminar.

Si una persona se sale del grupo, Sistemas Aspanias **desactiva la cuenta
M365** → automáticamente pierde el acceso a ÁGORA (no hace falta tocar
ÁGORA).

---

## 8. Gestión de bajas y cambios durante el piloto

### 8.1 Baja de un profesional
Cuando un profesional **se va del centro o del grupo**:

1. Sistemas Aspanias **desactiva la cuenta M365**.
2. Federico marca `Profesional.activo = False` en el admin de ÁGORA.
3. **NO se borra** el registro del profesional — su histórico debe permanecer
   visible (autoría de intervenciones, accesos en bitácora).
4. Si la persona era **gestora de caso**, se dispara automáticamente un
   `AvisoCambioProfesional` a Dirección para asignar gestora suplente.

### 8.2 Cambio de rol
Si un profesional pasa de TS a Coord., o de Auxiliar a DUE recién titulado:

1. Federico cambia `Profesional.rol_principal` en el admin.
2. El permiso cambia automáticamente al siguiente acceso (no hace falta
   logout/login pero conviene refrescar).
3. Anotar el cambio en el histórico interno del profesional.

### 8.3 Permisos especiales temporales
Si excepcionalmente un profesional necesita acceso clínico de forma
temporal (sustitución de un DUE de baja larga, p. ej.):

1. Decisión escrita de Federico (mail al expediente).
2. Federico cambia el rol temporalmente.
3. Al volver el DUE titular, se revierte.
4. Documentar el cambio en `docs/fase4/permisos_temporales.md`.

---

## 9. Auditoría continua de accesos

Durante el piloto, Federico revisa **mensualmente** la bitácora
`core_registroacceso`:

1. **Volumen de accesos** por profesional — detectar uso anormal (un
   auxiliar accediendo a 50 fichas en un día sin motivo).
2. **Accesos sin motivo registrado** en operaciones sensibles.
3. **Accesos fuera de horario** (entre 22:00 y 6:00) — pueden ser
   legítimos pero requieren explicación si son recurrentes.
4. **Discrepancias** entre quién está de turno y quién accede.

Cualquier anomalía se eleva a Lex Digital antes de tomar decisiones.

---

## 10. Calendario macro del onboarding

| Sem | Hito | Quién |
|---|---|---|
| -4 (dic) | Lista definitiva de 18 profesionales firmada | Lucía + Federico |
| -3 | Altas en Entra ID + creación de `Profesional` en ÁGORA | Sistemas + Federico |
| -3 | Sesiones formación al equipo (4 sesiones × 2 h) | Federico + Lucía |
| -2 | Envío del mail de bienvenida + chuleta SSO impresa | Federico |
| -1 | Sesiones presenciales 15 min × 18 = 4,5 h en agenda de Lucía | Lucía |
| 1 día 1 (lun 11 ene 2027) | Federico + Lucía presentes en sala todo el día | Federico + Lucía |
| 1 | Mail de Federico al cierre del día 1 al equipo con balance | Federico |

---

## 11. Documentos relacionados

- `docs/operaciones/despliegue_interno.md` — instalación VM Sistemas Aspanias
- `docs/fase3/manual_uso_rapido.md` — el manual de 5 hojas
- `docs/fase4/plan_piloto.md` — plan general del piloto
- `docs/rgpd/EIPD_inicial.md` v0.2 — marco RGPD
- `docs/fase4/checklist_arranque.md` (pendiente) — checklist firmable
- `docs/fase4/permisos_temporales.md` (vacío hasta que haga falta)

---

*Documento de acceso del equipo al piloto v0.1 · 2026-05-19 ·
Federico Martínez (sponsor) + Sistemas Aspanias.*

*Se revisa y firma con Sistemas Aspanias antes del arranque del piloto
(diciembre 2026).*

# Despliegue interno de ÁGORA — VM Ubuntu sobre Hyper-V

**Audiencia**: Sistemas Aspanias
**Versión**: 0.1 · 2026-05-19
**Tiempo estimado**: 2-3 h primera instalación

Esta guía describe paso a paso cómo montar ÁGORA en una máquina virtual Ubuntu
24.04 LTS dentro del Hyper-V interno del Grupo Social Aspanias. El resultado:
una instancia accesible en `https://agora.aspaniasburgos.com` desde la red
corporativa (o VPN).

---

## 0. Pre-requisitos

| Requisito | Quién lo provee |
|---|---|
| VM Ubuntu 24.04 LTS con 4 vCPU, 8 GB RAM, 80 GB disco | Sistemas Aspanias |
| IP fija interna y entrada DNS `agora.aspaniasburgos.com` apuntando a esa IP | Sistemas Aspanias |
| Acceso SSH a la VM con usuario `agora_admin` (sudo) | Sistemas Aspanias |
| Certificado SSL para `agora.aspaniasburgos.com` (interno o público) | Sistemas Aspanias |
| Aplicación registrada en Entra ID para SSO M365 (`M365_CLIENT_ID/SECRET/TENANT`) | Sistemas Aspanias |
| Acceso al repositorio Git del proyecto ÁGORA | Innovación Aspanias |

---

## 1. Preparar la VM

```bash
# Conectarse a la VM
ssh agora_admin@<IP-INTERNA>

# Actualizar paquetes
sudo apt update && sudo apt upgrade -y

# Instalar Docker + Compose plugin
sudo apt install -y ca-certificates curl gnupg lsb-release
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Permitir al usuario usar Docker sin sudo
sudo usermod -aG docker agora_admin
newgrp docker

# Verificar
docker --version
docker compose version
```

---

## 2. Clonar el repositorio

```bash
# Crear directorio de despliegue
sudo mkdir -p /opt/agora
sudo chown agora_admin:agora_admin /opt/agora

# Clonar el repo
cd /opt
git clone <url-repositorio> agora
cd /opt/agora

# Estructura esperada
ls -la
# backend/ demo/ docs/ infraestructura/ ...
```

---

## 3. Configurar variables de entorno

```bash
# Copiar la plantilla
cp backend/.env.example backend/.env
nano backend/.env
```

Rellenar:

```ini
DJANGO_SETTINGS_MODULE=agora.settings.prod
DJANGO_SECRET_KEY=<generar con: python -c "import secrets; print(secrets.token_urlsafe(50))">
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=agora.aspaniasburgos.com,<IP-INTERNA>

DATABASE_URL=postgres://agora:<password-fuerte>@db:5432/agora

M365_CLIENT_ID=<de Entra ID>
M365_CLIENT_SECRET=<de Entra ID>
M365_TENANT_ID=<de Entra ID>
M365_REDIRECT_URI=https://agora.aspaniasburgos.com/accounts/microsoft/login/callback/

AGORA_FIELD_ENCRYPTION_KEY=<generar: docker run --rm python:3.11-slim python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">

DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
DJANGO_SECURE_HSTS_SECONDS=31536000
```

También definir las variables Postgres en el entorno del compose:

```bash
# /opt/agora/.env (raíz, no backend/.env)
cat > .env <<EOF
POSTGRES_DB=agora
POSTGRES_USER=agora
POSTGRES_PASSWORD=<password-fuerte>
EOF
chmod 600 .env backend/.env
```

> ⚠️ La clave `AGORA_FIELD_ENCRYPTION_KEY` es **crítica**: si se pierde,
> los NUSS/TSI cifrados en BD quedan irrecuperables. Guárdala también en el
> gestor de contraseñas institucional de Aspanias.

---

## 4. Instalar el certificado SSL

```bash
sudo mkdir -p /opt/agora/infraestructura/nginx/ssl
# Copiar los archivos del certificado interno o del proveedor:
sudo cp agora.crt /opt/agora/infraestructura/nginx/ssl/
sudo cp agora.key /opt/agora/infraestructura/nginx/ssl/
sudo chmod 600 /opt/agora/infraestructura/nginx/ssl/agora.key
```

Si se usa Let's Encrypt (no recomendado para dominio interno), preguntar a
Sistemas Aspanias por el procedimiento estándar del grupo.

---

## 5. Primer arranque

```bash
cd /opt/agora

# Construir y levantar
docker compose -f infraestructura/docker-compose.prod.yml up -d

# Verificar que están todos los servicios
docker compose -f infraestructura/docker-compose.prod.yml ps
# Debe mostrar 3 servicios: db (healthy), web (running), nginx (running)

# Ver logs durante el primer arranque
docker compose -f infraestructura/docker-compose.prod.yml logs -f web
# Esperar a ver "Listening at: http://0.0.0.0:8000"
```

Las migraciones se aplican automáticamente al arrancar (`migrate --noinput`
está en el command del servicio `web`).

---

## 6. Crear el primer superusuario

```bash
docker compose -f infraestructura/docker-compose.prod.yml exec web \
    python manage.py createsuperuser

# Email: federico@aspaniasburgos.com (o el que corresponda)
# Contraseña: <fuerte>
```

Acceso al admin: `https://agora.aspaniasburgos.com/admin/`

---

## 7. Configurar backups automáticos

```bash
# Hacer ejecutable el script
chmod +x /opt/agora/infraestructura/scripts/backup_db.sh

# Crear cron para backup diario a las 3:00 (en root)
sudo crontab -e

# Añadir línea:
0 3 * * * /opt/agora/infraestructura/scripts/backup_db.sh >> /var/log/agora_backup.log 2>&1
```

Política de retención implementada en el script:
- **Diarios**: 7 días
- **Semanales**: 5 semanas (snapshot de cada domingo)
- **Mensuales**: 12 meses (snapshot del día 1)

> Replica adicional recomendada a Azure Blob o NAS institucional cifrado.
> Documentar como tarea separada de Sistemas Aspanias.

---

## 8. Verificación post-instalación

| Comprobación | Comando / URL | Resultado esperado |
|---|---|---|
| HTTPS funciona | `curl -I https://agora.aspaniasburgos.com` | 302 (redirige a login) |
| HSTS activo | inspeccionar cabecera `Strict-Transport-Security` | `max-age=31536000` |
| Admin accesible | `https://agora.aspaniasburgos.com/admin/` | Pantalla de login Django |
| SSO M365 | Login con cuenta Aspanias | Redirección a Microsoft + vuelta |
| Bitácora activa | crear un acceso y verificar en `core_registroacceso` | Fila creada |
| Trigger append-only | intentar DELETE en `core_registroacceso` desde psql | Exception P0001 |
| Cifrado NUSS | dar de alta una persona con NUSS, consultar BD raw | El valor en columna está cifrado (gAAAAA...) |
| Backup funciona | `sudo /opt/agora/infraestructura/scripts/backup_db.sh` | `.sql.gz` creado en `/opt/agora/backups/diarios/` |

---

## 9. Releases (actualizar a una versión nueva)

```bash
cd /opt/agora

# Bajar cambios
git pull

# Reconstruir imagen + reaplicar migraciones
docker compose -f infraestructura/docker-compose.prod.yml build web
docker compose -f infraestructura/docker-compose.prod.yml up -d
docker compose -f infraestructura/docker-compose.prod.yml exec web python manage.py migrate --noinput
docker compose -f infraestructura/docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Verificar
docker compose -f infraestructura/docker-compose.prod.yml logs --tail=50 web
```

Plan de rollback rápido si una release rompe:

```bash
# Volver al commit anterior (deshace migraciones aplicadas con cuidado)
cd /opt/agora
git log --oneline -5
git checkout <hash-anterior>
docker compose -f infraestructura/docker-compose.prod.yml down
docker compose -f infraestructura/docker-compose.prod.yml up -d --build
# Si hubo migraciones nuevas, revertirlas: python manage.py migrate <app> <num>
```

Restauración desde backup:

```bash
gunzip < /opt/agora/backups/diarios/agora_YYYYMMDD_HHMMSS.sql.gz | \
  docker compose -f infraestructura/docker-compose.prod.yml exec -T db \
    psql -U agora -d agora
```

---

## 10. Monitorización mínima

Por ahora, manualmente. En Fase 4 (piloto) se evaluará añadir Prometheus / Grafana.

```bash
# Estado de los servicios
docker compose -f infraestructura/docker-compose.prod.yml ps

# Uso de recursos
docker stats --no-stream

# Logs recientes
docker compose -f infraestructura/docker-compose.prod.yml logs --tail=100 web
docker compose -f infraestructura/docker-compose.prod.yml logs --tail=100 db
docker compose -f infraestructura/docker-compose.prod.yml logs --tail=100 nginx

# Espacio en disco
df -h /opt/agora /var/lib/docker
```

Alertas que conviene configurar en el monitor estándar del grupo:
- VM caída
- Disco > 80 % lleno
- Contenedor `agora_web_prod` no responde
- Backup diario no se ejecutó (verificar fichero del día en `/opt/agora/backups/diarios/`)

---

## 11. Contactos y escalado

| Tipo de incidencia | Contactar |
|---|---|
| Caída VM, problema infraestructura | Sistemas Aspanias |
| Error de aplicación, bug, datos incorrectos | Innovación Aspanias |
| Cuestión RGPD, brecha de seguridad | Lex Digital + Federico Martínez (DPO interino) |
| Cualquier dato real comprometido | Federico Martínez (notificación AEPD < 72 h) |

---

## 12. Próximos hitos de operaciones

- **2.5.7** Registrar la aplicación ÁGORA en Entra ID (M365) y obtener
  CLIENT_ID/SECRET/TENANT. Pendiente Sistemas Aspanias.
- **2.5.8** Configurar Azure Blob para los documentos sanitarios escaneados
  (certificados de discapacidad, etc.).
- **3.0** Pre-piloto Fuentecillas: importar datos reales del Excel y formar
  al equipo.

---

*Despliegue interno v0.1 · 2026-05-19 · Federico Martínez (sponsor) +
Sistemas Aspanias*

# Arranque local de ÁGORA

## Requisitos previos

- Docker Desktop (Windows) o Docker Engine + Docker Compose.
- Make (en Windows: vía Git Bash, WSL o `choco install make`).

## Pasos

```bash
# 1) Copiar variables de entorno y editar secretos
cp backend/.env.example backend/.env
# Editar DJANGO_SECRET_KEY y, si procede, credenciales M365.

# 2) Arrancar contenedores
make up

# 3) Crear superusuario
make createsuperuser

# 4) Cargar datos sintéticos (20 personas por defecto)
make datos-sinteticos
```

## Acceso

- App: http://localhost:8000
- Admin: http://localhost:8000/admin/
- Bitácora: dentro del admin → "Registros de acceso (bitácora)".

## SSO Microsoft 365

Por defecto la pantalla de login muestra acceso por email. Para activar M365:

1. Crear la aplicación en Entra ID (Azure AD) con redirect URI `http://localhost:8000/accounts/microsoft/login/callback/`.
2. Rellenar `M365_CLIENT_ID`, `M365_CLIENT_SECRET`, `M365_TENANT_ID` en `backend/.env`.
3. Reiniciar el servicio web: `make rebuild`.

Validar SSO con cuenta no privilegiada antes de probar con cuentas de Gerencia.

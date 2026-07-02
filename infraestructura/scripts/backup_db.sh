#!/usr/bin/env bash
# Backup automático de la BD PostgreSQL de ÁGORA.
# Ejecutar diariamente por cron (root) en la VM:
#     0 3 * * * /opt/agora/infraestructura/scripts/backup_db.sh
#
# Política de retención (ajustable):
#   - Diarios: 7 días
#   - Semanales (cada domingo): 5 semanas
#   - Mensuales (día 1): 12 meses
#
# Los dumps se guardan en /opt/agora/backups, accesibles dentro del contenedor
# de Postgres en /backups. Conviene replicarlos también a Azure Blob o NAS
# cifrados (script aparte, fuera del scope de esta versión).

set -euo pipefail

BACKUP_DIR="/opt/agora/backups"
COMPOSE_FILE="/opt/agora/infraestructura/docker-compose.prod.yml"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DOW=$(date +%u)              # 1=lunes ... 7=domingo
DOM=$(date +%d)              # día del mes

mkdir -p "$BACKUP_DIR/diarios" "$BACKUP_DIR/semanales" "$BACKUP_DIR/mensuales"

DEST="$BACKUP_DIR/diarios/agora_${TIMESTAMP}.sql.gz"

echo "[$(date)] Iniciando backup en $DEST"

docker compose -f "$COMPOSE_FILE" exec -T db \
    pg_dump -U agora -d agora --clean --if-exists \
  | gzip > "$DEST"

# Verificación: el archivo no está vacío
if [ ! -s "$DEST" ]; then
    echo "[$(date)] ERROR: backup vacío. Abortando."
    exit 1
fi

# Copia semanal los domingos (DOW=7)
if [ "$DOW" = "7" ]; then
    cp "$DEST" "$BACKUP_DIR/semanales/agora_${TIMESTAMP}_semanal.sql.gz"
fi

# Copia mensual el día 1
if [ "$DOM" = "01" ]; then
    cp "$DEST" "$BACKUP_DIR/mensuales/agora_${TIMESTAMP}_mensual.sql.gz"
fi

# Rotación: borrar archivos viejos
find "$BACKUP_DIR/diarios" -name "*.sql.gz" -mtime +7 -delete
find "$BACKUP_DIR/semanales" -name "*.sql.gz" -mtime +35 -delete
find "$BACKUP_DIR/mensuales" -name "*.sql.gz" -mtime +366 -delete

# Resumen
TAMANIO=$(du -h "$DEST" | cut -f1)
echo "[$(date)] Backup OK · tamaño $TAMANIO · $(ls "$BACKUP_DIR/diarios" | wc -l) backups diarios"

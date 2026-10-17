#!/bin/bash

# Script de backup automático para TalentoFutPay
# Agregar a crontab: 0 2 * * * /ruta/a/backup.sh

# Configuración
BACKUP_DIR="/backups/talentofutpay"
DB_PATH="/ruta/completa/a/TALENTOFUTPAY/talentofutpay.db"
STATIC_PATH="/ruta/completa/a/TALENTOFUTPAY/static/img/creadoras"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Crear directorio de backups si no existe
mkdir -p $BACKUP_DIR

# Backup de la base de datos
echo "Realizando backup de la base de datos..."
cp $DB_PATH "$BACKUP_DIR/talentofutpay_$DATE.db"
gzip "$BACKUP_DIR/talentofutpay_$DATE.db"

# Backup de imágenes de creadoras
echo "Realizando backup de imágenes..."
tar -czf "$BACKUP_DIR/creadoras_$DATE.tar.gz" -C $STATIC_PATH .

# Eliminar backups antiguos (más de 30 días)
echo "Eliminando backups antiguos..."
find $BACKUP_DIR -name "talentofutpay_*.db.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "creadoras_*.tar.gz" -mtime +$RETENTION_DAYS -delete

# Log
echo "Backup completado: $DATE" >> "$BACKUP_DIR/backup.log"
echo "Archivos en backup:"
ls -lh $BACKUP_DIR | tail -5

echo "=== Backup completado exitosamente ==="

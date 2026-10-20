#!/bin/sh
set -eu
umask 077

mkdir -p /data/uploads

if [ -z "${TALENTOFUTPAY_SECRET_KEY:-}" ]; then
    if [ ! -s /data/talentofutpay.secret_key ]; then
        python -c 'import secrets; print(secrets.token_urlsafe(48))' > /data/talentofutpay.secret_key
        chmod 600 /data/talentofutpay.secret_key
    fi
    TALENTOFUTPAY_SECRET_KEY=$(cat /data/talentofutpay.secret_key)
    export TALENTOFUTPAY_SECRET_KEY
fi

# Copiar imágenes iniciales si no existen en /data/uploads
cp -an /app/initial-uploads/. /data/uploads/

# Crear symlink para que static/img apunte a /data/uploads
if [ ! -L /app/static/img ]; then
    rm -rf /app/static/img
    ln -s /data/uploads /app/static/img
fi

exec gunicorn --workers 2 --bind "0.0.0.0:${PORT:-5000}" app:app

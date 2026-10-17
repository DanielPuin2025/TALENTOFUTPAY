#!/bin/sh
set -eu
umask 077

mkdir -p /data/creadoras

if [ -z "${TALENTOFUTPAY_SECRET_KEY:-}" ]; then
    if [ ! -s /data/talentofutpay.secret_key ]; then
        python -c 'import secrets; print(secrets.token_urlsafe(48))' > /data/talentofutpay.secret_key
        chmod 600 /data/talentofutpay.secret_key
    fi
    TALENTOFUTPAY_SECRET_KEY=$(cat /data/talentofutpay.secret_key)
    export TALENTOFUTPAY_SECRET_KEY
fi

cp -an /app/initial-creadoras/. /data/creadoras/

exec gunicorn --workers 2 --bind "0.0.0.0:${PORT:-5000}" app:app

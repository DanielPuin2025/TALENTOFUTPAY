#!/bin/bash

# Script de inicio para TalentoFutPay en producción

echo "=== Iniciando TalentoFutPay ==="

# Crear directorios necesarios
mkdir -p logs
mkdir -p static/img/creadoras

# Verificar que existe el entorno virtual
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
source venv/bin/activate

# Instalar/actualizar dependencias
echo "Instalando dependencias..."
pip install -r requirements.txt
pip install gunicorn

# Verificar que existe la base de datos
if [ ! -f "talentofutpay.db" ]; then
    echo "Inicializando base de datos..."
    python3 -c "from app import init_database; init_database()"
fi

# Detener proceso anterior si existe
if [ -f "talentofutpay.pid" ]; then
    OLD_PID=$(cat talentofutpay.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "Deteniendo proceso anterior (PID: $OLD_PID)..."
        kill $OLD_PID
        sleep 2
    fi
    rm -f talentofutpay.pid
fi

# Iniciar con Gunicorn
echo "Iniciando servidor con Gunicorn..."
gunicorn -c gunicorn_config.py app:app &

echo "=== TalentoFutPay iniciado exitosamente ==="
echo "URL: http://talentofutpay.programamega.com"
echo "Logs: logs/access.log y logs/error.log"

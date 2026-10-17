# Comandos para Despliegue Rápido - TalentoFutPay

## 🚀 PASO 1: Conectar al Servidor

```bash
ssh usuario@144.126.156.160
# O el usuario que uses para conectarte
```

## 📦 PASO 2: Preparar el Servidor (si es necesario)

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y python3 python3-pip python3-venv nginx git certbot python3-certbot-nginx
```

## 📥 PASO 3: Clonar/Actualizar Repositorio

```bash
# Si es la primera vez:
cd /var/www/
sudo git clone https://github.com/DanielPuin2025/TALENTOFUTPAY.git
sudo chown -R $USER:$USER TALENTOFUTPAY
cd TALENTOFUTPAY

# Si ya existe (actualizar):
cd /var/www/TALENTOFUTPAY
git pull origin master
```

## 🔧 PASO 4: Configurar Entorno Python

```bash
# Crear entorno virtual (solo primera vez)
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
```

## 🗄️ PASO 5: Configurar Base de Datos y Directorios

```bash
# Crear directorios necesarios
mkdir -p logs
mkdir -p static/img/creadoras

# Dar permisos
chmod 755 static/img/creadoras
chmod 644 talentofutpay.db 2>/dev/null || true
```

## 🔒 PASO 6: Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Generar SECRET_KEY segura
echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')" >> .env

# Editar si es necesario
nano .env
```

## 🌐 PASO 7: Configurar Nginx

```bash
# Editar configuración de Nginx primero
nano nginx_config

# Buscar y reemplazar:
# /ruta/completa/a/TALENTOFUTPAY  →  /var/www/TALENTOFUTPAY

# Copiar configuración a Nginx
sudo cp nginx_config /etc/nginx/sites-available/talentofutpay

# Crear enlace simbólico
sudo ln -sf /etc/nginx/sites-available/talentofutpay /etc/nginx/sites-enabled/

# Eliminar configuración default si existe
sudo rm -f /etc/nginx/sites-enabled/default

# Verificar configuración
sudo nginx -t

# Si está OK, recargar Nginx
sudo systemctl reload nginx
```

## 🔐 PASO 8: Configurar SSL (Let's Encrypt)

```bash
# Obtener certificado SSL
sudo certbot --nginx -d talentofutpay.programamega.com

# Seguir las instrucciones en pantalla
# Seleccionar opción 2: Redirect (redirigir HTTP a HTTPS)
```

## 🚀 PASO 9: Configurar Servicio Systemd

```bash
# Crear archivo de servicio
sudo nano /etc/systemd/system/talentofutpay.service
```

Pegar este contenido:
```ini
[Unit]
Description=TalentoFutPay Gunicorn Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/TALENTOFUTPAY
Environment="PATH=/var/www/TALENTOFUTPAY/venv/bin"
ExecStart=/var/www/TALENTOFUTPAY/venv/bin/gunicorn -c gunicorn_config.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Luego ejecutar:
```bash
# Recargar systemd
sudo systemctl daemon-reload

# Habilitar servicio
sudo systemctl enable talentofutpay

# Iniciar servicio
sudo systemctl start talentofutpay

# Verificar estado
sudo systemctl status talentofutpay
```

## 💾 PASO 10: Configurar Backups Automáticos

```bash
# Editar script de backup
nano backup.sh

# Cambiar las rutas a:
# BACKUP_DIR="/backups/talentofutpay"
# DB_PATH="/var/www/TALENTOFUTPAY/talentofutpay.db"
# STATIC_PATH="/var/www/TALENTOFUTPAY/static/img/creadoras"

# Hacer ejecutable
chmod +x backup.sh

# Crear directorio de backups
sudo mkdir -p /backups/talentofutpay
sudo chown $USER:$USER /backups/talentofutpay

# Agregar a crontab
crontab -e

# Agregar esta línea al final:
0 2 * * * /var/www/TALENTOFUTPAY/backup.sh >> /var/www/TALENTOFUTPAY/logs/backup.log 2>&1
```

## 🔒 PASO 11: Configurar Firewall

```bash
# Configurar UFW
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 3000/tcp  # Para AsyPanel
sudo ufw --force enable
sudo ufw status
```

## ✅ PASO 12: Verificación Final

```bash
# Ver logs en tiempo real
tail -f logs/error.log

# Verificar servicio
sudo systemctl status talentofutpay

# Probar desde el navegador
# https://talentofutpay.programamega.com
```

## 🔄 Comandos de Mantenimiento

### Reiniciar la aplicación
```bash
sudo systemctl restart talentofutpay
```

### Ver logs
```bash
# Logs de la aplicación
tail -f /var/www/TALENTOFUTPAY/logs/error.log
tail -f /var/www/TALENTOFUTPAY/logs/access.log

# Logs de systemd
sudo journalctl -u talentofutpay -f
```

### Actualizar código
```bash
cd /var/www/TALENTOFUTPAY
git pull origin master
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart talentofutpay
```

### Backup manual
```bash
cd /var/www/TALENTOFUTPAY
./backup.sh
```

## 🆘 Solución de Problemas Rápida

### El servicio no inicia
```bash
sudo journalctl -u talentofutpay -n 50 --no-pager
```

### Error 502 Bad Gateway
```bash
sudo systemctl restart talentofutpay
sudo systemctl status talentofutpay
```

### Nginx no inicia
```bash
sudo nginx -t
sudo systemctl status nginx
```

### Permisos incorrectos
```bash
sudo chown -R www-data:www-data /var/www/TALENTOFUTPAY
sudo chmod 755 /var/www/TALENTOFUTPAY
sudo chmod 644 /var/www/TALENTOFUTPAY/talentofutpay.db
```

---

## 📱 URLs de Acceso

- **Aplicación**: https://talentofutpay.programamega.com
- **Usuario**: admin
- **Contraseña**: admin123 (¡CAMBIAR INMEDIATAMENTE!)

---

**Nota**: Después del despliegue, cambiar todas las contraseñas por defecto desde el panel de administración.

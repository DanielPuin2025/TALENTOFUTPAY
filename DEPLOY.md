# Guía de Despliegue en Producción - TalentoFutPay

Esta guía cubre el despliegue completo en el servidor de producción.

## 📋 Pre-requisitos

- Servidor Linux (Ubuntu/Debian recomendado)
- Python 3.8+
- Nginx
- Acceso SSH al servidor
- Dominio configurado: talentofutpay.programamega.com

## 🚀 Paso 1: Preparar el Servidor

### Actualizar el sistema
```bash
sudo apt update
sudo apt upgrade -y
```

### Instalar dependencias del sistema
```bash
sudo apt install -y python3 python3-pip python3-venv nginx git
```

## 📦 Paso 2: Clonar el Repositorio

```bash
cd /var/www/
sudo git clone https://github.com/DanielPuin2025/TALENTOFUTPAY.git
sudo chown -R $USER:$USER TALENTOFUTPAY
cd TALENTOFUTPAY
```

## 🔧 Paso 3: Configurar el Entorno Python

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## 🗄️ Paso 4: Configurar la Base de Datos

```bash
# Crear directorios necesarios
mkdir -p logs
mkdir -p static/img/creadoras

# La base de datos se inicializa automáticamente al primer arranque
# O puedes inicializarla manualmente:
python3 -c "from app import init_database; init_database()"
```

## 🔒 Paso 5: Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar configuración
nano .env
```

**Importante**: Cambiar `SECRET_KEY` por una clave aleatoria segura:
```bash
# Generar clave segura
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## 🌐 Paso 6: Configurar Nginx

```bash
# Copiar configuración
sudo cp nginx_config /etc/nginx/sites-available/talentofutpay

# Editar y ajustar rutas
sudo nano /etc/nginx/sites-available/talentofutpay

# Cambiar esta línea con la ruta real:
# alias /ruta/completa/a/TALENTOFUTPAY/static;
# Por:
# alias /var/www/TALENTOFUTPAY/static;

# Crear enlace simbólico
sudo ln -s /etc/nginx/sites-available/talentofutpay /etc/nginx/sites-enabled/

# Verificar configuración
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

## 🔐 Paso 7: Configurar SSL con Let's Encrypt

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtener certificado SSL
sudo certbot --nginx -d talentofutpay.programamega.com

# Renovación automática (ya configurada)
sudo certbot renew --dry-run
```

## 🚀 Paso 8: Configurar Servicio Systemd

Crear archivo de servicio:
```bash
sudo nano /etc/systemd/system/talentofutpay.service
```

Contenido:
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

[Install]
WantedBy=multi-user.target
```

Activar servicio:
```bash
sudo systemctl daemon-reload
sudo systemctl enable talentofutpay
sudo systemctl start talentofutpay
sudo systemctl status talentofutpay
```

## 💾 Paso 9: Configurar Backups Automáticos

```bash
# Editar script de backup con rutas correctas
nano backup.sh

# Cambiar:
# BACKUP_DIR="/backups/talentofutpay"
# DB_PATH="/ruta/completa/a/TALENTOFUTPAY/talentofutpay.db"
# STATIC_PATH="/ruta/completa/a/TALENTOFUTPAY/static/img/creadoras"

# Por:
# BACKUP_DIR="/backups/talentofutpay"
# DB_PATH="/var/www/TALENTOFUTPAY/talentofutpay.db"
# STATIC_PATH="/var/www/TALENTOFUTPAY/static/img/creadoras"

# Hacer ejecutable
chmod +x backup.sh

# Crear directorio de backups
sudo mkdir -p /backups/talentofutpay
sudo chown $USER:$USER /backups/talentofutpay

# Agregar a crontab (ejecutar a las 2 AM diariamente)
crontab -e

# Agregar esta línea:
0 2 * * * /var/www/TALENTOFUTPAY/backup.sh >> /var/www/TALENTOFUTPAY/logs/backup.log 2>&1
```

## 🔄 Paso 10: Actualizar la Aplicación

Cuando necesites actualizar el código:

```bash
cd /var/www/TALENTOFUTPAY

# Descargar cambios
git pull origin master

# Activar entorno virtual
source venv/bin/activate

# Actualizar dependencias
pip install -r requirements.txt

# Reiniciar servicio
sudo systemctl restart talentofutpay
```

## 📊 Monitoreo y Logs

### Ver logs de la aplicación
```bash
# Logs de Gunicorn
tail -f /var/www/TALENTOFUTPAY/logs/access.log
tail -f /var/www/TALENTOFUTPAY/logs/error.log

# Logs de Nginx
sudo tail -f /var/log/nginx/talentofutpay_access.log
sudo tail -f /var/log/nginx/talentofutpay_error.log

# Logs del servicio systemd
sudo journalctl -u talentofutpay -f
```

### Verificar estado del servicio
```bash
sudo systemctl status talentofutpay
```

### Reiniciar servicio
```bash
sudo systemctl restart talentofutpay
```

## 🔒 Seguridad Post-Despliegue

### 1. Cambiar contraseñas por defecto
Acceder a: https://talentofutpay.programamega.com
- Login: admin / admin123
- Ir a: Cambiar contraseña

### 2. Configurar firewall
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. Permisos de archivos
```bash
cd /var/www/TALENTOFUTPAY
chmod 600 .env
chmod 644 talentofutpay.db
chmod 755 static/img/creadoras
```

### 4. Actualizar SECRET_KEY en app.py
```bash
nano app.py
```

Buscar y cambiar:
```python
app.secret_key = "clave_secreta_cambiar_en_produccion"
```

Por una clave generada:
```python
app.secret_key = "tu_clave_aleatoria_muy_larga_de_64_caracteres_minimo_generada"
```

## 🧪 Verificación

### 1. Verificar que el sitio está activo
```bash
curl -I https://talentofutpay.programamega.com
```

Debe retornar: `HTTP/2 200`

### 2. Verificar certificado SSL
```bash
openssl s_client -connect talentofutpay.programamega.com:443 -servername talentofutpay.programamega.com
```

### 3. Probar la aplicación
- Acceder a: https://talentofutpay.programamega.com
- Login con admin/admin123
- Verificar todas las funcionalidades

## 📞 Solución de Problemas

### El sitio no carga
```bash
# Verificar Nginx
sudo systemctl status nginx
sudo nginx -t

# Verificar Gunicorn
sudo systemctl status talentofutpay
sudo journalctl -u talentofutpay -n 50
```

### Error 502 Bad Gateway
```bash
# El servicio Gunicorn no está corriendo
sudo systemctl start talentofutpay
sudo systemctl status talentofutpay
```

### Error de permisos
```bash
sudo chown -R www-data:www-data /var/www/TALENTOFUTPAY
sudo chmod 755 /var/www/TALENTOFUTPAY
```

## 📱 URLs Importantes

- **Aplicación**: https://talentofutpay.programamega.com
- **Repositorio GitHub**: https://github.com/DanielPuin2025/TALENTOFUTPAY
- **Panel AsyPanel**: http://144.126.156.160:3000/projects/yearbook/app/talentofutpay

## 🎯 Checklist Final

- [ ] Servidor actualizado
- [ ] Dependencias instaladas
- [ ] Repositorio clonado
- [ ] Entorno virtual creado
- [ ] Base de datos inicializada
- [ ] Nginx configurado
- [ ] SSL configurado
- [ ] Servicio systemd activado
- [ ] Backups configurados
- [ ] Contraseñas cambiadas
- [ ] Firewall configurado
- [ ] Sitio verificado

---

**¡Listo!** Tu aplicación TalentoFutPay está desplegada y lista para producción.

# Configuración en AsyPanel - TalentoFutPay

## 📋 Información del Proyecto

- **Nombre del Proyecto**: talentofutpay
- **URL AsyPanel**: http://144.126.156.160:3000/projects/yearbook/app/talentofutpay
- **URL Producción**: https://talentofutpay.programamega.com
- **Repositorio**: https://github.com/DanielPuin2025/TALENTOFUTPAY

## 🚀 Configuración en AsyPanel

### 1. Acceder al Panel
```
URL: http://144.126.156.160:3000
Navegar a: Projects > yearbook > app > talentofutpay
```

### 2. Configuración del Proyecto

#### **General Settings**
```
Project Name: talentofutpay
Project Type: Python/Flask Application
Port: 5000
Domain: talentofutpay.programamega.com
```

#### **Repository Configuration**
```
Repository URL: https://github.com/DanielPuin2025/TALENTOFUTPAY.git
Branch: master
Auto Deploy: Enabled (opcional)
```

#### **Build Configuration**
```bash
# Build Command
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
mkdir -p logs static/img/creadoras
```

#### **Start Command**
```bash
source venv/bin/activate && gunicorn -c gunicorn_config.py app:app
```

#### **Environment Variables**
```env
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=<generar_clave_aleatoria_segura>
DATABASE_PATH=talentofutpay.db
HOST=0.0.0.0
PORT=5000
DOMAIN=talentofutpay.programamega.com
```

### 3. Configuración de Dominio

#### **Custom Domain**
```
Domain: talentofutpay.programamega.com
SSL/TLS: Enabled (Let's Encrypt)
Force HTTPS: Yes
```

#### **DNS Configuration**
Asegúrate de que el dominio apunte al servidor:
```
Type: A
Name: talentofutpay
Value: 144.126.156.160
TTL: 3600
```

### 4. Configuración de Procesos

#### **Process Manager**
```
Process Name: talentofutpay
Command: gunicorn -c gunicorn_config.py app:app
Working Directory: /var/www/TALENTOFUTPAY
Auto Restart: Yes
Instances: 2-4 (según CPU)
```

### 5. Configuración de Logs

#### **Log Files**
```
Access Log: logs/access.log
Error Log: logs/error.log
Application Log: logs/app.log
```

#### **Log Rotation**
```
Max Size: 100MB
Keep Files: 10
Compress: Yes
```

### 6. Backup Configuration

#### **Automated Backups**
```
Backup Type: Database + Files
Schedule: Daily at 2:00 AM
Retention: 30 days
Location: /backups/talentofutpay
```

#### **Backup Script**
```bash
# Usar el script incluido
/var/www/TALENTOFUTPAY/backup.sh
```

### 7. Monitoring

#### **Health Check**
```
URL: https://talentofutpay.programamega.com/
Method: GET
Interval: 5 minutes
Timeout: 30 seconds
Expected Status: 200
```

#### **Alerts**
```
Email: tu_email@example.com
Alert on: Down, High CPU, High Memory
Threshold CPU: 80%
Threshold Memory: 80%
```

### 8. Security Settings

#### **Firewall Rules**
```
Allow Port 80 (HTTP)
Allow Port 443 (HTTPS)
Allow Port 22 (SSH) - Only from specific IPs
Block all other ports
```

#### **SSL/TLS**
```
Certificate: Let's Encrypt (Auto-renew)
TLS Version: 1.2, 1.3
HSTS: Enabled
```

### 9. Performance Optimization

#### **Caching**
```
Static Files Cache: 30 days
Browser Cache: Enabled
Gzip Compression: Enabled
```

#### **Resource Limits**
```
Max Upload Size: 16MB
Max Request Size: 20MB
Connection Timeout: 60s
Worker Timeout: 60s
```

## 🔄 Despliegue desde AsyPanel

### Opción 1: Despliegue Automático
1. Ir a: Projects > talentofutpay > Deployments
2. Click en "New Deployment"
3. Seleccionar branch "master"
4. Click en "Deploy"

### Opción 2: Despliegue Manual desde SSH
```bash
# Conectar al servidor
ssh usuario@144.126.156.160

# Ir al proyecto
cd /var/www/TALENTOFUTPAY

# Actualizar código
git pull origin master

# Activar entorno
source venv/bin/activate

# Actualizar dependencias
pip install -r requirements.txt

# Reiniciar desde AsyPanel o systemd
sudo systemctl restart talentofutpay
```

## 📊 Monitoreo en AsyPanel

### Métricas a Monitorear
- **CPU Usage**: < 70%
- **Memory Usage**: < 80%
- **Disk Usage**: < 85%
- **Response Time**: < 500ms
- **Uptime**: > 99.5%

### Ver Métricas
```
AsyPanel > Projects > talentofutpay > Monitoring
```

## 🔧 Comandos Útiles en AsyPanel

### Restart Application
```bash
# Desde AsyPanel Terminal
cd /var/www/TALENTOFUTPAY
sudo systemctl restart talentofutpay
```

### View Logs
```bash
# Logs en tiempo real
tail -f logs/error.log
tail -f logs/access.log

# Últimas 100 líneas
tail -n 100 logs/error.log
```

### Database Backup
```bash
# Backup manual
./backup.sh

# Ver backups
ls -lh /backups/talentofutpay/
```

### Check Status
```bash
# Estado del servicio
sudo systemctl status talentofutpay

# Procesos activos
ps aux | grep gunicorn
```

## 🆘 Troubleshooting en AsyPanel

### Aplicación no responde
1. Ver logs en AsyPanel > Logs
2. Verificar estado: `sudo systemctl status talentofutpay`
3. Reiniciar: `sudo systemctl restart talentofutpay`

### Error 502 Bad Gateway
1. Verificar que Gunicorn está corriendo
2. Ver logs: `sudo journalctl -u talentofutpay -n 50`
3. Revisar configuración de Nginx
4. Reiniciar servicios

### Alta carga de CPU/Memoria
1. Ver métricas en AsyPanel
2. Identificar procesos: `top` o `htop`
3. Ajustar workers en `gunicorn_config.py`
4. Reiniciar aplicación

### SSL no funciona
1. Verificar certificado: AsyPanel > SSL/TLS
2. Renovar certificado: `sudo certbot renew`
3. Verificar configuración Nginx
4. Reiniciar Nginx: `sudo systemctl restart nginx`

## 📱 Acceso Rápido

### Panel de Control
```
http://144.126.156.160:3000/projects/yearbook/app/talentofutpay
```

### Aplicación en Producción
```
https://talentofutpay.programamega.com
```

### Repositorio GitHub
```
https://github.com/DanielPuin2025/TALENTOFUTPAY
```

## ✅ Checklist de Configuración

- [ ] Proyecto creado en AsyPanel
- [ ] Repositorio conectado
- [ ] Variables de entorno configuradas
- [ ] Dominio personalizado configurado
- [ ] SSL/TLS habilitado
- [ ] Proceso de inicio configurado
- [ ] Logs configurados
- [ ] Backups automáticos configurados
- [ ] Monitoreo activo
- [ ] Alertas configuradas
- [ ] Firewall configurado
- [ ] Aplicación desplegada y funcionando
- [ ] Contraseñas por defecto cambiadas

## 🔐 Seguridad Post-Configuración

1. **Cambiar contraseñas por defecto**
   - Login: https://talentofutpay.programamega.com
   - Usuario: admin / admin123
   - Ir a: Cambiar contraseña

2. **Configurar backups externos**
   - Descargar backups periódicamente
   - Almacenar en ubicación externa segura

3. **Actualizar SECRET_KEY**
   - Generar nueva clave
   - Actualizar en AsyPanel > Environment Variables
   - Reiniciar aplicación

4. **Monitorear logs regularmente**
   - Revisar intentos de acceso fallidos
   - Detectar patrones anómalos

---

**¡Configuración completa!** TalentoFutPay está listo para producción en AsyPanel.

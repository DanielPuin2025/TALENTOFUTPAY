# TalentoFutPay - Sistema de Gestión para Fútbol Femenino

Sistema completo de gestión administrativa y financiera para equipos de fútbol formativo femenino.

## 🚀 Características Principales

- **Gestión de Jugadoras**: Registro completo con datos de acudientes y estados
- **Control de Pagos**: Sistema de mensualidad fija ($80.000) con control de saldos pendientes
- **Gestión de Torneos**: Creación de torneos e inscripción de jugadoras
- **Sistema de Roles**: Admin, Instructor y Tesorero con permisos específicos
- **Recordatorios por WhatsApp**: Mensajes automáticos con deuda detallada y medios de pago
- **Reportes**: Exportación en PDF y CSV
- **Panel de Administración**: Gestión completa de usuarios y creadoras
- **Gestión de Creadoras**: Módulo para actualizar información y fotos del equipo

## 📋 Requisitos del Sistema

- Python 3.8 o superior
- Flask 2.3.0+
- SQLite3
- Dependencias listadas en `requirements.txt`

## 🔧 Instalación Local

1. **Clonar el repositorio:**
```bash
git clone https://github.com/DanielPuin2025/TALENTOFUTPAY.git
cd TALENTOFUTPAY
```

2. **Crear entorno virtual:**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Ejecutar la aplicación:**
```bash
python app.py
```

5. **Acceder al sistema:**
```
http://localhost:5000
```

## 👤 Acceso

Configura las cuentas iniciales mediante variables privadas en Easypanel. No uses
credenciales predeterminadas en producción; una base de datos existente conserva
las cuentas guardadas y cambiar las variables no cambia sus contraseñas.

## 📁 Estructura del Proyecto

```
TALENTOFUTPAY/
├── app.py                      # Aplicación principal Flask
├── requirements.txt           # Dependencias Python
├── README.md                  # Este archivo
├── GUIA_PRUEBAS.md           # Guía detallada de pruebas
├── static/
│   ├── css/
│   │   └── app.css           # Estilos globales
│   └── img/
│       ├── creadoras/        # Fotos de las creadoras
│       ├── logo-transparente.png
│       ├── fondo1.jpg
│       └── fondo2.jpg
└── templates/
    ├── index.html            # Página de inicio/login
    ├── dashboard.html        # Dashboard principal
    ├── jugadoras.html        # Gestión de jugadoras
    ├── pagos.html           # Gestión de pagos
    ├── reportes.html        # Reportes y estadísticas
    ├── torneos.html         # Gestión de torneos
    ├── acerca.html          # Información del proyecto
    ├── panel_admin.html     # Panel de administración
    ├── admin_usuarios.html  # Gestión de usuarios
    ├── admin_creadoras.html # Gestión de creadoras
    └── ...
```

## 🗄️ Base de Datos

El sistema utiliza SQLite con las siguientes tablas:

- **jugadoras**: Información de las jugadoras y acudientes
- **pagos**: Registro de pagos con control de saldos pendientes
- **usuarios**: Cuentas de acceso al sistema
- **torneos**: Eventos y competencias
- **inscripciones_torneo**: Relación jugadoras-torneos
- **creadoras**: Información del equipo de desarrollo
- **configuracion**: Configuraciones del sistema

## 💰 Sistema de Pagos

### Mensualidad Fija: $80.000

- **Pagos completos**: Se registran como "Pagado"
- **Pagos parciales**: Se calcula el saldo pendiente automáticamente
- **Validación**: No permite pagar meses siguientes si hay deudas anteriores
- **Recordatorios**: Incluyen deuda total, desglose por mes y medios de pago

### Ejemplo de Flujo de Pagos:

1. Jugadora debe $80.000 de Enero
2. Paga solo $50.000
3. Sistema registra: Saldo pendiente = $30.000
4. No puede pagar Febrero hasta completar Enero
5. Recordatorio por WhatsApp muestra: "Deuda total: $30.000, Enero: $30.000"

## 👥 Sistema de Roles y Permisos

### Administrador
- Acceso total al sistema
- CRUD completo de todos los módulos
- Gestión de usuarios y creadoras
- Panel de administración

### Instructor
- Gestión de jugadoras
- Crear torneos e inscribir jugadoras
- Crear pagos (no eliminar)
- Ver reportes

### Tesorero
- Crear pagos (no eliminar)
- Enviar recordatorios por WhatsApp
- Ver reportes
- No accede a jugadoras ni torneos

## 📱 Integración con WhatsApp

Los recordatorios de pago se envían vía WhatsApp Web con:
- Nombre del acudiente
- Deuda total acumulada
- Desglose por mes
- Medios de pago disponibles (Efectivo, Transferencia, Nequi)

Formato del mensaje:
```
Hola [Acudiente], le recordamos que la jugadora [Nombre] 
tiene pagos pendientes.

📊 Deuda total: $XX.XXX

Detalle:
Enero: $XX.XXX, Febrero: $XX.XXX

💳 Medios de pago:
• Efectivo
• Transferencia bancaria
• Nequi

Por favor, comuníquese con nosotros para ponerse al día. Gracias.
```

## 🚀 Despliegue en Easypanel

Sigue [DEPLOY_QUICKSTART.md](./DEPLOY_QUICKSTART.md) para configurar GitHub,
Dockerfile, secretos, volúmenes persistentes, dominio y verificación de salud.

## 🔒 Seguridad en Producción

1. Configurar `TALENTOFUTPAY_SECRET_KEY` como secreto privado en Easypanel.
2. Usar contraseñas fuertes y únicas; no guardar secretos en GitHub.
3. Mantener almacenamiento persistente y respaldos recuperables.
4. Configurar el dominio con HTTPS.

## 📊 Respaldos

El sistema incluye función de respaldo automático:
- Ir a menú → "Descargar respaldo"
- Se descarga el archivo `talentofutpay_respaldo.db`
- Guardar en lugar seguro fuera del servidor

## 🆘 Solución de Problemas

### Error: "Usuario o contraseña incorrectos"
- Verificar que la base persistente contenga las cuentas esperadas.
- Cambiar la contraseña desde la opción de administración correspondiente.

### Error: "No se puede subir foto"
- Verificar permisos del directorio `static/img/creadoras/`
- Verificar formato de imagen (JPG, PNG, GIF)

### Error: "No se puede registrar pago"
- Verificar que no haya deudas de meses anteriores
- Verificar que el mes no esté duplicado

## 📞 Contacto y Soporte

- **Repositorio**: https://github.com/DanielPuin2025/TALENTOFUTPAY
- **Producción**: https://talentofutpay.programamega.com
- **Panel**: http://144.126.156.160:3000/projects/yearbook/app/talentofutpay

## 📝 Licencia

© 2025 TalentoFutPay - Todos los derechos reservados

## 🙏 Créditos

Desarrollado para la gestión profesional de equipos de fútbol formativo femenino.

# 🏆 TalentoFutPay - Guía de Pruebas

## 📋 Resumen de Cambios Implementados

### ✅ Mejoras Visuales
- ✅ **Eliminados los balones girando** - Reemplazados por iconos profesionales flotantes (⚽🏆💳📊)
- ✅ **Footer agregado** - Derechos reservados para TalentoFutPay con enlace a página de creadoras
- ✅ **Página "Acerca de"** - Sección dedicada con información de las creadoras del proyecto

### ✅ Sistema de Roles Completo
- ✅ **Administrador**: Acceso total al sistema, puede modificar todo el CRUD
- ✅ **Instructor**: Gestión de jugadoras, crear torneos, inscribir jugadoras, crear pagos (no eliminar)
- ✅ **Tesorero**: Crear pagos, enviar recordatorios por WhatsApp (no eliminar pagos)

### ✅ Gestión de Torneos
- ✅ **Crear torneos** - Los instructores pueden crear eventos y competencias
- ✅ **Inscribir jugadoras** - Asignar jugadoras a torneos específicos
- ✅ **Ver inscripciones** - Listado completo de jugadoras por torneo
- ✅ **Editar/Eliminar torneos** - Solo administradores

### ✅ Panel de Administración
- ✅ **Gestión de usuarios** - Crear, editar y eliminar usuarios del sistema
- ✅ **Asignación de roles** - Control completo de permisos
- ✅ **Estadísticas generales** - Vista consolidada del sistema

### ✅ Formato de Valores
- ✅ **Valores en miles de pesos** - Formato: $50.000 (sin "COP" duplicado)
- ✅ **Consistencia en toda la aplicación**

---

## 🚀 Cómo Probar la Aplicación

### 1️⃣ Acceder al Sistema

Abre tu navegador y ve a: **http://127.0.0.1:5000**

### 2️⃣ Usuarios de Prueba

La aplicación viene con 3 usuarios predeterminados:

| Usuario | Contraseña | Rol | Permisos |
|---------|-----------|-----|----------|
| **admin** | admin123 | Administrador | Acceso total, CRUD completo |
| **instructor** | instructor123 | Instructor | Jugadoras, torneos, pagos (sin eliminar) |
| **tesorero** | tesorero123 | Tesorero | Pagos y recordatorios |

---

## 🧪 Casos de Prueba por Rol

### 🛡️ ADMINISTRADOR (admin / admin123)

#### Probar Panel de Administración:
1. Inicia sesión con: `admin` / `admin123`
2. En el menú lateral, haz clic en **"Panel Administrador"**
3. Verás estadísticas generales del sistema

#### Gestión de Usuarios:
1. En el Panel Administrador, clic en **"Administrar Usuarios"**
2. Crea un nuevo usuario:
   - Usuario: `prueba1`
   - Contraseña: `Prueba123!`
   - Rol: Instructor
3. Edita el usuario creado
4. **NO** elimines el usuario todavía

#### Gestión de Jugadoras:
1. Ve a **"Jugadoras"**
2. Registra una nueva jugadora:
   - Nombre: María López
   - Edad: 15
   - Posición: Delantera
   - Mensualidad: 50000
   - Nombre acudiente: Pedro López
   - Teléfono: 3001234567
   - Estado: Activa
3. Edita la jugadora
4. Verifica que aparece el botón de WhatsApp

#### Gestión de Pagos:
1. Ve a **"Pagos"**
2. Crea un pago:
   - Jugadora: María López
   - Mes: Enero
   - Fecha: Hoy
   - Valor: 50000
   - Método: Efectivo
   - Estado: Pagado
3. Verifica el formato del valor: $50.000 (sin COP al lado)
4. Edita el pago
5. Intenta eliminar el pago (solo admin puede)

#### Gestión de Torneos:
1. Ve a **"Torneos"**
2. Crea un nuevo torneo:
   - Nombre: Torneo Inter-Escuelas 2025
   - Fecha inicio: 01/03/2025
   - Fecha fin: 15/03/2025
   - Ubicación: Estadio Municipal
   - Descripción: Torneo de fútbol femenino
3. Inscribe a María López en el torneo
4. Ve a **"Ver Inscritas"** para verificar
5. Edita el torneo
6. **NO** elimines el torneo todavía

#### Reportes:
1. Ve a **"Reportes"**
2. Verifica las estadísticas
3. Descarga el CSV
4. Descarga el PDF
5. Verifica que los valores estén en formato de miles

---

### ⚽ INSTRUCTOR (instructor / instructor123)

1. **Cierra sesión** del administrador
2. Inicia sesión con: `instructor` / `instructor123`

#### Verificar Permisos:
- ✅ Debe ver: Jugadoras, Pagos, Torneos, Recordatorios
- ❌ NO debe ver: Panel Administrador
- ❌ NO debe poder eliminar pagos
- ✅ Debe poder crear torneos
- ✅ Debe poder inscribir jugadoras en torneos

#### Probar Funcionalidades:
1. Ve a **"Jugadoras"** y registra una nueva:
   - Nombre: Ana García
   - Edad: 14
   - Posición: Mediocampista
   - Mensualidad: 45000

2. Ve a **"Pagos"** y crea un pago para Ana García
   - Mes: Enero
   - Valor: 45000
   - Estado: Pendiente

3. **Intenta eliminar el pago** - Debe aparecer error de permisos

4. Ve a **"Torneos"** y crea otro torneo:
   - Nombre: Copa Primavera 2025
   - Fechas: A tu elección

5. Inscribe a Ana García en el torneo

6. Verifica que puedes ver las inscripciones

---

### 💰 TESORERO (tesorero / tesorero123)

1. **Cierra sesión** del instructor
2. Inicia sesión con: `tesorero` / `tesorero123`

#### Verificar Permisos:
- ✅ Debe ver: Pagos, Reportes, Recordatorios
- ❌ NO debe ver: Jugadoras, Torneos, Panel Administrador
- ✅ Debe poder crear pagos
- ❌ NO debe poder eliminar pagos

#### Probar Funcionalidades:
1. Ve a **"Pagos"**
2. Crea un nuevo pago (si hay jugadoras registradas)
3. **Intenta eliminar un pago** - Debe aparecer error

4. Ve a **"Recordatorios"**
5. Verifica los pagos pendientes
6. Haz clic en el botón de WhatsApp (abrirá WhatsApp Web)

7. Ve a **"Reportes"**
8. Descarga el CSV de pagos
9. Descarga el PDF de reportes

---

## 🔍 Verificaciones Importantes

### ✅ Formato de Valores
Verifica en TODAS las pantallas que los valores aparezcan como:
- ✅ **Correcto**: $50.000
- ❌ **Incorrecto**: $50.000 COP COP (duplicado)

### ✅ Iconos en Página de Inicio
1. Ve a la página de inicio (cierra sesión)
2. Verifica que:
   - ✅ NO hay balones girando
   - ✅ Hay iconos flotantes profesionales (⚽🏆💳📊)
   - ✅ Aparece el footer con derechos reservados
   - ✅ El enlace "Ver Creadoras" funciona

### ✅ Página Acerca de
1. En la página de inicio, haz clic en **"Ver Creadoras"**
2. Verifica que aparece información de las creadoras
3. Haz clic en **"Volver al inicio"**

### ✅ Funcionalidad de WhatsApp
1. Asegúrate de haber registrado jugadoras con teléfonos válidos
2. Ve a **"Recordatorios"**
3. Haz clic en el botón de WhatsApp
4. Verifica que se abre WhatsApp Web con el mensaje pre-escrito

---

## 🐛 Problemas Comunes y Soluciones

### Problema: "No puedo acceder a una sección"
**Solución**: Verifica que tu rol tiene permisos. Los permisos son:
- Admin: TODO
- Instructor: Jugadoras, Pagos (crear), Torneos
- Tesorero: Pagos (crear), Reportes, Recordatorios

### Problema: "Los valores aparecen mal formateados"
**Solución**: Verifica que estés usando el filtro `|cop` en las plantillas

### Problema: "No veo el Panel Administrador"
**Solución**: Solo visible para usuarios con rol 'admin'

### Problema: "El botón de WhatsApp no funciona"
**Solución**: Asegúrate de que:
1. La jugadora tiene un teléfono registrado
2. El teléfono tiene el formato correcto (10 dígitos)
3. El pago está en estado "Pendiente"

---

## 📊 Funcionalidades Clave Implementadas

### ✅ Sistema de Roles
- Cada rol tiene permisos específicos
- Validación en el backend y frontend
- Mensajes de error claros

### ✅ Gestión de Torneos
- CRUD completo de torneos
- Inscripción de jugadoras
- Historial de inscripciones
- Control por instructor

### ✅ Panel de Administración
- Vista consolidada del sistema
- Gestión de usuarios
- Estadísticas en tiempo real
- Acceso a todos los módulos

### ✅ Recordatorios por WhatsApp
- Generación automática de enlaces
- Mensajes personalizados
- Información del pago pendiente
- Integración con WhatsApp Web

### ✅ Reportes
- Exportación a CSV
- Exportación a PDF
- Filtros por mes y estado
- Formato profesional

---

## 🔐 Cambiar Contraseñas

Todos los usuarios pueden cambiar su contraseña:
1. En el menú lateral, haz clic en **"Cambiar contraseña"**
2. Ingresa la contraseña actual
3. Ingresa la nueva contraseña (mínimo 8 caracteres, con mayúscula, minúscula, número y símbolo)
4. Confirma la nueva contraseña

---

## 💾 Respaldo de Datos

Para descargar un respaldo de la base de datos:
1. En el menú lateral, haz clic en **"Descargar respaldo"**
2. Se descargará el archivo `talentofutpay_respaldo.db`
3. Guárdalo en un lugar seguro

---

## 📝 Notas Finales

- La aplicación está lista para producción
- Todos los valores están en formato de miles de pesos colombianos
- El sistema de roles funciona correctamente
- Los torneos están completamente integrados
- El panel de administración está operativo
- Las creadoras tienen su sección dedicada
- El diseño es profesional y sin elementos infantiles

---

## 🎉 ¡Listo para Usar!

El sistema **TalentoFutPay** está completamente funcional y listo para gestionar tu equipo de fútbol femenino de manera profesional y eficiente.

**© 2025 TalentoFutPay - Todos los derechos reservados**

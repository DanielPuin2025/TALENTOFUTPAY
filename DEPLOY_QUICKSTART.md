# Despliegue rápido en Easypanel

Esta guía despliega la rama `master` de GitHub mediante el `Dockerfile` de la raíz.
La aplicación escucha en el puerto `5000` y guarda SQLite en `/data/talentofutpay.db`.

## Antes de desplegar

1. Confirma que tienes una copia externa reciente y recuperable de la base de datos y
   las imágenes subidas.
2. No elimines el volumen existente `talentofutpay-data` montado en `/data`: contiene
   la base de datos de producción.
3. Si existen fotos subidas en el contenedor actual, cópialas al volumen `/data`
   antes del despliegue:

   ```sh
   mkdir -p /data/creadoras
   if [ -d /app/static/img/creadoras ]; then
     cp -an /app/static/img/creadoras/. /data/creadoras/
   fi
   ```
4. Asegúrate de que GitHub `master` contiene el `Dockerfile` y la revisión que vas a
   publicar.

## Configuración de Easypanel

En `Projects > yearbook > talentofutpay`, usa estos valores:

### Fuente

- Proveedor: **GitHub**
- Repositorio: `DanielPuin2025/TALENTOFUTPAY`
- Rama: `master`
- Ruta de compilación: `/`

### Compilación

- Constructor: **Dockerfile**
- Archivo: `Dockerfile`

### Almacenamiento persistente

- Conserva el volumen existente `talentofutpay-data` montado en `/data`.
- El mismo volumen `/data` conserva también las fotos en `/data/creadoras`; el
  contenedor las sirve desde `static/img/creadoras`.

### Variables de entorno

Configura los valores en Easypanel, nunca en Git:

```env
TALENTOFUTPAY_SECRET_KEY=<clave aleatoria larga y privada>
TALENTOFUTPAY_DATABASE_PATH=/data/talentofutpay.db
PORT=5000
```

Genera una clave con `python -c "import secrets; print(secrets.token_urlsafe(48))"`
y guárdala directamente como secreto en Easypanel.

`TALENTOFUTPAY_USER` y `TALENTOFUTPAY_PASSWORD` solo inicializan la cuenta admin
cuando la base de datos no contiene esa cuenta. Actualizar estas variables no cambia
las credenciales almacenadas en una base existente.

### Dominio y salud

- Mantén el dominio `talentofutpay.programamega.com`.
- Puerto interno: `5000`.
- HTTPS: habilitado.
- Comprobación de salud: `GET /health` (espera HTTP 200).

## Desplegar y verificar

1. Guarda los cambios de fuente, variables y volúmenes.
2. Inicia un despliegue manual desde Easypanel.
3. Revisa los registros de compilación y confirma que Gunicorn inicia sin errores.
4. Comprueba `https://talentofutpay.programamega.com/health`.
5. Inicia sesión y confirma que los registros existentes siguen presentes.

Si la compilación falla o la aplicación no queda saludable, no elimines ni recrees
el volumen `/data`. Vuelve a la configuración de fuente anterior y revisa los
registros antes de intentar otro despliegue.

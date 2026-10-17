# Configuración de TalentoFutPay en Easypanel

## Servicio

- Proyecto: `yearbook`
- Servicio: `talentofutpay`
- Repositorio: `DanielPuin2025/TALENTOFUTPAY`
- Rama de producción: `master`
- Constructor: **Dockerfile**
- Archivo: `/Dockerfile`
- Ruta de compilación: `/`
- Puerto interno: `5000`
- Dominio: `talentofutpay.programamega.com` con HTTPS

El `Dockerfile` instala `requirements.txt`, ejecuta Gunicorn en `0.0.0.0:5000` y
define `TALENTOFUTPAY_DATABASE_PATH=/data/talentofutpay.db`.

## Volúmenes

Conserva el volumen existente `talentofutpay-data` en `/data`; no lo borres ni lo
reemplaces al cambiar de rama o reconstruir el contenedor. La aplicación guarda allí
la base de datos y las fotos subidas (`/data/creadoras`).

Antes del primer despliegue de esta versión, copia las fotos del contenedor actual
al volumen persistente:

```sh
mkdir -p /data/creadoras
if [ -d /app/static/img/creadoras ]; then
  cp -an /app/static/img/creadoras/. /data/creadoras/
fi
```

El `Dockerfile` sirve las fotos desde `static/img/creadoras` mediante un enlace al
directorio persistente.

## Variables privadas

Define en Easypanel:

| Variable | Valor |
| --- | --- |
| `TALENTOFUTPAY_SECRET_KEY` | Secreto aleatorio largo y privado |
| `TALENTOFUTPAY_DATABASE_PATH` | `/data/talentofutpay.db` |
| `PORT` | `5000` |

Las credenciales iniciales `TALENTOFUTPAY_USER` y `TALENTOFUTPAY_PASSWORD` solo se
usan al crear el usuario admin por primera vez. La base existente conserva las
credenciales almacenadas; cámbialas desde la aplicación, no desde estas variables.

No guardes valores secretos en GitHub, en archivos `.env` versionados ni en capturas
de pantalla.

## Operación

- Haz un respaldo externo recuperable de `/data/talentofutpay.db` y de
  `/data/creadoras` antes de cambios de versión.
- Despliega manualmente después de confirmar que `master` pasó las pruebas.
- Revisa registros en Easypanel y valida `GET /health` (HTTP 200).
- Conserva el volumen `/data` durante rollback o reconstrucciones.

Para los pasos de despliegue y verificación, consulta
[DEPLOY_QUICKSTART.md](./DEPLOY_QUICKSTART.md).

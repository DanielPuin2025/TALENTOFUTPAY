# Despliegue en producción

La producción se ejecuta en Easypanel desde la rama `master` de GitHub usando el
`Dockerfile` del repositorio.

Antes de desplegar, confirma un respaldo externo recuperable de la base de datos y
las imágenes subidas. Conserva el volumen existente `talentofutpay-data` montado en
`/data`; ahí viven `/data/talentofutpay.db` y las fotos subidas en
`/data/creadoras`. Antes del primer despliegue de esta versión, copia las fotos del
contenedor actual al volumen siguiendo [DEPLOY_QUICKSTART.md](./DEPLOY_QUICKSTART.md).

El `Dockerfile` configura `TALENTOFUTPAY_DATABASE_PATH=/data/talentofutpay.db` y
`PORT=5000`. Si no defines `TALENTOFUTPAY_SECRET_KEY` como secreto en Easypanel, el
entrypoint genera una clave persistente en `/data/talentofutpay.secret_key`. No
publiques secretos ni bases SQLite en GitHub.

Consulta la guía operativa:

- [Despliegue rápido](./DEPLOY_QUICKSTART.md)
- [Configuración de Easypanel](./ASYPANEL_CONFIG.md)

# Despliegue en producción

La producción se ejecuta en Easypanel desde la rama `master` de GitHub usando el
`Dockerfile` del repositorio.

Antes de desplegar, confirma un respaldo externo recuperable de la base de datos y
las imágenes subidas. Conserva el volumen existente `talentofutpay-data` montado en
`/data`; ahí viven `/data/talentofutpay.db` y las fotos subidas en
`/data/creadoras`. Antes del primer despliegue de esta versión, copia las fotos del
contenedor actual al volumen siguiendo [DEPLOY_QUICKSTART.md](./DEPLOY_QUICKSTART.md).

Las variables privadas requeridas son `TALENTOFUTPAY_SECRET_KEY`,
`TALENTOFUTPAY_DATABASE_PATH=/data/talentofutpay.db` y `PORT=5000`. No publiques
secretos ni bases SQLite en GitHub.

Consulta la guía operativa:

- [Despliegue rápido](./DEPLOY_QUICKSTART.md)
- [Configuración de Easypanel](./ASYPANEL_CONFIG.md)

# TalentoFutPay

Aplicacion web Flask para gestionar jugadoras, pagos y recordatorios. Usa SQLite.

## Publicar el codigo en GitHub

1. Crea un repositorio vacio en GitHub (sin README, licencia ni `.gitignore`).
2. Desde la carpeta del proyecto, inicializa Git y crea el primer commit:

   ```powershell
   git init
   git add .
   git commit -m "Publicar TalentoFutPay"
   git branch -M main
   git remote add origin https://github.com/USUARIO/REPOSITORIO.git
   git push -u origin main
   ```

   Sustituye `USUARIO/REPOSITORIO` por la direccion de tu repositorio. GitHub puede
   pedir iniciar sesion o usar un token mediante Git Credential Manager.

3. `talentofutpay.db`, archivos `.env`, entornos virtuales y caches estan excluidos
   del commit. No subas la base de datos ni credenciales al repositorio.

## Desplegar en Easypanel

1. En Easypanel, crea un proyecto y agrega un servicio conectado al repositorio de
   GitHub.
2. Selecciona la rama `main`, el constructor Dockerfile y el archivo `Dockerfile`
   de la raiz del repositorio. Inicia el despliegue.
3. En el servicio, agrega un almacenamiento persistente montado en `/data`.
   La aplicacion guarda la base en `/data/talentofutpay.db`; sin ese volumen, los
   datos se perderan al recrear el contenedor.
4. En las variables de entorno del servicio define:

   - `TALENTOFUTPAY_SECRET_KEY`: una clave aleatoria larga y privada.
   - `TALENTOFUTPAY_USER`: usuario administrador inicial.
   - `TALENTOFUTPAY_PASSWORD`: contrasena inicial fuerte.
   - `TALENTOFUTPAY_TREASURER_USER` y `TALENTOFUTPAY_TREASURER_PASSWORD`:
     usuario y contrasena iniciales del tesorero.
   - `TALENTOFUTPAY_COACH_USER` y `TALENTOFUTPAY_COACH_PASSWORD`: usuario y
     contrasena iniciales del entrenador.
   - `PORT`: `5000`, salvo que Easypanel ya lo configure automaticamente.

   Configura estas variables como secretos en Easypanel; no las escribas en el
   repositorio. La base se inicializa al arrancar. Las credenciales iniciales
   se usan para crear las cuentas cuando la base esta vacia; si la base ya existe,
   cambiar estas variables no modifica las cuentas guardadas. En ese caso, inicia
   sesion y cambia las claves desde la opcion **Cambiar clave**.
5. Configura el puerto interno `5000` y el dominio del servicio. Activa HTTPS en
   Easypanel y usa `/health` como ruta de comprobacion si el panel permite
   configurar una.
6. Comprueba que el servicio este saludable y que el dominio cargue la pantalla
   de inicio de sesion.

## Conservar datos existentes

El archivo local `talentofutpay.db` no se publica en GitHub ni se copia a la imagen.
Si necesitas conservar sus registros, haz primero una copia de seguridad y transfiere
el archivo de forma privada al volumen de Easypanel en `/data/talentofutpay.db`
antes de iniciar la aplicacion. No lo adjuntes a un issue ni lo guardes en un
repositorio publico.

## Desarrollo local

Instala las dependencias con `pip install -r requirements.txt` y ejecuta
`python app.py`. Localmente, la base se crea junto a `app.py`. Para usar otra
ubicacion define `TALENTOFUTPAY_DATABASE_PATH`.

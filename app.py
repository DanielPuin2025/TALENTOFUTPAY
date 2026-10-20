import os
import re
import sqlite3
import csv
import io
from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from flask import Flask, Response, flash, redirect, render_template, request, send_file, session


app = Flask(__name__)
app.secret_key = os.environ.get("TALENTOFUTPAY_SECRET_KEY", "talentofutpay-clave-local")
USUARIO_ADMIN = os.environ.get("TALENTOFUTPAY_USER", "admin")
CLAVE_ADMIN = os.environ.get("TALENTOFUTPAY_PASSWORD", "admin123")
DATABASE = Path(
    os.environ.get(
        "TALENTOFUTPAY_DATABASE_PATH",
        str(Path(__file__).with_name("talentofutpay.db")),
    )
)


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS jugadoras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                edad INTEGER NOT NULL,
                posicion TEXT NOT NULL,
                mensualidad REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS pagos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                mes TEXT NOT NULL,
                valor REAL NOT NULL,
                estado TEXT NOT NULL CHECK (estado IN ('Pagado', 'Pendiente')),
                metodo_pago TEXT NOT NULL DEFAULT 'Efectivo'
            );
            CREATE TABLE IF NOT EXISTS configuracion (
                clave TEXT PRIMARY KEY,
                valor TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                clave TEXT NOT NULL,
                rol TEXT NOT NULL CHECK (rol IN ('admin', 'tesorero', 'instructor'))
            );
            CREATE TABLE IF NOT EXISTS torneos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                fecha_inicio TEXT NOT NULL,
                fecha_fin TEXT NOT NULL,
                ubicacion TEXT,
                descripcion TEXT,
                creado_por INTEGER,
                FOREIGN KEY (creado_por) REFERENCES usuarios(id)
            );
            CREATE TABLE IF NOT EXISTS inscripciones_torneo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                torneo_id INTEGER NOT NULL,
                jugadora_id INTEGER NOT NULL,
                fecha_inscripcion TEXT NOT NULL,
                instructor_id INTEGER NOT NULL,
                FOREIGN KEY (torneo_id) REFERENCES torneos(id),
                FOREIGN KEY (jugadora_id) REFERENCES jugadoras(id),
                FOREIGN KEY (instructor_id) REFERENCES usuarios(id)
            );
            CREATE TABLE IF NOT EXISTS creadoras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                rol TEXT NOT NULL,
                descripcion TEXT,
                foto TEXT
            );
            """
        )
        connection.execute(
            "INSERT OR IGNORE INTO configuracion (clave, valor) VALUES ('clave_admin', ?)",
            (CLAVE_ADMIN,),
        )
        clave_admin = connection.execute(
            "SELECT valor FROM configuracion WHERE clave = 'clave_admin'"
        ).fetchone()["valor"]
        connection.execute(
            "INSERT OR IGNORE INTO usuarios (usuario, clave, rol) VALUES (?, ?, 'admin')",
            (USUARIO_ADMIN, clave_admin),
        )
        connection.execute(
            "INSERT OR IGNORE INTO usuarios (usuario, clave, rol) VALUES ('tesorero', 'tesorero123', 'tesorero')"
        )
        connection.execute(
            "INSERT OR IGNORE INTO usuarios (usuario, clave, rol) VALUES ('instructor', 'instructor123', 'instructor')"
        )

        # Insertar creadoras por defecto si no existen
        creadoras_existentes = connection.execute("SELECT COUNT(*) as count FROM creadoras").fetchone()
        if creadoras_existentes['count'] == 0:
            connection.execute(
                """
                INSERT INTO creadoras (nombre, rol, descripcion, foto)
                VALUES
                ('Creadora 1', 'Desarrolladora Full Stack', 'Especialista en desarrollo web y gestión de bases de datos.', NULL),
                ('Creadora 2', 'Diseñadora UX/UI', 'Experta en experiencia de usuario y diseño de interfaces.', NULL)
                """
            )

        columnas_jugadora = {
            fila["name"]
            for fila in connection.execute("PRAGMA table_info(jugadoras)").fetchall()
        }
        if "acudiente_nombre" not in columnas_jugadora:
            connection.execute("ALTER TABLE jugadoras ADD COLUMN acudiente_nombre TEXT")
        if "acudiente_telefono" not in columnas_jugadora:
            connection.execute("ALTER TABLE jugadoras ADD COLUMN acudiente_telefono TEXT")
        if "estado" not in columnas_jugadora:
            connection.execute("ALTER TABLE jugadoras ADD COLUMN estado TEXT DEFAULT 'Activa'")
        connection.execute("UPDATE jugadoras SET estado = 'Activa' WHERE estado IS NULL")
        columnas_pago = {
            fila["name"]
            for fila in connection.execute("PRAGMA table_info(pagos)").fetchall()
        }
        if "jugadora_id" not in columnas_pago:
            connection.execute(
                "ALTER TABLE pagos ADD COLUMN jugadora_id INTEGER REFERENCES jugadoras(id)"
            )
        columnas_pago = {
            fila["name"]
            for fila in connection.execute("PRAGMA table_info(pagos)").fetchall()
        }
        if "fecha" not in columnas_pago:
            connection.execute("ALTER TABLE pagos ADD COLUMN fecha TEXT")
        if "metodo_pago" not in columnas_pago:
            connection.execute("ALTER TABLE pagos ADD COLUMN metodo_pago TEXT DEFAULT 'Efectivo'")
        if "saldo_pendiente" not in columnas_pago:
            connection.execute("ALTER TABLE pagos ADD COLUMN saldo_pendiente REAL DEFAULT 0")
        connection.execute("UPDATE pagos SET fecha = date('now') WHERE fecha IS NULL")
        connection.execute("UPDATE pagos SET metodo_pago = 'Efectivo' WHERE metodo_pago IS NULL OR metodo_pago = ''")

        # Calcular saldo pendiente para pagos existentes
        connection.execute("""
            UPDATE pagos
            SET saldo_pendiente = CASE
                WHEN estado = 'Pendiente' THEN valor
                ELSE 0
            END
            WHERE saldo_pendiente IS NULL OR saldo_pendiente = 0
        """)

        connection.execute(
            """
            UPDATE pagos
            SET jugadora_id = (
                SELECT jugadoras.id
                FROM jugadoras
                WHERE jugadoras.nombre = pagos.nombre
                LIMIT 1
            )
            WHERE jugadora_id IS NULL
            """
        )


def cargar_jugadoras(busqueda=""):
    with get_connection() as connection:
        if busqueda:
            filas = connection.execute(
                "SELECT id, nombre, edad, posicion, mensualidad, acudiente_nombre, "
                "acudiente_telefono, estado FROM jugadoras "
                "WHERE nombre LIKE ? ORDER BY id",
                (f"%{busqueda}%",),
            ).fetchall()
        else:
            filas = connection.execute(
                "SELECT id, nombre, edad, posicion, mensualidad, acudiente_nombre, "
                "acudiente_telefono, estado FROM jugadoras ORDER BY id"
            ).fetchall()
    return [dict(fila) for fila in filas]


def cargar_pagos(busqueda="", mes="", estado=""):
    condiciones = []
    parametros = []
    if busqueda:
        condiciones.append("COALESCE(jugadoras.nombre, pagos.nombre) LIKE ?")
        parametros.append(f"%{busqueda}%")
    if mes:
        condiciones.append("pagos.mes = ?")
        parametros.append(mes)
    if estado:
        condiciones.append("pagos.estado = ?")
        parametros.append(estado)
    where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
    with get_connection() as connection:
        filas = connection.execute(
            f"""
            SELECT pagos.id, pagos.jugadora_id,
                   COALESCE(jugadoras.nombre, pagos.nombre) AS nombre,
                   pagos.mes, pagos.valor, pagos.estado, pagos.fecha, pagos.metodo_pago,
                   COALESCE(pagos.saldo_pendiente, 0) as saldo_pendiente
            FROM pagos
            LEFT JOIN jugadoras ON jugadoras.id = pagos.jugadora_id
            {where}
            ORDER BY pagos.id
            """, parametros
        ).fetchall()
    return [dict(fila) for fila in filas]


def numero_valido(valor, entero=False):
    try:
        numero = int(valor) if entero else float(valor)
        return numero if numero >= 0 else None
    except (TypeError, ValueError):
        return None


@app.template_filter("cop")
def formato_cop(valor):
    try:
        return f"${float(valor):,.0f}".replace(",", ".")
    except (TypeError, ValueError):
        return "$0"


def obtener_clave_admin():
    with get_connection() as connection:
        fila = connection.execute(
            "SELECT valor FROM configuracion WHERE clave = 'clave_admin'"
        ).fetchone()
    return fila["valor"] if fila else CLAVE_ADMIN


def obtener_usuario(usuario, clave):
    with get_connection() as connection:
        return connection.execute(
            "SELECT id, usuario, rol FROM usuarios WHERE usuario = ? AND clave = ?",
            (usuario, clave),
        ).fetchone()


def validar_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[^A-Za-z0-9]", password):
        return False
    return True


def enlace_whatsapp(jugadora):
    telefono = re.sub(r"\D", "", jugadora.get("acudiente_telefono") or "")
    if len(telefono) == 10 and telefono.startswith("3"):
        telefono = "57" + telefono
    if len(telefono) < 10:
        return None
    mensaje = (
        f"Hola, le recordamos que se acerca la mensualidad de {jugadora['nombre']}. "
        f"El valor registrado es {formato_cop(jugadora['mensualidad'])} COP. Gracias."
    )
    return f"https://wa.me/{telefono}?text={quote(mensaje)}"


def enlace_recordatorio_pago(jugadora, mes, valor):
    telefono = re.sub(r"\D", "", jugadora.get("acudiente_telefono") or "")
    if len(telefono) == 10 and telefono.startswith("3"):
        telefono = "57" + telefono
    if len(telefono) < 10:
        return None

    # Obtener deuda total de la jugadora
    deuda_info = obtener_deuda_jugadora(jugadora['id'])
    deuda_total = deuda_info['deuda_total']
    detalle_deudas = deuda_info['detalle']

    if deuda_total > 0:
        mensaje = (
            f"Hola {jugadora.get('acudiente_nombre') or 'acudiente'}, le recordamos que "
            f"la jugadora {jugadora['nombre']} tiene pagos pendientes.\n\n"
            f"📊 *Deuda total: ${deuda_total:,.0f}*\n\n"
            f"Detalle:\n{detalle_deudas}\n\n"
            f"💳 *Medios de pago:*\n"
            f"• Efectivo\n"
            f"• Transferencia bancaria\n"
            f"• Nequi\n\n"
            f"Por favor, comuníquese con nosotros para ponerse al día. Gracias."
        )
    else:
        mensaje = (
            f"Hola {jugadora.get('acudiente_nombre') or 'acudiente'}, le recordamos que "
            f"la jugadora {jugadora['nombre']} tiene un pago pendiente del mes de {mes}. "
            f"El valor es ${valor:,.0f}.\n\n"
            f"💳 *Medios de pago:*\n"
            f"• Efectivo\n"
            f"• Transferencia bancaria\n"
            f"• Nequi\n\n"
            f"Gracias por su atención."
        )
    return f"https://wa.me/{telefono}?text={quote(mensaje)}"


def resumen_pagos(pagos):
    recaudado = sum(pago["valor"] for pago in pagos if pago["estado"] == "Pagado")
    pendiente = sum(pago["valor"] for pago in pagos if pago["estado"] == "Pendiente")
    return recaudado, pendiente


def get_server_config():
    host = os.environ.get("TALENTOFUTPAY_HOST", "0.0.0.0")
    port = int(os.environ.get("TALENTOFUTPAY_PORT", "5000"))
    return host, port


def obtener_recordatorios_pendientes():
    pendientes = []
    for pago in cargar_pagos():
        if pago["estado"] != "Pendiente":
            continue
        jugadora = next(
            (item for item in cargar_jugadoras() if item["id"] == pago.get("jugadora_id")),
            None,
        )
        if not jugadora:
            continue
        enlace = enlace_recordatorio_pago(jugadora, pago["mes"], pago["valor"])
        pendientes.append({
            "id": pago["id"],
            "jugadora": jugadora["nombre"],
            "mes": pago["mes"],
            "valor": pago["valor"],
            "fecha": pago.get("fecha"),
            "acudiente": jugadora.get("acudiente_nombre") or "Sin nombre",
            "enlace": enlace,
        })
    return pendientes


def pago_duplicado(jugadora_id, mes, excluir_id=None):
    consulta = "SELECT 1 FROM pagos WHERE jugadora_id = ? AND mes = ?"
    parametros = [jugadora_id, mes]
    if excluir_id is not None:
        consulta += " AND id != ?"
        parametros.append(excluir_id)
    with get_connection() as connection:
        return connection.execute(consulta, parametros).fetchone() is not None


def obtener_deuda_jugadora(jugadora_id):
    """Obtiene el total de deuda pendiente de una jugadora"""
    with get_connection() as connection:
        resultado = connection.execute(
            """
            SELECT COALESCE(SUM(saldo_pendiente), 0) as deuda_total,
                   GROUP_CONCAT(mes || ': $' || CAST(CAST(saldo_pendiente AS INTEGER) AS TEXT), ', ') as detalle_deudas
            FROM pagos
            WHERE jugadora_id = ? AND saldo_pendiente > 0
            """,
            (jugadora_id,)
        ).fetchone()
    return {
        'deuda_total': resultado['deuda_total'] if resultado else 0,
        'detalle': resultado['detalle_deudas'] if resultado and resultado['detalle_deudas'] else ''
    }


def tiene_pagos_anteriores_pendientes(jugadora_id, mes_actual):
    """Verifica si la jugadora tiene pagos anteriores con saldo pendiente"""
    meses_orden = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                   'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

    if mes_actual not in meses_orden:
        return False

    indice_actual = meses_orden.index(mes_actual)
    meses_anteriores = meses_orden[:indice_actual]

    with get_connection() as connection:
        for mes in meses_anteriores:
            pago = connection.execute(
                "SELECT saldo_pendiente FROM pagos WHERE jugadora_id = ? AND mes = ? AND saldo_pendiente > 0",
                (jugadora_id, mes)
            ).fetchone()
            if pago:
                return True
    return False


def cargar_creadoras():
    """Carga las creadoras desde la base de datos"""
    with get_connection() as connection:
        filas = connection.execute("SELECT * FROM creadoras ORDER BY id").fetchall()
    return [dict(fila) for fila in filas]


init_database()


@app.before_request
def proteger_aplicacion():
    if request.endpoint not in {"index", "static", "health_check"} and not session.get("usuario"):
        return redirect("/")
    permisos = {
        "jugadoras": {"admin", "instructor"},
        "editar_jugadora": {"admin", "instructor"},
        "eliminar_jugadora": {"admin"},
        "pagos": {"admin", "tesorero", "instructor"},
        "editar_pago": {"admin", "tesorero", "instructor"},
        "eliminar_pago": {"admin"},
        "reportes": {"admin", "tesorero"},
        "exportar_pagos": {"admin", "tesorero"},
        "torneos": {"admin", "instructor"},
        "crear_torneo": {"admin", "instructor"},
        "editar_torneo": {"admin", "instructor"},
        "eliminar_torneo": {"admin"},
        "inscribir_jugadora_torneo": {"admin", "instructor"},
        "ver_inscripciones": {"admin", "instructor"},
        "eliminar_inscripcion": {"admin", "instructor"},
        "panel_admin": {"admin"},
        "admin_usuarios": {"admin"},
        "admin_crear_usuario": {"admin"},
        "admin_editar_usuario": {"admin"},
        "admin_eliminar_usuario": {"admin"},
    }
    permitidos = permisos.get(request.endpoint)
    if permitidos and session.get("rol") not in permitidos:
        flash("Tu rol no tiene permiso para acceder a esta sección.", "error")
        return redirect("/dashboard")


@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        clave = request.form.get("clave", "")
        cuenta = obtener_usuario(usuario, clave)
        if cuenta:
            session["usuario"] = cuenta["usuario"]
            session["usuario_id"] = cuenta["id"]
            session["rol"] = cuenta["rol"]
            return redirect("/dashboard")
        error = "Usuario o contraseña incorrectos."
    return render_template("index.html", error=error)


@app.route("/cerrar_sesion")
def cerrar_sesion():
    session.clear()
    return redirect("/")


@app.route("/cambiar_clave", methods=["GET", "POST"])
def cambiar_clave():
    if request.method == "POST":
        actual = request.form.get("clave_actual", "")
        nueva = request.form.get("clave_nueva", "")
        confirmacion = request.form.get("confirmacion", "")
        with get_connection() as connection:
            cuenta = connection.execute(
                "SELECT clave FROM usuarios WHERE id = ?", (session["usuario_id"],)
            ).fetchone()
        if not cuenta or actual != cuenta["clave"]:
            flash("La contraseña actual no es correcta.", "error")
        elif not validar_password(nueva):
            flash("La nueva contraseña debe tener mínimo 8 caracteres, mayúscula, minúscula, número y símbolo.", "error")
        elif nueva != confirmacion:
            flash("Las contraseñas nuevas no coinciden.", "error")
        else:
            with get_connection() as connection:
                connection.execute(
                    "UPDATE usuarios SET clave = ? WHERE id = ?",
                    (nueva, session["usuario_id"]),
                )
            flash("Contraseña actualizada correctamente.", "success")
            return redirect("/dashboard")
    return render_template("cambiar_clave.html")


@app.route("/recomendacion_seguridad")
def recomendacion_seguridad():
    flash("Cambia la contraseña predeterminada por una más segura y usa mínimo 8 caracteres, con mayúscula, minúscula, número y símbolo.", "warning")
    return redirect("/dashboard")


@app.route("/descargar_respaldo")
def descargar_respaldo():
    return send_file(
        DATABASE,
        as_attachment=True,
        download_name="talentofutpay_respaldo.db",
        mimetype="application/x-sqlite3",
    )


@app.route("/dashboard")
def dashboard():
    jugadoras = cargar_jugadoras()
    pagos = cargar_pagos()
    recaudado, pendiente = resumen_pagos(pagos)
    cantidad_pagados = sum(pago["estado"] == "Pagado" for pago in pagos)
    cantidad_pendientes = sum(pago["estado"] == "Pendiente" for pago in pagos)
    return render_template("dashboard.html", cantidad_jugadoras=len(jugadoras),
                           total_recaudado=recaudado, total_pendiente=pendiente,
                           pagos=pagos, cantidad_pagados=cantidad_pagados,
                           cantidad_pendientes=cantidad_pendientes)


@app.route("/jugadoras", methods=["GET", "POST"])
def jugadoras():
    busqueda = request.args.get("busqueda", "").strip()
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        edad = numero_valido(request.form.get("edad"), entero=True)
        posicion = request.form.get("posicion", "").strip()
        mensualidad = numero_valido(request.form.get("mensualidad"))
        acudiente_nombre = request.form.get("acudiente_nombre", "").strip()
        acudiente_telefono = request.form.get("acudiente_telefono", "").strip()
        estado = request.form.get("estado", "Activa").strip()
        if nombre and edad is not None and posicion and mensualidad is not None:
            with get_connection() as connection:
                connection.execute(
                    """
                    INSERT INTO jugadoras
                    (nombre, edad, posicion, mensualidad, acudiente_nombre,
                     acudiente_telefono, estado)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (nombre, edad, posicion, mensualidad, acudiente_nombre,
                     acudiente_telefono, estado),
                )
            flash("Jugadora registrada correctamente.", "success")
            return redirect("/jugadoras")
        flash("Completa todos los campos con valores válidos.", "error")
    lista_jugadoras = cargar_jugadoras(busqueda)
    for jugadora in lista_jugadoras:
        jugadora["whatsapp_url"] = enlace_whatsapp(jugadora)
    return render_template("jugadoras.html", jugadoras=lista_jugadoras, busqueda=busqueda)


@app.route("/eliminar_jugadora/<int:indice>")
def eliminar_jugadora(indice):
    jugadoras = cargar_jugadoras()
    if 0 <= indice < len(jugadoras):
        with get_connection() as connection:
            connection.execute(
                "UPDATE pagos SET jugadora_id = NULL WHERE jugadora_id = ?",
                (jugadoras[indice]["id"],),
            )
            connection.execute("DELETE FROM jugadoras WHERE id = ?", (jugadoras[indice]["id"],))
        flash("Jugadora eliminada correctamente.", "success")
    return redirect("/jugadoras")


@app.route("/editar_jugadora/<int:indice>", methods=["GET", "POST"])
def editar_jugadora(indice):
    jugadoras = cargar_jugadoras()
    if indice < 0 or indice >= len(jugadoras):
        return redirect("/jugadoras")
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        edad = numero_valido(request.form.get("edad"), entero=True)
        posicion = request.form.get("posicion", "").strip()
        mensualidad = numero_valido(request.form.get("mensualidad"))
        acudiente_nombre = request.form.get("acudiente_nombre", "").strip()
        acudiente_telefono = request.form.get("acudiente_telefono", "").strip()
        estado = request.form.get("estado", "Activa").strip()
        if nombre and edad is not None and posicion and mensualidad is not None:
            with get_connection() as connection:
                connection.execute(
                    """
                    UPDATE jugadoras
                    SET nombre = ?, edad = ?, posicion = ?, mensualidad = ?,
                        acudiente_nombre = ?, acudiente_telefono = ?, estado = ?
                    WHERE id = ?
                    """,
                    (nombre, edad, posicion, mensualidad, acudiente_nombre,
                     acudiente_telefono, estado, jugadoras[indice]["id"]),
                )
            flash("Información de la jugadora actualizada.", "success")
            return redirect("/jugadoras")
        flash("No se pudo actualizar la jugadora. Revisa los datos.", "error")
    return render_template("editar_jugadora.html", jugadora=jugadoras[indice], indice=indice)


@app.route("/pagos", methods=["GET", "POST"])
def pagos():
    busqueda = request.args.get("busqueda", "").strip()
    filtro_mes = request.args.get("filtro_mes", "").strip()
    filtro_estado = request.args.get("filtro_estado", "").strip()
    if request.method == "POST":
        jugadora_id = numero_valido(request.form.get("jugadora_id"), entero=True)
        mes = request.form.get("mes", "").strip()
        valor = numero_valido(request.form.get("valor"))
        estado = request.form.get("estado", "").strip()
        fecha = request.form.get("fecha", "").strip()
        metodo_pago = request.form.get("metodo_pago", "").strip()
        jugadoras = cargar_jugadoras()
        jugadora = next((item for item in jugadoras if item["id"] == jugadora_id), None)

        if jugadora and mes and valor is not None and fecha and estado in {"Pagado", "Pendiente"} and metodo_pago in {"Efectivo", "Transferencia", "Nequi"}:
            # Verificar si hay pagos anteriores pendientes
            if tiene_pagos_anteriores_pendientes(jugadora_id, mes):
                flash("No se puede registrar este pago. La jugadora tiene meses anteriores con saldo pendiente. Por favor, complete los pagos anteriores primero.", "error")
                return redirect("/pagos")

            if pago_duplicado(jugadora_id, mes):
                flash("Ya existe un pago para esta jugadora y este mes.", "error")
                return redirect("/pagos")

            # Calcular saldo pendiente
            mensualidad = 80000  # Mensualidad fija
            saldo_pendiente = 0
            if estado == "Pendiente":
                saldo_pendiente = mensualidad - valor
            elif estado == "Pagado" and valor < mensualidad:
                saldo_pendiente = mensualidad - valor
                estado = "Pendiente"  # Si no pagó completo, queda pendiente

            with get_connection() as connection:
                connection.execute(
                    """
                    INSERT INTO pagos (nombre, jugadora_id, mes, valor, estado, fecha, metodo_pago, saldo_pendiente)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (jugadora["nombre"], jugadora_id, mes, valor, estado, fecha, metodo_pago, saldo_pendiente),
                )
            flash("Pago registrado correctamente.", "success")
            return redirect("/pagos")
        flash("Completa todos los campos del pago correctamente.", "error")
    return render_template(
        "pagos.html",
        pagos=cargar_pagos(busqueda, filtro_mes, filtro_estado),
        jugadoras=cargar_jugadoras(),
        busqueda=busqueda,
        filtro_mes=filtro_mes,
        filtro_estado=filtro_estado,
    )



@app.route("/eliminar_pago/<int:indice>")
def eliminar_pago(indice):
    pagos = cargar_pagos()
    if 0 <= indice < len(pagos):
        with get_connection() as connection:
            connection.execute("DELETE FROM pagos WHERE id = ?", (pagos[indice]["id"],))
        flash("Pago eliminado correctamente.", "success")
    return redirect("/pagos")


@app.route("/editar_pago/<int:indice>", methods=["GET", "POST"])
def editar_pago(indice):
    pagos = cargar_pagos()
    if indice < 0 or indice >= len(pagos):
        return redirect("/pagos")
    if request.method == "POST":
        jugadora_id = numero_valido(request.form.get("jugadora_id"), entero=True)
        mes = request.form.get("mes", "").strip()
        valor = numero_valido(request.form.get("valor"))
        estado = request.form.get("estado", "").strip()
        fecha = request.form.get("fecha", "").strip()
        metodo_pago = request.form.get("metodo_pago", "").strip()
        jugadoras = cargar_jugadoras()
        jugadora = next((item for item in jugadoras if item["id"] == jugadora_id), None)
        if jugadora and mes and valor is not None and fecha and estado in {"Pagado", "Pendiente"} and metodo_pago in {"Efectivo", "Transferencia", "Nequi"}:
            if pago_duplicado(jugadora_id, mes, pagos[indice]["id"]):
                flash("Ya existe otro pago para esta jugadora y este mes.", "error")
                return redirect(f"/editar_pago/{indice}")

            # Calcular saldo pendiente
            mensualidad = 80000
            saldo_pendiente = 0
            if estado == "Pendiente":
                saldo_pendiente = mensualidad - valor
            elif estado == "Pagado" and valor < mensualidad:
                saldo_pendiente = mensualidad - valor
                estado = "Pendiente"

            with get_connection() as connection:
                connection.execute(
                    """
                    UPDATE pagos
                    SET nombre = ?, jugadora_id = ?, mes = ?, valor = ?, estado = ?, fecha = ?, metodo_pago = ?, saldo_pendiente = ?
                    WHERE id = ?
                    """,
                    (jugadora["nombre"], jugadora_id, mes, valor, estado, fecha, metodo_pago, saldo_pendiente, pagos[indice]["id"]),
                )
            flash("Pago actualizado correctamente.", "success")
            return redirect("/pagos")
        flash("No se pudo actualizar el pago. Revisa los datos.", "error")
    return render_template("editar_pago.html", pago=pagos[indice], indice=indice,
                           jugadoras=cargar_jugadoras())


@app.route("/reportes")
def reportes():
    jugadoras = cargar_jugadoras()
    pagos = cargar_pagos()
    recaudado, pendiente = resumen_pagos(pagos)
    return render_template("reportes.html", cantidad_jugadoras=len(jugadoras),
                           total_recaudado=recaudado, total_pendiente=pendiente,
                           pagos=pagos)


@app.route("/health")
def health_check():
    return {"status": "ok", "app": "talentofutpay"}, 200


@app.route("/recordatorios_pendientes")
def recordatorios_pendientes():
    return render_template("recordatorios.html", recordatorios=obtener_recordatorios_pendientes())


@app.route("/recordatorio_whatsapp/<int:pagos_id>")
def recordatorio_whatsapp(pagos_id):
    pagos = cargar_pagos()
    pago = next((item for item in pagos if item["id"] == pagos_id), None)
    if not pago:
        flash("No se encontró el pago para enviar el recordatorio.", "error")
        return redirect("/pagos")

    jugadora = next((item for item in cargar_jugadoras() if item["id"] == pago.get("jugadora_id")), None)
    if not jugadora:
        flash("No se pudo encontrar la jugadora asociada al pago.", "error")
        return redirect("/pagos")

    enlace = enlace_recordatorio_pago(jugadora, pago["mes"], pago["valor"])
    if not enlace:
        flash("Esta jugadora no tiene un teléfono del acudiente registrado para enviar WhatsApp.", "error")
        return redirect("/pagos")

    return redirect(enlace)


@app.route("/exportar_pagos")
def exportar_pagos():
    pagos = cargar_pagos(
        request.args.get("busqueda", "").strip(),
        request.args.get("mes", "").strip(),
        request.args.get("estado", "").strip(),
    )
    archivo = io.StringIO()
    escritor = csv.writer(archivo)
    escritor.writerow(["Jugadora", "Mes", "Valor", "Estado", "Fecha", "Método de pago"])
    for pago in pagos:
        escritor.writerow([pago["nombre"], pago["mes"], pago["valor"], pago["estado"], pago["fecha"], pago["metodo_pago"]])
    return Response(
        "\ufeff" + archivo.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=reporte_pagos.csv"},
    )


@app.route("/exportar_reporte_pdf")
def exportar_reporte_pdf():
    pagos = cargar_pagos()
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    pdf.setTitle("TalentoFutPay - Reporte de pagos")
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, height - 50, "TalentoFutPay - Reporte de pagos")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, height - 70, f"Fecha de generación: {date.today().strftime('%d/%m/%Y')}")

    y = height - 110
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(50, y, "Jugadora")
    pdf.drawString(200, y, "Mes")
    pdf.drawString(275, y, "Fecha")
    pdf.drawString(360, y, "Valor")
    pdf.drawString(460, y, "Método")
    pdf.drawString(510, y, "Estado")
    pdf.line(45, y - 5, 560, y - 5)

    pdf.setFont("Helvetica", 9)
    y -= 18
    for pago in pagos:
        if y < 60:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica-Bold", 9)
            pdf.drawString(50, y, "Jugadora")
            pdf.drawString(200, y, "Mes")
            pdf.drawString(275, y, "Fecha")
            pdf.drawString(360, y, "Valor")
            pdf.drawString(460, y, "Método")
            pdf.drawString(510, y, "Estado")
            pdf.line(45, y - 5, 560, y - 5)
            pdf.setFont("Helvetica", 9)
            y -= 18
        pdf.drawString(50, y, (pago["nombre"] or "")[:25])
        pdf.drawString(200, y, (pago["mes"] or "")[:12])
        pdf.drawString(275, y, (pago["fecha"] or "")[:10])
        pdf.drawRightString(440, y, f"{float(pago['valor']):,.0f}".replace(",", "."))
        pdf.drawString(460, y, (pago["metodo_pago"] or "")[:8])
        pdf.drawString(510, y, pago["estado"])
        y -= 18

    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="reporte_pagos.pdf", mimetype="application/pdf")


@app.route("/torneos")
def torneos():
    with get_connection() as connection:
        torneos = connection.execute(
            """
            SELECT t.*, u.usuario as creador
            FROM torneos t
            LEFT JOIN usuarios u ON t.creado_por = u.id
            ORDER BY t.fecha_inicio DESC
            """
        ).fetchall()
    return render_template("torneos.html", torneos=[dict(t) for t in torneos])


@app.route("/crear_torneo", methods=["GET", "POST"])
def crear_torneo():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        fecha_inicio = request.form.get("fecha_inicio", "").strip()
        fecha_fin = request.form.get("fecha_fin", "").strip()
        ubicacion = request.form.get("ubicacion", "").strip()
        descripcion = request.form.get("descripcion", "").strip()

        if nombre and fecha_inicio and fecha_fin:
            with get_connection() as connection:
                connection.execute(
                    """
                    INSERT INTO torneos (nombre, fecha_inicio, fecha_fin, ubicacion, descripcion, creado_por)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (nombre, fecha_inicio, fecha_fin, ubicacion, descripcion, session["usuario_id"]),
                )
            flash("Torneo creado correctamente.", "success")
            return redirect("/torneos")
        flash("Completa todos los campos requeridos.", "error")
    return render_template("crear_torneo.html")


@app.route("/editar_torneo/<int:torneo_id>", methods=["GET", "POST"])
def editar_torneo(torneo_id):
    with get_connection() as connection:
        torneo = connection.execute("SELECT * FROM torneos WHERE id = ?", (torneo_id,)).fetchone()

    if not torneo:
        flash("Torneo no encontrado.", "error")
        return redirect("/torneos")

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        fecha_inicio = request.form.get("fecha_inicio", "").strip()
        fecha_fin = request.form.get("fecha_fin", "").strip()
        ubicacion = request.form.get("ubicacion", "").strip()
        descripcion = request.form.get("descripcion", "").strip()

        if nombre and fecha_inicio and fecha_fin:
            with get_connection() as connection:
                connection.execute(
                    """
                    UPDATE torneos
                    SET nombre = ?, fecha_inicio = ?, fecha_fin = ?, ubicacion = ?, descripcion = ?
                    WHERE id = ?
                    """,
                    (nombre, fecha_inicio, fecha_fin, ubicacion, descripcion, torneo_id),
                )
            flash("Torneo actualizado correctamente.", "success")
            return redirect("/torneos")
        flash("Completa todos los campos requeridos.", "error")

    return render_template("editar_torneo.html", torneo=dict(torneo))


@app.route("/eliminar_torneo/<int:torneo_id>")
def eliminar_torneo(torneo_id):
    with get_connection() as connection:
        connection.execute("DELETE FROM inscripciones_torneo WHERE torneo_id = ?", (torneo_id,))
        connection.execute("DELETE FROM torneos WHERE id = ?", (torneo_id,))
    flash("Torneo eliminado correctamente.", "success")
    return redirect("/torneos")


@app.route("/inscribir_jugadora_torneo/<int:torneo_id>", methods=["GET", "POST"])
def inscribir_jugadora_torneo(torneo_id):
    with get_connection() as connection:
        torneo = connection.execute("SELECT * FROM torneos WHERE id = ?", (torneo_id,)).fetchone()

    if not torneo:
        flash("Torneo no encontrado.", "error")
        return redirect("/torneos")

    if request.method == "POST":
        jugadora_id = numero_valido(request.form.get("jugadora_id"), entero=True)

        if jugadora_id:
            with get_connection() as connection:
                ya_inscrita = connection.execute(
                    "SELECT 1 FROM inscripciones_torneo WHERE torneo_id = ? AND jugadora_id = ?",
                    (torneo_id, jugadora_id)
                ).fetchone()

                if ya_inscrita:
                    flash("Esta jugadora ya está inscrita en este torneo.", "error")
                else:
                    connection.execute(
                        """
                        INSERT INTO inscripciones_torneo (torneo_id, jugadora_id, fecha_inscripcion, instructor_id)
                        VALUES (?, ?, date('now'), ?)
                        """,
                        (torneo_id, jugadora_id, session["usuario_id"]),
                    )
                    flash("Jugadora inscrita correctamente.", "success")
                    return redirect(f"/ver_inscripciones/{torneo_id}")
        else:
            flash("Selecciona una jugadora válida.", "error")

    jugadoras = cargar_jugadoras()
    return render_template("inscribir_jugadora.html", torneo=dict(torneo), jugadoras=jugadoras)


@app.route("/ver_inscripciones/<int:torneo_id>")
def ver_inscripciones(torneo_id):
    with get_connection() as connection:
        torneo = connection.execute("SELECT * FROM torneos WHERE id = ?", (torneo_id,)).fetchone()
        inscripciones = connection.execute(
            """
            SELECT i.id, j.nombre as jugadora, u.usuario as instructor, i.fecha_inscripcion
            FROM inscripciones_torneo i
            JOIN jugadoras j ON i.jugadora_id = j.id
            JOIN usuarios u ON i.instructor_id = u.id
            WHERE i.torneo_id = ?
            ORDER BY i.fecha_inscripcion DESC
            """,
            (torneo_id,)
        ).fetchall()

    if not torneo:
        flash("Torneo no encontrado.", "error")
        return redirect("/torneos")

    return render_template("ver_inscripciones.html", torneo=dict(torneo), inscripciones=[dict(i) for i in inscripciones])


@app.route("/eliminar_inscripcion/<int:inscripcion_id>")
def eliminar_inscripcion(inscripcion_id):
    with get_connection() as connection:
        inscripcion = connection.execute(
            "SELECT torneo_id FROM inscripciones_torneo WHERE id = ?", (inscripcion_id,)
        ).fetchone()

        if inscripcion:
            torneo_id = inscripcion["torneo_id"]
            connection.execute("DELETE FROM inscripciones_torneo WHERE id = ?", (inscripcion_id,))
            flash("Inscripción eliminada correctamente.", "success")
            return redirect(f"/ver_inscripciones/{torneo_id}")

    flash("Inscripción no encontrada.", "error")
    return redirect("/torneos")


@app.route("/panel_admin")
def panel_admin():
    with get_connection() as connection:
        usuarios = connection.execute("SELECT id, usuario, rol FROM usuarios ORDER BY id").fetchall()
        total_jugadoras = connection.execute("SELECT COUNT(*) as total FROM jugadoras").fetchone()["total"]
        total_pagos = connection.execute("SELECT COUNT(*) as total FROM pagos").fetchone()["total"]
        total_torneos = connection.execute("SELECT COUNT(*) as total FROM torneos").fetchone()["total"]

    return render_template("panel_admin.html",
                         usuarios=[dict(u) for u in usuarios],
                         total_jugadoras=total_jugadoras,
                         total_pagos=total_pagos,
                         total_torneos=total_torneos)


@app.route("/admin_usuarios")
def admin_usuarios():
    with get_connection() as connection:
        usuarios = connection.execute("SELECT id, usuario, rol FROM usuarios ORDER BY id").fetchall()
    return render_template("admin_usuarios.html", usuarios=[dict(u) for u in usuarios])


@app.route("/admin_crear_usuario", methods=["GET", "POST"])
def admin_crear_usuario():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        clave = request.form.get("clave", "").strip()
        rol = request.form.get("rol", "").strip()

        if usuario and clave and rol in {"admin", "tesorero", "instructor"}:
            with get_connection() as connection:
                existe = connection.execute("SELECT 1 FROM usuarios WHERE usuario = ?", (usuario,)).fetchone()
                if existe:
                    flash("Este nombre de usuario ya existe.", "error")
                else:
                    connection.execute(
                        "INSERT INTO usuarios (usuario, clave, rol) VALUES (?, ?, ?)",
                        (usuario, clave, rol)
                    )
                    flash("Usuario creado correctamente.", "success")
                    return redirect("/admin_usuarios")
        else:
            flash("Completa todos los campos correctamente.", "error")

    return render_template("admin_crear_usuario.html")


@app.route("/admin_editar_usuario/<int:usuario_id>", methods=["GET", "POST"])
def admin_editar_usuario(usuario_id):
    with get_connection() as connection:
        usuario = connection.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()

    if not usuario:
        flash("Usuario no encontrado.", "error")
        return redirect("/admin_usuarios")

    if request.method == "POST":
        nuevo_usuario = request.form.get("usuario", "").strip()
        nueva_clave = request.form.get("clave", "").strip()
        nuevo_rol = request.form.get("rol", "").strip()

        if nuevo_usuario and nuevo_rol in {"admin", "tesorero", "instructor"}:
            with get_connection() as connection:
                if nueva_clave:
                    connection.execute(
                        "UPDATE usuarios SET usuario = ?, clave = ?, rol = ? WHERE id = ?",
                        (nuevo_usuario, nueva_clave, nuevo_rol, usuario_id)
                    )
                else:
                    connection.execute(
                        "UPDATE usuarios SET usuario = ?, rol = ? WHERE id = ?",
                        (nuevo_usuario, nuevo_rol, usuario_id)
                    )
            flash("Usuario actualizado correctamente.", "success")
            return redirect("/admin_usuarios")
        flash("Completa todos los campos correctamente.", "error")

    return render_template("admin_editar_usuario.html", usuario=dict(usuario))


@app.route("/admin_eliminar_usuario/<int:usuario_id>")
def admin_eliminar_usuario(usuario_id):
    if usuario_id == session.get("usuario_id"):
        flash("No puedes eliminar tu propio usuario.", "error")
        return redirect("/admin_usuarios")

    with get_connection() as connection:
        connection.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
    flash("Usuario eliminado correctamente.", "success")
    return redirect("/admin_usuarios")


@app.route("/acerca")
def acerca():
    creadoras = cargar_creadoras()
    return render_template("acerca.html", creadoras=creadoras)


@app.route("/admin_creadoras")
def admin_creadoras():
    if session.get("rol") != "admin":
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect("/dashboard")
    creadoras = cargar_creadoras()
    return render_template("admin_creadoras.html", creadoras=creadoras)


@app.route("/admin_editar_creadora/<int:creadora_id>", methods=["GET", "POST"])
def admin_editar_creadora(creadora_id):
    if session.get("rol") != "admin":
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect("/dashboard")

    creadoras = cargar_creadoras()
    creadora = next((c for c in creadoras if c["id"] == creadora_id), None)

    if not creadora:
        flash("Creadora no encontrada.", "error")
        return redirect("/admin_creadoras")

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        rol = request.form.get("rol", "").strip()
        descripcion = request.form.get("descripcion", "").strip()

        # Manejo de la foto
        foto_actual = creadora["foto"]
        if "foto" in request.files:
            archivo = request.files["foto"]
            if archivo and archivo.filename:
                # Validar extensión
                extension = archivo.filename.rsplit(".", 1)[1].lower() if "." in archivo.filename else ""
                if extension in ["jpg", "jpeg", "png", "gif"]:
                    # Generar nombre único
                    nombre_archivo = f"creadora_{creadora_id}_{int(datetime.now().timestamp())}.{extension}"
                    ruta_archivo = os.path.join("static", "img", nombre_archivo)

                    # Guardar archivo directamente en static/img/
                    archivo.save(ruta_archivo)
                    foto_actual = nombre_archivo
                else:
                    flash("Formato de imagen no válido. Use JPG, PNG o GIF.", "error")
                    return redirect(f"/admin_editar_creadora/{creadora_id}")

        if nombre and rol:
            with get_connection() as connection:
                connection.execute(
                    "UPDATE creadoras SET nombre = ?, rol = ?, descripcion = ?, foto = ? WHERE id = ?",
                    (nombre, rol, descripcion, foto_actual, creadora_id)
                )
            flash("Creadora actualizada correctamente.", "success")
            return redirect("/admin_creadoras")

        flash("Por favor completa todos los campos obligatorios.", "error")

    return render_template("admin_editar_creadora.html", creadora=creadora)


if __name__ == "__main__":
    host, port = get_server_config()
    app.run(host=host, port=port, debug=True)
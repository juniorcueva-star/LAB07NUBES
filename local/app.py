import os
import socket
import sqlite3
from functools import wraps

from flask import (Flask, flash, g, jsonify, redirect, render_template_string,
                   request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

# ---------------- Configuracion ----------------
PORT = int(os.environ.get("PORT", 5000))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE_DIR, "datos.db"))
SERVER_ID = os.environ.get("SERVER_ID", f"{socket.gethostname()}:{PORT}")

app = Flask(__name__)
# Todas las copias deben usar la misma clave para compartir la sesión.
secret_key = os.environ.get("SECRET_KEY")
if not secret_key:
    raise RuntimeError("Defina SECRET_KEY antes de iniciar la aplicación")
app.secret_key = secret_key


# ---------------- Base de datos ----------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH, timeout=10)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH, timeout=10)
    db.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL)""")
    db.execute("""CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        precio REAL NOT NULL,
        stock INTEGER NOT NULL)""")
    admin_password = os.environ.get("ADMIN_PASSWORD")
    if admin_password:
        db.execute("INSERT OR IGNORE INTO usuarios (username, password) VALUES (?, ?)",
                   ("admin", generate_password_hash(admin_password)))
    db.commit()
    db.close()


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


# ---------------- Plantillas ----------------
HEAD = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lab Balanceo - CRUD</title>
<style>
 body{font-family:Arial,sans-serif;background:#f4f6f8;margin:0}
 .top{background:#1f3b57;color:#fff;padding:12px 24px;display:flex;justify-content:space-between;align-items:center}
 .top a{color:#fff}
 .box{max-width:820px;margin:24px auto;background:#fff;padding:24px;border-radius:8px;box-shadow:0 1px 4px #0002}
 table{width:100%;border-collapse:collapse}th,td{padding:8px;border-bottom:1px solid #ddd;text-align:left}
 input{padding:8px;margin:4px 0 12px;width:100%;box-sizing:border-box}
 .btn{background:#1f7a4d;color:#fff;border:0;padding:8px 14px;border-radius:4px;cursor:pointer;text-decoration:none;display:inline-block}
 .del{background:#b3261e}.edit{background:#1f5fa8}
 .msg{background:#fff3cd;padding:8px;border-radius:4px;margin-bottom:12px}
 .srv{text-align:center;margin:12px;padding:10px;background:#e8f0fe;border-radius:6px;font-weight:bold}
</style></head><body>
<div class="top"><b>Lab Balanceador de Carga</b>
{% if session.user %}<span>Usuario: {{ session.user }} | <a href="{{ url_for('logout') }}">Salir</a></span>{% endif %}
</div><div class="box">
{% with msgs = get_flashed_messages() %}{% for m in msgs %}<div class="msg">{{ m }}</div>{% endfor %}{% endwith %}
"""
FOOT = """</div><div class="srv">Atendido por el servidor: {{ server }}</div></body></html>"""


def page(body, **ctx):
    return render_template_string(HEAD + body + FOOT, server=SERVER_ID, **ctx)


# ---------------- Rutas: Login ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = get_db().execute("SELECT * FROM usuarios WHERE username = ?",
                                (request.form["username"],)).fetchone()
        if user and check_password_hash(user["password"], request.form["password"]):
            session["user"] = user["username"]
            return redirect(url_for("index"))
        flash("Usuario o contrasena incorrectos")
    return page("""<h2>Iniciar sesion</h2>
<form method="post">
 <label>Usuario</label><input name="username" required>
 <label>Contrasena</label><input name="password" type="password" required>
 <button class="btn">Ingresar</button>
</form>""")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------- Rutas: CRUD productos ----------------
@app.route("/")
@login_required
def index():
    productos = get_db().execute("SELECT * FROM productos ORDER BY id").fetchall()
    return page("""<h2>Productos</h2>
<a class="btn" href="{{ url_for('nuevo') }}">+ Nuevo producto</a><br><br>
<table><tr><th>ID</th><th>Nombre</th><th>Precio</th><th>Stock</th><th>Acciones</th></tr>
{% for p in productos %}
<tr><td>{{ p.id }}</td><td>{{ p.nombre }}</td><td>S/ {{ '%.2f' % p.precio }}</td><td>{{ p.stock }}</td>
<td><a class="btn edit" href="{{ url_for('editar', id=p.id) }}">Editar</a>
<form method="post" action="{{ url_for('eliminar', id=p.id) }}" style="display:inline">
<button class="btn del">Eliminar</button></form></td></tr>
{% else %}<tr><td colspan="5">No hay productos registrados</td></tr>{% endfor %}
</table>""", productos=productos)


FORM = """<h2>{{ titulo }}</h2>
<form method="post">
 <label>Nombre</label><input name="nombre" value="{{ p.nombre if p else '' }}" required>
 <label>Precio</label><input name="precio" type="number" step="0.01" min="0" value="{{ p.precio if p else '' }}" required>
 <label>Stock</label><input name="stock" type="number" min="0" value="{{ p.stock if p else '' }}" required>
 <button class="btn">Guardar</button> <a href="{{ url_for('index') }}">Cancelar</a>
</form>"""


@app.route("/productos/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    if request.method == "POST":
        db = get_db()
        db.execute("INSERT INTO productos (nombre, precio, stock) VALUES (?, ?, ?)",
                   (request.form["nombre"], float(request.form["precio"]), int(request.form["stock"])))
        db.commit()
        flash("Producto creado")
        return redirect(url_for("index"))
    return page(FORM, titulo="Nuevo producto", p=None)


@app.route("/productos/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar(id):
    db = get_db()
    p = db.execute("SELECT * FROM productos WHERE id = ?", (id,)).fetchone()
    if p is None:
        flash("Producto no encontrado")
        return redirect(url_for("index"))
    if request.method == "POST":
        db.execute("UPDATE productos SET nombre = ?, precio = ?, stock = ? WHERE id = ?",
                   (request.form["nombre"], float(request.form["precio"]), int(request.form["stock"]), id))
        db.commit()
        flash("Producto actualizado")
        return redirect(url_for("index"))
    return page(FORM, titulo="Editar producto", p=p)


@app.route("/productos/<int:id>/eliminar", methods=["POST"])
@login_required
def eliminar(id):
    db = get_db()
    db.execute("DELETE FROM productos WHERE id = ?", (id,))
    db.commit()
    flash("Producto eliminado")
    return redirect(url_for("index"))


# ---------------- Rutas de apoyo para el balanceo ----------------
@app.route("/health")
def health():
    return "OK", 200


@app.route("/whoami")
def whoami():
    return f"Servidor BACKEND {SERVER_ID}\n", 200, {"Content-Type": "text/plain"}


@app.route("/api/productos")
@login_required
def api_productos():
    filas = get_db().execute("SELECT * FROM productos ORDER BY id").fetchall()
    return jsonify(servidor=SERVER_ID, productos=[dict(f) for f in filas])


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=PORT, threaded=True)

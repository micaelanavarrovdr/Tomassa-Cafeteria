# import hashlib # se necesita para hashing de contraseñas
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import pyodbc
import hashlib
import base64
import pandas as pd
import matplotlib.pyplot as plt
import io

app = Flask(__name__)
app.secret_key = "clave_secreta_flask"

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=serverName;"
    "DATABASE=TomassaCafeteria;"
    "Trusted_Connection=yes;"
)

def get_connection():
    return pyodbc.connect(CONNECTION_STRING)

""" # insertar un usuario
username = "user"
password = "pass"
password_hash = hashlib.sha256(password.encode()).hexdigest().upper()

conn = get_connection()
cursor = conn.cursor()
cursor.execute("INSERT INTO Usuarios (username, passwordHash) VALUES (?, ?)", username, password_hash)
conn.commit()
conn.close()
print("Usuario admin insertado correctamente")
"""

@app.route("/")
def index():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Traer categorías desde la base de datos
    cursor.execute("SELECT idCategoria, nombre FROM Categorias")
    categorias = cursor.fetchall()
    
    conn.close()
    
    return render_template("index.html", categorias=categorias)


@app.route("/admin")
def admin():
    if "username" not in session:
        return redirect(url_for("index"))
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Obtener categorías
    cursor.execute("SELECT idCategoria, nombre FROM Categorias")
    categorias = cursor.fetchall()
    
    # Obtener productos existentes
    cursor.execute("""
        SELECT p.idProducto, p.nombre, p.descripcion, p.precio, 
               p.idCategoria, c.nombre as categoria, p.imagen
        FROM Productos p
        INNER JOIN Categorias c ON p.idCategoria = c.idCategoria
    """)
    productos = cursor.fetchall()
    
    conn.close()
    
    return render_template("adminPanel.html", categorias=categorias, productos=productos)

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT passwordHash FROM Usuarios WHERE username = ?", username)
    row = cursor.fetchone()
    conn.close()
    
    if row:
        password_hash = hashlib.sha256(password.encode()).hexdigest().upper()
        if password_hash == row[0]:
            session["username"] = username
            return redirect(url_for("admin"))
    
    flash("Usuario o contraseña incorrectos")
    return redirect(url_for("index"))

@app.route("/add_product", methods=["POST"])
def add_product():
    if "username" not in session:
        flash("Debes iniciar sesión")
        return redirect(url_for("index"))
    
    name = request.form.get("name")
    category = request.form.get("category")
    description = request.form.get("description")
    price = request.form.get("price")
    image_file = request.files.get("image")
    
    if not all([name, category, price, image_file]):
        flash("Faltan datos del producto")
        return redirect(url_for("admin"))
    
    # Convertir imagen a Base64
    image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Insertar en la base de datos
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Productos (nombre, descripcion, precio, idCategoria, imagen)
            VALUES (?, ?, ?, ?, ?)
        """, name, description, float(price), int(category), image_base64)
        conn.commit()
        flash("Producto agregado exitosamente")
    except Exception as e:
        flash(f"Error al agregar producto: {str(e)}")
    finally:
        conn.close()
    
    return redirect(url_for("admin"))

@app.route("/update_product/<int:product_id>", methods=["POST"])
def update_product(product_id):
    if "username" not in session:
        flash("Debes iniciar sesión")
        return redirect(url_for("index"))
    
    name = request.form.get("name")
    category = request.form.get("category")
    description = request.form.get("description")
    price = request.form.get("price")
    image_file = request.files.get("image")
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if image_file and image_file.filename != "":
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            cursor.execute("""
                UPDATE Productos
                SET nombre=?, descripcion=?, precio=?, idCategoria=?, imagen=?
                WHERE idProducto=?
            """, name, description, float(price), int(category), image_base64, product_id)
        else:
            cursor.execute("""
                UPDATE Productos
                SET nombre=?, descripcion=?, precio=?, idCategoria=?
                WHERE idProducto=?
            """, name, description, float(price), int(category), product_id)
        
        conn.commit()
        flash("Producto actualizado correctamente")
    except Exception as e:
        flash(f"Error al actualizar producto: {str(e)}")
    finally:
        conn.close()
    
    return redirect(url_for("admin"))

@app.route("/delete_product/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    if "username" not in session:
        return jsonify({"error": "No autorizado"}), 401
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Productos WHERE idProducto = ?", product_id)
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint para obtener productos en formato JSON
@app.route("/api/productos")
def get_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.idProducto, p.nombre, p.descripcion, p.precio, 
               c.nombre as categoria, p.imagen
        FROM Productos p
        INNER JOIN Categorias c ON p.idCategoria = c.idCategoria
    """)
    rows = cursor.fetchall()
    conn.close()

    # Convertir resultados a lista de dicts
    productos = []
    for r in rows:
        productos.append({
            "id": r.idProducto,
            "name": r.nombre,
            "description": r.descripcion,
            "price": float(r.precio),
            "category": r.categoria.lower(),  # ej: "cafe"
            # Si guardás imagen en base64:
            "image": f"data:image/png;base64,{r.imagen}" if r.imagen else "/static/img/default.png"
        })
    return jsonify(productos)

    
@app.route("/report")
def report():
    if "username" not in session:
        flash("Debes iniciar sesión")
        return redirect(url_for("index"))
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.nombre as categoria, COUNT(p.idProducto) as cantidad
        FROM Productos p
        INNER JOIN Categorias c ON p.idCategoria = c.idCategoria
        GROUP BY c.nombre
    """)
    
    rows = [(r[0], r[1]) for r in cursor.fetchall()]
    conn.close()
    
    df = pd.DataFrame(rows, columns=["Categoria", "Cantidad"])
    
    # Crear gráfico
    fig, ax = plt.subplots(figsize=(8,5))
    df.plot(kind='bar', x='Categoria', y='Cantidad', legend=False, ax=ax, color='skyblue')

    # Forzar eje Y a números enteros
    from matplotlib.ticker import MaxNLocator
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    ax.set_ylabel("Cantidad de productos")
    ax.set_title("Productos por categoría")
    
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    
    return render_template("report.html", chart=img_base64, table=df.to_html(index=False))

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
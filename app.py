# import hashlib # se necesita para hashing de contraseñas
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import pyodbc
import hashlib
import base64
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd
import io
import json

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

    productos = []
    for r in rows:
        productos.append({
            "id": r.idProducto,
            "name": str(r.nombre),
            "description": str(r.descripcion),
            "price": float(r.precio),
            "category": str(r.categoria).lower(),
            "image": f"data:image/png;base64,{r.imagen}" if r.imagen else "/static/img/default.png"
        })

    # 🔹 evitar escapes Unicode (\u00e9 → é)
    return app.response_class(
        response=json.dumps(productos, ensure_ascii=False),
        mimetype="application/json"
    )

@app.route("/report")
def analytics():
    if "username" not in session:
        return redirect(url_for("index"))
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.nombre as producto, p.precio, c.nombre as categoria
        FROM Productos p
        INNER JOIN Categorias c ON p.idCategoria = c.idCategoria
    """)
    rows = cursor.fetchall()
    conn.close()

    # Convertir a lista de tuplas para pandas
    data = [(r.producto, r.precio, r.categoria) for r in rows]
    df = pd.DataFrame(data, columns=["producto", "precio", "categoria"])

    # Convertir precios a float para evitar errores de tipo
    df['precio'] = pd.to_numeric(df['precio'], errors='coerce')  # convierte strings a float, NaN si no puede

    # Analisis:
    mas_caro = df.loc[df['precio'].idxmax()]
    mas_barato = df.loc[df['precio'].idxmin()]
    cantidad_por_categoria = df.groupby('categoria').size().to_dict()
    promedio_precio_categoria = df.groupby('categoria')['precio'].mean().round(0).astype(int).to_dict()  # redondea a entero

    # Pasar resultados al template
    return render_template(
        "report.html",
        mas_caro=mas_caro,
        mas_barato=mas_barato,
        cantidad_por_categoria=cantidad_por_categoria,
        promedio_precio_categoria=promedio_precio_categoria
    )


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
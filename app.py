from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import pyodbc
import hashlib
import base64

app = Flask(__name__)
app.secret_key = "clave_secreta_flask"

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-ELU753R\\SQLEXPRESS;"
    "DATABASE=TomassaCafeteria;"
    "Trusted_Connection=yes;"
)

def get_connection():
    return pyodbc.connect(CONNECTION_STRING)

@app.route("/")
def index():
    return render_template("index.html")

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

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
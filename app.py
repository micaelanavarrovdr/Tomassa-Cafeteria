from flask import Flask, render_template, request, redirect, url_for, flash, session
import pyodbc
import hashlib

app = Flask(__name__)
app.secret_key = "clave_secreta_flask"

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=nameServer;"
    "DATABASE=nameDB;"
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
    return render_template("adminPanel.html")

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

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template 
from flask import request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "clave_super_secreta_123"  
# Necesario para sesiones

# Conexión a la base de datos
def base_de_datos():
    conn = sqlite3.connect('login.db')
    conn.row_factory = sqlite3.Row  
    # Permite acceder a las columnas por nombre
    return conn

# Crear tabla si no existe
def crear_tabla():
    conn = base_de_datos()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

crear_tabla()

# Rutas de la aplicación
@app.route('/') # Es la ruta principal
def index():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    else:
        return redirect(url_for('login_page'))

# REGISTRO
@app.route('/register_page')
def register_page():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    
    conn = base_de_datos()
    try:
        conn.execute(
            'INSERT INTO users (username, password) VALUES (?, ?)',
            (username, password)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return "El usuario ya existe"
    
    conn.close()
    return redirect(url_for('login_page'))

# LOGIN
@app.route('/login_page')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    conn = base_de_datos()
    cursor = conn.execute(
        'SELECT * FROM users WHERE username = ? AND password = ?',
        (username, password)
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        session['username'] = username
        return redirect(url_for('index'))
    else:
        return "Usuario o contraseña incorrectos"
# LOGOUT
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login_page'))

# Ejecutar aplicación

if __name__ == '__main__':
    app.run(debug=True)

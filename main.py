import sqlite3
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)
DATABASE = "hardware/db/kora_cleanbot_database.db"
def init_db():
    conn = sqlite3.connect(DATABASE)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        names TEXT NOT NULL,
        surnames TEXT NOT NULL,
        code TEXT NOT NULL UNIQUE,
        points INTEGER DEFAULT 0,
        range TEXT DEFAULT 'Bronce',
        face_id BLOB NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

@app.route('/')
def home():
     return "Hello World"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.post("/register")
def register():

    names = request.form.get("names", "").strip()
    surnames = request.form.get("surnames", "").strip()
    code = request.form.get("code", "").strip()

    face = request.files.get("face_id")

    if not names or not surnames or not code or face is None:
        return jsonify({"error": "Todos los campos son obligatorios."}), 400

    face_blob = face.read()

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users
            (names, surnames, code, face_id)
            VALUES (?, ?, ?, ?)
        """, (
            names,
            surnames,
            code,
            face_blob
        ))

        conn.commit()

        return jsonify({
            "message": "Usuario registrado correctamente."
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Ese código ya existe."
        }), 409

    finally:
        conn.close()


@socketio.on('nueva_deteccion')
def handle_detection(data):
     emit('render_detection', data or {
          'objeto': "desconocido",
          'confianza': 0.0,
          'timestamp': "00:00:00"
     }, broadcast=True)

if __name__ == '__main__':
     init_db()
     socketio.run(app, host='127.0.0.1', port=5000, debug=True)
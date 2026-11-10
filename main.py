import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from flask_cors import CORS
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from hardware.status import get_status


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)
DATABASE = Path(__file__).resolve().parent / "hardware" / "db" / "kora_cleanbot_database.db"
_initial_status = get_status()
_latest_detection = {
    **_initial_status,
    "category": _initial_status.get("object_type"),
    "detected_objects": [],
}


@socketio.on("connect")
def send_current_detection():
    """Envía el último estado al cliente al conectarse."""
    emit("detection_update", _latest_detection)


@app.post("/detection")
def receive_detection():
    """Recibe el estado del detector y lo retransmite por WebSocket."""
    global _latest_detection

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Se esperaba un objeto JSON."}), 400

    category = data.get("object_type")
    if category not in (None, "person", "waste", "other"):
        return jsonify({"error": "object_type debe ser person, waste, other o null."}), 400

    detected_objects = data.get("detected_objects", [])
    if not isinstance(detected_objects, list):
        return jsonify({"error": "detected_objects debe ser una lista."}), 400

    tank_full = data.get("tank_full", False)
    if not isinstance(tank_full, bool):
        return jsonify({"error": "tank_full debe ser booleano."}), 400

    clean_objects = []
    for item in detected_objects:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        item_category = item.get("category")
        if (
            isinstance(name, str)
            and name.strip()
            and item_category in ("person", "waste", "other")
        ):
            clean_objects.append({"name": name.strip(), "category": item_category})

    _latest_detection = {
        "object_type": category,
        "category": category,
        "detected_objects": clean_objects,
        "tank_full": tank_full,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    socketio.emit("detection_update", _latest_detection)
    return jsonify({"message": "Detección difundida.", "data": _latest_detection}), 200


def init_db():
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
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

@app.get('/faces')
def faces():
    return jsonify(_latest_detection)

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

if __name__ == "__main__":
    init_db()
    socketio.run(app, host="127.0.0.1", port=5000, debug=True, use_reloader=False)
import sqlite3
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
DB_FILE = "hardware/kora_cleanbot_database.db"

@app.route('/')
def home():
     return "Hello World"

@socketio.on('nueva_deteccion')
def handle_detection(data):
     emit('render_detection', data or {
          'objeto': "desconocido",
          'confianza': 0.0,
          'timestamp': "00:00:00"
     }, broadcast=True)



if __name__ == '__main__':
     socketio.run(app, host='127.0.0.1', port=5000, debug=True)
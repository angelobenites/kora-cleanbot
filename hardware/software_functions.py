import json
from colorama import Fore, Back, Style, init
from tts import kora_voice
import sqlite3
import os

init()

route = "models/kora-local-cleanbot.json"
conn = sqlite3.connect('db/kora_cleanbot_database.db')
db = conn.cursor()

db.execute('''
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
''')

def kora_detect(object="person"):
     if object == "person":
          print(" ")
          with open(route, 'r', encoding='utf-8') as file:
               data = json.load(file)
               kora_voice(data["greet"] or "Hola, por el momento no puedo hablar.")
               print(Back.MAGENTA + Fore.WHITE + "Kora:" + Style.RESET_ALL + " " + data["greet"] or "Hola, por el momento no puedo hablar.")
               
     elif object == "waste":
          print(" ")
          with open(route, 'r', encoding='utf-8') as file:
               data = json.load(file)
               kora_voice(data["waste"] or "Hola, por el momento no puedo hablar.")
               print(Back.MAGENTA + Fore.WHITE + "Kora:" + Style.RESET_ALL + " " + data["waste"] or "Hola, por el momento no puedo hablar.")

     elif object == "completed":
          print(" ")
          with open(route, 'r', encoding='utf-8') as file:
               data = json.load(file)
               kora_voice(data["download"] or "Hola, por el momento no puedo hablar.")
               print(Back.MAGENTA + Fore.WHITE + "Kora:" + Style.RESET_ALL + " " + data["download"] or "Hola, por el momento no puedo hablar.")

def user_register(data):
     try:
          db.execute('''
               INSERT INTO users (names, surnames, code) VALUES (?, ?, ?)
          ''', (data["names"], data["surnames"], data["code"]))
          conn.commit()
          return True
     except sqlite3.IntegrityError:
          conn.rollback()
          return False

def increment_points(id, points_to_increment=1):
     try:
          db.execute('''
               UPDATE users SET points = points + ? WHERE id = ?
          ''', (points_to_increment, id,))
          db.execute('''
              UPDATE users SET range = 
              CASE 
                  WHEN points < 10 THEN 'Bronce'
                  WHEN points < 20 THEN 'Plata'
                  WHEN points < 30 THEN 'Oro'
                  WHEN points < 40 THEN 'Rubí'
                  WHEN points < 50 THEN 'Esmeralda'
                  WHEN points < 60 THEN 'Diamante'
                  WHEN points < 70 THEN 'Netherita'
                  WHEN points < 80 THEN 'Maestro'
                  WHEN points < 90 THEN 'Leyenda'
                  ELSE 'Rey de Reyes'
              END
              WHERE id = ?
          ''', (id,))

          conn.commit()
          return True
     except sqlite3.Error:
          conn.rollback()
          return False

def decrement_points(id, points_to_decrement=20):
     try:
          db.execute('''
               UPDATE users SET points = points - ? WHERE id = ?
          ''', (points_to_decrement, id,))
          db.execute('''
              UPDATE users SET range = 
              CASE 
                  WHEN points < 10 THEN 'Bronce'
                  WHEN points < 20 THEN 'Plata'
                  WHEN points < 30 THEN 'Oro'
                  WHEN points < 40 THEN 'Rubí'
                  WHEN points < 50 THEN 'Esmeralda'
                  WHEN points < 60 THEN 'Diamante'
                  WHEN points < 70 THEN 'Netherita'
                  WHEN points < 80 THEN 'Maestro'
                  WHEN points < 90 THEN 'Leyenda'
                  ELSE 'Rey de Reyes'
              END
              WHERE id = ?
          ''', (id,))

          conn.commit()
          return True
     except sqlite3.Error:
          conn.rollback()
          return False

def get_users():
    db.execute('SELECT id, names, range, points FROM users') 
    usuarios = db.fetchall()
    for usuario in usuarios:
         os.system('cls' if os.name == 'nt' else 'clear')
         print(f"ID: {usuario[0]}, Nombre: {usuario[1]}, Rango: {usuario[2]}, Puntos: {usuario[3]}")


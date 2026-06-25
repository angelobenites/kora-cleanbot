import sqlite3

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

name = input("Ingrese su nombre: ")
surnames = input("Ingrese sus apellidos: ")
code = input("Ingrese su código de usuario: ")

db.execute('''
     INSERT INTO users (names, surnames, code) VALUES (?, ?, ?)
''', (name, surnames, code))

conn.commit()
conn.close()
print("Usuario registrado exitosamente.")
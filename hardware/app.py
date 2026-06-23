import cv2
from ultralytics import YOLO
from hardware_functions import detected_person, detected_waste, detected_completed
from tts import kora_voice
import threading
# import socketio
import time
import sqlite3
import os



# sio = socketio.Client()

# try:
#     # sio.connect('http://localhost:5000')
#     print("Conectado al servidor Flask con éxito.")
# except Exception as e:
#     print(f"No se pudo conectar a Flask: {e}")

model = YOLO("models/yolo11n.pt")
cap = cv2.VideoCapture(0)

is_person_present = False
is_waste_present = False

WASTE_CLASSES = {
    "bottle", "cup", "fork", "knife", "spoon", "bowl",
    "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "pizza", "donut", "cake",
}


if not cap.isOpened():
    print("Error: No se pudo abrir la cámara web.")
    exit()

print("Cámara iniciada. Presiona 'q' para salir.")

conn = sqlite3.connect('kora_cleanbot_database.db')
db = conn.cursor()

db.execute('''
     CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          names TEXT NOT NULL,
          surnames TEXT NOT NULL,
          code TEXT NOT NULL UNIQUE,
          points INTEGER DEFAULT 0,
          range TEXT DEFAULT 'Bronce',
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
     )
''')

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, stream=True)
    person_detected_in_frame = False
    waste_detected_in_frame = False

    for r in results:
        draw_frame = r.plot()

        for c in r.boxes.cls:
            class_name = model.names[int(c)]

            if class_name == "person":
                person_detected_in_frame = True
                # sio.emit('nueva_deteccion', {
                #     'objeto': "person",
                #     'confianza': float(r.boxes.conf[0]),
                #     'timestamp': time.strftime("%H:%M:%S")
                # })
            elif class_name in WASTE_CLASSES:
                waste_detected_in_frame = True
                # sio.emit('nueva_deteccion', {
                #     'objeto': "waste",
                #     'confianza': float(r.boxes.conf[0]),
                #     'timestamp': time.strftime("%H:%M:%S")
                # })

    if person_detected_in_frame and not is_person_present:
        is_person_present = True
        threading.Thread(target=detected_person, daemon=True).start()
    elif not person_detected_in_frame and is_person_present:
        is_person_present = False

    if waste_detected_in_frame and not is_waste_present:
        is_waste_present = True
        threading.Thread(target=detected_waste, daemon=True).start()
    elif not waste_detected_in_frame and is_waste_present:
        is_waste_present = False

    cv2.imshow("Detección de Objetos YOLOv8 en Vivo", draw_frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('s') or key == ord('t'):
        detected_completed()
    elif key == ord('c'):
        os.system('py create_user.py')
    elif key == ord('q'):
        kora_voice("Apagando el sistema. ¡Hasta luego!")
        break

cap.release()
cv2.destroyAllWindows()

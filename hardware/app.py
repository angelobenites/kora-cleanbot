import cv2
from ultralytics import YOLO
from hardware_functions import detected_person, detected_waste, detected_completed
from tts import kora_voice
import threading
import sqlite3
import os
from deepface import DeepFace

model_objects = YOLO("models/yolo11n.pt")
model_face = YOLO("models/yolo11n-face.pt")

cap = cv2.VideoCapture(0)

is_person_present = False
is_waste_present = False
rostro_reconocido = "Desconocido"

DB_FACES_PATH = "./faces/" 

WASTE_CLASSES = {
    "bottle", "cup", "fork", "knife", "spoon", "bowl",
    "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "pizza", "donut", "cake",
}

if not cap.isOpened():
    print("Error: No se pudo abrir la cámara web.")
    exit()

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

def reconocer_usuario(face_crop):
    global rostro_reconocido
    try:
        resultado = DeepFace.find(
            img_path=face_crop, 
            db_path=DB_FACES_PATH, 
            model_name="VGG-Face", 
            detector_backend="skip", 
            enforce_detection=False,
            silent=True
        )

        if len(resultado) > 0 and not resultado[0].empty:
            path_coincidencia = resultado[0]['identity'].iloc[0]
            nombre_archivo = os.path.basename(path_coincidencia)
            nombre_sin_extension = os.path.splitext(nombre_archivo)[0]
            rostro_reconocido = nombre_sin_extension.capitalize()
            kora_voice(f"Bienvenido {rostro_reconocido}")
        else:
            rostro_reconocido = "Desconocido"
            kora_voice("Usuario no registrado")
            
    except Exception as e:
        rostro_reconocido = "Error"

while True:
    ret, frame = cap.read()
    if not ret:
        break

    draw_frame = frame.copy()

    results_obj = model_objects(frame, stream=True, verbose=False)
    waste_detected_in_frame = False

    for r in results_obj:
        for box in r.boxes:
            c = int(box.cls[0])
            class_name = model_objects.names[c]
            
            if class_name in WASTE_CLASSES:
                waste_detected_in_frame = True
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                cv2.rectangle(draw_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(draw_frame, class_name, (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    results_face = model_face(frame, stream=True, verbose=False)
    person_detected_in_frame = False
    face_crop = None

    for r in results_face:
        for box in r.boxes:
            person_detected_in_frame = True
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            h, w, _ = frame.shape
            y1, y2 = max(0, y1), min(h, y2)
            x1, x2 = max(0, x1), min(w, x2)
            
            face_crop = frame[y1:y2, x1:x2]
            cv2.rectangle(draw_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

    if person_detected_in_frame and not is_person_present:
        is_person_present = True
        threading.Thread(target=detected_person, daemon=True).start()
        
        if face_crop is not None and face_crop.size > 0:
            threading.Thread(target=reconocer_usuario, args=(face_crop,), daemon=True).start()

    elif not person_detected_in_frame and is_person_present:
        is_person_present = False
        rostro_reconocido = "Desconocido"

    if waste_detected_in_frame and not is_waste_present:
        is_waste_present = True
        threading.Thread(target=detected_waste, daemon=True).start()
    elif not waste_detected_in_frame and is_waste_present:
        is_waste_present = False

    if is_person_present:
        cv2.putText(draw_frame, f"User: {rostro_reconocido}", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Kora CleanBot", draw_frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('c') or key == ord('c'):
        detected_completed()
    elif key == ord('w'):
        os.system('start http://localhost:5173')
    elif key == ord('q'):
        kora_voice("Apagando")
        break

cap.release()
cv2.destroyAllWindows()

import cv2
from ultralytics import YOLO
from hardware_functions import detected_person, detected_waste, detected_completed
from tts import kora_voice
from status import update_status
from realtime import publish_detection
import threading
import os

# Cargar únicamente el modelo de objetos YOLOv8 nano
model = YOLO("models/yolov8n.pt")

cap = cv2.VideoCapture(0)

is_person_present = False
is_waste_present = False
tank_full = False

WASTE_CLASSES = {
    "bottle", "cup", "fork", "knife", "spoon", "bowl",
    "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "pizza", "donut", "cake",
}

if not cap.isOpened():
    print("Error: No se pudo abrir la cámara web.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    draw_frame = frame.copy()

    # Inferencia de YOLO para detección de objetos
    results = model(frame, stream=True, verbose=False)
    
    waste_detected_in_frame = False
    person_detected_in_frame = False
    detected_objects_in_frame = set()

    for r in results:
        for box in r.boxes:
            c = int(box.cls[0])
            class_name = model.names[c]
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

            # Detectar residuos
            if class_name in WASTE_CLASSES:
                waste_detected_in_frame = True
                detected_objects_in_frame.add((class_name, "waste"))
                cv2.rectangle(draw_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(draw_frame, class_name, (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            # Detectar personas usando el modelo YOLO de objetos
            elif class_name == "person":
                person_detected_in_frame = True
                detected_objects_in_frame.add((class_name, "person"))
                cv2.rectangle(draw_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(draw_frame, "Persona", (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            else:
                detected_objects_in_frame.add((class_name, "other"))
                cv2.rectangle(draw_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(draw_frame, class_name, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Evento al detectar o dejar de detectar personas
    if person_detected_in_frame and not is_person_present:
        is_person_present = True
        threading.Thread(target=detected_person, daemon=True).start()
    elif not person_detected_in_frame and is_person_present:
        is_person_present = False

    # Evento al detectar o dejar de detectar residuos
    if waste_detected_in_frame and not is_waste_present:
        is_waste_present = True
        threading.Thread(target=detected_waste, daemon=True).start()
    elif not waste_detected_in_frame and is_waste_present:
        is_waste_present = False

    # Actualizar estado global del robot
    visible_object = "person" if person_detected_in_frame else (
        "waste" if waste_detected_in_frame else (
            "other" if detected_objects_in_frame else None
        )
    )
    update_status(object_type=visible_object, tank_full=tank_full)
    publish_detection(
        object_type=visible_object,
        detected_objects=[
            {"name": name, "category": category}
            for name, category in sorted(detected_objects_in_frame)
        ],
        tank_full=tank_full,
    )

    # Mostrar ventana
    cv2.imshow("Kora CleanBot", draw_frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('c'):
        tank_full = True
        update_status(object_type=visible_object, tank_full=tank_full)
        detected_completed()
    elif key == ord('w'):
        # En Linux (Raspberry Pi) conviene usar xdg-open en vez de 'start' de Windows
        os.system('xdg-open http://localhost:5173 &')
    elif key == ord('q'):
        kora_voice("Apagando")
        break

cap.release()
cv2.destroyAllWindows()
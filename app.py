import cv2
from ultralytics import YOLO
from hardware_functions import detected_person, detected_waste
import threading

model = YOLO("models/yolov8n.pt")
cap = cv2.VideoCapture(0)

is_person_present = False
is_waste_present = False

WASTE_CLASSES = {
    "backpack", "umbrella", "handbag", "tie", "suitcase", 
    "bottle", "cup", "fork", "knife", "spoon", "bowl"
}

if not cap.isOpened():
    print("Error: No se pudo abrir la cámara web.")
    exit()

print("Cámara iniciada. Presiona 'q' para salir.")

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
            elif class_name in WASTE_CLASSES:
                waste_detected_in_frame = True

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

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

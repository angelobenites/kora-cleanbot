import cv2
from ultralytics import YOLO
from hardware_functions import detected_person
import time


model = YOLO("models/yolov8n.pt")
cap = cv2.VideoCapture(0)
last_greeting = 0
cooldown = 20

if not cap.isOpened():
    print("Error: No se pudo abrir la cámara web.")
    exit()

print("Cámara iniciada. Presiona 'q' para salir.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    
    results = model(frame, stream=True)

    
    for r in results:

        draw_frame = r.plot()

        for c in r.boxes.cls:
            class_name = model.names[int(c)]

            if class_name == "person":
                current_time = time.time()
                if current_time - last_greeting > cooldown:
                    detected_person()
                    last_greeting = current_time

    
    cv2.imshow("Detección de Objetos YOLOv8 en Vivo", draw_frame)

    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

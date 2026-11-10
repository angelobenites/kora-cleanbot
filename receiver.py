"""Recibe detecciones y actualiza las expresiones de la matriz LED."""

import json
from math import sin
import os
import threading
import time

import socketio

SERVER_URL = os.getenv("KORA_SERVER_URL", "http://127.0.0.1:5000")
RETRY_SECONDS = 2
FACE_BY_CATEGORY = {
    "person": "alegre",
    "waste": "sorprendido",
    "other": "serio",
}

_latest_detection = {"object_type": None, "tank_full": False}
_state_lock = threading.Lock()
_connected = threading.Event()
_stop_display = threading.Event()
client = socketio.Client(reconnection=True)


class MatrixFaceDisplay:
    """Renderiza una expresión en una matriz RGB 64x32."""

    def __init__(self):
        from PIL import Image, ImageDraw
        from rgbmatrix import RGBMatrix, RGBMatrixOptions

        self.Image = Image
        self.ImageDraw = ImageDraw
        options = RGBMatrixOptions()
        options.rows = 32
        options.cols = 64
        options.chain_length = 1
        options.parallel = 1
        options.hardware_mapping = "regular"
        options.disable_hardware_pulsing = True
        options.gpio_slowdown = 4
        self.matrix = RGBMatrix(options=options)
        self._thread = threading.Thread(target=self._render_loop, daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        _stop_display.set()
        if self._thread.is_alive():
            self._thread.join(timeout=1)
        self.matrix.Clear()

    def _render_loop(self):
        started_at = time.monotonic()
        while not _stop_display.is_set():
            with _state_lock:
                detection = dict(_latest_detection)

            if detection.get("tank_full") is True:
                expression = "enojado"
            elif not _connected.is_set():
                expression = "triste"
            else:
                expression = FACE_BY_CATEGORY.get(
                    detection.get("object_type"), "serio"
                )

            image = self.Image.new("RGB", (64, 32), (0, 0, 0))
            draw = self.ImageDraw.Draw(image)
            elapsed = time.monotonic() - started_at
            self._draw_expression(draw, expression, elapsed)
            self.matrix.SetImage(image)
            _stop_display.wait(0.1)

    @staticmethod
    def _draw_expression(draw, expression, elapsed):
        if expression == "alegre":
            color = (0, 255, 100)
            draw.arc([10, 8, 26, 22], 200, 340, fill=color, width=3)
            draw.arc([38, 8, 54, 22], 200, 340, fill=color, width=3)
            draw.arc([23, 16, 41, 30], 0, 180, fill=color, width=2)
        elif expression == "sorprendido":
            color = (255, 255, 255)
            radius = 1 + int(abs(sin(elapsed * 4)))
            draw.ellipse([12 - radius, 8 - radius, 24 + radius, 20 + radius], fill=color)
            draw.ellipse([40 - radius, 8 - radius, 52 + radius, 20 + radius], fill=color)
            draw.ellipse([27, 21, 37, 31], outline=color, width=2)
        elif expression == "enojado":
            color = (255, 0, 0)
            draw.rectangle([12, 12, 24, 24], fill=color)
            draw.rectangle([40, 12, 52, 24], fill=color)
            draw.line([10, 8, 26, 15], fill=color, width=2)
            draw.line([54, 8, 38, 15], fill=color, width=2)
            draw.line([26, 27, 38, 25], fill=color, width=2)
        elif expression == "triste":
            color = (0, 120, 255)
            draw.rectangle([12, 10, 24, 20], outline=color, width=2)
            draw.rectangle([40, 10, 52, 20], outline=color, width=2)
            draw.rectangle([15, 16, 21, 20], fill=color)
            draw.rectangle([43, 16, 49, 20], fill=color)
            draw.arc([26, 22, 38, 30], 180, 360, fill=color, width=2)
            if int(elapsed * 3) % 2 == 0:
                draw.line([40, 22, 40, 26], fill=(0, 200, 255), width=2)
        else:
            color = (0, 255, 255)
            if int(elapsed * 2) % 5 == 0:
                draw.line([12, 15, 24, 15], fill=color, width=2)
                draw.line([40, 15, 52, 15], fill=color, width=2)
            else:
                draw.rectangle([12, 10, 24, 20], fill=color)
                draw.rectangle([40, 10, 52, 20], fill=color)
            draw.line([26, 25, 38, 25], fill=color, width=2)


@client.event
def connect():
    _connected.set()
    print(f"Conectado al servidor de detecciones: {SERVER_URL}")


@client.event
def disconnect():
    _connected.clear()
    print("Conexión con el servidor cerrada.")


@client.on("detection_update")
def receive_detection(data):
    """Actualiza el estado compartido con la detección más reciente."""
    if not isinstance(data, dict):
        return

    with _state_lock:
        _latest_detection.update(
            object_type=data.get("object_type", data.get("category")),
            tank_full=data.get("tank_full") is True,
        )

    print("\nDetección recibida:")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main():
    display = None
    try:
        try:
            display = MatrixFaceDisplay()
            display.start()
        except (ImportError, OSError, RuntimeError) as error:
            print(f"Matriz LED no disponible; solo se mostrarán eventos: {error}")

        while True:
            try:
                client.connect(SERVER_URL, wait_timeout=5)
                client.wait()
            except socketio.exceptions.ConnectionError as error:
                print(f"Servidor no disponible ({error}); reintentando en {RETRY_SECONDS}s.")
                time.sleep(RETRY_SECONDS)
    except KeyboardInterrupt:
        print("\nReceptor detenido.")
    finally:
        if client.connected:
            client.disconnect()
        if display is not None:
            display.stop()


if __name__ == "__main__":
    main()

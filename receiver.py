"""Escucha las detecciones emitidas por el servidor local de Kora."""

import json
import os
import time

import socketio

SERVER_URL = os.getenv("KORA_SERVER_URL", "http://127.0.0.1:5000")
RETRY_SECONDS = 2
client = socketio.Client(reconnection=True)


@client.event
def connect():
    print(f"Conectado al servidor de detecciones: {SERVER_URL}")


@client.event
def disconnect():
    print("Conexión con el servidor cerrada.")


@client.on("detection_update")
def receive_detection(data):
    """Muestra el estado recibido en tiempo real."""
    print("\nDetección recibida:")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main():
    try:
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


if __name__ == "__main__":
    main()

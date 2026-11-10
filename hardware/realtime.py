"""Publica cambios del detector en el servidor Flask local."""

import json
import time
from threading import Lock
from urllib.error import URLError
from urllib.request import Request, urlopen

SERVER_URL = "http://127.0.0.1:5000/detection"
_RETRY_INTERVAL_SECONDS = 2
_last_sent = None
_last_failed = None
_last_attempt = 0.0
_lock = Lock()


def publish_detection(object_type=None, detected_objects=None, tank_full=False):
    """Envía el estado actual al servidor; omite fotogramas sin cambios."""
    global _last_sent, _last_failed, _last_attempt

    payload = {
        "object_type": object_type,
        "detected_objects": detected_objects or [],
        "tank_full": bool(tank_full),
    }
    signature = json.dumps(payload, sort_keys=True, ensure_ascii=False)

    with _lock:
        if signature == _last_sent:
            return True

        now = time.monotonic()
        if signature == _last_failed and now - _last_attempt < _RETRY_INTERVAL_SECONDS:
            return False
        _last_attempt = now

        request = Request(
            SERVER_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=1.5) as response:
                if response.status < 200 or response.status >= 300:
                    _last_failed = signature
                    return False
        except (URLError, TimeoutError, OSError):
            # El detector puede seguir funcionando si el servidor aún no arrancó.
            _last_failed = signature
            return False

        _last_sent = signature
        _last_failed = None
        return True

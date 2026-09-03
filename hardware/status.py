import json
import os
import tempfile
from threading import Lock


STATUS_FILE = os.path.join(os.path.dirname(__file__), "db", "detection_status.json")
_status_lock = Lock()
_last_status = None
DEFAULT_STATUS = {
    "object_type": None,
    "tank_full": False,
}


def get_status():
    with _status_lock:
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as status_file:
                status = json.load(status_file)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            status = {}

    return {**DEFAULT_STATUS, **status}


def update_status(object_type=None, tank_full=False):
    global _last_status

    status = {
        "object_type": object_type,
        "tank_full": tank_full,
    }

    if status == _last_status:
        return

    os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
    with _status_lock:
        if status == _last_status:
            return

        file_descriptor, temporary_file = tempfile.mkstemp(
            dir=os.path.dirname(STATUS_FILE),
            prefix="detection_status_",
            suffix=".tmp",
        )
        try:
            with os.fdopen(file_descriptor, "w", encoding="utf-8") as status_file:
                json.dump(status, status_file)
            os.replace(temporary_file, STATUS_FILE)
        finally:
            if os.path.exists(temporary_file):
                os.remove(temporary_file)
        _last_status = status
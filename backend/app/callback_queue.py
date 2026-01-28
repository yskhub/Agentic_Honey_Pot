import os
import json
import time
import threading
import requests
from pathlib import Path
from .audit import append_event

QUEUE_DIR = Path(os.getenv("CALLBACK_QUEUE_DIR", "data/callback_queue"))
QUEUE_DIR.mkdir(parents=True, exist_ok=True)
RETRY_INTERVAL = int(os.getenv("CALLBACK_RETRY_INTERVAL", "30"))  # seconds


def _queue_file_name():
    return str(int(time.time() * 1000)) + ".json"


def enqueue(payload: dict):
    # write payload to a file for persistent retry
    fname = QUEUE_DIR / _queue_file_name()
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    append_event("callback_enqueued", {"file": str(fname), "sessionId": payload.get("sessionId")})
    return str(fname)


def _process_file(path: Path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        guvi_url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
        guvi_key = os.getenv("GUVI_API_KEY", "")
        headers = {"Content-Type": "application/json", "x-api-key": guvi_key}
        resp = requests.post(guvi_url, json=payload, headers=headers, timeout=5)
        resp.raise_for_status()
        append_event("callback_sent_from_queue", {"file": str(path), "status": resp.status_code})
        path.unlink()
        return True
    except Exception as e:
        append_event("callback_queue_error", {"file": str(path), "error": str(e)})
        return False


def process_queue_once():
    files = sorted(QUEUE_DIR.glob("*.json"))
    for f in files:
        _process_file(f)


def _worker_loop():
    while True:
        try:
            process_queue_once()
        except Exception as e:
            append_event("callback_queue_worker_error", {"error": str(e)})
        time.sleep(RETRY_INTERVAL)


_worker_thread = None


def start_worker():
    global _worker_thread
    if _worker_thread and _worker_thread.is_alive():
        return
    _worker_thread = threading.Thread(target=_worker_loop, daemon=True)
    _worker_thread.start()
    append_event("callback_worker_started", {"interval": RETRY_INTERVAL})


import os
import requests
from .audit import append_event
from .callback_queue import enqueue
from .circuit_breaker import outgoing_breaker
import time


def send_guvi_callback(payload: dict):
    """Attempt to send final result to GUVI, with retries and enqueue fallback."""
    if not outgoing_breaker.allow():
        append_event('guvi_callback_shortcircuited', {'sessionId': payload.get('sessionId')})
        return {'status': 'shortcircuited'}

    guvi_url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    guvi_key = os.getenv("GUVI_API_KEY", "")
    headers = {"Content-Type": "application/json", "x-api-key": guvi_key}

    attempts = 0
    max_attempts = 3
    backoff = 1
    while attempts < max_attempts:
        try:
            resp = requests.post(guvi_url, json=payload, headers=headers, timeout=5)
            resp.raise_for_status()
            try:
                outgoing_breaker.record_success()
            except Exception:
                pass
            append_event("guvi_callback_sent", {"payload": payload, "status": resp.status_code})
            return {"status": "sent", "code": resp.status_code}
        except Exception as e:
            attempts += 1
            try:
                outgoing_breaker.record_failure()
            except Exception:
                pass
            append_event("guvi_callback_error", {"attempt": attempts, "error": str(e)})
            time.sleep(backoff)
            backoff *= 2

    # Enqueue for persistent retry
    try:
        enqueue(payload)
    except Exception:
        append_event("enqueue_failed", {"sessionId": payload.get("sessionId")})
    return {"status": "failed_enqueued", "attempts": attempts}

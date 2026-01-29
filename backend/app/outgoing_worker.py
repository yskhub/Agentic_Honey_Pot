import os
import time
import threading
import requests
from datetime import datetime
from .db import SessionLocal, OutgoingMessage
from .audit import append_event
import json
from pathlib import Path
from backend.phase4.metrics import OUTGOING_ATTEMPTS, OUTGOING_SUCCESS, OUTGOING_FAILURE

# Place logs in repository `logs/` directory (resolve repo root reliably)
REPO_ROOT = Path(__file__).resolve().parents[2]
LOG_PATH = Path(os.getenv('OUTGOING_HTTP_LOG', str(REPO_ROOT / 'logs' / 'outgoing_http.log')))
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def _write_http_log(entry: dict):
    try:
        # prefer structured logging via sentinel.http if configured
        import logging
        logger = logging.getLogger('sentinel.http')
        if logger and logger.handlers:
            logger.info(entry)
            return
    except Exception:
        pass
    try:
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, default=str) + '\n')
    except Exception:
        pass

INTERVAL = int(os.getenv("OUTGOING_WORKER_INTERVAL", "5"))
OUT_ENDPOINT = os.getenv("OUTGOING_ENDPOINT", "")
OUT_API_KEY = os.getenv("OUTGOING_API_KEY", "")


def _process_one(db):
    msgs = db.query(OutgoingMessage).filter(OutgoingMessage.status == 'queued').order_by(OutgoingMessage.created_at).limit(10).all()
    for m in msgs:
        try:
            payload = {"sessionId": m.session_id, "content": m.content}
            if OUT_ENDPOINT:
                headers = {"Content-Type": "application/json"}
                if OUT_API_KEY:
                    headers["x-api-key"] = OUT_API_KEY
                try:
                    OUTGOING_ATTEMPTS.inc()
                except Exception:
                    pass
                # record attempt
                append_event("outgoing_attempt", {"id": m.id, "sessionId": m.session_id, "endpoint": OUT_ENDPOINT})
                _write_http_log({"ts": datetime.utcnow().isoformat(), "event": "request", "id": m.id, "sessionId": m.session_id, "endpoint": OUT_ENDPOINT, "request": payload})
                resp = requests.post(OUT_ENDPOINT, json=payload, headers=headers, timeout=8)
                # log status and body
                status_code = getattr(resp, 'status_code', None)
                text = None
                try:
                    text = resp.text
                except Exception:
                    text = None
                _write_http_log({"ts": datetime.utcnow().isoformat(), "event": "response", "id": m.id, "sessionId": m.session_id, "endpoint": OUT_ENDPOINT, "status": status_code, "response_body": text})
                resp.raise_for_status()
                m.status = 'sent'
                append_event("outgoing_sent", {"id": m.id, "sessionId": m.session_id, "status": status_code, "response_body": text})
                try:
                    OUTGOING_SUCCESS.inc()
                except Exception:
                    pass
            else:
                # no endpoint configured: mark as simulated sent
                try:
                    OUTGOING_ATTEMPTS.inc()
                except Exception:
                    pass
                m.status = 'sent'
                append_event("outgoing_sent_simulated", {"id": m.id, "sessionId": m.session_id})
                _write_http_log({"ts": datetime.utcnow().isoformat(), "event": "simulated_sent", "id": m.id, "sessionId": m.session_id, "content": m.content})
            db.add(m)
            db.commit()
        except Exception as e:
            # record failure, include exception and any response text
            try:
                m.status = 'failed'
                db.add(m)
                db.commit()
            except Exception:
                # log error
                _write_http_log({"ts": datetime.utcnow().isoformat(), "event": "error", "id": getattr(m, 'id', None), "sessionId": getattr(m, 'session_id', None), "error": str(e)})
                try:
                    m.status = 'failed'
                    db.add(m)
                    db.commit()
                except Exception:
                    try:
                        db.rollback()
                    except Exception:
                        pass
            append_event("outgoing_send_error", {"id": getattr(m, 'id', None), "error": str(e)})
            try:
                OUTGOING_FAILURE.inc()
            except Exception:
                pass


def _worker_loop():
    db = SessionLocal()
    try:
        while True:
            try:
                _process_one(db)
            except Exception as e:
                append_event("outgoing_worker_error", {"error": str(e)})
            time.sleep(INTERVAL)
    finally:
        try:
            db.close()
        except Exception:
            pass


_thread = None


def start_outgoing_worker():
    global _thread
    if _thread and _thread.is_alive():
        return
    _thread = threading.Thread(target=_worker_loop, daemon=True)
    _thread.start()
    append_event("outgoing_worker_started", {"interval": INTERVAL, "endpoint_configured": bool(OUT_ENDPOINT)})

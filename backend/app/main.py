from fastapi import FastAPI, Response
from .routes import router
from .db import init_db
from dotenv import load_dotenv
import os
from .callback_queue import start_worker
from .outgoing_worker import start_outgoing_worker
from backend.phase4.metrics import metrics_payload
from backend.logging_config import setup_logging

load_dotenv()
setup_logging()
init_db()

app = FastAPI(title="SentinelTrap Honeypot")

app.include_router(router)


@app.get('/metrics')
def metrics():
    try:
        data = metrics_payload()
        return Response(content=data, media_type='text/plain')
    except Exception:
        return Response(content=b'', media_type='text/plain')


@app.get('/health')
def health():
    return {"ok": True}

@app.on_event("startup")
def startup_event():
    # Placeholder for model loads if needed
    print("Server starting. Detector threshold:", os.getenv("DETECTOR_THRESHOLD", "0.5"))
    # start persistent callback queue worker
    try:
        start_worker()
    except Exception as e:
        print("Failed to start callback queue worker:", e)
    try:
        start_outgoing_worker()
    except Exception as e:
        print("Failed to start outgoing worker:", e)

from fastapi import FastAPI
from .routes import router
from .db import init_db
from dotenv import load_dotenv
import os
from .callback_queue import start_worker
from .outgoing_worker import start_outgoing_worker

load_dotenv()
init_db()

app = FastAPI(title="SentinelTrap Honeypot")

app.include_router(router)

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

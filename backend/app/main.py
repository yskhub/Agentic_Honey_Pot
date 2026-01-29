from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from time import monotonic
from starlette.types import ASGIApp, Receive, Scope, Send
from backend.phase4.metrics import record_request_latency
from .profiler import add_slow_request
import os
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

# CORS: allow Next.js dev server origins for browser-based judge UI
origins = [
    os.getenv('NEXT_PUBLIC_BASE_URL', 'http://localhost:3000'),
    os.getenv('NEXT_PUBLIC_BASE_URL', 'http://127.0.0.1:3000')
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(router)


@app.middleware("http")
async def timing_middleware(request, call_next):
    start = monotonic()
    try:
        response = await call_next(request)
        return response
    finally:
        dur = monotonic() - start
        # use request.url.path to label
        try:
            path = request.url.path
            record_request_latency(path, dur)
            thresh = float(os.getenv('SLOW_REQUEST_THRESHOLD', '0.5'))
            if dur > thresh:
                add_slow_request(path, request.method, dur)
        except Exception:
            pass


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

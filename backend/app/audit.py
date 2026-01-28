import hmac
import hashlib
import json
from datetime import datetime
import os
from pathlib import Path

LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_FILE = LOG_DIR / "audit.log"

# HMAC key for tamper-evidence
HMAC_KEY = os.getenv("AUDIT_HMAC_KEY", "change_this_secret")


def _sign(data: bytes) -> str:
    return hmac.new(HMAC_KEY.encode("utf-8"), data, hashlib.sha256).hexdigest()


def append_event(event_type: str, payload: dict):
    entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "type": event_type,
        "payload": payload
    }
    raw = json.dumps(entry, separators=(",", ":"), sort_keys=True).encode("utf-8")
    sig = _sign(raw)
    with open(AUDIT_FILE, "ab") as f:
        f.write(raw + b"\n")
        f.write((sig + "\n").encode("utf-8"))


def read_events():
    if not AUDIT_FILE.exists():
        return []
    events = []
    with open(AUDIT_FILE, "rb") as f:
        lines = f.read().splitlines()
    # lines: raw, sig, raw, sig, ...
    for i in range(0, len(lines), 2):
        raw = lines[i]
        sig = lines[i+1].decode("utf-8") if i+1 < len(lines) else ""
        events.append({"raw": raw.decode("utf-8"), "sig": sig})
    return events

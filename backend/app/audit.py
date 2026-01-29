import hmac
import hashlib
import json
from datetime import datetime
import os
from pathlib import Path
import logging

# structured logger
_audit_logger = logging.getLogger('sentinel.audit')

LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_FILE = LOG_DIR / "audit.log"

# HMAC key for tamper-evidence
HMAC_KEY = os.getenv("AUDIT_HMAC_KEY", None)
# Optional next key used during rotation. When present, verification will accept
# signatures produced by either key. To sign new entries with the new key set
# `AUDIT_HMAC_KEY_USE_NEXT=1` in the environment.
HMAC_KEY_NEXT = os.getenv("AUDIT_HMAC_KEY_NEXT", None)
USE_NEXT_FOR_SIGN = os.getenv("AUDIT_HMAC_KEY_USE_NEXT", "0") == "1"


def _sign_with_key(data: bytes, key: str) -> str:
    return hmac.new(key.encode("utf-8"), data, hashlib.sha256).hexdigest()


def _sign(data: bytes) -> str:
    key = None
    if USE_NEXT_FOR_SIGN and HMAC_KEY_NEXT:
        key = HMAC_KEY_NEXT
    elif HMAC_KEY:
        key = HMAC_KEY
    else:
        raise RuntimeError("No AUDIT_HMAC_KEY configured for signing audit entries")
    return _sign_with_key(data, key)


def _verify_signature(data: bytes, sig: str) -> bool:
    """Verify signature using current and next keys (if present)."""
    if HMAC_KEY:
        try:
            if hmac.compare_digest(_sign_with_key(data, HMAC_KEY), sig):
                return True
        except Exception:
            pass
    if HMAC_KEY_NEXT:
        try:
            if hmac.compare_digest(_sign_with_key(data, HMAC_KEY_NEXT), sig):
                return True
        except Exception:
            pass
    return False


def append_event(event_type: str, payload: dict):
    entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "type": event_type,
        "payload": payload
    }
    raw = json.dumps(entry, separators=(",", ":"), sort_keys=True).encode("utf-8")
    sig = _sign(raw)
    # Preserve current two-line JSONL+sig format for streaming compatibility.
    with open(AUDIT_FILE, "ab") as f:
        f.write(raw + b"\n")
        f.write((sig + "\n").encode("utf-8"))
    try:
        # also emit structured JSON line to audit logger
        # include an indicator of which key was used for signing (best-effort)
        log_entry = dict(entry)
        log_entry["_audit_signed_with_next"] = USE_NEXT_FOR_SIGN and bool(HMAC_KEY_NEXT)
        _audit_logger.info(log_entry)
    except Exception:
        pass


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
        valid = False
        try:
            valid = _verify_signature(raw, sig)
        except Exception:
            valid = False
        events.append({"raw": raw.decode("utf-8"), "sig": sig, "valid": valid})
    return events

import time
from collections import deque
import os
from threading import Lock

# Simple sliding window rate limiter per API key
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds
RATE_LIMIT_MAX = int(os.getenv("RATE_LIMIT_MAX", "60"))

_lock = Lock()
_buckets = {}  # api_key -> deque of timestamps


def is_allowed(api_key: str) -> bool:
    now = time.time()
    with _lock:
        dq = _buckets.get(api_key)
        if dq is None:
            dq = deque()
            _buckets[api_key] = dq
        # prune old
        while dq and dq[0] < now - RATE_LIMIT_WINDOW:
            dq.popleft()
        if len(dq) >= RATE_LIMIT_MAX:
            return False
        dq.append(now)
        return True


def get_usage(api_key: str) -> dict:
    now = time.time()
    with _lock:
        dq = _buckets.get(api_key) or deque()
        while dq and dq[0] < now - RATE_LIMIT_WINDOW:
            dq.popleft()
        return {"window_seconds": RATE_LIMIT_WINDOW, "count": len(dq), "limit": RATE_LIMIT_MAX}

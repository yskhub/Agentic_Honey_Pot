from collections import deque
from threading import Lock
from datetime import datetime
from typing import List, Dict

# Simple thread-safe ring buffer for slow request records
_lock = Lock()
_buf: deque = deque(maxlen=200)


def add_slow_request(path: str, method: str, duration: float, info: Dict = None):
    rec = {
        'ts': datetime.utcnow().isoformat() + 'Z',
        'path': path,
        'method': method,
        'duration': float(duration),
        'info': info or {}
    }
    with _lock:
        _buf.appendleft(rec)


def get_recent_slow_requests(limit: int = 50) -> List[Dict]:
    with _lock:
        items = list(_buf)[:limit]
    return items

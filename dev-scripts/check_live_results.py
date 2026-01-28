import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import time
from backend.app.db import SessionLocal, OutgoingMessage

SID = 'live-server-001'

def tail(path, n=80):
    try:
        with open(path, 'rb') as f:
            f.seek(0, 2)
            end = f.tell()
            size = 1024
            data = b''
            while end > 0 and data.count(b'\n') <= n:
                toread = min(size, end)
                f.seek(end - toread)
                chunk = f.read(toread)
                data = chunk + data
                end -= toread
            return data.decode('utf-8', errors='replace').splitlines()[-n:]
    except FileNotFoundError:
        return []

time.sleep(3)
db = SessionLocal()
try:
    rows = db.query(OutgoingMessage).filter(OutgoingMessage.session_id == SID).all()
    print('Outgoing rows for', SID, len(rows))
    for r in rows:
        print('ROW:', r.id, r.content, r.status, r.created_at)
finally:
    try:
        db.close()
    except Exception:
        pass

print('\nLast audit.log lines:')
for l in tail('logs/audit.log', n=80):
    print(l)

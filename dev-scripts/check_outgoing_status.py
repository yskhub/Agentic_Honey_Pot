from pathlib import Path
import sys
import time
sys.path.insert(0, str(Path('.').resolve()))
from backend.app.db import SessionLocal, OutgoingMessage

print('waiting 6s for worker...')
time.sleep(6)
db = SessionLocal()
try:
    rows = db.query(OutgoingMessage).filter(OutgoingMessage.session_id == 'tc-e2e-001').all()
    for r in rows:
        print(r.id, r.content, r.status)
finally:
    try:
        db.close()
    except Exception:
        pass

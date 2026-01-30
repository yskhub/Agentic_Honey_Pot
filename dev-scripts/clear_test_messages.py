import os
import sys

# ensure project root is on sys.path so `backend` imports resolve
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.app.db import SessionLocal, Message as DBMessage

db = SessionLocal()
count = db.query(DBMessage).filter(DBMessage.session_id=='test-session-sse').count()
print('messages for test-session-sse before:', count)
if count > 10:
    # keep the most recent 5
    rows = db.query(DBMessage).filter(DBMessage.session_id=='test-session-sse').order_by(DBMessage.timestamp.desc()).offset(5).all()
    ids = [r.id for r in rows]
    if ids:
        db.query(DBMessage).filter(DBMessage.id.in_(ids)).delete(synchronize_session=False)
        db.commit()
        print('deleted', len(ids), 'old messages')
else:
    print('nothing to delete')

count2 = db.query(DBMessage).filter(DBMessage.session_id=='test-session-sse').count()
print('messages for test-session-sse after:', count2)
db.close()

import os
import time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db import SessionLocal, OutgoingMessage

os.environ['API_KEY'] = os.environ.get('API_KEY', 'test_tc_key')
os.environ['ADMIN_API_KEY'] = os.environ.get('ADMIN_API_KEY', 'test_admin_key')

client = TestClient(app)

sid = 'tc-e2e-001'
payload = {
    'sessionId': sid,
    'message': {'sender': 'scammer', 'text': 'Send money to my UPI id scammer@upi please', 'timestamp': '2026-01-01T00:00:00Z'},
    'conversationHistory': [],
    'metadata': {}
}

headers = {'x-api-key': os.environ['API_KEY']}

print('Posting message via TestClient...')
r = client.post('/v1/message', json=payload, headers=headers)
print('resp:', r.status_code, r.json())

time.sleep(8)

db = SessionLocal()
try:
    outs = db.query(OutgoingMessage).filter(OutgoingMessage.session_id == sid).all()
    print('Outgoing messages found:', len(outs))
    for o in outs:
        print('OUT', o.id, o.content, o.status)
finally:
    try:
        db.close()
    except Exception:
        pass

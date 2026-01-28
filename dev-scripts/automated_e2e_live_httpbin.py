import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db import SessionLocal, OutgoingMessage

# configure to use httpbin
os.environ['OUTGOING_ENDPOINT'] = 'https://httpbin.org/post'
os.environ['OUTGOING_API_KEY'] = ''
os.environ['API_KEY'] = os.environ.get('API_KEY', 'test_client_key')
os.environ['ADMIN_API_KEY'] = os.environ.get('ADMIN_API_KEY', 'test_admin_key')

client = TestClient(app)

def run():
    sid = 'live-e2e-001'
    payload = {
        'sessionId': sid,
        'message': {'sender': 'scammer', 'text': 'Please send money to my UPI scam@bank', 'timestamp': '2026-01-01T00:00:00Z'},
        'conversationHistory': [],
        'metadata': {}
    }
    headers = {'x-api-key': os.environ['API_KEY']}
    print('Posting to /v1/message')
    r = client.post('/v1/message', json=payload, headers=headers)
    print('POST', r.status_code, r.json())
    print('Waiting up to 12s for worker...')
    time.sleep(12)
    db = SessionLocal()
    try:
        outs = db.query(OutgoingMessage).filter(OutgoingMessage.session_id == sid).all()
        print('Outgoing:', len(outs))
        for o in outs:
            print('ROW:', o.id, o.content, o.status)
    finally:
        try:
            db.close()
        except Exception:
            pass

if __name__ == '__main__':
    run()

import os
import time
import requests
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.app.db import SessionLocal, OutgoingMessage

API_URL = os.environ.get('API_URL', 'http://127.0.0.1:8001')
API_KEY = os.environ.get('API_KEY', 'test_server_key')
ADMIN_KEY = os.environ.get('ADMIN_API_KEY', 'test_admin_key')

def post_message(sid, text):
    payload = {
        'sessionId': sid,
        'message': {'sender': 'scammer', 'text': text, 'timestamp': '2026-01-01T00:00:00Z'},
        'conversationHistory': [],
        'metadata': {}
    }
    headers = {'x-api-key': API_KEY}
    r = requests.post(API_URL + '/v1/message', json=payload, headers=headers, timeout=5)
    print('POST message', r.status_code, r.text)

def terminate(sid):
    headers = {'x-api-key': ADMIN_KEY}
    r = requests.post(API_URL + '/v1/admin/terminate-session', json={'sessionId': sid}, headers=headers, timeout=5)
    print('POST terminate', r.status_code, r.text)

if __name__ == '__main__':
    sid = 'e2e-run-001'
    post_message(sid, 'Please confirm your UPI id example@bank')
    time.sleep(1)
    post_message(sid, 'Send payment to my UPI scammer@upi now')
    time.sleep(1)
    terminate(sid)
    time.sleep(2)

    db = SessionLocal()
    try:
        rows = db.query(OutgoingMessage).filter(OutgoingMessage.session_id == sid).all()
        print('Outgoing rows:', len(rows))
        for r in rows:
            print('OUT:', r.id, r.session_id, r.content, r.status)
    finally:
        try:
            db.close()
        except Exception:
            pass

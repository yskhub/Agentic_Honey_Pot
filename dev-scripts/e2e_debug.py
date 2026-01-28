from fastapi.testclient import TestClient
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.app.main import app
from backend.app.db import SessionLocal, Message as DBMessage
from backend.app.db import ConversationState as CSModel
from backend.app.agent import respond as agent_respond

os.environ['API_KEY'] = os.environ.get('API_KEY', 'test_client_key')
os.environ['ADMIN_API_KEY'] = os.environ.get('ADMIN_API_KEY', 'test_admin_key')

client = TestClient(app)

sid = 'e2e-debug-001'
payload = {
    'sessionId': sid,
    'message': {'sender': 'scammer', 'text': 'Send money to my UPI id scammer@upi please', 'timestamp': '2026-01-01T00:00:00Z'},
    'conversationHistory': [],
    'metadata': {}
}
headers = {'x-api-key': os.environ['API_KEY']}

print('Posting payload...')
r = client.post('/v1/message', json=payload, headers=headers)
print('Status:', r.status_code)
print('Response:', r.json())

db = SessionLocal()
try:
    cs = db.query(CSModel).filter(CSModel.session_id == sid).first()
    print('ConversationState:', cs is not None, getattr(cs, 'human_override', None))
    msgs = db.query(DBMessage).filter(DBMessage.session_id == sid).all()
    print('DB messages count:', len(msgs))
    for m in msgs:
        print('MSG:', m.id, m.sender, m.text)

    print('\nCalling agent_respond directly...')
    try:
        resp = agent_respond(sid, payload['message']['text'], db)
        print('agent_respond returned:', resp)
    except Exception as e:
        print('agent_respond raised:', e)
    msgs2 = db.query(DBMessage).filter(DBMessage.session_id == sid).all()
    print('DB messages after direct call:', len(msgs2))
    for m in msgs2:
        print('MSG2:', m.id, m.sender, m.text)
finally:
    try:
        db.close()
    except Exception:
        pass

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db import SessionLocal, Message as DBMessage, ConversationState
import os


client = TestClient(app)


def test_e2e_agent_auto_reply_and_persist():
    # ensure API keys env loaded for test client
    os.environ['API_KEY'] = os.environ.get('API_KEY', 'test_client_key')
    os.environ['ADMIN_API_KEY'] = os.environ.get('ADMIN_API_KEY', 'test_admin_key')

    sid = 'e2e-session-001'
    payload = {
        'sessionId': sid,
        'message': {'sender': 'scammer', 'text': 'Send money to my UPI id scammer@upi please', 'timestamp': '2026-01-01T00:00:00Z'},
        'conversationHistory': [],
        'metadata': {}
    }
    headers = {'x-api-key': os.environ['API_KEY']}
    # post message (avoid direct ConversationState access to keep test resilient)

    r = client.post('/v1/message', json=payload, headers=headers)
    assert r.status_code == 200
    data = r.json()
    # routeToAgent should be true
    assert data.get('routeToAgent') is True

    # check DB for agent message persisted
    db = SessionLocal()
    msg = db.query(DBMessage).filter(DBMessage.session_id == sid, DBMessage.sender == 'agent').order_by(DBMessage.id.desc()).first()
    assert msg is not None
    db.close()

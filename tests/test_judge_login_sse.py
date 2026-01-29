import os
import json
from datetime import datetime
from backend.app.main import app
from fastapi.testclient import TestClient
from backend.app.db import SessionLocal, init_db, Session as DBSess, Message as DBMessage


def test_judge_login_and_sse_stream():
    os.environ['JUDGE_USERS'] = 'alice:password123'
    os.environ['ADMIN_SSE_SECRET'] = 'testsecret-for-ci'

    # Ensure DB initialized
    init_db()

    # create a session and one message
    db = SessionLocal()
    sess = db.query(DBSess).filter(DBSess.id == 'test-session-sse').first()
    if not sess:
        sess = DBSess(id='test-session-sse', metadata_json='{}')
        db.add(sess)
        db.commit()

    msg = DBMessage(session_id='test-session-sse', sender='user', text='hello-from-test', timestamp=datetime.utcnow())
    db.add(msg)
    db.commit()
    db.close()

    client = TestClient(app)

    # login as judge
    r = client.post('/admin/ui/judge-login', json={'username': 'alice', 'password': 'password123', 'session_id': 'test-session-sse'})
    assert r.status_code == 200, r.text
    body = r.json()
    assert 'token' in body
    token = body['token']

    # request SSE stream for the session using token and ensure we receive the inserted message
    sse_url = f'/admin/ui/sse/session/test-session-sse?token={token}'
    found = False
    with client.stream('GET', sse_url) as resp:
        assert resp.status_code == 200
        for raw in resp.iter_lines(timeout=2):
            if not raw:
                continue
            try:
                line = raw.decode('utf-8')
            except Exception:
                line = raw if isinstance(raw, str) else str(raw)
            if line.startswith('data: '):
                payload = json.loads(line.split('data: ', 1)[1])
                if payload.get('text') == 'hello-from-test':
                    found = True
                    break

    assert found, 'Expected SSE message not received'

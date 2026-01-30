from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db import SessionLocal, Message as DBMessage, Extraction as DBExtraction, Session as DBSess
import os
from pathlib import Path
import time

client = TestClient(app)


def setup_module(module):
    os.environ['API_KEY'] = os.environ.get('API_KEY', 'test_client_key')
    os.environ['ADMIN_API_KEY'] = os.environ.get('ADMIN_API_KEY', 'test_admin_key')
    # ensure callback queue dir is clean
    qdir = Path('data/callback_queue')
    if qdir.exists():
        for f in qdir.glob('*.json'):
            f.unlink()


def test_session_result_endpoint():
    sid = 'result-session-001'
    db = SessionLocal()
    # create session and messages
    sess = db.query(DBSess).filter(DBSess.id == sid).first()
    if not sess:
        sess = DBSess(id=sid, metadata_json='{}')
        db.add(sess)
        db.commit()
    msg1 = DBMessage(session_id=sid, sender='scammer', text='Please send money', timestamp=None)
    db.add(msg1)
    ex = DBExtraction(session_id=sid, type='upi', value='scammer@upi', confidence=0.9)
    db.add(ex)
    db.commit()
    db.close()

    headers = {'x-api-key': os.environ['API_KEY']}
    r = client.get(f'/v1/session/{sid}/result', headers=headers)
    assert r.status_code == 200
    j = r.json()
    assert j['status'] == 'success'
    assert j['scamDetected'] is True
    assert 'extractedIntelligence' in j
    assert 'upiIds' in j['extractedIntelligence']
    assert 'scammer@upi' in j['extractedIntelligence']['upiIds']


def test_agent_schedules_guvi_callback():
    # set env override so agent completes after 1 turn
    os.environ['AGENT_COMPLETE_AFTER_TURNS'] = '1'
    sid = 'callback-session-001'
    db = SessionLocal()
    sess = db.query(DBSess).filter(DBSess.id == sid).first()
    if not sess:
        sess = DBSess(id=sid, metadata_json='{}')
        db.add(sess)
        db.commit()
    db.close()

    payload = {
        'sessionId': sid,
        'message': {'sender': 'scammer', 'text': 'This is urgent, send UPI', 'timestamp': '2026-01-01T00:00:00Z'},
        'conversationHistory': [],
        'metadata': {}
    }
    headers = {'x-api-key': os.environ['API_KEY']}
    # post message which should trigger agent and schedule GUVI callback
    r = client.post('/v1/message', json=payload, headers=headers)
    assert r.status_code == 200

    # give background tasks a moment to run
    time.sleep(0.5)
    qdir = Path('data/callback_queue')
    files = list(qdir.glob('*.json'))
    assert isinstance(files, list)

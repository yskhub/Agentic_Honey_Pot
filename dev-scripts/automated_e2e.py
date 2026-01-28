import os
import sys
import time
import threading
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# start mock receiver early and set OUTGOING_ENDPOINT before importing the app
RECV_PORT = 9002
RECV_PATH = '/receive'
os.environ['OUTGOING_ENDPOINT'] = f'http://127.0.0.1:{RECV_PORT}{RECV_PATH}'
os.environ['OUTGOING_API_KEY'] = ''
os.environ['API_KEY'] = os.environ.get('API_KEY', 'test_client_key')
os.environ['ADMIN_API_KEY'] = os.environ.get('ADMIN_API_KEY', 'test_admin_key')

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db import SessionLocal, OutgoingMessage
import backend.app.outgoing_worker as ow


received = []


class MockHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != RECV_PATH:
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get('content-length', 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body.decode('utf-8'))
        except Exception:
            payload = body.decode('utf-8')
        received.append(payload)
        self.send_response(200)
        self.end_headers()


def start_mock():
    server = HTTPServer(('127.0.0.1', RECV_PORT), MockHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server


def run():
    # start mock receiver
    server = start_mock()
    os.environ['OUTGOING_ENDPOINT'] = f'http://127.0.0.1:{RECV_PORT}{RECV_PATH}'
    os.environ['OUTGOING_API_KEY'] = ''
    os.environ['API_KEY'] = os.environ.get('API_KEY', 'test_client_key')
    os.environ['ADMIN_API_KEY'] = os.environ.get('ADMIN_API_KEY', 'test_admin_key')

    client = TestClient(app)
    print('Outgoing worker endpoint config:', getattr(ow, 'OUT_ENDPOINT', None))
    # quick sanity post to mock receiver
    try:
        import requests
        r = requests.post(os.environ['OUTGOING_ENDPOINT'], json={'test': 'ping'}, timeout=2)
        print('Sanity post to mock receiver status:', r.status_code)
    except Exception as e:
        print('Sanity post failed:', e)

    sid = 'auto-e2e-001'
    payload = {
        'sessionId': sid,
        'message': {'sender': 'scammer', 'text': 'Please send to my UPI spam@bank', 'timestamp': '2026-01-01T00:00:00Z'},
        'conversationHistory': [],
        'metadata': {}
    }
    headers = {'x-api-key': os.environ['API_KEY']}

    print('Posting message to /v1/message')
    r = client.post('/v1/message', json=payload, headers=headers)
    print('POST resp:', r.status_code, r.json())

    # wait for worker to pick outgoing
    wait = 0
    print('Waiting for outgoing worker to process (up to 12s)')
    while wait < 12:
        time.sleep(1)
        wait += 1
    db = SessionLocal()
    try:
        outs = db.query(OutgoingMessage).filter(OutgoingMessage.session_id == sid).all()
        print('Outgoing rows found:', len(outs))
        for o in outs:
            print('OUT:', o.id, o.content, o.status)
    finally:
        try:
            db.close()
        except Exception:
            pass

    print('Mock receiver received:', len(received))
    for rcv in received:
        print('RECV:', rcv)

    # cleanup
    try:
        server.shutdown()
    except Exception:
        pass


if __name__ == '__main__':
    run()

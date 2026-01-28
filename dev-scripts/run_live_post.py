import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import os
import requests

API_URL = os.environ.get('API_URL', 'http://127.0.0.1:8020')
API_KEY = os.environ.get('API_KEY', 'test_server_key')

sid = 'live-server-001'
payload = {
    'sessionId': sid,
    'message': {'sender': 'scammer', 'text': 'Send money to my UPI id live@upi please', 'timestamp': '2026-01-01T00:00:00Z'},
    'conversationHistory': [],
    'metadata': {}
}

headers = {'x-api-key': API_KEY}

print('Posting to', API_URL + '/v1/message')
resp = requests.post(API_URL + '/v1/message', json=payload, headers=headers, timeout=10)
print('Status:', resp.status_code)
try:
    print('Body:', resp.json())
except Exception:
    print('Body (text):', resp.text)

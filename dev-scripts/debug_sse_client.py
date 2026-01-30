import os
import sys
from time import time

# ensure project root is on sys.path so `backend` package imports resolve
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ensure secret for test
os.environ['ADMIN_SSE_SECRET'] = os.environ.get('ADMIN_SSE_SECRET', 'testsecret-for-ci')

from backend.app.main import app
from fastapi.testclient import TestClient
from jose import jwt as jose_jwt

client = TestClient(app)

payload = {'iat': int(time()), 'exp': int(time()) + 120, 'session_id': 'test-session-sse'}
secret = os.environ['ADMIN_SSE_SECRET']

try:
    token = jose_jwt.encode(payload, secret, algorithm='HS256')
except Exception as e:
    print('token encode error', e)
    sys.exit(2)

sse_url = f'/admin/ui/sse/session/test-session-sse?token={token}'
print('requesting', sse_url)
with client.stream('GET', sse_url) as resp:
    print('status', resp.status_code)
    # try iter_content first
    try:
        for i, chunk in enumerate(resp.iter_content(chunk_size=64)):
            print(f'chunk {i} repr: {repr(chunk)}')
            if i >= 20:
                break
    except TypeError as e:
        print('iter_content TypeError, falling back to content read', e)
        body = resp.content
        print('content len', len(body))
    except Exception as e:
        print('iter_content exception', e)

print('done')

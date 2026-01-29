import os
import requests
from concurrent.futures import ThreadPoolExecutor

BACKEND = os.getenv('BACKEND_URL', 'http://127.0.0.1:8030')

def send(i):
    url = f"{BACKEND}/v1/message"
    payload = {
        'sessionId': f'smoke-{i%10}',
        'message': {'sender': 'user', 'text': f'hello {i}', 'timestamp': None},
        'metadata': {}
    }
    try:
        r = requests.post(url, json=payload, headers={'x-api-key': os.getenv('API_KEY','test_server_key')}, timeout=5)
        return r.status_code
    except Exception as e:
        return str(e)

def run_load(n=50, workers=10):
    with ThreadPoolExecutor(max_workers=workers) as ex:
        res = list(ex.map(send, range(n)))
    print(res[:20])

if __name__ == '__main__':
    run_load()

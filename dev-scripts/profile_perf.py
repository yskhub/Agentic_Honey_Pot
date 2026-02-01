"""Simple profiling script: post multiple messages and measure latency."""
import time
import requests
import os
import sys

# Accept backend URL as CLI arg or use env var BACKEND or fallback to 127.0.0.1:8030
BACKEND = None
if len(sys.argv) > 1:
    BACKEND = sys.argv[1]
BACKEND = BACKEND or os.environ.get('BACKEND') or os.environ.get('BACKEND_URL') or 'http://127.0.0.1:8030'
API_KEY = os.environ.get('API_KEY', 'test_client_key')

payload = {
    'sessionId': 'perf-session-001',
    'message': {'sender': 'scammer', 'text': 'Please send UPI', 'timestamp': None},
    'conversationHistory': [],
    'metadata': {}
}

def run(n=20, delay=0.1):
    url = BACKEND.rstrip('/') + '/v1/message'
    headers = {'x-api-key': API_KEY}
    times = []
    for i in range(n):
        t0 = time.perf_counter()
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        t1 = time.perf_counter()
        latency = (t1 - t0) * 1000.0
        times.append(latency)
        print(f"{i+1}/{n}: {r.status_code} {latency:.1f}ms")
        time.sleep(delay)
    print("-- Summary --")
    print(f"min {min(times):.1f}ms  median {sorted(times)[len(times)//2]:.1f}ms  mean {sum(times)/len(times):.1f}ms  max {max(times):.1f}ms")


if __name__ == '__main__':
    # allow passing backend url: python profile_perf.py http://127.0.0.1:8001
    run()

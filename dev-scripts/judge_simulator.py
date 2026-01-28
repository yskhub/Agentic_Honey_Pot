"""
Simple judge simulator to POST messages and trigger admin termination.
Usage:
  python dev-scripts/judge_simulator.py
"""
import requests
import os
import time
from datetime import datetime

API_URL = "http://localhost:8000"
API_KEY = os.getenv("API_KEY", "replace_with_client_api_key")
ADMIN_KEY = os.getenv("ADMIN_API_KEY", "replace_with_admin_key")

def post_message(session_id, text, sender="scammer"):
    payload = {
        "sessionId": session_id,
        "message": {
            "sender": sender,
            "text": text,
            "timestamp": datetime.utcnow().isoformat()
        },
        "conversationHistory": [],
        "metadata": {"channel": "SMS", "language": "en", "locale": "IN"}
    }
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    r = requests.post(API_URL + "/v1/message", json=payload, headers=headers, timeout=5)
    print("POST /v1/message", r.status_code, r.text)
    return r.json()

def terminate(session_id):
    headers = {"x-api-key": ADMIN_KEY, "Content-Type": "application/json"}
    r = requests.post(API_URL + "/v1/admin/terminate-session", json={"sessionId": session_id}, headers=headers, timeout=10)
    print("POST /v1/admin/terminate-session", r.status_code, r.text)
    return r.text

if __name__ == "__main__":
    sid = "test-session-001"
    post_message(sid, "Your bank account will be blocked today. Verify immediately.")
    time.sleep(1)
    post_message(sid, "Share your UPI ID to avoid account suspension.")
    time.sleep(1)
    terminate(sid)

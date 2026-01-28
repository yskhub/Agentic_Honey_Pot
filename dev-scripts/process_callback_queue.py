"""
Process any queued callback files immediately (manual runner).
Usage:
  python dev-scripts/process_callback_queue.py
"""
from backend.app.callback_queue import process_queue_once

if __name__ == "__main__":
    print("Processing callback queue once...")
    process_queue_once()
    print("Done")

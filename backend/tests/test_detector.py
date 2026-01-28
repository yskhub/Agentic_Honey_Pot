import sys
from pathlib import Path
import pytest

# Ensure repo root is on path so we can import backend.app.detector
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.detector import detect


def test_detector_detects_upi_and_urgency():
    text = "Share your UPI ID to avoid account suspension. Verify immediately!"
    res = detect(text)
    assert res["score"] > 0.5
    assert any("upi" in r or "upi_detected" in r for r in res.get("reasons", []) ) or len(res.get("matches", {}).get("upis", [])) > 0


def test_detector_detects_phone_and_url():
    text = "Please send payment to +91 98765 43210 or visit http://malicious.example.com"
    res = detect(text)
    assert res["score"] > 0.5
    assert len(res.get("matches", {}).get("phones", [])) >= 1
    assert len(res.get("matches", {}).get("urls", [])) >= 1


def test_detector_ignores_benign_message():
    text = "Hi there, are we still on for lunch tomorrow at the cafe?"
    res = detect(text)
    assert res["score"] < 0.2


if __name__ == "__main__":
    pytest.main([str(Path(__file__))])

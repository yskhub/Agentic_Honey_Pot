import re
from typing import Dict, Any, List
import os

KEYWORDS = [
    "verify", "account", "blocked", "upi", "transfer", "pay", "urgent",
    "immediately", "password", "otp", "pin", "bank", "paytm"
]

PHONE_RE = re.compile(r"(\+?\d{1,3}[\s-]?)?((?:\d[\s-]?){6,15}\d)")
UPI_RE = re.compile(r"\b[A-Za-z0-9.\-_]{3,}@[a-zA-Z]+\b")
URL_RE = re.compile(r"https?://[^\s]+|www\.[^\s]+")

def detect(text: str) -> Dict[str, Any]:
    text_lower = text.lower()
    score = 0.0
    reasons: List[str] = []
    matches = {"phones": [], "upis": [], "urls": []}

    # Keyword scoring
    kw_matches = [k for k in KEYWORDS if k in text_lower]
    if kw_matches:
        score += min(0.5, 0.05 * len(kw_matches))
        reasons.append(f"keywords:{', '.join(set(kw_matches))}")

    # Heuristic: presence of phrases indicating UPI request even if no id provided
    if "upi id" in text_lower or "share your upi" in text_lower or "share upi" in text_lower:
        score += 0.4
        reasons.append("upi_phrase_detected")
    # Heuristic: payment request phrase
    if "send payment" in text_lower or "send money" in text_lower or "share your upi" in text_lower:
        score += 0.2
        reasons.append("payment_phrase_detected")

    # Phone
    for m in PHONE_RE.findall(text):
        phone = "".join(m)
        # normalize: keep only digits and leading + if present
        norm = re.sub(r"[^0-9+]", "", phone)
        # ensure reasonable length
        if len(re.sub(r"\D", "", norm)) >= 6:
            matches["phones"].append(norm)
    if matches["phones"]:
        score += 0.3
        reasons.append("phone_detected")

    # UPI
    upi = UPI_RE.findall(text)
    if upi:
        matches["upis"].extend(upi)
        score += 0.4
        reasons.append("upi_detected")

    # URL
    urls = URL_RE.findall(text)
    if urls:
        matches["urls"].extend(urls)
        score += 0.2
        reasons.append("url_detected")

    # cap at 1.0
    if score > 1.0:
        score = 1.0

    return {"score": round(score, 3), "reasons": reasons, "matches": matches}

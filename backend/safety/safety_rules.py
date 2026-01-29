import re
from typing import Dict

# Patterns indicating monetary instructions or requests
_MONEY_VERB_RE = re.compile(r"\b(send|transfer|pay|deposit|wire|refund|give|request|collect|paytm|upi|payable)\b", re.IGNORECASE)
_MONEY_NOUN_RE = re.compile(r"\b(money|amount|rupees|rs\.?|inr|dollars|payment|payment link|account|bank|amounts?)\b", re.IGNORECASE)

# Phone-ish pattern (loose) and UPI id pattern
_PHONE_RE = re.compile(r"\+?\d[\d\-\s]{5,}\d")
_UPI_RE = re.compile(r"\b[\w.\-]{2,}@[a-zA-Z]{2,}\b")

# common payment words that often imply scam attempts when paired with identifiers
_PAYMENT_INDICATORS = re.compile(r"\b(upi id|upi|payment link|collect|send money|pay now|paytm|scan and pay)\b", re.IGNORECASE)

# PII numeric sequences to mask (6+ digits)
_PII_DIGITS_RE = re.compile(r"(\d{6,})")

def sanitize_reply(text: str) -> str:
    """Return a sanitized version of text with long digit sequences masked."""
    def _mask(m):
        s = m.group(1)
        # keep last 4 digits for traceability, mask the rest
        if len(s) <= 4:
            return 'X' * len(s)
        return 'X' * (len(s) - 4) + s[-4:]
    return _PII_DIGITS_RE.sub(_mask, text)

def check_reply_safety(text: str) -> Dict[str, str]:
    """Check whether a reply is allowed to be sent.

    Returns a dict: {
      'allowed': True|False,
      'reason': str (if blocked),
      'sanitized': str (a safe fallback or sanitized text)
    }
    """
    txt = text or ""

    # Block if reply contains both an instruction verb and a money noun
    if _MONEY_VERB_RE.search(txt) and _MONEY_NOUN_RE.search(txt):
        sanitized = "I'm sorry, I can't assist with requests to transfer money."
        return {"allowed": False, "reason": "financial_instruction", "sanitized": sanitized}

    # Block if reply includes explicit UPI/phone + payment indicator
    if (_UPI_RE.search(txt) or _PHONE_RE.search(txt)) and _PAYMENT_INDICATORS.search(txt):
        sanitized = "I can't accept or share payment identifiers."
        return {"allowed": False, "reason": "identifier_with_payment_instruction", "sanitized": sanitized}

    # Redact long numeric sequences before allowing reply
    if _PII_DIGITS_RE.search(txt):
        return {"allowed": True, "reason": "redacted_digits", "sanitized": sanitize_reply(txt)}

    # otherwise allowed
    return {"allowed": True, "reason": "ok", "sanitized": txt}

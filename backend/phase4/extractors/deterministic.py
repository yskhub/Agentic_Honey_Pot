import re
from typing import Dict, Any, List

# Simple deterministic extractors for common items: phones, upi/ids, urls
PHONE_RE = re.compile(r"\b(\+?\d[\d\-\s]{6,}\d)\b")
UPI_RE = re.compile(r"\b[\w\.\-]{2,}@[\w]{2,}\b")
URL_RE = re.compile(r"https?://[\w\./\-\?=&%#]+")


def extract_phones(text: str) -> List[str]:
    return list({m.group(1).strip() for m in PHONE_RE.finditer(text)})


def extract_upi(text: str) -> List[str]:
    return list({m.group(0).strip() for m in UPI_RE.finditer(text)})


def extract_urls(text: str) -> List[str]:
    return list({m.group(0).strip() for m in URL_RE.finditer(text)})


def extract_all(text: str) -> Dict[str, Any]:
    return {
        "phones": extract_phones(text),
        "upis": extract_upi(text),
        "urls": extract_urls(text),
    }

from typing import Dict, Any, Optional
import json
import logging
import requests

logger = logging.getLogger(__name__)


class Exporter:
    """Base exporter interface.

    Implementations should be idempotent where possible and return a
    tuple `(success: bool, info: Optional[Dict])`.
    """

    def send(self, payload: Dict[str, Any]) -> (bool, Optional[Dict[str, Any]]):
        raise NotImplementedError()


class GuviExporter(Exporter):
    """Simple GUVI exporter stub — performs an HTTP POST to configured endpoint.

    This class intentionally keeps the implementation minimal; the real
    adapter should add retries, idempotency keys, exponential backoff and
    observability hooks.
    """

    def __init__(self, endpoint: str, api_key: Optional[str] = None):
        self.endpoint = endpoint
        self.api_key = api_key

    def send(self, payload: Dict[str, Any]):
        logger.info("GuviExporter.send to %s payload keys=%s", self.endpoint, list(payload.keys()))
        if not self.endpoint:
            # No endpoint configured — behave as a no-op success for testing
            return True, {"note": "no-endpoint-stub"}

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["x-api-key"] = self.api_key

        try:
            resp = requests.post(self.endpoint, json=payload, headers=headers, timeout=8)
            status = getattr(resp, "status_code", None)
            text = None
            try:
                text = resp.text
            except Exception:
                text = None
            if status and 200 <= status < 300:
                return True, {"status": status, "response": text}
            else:
                return False, {"status": status, "response": text}
        except Exception as e:
            logger.exception("Exporter send failed: %s", e)
            return False, {"error": str(e)}

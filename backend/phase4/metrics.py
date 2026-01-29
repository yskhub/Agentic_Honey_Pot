"""Metrics helper for Phase 4. Provides a small wrapper around Prometheus
client if available; otherwise provides no-op implementations so imports
remain safe in environments without the dependency.
"""
from typing import Optional
import logging

logger = logging.getLogger(__name__)

try:
    from prometheus_client import Counter, generate_latest, CollectorRegistry

    registry = CollectorRegistry()
    MESSAGES_TOTAL = Counter("sentinel_messages_total", "Total messages processed", registry=registry)
    OUTGOING_ATTEMPTS = Counter("sentinel_outgoing_attempts_total", "Total outgoing attempts", registry=registry)
    OUTGOING_SUCCESS = Counter("sentinel_outgoing_success_total", "Outgoing successes", registry=registry)
    OUTGOING_FAILURE = Counter("sentinel_outgoing_failure_total", "Outgoing failures", registry=registry)
    DETECTOR_INVOCATIONS = Counter("sentinel_detector_invocations_total", "Detector runs", registry=registry)

    def metrics_payload() -> bytes:
        return generate_latest(registry)

except Exception:  # pragma: no cover - optional dependency
    registry = None
    class _Noop:
        def inc(self, *a, **k):
            return None

    MESSAGES_TOTAL = _Noop()
    OUTGOING_ATTEMPTS = _Noop()
    OUTGOING_SUCCESS = _Noop()
    OUTGOING_FAILURE = _Noop()
    DETECTOR_INVOCATIONS = _Noop()

    def metrics_payload() -> bytes:  # type: ignore[return-value]
        logger.debug("Prometheus client not installed; metrics disabled")
        return b""

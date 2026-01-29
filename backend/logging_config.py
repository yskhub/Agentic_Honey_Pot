import logging
import json
import os
from pathlib import Path


class JsonLineFormatter(logging.Formatter):
    def format(self, record):
        msg = record.getMessage()
        if isinstance(msg, dict):
            return json.dumps(msg, default=str, ensure_ascii=False)
        try:
            return json.dumps({"message": msg, **(record.__dict__.get('extra', {}) or {})}, default=str, ensure_ascii=False)
        except Exception:
            return json.dumps({"message": str(msg)}, ensure_ascii=False)


def setup_logging(log_dir: str = None):
    root = Path(log_dir or os.getenv('LOG_DIR', 'logs'))
    root.mkdir(parents=True, exist_ok=True)

    # Audit logger
    audit_logger = logging.getLogger('sentinel.audit')
    audit_logger.setLevel(logging.INFO)
    ah = logging.FileHandler(str(root / 'audit.jsonl'), encoding='utf-8')
    ah.setFormatter(JsonLineFormatter())
    audit_logger.addHandler(ah)

    # Outgoing HTTP logger
    http_logger = logging.getLogger('sentinel.http')
    http_logger.setLevel(logging.INFO)
    hh = logging.FileHandler(str(root / 'outgoing_http.jsonl'), encoding='utf-8')
    hh.setFormatter(JsonLineFormatter())
    http_logger.addHandler(hh)

    # Default simple console logger
    console = logging.getLogger()
    if not console.handlers:
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))
        console.addHandler(ch)

    return audit_logger, http_logger

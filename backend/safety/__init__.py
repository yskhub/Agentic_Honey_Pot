"""Safety helpers and rules for Phase 4.

Provides simple, deterministic checks to prevent agent replies from including
financial instructions or PII. This module is intentionally small and audit-friendly.
"""

__all__ = ["check_reply_safety", "sanitize_reply"]

"""Deterministic and pluggable extractors for Phase 4.

Expose `extract_all(text)` to return structured extraction results.
"""

from .deterministic import extract_all

__all__ = ["extract_all"]

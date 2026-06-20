"""Stable ID helpers for Trade Inspector modules."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def stable_hash_id(prefix: str, payload: Any, length: int = 12) -> str:
    """Create a stable hash-based ID from JSON-serializable payload."""
    normalized = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=str,
    )
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:length]
    return f"{prefix}{digest}"

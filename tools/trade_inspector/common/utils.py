"""General utility helpers for Trade Inspector modules."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def pick(row: dict[str, Any], *keys: Any, default: Any = "") -> Any:
    """Return the first non-empty value for the given keys.

    Supports both pick(row, "a", "b") and legacy pick(row, ["a", "b"]).
    """
    if len(keys) == 1 and isinstance(keys[0], (list, tuple)):
        keys = tuple(keys[0])

    for key in keys:
        value = row.get(str(key))
        if value is not None and value != "":
            return value
    return default


def to_float(value: Any, default: float = 0.0) -> float:
    """Convert value to float with safe fallback."""
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def to_int(value: Any, default: int = 0) -> int:
    """Convert value to int with safe fallback."""
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def fnum(value: Any, digits: int = 6, default: str = "") -> str:
    """Format numeric values consistently."""
    try:
        if value is None or value == "":
            return default
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return default


def inum(value: Any, default: str = "") -> str:
    """Format integer-like values consistently."""
    try:
        if value is None or value == "":
            return default
        return str(int(float(value)))
    except (TypeError, ValueError):
        return default


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    """Clamp numeric value into inclusive range."""
    return max(low, min(high, value))


def bool_text(value: Any) -> str:
    """Return stable lowercase boolean text."""
    return "true" if bool(value) else "false"


def now_utc() -> str:
    """Return current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

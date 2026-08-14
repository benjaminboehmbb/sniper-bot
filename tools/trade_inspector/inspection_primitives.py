"""Compatibility-preserving primitives for the Trade Inspector façade.

These conversions intentionally retain the historical inspection semantics.
Do not align them with similarly named shared helpers without updating the
characterization gate and explicitly reviewing output compatibility.
"""

from __future__ import annotations

from datetime import datetime, timezone

__all__ = ["safe_text", "safe_float", "safe_int", "parse_ts", "ts_key"]


def safe_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def safe_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def parse_ts(value: object) -> datetime | None:
    s = safe_text(value).replace("_", " ")
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def ts_key(value: object) -> str:
    dt = parse_ts(value)
    if dt is None:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()

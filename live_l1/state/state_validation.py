#!/usr/bin/env python3
# live_l1/state/state_validation.py
# L1-D state validation and fail-safe normalization.
# ASCII-only.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional


_ALLOWED_KILL_LEVELS = {"NONE", "SOFT", "HARD", "EMERGENCY"}


@dataclass(frozen=True)
class StateValidationResult:
    is_valid: bool
    recovery_mode: str
    warnings: List[str]


def _safe_getattr(obj: Any, name: str, default: Any = None) -> Any:
    try:
        return getattr(obj, name, default)
    except Exception:
        return default


def _safe_setattr(obj: Any, name: str, value: Any) -> bool:
    try:
        setattr(obj, name, value)
        return True
    except Exception:
        return False


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_upper(value: Any) -> str:
    return _normalize_text(value).upper()


def _safe_float(value: Any, default: Optional[float] = None) -> Optional[float]:
    try:
        if value is None:
            return default
        s = str(value).strip()
        if s == "":
            return default
        return float(s)
    except Exception:
        return default


def _safe_int(value: Any, default: Optional[int] = None) -> Optional[int]:
    try:
        if value is None:
            return default
        s = str(value).strip()
        if s == "":
            return default
        return int(float(s))
    except Exception:
        return default


def _ensure_attr(obj: Any, name: str, default: Any) -> bool:
    current = _safe_getattr(obj, name, None)
    if current is None:
        return _safe_setattr(obj, name, default)
    return True


def _validate_system_state_id(state: Any, warnings: List[str]) -> bool:
    system_state_id = _normalize_text(_safe_getattr(state, "system_state_id", ""))
    if system_state_id == "":
        warnings.append("missing_system_state_id")
        return False
    return True


def _validate_position_state(state: Any, warnings: List[str]) -> bool:
    s2 = _safe_getattr(state, "s2_position", None)
    if s2 is None:
        warnings.append("missing_s2_position")
        return False

    _ensure_attr(s2, "position", "FLAT")
    _ensure_attr(s2, "entry_price", None)
    _ensure_attr(s2, "entry_timestamp_utc", "")
    _ensure_attr(s2, "position_size", 0.0)
    _ensure_attr(s2, "last_intent_id", "")
    _ensure_attr(s2, "snapshot_id", "")

    position_raw = _normalize_upper(_safe_getattr(s2, "position", "FLAT"))
    entry_price = _safe_float(_safe_getattr(s2, "entry_price", None), None)
    entry_timestamp_utc = _normalize_text(_safe_getattr(s2, "entry_timestamp_utc", ""))
    position_size = _safe_float(_safe_getattr(s2, "position_size", 0.0), 0.0)

    if position_raw in ("", "NONE", "NULL"):
        position_raw = "FLAT"
        _safe_setattr(s2, "position", "FLAT")

    if position_raw not in ("FLAT", "LONG", "SHORT"):
        warnings.append("invalid_position_value")
        _safe_setattr(s2, "position", "FLAT")
        _safe_setattr(s2, "entry_price", None)
        _safe_setattr(s2, "entry_timestamp_utc", "")
        _safe_setattr(s2, "position_size", 0.0)
        return False

    if position_raw == "FLAT":
        _safe_setattr(s2, "position", "FLAT")
        _safe_setattr(s2, "entry_price", None)
        _safe_setattr(s2, "entry_timestamp_utc", "")
        _safe_setattr(s2, "position_size", 0.0)
        return True

    ok = True

    if entry_price is None or entry_price <= 0.0:
        warnings.append("open_position_missing_entry_price")
        ok = False

    if entry_timestamp_utc == "":
        warnings.append("open_position_missing_entry_timestamp")
        ok = False

    if position_size is None or position_size <= 0.0:
        warnings.append("open_position_missing_position_size")
        ok = False

    if not ok:
        _safe_setattr(s2, "position", "FLAT")
        _safe_setattr(s2, "entry_price", None)
        _safe_setattr(s2, "entry_timestamp_utc", "")
        _safe_setattr(s2, "position_size", 0.0)
        return False

    _safe_setattr(s2, "position", position_raw)
    _safe_setattr(s2, "entry_price", float(entry_price))
    _safe_setattr(s2, "entry_timestamp_utc", entry_timestamp_utc)
    _safe_setattr(s2, "position_size", float(position_size))
    return True


def _validate_risk_state(state: Any, warnings: List[str]) -> bool:
    s4 = _safe_getattr(state, "s4_risk", None)
    if s4 is None:
        warnings.append("missing_s4_risk")
        return False

    _ensure_attr(s4, "kill_level", "SOFT")
    _ensure_attr(s4, "trades_6h", 0)
    _ensure_attr(s4, "trades_today", 0)
    _ensure_attr(s4, "last_trade_timestamp_utc", "")

    kill_level = _normalize_upper(_safe_getattr(s4, "kill_level", "SOFT"))
    trades_6h = _safe_int(_safe_getattr(s4, "trades_6h", 0), 0)
    trades_today = _safe_int(_safe_getattr(s4, "trades_today", 0), 0)

    ok = True

    if kill_level not in _ALLOWED_KILL_LEVELS:
        warnings.append("invalid_kill_level")
        kill_level = "SOFT"
        ok = False

    if trades_6h is None or trades_6h < 0:
        warnings.append("invalid_trades_6h")
        trades_6h = 0
        ok = False

    if trades_today is None or trades_today < 0:
        warnings.append("invalid_trades_today")
        trades_today = 0
        ok = False

    _safe_setattr(s4, "kill_level", kill_level)
    _safe_setattr(s4, "trades_6h", int(trades_6h))
    _safe_setattr(s4, "trades_today", int(trades_today))

    return ok


def _validate_snapshot_progress(state: Any, warnings: List[str]) -> bool:
    has_top_snapshot_id = _normalize_text(_safe_getattr(state, "last_snapshot_id", "")) != ""
    has_top_timestamp = _normalize_text(_safe_getattr(state, "last_timestamp_utc", "")) != ""

    if has_top_snapshot_id and has_top_timestamp:
        return True

    s2 = _safe_getattr(state, "s2_position", None)
    if s2 is not None:
        legacy_snapshot_id = _normalize_text(_safe_getattr(s2, "snapshot_id", ""))
        if legacy_snapshot_id != "":
            warnings.append("missing_top_level_snapshot_marker_using_legacy_s2_snapshot_id")
            return True

    warnings.append("missing_snapshot_progress_marker")
    return False


def _apply_fail_safe_defaults(state: Any) -> None:
    s2 = _safe_getattr(state, "s2_position", None)
    if s2 is not None:
        _safe_setattr(s2, "position", "FLAT")
        _safe_setattr(s2, "entry_price", None)
        _safe_setattr(s2, "entry_timestamp_utc", "")
        _safe_setattr(s2, "position_size", 0.0)

    s4 = _safe_getattr(state, "s4_risk", None)
    if s4 is not None:
        _safe_setattr(s4, "kill_level", "SOFT")
        _safe_setattr(s4, "trades_6h", 0)
        _safe_setattr(s4, "trades_today", 0)


def validate_loaded_state(state: Any) -> StateValidationResult:
    """
    Validates a loaded state object and normalizes obviously broken values.

    Returns
    -------
    StateValidationResult
        is_valid       : True if state is acceptable for resume
        recovery_mode  : 'resume' or 'clean_init'
        warnings       : list of validation warnings

    Behavior
    --------
    - Never throws on malformed state
    - Downgrades invalid position/risk data to fail-safe defaults
    - If critical validation fails, returns clean_init recommendation
    """

    warnings: List[str] = []

    if state is None:
        return StateValidationResult(
            is_valid=False,
            recovery_mode="clean_init",
            warnings=["state_is_none"],
        )

    ok_system = _validate_system_state_id(state, warnings)
    ok_position = _validate_position_state(state, warnings)
    ok_risk = _validate_risk_state(state, warnings)
    ok_progress = _validate_snapshot_progress(state, warnings)

    is_valid = bool(ok_system and ok_position and ok_risk and ok_progress)

    if not is_valid:
        _apply_fail_safe_defaults(state)
        return StateValidationResult(
            is_valid=False,
            recovery_mode="clean_init",
            warnings=warnings,
        )

    return StateValidationResult(
        is_valid=True,
        recovery_mode="resume",
        warnings=warnings,
    )
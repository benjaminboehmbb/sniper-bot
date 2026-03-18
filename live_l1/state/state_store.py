#!/usr/bin/env python3
# live_l1/state/state_store.py
# L1 state store with minimal JSONL resume loading for L1-D recovery.
# ASCII-only.

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

from live_l1.state.models import PositionStateS2, RiskStateS4
from live_l1.state.persist import _atomic_append_jsonl


S2Position = PositionStateS2
S4Risk = RiskStateS4


@dataclass
class L1State:
    system_state_id: str
    is_running: bool
    s2_position: S2Position
    s4_risk: S4Risk
    last_snapshot_id: str
    last_timestamp_utc: str
    last_tick_id: int


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


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        s = str(value).strip()
        if s == "":
            return default
        return int(float(s))
    except Exception:
        return default


def _safe_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _read_last_jsonl_record(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        return {}

    last_good: Dict[str, Any] = {}

    with open(path, "r", encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if isinstance(obj, dict):
                last_good = obj

    return last_good


def _build_default_position() -> S2Position:
    s2 = S2Position(
        symbol="BTCUSDT",
        position="FLAT",
        size=0.0,
        entry_price=None,
    )
    setattr(s2, "entry_timestamp_utc", "")
    setattr(s2, "position_size", 0.0)
    setattr(s2, "last_intent_id", "")
    setattr(s2, "snapshot_id", "")
    setattr(s2, "side", "")
    return s2


def _build_default_risk() -> S4Risk:
    s4 = S4Risk(
        kill_level="NONE",
        cooldown_until_utc=None,
    )
    setattr(s4, "trades_6h", 0)
    setattr(s4, "trades_today", 0)
    setattr(s4, "last_trade_timestamp_utc", "")
    return s4


def load_or_init_state(state_dir: str, system_state_id: str) -> L1State:
    os.makedirs(state_dir, exist_ok=True)

    s2_path = os.path.join(state_dir, "s2_position.jsonl")
    s4_path = os.path.join(state_dir, "s4_risk.jsonl")

    s2_last = _read_last_jsonl_record(s2_path)
    s4_last = _read_last_jsonl_record(s4_path)

    s2 = _build_default_position()
    s4 = _build_default_risk()

    loaded_system_state_id = system_state_id

    if s2_last:
        loaded_system_state_id = _safe_text(s2_last.get("system_state_id"), loaded_system_state_id)

        s2.symbol = _safe_text(s2_last.get("symbol"), "BTCUSDT")
        s2.position = _safe_text(s2_last.get("position"), "FLAT").upper()
        s2.size = float(_safe_float(s2_last.get("size"), 0.0) or 0.0)
        s2.entry_price = _safe_float(s2_last.get("entry_price"), None)

        setattr(s2, "entry_timestamp_utc", _safe_text(s2_last.get("entry_timestamp_utc"), ""))
        setattr(s2, "position_size", float(_safe_float(s2_last.get("position_size"), s2.size) or 0.0))
        setattr(s2, "last_intent_id", _safe_text(s2_last.get("last_intent_id"), ""))
        setattr(s2, "snapshot_id", _safe_text(s2_last.get("snapshot_id"), ""))

        loaded_side = _safe_text(s2_last.get("side"), "")
        if loaded_side == "":
            if s2.position == "LONG":
                loaded_side = "long"
            elif s2.position == "SHORT":
                loaded_side = "short"
        setattr(s2, "side", loaded_side)

    if s4_last:
        loaded_system_state_id = _safe_text(s4_last.get("system_state_id"), loaded_system_state_id)

        s4.kill_level = _safe_text(s4_last.get("kill_level"), "NONE").upper()
        s4.cooldown_until_utc = s4_last.get("cooldown_until_utc", None)

        setattr(s4, "trades_6h", _safe_int(s4_last.get("trades_6h"), 0))
        setattr(s4, "trades_today", _safe_int(s4_last.get("trades_today"), 0))
        setattr(s4, "last_trade_timestamp_utc", _safe_text(s4_last.get("last_trade_timestamp_utc"), ""))

    last_snapshot_id = ""
    last_timestamp_utc = ""
    last_tick_id = 0

    if s2_last:
        last_snapshot_id = _safe_text(s2_last.get("last_snapshot_id"), _safe_text(s2_last.get("snapshot_id"), ""))
        last_timestamp_utc = _safe_text(s2_last.get("last_timestamp_utc"), "")
        last_tick_id = _safe_int(s2_last.get("last_tick_id"), 0)

    return L1State(
        system_state_id=loaded_system_state_id,
        is_running=True,
        s2_position=s2,
        s4_risk=s4,
        last_snapshot_id=last_snapshot_id,
        last_timestamp_utc=last_timestamp_utc,
        last_tick_id=last_tick_id,
    )


def persist_state(state_dir: str, state: L1State) -> None:
    os.makedirs(state_dir, exist_ok=True)

    s2_path = os.path.join(state_dir, "s2_position.jsonl")
    s4_path = os.path.join(state_dir, "s4_risk.jsonl")

    s2_position_size = _safe_float(getattr(state.s2_position, "position_size", getattr(state.s2_position, "size", 0.0)), 0.0)
    s2_entry_timestamp_utc = _safe_text(getattr(state.s2_position, "entry_timestamp_utc", ""), "")
    s2_last_intent_id = _safe_text(getattr(state.s2_position, "last_intent_id", ""), "")
    s2_snapshot_id = _safe_text(getattr(state.s2_position, "snapshot_id", ""), "")
    s2_side = _safe_text(getattr(state.s2_position, "side", ""), "")

    s4_trades_6h = _safe_int(getattr(state.s4_risk, "trades_6h", 0), 0)
    s4_trades_today = _safe_int(getattr(state.s4_risk, "trades_today", 0), 0)
    s4_last_trade_timestamp_utc = _safe_text(getattr(state.s4_risk, "last_trade_timestamp_utc", ""), "")

    _atomic_append_jsonl(
        s2_path,
        {
            "system_state_id": state.system_state_id,
            "symbol": state.s2_position.symbol,
            "position": state.s2_position.position,
            "side": s2_side,
            "size": state.s2_position.size,
            "entry_price": state.s2_position.entry_price,
            "entry_timestamp_utc": s2_entry_timestamp_utc,
            "position_size": s2_position_size,
            "last_intent_id": s2_last_intent_id,
            "snapshot_id": s2_snapshot_id,
            "last_snapshot_id": _safe_text(state.last_snapshot_id, ""),
            "last_timestamp_utc": _safe_text(state.last_timestamp_utc, ""),
            "last_tick_id": _safe_int(state.last_tick_id, 0),
        },
    )

    _atomic_append_jsonl(
        s4_path,
        {
            "system_state_id": state.system_state_id,
            "kill_level": state.s4_risk.kill_level,
            "cooldown_until_utc": state.s4_risk.cooldown_until_utc,
            "trades_6h": s4_trades_6h,
            "trades_today": s4_trades_today,
            "last_trade_timestamp_utc": s4_last_trade_timestamp_utc,
        },
    )
#!/usr/bin/env python3
# live_l1/core/execution.py
#
# L1-K paper execution with trade logging on CLOSE.
# - deterministic
# - ASCII-only
# - no real broker/exchange actions
# - state transition logic for paper positions
# - realized trade log written only when a trade is CLOSED
# - duplicate guard on trade_id
# - loss-cluster entry gate
#
# Current scope:
# - FLAT + BUY   -> OPEN_LONG
# - LONG + BUY   -> NOOP
# - SHORT + BUY  -> CLOSE_SHORT (+ trade log)
# - FLAT + SELL  -> OPEN_SHORT
# - SHORT + SELL -> NOOP
# - LONG + SELL  -> CLOSE_LONG (+ trade log)
# - HOLD         -> NOOP
#
# Added:
# - fixed TP/SL exits
# - TP/SL is checked before signal-based exit
# - loss-cluster gate:
#   if 5 of last 10 closed trades are losses, block next 25 entry attempts
#
# Intentionally still not implemented:
# - flip in one step
# - fees deducted from pnl
# - partial close

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal, Optional


IntentFinal = Literal["BUY", "SELL", "HOLD"]


@dataclass(frozen=True)
class ExecutionDecision:
    action: str
    executed: bool
    position_before: str
    position_after: str
    side_after: str
    entry_price: Optional[float]
    entry_timestamp_utc: str
    reason: str


LOSS_CLUSTER_LOOKBACK = 10
LOSS_CLUSTER_MIN_LOSSES = 5
LOSS_CLUSTER_PAUSE_ENTRIES = 35


@dataclass
class _LossClusterGateState:
    recent_closed_trade_pnls: list[float] = field(default_factory=list)
    pause_entries_remaining: int = 0


_LOSS_GATE_STATE = _LossClusterGateState()


def _loss_gate_register_closed_trade(pnl: float) -> None:
    _LOSS_GATE_STATE.recent_closed_trade_pnls.append(float(pnl))

    if len(_LOSS_GATE_STATE.recent_closed_trade_pnls) > LOSS_CLUSTER_LOOKBACK:
        _LOSS_GATE_STATE.recent_closed_trade_pnls.pop(0)

    losses = sum(1 for x in _LOSS_GATE_STATE.recent_closed_trade_pnls if float(x) < 0.0)

    if (
        len(_LOSS_GATE_STATE.recent_closed_trade_pnls) >= LOSS_CLUSTER_LOOKBACK
        and losses >= LOSS_CLUSTER_MIN_LOSSES
    ):
        _LOSS_GATE_STATE.pause_entries_remaining = LOSS_CLUSTER_PAUSE_ENTRIES
        _LOSS_GATE_STATE.recent_closed_trade_pnls = []


def _loss_gate_allows_entry() -> bool:
    if _LOSS_GATE_STATE.pause_entries_remaining > 0:
        _LOSS_GATE_STATE.pause_entries_remaining -= 1
        return False
    return True


def _norm_position(value: object) -> str:
    s = "" if value is None else str(value).strip().upper()
    if s in ("LONG", "SHORT", "FLAT"):
        return s
    return "FLAT"


def _safe_float(value: object, default: float = 0.0) -> float:
    if value is None:
        return default
    s = str(value).strip()
    if s == "":
        return default
    try:
        return float(s)
    except Exception:
        return default


def _safe_optional_float(value: object) -> Optional[float]:
    if value is None:
        return None
    s = str(value).strip()
    if s == "":
        return None
    try:
        return float(s)
    except Exception:
        return None


def _safe_text(value: object, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _ensure_position_attrs(state) -> None:
    if not hasattr(state, "s2_position"):
        raise AttributeError("state.s2_position missing")

    if not hasattr(state.s2_position, "position"):
        state.s2_position.position = "FLAT"

    if not hasattr(state.s2_position, "size"):
        state.s2_position.size = 0.0

    if not hasattr(state.s2_position, "entry_price"):
        state.s2_position.entry_price = None

    if not hasattr(state.s2_position, "entry_timestamp_utc"):
        state.s2_position.entry_timestamp_utc = ""

    if not hasattr(state.s2_position, "position_size"):
        state.s2_position.position_size = float(getattr(state.s2_position, "size", 0.0) or 0.0)

    if not hasattr(state.s2_position, "side"):
        state.s2_position.side = ""


def _reset_to_flat(state) -> None:
    state.s2_position.position = "FLAT"
    state.s2_position.side = ""
    state.s2_position.size = 0.0
    state.s2_position.position_size = 0.0
    state.s2_position.entry_price = None
    state.s2_position.entry_timestamp_utc = ""


def _resolve_trade_log_path(trade_log_path: Optional[str]) -> str:
    if trade_log_path is not None and str(trade_log_path).strip() != "":
        return str(trade_log_path).strip()

    env_path = os.environ.get("L1_TRADE_LOG_PATH", "").strip()
    if env_path != "":
        return env_path

    return "live_logs/trades_l1.jsonl"


def _ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent != "":
        os.makedirs(parent, exist_ok=True)


def _append_jsonl(path: str, payload: dict) -> None:
    _ensure_parent_dir(path)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=True, sort_keys=True) + "\n")


def _trade_id_exists(path: str, trade_id: str) -> bool:
    if not os.path.isfile(path):
        return False

    target = _safe_text(trade_id, "")
    if target == "":
        return False

    try:
        with open(path, "r", encoding="utf-8") as fh:
            for raw_line in fh:
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if not isinstance(obj, dict):
                    continue
                existing_trade_id = _safe_text(obj.get("trade_id"), "")
                if existing_trade_id == target:
                    return True
    except Exception:
        return False

    return False


def _parse_timestamp_utc(ts: str) -> Optional[datetime]:
    s = _safe_text(ts, "")
    if s == "":
        return None

    normalized = s.replace("_", " ")

    try:
        if normalized.endswith("Z"):
            return datetime.fromisoformat(normalized[:-1] + "+00:00")
        dt = datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def _compute_duration_sec(entry_timestamp_utc: str, exit_timestamp_utc: str) -> float:
    dt_entry = _parse_timestamp_utc(entry_timestamp_utc)
    dt_exit = _parse_timestamp_utc(exit_timestamp_utc)

    if dt_entry is None or dt_exit is None:
        return 0.0

    duration = (dt_exit - dt_entry).total_seconds()
    if duration < 0:
        return 0.0
    return float(duration)


def _compute_pnl(side: str, entry_price: float, exit_price: float, size: float) -> float:
    if side == "long":
        return (exit_price - entry_price) * size
    if side == "short":
        return (entry_price - exit_price) * size
    return 0.0


def _compute_pnl_pct(pnl: float, entry_price: float, size: float) -> float:
    denom = entry_price * size
    if denom <= 0.0:
        return 0.0
    return pnl / denom


def _build_trade_id(system_state_id: str, entry_timestamp_utc: str) -> str:
    sid = _safe_text(system_state_id, "UNKNOWN_SYSTEM")
    ets = _safe_text(entry_timestamp_utc, "UNKNOWN_ENTRY_TS")
    return sid + "_" + ets


def _log_closed_trade(
    *,
    state,
    side: str,
    entry_price: float,
    exit_price: float,
    entry_timestamp_utc: str,
    exit_timestamp_utc: str,
    size: float,
    fee_roundtrip: float,
    exit_reason: str,
    trade_log_path: Optional[str],
) -> None:
    system_state_id = _safe_text(getattr(state, "system_state_id", ""), "")
    trade_id = _build_trade_id(system_state_id, entry_timestamp_utc)
    duration_sec = _compute_duration_sec(entry_timestamp_utc, exit_timestamp_utc)
    pnl = _compute_pnl(side, entry_price, exit_price, size)
    pnl_pct = _compute_pnl_pct(pnl, entry_price, size)

    payload = {
        "system_state_id": system_state_id,
        "trade_id": trade_id,
        "side": side,
        "entry_price": float(entry_price),
        "exit_price": float(exit_price),
        "entry_timestamp_utc": _safe_text(entry_timestamp_utc, ""),
        "exit_timestamp_utc": _safe_text(exit_timestamp_utc, ""),
        "duration_sec": float(duration_sec),
        "size": float(size),
        "pnl": float(pnl),
        "pnl_pct": float(pnl_pct),
        "fee_roundtrip": float(fee_roundtrip),
        "exit_reason": _safe_text(exit_reason, ""),
    }

    path = _resolve_trade_log_path(trade_log_path)

    if _trade_id_exists(path, trade_id):
        return

    _append_jsonl(path, payload)
    _loss_gate_register_closed_trade(float(pnl))


def _capture_open_position_snapshot(state) -> dict:
    return {
        "position": _norm_position(getattr(state.s2_position, "position", "FLAT")),
        "side": _safe_text(getattr(state.s2_position, "side", ""), ""),
        "entry_price": _safe_optional_float(getattr(state.s2_position, "entry_price", None)),
        "entry_timestamp_utc": _safe_text(getattr(state.s2_position, "entry_timestamp_utc", ""), ""),
        "size": _safe_float(
            getattr(
                state.s2_position,
                "position_size",
                getattr(state.s2_position, "size", 0.0),
            ),
            0.0,
        ),
    }


def _valid_trade_snapshot(snapshot: dict) -> bool:
    return bool(
        snapshot.get("position") in ("LONG", "SHORT")
        and snapshot.get("side") in ("long", "short")
        and snapshot.get("entry_price") is not None
        and float(snapshot.get("entry_price")) > 0.0
        and float(snapshot.get("size", 0.0)) > 0.0
        and _safe_text(snapshot.get("entry_timestamp_utc", ""), "") != ""
    )


def _blocked_entry_decision(pos_before: str, side_after: str, entry_price, entry_timestamp_utc: str) -> ExecutionDecision:
    return ExecutionDecision(
        action="NOOP",
        executed=False,
        position_before=pos_before,
        position_after=pos_before,
        side_after=side_after,
        entry_price=entry_price,
        entry_timestamp_utc=entry_timestamp_utc,
        reason="LOSS_CLUSTER_GATE_BLOCKED_ENTRY",
    )


def apply_paper_execution(
    *,
    state,
    intent_final: IntentFinal,
    price: float,
    timestamp_utc: str,
    position_size: float = 1.0,
    fee_roundtrip: float = 0.0,
    trade_log_path: Optional[str] = None,
) -> ExecutionDecision:
    """
    L1-K paper execution state transition with trade logging on CLOSE.
    """

    _ensure_position_attrs(state)

    pos_before = _norm_position(getattr(state.s2_position, "position", "FLAT"))
    px = _safe_float(price, 0.0)
    ts = _safe_text(timestamp_utc, "")
    size_new = _safe_float(position_size, 1.0)

    if size_new <= 0.0:
        size_new = 1.0

    tp_pct = 0.05
    sl_pct = 0.015

    entry_price_current = _safe_optional_float(getattr(state.s2_position, "entry_price", None))

    if pos_before == "LONG" and entry_price_current is not None and entry_price_current > 0.0:
        tp_price_long = entry_price_current * (1.0 + tp_pct)
        sl_price_long = entry_price_current * (1.0 - sl_pct)

        if px >= tp_price_long or px <= sl_price_long:
            trade_snapshot = _capture_open_position_snapshot(state)

            if _valid_trade_snapshot(trade_snapshot):
                _log_closed_trade(
                    state=state,
                    side="long",
                    entry_price=float(trade_snapshot["entry_price"]),
                    exit_price=float(px),
                    entry_timestamp_utc=_safe_text(trade_snapshot["entry_timestamp_utc"], ""),
                    exit_timestamp_utc=ts,
                    size=float(trade_snapshot["size"]),
                    fee_roundtrip=float(fee_roundtrip),
                    exit_reason="TP_LONG" if px >= tp_price_long else "SL_LONG",
                    trade_log_path=trade_log_path,
                )

            _reset_to_flat(state)

            return ExecutionDecision(
                action="CLOSE_LONG",
                executed=True,
                position_before="LONG",
                position_after="FLAT",
                side_after="",
                entry_price=None,
                entry_timestamp_utc="",
                reason="TP_LONG_HIT" if px >= tp_price_long else "SL_LONG_HIT",
            )

    if pos_before == "SHORT" and entry_price_current is not None and entry_price_current > 0.0:
        tp_price_short = entry_price_current * (1.0 - tp_pct)
        sl_price_short = entry_price_current * (1.0 + sl_pct)

        if px <= tp_price_short or px >= sl_price_short:
            trade_snapshot = _capture_open_position_snapshot(state)

            if _valid_trade_snapshot(trade_snapshot):
                _log_closed_trade(
                    state=state,
                    side="short",
                    entry_price=float(trade_snapshot["entry_price"]),
                    exit_price=float(px),
                    entry_timestamp_utc=_safe_text(trade_snapshot["entry_timestamp_utc"], ""),
                    exit_timestamp_utc=ts,
                    size=float(trade_snapshot["size"]),
                    fee_roundtrip=float(fee_roundtrip),
                    exit_reason="TP_SHORT" if px <= tp_price_short else "SL_SHORT",
                    trade_log_path=trade_log_path,
                )

            _reset_to_flat(state)

            return ExecutionDecision(
                action="CLOSE_SHORT",
                executed=True,
                position_before="SHORT",
                position_after="FLAT",
                side_after="",
                entry_price=None,
                entry_timestamp_utc="",
                reason="TP_SHORT_HIT" if px <= tp_price_short else "SL_SHORT_HIT",
            )

    if intent_final == "HOLD":
        return ExecutionDecision(
            action="NOOP",
            executed=False,
            position_before=pos_before,
            position_after=pos_before,
            side_after=_safe_text(getattr(state.s2_position, "side", ""), ""),
            entry_price=getattr(state.s2_position, "entry_price", None),
            entry_timestamp_utc=_safe_text(getattr(state.s2_position, "entry_timestamp_utc", ""), ""),
            reason="HOLD_NO_EXECUTION",
        )

    if intent_final == "BUY":
        if pos_before == "FLAT":
            if not _loss_gate_allows_entry():
                return _blocked_entry_decision(
                    pos_before="FLAT",
                    side_after="",
                    entry_price=None,
                    entry_timestamp_utc="",
                )

            state.s2_position.position = "LONG"
            state.s2_position.side = "long"
            state.s2_position.size = float(size_new)
            state.s2_position.position_size = float(size_new)
            state.s2_position.entry_price = float(px)
            state.s2_position.entry_timestamp_utc = ts

            return ExecutionDecision(
                action="OPEN_LONG",
                executed=True,
                position_before="FLAT",
                position_after="LONG",
                side_after="long",
                entry_price=float(px),
                entry_timestamp_utc=ts,
                reason="BUY_FROM_FLAT",
            )

        if pos_before == "LONG":
            return ExecutionDecision(
                action="NOOP",
                executed=False,
                position_before="LONG",
                position_after="LONG",
                side_after="long",
                entry_price=getattr(state.s2_position, "entry_price", None),
                entry_timestamp_utc=_safe_text(getattr(state.s2_position, "entry_timestamp_utc", ""), ""),
                reason="BUY_ALREADY_LONG",
            )

        if pos_before == "SHORT":
            trade_snapshot = _capture_open_position_snapshot(state)

            if _valid_trade_snapshot(trade_snapshot):
                _log_closed_trade(
                    state=state,
                    side="short",
                    entry_price=float(trade_snapshot["entry_price"]),
                    exit_price=float(px),
                    entry_timestamp_utc=_safe_text(trade_snapshot["entry_timestamp_utc"], ""),
                    exit_timestamp_utc=ts,
                    size=float(trade_snapshot["size"]),
                    fee_roundtrip=float(fee_roundtrip),
                    exit_reason="CLOSE_SHORT",
                    trade_log_path=trade_log_path,
                )

            _reset_to_flat(state)

            return ExecutionDecision(
                action="CLOSE_SHORT",
                executed=True,
                position_before="SHORT",
                position_after="FLAT",
                side_after="",
                entry_price=None,
                entry_timestamp_utc="",
                reason="BUY_CLOSES_SHORT",
            )

    if intent_final == "SELL":
        if pos_before == "FLAT":
            if not _loss_gate_allows_entry():
                return _blocked_entry_decision(
                    pos_before="FLAT",
                    side_after="",
                    entry_price=None,
                    entry_timestamp_utc="",
                )

            state.s2_position.position = "SHORT"
            state.s2_position.side = "short"
            state.s2_position.size = float(size_new)
            state.s2_position.position_size = float(size_new)
            state.s2_position.entry_price = float(px)
            state.s2_position.entry_timestamp_utc = ts

            return ExecutionDecision(
                action="OPEN_SHORT",
                executed=True,
                position_before="FLAT",
                position_after="SHORT",
                side_after="short",
                entry_price=float(px),
                entry_timestamp_utc=ts,
                reason="SELL_FROM_FLAT",
            )

        if pos_before == "SHORT":
            return ExecutionDecision(
                action="NOOP",
                executed=False,
                position_before="SHORT",
                position_after="SHORT",
                side_after="short",
                entry_price=getattr(state.s2_position, "entry_price", None),
                entry_timestamp_utc=_safe_text(getattr(state.s2_position, "entry_timestamp_utc", ""), ""),
                reason="SELL_ALREADY_SHORT",
            )

        if pos_before == "LONG":
            trade_snapshot = _capture_open_position_snapshot(state)

            if _valid_trade_snapshot(trade_snapshot):
                _log_closed_trade(
                    state=state,
                    side="long",
                    entry_price=float(trade_snapshot["entry_price"]),
                    exit_price=float(px),
                    entry_timestamp_utc=_safe_text(trade_snapshot["entry_timestamp_utc"], ""),
                    exit_timestamp_utc=ts,
                    size=float(trade_snapshot["size"]),
                    fee_roundtrip=float(fee_roundtrip),
                    exit_reason="CLOSE_LONG",
                    trade_log_path=trade_log_path,
                )

            _reset_to_flat(state)

            return ExecutionDecision(
                action="CLOSE_LONG",
                executed=True,
                position_before="LONG",
                position_after="FLAT",
                side_after="",
                entry_price=None,
                entry_timestamp_utc="",
                reason="SELL_CLOSES_LONG",
            )

    return ExecutionDecision(
        action="NOOP",
        executed=False,
        position_before=pos_before,
        position_after=pos_before,
        side_after=_safe_text(getattr(state.s2_position, "side", ""), ""),
        entry_price=getattr(state.s2_position, "entry_price", None),
        entry_timestamp_utc=_safe_text(getattr(state.s2_position, "entry_timestamp_utc", ""), ""),
        reason="UNKNOWN_INTENT",
    )

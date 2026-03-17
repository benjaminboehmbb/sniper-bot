#!/usr/bin/env python3
# live_l1/core/execution.py
#
# Minimal paper execution for L1-F.
# - deterministic
# - ASCII-only
# - no real broker/exchange actions
# - only state transition logic for paper positions
#
# Current scope:
# - FLAT + BUY  -> open LONG
# - LONG + BUY  -> no action
# - FLAT + SELL -> open SHORT
# - SHORT + SELL -> no action
# - HOLD -> no action
#
# Exit / flip / PnL logic is intentionally not implemented yet.

from __future__ import annotations

from dataclasses import dataclass
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


def _safe_text(value: object, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _ensure_position_attrs(state) -> None:
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


def apply_paper_execution(
    *,
    state,
    intent_final: IntentFinal,
    price: float,
    timestamp_utc: str,
    position_size: float = 1.0,
) -> ExecutionDecision:
    """
    Minimal paper execution state transition.

    Parameters
    ----------
    state : loaded L1 state
    intent_final : BUY / SELL / HOLD
    price : current market price
    timestamp_utc : timestamp of current snapshot
    position_size : paper position size for new entries

    Returns
    -------
    ExecutionDecision
    """

    _ensure_position_attrs(state)

    pos_before = _norm_position(getattr(state.s2_position, "position", "FLAT"))
    px = _safe_float(price, 0.0)
    ts = _safe_text(timestamp_utc, "")
    size = _safe_float(position_size, 1.0)

    if size <= 0.0:
        size = 1.0

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
            state.s2_position.position = "LONG"
            state.s2_position.side = "long"
            state.s2_position.size = float(size)
            state.s2_position.position_size = float(size)
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
            return ExecutionDecision(
                action="NOOP",
                executed=False,
                position_before="SHORT",
                position_after="SHORT",
                side_after="short",
                entry_price=getattr(state.s2_position, "entry_price", None),
                entry_timestamp_utc=_safe_text(getattr(state.s2_position, "entry_timestamp_utc", ""), ""),
                reason="BUY_WHILE_SHORT_NOT_SUPPORTED_YET",
            )

    if intent_final == "SELL":
        if pos_before == "FLAT":
            state.s2_position.position = "SHORT"
            state.s2_position.side = "short"
            state.s2_position.size = float(size)
            state.s2_position.position_size = float(size)
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
            return ExecutionDecision(
                action="NOOP",
                executed=False,
                position_before="LONG",
                position_after="LONG",
                side_after="long",
                entry_price=getattr(state.s2_position, "entry_price", None),
                entry_timestamp_utc=_safe_text(getattr(state.s2_position, "entry_timestamp_utc", ""), ""),
                reason="SELL_WHILE_LONG_NOT_SUPPORTED_YET",
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

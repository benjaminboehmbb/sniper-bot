#!/usr/bin/env python3
# live_l1/core/intent.py
# Deterministic 1m intent logic for L1 paper loop.
# ASCII-only.

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Literal, Tuple

from live_l1.core.feature_snapshot import FeatureSnapshot


IntentAction = Literal["BUY", "SELL", "HOLD"]
Position = Literal["FLAT", "LONG", "SHORT"]

ENTRY_COOLDOWN_NORMAL_TICKS = 120
ENTRY_COOLDOWN_BAD_ATR_TICKS = 200


@dataclass(frozen=True)
class Intent:
    action: IntentAction


@dataclass
class _IntentState:
    recent_scores: list[int] = field(default_factory=list)
    last_tick_id: int | None = None
    last_position: Position = "FLAT"
    last_flat_after_position_tick: int | None = None


_STATE = _IntentState()


def make_hold_intent() -> Intent:
    return Intent(action="HOLD")


def reset_intent_state() -> None:
    _STATE.recent_scores = []
    _STATE.last_tick_id = None
    _STATE.last_position = "FLAT"
    _STATE.last_flat_after_position_tick = None


def _load_l1_signal_weights() -> dict[str, float] | None:
    path = os.environ.get("L1_SIGNAL_WEIGHTS_JSON", "").strip()
    if path == "":
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)
        if not isinstance(obj, dict):
            return None
        out: dict[str, float] = {}
        for k, v in obj.items():
            try:
                out[str(k)] = float(v)
            except Exception:
                continue
        return out if out else None
    except Exception:
        return None


def _normalize_score(features: FeatureSnapshot) -> int:
    try:
        weights = _load_l1_signal_weights()
        if weights:
            return int(round(features.weighted_signal_score(weights)))
        return int(
            features.signal("rsi_signal")
            + features.signal("bollinger_signal")
            + features.signal("stoch_signal")
            + features.signal("cci_signal")
        )
    except Exception:
        return 0


def _normalize_position(value: object) -> Position:
    s = "" if value is None else str(value).strip().upper()
    if s == "LONG":
        return "LONG"
    if s == "SHORT":
        return "SHORT"
    return "FLAT"


def _maybe_reset_on_tick_reset(tick_id: int) -> None:
    last_tick = _STATE.last_tick_id
    if last_tick is None:
        return
    if tick_id <= last_tick:
        reset_intent_state()


def _push_score(score: int) -> None:
    _STATE.recent_scores.append(int(score))
    if len(_STATE.recent_scores) > 6:
        _STATE.recent_scores.pop(0)


def _last_n_all_ge(n: int, threshold: int) -> bool:
    if len(_STATE.recent_scores) < n:
        return False
    return all(s >= threshold for s in _STATE.recent_scores[-n:])


def _last_n_all_le(n: int, threshold: int) -> bool:
    if len(_STATE.recent_scores) < n:
        return False
    return all(s <= threshold for s in _STATE.recent_scores[-n:])


def _entry_cooldown_ticks(atr_sig: int) -> int:
    if int(atr_sig) == -1:
        return ENTRY_COOLDOWN_BAD_ATR_TICKS
    return ENTRY_COOLDOWN_NORMAL_TICKS


def _in_entry_cooldown(tick_id: int, atr_sig: int) -> bool:
    last = _STATE.last_flat_after_position_tick
    if last is None:
        return False
    cooldown = _entry_cooldown_ticks(atr_sig)
    return (int(tick_id) - int(last)) < int(cooldown)


def _update_position_transition(pos: Position, tick_id: int) -> None:
    prev = _STATE.last_position
    if prev in ("LONG", "SHORT") and pos == "FLAT":
        _STATE.last_flat_after_position_tick = int(tick_id)
    _STATE.last_position = pos


def _debug_enabled() -> bool:
    v = os.environ.get("L1_INTENT_DEBUG", "")
    return v.strip().lower() in ("1", "true", "yes", "on")


def _debug_log_line(
    *,
    tick_id: int,
    current_position: Position,
    score: int,
    intent: IntentAction,
    forced: bool,
    atr_sig: int = 0,
) -> None:
    if not _debug_enabled():
        return

    try:
        log_dir = os.path.join(os.getcwd(), "live_logs")
        os.makedirs(log_dir, exist_ok=True)
        path = os.path.join(log_dir, "intent_debug.log")
        with open(path, "a", encoding="utf-8") as f:
            f.write(
                "tick={tick} pos={pos} score={score} recent={recent} intent={intent} forced={forced} cooldown={cooldown} cooldown_ticks={cooldown_ticks} cooldown_last={cooldown_last} atr_sig={atr_sig}\n".format(
                    tick=tick_id,
                    pos=current_position,
                    score=score,
                    recent=list(_STATE.recent_scores),
                    intent=intent,
                    forced=int(forced),
                    cooldown=int(_in_entry_cooldown(tick_id, atr_sig)),
                    cooldown_ticks=_entry_cooldown_ticks(atr_sig),
                    cooldown_last=_STATE.last_flat_after_position_tick,
                    atr_sig=int(atr_sig),
                )
            )
    except Exception:
        pass


def compute_1m_intent_raw(
    *,
    cfg,
    tick_id: int,
    features: FeatureSnapshot,
    current_position: str = "FLAT",
) -> Tuple[IntentAction, bool]:
    tick_id = int(tick_id)
    _maybe_reset_on_tick_reset(tick_id)

    warmup = int(getattr(cfg, "test_force_warmup_ticks", 0))
    if tick_id <= warmup:
        _STATE.last_tick_id = tick_id
        _STATE.recent_scores = []
        _STATE.last_position = "FLAT"
        _STATE.last_flat_after_position_tick = None
        _debug_log_line(
            tick_id=tick_id,
            current_position="FLAT",
            score=0,
            intent="HOLD",
            forced=False,
            atr_sig=0,
        )
        return ("HOLD", False)

    force_enabled = bool(getattr(cfg, "test_force_intents", False))
    if force_enabled:
        sell_every = int(getattr(cfg, "test_force_sell_every", 0))
        buy_every = int(getattr(cfg, "test_force_buy_every", 0))

        _STATE.last_tick_id = tick_id
        _STATE.recent_scores = []

        if sell_every > 0 and tick_id % sell_every == 0:
            _debug_log_line(
                tick_id=tick_id,
                current_position=_normalize_position(current_position),
                score=0,
                intent="SELL",
                forced=True,
                atr_sig=0,
            )
            return ("SELL", True)

        if buy_every > 0 and tick_id % buy_every == 0:
            _debug_log_line(
                tick_id=tick_id,
                current_position=_normalize_position(current_position),
                score=0,
                intent="BUY",
                forced=True,
                atr_sig=0,
            )
            return ("BUY", True)

        _debug_log_line(
            tick_id=tick_id,
            current_position=_normalize_position(current_position),
            score=0,
            intent="HOLD",
            forced=True,
            atr_sig=0,
        )
        return ("HOLD", False)

    score = _normalize_score(features)
    pos = _normalize_position(current_position)

    _push_score(score)
    _update_position_transition(pos, tick_id)

    intent: IntentAction = "HOLD"
    atr_sig = int(features.signal("atr_signal"))

    if pos == "FLAT":
        ma200_sig = int(features.signal("ma200_signal"))
        mfi_sig = int(features.signal("mfi_signal"))

        if not _in_entry_cooldown(tick_id, atr_sig):
            if ma200_sig == 1 and mfi_sig == 1:
                if atr_sig == -1:
                    if _last_n_all_ge(3, 4):
                        intent = "BUY"
                else:
                    if _last_n_all_ge(3, 3):
                        intent = "BUY"

            elif ma200_sig == -1 and mfi_sig == -1:
                if atr_sig == -1:
                    if _last_n_all_le(3, -4):
                        intent = "SELL"
                else:
                    if _last_n_all_le(3, -3):
                        intent = "SELL"

    elif pos == "LONG":
        if _last_n_all_le(1, -1):
            intent = "SELL"

    elif pos == "SHORT":
        if _last_n_all_ge(2, 2):
            intent = "BUY"

    _STATE.last_tick_id = tick_id

    _debug_log_line(
        tick_id=tick_id,
        current_position=pos,
        score=score,
        intent=intent,
        forced=False,
        atr_sig=atr_sig,
    )

    return (intent, False)
#!/usr/bin/env python3
# live_l1/core/intent.py
# Deterministic 1m intent logic for L1 paper loop.
# ASCII-only.

from __future__ import annotations

import os
import json
from dataclasses import dataclass, field
from typing import Literal, Tuple

from live_l1.core.feature_snapshot import FeatureSnapshot


IntentAction = Literal["BUY", "SELL", "HOLD"]
Position = Literal["FLAT", "LONG", "SHORT"]


@dataclass(frozen=True)
class Intent:
    action: IntentAction


@dataclass
class _IntentState:
    recent_scores: list[int] = field(default_factory=list)
    last_tick_id: int | None = None


_STATE = _IntentState()


def make_hold_intent() -> Intent:
    return Intent(action="HOLD")


def reset_intent_state() -> None:
    _STATE.recent_scores = []
    _STATE.last_tick_id = None


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
) -> None:
    if not _debug_enabled():
        return

    try:
        log_dir = os.path.join(os.getcwd(), "live_logs")
        os.makedirs(log_dir, exist_ok=True)
        path = os.path.join(log_dir, "intent_debug.log")
        with open(path, "a", encoding="utf-8") as f:
            f.write(
                "tick={tick} pos={pos} score={score} recent={recent} intent={intent} forced={forced}\n".format(
                    tick=tick_id,
                    pos=current_position,
                    score=score,
                    recent=list(_STATE.recent_scores),
                    intent=intent,
                    forced=int(forced),
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
        _debug_log_line(
            tick_id=tick_id,
            current_position="FLAT",
            score=0,
            intent="HOLD",
            forced=False,
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
            )
            return ("SELL", True)

        if buy_every > 0 and tick_id % buy_every == 0:
            _debug_log_line(
                tick_id=tick_id,
                current_position=_normalize_position(current_position),
                score=0,
                intent="BUY",
                forced=True,
            )
            return ("BUY", True)

        _debug_log_line(
            tick_id=tick_id,
            current_position=_normalize_position(current_position),
            score=0,
            intent="HOLD",
            forced=True,
        )
        return ("HOLD", False)

    score = _normalize_score(features)
    pos = _normalize_position(current_position)

    _push_score(score)

    intent: IntentAction = "HOLD"

    if pos == "FLAT":
        ma200_sig = int(features.signal("ma200_signal"))
        mfi_sig = int(features.signal("mfi_signal"))
        adx_sig = int(features.signal("adx_signal"))

        if (
            ma200_sig == 1
            and mfi_sig == 1
            and adx_sig == 1
            and _last_n_all_ge(2, 3)
        ):
            intent = "BUY"
        elif (
            ma200_sig == -1
            and mfi_sig == -1
            and adx_sig == -1
            and _last_n_all_le(2, -3)
        ):
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
    )

    return (intent, False)
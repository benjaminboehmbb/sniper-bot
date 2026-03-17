#!/usr/bin/env python3
# live_l1/guards/guards.py
#
# L1 Guards & Kill-Switches (Step 4/8)
# - deterministisch
# - monotoner Kill-Level (NONE -> SOFT -> HARD -> EMERGENCY)
# - blockiert Intent, erzeugt L4 Logs (macht der Loop)
#
# ASCII-only.

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from live_l1.core.intent import Intent


# Monotone Kill-Level Reihenfolge
_LEVELS = ["NONE", "SOFT", "HARD", "EMERGENCY"]
_LEVEL_RANK = {k: i for i, k in enumerate(_LEVELS)}


def _max_level(a: str, b: str) -> str:
    ra = _LEVEL_RANK.get(a, 0)
    rb = _LEVEL_RANK.get(b, 0)
    return a if ra >= rb else b


@dataclass(frozen=True)
class GuardDecision:
    allowed: bool
    kill_level_new: str
    reasons: List[str]


def apply_guards(
    *,
    kill_level_current: str,
    data_valid: bool,
    intent: Optional[Intent],
) -> GuardDecision:
    reasons: List[str] = []
    kill_new = kill_level_current if kill_level_current in _LEVEL_RANK else "NONE"

    # Guard 1: data_valid muss true sein, sonst blockieren (SOFT)
    if not data_valid:
        reasons.append("guard_data_invalid")
        kill_new = _max_level(kill_new, "SOFT")

    # Guard 2: Intent muss existieren
    if intent is None:
        reasons.append("guard_intent_missing")
        return GuardDecision(allowed=False, kill_level_new=kill_new, reasons=reasons)

    # Guard 3: Kill-Level HARD/EMERGENCY blockiert alles
    if kill_new in ("HARD", "EMERGENCY"):
        reasons.append(f"guard_kill_level_block:{kill_new}")
        return GuardDecision(allowed=False, kill_level_new=kill_new, reasons=reasons)

    # Guard 4: In diesem Build erlauben wir NUR HOLD
    if intent.action != "HOLD":
        reasons.append(f"guard_action_not_allowed:{intent.action}")
        kill_new = _max_level(kill_new, "HARD")
        return GuardDecision(allowed=False, kill_level_new=kill_new, reasons=reasons)

    return GuardDecision(allowed=True, kill_level_new=kill_new, reasons=reasons)


def evaluate_guards(*, cfg, state):
    """
    Wrapper expected by live_l1/core/loop.py

    Returns
    -------
    guard_reason : str
    kill_level   : str
    """

    gate_mode = str(getattr(cfg, "gate_mode", "auto")).strip().lower()

    current_kill = "NONE"
    if hasattr(state, "s4_risk") and hasattr(state.s4_risk, "kill_level"):
        current_kill = str(state.s4_risk.kill_level).strip().upper()
        if current_kill not in _LEVEL_RANK:
            current_kill = "NONE"

    if gate_mode == "closed":
        return ("guard_gate_closed", _max_level(current_kill, "HARD"))

    if gate_mode in ("auto", "open"):
        return ("guard_ok", current_kill)

    return ("guard_invalid_gate_mode", _max_level(current_kill, "SOFT"))
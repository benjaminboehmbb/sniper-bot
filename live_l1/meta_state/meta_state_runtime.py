from __future__ import annotations

from live_l1.meta_state.meta_state_shadow import build_meta_state_shadow


META_STATE_ENABLED = False


def resolve_position_multiplier(current_score: int) -> tuple[float, dict]:
    shadow = build_meta_state_shadow(current_score)

    multiplier = 1.0

    if META_STATE_ENABLED:
        multiplier = float(shadow["position_multiplier"])

    return multiplier, shadow

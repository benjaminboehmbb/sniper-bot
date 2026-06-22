from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from tools.ssi.builder.lifecycle_snapshot import LifecycleSnapshot
from tools.ssi.common.normalization import clamp, normalize_abs_penalty


@dataclass(frozen=True)
class StabilityResult:
    value: float
    raw: float
    components: Dict[str, Any]


def calculate_stability(
    snapshot: LifecycleSnapshot,
    *,
    entry_snapshot: Optional[LifecycleSnapshot] = None,
    score_delta_scale: float = 4.0,
) -> StabilityResult:
    if score_delta_scale <= 0:
        raise ValueError("score_delta_scale must be > 0")

    if entry_snapshot is None:
        regime_changed = False
        score_delta = 0.0
    else:
        regime_changed = (
            snapshot.market_regime.strip().lower()
            != entry_snapshot.market_regime.strip().lower()
        )
        score_delta = snapshot.current_score - entry_snapshot.current_score

    score_stability = normalize_abs_penalty(score_delta, max_abs=score_delta_scale)
    regime_stability = 0.0 if regime_changed else 1.0

    raw = (0.65 * regime_stability) + (0.35 * score_stability)
    value = clamp(raw)

    return StabilityResult(
        value=value,
        raw=raw,
        components={
            "market_regime": snapshot.market_regime,
            "entry_market_regime": (
                entry_snapshot.market_regime if entry_snapshot is not None else None
            ),
            "regime_changed": regime_changed,
            "current_score": snapshot.current_score,
            "entry_score": (
                entry_snapshot.current_score if entry_snapshot is not None else None
            ),
            "score_delta": score_delta,
            "score_delta_scale": score_delta_scale,
            "regime_stability": regime_stability,
            "score_stability": score_stability,
            "method": "regime_change_score_delta_stability_v1",
        },
    )

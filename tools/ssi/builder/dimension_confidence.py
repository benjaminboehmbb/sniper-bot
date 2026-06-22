from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from tools.ssi.builder.lifecycle_snapshot import LifecycleSnapshot
from tools.ssi.common.normalization import clamp, normalize_linear


@dataclass(frozen=True)
class ConfidenceResult:
    value: float
    raw: float
    components: Dict[str, Any]


def _atr_score(atr_quality: str) -> float:
    value = atr_quality.strip().lower()

    if value == "good_atr":
        return 1.0

    if value == "bad_atr":
        return 0.0

    return 0.5


def _mfi_score_for_side(side: str, mfi_signal: Optional[int]) -> float:
    if mfi_signal is None:
        return 0.5

    if side == "LONG":
        if mfi_signal > 0:
            return 1.0
        if mfi_signal < 0:
            return 0.0
        return 0.5

    if side == "SHORT":
        if mfi_signal < 0:
            return 1.0
        if mfi_signal > 0:
            return 0.0
        return 0.5

    return 0.5


def calculate_confidence(
    snapshot: LifecycleSnapshot,
    *,
    score_abs_max: float = 4.0,
    score_weight: float = 0.50,
    atr_weight: float = 0.25,
    mfi_weight: float = 0.25,
) -> ConfidenceResult:
    if score_abs_max <= 0:
        raise ValueError("score_abs_max must be > 0")

    if score_weight < 0 or atr_weight < 0 or mfi_weight < 0:
        raise ValueError("weights must be >= 0")

    total_weight = score_weight + atr_weight + mfi_weight
    if total_weight <= 0:
        raise ValueError("sum of weights must be > 0")

    score_strength = normalize_linear(
        abs(snapshot.current_score),
        lower=0.0,
        upper=score_abs_max,
    )

    atr_score = _atr_score(snapshot.atr_quality)
    mfi_score = _mfi_score_for_side(snapshot.side, snapshot.mfi_signal)

    raw = (
        (score_strength * score_weight)
        + (atr_score * atr_weight)
        + (mfi_score * mfi_weight)
    ) / total_weight

    value = clamp(raw)

    return ConfidenceResult(
        value=value,
        raw=raw,
        components={
            "current_score": snapshot.current_score,
            "score_abs_max": score_abs_max,
            "score_strength": score_strength,
            "atr_quality": snapshot.atr_quality,
            "atr_score": atr_score,
            "mfi_signal": snapshot.mfi_signal,
            "mfi_score": mfi_score,
            "score_weight": score_weight,
            "atr_weight": atr_weight,
            "mfi_weight": mfi_weight,
            "method": "score_atr_mfi_entry_confidence_v1",
        },
    )

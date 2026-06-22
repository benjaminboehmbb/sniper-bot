from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any

from tools.ssi.builder.lifecycle_snapshot import LifecycleSnapshot
from tools.ssi.common.normalization import clamp, normalize_symmetric


@dataclass(frozen=True)
class ProgressResult:
    value: float
    raw: float
    components: Dict[str, Any]


def calculate_progress(
    snapshot: LifecycleSnapshot,
    *,
    pnl_scale: float = 100.0,
) -> ProgressResult:
    if pnl_scale <= 0:
        raise ValueError("pnl_scale must be > 0")

    raw = snapshot.unrealized_pnl
    value = normalize_symmetric(raw, scale=pnl_scale, center=0.0)

    if snapshot.unrealized_pnl > 0:
        direction = "positive"
    elif snapshot.unrealized_pnl < 0:
        direction = "negative"
    else:
        direction = "neutral"

    value = clamp(value)

    return ProgressResult(
        value=value,
        raw=raw,
        components={
            "unrealized_pnl": snapshot.unrealized_pnl,
            "pnl_scale": pnl_scale,
            "direction": direction,
            "method": "symmetric_pnl_normalization_v1",
        },
    )

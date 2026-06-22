from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class LifecycleSnapshot:
    runtime_id: str
    source_file: str
    source_row_index: int

    timestamp: str
    snapshot_id: str
    tick: int
    side: str

    current_score: float
    market_regime: str
    unrealized_pnl: float
    atr_quality: str
    duration: float

    trade_id: Optional[str] = None
    ma200_signal: Optional[int] = None
    mfi_signal: Optional[int] = None

    raw: Optional[Dict[str, Any]] = None

    def validate(self) -> List[str]:
        errors: List[str] = []

        if not self.runtime_id.strip():
            errors.append("runtime_id is empty")

        if not self.source_file.strip():
            errors.append("source_file is empty")

        if self.source_row_index < 0:
            errors.append("source_row_index must be >= 0")

        if not self.timestamp.strip():
            errors.append("timestamp is empty")

        if not self.snapshot_id.strip():
            errors.append("snapshot_id is empty")

        if self.tick < 0:
            errors.append("tick must be >= 0")

        if self.side not in {"LONG", "SHORT"}:
            errors.append(f"invalid side: {self.side}")

        if not self.market_regime.strip():
            errors.append("market_regime is empty")

        if not self.atr_quality.strip():
            errors.append("atr_quality is empty")

        if self.duration < 0:
            errors.append("duration must be >= 0")

        return errors


def _get_value(row: Dict[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in row:
            return row[name]
    return default


def _safe_int(value: Any, default: int = 0) -> int:
    if value is None or value == "":
        return default
    return int(float(value))


def _safe_float(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    return float(value)


def snapshot_from_row(
    *,
    row: Dict[str, Any],
    runtime_id: str,
    source_file: str,
    source_row_index: int,
) -> LifecycleSnapshot:
    snapshot = LifecycleSnapshot(
        runtime_id=runtime_id,
        source_file=source_file,
        source_row_index=source_row_index,
        timestamp=str(_get_value(row, "timestamp", "timestamp_utc", default="")),
        snapshot_id=str(_get_value(row, "snapshot_id", default=f"row_{source_row_index}")),
        tick=_safe_int(_get_value(row, "tick", default=0)),
        side=str(_get_value(row, "side", default="")).upper(),
        current_score=_safe_float(_get_value(row, "current_score", default=0.0)),
        market_regime=str(_get_value(row, "market_regime", default="")),
        unrealized_pnl=_safe_float(_get_value(row, "unrealized_pnl", default=0.0)),
        atr_quality=str(_get_value(row, "atr_quality", default="")),
        duration=_safe_float(_get_value(row, "duration", "duration_sec", default=0.0)),
        trade_id=(
            str(_get_value(row, "trade_id", default=""))
            if _get_value(row, "trade_id", default="") != ""
            else None
        ),
        ma200_signal=(
            _safe_int(_get_value(row, "ma200_signal"), default=0)
            if _get_value(row, "ma200_signal") is not None
            else None
        ),
        mfi_signal=(
            _safe_int(_get_value(row, "mfi_signal"), default=0)
            if _get_value(row, "mfi_signal") is not None
            else None
        ),
        raw=dict(row),
    )

    errors = snapshot.validate()
    if errors:
        joined = "\n".join(f"- {error}" for error in errors)
        raise ValueError(f"Invalid LifecycleSnapshot:\n{joined}")

    return snapshot

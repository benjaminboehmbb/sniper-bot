from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


TSV_VERSION = "1.0"
GENERATOR_NAME = "ssi_tsv_builder"


@dataclass(frozen=True)
class TradeStateVector:
    tsv_id: str
    tsv_version: str
    runtime_id: str

    trade_id: Optional[str]
    snapshot_id: str
    timestamp_utc: str
    tick: int
    side: str

    progress: float
    compatibility: float
    stability: float
    confidence: float

    source_file: str
    source_row_index: int
    created_at_utc: str
    generator_name: str
    generator_version: str

    progress_raw: Optional[float] = None
    compatibility_raw: Optional[float] = None
    stability_raw: Optional[float] = None
    confidence_raw: Optional[float] = None

    progress_components: Optional[Dict[str, Any]] = None
    compatibility_components: Optional[Dict[str, Any]] = None
    stability_components: Optional[Dict[str, Any]] = None
    confidence_components: Optional[Dict[str, Any]] = None

    market_regime: Optional[str] = None
    current_score: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    duration_sec: Optional[float] = None
    atr_quality: Optional[str] = None
    ma200_signal: Optional[int] = None
    mfi_signal: Optional[int] = None

    def validate(self) -> List[str]:
        errors: List[str] = []

        required_strings = {
            "tsv_id": self.tsv_id,
            "tsv_version": self.tsv_version,
            "runtime_id": self.runtime_id,
            "snapshot_id": self.snapshot_id,
            "timestamp_utc": self.timestamp_utc,
            "side": self.side,
            "source_file": self.source_file,
            "created_at_utc": self.created_at_utc,
            "generator_name": self.generator_name,
            "generator_version": self.generator_version,
        }

        for name, value in required_strings.items():
            if not str(value).strip():
                errors.append(f"{name} is empty")

        if self.tick < 0:
            errors.append("tick must be >= 0")

        if self.source_row_index < 0:
            errors.append("source_row_index must be >= 0")

        if self.side not in {"LONG", "SHORT"}:
            errors.append(f"invalid side: {self.side}")

        dimensions = {
            "progress": self.progress,
            "compatibility": self.compatibility,
            "stability": self.stability,
            "confidence": self.confidence,
        }

        for name, value in dimensions.items():
            if value < 0.0 or value > 1.0:
                errors.append(f"{name} out of range [0.0, 1.0]: {value}")

        return errors

    def to_record(self) -> Dict[str, Any]:
        return {
            "tsv_id": self.tsv_id,
            "tsv_version": self.tsv_version,
            "runtime_id": self.runtime_id,
            "trade_id": self.trade_id,
            "snapshot_id": self.snapshot_id,
            "timestamp_utc": self.timestamp_utc,
            "tick": self.tick,
            "side": self.side,
            "progress": self.progress,
            "compatibility": self.compatibility,
            "stability": self.stability,
            "confidence": self.confidence,
            "source_file": self.source_file,
            "source_row_index": self.source_row_index,
            "created_at_utc": self.created_at_utc,
            "generator_name": self.generator_name,
            "generator_version": self.generator_version,
            "progress_raw": self.progress_raw,
            "compatibility_raw": self.compatibility_raw,
            "stability_raw": self.stability_raw,
            "confidence_raw": self.confidence_raw,
            "progress_components": self.progress_components,
            "compatibility_components": self.compatibility_components,
            "stability_components": self.stability_components,
            "confidence_components": self.confidence_components,
            "market_regime": self.market_regime,
            "current_score": self.current_score,
            "unrealized_pnl": self.unrealized_pnl,
            "duration_sec": self.duration_sec,
            "atr_quality": self.atr_quality,
            "ma200_signal": self.ma200_signal,
            "mfi_signal": self.mfi_signal,
        }


def assert_valid_tsv(tsv: TradeStateVector) -> None:
    errors = tsv.validate()
    if errors:
        joined = "\n".join(f"- {error}" for error in errors)
        raise ValueError(f"Invalid TradeStateVector:\n{joined}")

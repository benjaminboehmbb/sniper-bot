from __future__ import annotations

from datetime import datetime, timezone

from tools.ssi.builder.dimension_compatibility import calculate_compatibility
from tools.ssi.builder.dimension_confidence import calculate_confidence
from tools.ssi.builder.dimension_progress import calculate_progress
from tools.ssi.builder.dimension_stability import calculate_stability
from tools.ssi.builder.lifecycle_snapshot import LifecycleSnapshot
from tools.ssi.builder.trade_state_vector import (
    GENERATOR_NAME,
    TSV_VERSION,
    TradeStateVector,
    assert_valid_tsv,
)
from tools.ssi.common.hash_utils import build_tsv_id


GENERATOR_VERSION = "1.0"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_trade_state_vector(
    *,
    snapshot: LifecycleSnapshot,
    entry_snapshot: LifecycleSnapshot | None = None,
    created_at_utc: str | None = None,
    generator_version: str = GENERATOR_VERSION,
) -> TradeStateVector:
    progress = calculate_progress(snapshot)
    compatibility = calculate_compatibility(snapshot)
    stability = calculate_stability(snapshot, entry_snapshot=entry_snapshot)
    confidence = calculate_confidence(entry_snapshot if entry_snapshot is not None else snapshot)

    timestamp_utc = snapshot.timestamp
    created = created_at_utc if created_at_utc is not None else utc_now_iso()

    tsv = TradeStateVector(
        tsv_id=build_tsv_id(
            runtime_id=snapshot.runtime_id,
            trade_id=snapshot.trade_id,
            snapshot_id=snapshot.snapshot_id,
            timestamp_utc=timestamp_utc,
            tsv_version=TSV_VERSION,
        ),
        tsv_version=TSV_VERSION,
        runtime_id=snapshot.runtime_id,
        trade_id=snapshot.trade_id,
        snapshot_id=snapshot.snapshot_id,
        timestamp_utc=timestamp_utc,
        tick=snapshot.tick,
        side=snapshot.side,
        progress=progress.value,
        compatibility=compatibility.value,
        stability=stability.value,
        confidence=confidence.value,
        source_file=snapshot.source_file,
        source_row_index=snapshot.source_row_index,
        created_at_utc=created,
        generator_name=GENERATOR_NAME,
        generator_version=generator_version,
        progress_raw=progress.raw,
        compatibility_raw=compatibility.raw,
        stability_raw=stability.raw,
        confidence_raw=confidence.raw,
        progress_components=progress.components,
        compatibility_components=compatibility.components,
        stability_components=stability.components,
        confidence_components=confidence.components,
        market_regime=snapshot.market_regime,
        current_score=snapshot.current_score,
        unrealized_pnl=snapshot.unrealized_pnl,
        duration_sec=snapshot.duration,
        atr_quality=snapshot.atr_quality,
        ma200_signal=snapshot.ma200_signal,
        mfi_signal=snapshot.mfi_signal,
    )

    assert_valid_tsv(tsv)
    return tsv

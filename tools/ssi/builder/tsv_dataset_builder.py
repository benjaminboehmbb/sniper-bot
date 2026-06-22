from __future__ import annotations

from typing import Dict, List

from tools.ssi.builder.lifecycle_loader import group_entry_snapshots_by_trade
from tools.ssi.builder.lifecycle_snapshot import LifecycleSnapshot
from tools.ssi.builder.trade_state_vector import TradeStateVector, assert_valid_tsv
from tools.ssi.builder.tsv_builder import build_trade_state_vector


def build_tsv_dataset(
    snapshots: List[LifecycleSnapshot],
    *,
    created_at_utc: str | None = None,
) -> List[TradeStateVector]:
    if not snapshots:
        raise ValueError("snapshots must not be empty")

    entry_by_trade: Dict[str, LifecycleSnapshot] = group_entry_snapshots_by_trade(snapshots)

    tsv_records: List[TradeStateVector] = []

    for snapshot in snapshots:
        entry_snapshot = (
            entry_by_trade.get(snapshot.trade_id)
            if snapshot.trade_id is not None
            else None
        )

        tsv = build_trade_state_vector(
            snapshot=snapshot,
            entry_snapshot=entry_snapshot,
            created_at_utc=created_at_utc,
        )

        assert_valid_tsv(tsv)
        tsv_records.append(tsv)

    seen_ids = set()
    for tsv in tsv_records:
        if tsv.tsv_id in seen_ids:
            raise ValueError(f"duplicate tsv_id detected: {tsv.tsv_id}")
        seen_ids.add(tsv.tsv_id)

    return tsv_records

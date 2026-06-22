from __future__ import annotations

import csv
from pathlib import Path
from typing import List

from tools.ssi.builder.lifecycle_snapshot import LifecycleSnapshot, snapshot_from_row


def load_lifecycle_snapshots(
    *,
    input_path: Path,
    runtime_id: str,
) -> List[LifecycleSnapshot]:
    if not input_path.exists():
        raise FileNotFoundError(f"lifecycle snapshot file not found: {input_path}")

    if not input_path.is_file():
        raise ValueError(f"lifecycle snapshot path is not a file: {input_path}")

    snapshots: List[LifecycleSnapshot] = []

    with input_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)

        if reader.fieldnames is None:
            raise ValueError(f"lifecycle snapshot file has no header: {input_path}")

        for row_index, row in enumerate(reader):
            snapshot = snapshot_from_row(
                row=row,
                runtime_id=runtime_id,
                source_file=str(input_path),
                source_row_index=row_index,
            )
            snapshots.append(snapshot)

    if not snapshots:
        raise ValueError(f"lifecycle snapshot file contains no rows: {input_path}")

    return snapshots


def group_entry_snapshots_by_trade(
    snapshots: List[LifecycleSnapshot],
) -> dict[str, LifecycleSnapshot]:
    entries: dict[str, LifecycleSnapshot] = {}

    for snapshot in snapshots:
        if snapshot.trade_id is None:
            continue

        existing = entries.get(snapshot.trade_id)
        if existing is None:
            entries[snapshot.trade_id] = snapshot
            continue

        if (snapshot.tick, snapshot.source_row_index) < (
            existing.tick,
            existing.source_row_index,
        ):
            entries[snapshot.trade_id] = snapshot

    return entries

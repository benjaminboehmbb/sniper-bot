from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from tools.ssi.builder.trade_state_vector import TradeStateVector


TSV_CSV_COLUMNS = [
    "tsv_id",
    "tsv_version",
    "runtime_id",
    "trade_id",
    "snapshot_id",
    "timestamp_utc",
    "tick",
    "side",
    "progress",
    "compatibility",
    "stability",
    "confidence",
    "source_file",
    "source_row_index",
    "created_at_utc",
    "generator_name",
    "generator_version",
    "progress_raw",
    "compatibility_raw",
    "stability_raw",
    "confidence_raw",
    "progress_components",
    "compatibility_components",
    "stability_components",
    "confidence_components",
    "market_regime",
    "current_score",
    "unrealized_pnl",
    "duration_sec",
    "atr_quality",
    "ma200_signal",
    "mfi_signal",
]


def _serialize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))

    return value


def write_tsv_csv(
    *,
    records: List[TradeStateVector],
    output_path: Path,
) -> Path:
    if not records:
        raise ValueError("records must not be empty")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TSV_CSV_COLUMNS)
        writer.writeheader()

        for record in records:
            row: Dict[str, Any] = record.to_record()
            writer.writerow(
                {
                    column: _serialize_value(row.get(column))
                    for column in TSV_CSV_COLUMNS
                }
            )

    return output_path

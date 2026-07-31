#!/usr/bin/env python3
"""Verify the implemented S0 source profile against provider evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
from zipfile import ZipFile

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from rcc002.s0.source_identity import scan_binance_vision_archive
from rcc002.s1.normalize import (
    normalize_registered_rows,
    parse_csv_rows,
)


COLUMN_MAPPING = {
    "open_time": 0,
    "open": 1,
    "high": 2,
    "low": 3,
    "close": 4,
    "volume": 5,
    "close_time": 6,
}
SNAPSHOT_ID = "source:sha256:" + "0" * 64


def _provider_relative_name(basename: str) -> str:
    token = basename.removeprefix("BTCUSDT-1m-").removesuffix(".zip")
    family = "daily" if len(token) == 10 else "monthly"
    return (
        f"data/spot/{family}/klines/BTCUSDT/1m/"
        f"{basename}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence_zip", type=Path)
    args = parser.parse_args()

    results: list[dict[str, object]] = []
    with ZipFile(args.evidence_zip) as evidence:
        names = sorted(
            item.filename
            for item in evidence.infolist()
            if not item.is_dir() and item.filename.endswith(".zip")
        )
        if len(names) != 4:
            raise AssertionError("expected exactly four evidence archives")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            all_row_ids: set[str] = set()
            for source_file_ordinal, name in enumerate(names):
                checksum_name = name + ".CHECKSUM"
                checksum = evidence.read(checksum_name).decode("ascii").split()[0]
                local = root / Path(name).name
                local.write_bytes(evidence.read(name))
                scanned = scan_binance_vision_archive(
                    local,
                    provider_relative_name=_provider_relative_name(name),
                    provider_checksum_sha256=checksum,
                )
                with ZipFile(local) as archive:
                    csv_name = archive.namelist()[0]
                    text = archive.read(csv_name).decode("utf-8")
                raw_rows = parse_csv_rows(
                    text,
                    COLUMN_MAPPING,
                    header_mode="ABSENT",
                )
                normalized = normalize_registered_rows(
                    raw_rows,
                    archive_period=scanned.archive_period,
                    source_snapshot_id=SNAPSHOT_ID,
                    source_file_ordinal=source_file_ordinal,
                    provider="BINANCE_VISION",
                    market_type="spot",
                    symbol="BTCUSDT",
                    interval="1m",
                )
                if len(normalized.rows) != scanned.record_count:
                    raise AssertionError("S0/S1 record counts disagree")
                if (
                    min(row.open_time for row in normalized.rows)
                    != scanned.min_open_time_utc_ms
                    or max(row.close_time for row in normalized.rows)
                    != scanned.max_close_time_utc_ms
                ):
                    raise AssertionError("S0/S1 normalized coverage disagrees")
                row_ids = {row.source_row_id for row in normalized.rows}
                if len(row_ids) != len(normalized.rows):
                    raise AssertionError("S1 row IDs collide within archive")
                if all_row_ids & row_ids:
                    raise AssertionError("S1 row IDs collide across archives")
                all_row_ids.update(row_ids)
                results.append(
                    {
                        "archive_name": name,
                        "record_count": scanned.record_count,
                        "timestamp_unit": scanned.timestamp_unit.value,
                        "min_open_time_utc_ms": (
                            scanned.min_open_time_utc_ms
                        ),
                        "max_close_time_utc_ms": (
                            scanned.max_close_time_utc_ms
                        ),
                        "s0_s1_normalization_parity": "PASS",
                        "verification_result": "PASS",
                    }
                )

    record_count = sum(int(item["record_count"]) for item in results)
    if record_count != 92_160:
        raise AssertionError(f"unexpected record count {record_count}")
    report = {
        "result": "PASS",
        "archive_count": len(results),
        "record_count": record_count,
        "source_row_id_unique_count": len(all_row_ids),
        "archives": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Deterministically verify RCC-002 Binance Vision timestamp evidence."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from io import BytesIO, StringIO
import json
from pathlib import Path, PurePosixPath
import re
from zipfile import ZipFile


BOUNDARY = datetime(2025, 1, 1, tzinfo=timezone.utc)
DAILY = re.compile(r"^BTCUSDT-1m-(\d{4}-\d{2}-\d{2})\.zip$")
MONTHLY = re.compile(r"^BTCUSDT-1m-(\d{4}-\d{2})\.zip$")


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def safe_member(name: str) -> bool:
    path = PurePosixPath(name)
    return (
        bool(name)
        and not path.is_absolute()
        and ".." not in path.parts
        and "\\" not in name
    )


def add_month(value: datetime) -> datetime:
    if value.month == 12:
        return value.replace(year=value.year + 1, month=1)
    return value.replace(month=value.month + 1)


def period_for(name: str) -> tuple[str, str, datetime, datetime]:
    daily = DAILY.fullmatch(name)
    if daily:
        start = datetime.strptime(daily.group(1), "%Y-%m-%d").replace(
            tzinfo=timezone.utc
        )
        return "DAILY", daily.group(1), start, start + timedelta(days=1)
    monthly = MONTHLY.fullmatch(name)
    if monthly:
        start = datetime.strptime(monthly.group(1), "%Y-%m").replace(
            tzinfo=timezone.utc
        )
        return "MONTHLY", monthly.group(1), start, add_month(start)
    raise AssertionError(f"unregistered archive name: {name}")


def utc_ms(value: datetime) -> int:
    return int(value.timestamp() * 1000)


def verify_archive(
    archive_name: str,
    archive_bytes: bytes,
    checksum_bytes: bytes,
    registry_entry: dict,
) -> dict:
    family, token, period_start, period_end = period_for(archive_name)
    archive_hash = digest(archive_bytes)
    checksum_text = checksum_bytes.decode("ascii").strip()
    match = re.fullmatch(r"([0-9a-f]{64})\s+\*?(\S+)", checksum_text)
    assert match is not None, f"invalid provider checksum file: {archive_name}"
    assert match.group(2) == archive_name
    assert match.group(1) == archive_hash

    with ZipFile(BytesIO(archive_bytes)) as nested:
        assert nested.testzip() is None
        members = [item for item in nested.infolist() if not item.is_dir()]
        assert len(members) == 1
        member = members[0]
        assert safe_member(member.filename)
        assert member.filename == archive_name.removesuffix(".zip") + ".csv"
        csv_bytes = nested.read(member)

    assert not csv_bytes.startswith(b"\xef\xbb\xbf")
    assert b"\r" not in csv_bytes
    assert csv_bytes.endswith(b"\n")
    csv_text = csv_bytes.decode("utf-8")
    rows = list(csv.reader(StringIO(csv_text, newline="")))
    assert rows
    assert all(len(row) == 12 for row in rows)
    assert rows[0][0].isdigit(), "registered header mode is ABSENT"

    if period_end <= BOUNDARY:
        unit = "MILLISECOND"
        divisor = 1
    elif period_start >= BOUNDARY:
        unit = "MICROSECOND"
        divisor = 1000
    else:
        raise AssertionError("archive period crosses timestamp-unit boundary")

    normalized_open: list[int] = []
    normalized_close: list[int] = []
    for index, row in enumerate(rows):
        raw_open = int(row[0])
        raw_close = int(row[6])
        if unit == "MICROSECOND":
            assert raw_open % 1000 == 0, (archive_name, index, "open remainder")
            assert raw_close % 1000 == 999, (archive_name, index, "close remainder")
        open_ms = raw_open // divisor
        close_ms = raw_close // divisor
        assert open_ms % 60000 == 0, (archive_name, index, "minute alignment")
        assert close_ms == open_ms + 59999, (archive_name, index, "close relation")
        if normalized_open:
            assert open_ms == normalized_open[-1] + 60000, (
                archive_name,
                index,
                "continuity",
            )
        normalized_open.append(open_ms)
        normalized_close.append(close_ms)

    assert len(set(normalized_open)) == len(rows)
    assert normalized_open[0] == utc_ms(period_start)
    assert normalized_close[-1] == utc_ms(period_end) - 1

    result = {
        "archive_name": archive_name,
        "archive_family": family,
        "period_token": token,
        "archive_byte_sha256": archive_hash,
        "archive_size_bytes": len(archive_bytes),
        "provider_checksum_text_sha256": digest(checksum_bytes),
        "provider_checksum_sha256": match.group(1),
        "csv_member_name": member.filename,
        "csv_member_byte_sha256": digest(csv_bytes),
        "csv_member_size_bytes": len(csv_bytes),
        "record_count": len(rows),
        "selected_timestamp_unit": unit,
        "first_raw_open_time": int(rows[0][0]),
        "first_raw_close_time": int(rows[0][6]),
        "last_raw_open_time": int(rows[-1][0]),
        "last_raw_close_time": int(rows[-1][6]),
        "first_open_time_utc_ms": normalized_open[0],
        "last_close_time_utc_ms": normalized_close[-1],
        "verification_result": "PASS",
    }
    for key, value in result.items():
        if key in registry_entry:
            assert registry_entry[key] == value, (archive_name, key)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence_zip", type=Path)
    parser.add_argument("--registry", type=Path, required=True)
    args = parser.parse_args()

    outer_bytes = args.evidence_zip.read_bytes()
    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    registry_by_basename = {
        PurePosixPath(item["provider_relative_name"]).name: item
        for item in registry["archives"]
    }

    with ZipFile(BytesIO(outer_bytes)) as outer:
        assert outer.testzip() is None
        names = [item.filename for item in outer.infolist() if not item.is_dir()]
        assert all(safe_member(name) for name in names)
        archives = sorted(name for name in names if name.endswith(".zip"))
        checksums = sorted(name for name in names if name.endswith(".zip.CHECKSUM"))
        assert len(archives) == 4
        assert checksums == [name + ".CHECKSUM" for name in archives]
        assert set(archives) == set(registry_by_basename)
        results = [
            verify_archive(
                name,
                outer.read(name),
                outer.read(name + ".CHECKSUM"),
                registry_by_basename[name],
            )
            for name in archives
        ]

    report = {
        "evidence_input_sha256": digest(outer_bytes),
        "archive_count": len(results),
        "record_count": sum(item["record_count"] for item in results),
        "archives": results,
        "result": "PASS",
    }
    assert report["evidence_input_sha256"] == registry["evidence_input_package"][
        "byte_sha256"
    ]
    assert report["record_count"] == registry["aggregate_result"]["record_count"]
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

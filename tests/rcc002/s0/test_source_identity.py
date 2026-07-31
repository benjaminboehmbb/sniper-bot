"""Tests for deterministic S0 archive scanning and Source Snapshot V1."""

from __future__ import annotations

import dataclasses
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZIP_DEFLATED, ZipFile

from rcc002.s0.profiles import (
    ArchivePeriod,
    SourceProfileError,
    TimestampUnit,
)
from rcc002.s0.source_identity import (
    SourceFileIdentity,
    build_source_snapshot,
    canonical_json_bytes,
    scan_binance_vision_archive,
)


FIXTURE_ROOT = (
    Path(__file__).resolve().parents[2]
    / "fixtures/rcc002/source"
)
DAILY_2025_NAME = (
    "data/spot/daily/klines/BTCUSDT/1m/"
    "BTCUSDT-1m-2025-01-01.zip"
)


def _record(open_time: int, close_time: int) -> str:
    return ",".join(
        (
            str(open_time),
            "1.0",
            "2.0",
            "0.5",
            "1.5",
            "100.0",
            str(close_time),
            "100.0",
            "2",
            "50.0",
            "50.0",
            "0",
        )
    )


def _zip_bytes(
    members: dict[str, str],
) -> bytes:
    output = io.BytesIO()
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        for name, value in members.items():
            archive.writestr(name, value)
    return output.getvalue()


def _descriptor(
    *,
    name: str,
    digest_character: str,
    period: ArchivePeriod,
    minimum: int,
    maximum: int,
    ordinal: int = 0,
) -> SourceFileIdentity:
    return SourceFileIdentity(
        provider_relative_name=name,
        byte_sha256=digest_character * 64,
        provider_checksum_sha256=digest_character * 64,
        size_bytes=100,
        csv_member_name=Path(name).name.removesuffix(".zip") + ".csv",
        source_file_ordinal=ordinal,
        archive_period=period,
        record_count=1,
        min_open_time_utc_ms=minimum,
        max_close_time_utc_ms=maximum,
        timestamp_unit=TimestampUnit.MILLISECOND,
    )


class ArchiveScanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_archive(self, members: dict[str, str]) -> tuple[Path, str]:
        data = _zip_bytes(members)
        path = self.root / "source.zip"
        path.write_bytes(data)
        return path, hashlib.sha256(data).hexdigest()

    def test_headerless_record_zero_is_retained(self) -> None:
        path, digest = self.write_archive(
            {
                "BTCUSDT-1m-2025-01-01.csv": "\n".join(
                    (
                        _record(
                            1_735_689_600_000_000,
                            1_735_689_659_999_999,
                        ),
                        _record(
                            1_735_689_660_000_000,
                            1_735_689_719_999_999,
                        ),
                    )
                )
                + "\n"
            }
        )
        result = scan_binance_vision_archive(
            path,
            provider_relative_name=DAILY_2025_NAME,
            provider_checksum_sha256=digest,
        )
        self.assertEqual(result.record_count, 2)
        self.assertEqual(result.min_open_time_utc_ms, 1_735_689_600_000)
        self.assertEqual(result.max_close_time_utc_ms, 1_735_689_719_999)
        self.assertIs(result.timestamp_unit, TimestampUnit.MICROSECOND)

    def test_unexpected_header_rejected(self) -> None:
        path, digest = self.write_archive(
            {
                "BTCUSDT-1m-2025-01-01.csv": (
                    "open_time,open,high,low,close,volume,close_time,"
                    "quote_asset_volume,number_of_trades,"
                    "taker_buy_base_asset_volume,"
                    "taker_buy_quote_asset_volume,ignore\n"
                )
            }
        )
        with self.assertRaises(SourceProfileError) as context:
            scan_binance_vision_archive(
                path,
                provider_relative_name=DAILY_2025_NAME,
                provider_checksum_sha256=digest,
            )
        self.assertEqual(
            context.exception.reason_code,
            "RCC_SOURCE_HEADER_MODE_MISMATCH",
        )

    def test_wrong_column_count_rejected(self) -> None:
        path, digest = self.write_archive(
            {"BTCUSDT-1m-2025-01-01.csv": "1,2,3\n"}
        )
        with self.assertRaises(SourceProfileError) as context:
            scan_binance_vision_archive(
                path,
                provider_relative_name=DAILY_2025_NAME,
                provider_checksum_sha256=digest,
            )
        self.assertEqual(
            context.exception.reason_code,
            "RCC_SOURCE_COLUMN_COUNT_MISMATCH",
        )

    def test_blank_physical_record_rejected(self) -> None:
        path, digest = self.write_archive(
            {
                "BTCUSDT-1m-2025-01-01.csv": (
                    _record(
                        1_735_689_600_000_000,
                        1_735_689_659_999_999,
                    )
                    + "\n\n"
                    + _record(
                        1_735_689_660_000_000,
                        1_735_689_719_999_999,
                    )
                )
            }
        )
        with self.assertRaises(SourceProfileError) as context:
            scan_binance_vision_archive(
                path,
                provider_relative_name=DAILY_2025_NAME,
                provider_checksum_sha256=digest,
            )
        self.assertEqual(
            context.exception.reason_code,
            "RCC_SOURCE_COLUMN_COUNT_MISMATCH",
        )

    def test_multiple_csv_members_rejected(self) -> None:
        path, digest = self.write_archive(
            {
                "BTCUSDT-1m-2025-01-01.csv": _record(
                    1_735_689_600_000_000,
                    1_735_689_659_999_999,
                ),
                "unexpected.csv": _record(
                    1_735_689_600_000_000,
                    1_735_689_659_999_999,
                ),
            }
        )
        with self.assertRaises(SourceProfileError) as context:
            scan_binance_vision_archive(
                path,
                provider_relative_name=DAILY_2025_NAME,
                provider_checksum_sha256=digest,
            )
        self.assertEqual(
            context.exception.reason_code,
            "RCC_SOURCE_ZIP_MEMBER_COUNT_MISMATCH",
        )

    def test_provider_checksum_mismatch_rejected(self) -> None:
        path, _ = self.write_archive(
            {
                "BTCUSDT-1m-2025-01-01.csv": _record(
                    1_735_689_600_000_000,
                    1_735_689_659_999_999,
                )
            }
        )
        with self.assertRaises(SourceProfileError) as context:
            scan_binance_vision_archive(
                path,
                provider_relative_name=DAILY_2025_NAME,
                provider_checksum_sha256="0" * 64,
            )
        self.assertEqual(
            context.exception.reason_code,
            "RCC_SOURCE_PROVIDER_CHECKSUM_MISMATCH",
        )


class SourceSnapshotTests(unittest.TestCase):
    def test_golden_preimage_and_identity(self) -> None:
        fixture = json.loads(
            (
                FIXTURE_ROOT / "source_identity_golden.v1.json"
            ).read_text(encoding="utf-8")
        )
        case = fixture["source_snapshot_case"]
        source = case["preimage"]["source_files"][0]
        period = source["archive_period"]
        descriptor = SourceFileIdentity(
            provider_relative_name=source["provider_relative_name"],
            byte_sha256=source["byte_sha256"],
            provider_checksum_sha256=source[
                "provider_checksum_sha256"
            ],
            size_bytes=source["size_bytes"],
            csv_member_name=source["csv_member_name"],
            source_file_ordinal=source["source_file_ordinal"],
            archive_period=ArchivePeriod(**period),
            record_count=source["record_count"],
            min_open_time_utc_ms=source["min_open_time_utc_ms"],
            max_close_time_utc_ms=source["max_close_time_utc_ms"],
            timestamp_unit=TimestampUnit(source["timestamp_unit"]),
        )
        snapshot = build_source_snapshot((descriptor,))
        self.assertEqual(snapshot.preimage(), case["preimage"])
        self.assertEqual(snapshot.preimage_sha256, case["expected_sha256"])
        self.assertEqual(
            snapshot.source_snapshot_id,
            case["expected_source_snapshot_id"],
        )
        self.assertEqual(
            hashlib.sha256(
                canonical_json_bytes(snapshot.preimage())
            ).hexdigest(),
            case["expected_sha256"],
        )

    def test_discovery_order_does_not_change_ordinals_or_identity(self) -> None:
        first_period = ArchivePeriod(
            "DAILY",
            "2024-12-30",
            "2024-12-30T00:00:00Z",
            "2024-12-31T00:00:00Z",
        )
        second_period = ArchivePeriod(
            "DAILY",
            "2024-12-31",
            "2024-12-31T00:00:00Z",
            "2025-01-01T00:00:00Z",
        )
        first = _descriptor(
            name=(
                "data/spot/daily/klines/BTCUSDT/1m/"
                "BTCUSDT-1m-2024-12-30.zip"
            ),
            digest_character="a",
            period=first_period,
            minimum=1_735_516_800_000,
            maximum=1_735_516_859_999,
            ordinal=99,
        )
        second = _descriptor(
            name=(
                "data/spot/daily/klines/BTCUSDT/1m/"
                "BTCUSDT-1m-2024-12-31.zip"
            ),
            digest_character="b",
            period=second_period,
            minimum=1_735_603_200_000,
            maximum=1_735_603_259_999,
            ordinal=88,
        )
        forward = build_source_snapshot((first, second))
        reverse = build_source_snapshot((second, first))
        self.assertEqual(
            forward.source_snapshot_id,
            reverse.source_snapshot_id,
        )
        self.assertEqual(
            tuple(item.source_file_ordinal for item in forward.source_files),
            (0, 1),
        )

    def test_duplicate_logical_period_matches_golden_error(self) -> None:
        fixture = json.loads(
            (
                FIXTURE_ROOT / "source_identity_golden.v1.json"
            ).read_text(encoding="utf-8")
        )
        case = next(
            item
            for item in fixture["negative_cases"]
            if item["case_id"]
            == "duplicate_logical_period_different_bytes"
        )
        period = ArchivePeriod(
            "DAILY",
            "2024-12-31",
            "2024-12-31T00:00:00Z",
            "2025-01-01T00:00:00Z",
        )
        first = _descriptor(
            name=(
                "data/spot/daily/klines/BTCUSDT/1m/"
                "BTCUSDT-1m-2024-12-31.zip"
            ),
            digest_character="a",
            period=period,
            minimum=1_735_603_200_000,
            maximum=1_735_603_259_999,
        )
        second = _descriptor(
            name=(
                "mirror/spot/daily/klines/BTCUSDT/1m/"
                "BTCUSDT-1m-2024-12-31.zip"
            ),
            digest_character="b",
            period=period,
            minimum=1_735_603_200_000,
            maximum=1_735_603_259_999,
            ordinal=1,
        )
        with self.assertRaises(SourceProfileError) as context:
            build_source_snapshot((first, second))
        self.assertEqual(
            context.exception.reason_code,
            case["expected_error"],
        )

    def test_empty_snapshot_rejected(self) -> None:
        with self.assertRaises(SourceProfileError):
            build_source_snapshot(())

    def test_source_revision_changes_snapshot_identity(self) -> None:
        fixture = json.loads(
            (
                FIXTURE_ROOT / "source_identity_golden.v1.json"
            ).read_text(encoding="utf-8")
        )
        source = fixture["source_snapshot_case"]["preimage"][
            "source_files"
        ][0]
        descriptor = SourceFileIdentity(
            provider_relative_name=source["provider_relative_name"],
            byte_sha256=source["byte_sha256"],
            provider_checksum_sha256=source[
                "provider_checksum_sha256"
            ],
            size_bytes=source["size_bytes"],
            csv_member_name=source["csv_member_name"],
            source_file_ordinal=0,
            archive_period=ArchivePeriod(**source["archive_period"]),
            record_count=source["record_count"],
            min_open_time_utc_ms=source["min_open_time_utc_ms"],
            max_close_time_utc_ms=source["max_close_time_utc_ms"],
            timestamp_unit=TimestampUnit(source["timestamp_unit"]),
        )
        original = build_source_snapshot((descriptor,))
        revised = build_source_snapshot(
            (descriptor,),
            source_revision="synthetic-revision-1",
        )
        self.assertNotEqual(
            original.source_snapshot_id,
            revised.source_snapshot_id,
        )

    def test_empty_source_revision_rejected(self) -> None:
        fixture = json.loads(
            (
                FIXTURE_ROOT / "source_identity_golden.v1.json"
            ).read_text(encoding="utf-8")
        )
        source = fixture["source_snapshot_case"]["preimage"][
            "source_files"
        ][0]
        descriptor = SourceFileIdentity(
            provider_relative_name=source["provider_relative_name"],
            byte_sha256=source["byte_sha256"],
            provider_checksum_sha256=source[
                "provider_checksum_sha256"
            ],
            size_bytes=source["size_bytes"],
            csv_member_name=source["csv_member_name"],
            source_file_ordinal=0,
            archive_period=ArchivePeriod(**source["archive_period"]),
            record_count=source["record_count"],
            min_open_time_utc_ms=source["min_open_time_utc_ms"],
            max_close_time_utc_ms=source["max_close_time_utc_ms"],
            timestamp_unit=TimestampUnit(source["timestamp_unit"]),
        )
        with self.assertRaises(SourceProfileError):
            build_source_snapshot((descriptor,), source_revision="")

    def test_descriptor_member_name_mismatch_rejected(self) -> None:
        period = ArchivePeriod(
            "DAILY",
            "2024-12-31",
            "2024-12-31T00:00:00Z",
            "2025-01-01T00:00:00Z",
        )
        descriptor = _descriptor(
            name=(
                "data/spot/daily/klines/BTCUSDT/1m/"
                "BTCUSDT-1m-2024-12-31.zip"
            ),
            digest_character="a",
            period=period,
            minimum=1_735_603_200_000,
            maximum=1_735_603_259_999,
        )
        with self.assertRaises(SourceProfileError):
            build_source_snapshot(
                (
                    dataclasses.replace(
                        descriptor,
                        csv_member_name="unexpected.csv",
                    ),
                )
            )

    def test_overlapping_coverage_rejected(self) -> None:
        period = ArchivePeriod(
            "DAILY",
            "2024-12-31",
            "2024-12-31T00:00:00Z",
            "2025-01-01T00:00:00Z",
        )
        first = _descriptor(
            name=(
                "data/spot/daily/klines/BTCUSDT/1m/"
                "BTCUSDT-1m-2024-12-31.zip"
            ),
            digest_character="a",
            period=period,
            minimum=1_735_603_200_000,
            maximum=1_735_603_259_999,
        )
        second = dataclasses.replace(
            first,
            provider_relative_name=(
                "data/spot/monthly/klines/BTCUSDT/1m/"
                "BTCUSDT-1m-2024-12.zip"
            ),
            byte_sha256="b" * 64,
            provider_checksum_sha256="b" * 64,
            archive_period=ArchivePeriod(
                "MONTHLY",
                "2024-12",
                "2024-12-01T00:00:00Z",
                "2025-01-01T00:00:00Z",
            ),
        )
        with self.assertRaises(SourceProfileError):
            build_source_snapshot((first, second))


if __name__ == "__main__":
    unittest.main()

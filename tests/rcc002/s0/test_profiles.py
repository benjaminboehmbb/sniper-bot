"""Golden and negative tests for registered source timestamp profiles."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

from rcc002.s0.profiles import (
    ArchivePeriod,
    SourceProfileError,
    TimestampUnit,
    normalize_timestamp_pair,
    parse_archive_period,
    reconcile_timestamp_to_period,
    resolve_timestamp_unit,
)


FIXTURE_ROOT = (
    Path(__file__).resolve().parents[2]
    / "fixtures/rcc002/source"
)


class ArchivePeriodTests(unittest.TestCase):
    def test_registered_daily_name(self) -> None:
        symbol, interval, period = parse_archive_period(
            "data/spot/daily/klines/BTCUSDT/1m/"
            "BTCUSDT-1m-2024-12-31.zip"
        )
        self.assertEqual((symbol, interval), ("BTCUSDT", "1m"))
        self.assertEqual(period.archive_family, "DAILY")
        self.assertEqual(period.period_start_utc, "2024-12-31T00:00:00Z")
        self.assertEqual(period.period_end_utc, "2025-01-01T00:00:00Z")

    def test_registered_monthly_name(self) -> None:
        _, _, period = parse_archive_period(
            "data/spot/monthly/klines/BTCUSDT/1m/"
            "BTCUSDT-1m-2025-01.zip"
        )
        self.assertEqual(period.archive_family, "MONTHLY")
        self.assertEqual(period.period_start_utc, "2025-01-01T00:00:00Z")
        self.assertEqual(period.period_end_utc, "2025-02-01T00:00:00Z")

    def test_path_basename_mismatch_rejected(self) -> None:
        with self.assertRaises(SourceProfileError):
            parse_archive_period(
                "data/spot/daily/klines/BTCUSDT/1m/"
                "ETHUSDT-1m-2025-01-01.zip"
            )

    def test_path_traversal_rejected(self) -> None:
        with self.assertRaises(SourceProfileError):
            parse_archive_period("../BTCUSDT-1m-2025-01-01.zip")

    def test_transition_branches(self) -> None:
        _, _, before = parse_archive_period(
            "data/spot/daily/klines/BTCUSDT/1m/"
            "BTCUSDT-1m-2024-12-31.zip"
        )
        _, _, after = parse_archive_period(
            "data/spot/daily/klines/BTCUSDT/1m/"
            "BTCUSDT-1m-2025-01-01.zip"
        )
        self.assertIs(resolve_timestamp_unit(before), TimestampUnit.MILLISECOND)
        self.assertIs(resolve_timestamp_unit(after), TimestampUnit.MICROSECOND)

    def test_boundary_crossing_period_rejected(self) -> None:
        crossing = ArchivePeriod(
            archive_family="DAILY",
            period_token="synthetic-crossing",
            period_start_utc="2024-12-31T00:00:00Z",
            period_end_utc="2025-01-02T00:00:00Z",
        )
        with self.assertRaises(SourceProfileError) as context:
            resolve_timestamp_unit(crossing)
        self.assertEqual(
            context.exception.reason_code,
            "RCC_SOURCE_ARCHIVE_PERIOD_CROSSES_UNIT_BOUNDARY",
        )


class TimestampGoldenFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(
            (
                FIXTURE_ROOT
                / "binance_spot_kline_timestamp_golden.v1.json"
            ).read_text(encoding="utf-8")
        )

    def test_all_registered_golden_cases(self) -> None:
        for case in self.fixture["cases"]:
            with self.subTest(case=case["case_id"]):
                period = ArchivePeriod(
                    archive_family=case["archive_family"],
                    period_token=case["case_id"],
                    period_start_utc=case["period_start_utc"],
                    period_end_utc=case["period_end_utc"],
                )
                unit = resolve_timestamp_unit(period)
                self.assertEqual(unit.value, case["expected_raw_unit"])
                actual = normalize_timestamp_pair(
                    case["raw_open_time"],
                    case["raw_close_time"],
                    unit,
                )
                self.assertEqual(
                    actual,
                    (
                        case["expected_open_time_ms"],
                        case["expected_close_time_ms"],
                    ),
                )
                reconcile_timestamp_to_period(*actual, period)

    def test_wrong_microsecond_open_remainder(self) -> None:
        with self.assertRaises(SourceProfileError) as context:
            normalize_timestamp_pair(
                1_735_689_600_000_001,
                1_735_689_659_999_999,
                TimestampUnit.MICROSECOND,
            )
        self.assertEqual(
            context.exception.reason_code,
            "RCC_SOURCE_TIMESTAMP_OPEN_REMAINDER",
        )

    def test_wrong_microsecond_close_remainder(self) -> None:
        with self.assertRaises(SourceProfileError) as context:
            normalize_timestamp_pair(
                1_735_689_600_000_000,
                1_735_689_659_999_998,
                TimestampUnit.MICROSECOND,
            )
        self.assertEqual(
            context.exception.reason_code,
            "RCC_SOURCE_TIMESTAMP_CLOSE_REMAINDER",
        )

    def test_selected_unit_mismatch_rejected(self) -> None:
        cases = (
            (
                1_735_689_600_000,
                1_735_689_659_999,
                TimestampUnit.MICROSECOND,
            ),
            (
                1_735_603_200_000_000,
                1_735_603_259_999_999,
                TimestampUnit.MILLISECOND,
            ),
        )
        for raw_open, raw_close, unit in cases:
            with self.subTest(unit=unit):
                with self.assertRaises(SourceProfileError) as context:
                    normalize_timestamp_pair(raw_open, raw_close, unit)
                self.assertEqual(
                    context.exception.reason_code,
                    "RCC_SOURCE_TIMESTAMP_UNIT_MISMATCH",
                )


if __name__ == "__main__":
    unittest.main()

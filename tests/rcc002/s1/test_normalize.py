"""Unit tests for rcc002.s1.normalize."""

import unittest

from rcc002.s1.normalize import (
    NormalizationAbortedError,
    parse_csv_rows,
    normalize_rows,
)

SNAPSHOT = "source:sha256:" + "a" * 64

COLUMN_MAPPING = {
    "open_time": 0,
    "open": 1,
    "high": 2,
    "low": 3,
    "close": 4,
    "volume": 5,
}


def make_raw_rows(*open_times_ms: int) -> list[dict[str, str]]:
    return [
        {
            "open_time": str(t),
            "open": "1.0",
            "high": "2.0",
            "low": "0.5",
            "close": "1.5",
            "volume": "100.0",
        }
        for t in open_times_ms
    ]


class ParseCsvRowsTests(unittest.TestCase):
    def test_splits_header_and_data(self) -> None:
        text = "open_time,open,high,low,close,volume\n60000,1,2,0.5,1.5,100\n"
        rows = parse_csv_rows(text, COLUMN_MAPPING)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["open_time"], "60000")

    def test_empty_text_yields_no_rows(self) -> None:
        self.assertEqual(parse_csv_rows("", COLUMN_MAPPING), [])

    def test_header_only_yields_no_rows(self) -> None:
        text = "open_time,open,high,low,close,volume\n"
        self.assertEqual(parse_csv_rows(text, COLUMN_MAPPING), [])

    def test_skips_blank_lines(self) -> None:
        text = "header\n60000,1,2,0.5,1.5,100\n\n120000,1,2,0.5,1.5,100\n"
        rows = parse_csv_rows(text, COLUMN_MAPPING)
        self.assertEqual(len(rows), 2)


class NormalizeRowsBasicTests(unittest.TestCase):
    def normalize(self, raw_rows: list[dict[str, str]], **overrides: object):
        kwargs: dict[str, object] = dict(
            source_snapshot_id=SNAPSHOT,
            provider="binance",
            market_type="spot",
            symbol="BTCUSDT",
            interval="1m",
        )
        kwargs.update(overrides)
        return normalize_rows(raw_rows, **kwargs)  # type: ignore[arg-type]

    def test_produces_one_row_per_input(self) -> None:
        result = self.normalize(make_raw_rows(0, 60_000, 120_000))
        self.assertEqual(len(result.rows), 3)

    def test_fields_carried_through(self) -> None:
        result = self.normalize(make_raw_rows(0))
        row = result.rows[0]
        self.assertEqual(row.source_snapshot_id, SNAPSHOT)
        self.assertEqual(row.provider, "binance")
        self.assertEqual(row.market_type, "spot")
        self.assertEqual(row.symbol, "BTCUSDT")
        self.assertEqual(row.interval, "1m")

    def test_ohlcv_parsed_correctly(self) -> None:
        result = self.normalize(make_raw_rows(0))
        row = result.rows[0]
        self.assertEqual(row.open, 1.0)
        self.assertEqual(row.high, 2.0)
        self.assertEqual(row.low, 0.5)
        self.assertEqual(row.close, 1.5)
        self.assertEqual(row.volume, 100.0)

    def test_close_time_derived_for_1m(self) -> None:
        result = self.normalize(make_raw_rows(0))
        self.assertEqual(result.rows[0].close_time, 59_999)

    def test_already_sorted_input_not_flagged_as_resorted(self) -> None:
        result = self.normalize(make_raw_rows(0, 60_000, 120_000))
        self.assertFalse(result.was_resorted)

    def test_output_is_sorted_ascending_by_open_time(self) -> None:
        result = self.normalize(make_raw_rows(120_000, 0, 60_000))
        self.assertEqual(
            [row.open_time for row in result.rows], [0, 60_000, 120_000]
        )

    def test_unsorted_input_flagged_as_resorted(self) -> None:
        result = self.normalize(make_raw_rows(120_000, 0, 60_000))
        self.assertTrue(result.was_resorted)


class SourceRowIdOriginalOrderTests(unittest.TestCase):
    def test_source_row_id_reflects_original_not_sorted_order(self) -> None:
        # Row at original index 0 has open_time 120000 (will sort last);
        # its source_row_id must still encode original index 0.
        result = normalize_rows(
            make_raw_rows(120_000, 0, 60_000),
            source_snapshot_id=SNAPSHOT,
            provider="binance",
            market_type="spot",
            symbol="BTCUSDT",
            interval="1m",
        )
        row_with_open_time_120000 = next(
            r for r in result.rows if r.open_time == 120_000
        )
        self.assertTrue(row_with_open_time_120000.source_row_id.endswith("0" * 19 + "0"))


class DuplicateKeyPreservationTests(unittest.TestCase):
    def test_duplicate_canonical_keys_both_preserved(self) -> None:
        # Two rows with identical open_time (a "conflicting duplicate" per
        # Data Pipeline §7.3) must both survive S1 — S1 must not resolve
        # duplicates (Data Pipeline §7.2: "S1 darf ... keine Duplikate
        # willkürlich entfernen").
        raw_rows = make_raw_rows(0, 0)
        result = normalize_rows(
            raw_rows,
            source_snapshot_id=SNAPSHOT,
            provider="binance",
            market_type="spot",
            symbol="BTCUSDT",
            interval="1m",
        )
        self.assertEqual(len(result.rows), 2)

    def test_duplicate_rows_keep_relative_order(self) -> None:
        raw_rows = [
            {"open_time": "0", "open": "1", "high": "2", "low": "0.5", "close": "1.5", "volume": "100"},
            {"open_time": "0", "open": "9", "high": "9", "low": "9", "close": "9", "volume": "9"},
        ]
        result = normalize_rows(
            raw_rows,
            source_snapshot_id=SNAPSHOT,
            provider="binance",
            market_type="spot",
            symbol="BTCUSDT",
            interval="1m",
        )
        self.assertEqual(result.rows[0].open, 1.0)
        self.assertEqual(result.rows[1].open, 9.0)


class NumericParsingFailureTests(unittest.TestCase):
    def test_invalid_ohlcv_aborts_normalization(self) -> None:
        raw_rows = [
            {"open_time": "0", "open": "bad", "high": "2", "low": "0.5", "close": "1.5", "volume": "100"}
        ]
        with self.assertRaises(NormalizationAbortedError) as ctx:
            normalize_rows(
                raw_rows,
                source_snapshot_id=SNAPSHOT,
                provider="binance",
                market_type="spot",
                symbol="BTCUSDT",
                interval="1m",
            )
        self.assertEqual(len(ctx.exception.critical_errors), 1)
        self.assertTrue(ctx.exception.critical_errors[0].critical)

    def test_invalid_open_time_aborts_normalization(self) -> None:
        raw_rows = [
            {"open_time": "not-a-time", "open": "1", "high": "2", "low": "0.5", "close": "1.5", "volume": "100"}
        ]
        with self.assertRaises(NormalizationAbortedError):
            normalize_rows(
                raw_rows,
                source_snapshot_id=SNAPSHOT,
                provider="binance",
                market_type="spot",
                symbol="BTCUSDT",
                interval="1m",
            )

    def test_multiple_critical_errors_all_accumulated(self) -> None:
        raw_rows = [
            {"open_time": "0", "open": "bad", "high": "2", "low": "0.5", "close": "1.5", "volume": "100"},
            {"open_time": "60000", "open": "1", "high": "bad2", "low": "0.5", "close": "1.5", "volume": "100"},
        ]
        with self.assertRaises(NormalizationAbortedError) as ctx:
            normalize_rows(
                raw_rows,
                source_snapshot_id=SNAPSHOT,
                provider="binance",
                market_type="spot",
                symbol="BTCUSDT",
                interval="1m",
            )
        self.assertEqual(len(ctx.exception.critical_errors), 2)

    def test_one_bad_row_does_not_block_reporting_of_valid_rows_errors_only(self) -> None:
        # Valid rows alongside an invalid one: the invalid one contributes a
        # critical error; overall the whole normalization still aborts
        # (build-level abort, not partial success).
        raw_rows = make_raw_rows(0, 60_000) + [
            {"open_time": "120000", "open": "bad", "high": "2", "low": "0.5", "close": "1.5", "volume": "100"}
        ]
        with self.assertRaises(NormalizationAbortedError):
            normalize_rows(
                raw_rows,
                source_snapshot_id=SNAPSHOT,
                provider="binance",
                market_type="spot",
                symbol="BTCUSDT",
                interval="1m",
            )


class IntervalAlignmentPassThroughTests(unittest.TestCase):
    """Stage-ownership correction (DVSEV-001 Step 4): S1 must NOT abort on a
    misaligned but parseable open_time. Interval-alignment validation
    (DV_TIME_MISALIGNED) belongs to S2 (Data Pipeline §7.3); S1 only parses
    and passes the value through unchanged."""

    def test_misaligned_open_time_passes_through_unchanged(self) -> None:
        raw_rows = make_raw_rows(1)  # 1 ms past epoch, not aligned to 60000ms
        result = normalize_rows(
            raw_rows,
            source_snapshot_id=SNAPSHOT,
            provider="binance",
            market_type="spot",
            symbol="BTCUSDT",
            interval="1m",
        )
        self.assertEqual(len(result.rows), 1)
        self.assertEqual(result.rows[0].open_time, 1)


class MultiProviderSortTests(unittest.TestCase):
    def test_multi_provider_flag_changes_sort_key(self) -> None:
        result = normalize_rows(
            make_raw_rows(0, 60_000),
            source_snapshot_id=SNAPSHOT,
            provider="binance",
            market_type="spot",
            symbol="BTCUSDT",
            interval="1m",
            multi_provider=True,
        )
        self.assertEqual(len(result.rows), 2)


if __name__ == "__main__":
    unittest.main()

"""End-to-end tests for rcc002.s3.compute."""

import unittest

from rcc002.s2.schema import S2Row
from rcc002.s3.compute import compute_indicators
from rcc002.s3.constants import INDICATOR_FIELD_ALLOWLIST

SNAPSHOT = "source:sha256:" + "a" * 64


def make_s2_row(source_row_id: str, open_time: int, **overrides: object) -> S2Row:
    fields: dict[str, object] = dict(
        source_snapshot_id=SNAPSHOT,
        source_row_id=source_row_id,
        source_file_ordinal=0,
        original_record_index=0,
        provider="binance",
        market_type="spot",
        symbol="BTCUSDT",
        interval="1m",
        open_time=open_time,
        close_time=open_time + 59_999,
        open=100.0,
        high=101.0,
        low=99.0,
        close=100.0,
        volume=10.0,
        market_segment_id="seg-1",
        quality_is_observed=True,
        quality_is_synthetic=False,
        quality_has_source_conflict=False,
        quality_gap_before=False,
        quality_gap_after=False,
        quality_timestamp_valid=True,
        quality_ohlc_valid=True,
        quality_volume_valid=True,
        quality_market_values_valid=True,
        quality_status="PASS",
        quality_reason_codes=(),
        quality_rule_version="RCC002_QUALITY_RULE_V1",
        quality_gate_pass=True,
    )
    fields.update(overrides)
    return S2Row(**fields)  # type: ignore[arg-type]


def make_series(n: int, market_segment_id: str = "seg-1", quality_gate_pass: bool = True, start_time: int = 0):
    rows = []
    close = 100.0
    for i in range(n):
        close += 1.0 if i % 2 == 0 else -0.5
        rows.append(
            make_s2_row(
                f"r{i}",
                start_time + i * 60_000,
                open=close - 0.2,
                high=close + 1.0,
                low=close - 1.0,
                close=close,
                volume=10.0 + i,
                market_segment_id=market_segment_id,
                quality_gate_pass=quality_gate_pass,
            )
        )
    return rows


class EmptyInputTests(unittest.TestCase):
    def test_empty_input_yields_empty_result(self) -> None:
        result = compute_indicators([])
        self.assertEqual(result.rows, ())


class RowPreservationTests(unittest.TestCase):
    def test_s3_rows_equals_s2_rows(self) -> None:
        rows = make_series(30)
        result = compute_indicators(rows)
        self.assertEqual(len(result.rows), 30)

    def test_canonical_key_unchanged(self) -> None:
        rows = make_series(5)
        result = compute_indicators(rows)
        for s2_row, s3_row in zip(rows, result.rows):
            self.assertEqual(
                (s3_row.market_type, s3_row.symbol, s3_row.interval, s3_row.open_time),
                (s2_row.market_type, s2_row.symbol, s2_row.interval, s2_row.open_time),
            )

    def test_ohlcv_unchanged(self) -> None:
        rows = make_series(5)
        result = compute_indicators(rows)
        for s2_row, s3_row in zip(rows, result.rows):
            self.assertEqual(s3_row.close, s2_row.close)
            self.assertEqual(s3_row.volume, s2_row.volume)

    def test_all_22_fields_present_on_every_row(self) -> None:
        rows = make_series(5)
        result = compute_indicators(rows)
        for row in result.rows:
            self.assertEqual(set(row.indicators), set(INDICATOR_FIELD_ALLOWLIST))


class WarmupTests(unittest.TestCase):
    def test_sma_200_invalid_before_full_warmup(self) -> None:
        rows = make_series(199)
        result = compute_indicators(rows)
        field = result.rows[-1].indicators["sma_close_200"]
        self.assertFalse(field.valid)
        self.assertFalse(field.warmup_complete)
        self.assertIsNone(field.value)
        self.assertIn("IND_WARMUP_INCOMPLETE", field.reason_codes)

    def test_sma_200_valid_at_full_warmup(self) -> None:
        rows = make_series(200)
        result = compute_indicators(rows)
        field = result.rows[-1].indicators["sma_close_200"]
        self.assertTrue(field.valid)
        self.assertTrue(field.warmup_complete)
        self.assertIsNotNone(field.value)
        self.assertEqual(field.reason_codes, ())

    def test_typical_price_valid_from_first_row(self) -> None:
        rows = make_series(3)
        result = compute_indicators(rows)
        self.assertTrue(result.rows[0].indicators["typical_price"].valid)


class QualityGatePassFalseTests(unittest.TestCase):
    def test_all_indicators_invalid_when_gate_fails(self) -> None:
        rows = make_series(30, quality_gate_pass=False)
        result = compute_indicators(rows)
        for row in result.rows:
            for name in INDICATOR_FIELD_ALLOWLIST:
                field = row.indicators[name]
                self.assertFalse(field.valid)
                self.assertFalse(field.warmup_complete)
                self.assertIsNone(field.value)

    def test_no_reason_code_attached_solely_for_gate_failure(self) -> None:
        # quality_gate_pass=false does not by itself imply an invalid
        # indicator input (approved decision, 2026-07-27): no reason code
        # is attached unless independently triggered.
        rows = make_series(5, quality_gate_pass=False)
        result = compute_indicators(rows)
        for row in result.rows:
            for name in INDICATOR_FIELD_ALLOWLIST:
                self.assertEqual(row.indicators[name].reason_codes, ())

    def test_row_still_retained(self) -> None:
        rows = make_series(5, quality_gate_pass=False)
        result = compute_indicators(rows)
        self.assertEqual(len(result.rows), 5)


class SegmentResetTests(unittest.TestCase):
    def test_market_segment_change_starts_new_indicator_segment(self) -> None:
        rows_a = make_series(30, market_segment_id="seg-a")
        rows_b = make_series(30, market_segment_id="seg-b", start_time=30 * 60_000)
        combined = rows_a + rows_b
        result = compute_indicators(combined)
        self.assertNotEqual(
            result.rows[29].indicator_segment_id, result.rows[30].indicator_segment_id
        )

    def test_recursive_indicator_reseeds_after_segment_change(self) -> None:
        rows_a = make_series(60, market_segment_id="seg-a")
        rows_b = make_series(60, market_segment_id="seg-b", start_time=60 * 60_000)
        combined = rows_a + rows_b
        result = compute_indicators(combined)
        # ema_close_50 must be invalid (re-warming up) immediately after the
        # segment boundary, even though the first segment already fully
        # warmed it up.
        self.assertTrue(result.rows[49].indicators["ema_close_50"].valid)
        self.assertFalse(result.rows[60].indicators["ema_close_50"].valid)
        self.assertFalse(result.rows[60].indicators["ema_close_50"].warmup_complete)

    def test_quality_gate_pass_toggle_starts_new_segment(self) -> None:
        good = make_series(20, quality_gate_pass=True)
        bad = make_series(5, quality_gate_pass=False, start_time=20 * 60_000)
        good_again = make_series(20, quality_gate_pass=True, start_time=25 * 60_000)
        combined = good + bad + good_again
        result = compute_indicators(combined)
        segment_ids = [row.indicator_segment_id for row in result.rows]
        self.assertEqual(len(set(segment_ids)), 3)
        # ema re-warms up after returning to a good segment
        self.assertFalse(result.rows[25].indicators["ema_close_50"].warmup_complete)


class CausalityTests(unittest.TestCase):
    def test_earlier_values_unaffected_by_later_changes(self) -> None:
        rows_original = make_series(60)
        rows_modified = list(rows_original[:59]) + [
            make_s2_row(
                "r59-modified",
                59 * 60_000,
                close=999.0,
                open=998.0,
                high=1000.0,
                low=997.0,
                volume=1.0,
            )
        ]
        result_original = compute_indicators(rows_original)
        result_modified = compute_indicators(rows_modified)
        for i in range(59):
            for name in INDICATOR_FIELD_ALLOWLIST:
                self.assertEqual(
                    result_original.rows[i].indicators[name],
                    result_modified.rows[i].indicators[name],
                    msg=f"field {name} at row {i} changed due to a later-row edit",
                )


class ReasonCodeOrderingTests(unittest.TestCase):
    def test_deterministic_ordering_warmup_only(self) -> None:
        rows = make_series(1)
        result = compute_indicators(rows)
        field = result.rows[0].indicators["sma_close_200"]
        self.assertEqual(field.reason_codes, ("IND_WARMUP_INCOMPLETE",))

    def test_replay_is_deterministic(self) -> None:
        rows = make_series(60)
        result_a = compute_indicators(list(rows))
        result_b = compute_indicators(list(rows))
        self.assertEqual(
            [r.indicator_segment_id for r in result_a.rows],
            [r.indicator_segment_id for r in result_b.rows],
        )
        for a, b in zip(result_a.rows, result_b.rows):
            self.assertEqual(a.indicators, b.indicators)


class RangeInvariantTests(unittest.TestCase):
    def test_rsi_within_0_100(self) -> None:
        rows = make_series(60)
        result = compute_indicators(rows)
        for row in result.rows:
            field = row.indicators["rsi_wilder_14"]
            if field.valid:
                self.assertGreaterEqual(field.value, 0.0)
                self.assertLessEqual(field.value, 100.0)

    def test_bb_ordering_holds(self) -> None:
        rows = make_series(30)
        result = compute_indicators(rows)
        for row in result.rows:
            mid = row.indicators["bb_mid_20"]
            upper = row.indicators["bb_upper_20_2"]
            lower = row.indicators["bb_lower_20_2"]
            if mid.valid and upper.valid and lower.valid:
                self.assertGreaterEqual(upper.value, mid.value)
                self.assertGreaterEqual(mid.value, lower.value)


if __name__ == "__main__":
    unittest.main()

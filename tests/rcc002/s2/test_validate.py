"""Unit and end-to-end tests for rcc002.s2.validate."""

import unittest

from rcc002.reason_codes import QUALITY_RULE_VERSION
from rcc002.s1.normalize import normalize_rows
from rcc002.s1.schema import S1Row
from rcc002.s2.anomalies import AnomalyThresholds
from rcc002.s2.duplicates import ConflictingDuplicatesWithoutResolutionRuleError
from rcc002.s2.validate import MixedSeriesInputError, validate_rows

SNAPSHOT = "source:sha256:" + "a" * 64


def make_row(source_row_id: str, open_time: int, **overrides: object) -> S1Row:
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
        open=1.0,
        high=2.0,
        low=0.5,
        close=1.5,
        volume=100.0,
    )
    fields.update(overrides)
    return S1Row(**fields)  # type: ignore[arg-type]


class EmptyInputTests(unittest.TestCase):
    def test_empty_input_yields_empty_result(self) -> None:
        result = validate_rows([])
        self.assertEqual(result.rows, ())
        self.assertEqual(result.reconciliation.s1_input_rows, 0)


class MixedSeriesTests(unittest.TestCase):
    def test_mixed_symbols_raise(self) -> None:
        rows = [make_row("r0", 0), make_row("r1", 60_000, symbol="ETHUSDT")]
        with self.assertRaises(MixedSeriesInputError):
            validate_rows(rows)


class RowPreservationTests(unittest.TestCase):
    def test_all_valid_rows_pass_through(self) -> None:
        rows = [make_row("r0", 0), make_row("r1", 60_000)]
        result = validate_rows(rows)
        self.assertEqual(len(result.rows), 2)

    def test_invalid_rows_are_retained_not_dropped(self) -> None:
        # OHLC-invalid row must still appear in output, marked accordingly.
        rows = [make_row("r0", 0, open=-1.0)]
        result = validate_rows(rows)
        self.assertEqual(len(result.rows), 1)
        self.assertFalse(result.rows[0].quality_gate_pass)

    def test_source_snapshot_id_propagated_unchanged(self) -> None:
        rows = [make_row("r0", 0)]
        result = validate_rows(rows)
        self.assertEqual(result.rows[0].source_snapshot_id, SNAPSHOT)


class TimestampValidationTests(unittest.TestCase):
    def test_aligned_row_has_no_misalignment_code(self) -> None:
        rows = [make_row("r0", 0)]
        result = validate_rows(rows)
        self.assertNotIn("DV_TIME_MISALIGNED", result.rows[0].quality_reason_codes)
        self.assertTrue(result.rows[0].quality_timestamp_valid)

    def test_misaligned_row_flagged_critical_and_retained(self) -> None:
        rows = [make_row("r0", 1)]  # 1 ms past epoch, not aligned to 60000ms
        result = validate_rows(rows)
        self.assertEqual(len(result.rows), 1)
        self.assertIn("DV_TIME_MISALIGNED", result.rows[0].quality_reason_codes)
        self.assertFalse(result.rows[0].quality_timestamp_valid)
        self.assertEqual(result.rows[0].quality_status, "CRITICAL")
        self.assertFalse(result.rows[0].quality_gate_pass)

    def test_out_of_range_row_flagged_error_and_retained(self) -> None:
        rows = [make_row("r0", 0), make_row("r1", 60_000), make_row("r2", 120_000)]
        result = validate_rows(rows, expected_start_ms=60_000, expected_end_ms=120_000)
        by_id = {row.source_row_id: row for row in result.rows}
        self.assertIn("DV_TIME_OUT_OF_RANGE", by_id["r0"].quality_reason_codes)
        self.assertEqual(result.reconciliation.out_of_range_rows, 1)
        self.assertEqual(result.reconciliation.in_range_rows, 2)
        self.assertEqual(len(result.rows), 3)  # retained, not dropped

    def test_in_range_row_not_flagged(self) -> None:
        rows = [make_row("r0", 60_000)]
        result = validate_rows(rows, expected_start_ms=60_000, expected_end_ms=120_000)
        self.assertNotIn("DV_TIME_OUT_OF_RANGE", result.rows[0].quality_reason_codes)


class EndToEndS1S2AlignmentTests(unittest.TestCase):
    """Proves the DVSEV-001 stage-ownership correction end-to-end: S1 must
    pass a misaligned row through unchanged, and S2 must be the one that
    flags it with DV_TIME_MISALIGNED."""

    def test_misaligned_row_survives_s1_and_is_flagged_in_s2(self) -> None:
        raw_rows = [
            {
                "open_time": "1",  # misaligned: 1 % 60000 != 0
                "open": "1.0",
                "high": "2.0",
                "low": "0.5",
                "close": "1.5",
                "volume": "100.0",
            }
        ]
        s1_result = normalize_rows(
            raw_rows,
            source_snapshot_id=SNAPSHOT,
            provider="binance",
            market_type="spot",
            symbol="BTCUSDT",
            interval="1m",
        )
        self.assertEqual(len(s1_result.rows), 1)
        self.assertEqual(s1_result.rows[0].open_time, 1)

        s2_result = validate_rows(s1_result.rows)
        self.assertEqual(len(s2_result.rows), 1)
        self.assertIn("DV_TIME_MISALIGNED", s2_result.rows[0].quality_reason_codes)
        self.assertEqual(s2_result.rows[0].quality_status, "CRITICAL")
        self.assertFalse(s2_result.rows[0].quality_gate_pass)
        self.assertEqual(s2_result.rows[0].open_time, 1)  # unchanged


class DuplicateHandlingTests(unittest.TestCase):
    def test_identical_duplicate_collapses_and_flags_info(self) -> None:
        rows = [make_row("r1", 0), make_row("r0", 0)]
        result = validate_rows(rows)
        self.assertEqual(len(result.rows), 1)
        self.assertEqual(result.rows[0].source_row_id, "r0")
        self.assertIn("DV_DUPLICATE_IDENTICAL_COLLAPSED", result.rows[0].quality_reason_codes)
        self.assertEqual(result.reconciliation.duplicate_rows_removed, 1)

    def test_conflicting_duplicate_without_rule_aborts(self) -> None:
        rows = [make_row("r0", 0, close=1.5), make_row("r1", 0, close=9.9)]
        with self.assertRaises(ConflictingDuplicatesWithoutResolutionRuleError):
            validate_rows(rows)

    def test_conflicting_duplicate_with_rule_resolves_and_flags_info(self) -> None:
        rows = [make_row("r0", 0, close=1.5), make_row("r1", 0, close=9.9)]
        result = validate_rows(
            rows, conflict_resolution_rule=lambda group: max(group, key=lambda r: r.close)
        )
        self.assertEqual(len(result.rows), 1)
        row = result.rows[0]
        self.assertEqual(row.source_row_id, "r1")
        self.assertIn("DV_SOURCE_CONFLICT_RESOLVED", row.quality_reason_codes)
        self.assertFalse(row.quality_has_source_conflict)


class GapAndSegmentTests(unittest.TestCase):
    """DV_GAP_DETECTED/DV_GAP_UNEXPLAINED attach exclusively to the first
    row after the gap (approved implementation-level binding, 2026-07-27),
    never to the row before it, never to both."""

    def test_gap_produces_two_segments(self) -> None:
        rows = [make_row("r0", 0), make_row("r1", 180_000)]
        result = validate_rows(rows)
        by_id = {row.source_row_id: row for row in result.rows}
        self.assertNotEqual(by_id["r0"].market_segment_id, by_id["r1"].market_segment_id)
        self.assertTrue(by_id["r0"].quality_gap_after)
        self.assertTrue(by_id["r1"].quality_gap_before)

    def test_gap_codes_attach_only_to_first_post_gap_row(self) -> None:
        rows = [make_row("r0", 0), make_row("r1", 180_000)]
        result = validate_rows(rows)
        by_id = {row.source_row_id: row for row in result.rows}
        self.assertIn("DV_GAP_DETECTED", by_id["r1"].quality_reason_codes)
        self.assertIn("DV_GAP_UNEXPLAINED", by_id["r1"].quality_reason_codes)
        self.assertIn("DV_TIME_GAP_SEGMENT_STARTED", by_id["r1"].quality_reason_codes)

    def test_gap_codes_not_attached_to_pre_gap_row(self) -> None:
        rows = [make_row("r0", 0), make_row("r1", 180_000)]
        result = validate_rows(rows)
        by_id = {row.source_row_id: row for row in result.rows}
        self.assertNotIn("DV_GAP_DETECTED", by_id["r0"].quality_reason_codes)
        self.assertNotIn("DV_GAP_UNEXPLAINED", by_id["r0"].quality_reason_codes)
        self.assertNotIn("DV_TIME_GAP_SEGMENT_STARTED", by_id["r0"].quality_reason_codes)

    def test_contiguous_rows_no_gap_codes(self) -> None:
        rows = [make_row("r0", 0), make_row("r1", 60_000)]
        result = validate_rows(rows)
        for row in result.rows:
            self.assertNotIn("DV_GAP_DETECTED", row.quality_reason_codes)
            self.assertNotIn("DV_TIME_GAP_SEGMENT_STARTED", row.quality_reason_codes)


class OhlcvInvariantIntegrationTests(unittest.TestCase):
    def test_ohlc_violation_flagged_critical(self) -> None:
        rows = [make_row("r0", 0, high=0.1, low=0.5)]
        result = validate_rows(rows)
        self.assertIn("DV_OHLC_INVARIANT_FAILED", result.rows[0].quality_reason_codes)
        self.assertEqual(result.rows[0].quality_status, "CRITICAL")

    def test_negative_volume_flagged_critical(self) -> None:
        rows = [make_row("r0", 0, volume=-5.0)]
        result = validate_rows(rows)
        self.assertIn("DV_VOLUME_NEGATIVE", result.rows[0].quality_reason_codes)

    def test_zero_volume_flagged_warn_and_gate_blocked(self) -> None:
        rows = [make_row("r0", 0, volume=0.0)]
        result = validate_rows(rows)
        self.assertIn("DV_VOLUME_ZERO_OBSERVED", result.rows[0].quality_reason_codes)
        self.assertEqual(result.rows[0].quality_status, "WARN")
        # No WARN-whitelisting profile exists yet (§25.1 open parameter) —
        # fail-closed default: any active WARN blocks quality_gate_pass.
        self.assertFalse(result.rows[0].quality_gate_pass)


class AnomalyIntegrationTests(unittest.TestCase):
    def test_anomalies_not_computed_without_thresholds(self) -> None:
        rows = [make_row("r0", 0, close=1.0), make_row("r1", 60_000, close=100.0)]
        result = validate_rows(rows)
        for row in result.rows:
            self.assertFalse(any(code.startswith("DV_ANOMALY_") for code in row.quality_reason_codes))

    def test_anomalies_computed_when_thresholds_given(self) -> None:
        thresholds = AnomalyThresholds(
            extreme_candle_return_abs=0.5,
            extreme_high_low_range_abs=0.5,
            extreme_volume_abs=1000.0,
            zero_volume_cluster_min_length=3,
            repeated_identical_ohlc_min_length=3,
        )
        rows = [make_row("r0", 0, close=1.0), make_row("r1", 60_000, close=100.0)]
        result = validate_rows(rows, anomaly_thresholds=thresholds)
        by_id = {row.source_row_id: row for row in result.rows}
        self.assertIn("DV_ANOMALY_EXTREME_CANDLE_RETURN", by_id["r1"].quality_reason_codes)


class QualityStatusAndGatePassTests(unittest.TestCase):
    def test_no_findings_is_pass_and_gate_true(self) -> None:
        rows = [make_row("r0", 0)]
        result = validate_rows(rows)
        self.assertEqual(result.rows[0].quality_status, "PASS")
        self.assertTrue(result.rows[0].quality_gate_pass)

    def test_info_only_findings_is_pass(self) -> None:
        # Identical duplicate collapse -> DV_DUPLICATE_IDENTICAL_COLLAPSED (INFO) only
        rows = [make_row("r1", 0), make_row("r0", 0)]
        result = validate_rows(rows)
        self.assertEqual(result.rows[0].quality_status, "PASS")
        self.assertTrue(result.rows[0].quality_gate_pass)

    def test_quality_rule_version_recorded_on_every_row(self) -> None:
        rows = [make_row("r0", 0)]
        result = validate_rows(rows)
        self.assertEqual(result.rows[0].quality_rule_version, QUALITY_RULE_VERSION)

    def test_reason_codes_deterministically_ordered(self) -> None:
        rows = [make_row("r0", 0, open=-1.0, volume=-1.0)]  # OHLC CRITICAL + volume CRITICAL
        result = validate_rows(rows)
        codes = result.rows[0].quality_reason_codes
        self.assertEqual(codes, tuple(sorted(codes, key=lambda c: c)) if len(set(codes)) < 2 else codes)
        # Both are CRITICAL; alphabetic tiebreak: DV_OHLC_INVARIANT_FAILED < DV_VOLUME_NEGATIVE
        self.assertEqual(codes, ("DV_OHLC_INVARIANT_FAILED", "DV_VOLUME_NEGATIVE"))


class ReconciliationTests(unittest.TestCase):
    def test_reconciliation_counts_without_range(self) -> None:
        rows = [make_row("r0", 0), make_row("r1", 60_000)]
        result = validate_rows(rows)
        recon = result.reconciliation
        self.assertEqual(recon.s1_input_rows, 2)
        self.assertEqual(recon.duplicate_rows_removed, 0)
        self.assertEqual(recon.s1_unique_valid_rows, 2)
        self.assertEqual(recon.s2_observed_rows, 2)

    def test_reconciliation_counts_with_range_and_gap(self) -> None:
        rows = [make_row("r0", 0), make_row("r1", 120_000)]  # missing 60_000
        result = validate_rows(rows, expected_start_ms=0, expected_end_ms=120_000)
        recon = result.reconciliation
        self.assertEqual(recon.expected_intervals, 3)
        self.assertEqual(recon.observed_unique_intervals, 2)
        self.assertEqual(recon.missing_intervals, 1)

    def test_reconciliation_accounts_for_collapsed_duplicates(self) -> None:
        rows = [make_row("r1", 0), make_row("r0", 0), make_row("r2", 60_000)]
        result = validate_rows(rows)
        self.assertEqual(result.reconciliation.s1_input_rows, 3)
        self.assertEqual(result.reconciliation.duplicate_rows_removed, 1)
        self.assertEqual(result.reconciliation.s2_observed_rows, 2)


class GapClassificationTests(unittest.TestCase):
    """DV_GAP_UNEXPLAINED (Step 4 completion): every detected gap is
    classified UNKNOWN by elimination (no evidence is modeled or invented)
    and, per the approved implementation-level binding, attaches — together
    with DV_GAP_DETECTED — exclusively to the first row after the gap."""

    def test_single_missing_interval(self) -> None:
        # r0 at 0, r1 at 120_000: exactly one missing interval (60_000).
        rows = [make_row("r0", 0), make_row("r1", 120_000)]
        result = validate_rows(rows)
        by_id = {row.source_row_id: row for row in result.rows}
        self.assertIn("DV_GAP_DETECTED", by_id["r1"].quality_reason_codes)
        self.assertIn("DV_GAP_UNEXPLAINED", by_id["r1"].quality_reason_codes)
        self.assertNotIn("DV_GAP_DETECTED", by_id["r0"].quality_reason_codes)
        self.assertNotIn("DV_GAP_UNEXPLAINED", by_id["r0"].quality_reason_codes)
        self.assertEqual(by_id["r1"].quality_status, "ERROR")
        self.assertFalse(by_id["r1"].quality_gate_pass)

    def test_multiple_consecutive_missing_intervals_form_one_gap(self) -> None:
        # r0 at 0, r1 at 240_000: three missing intervals (60k, 120k, 180k),
        # but still exactly one gap boundary -> exactly one flagged row.
        rows = [make_row("r0", 0), make_row("r1", 240_000)]
        result = validate_rows(rows)
        by_id = {row.source_row_id: row for row in result.rows}
        self.assertIn("DV_GAP_UNEXPLAINED", by_id["r1"].quality_reason_codes)
        self.assertNotIn("DV_GAP_UNEXPLAINED", by_id["r0"].quality_reason_codes)
        gap_flagged_rows = [
            row for row in result.rows if "DV_GAP_UNEXPLAINED" in row.quality_reason_codes
        ]
        self.assertEqual(len(gap_flagged_rows), 1)

    def test_multiple_distinct_gaps_each_flag_their_own_post_gap_row(self) -> None:
        # Gap 1 between r0(0) and r1(180_000); contiguous r1->r2(240_000);
        # gap 2 between r2(240_000) and r3(420_000).
        rows = [
            make_row("r0", 0),
            make_row("r1", 180_000),
            make_row("r2", 240_000),
            make_row("r3", 420_000),
        ]
        result = validate_rows(rows)
        by_id = {row.source_row_id: row for row in result.rows}
        self.assertIn("DV_GAP_UNEXPLAINED", by_id["r1"].quality_reason_codes)
        self.assertIn("DV_GAP_UNEXPLAINED", by_id["r3"].quality_reason_codes)
        self.assertNotIn("DV_GAP_UNEXPLAINED", by_id["r0"].quality_reason_codes)
        self.assertNotIn("DV_GAP_UNEXPLAINED", by_id["r2"].quality_reason_codes)
        gap_flagged_rows = [
            row for row in result.rows if "DV_GAP_UNEXPLAINED" in row.quality_reason_codes
        ]
        self.assertEqual(len(gap_flagged_rows), 2)

    def test_no_gap_data_emits_neither_code(self) -> None:
        rows = [make_row("r0", 0), make_row("r1", 60_000), make_row("r2", 120_000)]
        result = validate_rows(rows)
        for row in result.rows:
            self.assertNotIn("DV_GAP_DETECTED", row.quality_reason_codes)
            self.assertNotIn("DV_GAP_UNEXPLAINED", row.quality_reason_codes)

    def test_deterministic_replay(self) -> None:
        rows = [make_row("r0", 0), make_row("r1", 180_000), make_row("r2", 240_000)]
        result_a = validate_rows(list(rows))
        result_b = validate_rows(list(reversed(rows)))  # input order must not matter
        self.assertEqual(
            [(r.source_row_id, r.quality_reason_codes, r.market_segment_id, r.quality_status)
             for r in result_a.rows],
            [(r.source_row_id, r.quality_reason_codes, r.market_segment_id, r.quality_status)
             for r in result_b.rows],
        )

    def test_deterministic_reason_code_ordering_with_gap_and_other_code(self) -> None:
        # r1 is the first row after a gap AND has an OHLC invariant violation
        # (CRITICAL). Expected order: severity descending, then alphabetic:
        # CRITICAL (DV_OHLC_INVARIANT_FAILED) > ERROR (DV_GAP_UNEXPLAINED) >
        # WARN (DV_GAP_DETECTED) > INFO (DV_TIME_GAP_SEGMENT_STARTED).
        rows = [make_row("r0", 0), make_row("r1", 180_000, open=-1.0)]
        result = validate_rows(rows)
        by_id = {row.source_row_id: row for row in result.rows}
        self.assertEqual(
            by_id["r1"].quality_reason_codes,
            (
                "DV_OHLC_INVARIANT_FAILED",
                "DV_GAP_UNEXPLAINED",
                "DV_GAP_DETECTED",
                "DV_TIME_GAP_SEGMENT_STARTED",
            ),
        )
        self.assertEqual(by_id["r1"].quality_status, "CRITICAL")
        self.assertFalse(by_id["r1"].quality_gate_pass)

    def test_row_preservation_and_reconciliation_unchanged_by_gap(self) -> None:
        rows = [make_row("r0", 0), make_row("r1", 180_000)]
        result = validate_rows(rows)
        self.assertEqual(len(result.rows), 2)  # both rows retained, none dropped
        self.assertEqual(result.reconciliation.s1_input_rows, 2)
        self.assertEqual(result.reconciliation.s1_unique_valid_rows, 2)
        self.assertEqual(result.reconciliation.s2_observed_rows, 2)
        self.assertEqual(result.reconciliation.duplicate_rows_removed, 0)

    def test_severity_and_quality_status_derived_from_central_registry(self) -> None:
        from rcc002.reason_codes import REASON_CODE_SEVERITY, Severity, derive_quality_status

        self.assertEqual(REASON_CODE_SEVERITY["DV_GAP_UNEXPLAINED"], Severity.ERROR)
        rows = [make_row("r0", 0), make_row("r1", 180_000)]
        result = validate_rows(rows)
        by_id = {row.source_row_id: row for row in result.rows}
        self.assertEqual(
            derive_quality_status(by_id["r1"].quality_reason_codes),
            by_id["r1"].quality_status,
        )
        self.assertEqual(by_id["r1"].quality_status, "ERROR")
        self.assertFalse(by_id["r1"].quality_gate_pass)


if __name__ == "__main__":
    unittest.main()

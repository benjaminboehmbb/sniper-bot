"""Unit tests for rcc002.s2.anomalies."""

import unittest

from rcc002.s1.schema import S1Row
from rcc002.s2.anomalies import AnomalyThresholds, detect_anomalies

SNAPSHOT = "source:sha256:" + "a" * 64


def make_row(source_row_id: str, open_time: int, **overrides: object) -> S1Row:
    fields: dict[str, object] = dict(
        source_snapshot_id=SNAPSHOT,
        source_row_id=source_row_id,
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


THRESHOLDS = AnomalyThresholds(
    extreme_candle_return_abs=0.5,
    extreme_high_low_range_abs=0.5,
    extreme_volume_abs=1000.0,
    zero_volume_cluster_min_length=3,
    repeated_identical_ohlc_min_length=3,
)


class ExtremeCandleReturnTests(unittest.TestCase):
    def test_large_jump_flagged(self) -> None:
        rows = [make_row("r0", 0, close=1.0), make_row("r1", 60_000, close=10.0)]
        findings = detect_anomalies(rows, thresholds=THRESHOLDS, gap_before_by_source_row_id={})
        self.assertIn("r1", findings.extreme_candle_return)

    def test_small_change_not_flagged(self) -> None:
        rows = [make_row("r0", 0, close=1.0), make_row("r1", 60_000, close=1.01)]
        findings = detect_anomalies(rows, thresholds=THRESHOLDS, gap_before_by_source_row_id={})
        self.assertNotIn("r1", findings.extreme_candle_return)

    def test_first_row_never_flagged(self) -> None:
        rows = [make_row("r0", 0, close=1.0)]
        findings = detect_anomalies(rows, thresholds=THRESHOLDS, gap_before_by_source_row_id={})
        self.assertNotIn("r0", findings.extreme_candle_return)


class ExtremeHighLowRangeTests(unittest.TestCase):
    def test_wide_range_flagged(self) -> None:
        rows = [make_row("r0", 0, high=10.0, low=0.1, close=1.0)]
        findings = detect_anomalies(rows, thresholds=THRESHOLDS, gap_before_by_source_row_id={})
        self.assertIn("r0", findings.extreme_high_low_range)

    def test_narrow_range_not_flagged(self) -> None:
        rows = [make_row("r0", 0, high=1.1, low=0.9, close=1.0)]
        findings = detect_anomalies(rows, thresholds=THRESHOLDS, gap_before_by_source_row_id={})
        self.assertNotIn("r0", findings.extreme_high_low_range)


class ExtremeVolumeTests(unittest.TestCase):
    def test_huge_volume_flagged(self) -> None:
        rows = [make_row("r0", 0, volume=5000.0)]
        findings = detect_anomalies(rows, thresholds=THRESHOLDS, gap_before_by_source_row_id={})
        self.assertIn("r0", findings.extreme_volume)

    def test_normal_volume_not_flagged(self) -> None:
        rows = [make_row("r0", 0, volume=100.0)]
        findings = detect_anomalies(rows, thresholds=THRESHOLDS, gap_before_by_source_row_id={})
        self.assertNotIn("r0", findings.extreme_volume)


class ZeroVolumeClusterTests(unittest.TestCase):
    def test_cluster_at_or_above_min_length_flagged(self) -> None:
        rows = [
            make_row("r0", 0, volume=0.0),
            make_row("r1", 60_000, volume=0.0),
            make_row("r2", 120_000, volume=0.0),
        ]
        findings = detect_anomalies(rows, thresholds=THRESHOLDS, gap_before_by_source_row_id={})
        self.assertEqual(findings.zero_volume_cluster, frozenset({"r0", "r1", "r2"}))

    def test_shorter_run_not_flagged(self) -> None:
        rows = [
            make_row("r0", 0, volume=0.0),
            make_row("r1", 60_000, volume=0.0),
            make_row("r2", 120_000, volume=100.0),
        ]
        findings = detect_anomalies(rows, thresholds=THRESHOLDS, gap_before_by_source_row_id={})
        self.assertEqual(findings.zero_volume_cluster, frozenset())


class RepeatedIdenticalOhlcTests(unittest.TestCase):
    def test_repeated_run_flagged(self) -> None:
        rows = [make_row(f"r{i}", i * 60_000) for i in range(3)]
        findings = detect_anomalies(rows, thresholds=THRESHOLDS, gap_before_by_source_row_id={})
        self.assertEqual(findings.repeated_identical_ohlc, frozenset({"r0", "r1", "r2"}))

    def test_varying_ohlc_not_flagged(self) -> None:
        rows = [
            make_row("r0", 0, close=1.0),
            make_row("r1", 60_000, close=1.1),
            make_row("r2", 120_000, close=1.2),
        ]
        findings = detect_anomalies(rows, thresholds=THRESHOLDS, gap_before_by_source_row_id={})
        self.assertEqual(findings.repeated_identical_ohlc, frozenset())


class PartitionBoundaryJumpTests(unittest.TestCase):
    def test_jump_at_boundary_flagged(self) -> None:
        rows = [make_row("r0", 0, close=1.0), make_row("r1", 180_000, close=10.0)]
        findings = detect_anomalies(
            rows, thresholds=THRESHOLDS, gap_before_by_source_row_id={"r1": True}
        )
        self.assertIn("r1", findings.partition_boundary_jump)

    def test_jump_not_at_boundary_not_flagged_as_boundary_jump(self) -> None:
        rows = [make_row("r0", 0, close=1.0), make_row("r1", 60_000, close=10.0)]
        findings = detect_anomalies(
            rows, thresholds=THRESHOLDS, gap_before_by_source_row_id={"r1": False}
        )
        self.assertNotIn("r1", findings.partition_boundary_jump)
        self.assertIn("r1", findings.extreme_candle_return)  # still flagged as a plain return anomaly


if __name__ == "__main__":
    unittest.main()

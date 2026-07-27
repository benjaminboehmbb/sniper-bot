"""Unit tests for rcc002.s2.schema."""

import unittest

from rcc002.s2.schema import S2Row


def make_row(**overrides: object) -> S2Row:
    fields: dict[str, object] = dict(
        source_snapshot_id="source:sha256:" + "a" * 64,
        source_row_id="RCC002_S1_SOURCE_ROW_ID_V1:x:00000000000000000000",
        provider="binance",
        market_type="spot",
        symbol="BTCUSDT",
        interval="1m",
        open_time=0,
        close_time=59_999,
        open=1.0,
        high=2.0,
        low=0.5,
        close=1.5,
        volume=100.0,
        market_segment_id="RCC002_S2_MARKET_SEGMENT_ID_V1:1:deadbeef",
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


class S2RowConstructionTests(unittest.TestCase):
    def test_valid_row_constructs(self) -> None:
        row = make_row()
        self.assertEqual(row.symbol, "BTCUSDT")

    def test_is_frozen(self) -> None:
        row = make_row()
        with self.assertRaises(Exception):
            row.quality_gate_pass = False  # type: ignore[misc]

    def test_invalid_quality_status_rejected(self) -> None:
        with self.assertRaises(ValueError):
            make_row(quality_status="BOGUS")

    def test_quality_reason_codes_must_be_tuple(self) -> None:
        with self.assertRaises(ValueError):
            make_row(quality_reason_codes=["DV_GAP_DETECTED"])  # type: ignore[arg-type]

    def test_s1_fields_carried_through(self) -> None:
        row = make_row(open=3.5)
        self.assertEqual(row.open, 3.5)


if __name__ == "__main__":
    unittest.main()

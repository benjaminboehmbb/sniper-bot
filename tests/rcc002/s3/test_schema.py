"""Unit tests for rcc002.s3.schema."""

import unittest

from rcc002.s3.constants import INDICATOR_FIELD_ALLOWLIST
from rcc002.s3.schema import IndicatorField, S3Row


def make_indicators(**overrides: IndicatorField) -> dict[str, IndicatorField]:
    fields = {name: IndicatorField(None, False, False, ("IND_WARMUP_INCOMPLETE",)) for name in INDICATOR_FIELD_ALLOWLIST}
    fields.update(overrides)
    return fields


def make_row(**overrides: object) -> S3Row:
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
        market_segment_id="seg",
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
        indicator_profile_id="RCC002_CANONICAL_INDICATORS_V1",
        indicator_profile_version="1.0.0",
        indicator_schema_id="rcc002.stage.s3-indicators",
        indicator_schema_version="1.0.0",
        indicator_segment_id="ind-seg",
        indicators=make_indicators(),
    )
    fields.update(overrides)
    return S3Row(**fields)  # type: ignore[arg-type]


class IndicatorFieldTests(unittest.TestCase):
    def test_valid_field_constructs(self) -> None:
        field = IndicatorField(1.5, True, True, ())
        self.assertEqual(field.value, 1.5)

    def test_reason_codes_must_be_tuple(self) -> None:
        with self.assertRaises(ValueError):
            IndicatorField(None, False, False, ["IND_WARMUP_INCOMPLETE"])  # type: ignore[arg-type]

    def test_valid_field_cannot_have_none_value(self) -> None:
        with self.assertRaises(ValueError):
            IndicatorField(None, True, True, ())

    def test_invalid_field_cannot_have_a_value(self) -> None:
        with self.assertRaises(ValueError):
            IndicatorField(1.0, False, True, ("IND_WARMUP_INCOMPLETE",))


class S3RowTests(unittest.TestCase):
    def test_valid_row_constructs(self) -> None:
        row = make_row()
        self.assertEqual(row.symbol, "BTCUSDT")

    def test_is_frozen(self) -> None:
        row = make_row()
        with self.assertRaises(Exception):
            row.quality_gate_pass = False  # type: ignore[misc]

    def test_indicators_must_cover_exact_allowlist(self) -> None:
        incomplete = make_indicators()
        del incomplete["sma_close_200"]
        with self.assertRaises(ValueError):
            make_row(indicators=incomplete)

    def test_s2_fields_carried_through(self) -> None:
        row = make_row(close=42.0)
        self.assertEqual(row.close, 42.0)


if __name__ == "__main__":
    unittest.main()

"""Unit tests for rcc002.s1.schema."""

import unittest

from rcc002.s1.schema import (
    CANONICAL_PRIMARY_KEY_MULTI_PROVIDER,
    CANONICAL_PRIMARY_KEY_SINGLE_PROVIDER,
    S1ConflictingLegacyAliasError,
    S1Row,
    migrate_s1_legacy_aliases,
)


def make_row(**overrides: object) -> S1Row:
    fields: dict[str, object] = dict(
        source_snapshot_id="source:sha256:" + "a" * 64,
        source_row_id="RCC002_S1_SOURCE_ROW_ID_V1:x:00000000000000000000",
        provider="binance",
        market_type="spot",
        symbol="BTCUSDT",
        interval="1m",
        open_time=1_700_000_000_000,
        close_time=1_700_000_059_999,
        open=1.0,
        high=2.0,
        low=0.5,
        close=1.5,
        volume=100.0,
    )
    fields.update(overrides)
    return S1Row(**fields)  # type: ignore[arg-type]


class S1RowConstructionTests(unittest.TestCase):
    def test_valid_row_constructs(self) -> None:
        row = make_row()
        self.assertEqual(row.symbol, "BTCUSDT")

    def test_is_frozen(self) -> None:
        row = make_row()
        with self.assertRaises(Exception):
            row.symbol = "ETHUSDT"  # type: ignore[misc]

    def test_empty_provider_rejected(self) -> None:
        with self.assertRaises(ValueError):
            make_row(provider="")

    def test_open_time_must_be_int(self) -> None:
        with self.assertRaises(ValueError):
            make_row(open_time="1700000000000")  # type: ignore[arg-type]

    def test_open_time_rejects_bool(self) -> None:
        with self.assertRaises(ValueError):
            make_row(open_time=True)  # type: ignore[arg-type]

    def test_ohlcv_fields_must_be_float(self) -> None:
        with self.assertRaises(ValueError):
            make_row(open=1)  # type: ignore[arg-type]  # int, not float


class CanonicalKeyTests(unittest.TestCase):
    def test_single_provider_key_fields(self) -> None:
        self.assertEqual(
            CANONICAL_PRIMARY_KEY_SINGLE_PROVIDER,
            ("market_type", "symbol", "interval", "open_time"),
        )

    def test_multi_provider_key_fields(self) -> None:
        self.assertEqual(
            CANONICAL_PRIMARY_KEY_MULTI_PROVIDER,
            ("provider", "market_type", "symbol", "interval", "open_time"),
        )

    def test_canonical_key_single_provider(self) -> None:
        row = make_row()
        self.assertEqual(
            row.canonical_key(multi_provider=False),
            ("spot", "BTCUSDT", "1m", 1_700_000_000_000),
        )

    def test_canonical_key_multi_provider(self) -> None:
        row = make_row()
        self.assertEqual(
            row.canonical_key(multi_provider=True),
            ("binance", "spot", "BTCUSDT", "1m", 1_700_000_000_000),
        )


class LegacyAliasMigrationTests(unittest.TestCase):
    def test_migrates_source_id(self) -> None:
        result = migrate_s1_legacy_aliases({"source_id": "abc"})
        self.assertEqual(result, {"source_snapshot_id": "abc"})
        self.assertNotIn("source_id", result)

    def test_non_aliased_keys_unaffected(self) -> None:
        result = migrate_s1_legacy_aliases({"symbol": "BTCUSDT"})
        self.assertEqual(result, {"symbol": "BTCUSDT"})

    def test_conflicting_keys_raise(self) -> None:
        with self.assertRaises(S1ConflictingLegacyAliasError):
            migrate_s1_legacy_aliases(
                {"source_id": "abc", "source_snapshot_id": "def"}
            )


if __name__ == "__main__":
    unittest.main()

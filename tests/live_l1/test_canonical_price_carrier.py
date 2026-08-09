#!/usr/bin/env python3

from __future__ import annotations

import math
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

from live_l1.core.feature_snapshot import build_feature_snapshot
from live_l1.io.market import CSVMarketFeed, DummyMarketFeed, MarketSnapshot


CSV_HEADER = (
    "timestamp_utc,open,high,low,close,volume,"
    "allow_long,allow_short,regime_v2,rsi_signal\n"
)


def csv_row(close: str, *, minute: int = 0) -> str:
    return (
        f"2026-08-09T10:{minute:02d}:00Z,{close},{close},{close},{close},1,"
        "1,1,0,1\n"
    )


class CanonicalPriceCarrierTests(unittest.TestCase):
    def _feed(self, rows: str) -> CSVMarketFeed:
        temporary = tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".csv",
            delete=False,
        )
        self.addCleanup(Path(temporary.name).unlink, missing_ok=True)
        temporary.write(CSV_HEADER)
        temporary.write(rows)
        temporary.close()
        feed = CSVMarketFeed(temporary.name)
        self.addCleanup(feed.close)
        return feed

    def test_exact_source_price_survives_without_float_round_trip(self) -> None:
        raw_price = "12345.678901234567890123456789"
        snapshot = self._feed(csv_row(raw_price)).next_snapshot()
        features = build_feature_snapshot(snapshot)

        self.assertEqual(
            snapshot.reference_price_text,
            "12345.678901234567890123456789",
        )
        self.assertEqual(features.reference_price_text, snapshot.reference_price_text)
        self.assertEqual(Decimal(features.reference_price_text), Decimal(raw_price))
        self.assertNotEqual(Decimal(str(features.price)), Decimal(raw_price))

    def test_decimal_text_is_canonicalized_directly_from_source(self) -> None:
        snapshot = self._feed(csv_row("00100.12000")).next_snapshot()

        self.assertEqual(snapshot.reference_price_text, "100.12")
        self.assertEqual(snapshot.price, float("00100.12000"))
        self.assertEqual(snapshot.close, float("00100.12000"))

    def test_scientific_source_text_is_canonicalized_without_float(self) -> None:
        snapshot = self._feed(csv_row("1.2300E+2")).next_snapshot()

        self.assertEqual(snapshot.reference_price_text, "123")
        self.assertEqual(snapshot.price, 123.0)

    def test_invalid_or_nonpositive_source_is_not_economic_authority(self) -> None:
        feed = self._feed(
            csv_row("not-a-price", minute=0)
            + csv_row("0", minute=1)
            + csv_row("-1", minute=2)
            + csv_row("NaN", minute=3)
            + csv_row("Infinity", minute=4)
        )

        snapshots = [feed.next_snapshot() for _ in range(5)]

        self.assertEqual(
            [snapshot.reference_price_text for snapshot in snapshots],
            ["", "", "", "", ""],
        )
        self.assertEqual(snapshots[0].price, 0.0)
        self.assertEqual(snapshots[1].price, 0.0)
        self.assertEqual(snapshots[2].price, -1.0)
        self.assertTrue(math.isnan(snapshots[3].price))
        self.assertTrue(math.isinf(snapshots[4].price))

    def test_feature_builder_never_recreates_authority_from_float(self) -> None:
        legacy_snapshot = SimpleNamespace(
            snapshot_id="LEGACY-1",
            timestamp_utc="2026-08-09T10:00:00Z",
            symbol="BTCUSDT",
            price=12345.678901234567,
            open=12345.0,
            high=12346.0,
            low=12344.0,
            close=12345.678901234567,
            volume=1.0,
            allow_long=1,
            allow_short=1,
            regime_v2=0,
            signals={"rsi_signal": 1},
        )

        features = build_feature_snapshot(legacy_snapshot)

        self.assertEqual(features.reference_price_text, "")
        self.assertEqual(features.price, legacy_snapshot.price)
        self.assertEqual(features.signal("rsi_signal"), 1)

    def test_additive_market_field_preserves_old_constructor_contract(self) -> None:
        snapshot = MarketSnapshot(
            snapshot_id="MANUAL-1",
            timestamp_utc="2026-08-09T10:00:00Z",
            symbol="BTCUSDT",
            price=100.0,
            signals={},
        )

        self.assertEqual(snapshot.reference_price_text, "")
        self.assertEqual(build_feature_snapshot(snapshot).reference_price_text, "")

    def test_dummy_feed_exposes_deterministic_decimal_text(self) -> None:
        snapshot = DummyMarketFeed().next_snapshot()
        features = build_feature_snapshot(snapshot)

        self.assertEqual(snapshot.price, 101.0)
        self.assertEqual(snapshot.reference_price_text, "101")
        self.assertEqual(features.reference_price_text, "101")


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
# live_l1/io/market.py
#
# L1 Market Snapshot Feed
# - DummyMarketFeed: Pipeline / Smoke Tests
# - CSVMarketFeed: deterministic 1m Paper Runs
# - supports resume-after-snapshot fast-forward for L1-D
# ASCII-only.

from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from typing import Dict, Optional, TextIO


DEFAULT_CSV_PATH = "data/l1_paper_short_gate_test.csv"

SIGNAL_COLUMNS = (
    "rsi_signal",
    "macd_signal",
    "bollinger_signal",
    "ma200_signal",
    "stoch_signal",
    "atr_signal",
    "ema50_signal",
    "adx_signal",
    "cci_signal",
    "mfi_signal",
    "obv_signal",
    "roc_signal",
)


def _to_int(value: object, default: int = 0) -> int:
    if value is None:
        return default
    s = str(value).strip()
    if s == "":
        return default
    try:
        return int(float(s))
    except Exception:
        return default


def _to_float(value: object, default: float = 0.0) -> float:
    if value is None:
        return default
    s = str(value).strip()
    if s == "":
        return default
    try:
        return float(s)
    except Exception:
        return default


def _to_text(value: object, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _snapshot_id_from_index(index_1based: int) -> str:
    return f"CSV-{index_1based:08d}"


def _parse_snapshot_index(snapshot_id: str) -> Optional[int]:
    s = _to_text(snapshot_id, "")
    if not s.startswith("CSV-"):
        return None
    raw = s[4:]
    if raw == "":
        return None
    try:
        n = int(raw)
    except Exception:
        return None
    if n < 0:
        return None
    return n


@dataclass(frozen=True)
class MarketSnapshot:
    snapshot_id: str
    timestamp_utc: str
    symbol: str
    price: float
    signals: Dict[str, int]
    allow_long: int = 1
    allow_short: int = 1
    regime_v2: int = 0
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0
    volume: float = 0.0


class DummyMarketFeed:
    """
    Deterministic stub used for pipeline verification.
    """

    def __init__(self, symbol: str = "BTCUSDT"):
        self.symbol = symbol
        self.tick = 0

    def next_snapshot(self) -> MarketSnapshot:
        self.tick += 1

        signals = {
            "rsi_signal": 0,
            "macd_signal": 0,
        }

        price = 100.0 + float(self.tick)
        snapshot_id = f"DUMMY-{self.tick:06d}"

        return MarketSnapshot(
            snapshot_id=snapshot_id,
            timestamp_utc="1970-01-01T00:00:00Z",
            symbol=self.symbol,
            price=price,
            signals=signals,
        )

    def close(self) -> None:
        pass


class CSVMarketFeed:
    """
    Streaming CSV reader for deterministic paper runs.
    Reads exactly one CSV row per tick.

    Resume behavior:
    - if resume_after_snapshot_id is set to a valid CSV-XXXXXXXX id,
      the reader fast-forwards so the next emitted snapshot is the row
      immediately AFTER that snapshot id.
    - if the snapshot id is invalid or empty, no fast-forward happens.
    """

    def __init__(
        self,
        csv_path: str = DEFAULT_CSV_PATH,
        symbol: str = "BTCUSDT",
        resume_after_snapshot_id: str = "",
    ):
        self.csv_path = csv_path
        self.symbol = symbol
        self.tick = 0

        self._fh: Optional[TextIO] = open(self.csv_path, "r", encoding="utf-8")
        self._reader = csv.DictReader(self._fh)

        env_resume = _to_text(os.environ.get("L1_RESUME_AFTER_SNAPSHOT_ID", ""), "")
        self.resume_after_snapshot_id = _to_text(
            resume_after_snapshot_id if resume_after_snapshot_id else env_resume,
            "",
        )

        self._fast_forward_if_needed()

    def _fast_forward_if_needed(self) -> None:
        target_idx = _parse_snapshot_index(self.resume_after_snapshot_id)
        if target_idx is None or target_idx <= 0:
            return

        skipped = 0
        while skipped < target_idx:
            try:
                next(self._reader)
            except StopIteration:
                break
            skipped += 1

        self.tick = skipped

    def close(self) -> None:
        if self._fh:
            self._fh.close()

    def next_snapshot(self) -> MarketSnapshot:
        row = next(self._reader)

        self.tick += 1

        timestamp_utc = _to_text(row.get("timestamp_utc", ""), "")
        price = _to_float(row.get("close"), 0.0)

        signals: Dict[str, int] = {}
        for col in SIGNAL_COLUMNS:
            signals[col] = _to_int(row.get(col), 0)

        snapshot_id = _snapshot_id_from_index(self.tick)

        return MarketSnapshot(
            snapshot_id=snapshot_id,
            timestamp_utc=timestamp_utc,
            symbol=self.symbol,
            price=price,
            signals=signals,
            allow_long=_to_int(row.get("allow_long"), 1),
            allow_short=_to_int(row.get("allow_short"), 1),
            regime_v2=_to_int(row.get("regime_v2"), 0),
            open=_to_float(row.get("open"), 0.0),
            high=_to_float(row.get("high"), 0.0),
            low=_to_float(row.get("low"), 0.0),
            close=_to_float(row.get("close"), 0.0),
            volume=_to_float(row.get("volume"), 0.0),
        )
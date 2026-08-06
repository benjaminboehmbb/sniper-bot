from __future__ import annotations

import unittest

from live_l1.core.paper_economics_shadow import load_shadow_settings
from live_l1.tools.paper_economics_shadow_sidecar import (
    PaperEconomicsSidecarError,
    analyze_l1_log_text,
    parse_l1_log_line,
)


def shadow_environment() -> dict[str, str]:
    return {
        "PEE_MODE": "SHADOW",
        "PEE_SCHEMA_VERSION": "1",
        "PEE_ECONOMICS_MODEL_VERSION": "PEE_V1",
        "PEE_ECONOMICS_PROFILE_ID": "TEST_ONLY_CONSERVATIVE",
        "PEE_QUOTE_CURRENCY": "USDT",
        "PEE_STARTING_EQUITY_QUOTE": "10000",
        "PEE_RISK_PER_TRADE_RATE": "0.01",
        "PEE_MAX_POSITION_NOTIONAL_RATE": "0.05",
        "PEE_ENTRY_FEE_RATE": "0.0005",
        "PEE_EXIT_FEE_RATE": "0.0005",
        "PEE_ENTRY_SLIPPAGE_BPS": "2",
        "PEE_EXIT_SLIPPAGE_BPS": "2",
        "PEE_QUANTITY_STEP": "0.001",
        "PEE_MIN_QUANTITY": "0.001",
        "PEE_MIN_NOTIONAL_QUOTE": "5",
        "PEE_MAX_DAILY_LOSS_RATE": "0.03",
        "PEE_MAX_DAILY_FEE_RATE": "0.01",
        "PEE_MAX_REALIZED_DRAWDOWN_RATE": "0.10",
        "PEE_REFERENCE_STOP_RATE": "0.015",
    }


def log_line(*tokens: str) -> str:
    return " ".join(tokens)


class LogParserTests(unittest.TestCase):
    def test_market_timestamp_is_distinct_from_log_timestamp(self) -> None:
        event = parse_l1_log_line(
            log_line(
                "timestamp_utc=2026-08-06T10:00:01.123456Z",
                "seq=1",
                "category=L2",
                "event=market_snapshot",
                "severity=INFO",
                "system_state_id=STATE-1",
                "price=100",
                "tick=7",
                "timestamp_utc=2026-08-06T10:00:00Z",
            ),
            1,
        )

        self.assertEqual(event.timestamp_utc, "2026-08-06T10:00:01.123456Z")
        self.assertEqual(event.fields["timestamp_utc"], "2026-08-06T10:00:00Z")

    def test_duplicate_non_timestamp_key_is_rejected(self) -> None:
        with self.assertRaises(PaperEconomicsSidecarError):
            parse_l1_log_line(
                log_line(
                    "timestamp_utc=2026-08-06T10:00:01Z",
                    "seq=1",
                    "category=L2",
                    "event=market_snapshot",
                    "severity=INFO",
                    "system_state_id=STATE-1",
                    "tick=7",
                    "tick=8",
                ),
                1,
            )

    def test_third_timestamp_is_rejected(self) -> None:
        with self.assertRaises(PaperEconomicsSidecarError):
            parse_l1_log_line(
                log_line(
                    "timestamp_utc=2026-08-06T10:00:01Z",
                    "seq=1",
                    "category=L2",
                    "event=market_snapshot",
                    "severity=INFO",
                    "system_state_id=STATE-1",
                    "timestamp_utc=2026-08-06T10:00:00Z",
                    "timestamp_utc=2026-08-06T09:59:59Z",
                ),
                1,
            )


class SidecarAnalysisTests(unittest.TestCase):
    def setUp(self) -> None:
        self.settings = load_shadow_settings(shadow_environment())

    def test_real_logger_sequence_creates_one_observation(self) -> None:
        source = "\n".join(
            (
                log_line(
                    "timestamp_utc=2026-08-06T10:00:01.100000Z",
                    "seq=1",
                    "category=L2",
                    "event=market_snapshot",
                    "severity=INFO",
                    "system_state_id=STATE-1",
                    "price=100",
                    "snapshot_id=SNAP-7",
                    "symbol=BTCUSDT",
                    "tick=7",
                    "timestamp_utc=2026-08-06T10:00:00Z",
                ),
                log_line(
                    "timestamp_utc=2026-08-06T10:00:01.200000Z",
                    "seq=2",
                    "category=L3",
                    "event=intent_fused",
                    "severity=INFO",
                    "system_state_id=STATE-1",
                    "intent_id=INTENT-7",
                    "current_position=FLAT",
                    "intent_final=BUY",
                    "tick=7",
                ),
                log_line(
                    "timestamp_utc=2026-08-06T10:00:01.300000Z",
                    "seq=3",
                    "category=L5",
                    "event=execution",
                    "severity=INFO",
                    "system_state_id=STATE-1",
                    "intent_id=INTENT-7",
                    "action=OPEN_LONG",
                    "executed=1",
                    "position_before=FLAT",
                    "position_after=LONG",
                    "tick=7",
                ),
            )
        )

        report = analyze_l1_log_text(
            source,
            settings=self.settings,
            source_id="real-logger-sequence",
        )

        self.assertEqual(report.statistics.malformed_lines, 0)
        self.assertEqual(report.statistics.observations, 1)
        self.assertEqual(report.statistics.issues, 0)
        self.assertEqual(len(report.observations), 1)
        self.assertEqual(
            report.observations[0].fields["timestamp_utc"],
            "2026-08-06T10:00:00Z",
        )

    def test_single_timestamp_falls_back_to_log_timestamp(self) -> None:
        source = "\n".join(
            (
                "timestamp_utc=2026-08-06T10:00:01Z seq=1 category=L2 "
                "event=market_snapshot severity=INFO system_state_id=STATE-1 "
                "price=100 snapshot_id=SNAP-7 tick=7",
                "timestamp_utc=2026-08-06T10:00:02Z seq=2 category=L3 "
                "event=intent_fused severity=INFO system_state_id=STATE-1 "
                "intent_id=INTENT-7 current_position=FLAT intent_final=BUY tick=7",
                "timestamp_utc=2026-08-06T10:00:03Z seq=3 category=L5 "
                "event=execution severity=INFO system_state_id=STATE-1 "
                "intent_id=INTENT-7 action=OPEN_LONG executed=1 "
                "position_before=FLAT position_after=LONG tick=7",
            )
        )

        report = analyze_l1_log_text(
            source,
            settings=self.settings,
            source_id="single-timestamp-sequence",
        )

        self.assertEqual(
            report.observations[0].fields["timestamp_utc"],
            "2026-08-06T10:00:01Z",
        )


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from live_l1.core.paper_economics_shadow import load_shadow_settings
from live_l1.logs.logger import L1Logger
from live_l1.tools.paper_economics_shadow_sidecar import (
    PaperEconomicsSidecarError,
    analyze_l1_log_path,
    analyze_l1_log_text,
    main,
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


def write_original_logger_sequence(log_path: Path) -> None:
    logger = L1Logger(str(log_path))
    try:
        with redirect_stdout(io.StringIO()):
            logger.log(
                category="L2",
                event="market_snapshot",
                severity="INFO",
                system_state_id="STATE-LOGGER",
                fields={
                    "tick": 11,
                    "snapshot_id": "SNAP-11",
                    "timestamp_utc": "2026-08-06T11:00:00Z",
                    "price": 101,
                },
            )
            logger.log(
                category="L3",
                event="intent_fused",
                severity="INFO",
                system_state_id="STATE-LOGGER",
                intent_id="INTENT-11",
                fields={
                    "tick": 11,
                    "current_position": "FLAT",
                    "intent_final": "SELL",
                },
            )
            logger.log(
                category="L5",
                event="execution",
                severity="INFO",
                system_state_id="STATE-LOGGER",
                intent_id="INTENT-11",
                fields={
                    "tick": 11,
                    "action": "OPEN_SHORT",
                    "executed": 1,
                    "position_before": "FLAT",
                    "position_after": "SHORT",
                },
            )
    finally:
        logger.close()


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

    def test_original_l1_logger_output_is_analyzed_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            log_path = Path(directory) / "l1.log"
            write_original_logger_sequence(log_path)

            report = analyze_l1_log_path(
                log_path,
                settings=self.settings,
                source_id="original-l1-logger",
            )

        self.assertEqual(report.statistics.malformed_lines, 0)
        self.assertEqual(report.statistics.observations, 1)
        self.assertEqual(report.statistics.issues, 0)
        self.assertEqual(
            report.observations[0].fields["timestamp_utc"],
            "2026-08-06T11:00:00Z",
        )
        self.assertEqual(report.observations[0].fields["side"], "SHORT")


class SidecarCommandTests(unittest.TestCase):
    def test_cli_writes_repeatable_atomic_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log_path = root / "l1.log"
            config_path = root / "pee.json"
            first_output = root / "first-report.json"
            second_output = root / "second-report.json"
            write_original_logger_sequence(log_path)
            config_path.write_text(
                json.dumps(shadow_environment()),
                encoding="utf-8",
            )

            with redirect_stdout(io.StringIO()):
                first_status = main(
                    (
                        "--input-log",
                        str(log_path),
                        "--config-json",
                        str(config_path),
                        "--output-report",
                        str(first_output),
                    )
                )
                second_status = main(
                    (
                        "--input-log",
                        str(log_path),
                        "--config-json",
                        str(config_path),
                        "--output-report",
                        str(second_output),
                    )
                )

            first_bytes = first_output.read_bytes()
            payload = json.loads(first_bytes)
            self.assertEqual(first_status, 0)
            self.assertEqual(second_status, 0)
            self.assertEqual(first_bytes, second_output.read_bytes())
            self.assertEqual(payload["statistics"]["observations"], 1)
            self.assertEqual(len(payload["report_id"]), 64)
            self.assertEqual(list(root.glob(".*.tmp")), [])

    def test_cli_refuses_to_overwrite_source_log(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log_path = root / "l1.log"
            config_path = root / "pee.json"
            write_original_logger_sequence(log_path)
            original_bytes = log_path.read_bytes()
            config_path.write_text(
                json.dumps(shadow_environment()),
                encoding="utf-8",
            )

            with self.assertRaises(PaperEconomicsSidecarError):
                with redirect_stdout(io.StringIO()):
                    main(
                        (
                            "--input-log",
                            str(log_path),
                            "--config-json",
                            str(config_path),
                            "--output-report",
                            str(log_path),
                        )
                    )

            self.assertEqual(log_path.read_bytes(), original_bytes)


if __name__ == "__main__":
    unittest.main()

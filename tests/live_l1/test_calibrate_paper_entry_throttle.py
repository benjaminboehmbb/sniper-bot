#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from live_l1.core.paper_entry_throttle import EntryThrottleReasonCode
from live_l1.tools.calibrate_paper_entry_throttle import (
    ThrottleCalibrationError,
    build_calibration_report,
    publish_report,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ThrottleCalibrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp())
        self.execution = self.root / "execution.jsonl"
        self.trades = self.root / "trades.jsonl"
        self.manifest = self.root / "run_manifest.json"
        self.profile = self.root / "profile.json"
        self.candidates = self.root / "candidates.json"
        entry_times = (
            "2026-01-01 00:00:00+00:00",
            "2026-01-01 03:00:00+00:00",
            "2026-01-02 00:00:00+00:00",
        )
        exit_times = (
            "2026-01-01 01:00:00+00:00",
            "2026-01-01 04:00:00+00:00",
            "2026-01-02 01:00:00+00:00",
        )
        execution_records = []
        trade_records = []
        for index, (entry, exit_) in enumerate(zip(entry_times, exit_times), start=1):
            entry_price = 100 + index
            execution_records.extend(
                (
                    {
                        "event": "ENTRY_ACCEPTED",
                        "position_after": "LONG",
                        "position_before": "FLAT",
                        "price": entry_price,
                        "reason": "BUY_FROM_FLAT",
                        "schema_version": 1,
                        "side": "long",
                        "timestamp_utc": entry,
                    },
                    {
                        "event": "EXIT_EXECUTED",
                        "position_after": "FLAT",
                        "price": entry_price + 1,
                        "reason": "LONG_TIME_STOP_HIT",
                        "schema_version": 1,
                        "side": "long",
                        "timestamp_utc": exit_,
                    },
                )
            )
            trade_records.append(
                {
                    "entry_price": entry_price,
                    "entry_timestamp_utc": entry,
                    "exit_price": entry_price + 1,
                    "exit_timestamp_utc": exit_,
                    "schema_version": 1,
                    "side": "long",
                    "trade_id": f"TRADE-{index}",
                }
            )
        self.execution.write_text(
            "".join(json.dumps(record, sort_keys=True) + "\n" for record in execution_records),
            encoding="utf-8",
        )
        self.trades.write_text(
            "".join(json.dumps(record, sort_keys=True) + "\n" for record in trade_records),
            encoding="utf-8",
        )
        self.manifest.write_text(
            json.dumps(
                {
                    "git_commit": "a" * 40,
                    "normalized_market_slice": {
                        "rows_written": 3,
                        "first_timestamp_utc": entry_times[0],
                        "last_timestamp_utc": exit_times[-1],
                    },
                    "runtime": {
                        "return_code": 0,
                        "executed_actions": {"CLOSE_LONG": 3, "OPEN_LONG": 3},
                    },
                    "sidecar": {
                        "issues": 0,
                        "observation_ids_match_integrated": True,
                    },
                    "source_csv": {"sha256": "b" * 64},
                },
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        self.profile.write_text(
            json.dumps(
                {
                    "PEE_ECONOMICS_MODEL_VERSION": "PEE_V1",
                    "PEE_ECONOMICS_PROFILE_ID": "TEST",
                    "PEE_ENTRY_FEE_RATE": "0.001",
                    "PEE_ENTRY_SLIPPAGE_BPS": "5",
                    "PEE_EXIT_FEE_RATE": "0.001",
                    "PEE_EXIT_SLIPPAGE_BPS": "8",
                    "PEE_MAX_DAILY_FEE_RATE": "0.01",
                    "PEE_MAX_DAILY_LOSS_RATE": "0.1",
                    "PEE_MAX_POSITION_NOTIONAL_RATE": "0.1",
                    "PEE_MAX_REALIZED_DRAWDOWN_RATE": "0.5",
                    "PEE_MIN_NOTIONAL_QUOTE": "10",
                    "PEE_MIN_QUANTITY": "0.00001",
                    "PEE_MODE": "SHADOW",
                    "PEE_QUANTITY_STEP": "0.000001",
                    "PEE_QUOTE_CURRENCY": "USDT",
                    "PEE_REFERENCE_STOP_RATE": "0.015",
                    "PEE_RISK_PER_TRADE_RATE": "0.0025",
                    "PEE_SCHEMA_VERSION": "1",
                    "PEE_STARTING_EQUITY_QUOTE": "10000",
                },
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        self.candidates.write_text(
            json.dumps(
                {
                    "artifact_type": "pee_rate_calibration_candidate_set",
                    "schema_version": 1,
                    "calibration_only": True,
                    "operationally_approved": False,
                    "candidate_set_id": "TEST-CANDIDATES",
                    "rolling_window_seconds": 21600,
                    "sensitivity": {
                        "max_entries_per_utc_day": [1, 2],
                        "max_entries_per_rolling_window": [1, 2],
                        "min_reentry_cooldown_seconds": [10800, 10801],
                    },
                    "profiles": [
                        {
                            "policy_profile_id": "EXACT-BOUNDARY",
                            "max_entries_per_utc_day": 2,
                            "max_entries_per_rolling_window": 2,
                            "min_reentry_cooldown_seconds": 10800,
                            "classification": "TEST",
                        },
                        {
                            "policy_profile_id": "STRICT",
                            "max_entries_per_utc_day": 1,
                            "max_entries_per_rolling_window": 1,
                            "min_reentry_cooldown_seconds": 10801,
                            "classification": "TEST",
                        },
                    ],
                },
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.root)

    def build(self):
        return build_calibration_report(
            execution_log_path=self.execution,
            trades_log_path=self.trades,
            iu3_manifest_path=self.manifest,
            economics_profile_path=self.profile,
            candidate_set_path=self.candidates,
            expected_execution_sha256=sha256(self.execution),
            expected_trades_sha256=sha256(self.trades),
            expected_iu3_manifest_sha256=sha256(self.manifest),
            expected_source_sha256="b" * 64,
            calibration_git_commit="c" * 40,
            generated_at_utc="2026-08-11T00:00:00Z",
        )

    def test_report_is_deterministic_and_exact_cooldown_boundary_allows(self) -> None:
        first = self.build()
        second = self.build()
        self.assertEqual(first, second)
        self.assertEqual(first["distribution"]["max_entries_per_utc_day"], 2)
        self.assertEqual(first["distribution"]["max_entries_per_rolling_window"], 2)
        self.assertEqual(first["distribution"]["inter_entry_gap_seconds"]["minimum"], 10800)
        exact, strict = first["candidate_profiles"]
        self.assertEqual(exact["blocked_entry_count"], 0)
        self.assertEqual(strict["blocked_entry_count"], 1)
        self.assertEqual(strict["reason_counts"][EntryThrottleReasonCode.DAILY_ENTRY_LIMIT], 1)
        self.assertEqual(strict["reason_counts"][EntryThrottleReasonCode.ROLLING_ENTRY_LIMIT], 1)
        self.assertEqual(strict["reason_counts"][EntryThrottleReasonCode.REENTRY_COOLDOWN], 1)
        self.assertEqual(exact["delta_vs_unthrottled"]["settled_trade_count"], 0)
        self.assertEqual(strict["delta_vs_unthrottled"]["settled_trade_count"], -1)

    def test_report_requires_profile_approval_and_keeps_live_locked(self) -> None:
        report = self.build()
        interpretation = report["interpretation"]
        self.assertTrue(interpretation["approval_required"])
        self.assertFalse(interpretation["automatic_operational_selection"])
        self.assertFalse(interpretation["iu4_enforced_authorized"])
        self.assertFalse(interpretation["exchange_authorized"])
        self.assertFalse(interpretation["live_authorized"])
        self.assertTrue(all(not item["operationally_approved"] for item in report["candidate_profiles"]))

    def test_input_hash_mismatch_fails_closed(self) -> None:
        with self.assertRaises(ThrottleCalibrationError):
            build_calibration_report(
                execution_log_path=self.execution,
                trades_log_path=self.trades,
                iu3_manifest_path=self.manifest,
                economics_profile_path=self.profile,
                candidate_set_path=self.candidates,
                expected_execution_sha256="0" * 64,
                expected_trades_sha256=sha256(self.trades),
                expected_iu3_manifest_sha256=sha256(self.manifest),
                expected_source_sha256="b" * 64,
                calibration_git_commit="c" * 40,
                generated_at_utc="2026-08-11T00:00:00Z",
            )

    def test_execution_trade_parity_mismatch_fails_closed(self) -> None:
        lines = self.trades.read_text(encoding="utf-8").splitlines()
        self.trades.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
        with self.assertRaises(ThrottleCalibrationError):
            self.build()

    def test_publish_is_immutable(self) -> None:
        report = self.build()
        output = self.root / "report.json"
        first = publish_report(output, report)
        second = publish_report(output, report)
        self.assertEqual(first, second)
        changed = dict(report)
        changed["status"] = "CHANGED"
        with self.assertRaises(ThrottleCalibrationError):
            publish_report(output, changed)


if __name__ == "__main__":
    unittest.main()

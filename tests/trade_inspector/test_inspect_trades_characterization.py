from __future__ import annotations

import contextlib
import csv
import hashlib
import io
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest

from tools.trade_inspector import archive_intake as intake
from tools.trade_inspector import inspect_trades as inspector
from tools.trade_inspector import inspection_primitives as primitives


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "tools" / "trade_inspector" / "inspect_trades.py"

ENTRY_TS = "2026-01-01T00:00:00+00:00"
EXIT_TS = "2026-01-01T00:02:00+00:00"
EXPECTED_ROW_SHA256 = "54fc961343d463d4e55d6489c70ec9ffcf3892acc9155b45b95e5f9408a2ce24"
S3_SCENARIO_SHA256 = {
    "long": "de903d536a9874756c6a74bd6325f8e8bfea20ee6157222923efe024a5863aa1",
    "short": "c9cd9800a4a4de3f2b64daf9c6ec3c7df328308615064c37aff5bc9441a23276",
    "missing_path": "c54567d7b491ea7bf5f52d7b3bdb1a6a3c7df8e7d2815cb3efc07746ff7126f1",
    "zero_pnl": "3ca07215b9a292188e019f10617e2c1537f384d049818b857cb7c583a3bb5f72",
    "invalid_duration": "12d34e43c7117698ea579014b503e539a8dff6bd07c3095ecaa2d9cc78656987",
}


def sample_trade() -> dict[str, object]:
    return {
        "symbol": "BTCUSDT",
        "side": "long",
        "entry_timestamp_utc": ENTRY_TS,
        "exit_timestamp_utc": EXIT_TS,
        "duration_sec": 120,
        "entry_price": 100.0,
        "exit_price": 102.0,
        "pnl": 2.0,
        "pnl_pct": 0.02,
        "exit_reason": "take_profit",
    }


def sample_audit_rows() -> list[dict[str, object]]:
    return [
        {
            "event": "ENTRY_ACCEPTED",
            "timestamp_utc": ENTRY_TS,
            "side": "short",
            "reason": "wrong_side_decoy",
        },
        {
            "event": "ENTRY_ACCEPTED",
            "timestamp_utc": ENTRY_TS,
            "side": "long",
            "reason": "signal",
            "position_before": "FLAT",
            "position_after": "LONG",
        },
        {
            "event": "EXIT_EXECUTED",
            "timestamp_utc": EXIT_TS,
            "side": "long",
            "reason": "take_profit",
            "position_after": "FLAT",
        },
    ]


def sample_market_path() -> tuple[list[str], list[float]]:
    base = datetime.fromisoformat(ENTRY_TS)
    minute_offsets = [0, 1, 2, 17, 62, 242, 1442, 4322, 10082]
    timestamps = [(base + timedelta(minutes=value)).isoformat() for value in minute_offsets]
    prices = [100.0, 105.0, 102.0, 103.0, 104.0, 106.0, 108.0, 110.0, 112.0]
    return timestamps, prices


def sample_short_market_path() -> tuple[list[str], list[float]]:
    timestamps, _ = sample_market_path()
    prices = [100.0, 95.0, 98.0, 97.0, 96.0, 94.0, 92.0, 90.0, 88.0]
    return timestamps, prices


def sample_regime_index() -> dict[str, dict[str, object]]:
    return inspector.build_regime_index(
        [
            {
                "timestamp_utc": ENTRY_TS,
                "regime_label": "bull",
                "risk_label": "good_atr",
                "entry_score": "2",
                "ma200_signal": "1",
                "mfi_signal": "1",
                "atr_signal": "1",
            },
            {
                "timestamp_utc": EXIT_TS,
                "regime_label": "bear",
                "risk_label": "bad_atr",
                "entry_score": "-1",
                "ma200_signal": "-1",
                "mfi_signal": "-1",
                "atr_signal": "-1",
            },
        ]
    )


def build_sample_row() -> dict[str, object]:
    trade = sample_trade()
    timestamps, prices = sample_market_path()
    trade_id = inspector.build_trade_id(trade)
    return inspector.build_rows(
        [trade],
        sample_audit_rows(),
        sample_regime_index(),
        timestamps,
        prices,
        {trade_id: "alpha"},
    )[0]


def build_s3_snapshot(
    trade: dict[str, object],
    timestamps: list[str],
    prices: list[float],
) -> dict[str, object]:
    entry = {"event": "ENTRY_ACCEPTED"}
    exit_row = {"event": "EXIT_EXECUTED"}
    path = inspector.calculate_trade_path(trade, timestamps, prices)
    counterfactuals = inspector.calculate_counterfactuals(trade, timestamps, prices)
    quality_score, quality_band, positives, negatives = inspector.compute_quality_score(
        trade,
        entry,
        exit_row,
    )
    interpretation = inspector.interpretation_flags(path, counterfactuals)
    diagnosis = inspector.compute_diagnosis(path, counterfactuals, float(trade.get("pnl", 0.0)))
    confidence = inspector.compute_confidence_layer(
        {
            "has_entry_audit": 1,
            "has_exit_audit": 1,
            **path,
            **counterfactuals,
            **interpretation,
            **diagnosis,
        }
    )
    return {
        "quality_flags": inspector.quality_flags(trade, entry, exit_row),
        "quality": {
            "score": quality_score,
            "band": quality_band,
            "positives": positives,
            "negatives": negatives,
        },
        "path": path,
        "counterfactuals": counterfactuals,
        "interpretation": interpretation,
        "diagnosis": diagnosis,
        "confidence": confidence,
    }


def s3_snapshot_sha256(snapshot: dict[str, object]) -> str:
    payload = json.dumps(snapshot, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


class TradeInspectorCharacterizationTests(unittest.TestCase):
    def test_compatibility_primitives_are_reexported_with_exact_conversion_rules(self) -> None:
        self.assertIs(inspector.safe_text, primitives.safe_text)
        self.assertIs(inspector.safe_float, primitives.safe_float)
        self.assertIs(inspector.safe_int, primitives.safe_int)
        self.assertIs(inspector.parse_ts, primitives.parse_ts)
        self.assertIs(inspector.ts_key, primitives.ts_key)

        cases = [
            (None, -9.0, -9),
            ("", -9.0, -9),
            ("1", 1.0, 1),
            ("1.0", 1.0, -9),
            ("bad", -9.0, -9),
            (True, 1.0, 1),
        ]
        for value, expected_float, expected_int in cases:
            with self.subTest(value=value):
                self.assertEqual(primitives.safe_float(value, -9.0), expected_float)
                self.assertEqual(primitives.safe_int(value, -9), expected_int)

    def test_jsonl_and_market_parsers_keep_current_acceptance_rules(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            jsonl_path = root / "records.jsonl"
            jsonl_path.write_text('{"id": 1}\n\n{"id": 2}\n', encoding="utf-8")
            self.assertEqual(inspector.read_jsonl(jsonl_path), [{"id": 1}, {"id": 2}])

            bad_path = root / "bad.jsonl"
            bad_path.write_text('{"id": 1}\nnot-json\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, r"line 2"):
                inspector.read_jsonl(bad_path)

            market_path = root / "market.csv"
            with market_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["timestamp_utc", "close"])
                writer.writeheader()
                writer.writerow({"timestamp_utc": ENTRY_TS, "close": "100.5"})
                writer.writerow({"timestamp_utc": EXIT_TS, "close": "0"})
                writer.writerow({"timestamp_utc": "", "close": "102"})

            timestamps, prices = inspector.parse_market_rows(market_path)
            self.assertEqual(timestamps, [ENTRY_TS])
            self.assertEqual(prices, [100.5])

    def test_entry_matching_is_side_sensitive_and_exit_matching_is_timestamp_based(self) -> None:
        trade = sample_trade()
        audit_rows = sample_audit_rows()
        audit_rows[-1]["side"] = "short"

        entry, exit_row = inspector.find_matching_entry_exit(trade, audit_rows)

        self.assertIsNotNone(entry)
        self.assertEqual(entry["reason"], "signal")
        self.assertIsNotNone(exit_row)
        self.assertEqual(exit_row["reason"], "take_profit")

    def test_built_row_has_stable_semantic_fingerprint(self) -> None:
        row = build_sample_row()

        self.assertEqual(len(row), 127)
        self.assertEqual(row["trade_id"], "T_20260101_000000_LONG_BTCUSDT")
        self.assertEqual(row["quality_score"], 80)
        self.assertEqual(row["quality_class"], "good")
        self.assertEqual(row["bars_held"], 3)
        self.assertEqual(row["mfe_pct"], 0.05)
        self.assertEqual(row["opportunity_loss_24h_pct"], 0.06)
        self.assertEqual(row["root_cause"], "early_exit")
        self.assertEqual(row["priority"], "HIGH")
        self.assertEqual(row["regime_aligned"], 1)
        self.assertEqual(row["regime_changed_during_trade"], 1)
        self.assertEqual(row["trade_family_group"], "exit_after_regime_flip")

        payload = json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
        self.assertEqual(hashlib.sha256(payload).hexdigest(), EXPECTED_ROW_SHA256)

    def test_s3_long_path_and_diagnosis_snapshot(self) -> None:
        timestamps, prices = sample_market_path()
        snapshot = build_s3_snapshot(sample_trade(), timestamps, prices)

        self.assertEqual(s3_snapshot_sha256(snapshot), S3_SCENARIO_SHA256["long"])
        self.assertEqual(snapshot["quality"]["score"], 80)
        self.assertEqual(snapshot["path"]["mfe_pct"], 0.05)
        self.assertEqual(snapshot["diagnosis"]["root_cause"], "early_exit")
        self.assertEqual(snapshot["confidence"]["priority"], "HIGH")

    def test_s3_short_path_and_diagnosis_snapshot(self) -> None:
        trade = dict(sample_trade())
        trade.update({"side": "short", "exit_price": 98.0})
        timestamps, prices = sample_short_market_path()
        snapshot = build_s3_snapshot(trade, timestamps, prices)

        self.assertEqual(s3_snapshot_sha256(snapshot), S3_SCENARIO_SHA256["short"])
        self.assertEqual(inspector.trade_pnl_from_price("short", 100.0, 95.0), 5.0)
        self.assertEqual(snapshot["path"]["best_price_during_trade"], 95.0)
        self.assertEqual(snapshot["path"]["worst_price_during_trade"], 100.0)
        self.assertEqual(snapshot["path"]["mfe_pct"], 0.05)

    def test_s3_missing_path_snapshot(self) -> None:
        snapshot = build_s3_snapshot(sample_trade(), [], [])

        self.assertEqual(s3_snapshot_sha256(snapshot), S3_SCENARIO_SHA256["missing_path"])
        self.assertEqual(snapshot["path"]["path_available"], 0)
        self.assertEqual(snapshot["confidence"]["diagnosis_reliability"], 60)
        for label in inspector.FUTURE_WINDOWS_MIN:
            self.assertEqual(snapshot["counterfactuals"][f"counterfactual_available_{label}"], 0)

    def test_s3_zero_pnl_snapshot(self) -> None:
        trade = dict(sample_trade())
        trade.update({"exit_price": 100.0, "pnl": 0.0, "pnl_pct": 0.0})
        timestamps, prices = sample_market_path()
        snapshot = build_s3_snapshot(trade, timestamps, prices)

        self.assertEqual(s3_snapshot_sha256(snapshot), S3_SCENARIO_SHA256["zero_pnl"])
        self.assertEqual(snapshot["quality_flags"], ["flat_trade"])
        self.assertEqual(snapshot["quality"]["score"], 60)
        self.assertEqual(snapshot["quality"]["band"], "acceptable")
        self.assertEqual(snapshot["counterfactuals"]["exit_efficiency_24h_pct"], 0.0)
        self.assertEqual(snapshot["counterfactuals"]["opportunity_loss_24h_pct"], 0.08)

    def test_s3_invalid_duration_snapshot(self) -> None:
        trade = dict(sample_trade())
        trade["duration_sec"] = -1
        timestamps, prices = sample_market_path()
        snapshot = build_s3_snapshot(trade, timestamps, prices)

        self.assertEqual(s3_snapshot_sha256(snapshot), S3_SCENARIO_SHA256["invalid_duration"])
        self.assertEqual(snapshot["quality_flags"], ["negative_duration", "very_short_trade"])
        self.assertEqual(snapshot["quality"]["score"], 20)
        self.assertEqual(snapshot["quality"]["band"], "bad")
        self.assertEqual(snapshot["quality"]["negatives"], ["invalid_duration"])

    def test_s3_score_and_direction_boundaries(self) -> None:
        cases = [
            (39, "bad", -1),
            (40, "weak", 0),
            (59, "weak", 0),
            (60, "acceptable", 0),
            (74, "acceptable", 0),
            (75, "good", 1),
            (89, "good", 1),
            (90, "excellent", 1),
        ]
        for score, expected_band, expected_diagnosis in cases:
            with self.subTest(score=score):
                self.assertEqual(inspector.score_band(score), expected_band)
                self.assertEqual(inspector.signed_diagnosis(score), expected_diagnosis)

        self.assertEqual(inspector.trade_pnl_from_price("long", 100.0, 105.0), 5.0)
        self.assertEqual(inspector.trade_pnl_from_price("short", 100.0, 95.0), 5.0)
        self.assertEqual(inspector.trade_pnl_from_price("unknown", 100.0, 105.0), 0.0)

    def test_missing_market_path_remains_explicitly_unavailable(self) -> None:
        trade = sample_trade()
        path = inspector.calculate_trade_path(trade, [], [])
        counterfactuals = inspector.calculate_counterfactuals(trade, [], [])

        self.assertEqual(path["path_available"], 0)
        self.assertEqual(path["bars_held"], 0)
        for label in inspector.FUTURE_WINDOWS_MIN:
            self.assertEqual(counterfactuals[f"counterfactual_available_{label}"], 0)
            self.assertEqual(counterfactuals[f"cf_return_{label}_pct"], 0.0)

    def test_archive_intake_fails_closed_on_bad_json_and_count_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_dir = Path(temp_dir)
            (archive_dir / "trades_l1.jsonl").write_text('{"id": 1}\nnot-json\n', encoding="utf-8")
            (archive_dir / "execution_audit.jsonl").write_text('{"event": "ENTRY_ACCEPTED"}\n', encoding="utf-8")
            (archive_dir / "l1_paper.log").write_text("", encoding="utf-8")
            metadata = {
                "archive_id": "fixture",
                "archive_path": str(archive_dir),
                "created_at": "2026-01-01T00:00:00+00:00",
                "source_device": "X1",
                "run_type": "characterization",
                "strategy_profile": "fixture",
                "market_symbol": "BTCUSDT",
                "market_csv": "fixture.csv",
                "seeds_5m_csv": "fixture.csv",
                "max_ticks": 1,
                "tick_offset": 0,
                "decision_tick_seconds": 60,
                "start_time_utc": ENTRY_TS,
                "end_time_utc": EXIT_TS,
                "trade_count": 2,
                "audit_event_count": 1,
                "status": "validated",
                "notes": "hermetic characterization fixture",
            }
            (archive_dir / "archive_metadata.json").write_text(
                json.dumps(metadata, sort_keys=True),
                encoding="utf-8",
            )

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = inspector.run_archive_intake_validation(SimpleNamespace(archive_dir=str(archive_dir)))

            self.assertEqual(result, 1)
            self.assertIn("ARCHIVE_INTAKE: FAIL", output.getvalue())
            self.assertIn("trades_l1.jsonl bad JSON lines: 1", output.getvalue())
            self.assertIn("metadata trade_count mismatch", output.getvalue())

            ordered_diagnostics = [
                line
                for line in output.getvalue().splitlines()
                if line.startswith(("CHECK warnings:", "WARNING:", "ARCHIVE_INTAKE:", "ERROR:"))
            ]
            self.assertEqual(
                ordered_diagnostics,
                [
                    "CHECK warnings: 5",
                    "WARNING: optional file missing: trade_lifecycle_snapshots.csv",
                    "WARNING: optional file missing: monitor_status.json",
                    "WARNING: optional file missing: runtime_control.json",
                    "WARNING: optional file missing: loss_cluster_state.json",
                    "WARNING: optional file missing: trades_l1_auto_analysis.csv",
                    "ARCHIVE_INTAKE: FAIL",
                    "ERROR: trades_l1.jsonl bad JSON lines: 1",
                    "ERROR: metadata trade_count mismatch: metadata=2 actual=1",
                ],
            )

    def test_archive_intake_complete_fixture_passes_without_warnings(self) -> None:
        self.assertIs(inspector.count_valid_jsonl, intake.count_valid_jsonl)
        self.assertIs(inspector.run_archive_intake_validation, intake.run_archive_intake_validation)

        with tempfile.TemporaryDirectory() as temp_dir:
            archive_dir = Path(temp_dir)
            trades = [{"id": 1}, {"id": 2}]
            audit_rows = [{"event": "ENTRY_ACCEPTED"}, {"event": "EXIT_EXECUTED"}]

            (archive_dir / "trades_l1.jsonl").write_text(
                "".join(json.dumps(row, sort_keys=True) + "\n" for row in trades),
                encoding="utf-8",
            )
            (archive_dir / "execution_audit.jsonl").write_text(
                "".join(json.dumps(row, sort_keys=True) + "\n" for row in audit_rows),
                encoding="utf-8",
            )
            (archive_dir / "l1_paper.log").write_text("", encoding="utf-8")

            for name in [
                "trade_lifecycle_snapshots.csv",
                "monitor_status.json",
                "runtime_control.json",
                "loss_cluster_state.json",
                "trades_l1_auto_analysis.csv",
            ]:
                (archive_dir / name).write_text("", encoding="utf-8")

            metadata = {
                "archive_id": "fixture-pass",
                "archive_path": str(archive_dir),
                "created_at": "2026-01-01T00:00:00+00:00",
                "source_device": "X1",
                "run_type": "characterization",
                "strategy_profile": "fixture",
                "market_symbol": "BTCUSDT",
                "market_csv": "fixture.csv",
                "seeds_5m_csv": "fixture.csv",
                "max_ticks": 2,
                "tick_offset": 0,
                "decision_tick_seconds": 60,
                "start_time_utc": ENTRY_TS,
                "end_time_utc": EXIT_TS,
                "trade_count": len(trades),
                "audit_event_count": len(audit_rows),
                "status": "validated",
                "notes": "complete hermetic characterization fixture",
            }
            (archive_dir / "archive_metadata.json").write_text(
                json.dumps(metadata, sort_keys=True),
                encoding="utf-8",
            )

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = inspector.run_archive_intake_validation(SimpleNamespace(archive_dir=str(archive_dir)))

            self.assertEqual(result, 0)
            self.assertEqual(
                output.getvalue(),
                "\n".join(
                    [
                        "TRADE INSPECTOR V7I ARCHIVE INTAKE VALIDATION",
                        f"archive_dir: {archive_dir}",
                        "",
                        "CHECK required_files: PASS",
                        "CHECK archive_metadata_json: PASS",
                        "CHECK archive_id: fixture-pass",
                        "CHECK trades_valid_jsonl: 2",
                        "CHECK trades_bad_jsonl: 0",
                        "CHECK audit_valid_jsonl: 2",
                        "CHECK audit_bad_jsonl: 0",
                        "CHECK warnings: 0",
                        "",
                        "ARCHIVE_INTAKE: PASS",
                        "",
                    ]
                ),
            )

    def test_summary_cli_is_hermetic_and_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            archive_dir = root / "archive"
            archive_dir.mkdir()

            (archive_dir / "trades_l1.jsonl").write_text(
                json.dumps(sample_trade(), sort_keys=True) + "\n",
                encoding="utf-8",
            )
            (archive_dir / "execution_audit.jsonl").write_text(
                "".join(json.dumps(row, sort_keys=True) + "\n" for row in sample_audit_rows()),
                encoding="utf-8",
            )
            (archive_dir / "l1_paper.log").write_text(
                " ".join(
                    [
                        "event=regime_snapshot",
                        f"timestamp_utc={ENTRY_TS}",
                        "regime_label=bull",
                        "risk_label=good_atr",
                        "entry_score=2",
                        "ma200_signal=1",
                        "mfi_signal=1",
                        "atr_signal=1",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            market_path = root / "market.csv"
            timestamps, prices = sample_market_path()
            with market_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["timestamp_utc", "close"])
                writer.writeheader()
                writer.writerows(
                    {"timestamp_utc": timestamp, "close": price}
                    for timestamp, price in zip(timestamps, prices)
                )

            label_list = root / "labels.txt"
            label_list.write_text("alpha\n", encoding="utf-8")
            label_registry = root / "registry.csv"

            environment = dict(os.environ)
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            command = [
                sys.executable,
                str(SCRIPT_PATH),
                "--archive-dir",
                str(archive_dir),
                "--market-csv",
                str(market_path),
                "--label-list",
                str(label_list),
                "--label-registry",
                str(label_registry),
                "--summary",
            ]

            first = subprocess.run(
                command,
                cwd=REPO_ROOT,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
            second = subprocess.run(
                command,
                cwd=REPO_ROOT,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(first.stderr, "")
            self.assertEqual(first.stdout, second.stdout)
            self.assertIn("TRADE INSPECTOR V6", first.stdout)
            self.assertIn("TRADE INSPECTOR SUMMARY", first.stdout)
            self.assertIn("trades: 1", first.stdout)
            self.assertIn("winners: 1", first.stdout)
            self.assertIn("total_pnl: 2.0", first.stdout)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import csv
import hashlib
import tempfile
import unittest
from pathlib import Path

from live_l1.tools.run_pee_shadow_validation import (
    run_validation,
    write_normalized_slice,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = (
    PROJECT_ROOT
    / "config"
    / "pee"
    / "PEE_V1_PAPER_CONSERVATIVE_CANDIDATE_001.json"
)
SEED_PATH = PROJECT_ROOT / "seeds" / "5m" / "btcusdt_5m_timing_core_v2.csv"


class PeeShadowValidationRunnerTests(unittest.TestCase):
    def test_normalized_slice_filters_invalid_rows_and_applies_valid_offset(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pee-runner-test-") as directory:
            root = Path(directory)
            source = root / "source.csv"
            destination = root / "normalized.csv"
            source.write_text(
                "open_time,open_time_iso,close,rsi_signal\n"
                "1,2026-08-06T00:00:00Z,100,1\n"
                "2,2026-08-06T00:01:00Z,,0\n"
                "3,2026-08-06T00:02:00Z,101,-1\n"
                "4,,102,1\n"
                "5,2026-08-06T00:04:00Z,103,0\n",
                encoding="utf-8",
            )

            statistics = write_normalized_slice(
                source_path=source,
                destination_path=destination,
                max_ticks=2,
                valid_row_offset=1,
            )

            with destination.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual([row["close"] for row in rows], ["101", "103"])
            self.assertEqual(
                [row["timestamp_utc"] for row in rows],
                ["2026-08-06T00:02:00Z", "2026-08-06T00:04:00Z"],
            )
            self.assertNotIn("open_time_iso", rows[0])
            self.assertEqual(statistics.source_rows_scanned, 5)
            self.assertEqual(statistics.invalid_rows_skipped, 2)
            self.assertEqual(statistics.valid_offset_rows_skipped, 1)
            self.assertEqual(statistics.rows_written, 2)

    def test_normalized_slice_refuses_insufficient_valid_rows(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pee-runner-test-") as directory:
            root = Path(directory)
            source = root / "source.csv"
            destination = root / "normalized.csv"
            source.write_text(
                "timestamp_utc,close\n2026-08-06T00:00:00Z,100\n",
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                write_normalized_slice(
                    source_path=source,
                    destination_path=destination,
                    max_ticks=2,
                    valid_row_offset=0,
                )
            self.assertFalse(destination.exists())

    def test_two_tick_validation_writes_complete_manifest(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pee-runner-test-") as directory:
            root = Path(directory)
            source = root / "source.csv"
            output = root / "run"
            source.write_text(
                "timestamp_utc,open,high,low,close,volume\n"
                "2026-08-06T00:00:00Z,100,100,100,100,1\n"
                "2026-08-06T00:01:00Z,101,101,101,101,1\n",
                encoding="utf-8",
            )
            source_hash = hashlib.sha256(source.read_bytes()).hexdigest()

            manifest = run_validation(
                source_csv=source,
                expected_source_sha256=source_hash,
                profile_json=PROFILE_PATH,
                seed_csv=SEED_PATH,
                output_directory=output,
                max_ticks=2,
                valid_row_offset=0,
                source_id="TEST-TWO-TICKS",
            )

            self.assertEqual(manifest["runtime"]["return_code"], 0)
            self.assertEqual(manifest["runtime"]["max_ticks"], 2)
            self.assertEqual(manifest["runtime"]["execution_events"], 2)
            self.assertEqual(manifest["sidecar"]["issues"], 0)
            self.assertTrue(manifest["sidecar"]["observation_ids_match_integrated"])
            self.assertEqual(len(manifest["git_commit"]), 40)
            self.assertTrue((output / "run_manifest.json").is_file())
            self.assertTrue((output / "live_logs" / "sidecar_report.json").is_file())

    def test_four_tick_restart_validation_proves_resume_invariants(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pee-runner-restart-") as directory:
            root = Path(directory)
            source = root / "source.csv"
            output = root / "run"
            source.write_text(
                "timestamp_utc,open,high,low,close,volume\n"
                "2026-08-06T00:00:00Z,100,100,100,100,1\n"
                "2026-08-06T00:01:00Z,101,101,101,101,1\n"
                "2026-08-06T00:02:00Z,102,102,102,102,1\n"
                "2026-08-06T00:03:00Z,103,103,103,103,1\n",
                encoding="utf-8",
            )
            source_hash = hashlib.sha256(source.read_bytes()).hexdigest()

            manifest = run_validation(
                source_csv=source,
                expected_source_sha256=source_hash,
                profile_json=PROFILE_PATH,
                seed_csv=SEED_PATH,
                output_directory=output,
                max_ticks=4,
                valid_row_offset=0,
                source_id="TEST-FOUR-TICK-RESTART",
                restart_after_ticks=2,
            )

            self.assertEqual(manifest["runtime"]["execution_events"], 4)
            self.assertEqual(len(manifest["runtime"]["segments"]), 2)
            self.assertEqual(manifest["sidecar"]["issues"], 0)
            self.assertTrue(manifest["restart"]["system_state_ids_are_distinct"])
            self.assertEqual(
                manifest["restart"]["observed_resume_snapshot_id"],
                "CSV-00000002",
            )
            self.assertEqual(
                manifest["restart"]["observed_final_snapshot_id"],
                "CSV-00000004",
            )
            self.assertEqual(manifest["restart"]["s2_records"], 4)
            self.assertEqual(manifest["restart"]["s4_records"], 4)
            self.assertEqual(manifest["restart"]["state_bad_lines"], 0)


if __name__ == "__main__":
    unittest.main()

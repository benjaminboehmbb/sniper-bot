from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from live_l1.tools.run_paper_iu4_x1_replay_dataset import (
    IU4X1DatasetError,
    IU4X1DatasetReasonCode,
    run_x1_replay_dataset,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = (
    PROJECT_ROOT
    / "config"
    / "pee"
    / "PEE_V1_PAPER_CONSERVATIVE_CANDIDATE_001.json"
)
POLICY_PATH = (
    PROJECT_ROOT
    / "config"
    / "pee"
    / "PEE_RATE_X1_REPLAY_OBSERVATION_001.json"
)
SEED_PATH = PROJECT_ROOT / "seeds" / "5m" / "btcusdt_5m_timing_core_v2.csv"


class PaperIU4X1ReplayDatasetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory(
            prefix="pee-iu4-x1-dataset-"
        )
        self.root = Path(self.temporary_directory.name)
        self.source = self.root / "source.csv"
        self.source.write_text(
            "timestamp_utc,open,high,low,close,volume,allow_long,allow_short,regime_v2\n"
            "2026-08-09T10:00:00Z,100,100,100,100,1,1,1,0\n"
            "2026-08-09T10:01:00Z,110,110,110,110,1,1,1,0\n"
            "2026-08-09T10:02:00Z,105,105,105,105,1,1,1,0\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _arguments(self) -> dict[str, object]:
        return {
            "source_csv": self.source,
            "expected_source_sha256": hashlib.sha256(
                self.source.read_bytes()
            ).hexdigest(),
            "economics_profile_json": PROFILE_PATH,
            "throttle_observation_policy_json": POLICY_PATH,
            "seed_csv": SEED_PATH,
            "output_directory": self.root / "run",
            "max_ticks": 3,
            "valid_row_offset": 0,
            "source_id": "PEE-IU4-X1-DATASET-TEST",
            "replay_id": "PEE-IU4-X1-DATASET-TEST",
            "generated_at_utc": "2026-08-09T16:00:00Z",
        }

    def test_three_tick_run_writes_bound_evidence_without_activation(self) -> None:
        result = run_x1_replay_dataset(**self._arguments())
        manifest = json.loads(result.run_manifest_path.read_text(encoding="utf-8"))
        receipt = json.loads(result.pipeline.receipt_path.read_text(encoding="utf-8"))
        evidence_path = result.output_directory / "iu4_replay" / "replay_evidence.json"
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))

        fingerprint = manifest.pop("manifest_fingerprint")
        canonical = json.dumps(
            manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
        self.assertEqual(fingerprint, hashlib.sha256(canonical).hexdigest())
        self.assertEqual(result.iu3_manifest["sidecar"]["issues"], 0)
        self.assertEqual(evidence["validation"]["step_count"], 3)
        self.assertEqual(receipt["result"]["step_count"], 3)
        self.assertTrue(all(receipt["chain_checks"].values()))
        self.assertEqual(manifest["atomic_source"]["transaction_sequence"], 0)
        self.assertTrue(manifest["x1_only"])
        self.assertTrue(
            manifest["throttle_observation_policy"]["calibration_only"]
        )
        self.assertFalse(
            manifest["throttle_observation_policy"]["operationally_approved"]
        )
        self.assertFalse(manifest["iu4_enforced_enabled"])
        self.assertFalse(manifest["exchange_enabled"])
        self.assertFalse(manifest["live_enabled"])

    def test_operationally_approved_policy_is_rejected(self) -> None:
        unsafe_policy = self.root / "unsafe-policy.json"
        record = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        record["operationally_approved"] = True
        unsafe_policy.write_text(json.dumps(record), encoding="utf-8")
        arguments = self._arguments()
        arguments["throttle_observation_policy_json"] = unsafe_policy

        with self.assertRaises(IU4X1DatasetError) as raised:
            run_x1_replay_dataset(**arguments)
        self.assertEqual(
            raised.exception.reason_code,
            IU4X1DatasetReasonCode.POLICY_INVALID,
        )
        self.assertFalse((self.root / "run").exists())

    def test_controlled_restart_is_bound_into_top_manifest_and_receipt(self) -> None:
        arguments = self._arguments()
        arguments["restart_after_steps"] = 1

        result = run_x1_replay_dataset(**arguments)
        manifest = json.loads(result.run_manifest_path.read_text(encoding="utf-8"))
        receipt = json.loads(result.pipeline.receipt_path.read_text(encoding="utf-8"))

        self.assertEqual(manifest["restart_after_steps"], 1)
        self.assertTrue(receipt["result"]["restart_enabled"])
        self.assertEqual(receipt["result"]["restart_after_step"], 1)
        self.assertEqual(receipt["result"]["restart_position"], "FLAT")
        self.assertTrue(receipt["result"]["restart_state_restored"])

    def test_invalid_restart_boundary_is_rejected_before_output_creation(self) -> None:
        arguments = self._arguments()
        arguments["restart_after_steps"] = 3

        with self.assertRaises(IU4X1DatasetError) as raised:
            run_x1_replay_dataset(**arguments)
        self.assertEqual(
            raised.exception.reason_code,
            IU4X1DatasetReasonCode.INPUT_INVALID,
        )
        self.assertFalse((self.root / "run").exists())

    def test_restart_fault_injection_is_bound_and_blocks_remaining_steps(self) -> None:
        arguments = self._arguments()
        arguments["restart_after_steps"] = 1
        arguments["restart_fault_injection"] = "SNAPSHOT_TRUNCATED"

        result = run_x1_replay_dataset(**arguments)
        manifest = json.loads(result.run_manifest_path.read_text(encoding="utf-8"))
        receipt = json.loads(result.pipeline.receipt_path.read_text(encoding="utf-8"))

        self.assertEqual(manifest["restart_after_steps"], 1)
        self.assertEqual(
            manifest["restart_fault_injection"],
            "SNAPSHOT_TRUNCATED",
        )
        self.assertEqual(receipt["result"]["requested_step_count"], 3)
        self.assertEqual(receipt["result"]["step_count"], 1)
        self.assertTrue(receipt["result"]["restart_fault_detected"])
        self.assertTrue(receipt["result"]["continuation_blocked"])
        self.assertTrue(all(receipt["chain_checks"].values()))

    def test_existing_output_directory_is_never_overwritten(self) -> None:
        output = self.root / "run"
        output.mkdir()
        marker = output / "foreign.txt"
        marker.write_text("keep", encoding="utf-8")

        with self.assertRaises(IU4X1DatasetError) as raised:
            run_x1_replay_dataset(**self._arguments())
        self.assertEqual(
            raised.exception.reason_code,
            IU4X1DatasetReasonCode.OUTPUT_INVALID,
        )
        self.assertEqual(marker.read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()

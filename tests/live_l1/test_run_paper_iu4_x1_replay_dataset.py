from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from live_l1.tools.run_paper_iu4_x1_replay_dataset import (
    EXECUTION_HOST_WORKSTATION,
    IU4X1DatasetError,
    IU4X1DatasetReasonCode,
    run_x1_replay_dataset,
)
from live_l1.tools.paper_iu4_replay_pipeline import IU4ReplayPipelineError


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
APPROVED_POLICY_PATH = (
    PROJECT_ROOT / "config" / "pee" / "PEE_RATE_OBSERVED_BOUNDARY_001.json"
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

    def _approved_arguments(self) -> dict[str, object]:
        arguments = self._arguments()
        arguments["throttle_observation_policy_json"] = None
        arguments["approved_throttle_policy_json"] = APPROVED_POLICY_PATH
        return arguments

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
        self.assertFalse(manifest["workstation_only"])
        self.assertEqual(manifest["execution_host"], "X1")
        self.assertTrue(
            manifest["throttle_observation_policy"]["calibration_only"]
        )
        self.assertFalse(
            manifest["throttle_observation_policy"]["operationally_approved"]
        )
        self.assertFalse(manifest["iu4_enforced_enabled"])
        self.assertFalse(manifest["exchange_enabled"])
        self.assertFalse(manifest["live_enabled"])

    def test_workstation_run_is_bound_to_workstation_in_all_host_ids(self) -> None:
        arguments = self._arguments()
        arguments["execution_host"] = EXECUTION_HOST_WORKSTATION

        result = run_x1_replay_dataset(**arguments)
        manifest = json.loads(result.run_manifest_path.read_text(encoding="utf-8"))
        receipt = json.loads(result.pipeline.receipt_path.read_text(encoding="utf-8"))

        self.assertEqual(
            manifest["artifact_type"],
            "PEE_IU4_WORKSTATION_REPLAY_DATASET_RUN",
        )
        self.assertEqual(manifest["execution_host"], "WORKSTATION")
        self.assertFalse(manifest["x1_only"])
        self.assertTrue(manifest["workstation_only"])
        self.assertIn(
            "IU4-WORKSTATION-REPLAY",
            receipt["atomic_source"]["coordinator_id"],
        )

    def test_approved_profile_runs_offline_shadow_with_exact_binding(self) -> None:
        result = run_x1_replay_dataset(**self._approved_arguments())
        manifest = json.loads(result.run_manifest_path.read_text(encoding="utf-8"))
        receipt = json.loads(result.pipeline.receipt_path.read_text(encoding="utf-8"))

        approved = manifest["throttle_approved_policy"]
        self.assertNotIn("throttle_observation_policy", manifest)
        self.assertEqual(approved["profile_id"], "PEE_RATE_OBSERVED_BOUNDARY_001")
        self.assertEqual(approved["policy_model_version"], "PEE_RATE_V1")
        self.assertEqual(
            approved["policy_fingerprint"],
            "ed6e55744ce76d4f2e159832a2aeebcd4dbeb0f5dc1cdbbfda6177af119d1ada",
        )
        self.assertTrue(approved["profile_approved"])
        self.assertFalse(approved["runtime_activated"])
        self.assertEqual(
            approved["calibration_binding"]["report_sha256"],
            "c7ecc33ff559ab8c57b15928bc0ad0f98a466bd15130ac9f30f763918454afe8",
        )
        self.assertTrue(all(receipt["chain_checks"].values()))
        self.assertFalse(manifest["iu4_enforced_enabled"])
        self.assertFalse(manifest["exchange_enabled"])
        self.assertFalse(manifest["live_enabled"])

    def test_approved_profile_enforces_cooldown_and_keeps_exits_allowed(self) -> None:
        self.source.write_text(
            "timestamp_utc,open,high,low,close,volume,allow_long,allow_short,regime_v2\n"
            "2026-08-11T11:00:00Z,100,100,100,100,1,1,1,0\n"
            "2026-08-11T11:01:00Z,101,101,101,101,1,1,1,0\n"
            "2026-08-11T11:02:00Z,102,102,102,102,1,1,1,0\n"
            "2026-08-11T11:03:00Z,103,103,103,103,1,1,1,0\n"
            "2026-08-11T11:04:00Z,104,104,104,104,1,1,1,0\n"
            "2026-08-11T11:05:00Z,105,105,105,105,1,1,1,0\n",
            encoding="utf-8",
        )
        arguments = self._approved_arguments()
        arguments["expected_source_sha256"] = hashlib.sha256(
            self.source.read_bytes()
        ).hexdigest()
        arguments["max_ticks"] = 6
        with patch.dict(
            os.environ,
            {
                "L1_TEST_FORCE_INTENTS": "1",
                "L1_TEST_FORCE_BUY_EVERY": "2",
                "L1_TEST_FORCE_SELL_EVERY": "3",
                "L1_TEST_FORCE_WARMUP_TICKS": "0",
            },
        ):
            result = run_x1_replay_dataset(**arguments)

        receipt = json.loads(result.pipeline.receipt_path.read_text(encoding="utf-8"))
        evidence = json.loads(
            (result.output_directory / "iu4_replay" / "replay_evidence.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(receipt["result"]["committed_step_count"], 2)
        self.assertEqual(receipt["result"]["noop_step_count"], 2)
        self.assertEqual(receipt["result"]["rejected_step_count"], 2)
        rejected = [
            outcome
            for outcome in evidence["outcomes"]
            if outcome["status"] == "REJECTED"
        ]
        self.assertEqual(
            [outcome["reason_code"] for outcome in rejected],
            ["PEE_RATE_REENTRY_COOLDOWN", "PEE_RATE_REENTRY_COOLDOWN"],
        )
        self.assertTrue(all(outcome["exit_allowed"] for outcome in evidence["outcomes"]))
        self.assertTrue(all(receipt["chain_checks"].values()))
        self.assertFalse(receipt["result"]["continuation_blocked"])

    def test_both_throttle_policy_inputs_are_rejected_before_output(self) -> None:
        arguments = self._arguments()
        arguments["approved_throttle_policy_json"] = APPROVED_POLICY_PATH

        with self.assertRaises(IU4X1DatasetError) as raised:
            run_x1_replay_dataset(**arguments)
        self.assertEqual(
            raised.exception.reason_code,
            IU4X1DatasetReasonCode.POLICY_INVALID,
        )
        self.assertFalse((self.root / "run").exists())

    def test_approved_policy_activation_flag_fails_closed(self) -> None:
        unsafe_policy = self.root / "unsafe-approved-policy.json"
        record = json.loads(APPROVED_POLICY_PATH.read_text(encoding="utf-8"))
        record["runtime_activated"] = True
        unsafe_policy.write_text(json.dumps(record), encoding="utf-8")
        arguments = self._approved_arguments()
        arguments["approved_throttle_policy_json"] = unsafe_policy

        with self.assertRaises(IU4X1DatasetError) as raised:
            run_x1_replay_dataset(**arguments)
        self.assertEqual(
            raised.exception.reason_code,
            IU4X1DatasetReasonCode.POLICY_INVALID,
        )
        self.assertFalse((self.root / "run").exists())

    def test_approved_policy_fingerprint_mismatch_fails_closed(self) -> None:
        unsafe_policy = self.root / "mismatched-approved-policy.json"
        record = json.loads(APPROVED_POLICY_PATH.read_text(encoding="utf-8"))
        record["policy"]["max_entries_per_utc_day"] = 3
        unsafe_policy.write_text(json.dumps(record), encoding="utf-8")
        arguments = self._approved_arguments()
        arguments["approved_throttle_policy_json"] = unsafe_policy

        with self.assertRaises(IU4X1DatasetError) as raised:
            run_x1_replay_dataset(**arguments)
        self.assertEqual(
            raised.exception.reason_code,
            IU4X1DatasetReasonCode.POLICY_INVALID,
        )
        self.assertFalse((self.root / "run").exists())

    def test_unknown_execution_host_is_rejected_before_output_creation(self) -> None:
        arguments = self._arguments()
        arguments["execution_host"] = "UNBOUND"

        with self.assertRaises(IU4X1DatasetError) as raised:
            run_x1_replay_dataset(**arguments)
        self.assertEqual(
            raised.exception.reason_code,
            IU4X1DatasetReasonCode.INPUT_INVALID,
        )
        self.assertFalse((self.root / "run").exists())

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

    def test_resume_reuses_completed_iu3_and_replay_input(self) -> None:
        arguments = self._arguments()
        first = run_x1_replay_dataset(**arguments)
        replay_path = first.output_directory / "iu4_replay" / "replay.jsonl"
        evidence_path = (
            first.output_directory / "iu4_replay" / "replay_evidence.json"
        )
        replay_hash = hashlib.sha256(replay_path.read_bytes()).hexdigest()
        evidence_hash = hashlib.sha256(evidence_path.read_bytes()).hexdigest()
        iu3_manifest_path = first.output_directory / "iu3_source" / "run_manifest.json"
        iu3_manifest = json.loads(iu3_manifest_path.read_text(encoding="utf-8"))
        iu3_manifest["git_commit"] = "0" * 40
        iu3_manifest_path.write_text(
            json.dumps(iu3_manifest, sort_keys=True), encoding="utf-8"
        )
        evidence_path.unlink()
        (first.output_directory / "iu4_replay" / "pipeline_receipt.json").unlink()
        first.run_manifest_path.unlink()

        resumed = run_x1_replay_dataset(
            **arguments,
            resume_existing_output=True,
            expected_iu3_git_commit="0" * 40,
            progress_interval_steps=1,
        )
        progress = json.loads(
            (resumed.output_directory / "iu4_replay" / "phase2_progress.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(
            hashlib.sha256(replay_path.read_bytes()).hexdigest(), replay_hash
        )
        self.assertEqual(
            hashlib.sha256(evidence_path.read_bytes()).hexdigest(), evidence_hash
        )
        self.assertTrue(resumed.pipeline.input_build.replay.already_exists)
        self.assertEqual(progress["completed_steps"], 3)
        self.assertEqual(progress["total_steps"], 3)
        self.assertEqual(progress["percentage"], 100.0)
        self.assertEqual(progress["status"], "COMPLETE")
        top_manifest = json.loads(
            resumed.run_manifest_path.read_text(encoding="utf-8")
        )
        self.assertEqual(top_manifest["iu3_manifest"]["source_git_commit"], "0" * 40)

    def test_resume_rejects_modified_replay_input(self) -> None:
        arguments = self._arguments()
        first = run_x1_replay_dataset(**arguments)
        replay_path = first.output_directory / "iu4_replay" / "replay.jsonl"
        (first.output_directory / "iu4_replay" / "replay_evidence.json").unlink()
        (first.output_directory / "iu4_replay" / "pipeline_receipt.json").unlink()
        first.run_manifest_path.unlink()
        replay_path.write_bytes(replay_path.read_bytes() + b"{}\n")

        with self.assertRaises(IU4ReplayPipelineError):
            run_x1_replay_dataset(
                **arguments,
                resume_existing_output=True,
            )
        self.assertFalse(
            (first.output_directory / "iu4_replay" / "replay_evidence.json").exists()
        )


if __name__ == "__main__":
    unittest.main()

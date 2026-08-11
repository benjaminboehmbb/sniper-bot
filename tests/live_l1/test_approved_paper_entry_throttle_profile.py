#!/usr/bin/env python3

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from live_l1.core.paper_entry_throttle import PaperEntryThrottlePolicy
from live_l1.tools.run_paper_iu4_x1_replay_dataset import (
    IU4X1DatasetError,
    _load_calibration_policy,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = (
    PROJECT_ROOT / "config" / "pee" / "PEE_RATE_OBSERVED_BOUNDARY_001.json"
)
CANDIDATE_SET_PATH = (
    PROJECT_ROOT
    / "config"
    / "pee"
    / "PEE_RATE_CALIBRATION_CANDIDATES_001.json"
)

EXPECTED_PROFILE_FIELDS = {
    "artifact_type",
    "schema_version",
    "approval_id",
    "profile_approved",
    "runtime_activated",
    "iu4_enforced_authorized",
    "exchange_authorized",
    "live_authorized",
    "calibration_binding",
    "policy",
    "policy_fingerprint",
}
EXPECTED_BINDING_FIELDS = {
    "report_sha256",
    "report_fingerprint",
    "candidate_policy_profile_id",
    "candidate_policy_fingerprint",
    "decision_replay_sha256",
}


class ApprovedPaperEntryThrottleProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        cls.candidate_set = json.loads(
            CANDIDATE_SET_PATH.read_text(encoding="utf-8")
        )

    def test_profile_metadata_is_exact_and_runtime_stays_locked(self) -> None:
        self.assertEqual(set(self.record), EXPECTED_PROFILE_FIELDS)
        self.assertEqual(
            self.record["artifact_type"], "pee_rate_approved_policy_profile"
        )
        self.assertEqual(self.record["schema_version"], 1)
        self.assertEqual(
            self.record["approval_id"],
            "IU4-THROTTLE-PROFIL-OBSERVED-BOUNDARY-2026-08-11",
        )
        self.assertIs(self.record["profile_approved"], True)
        for field in (
            "runtime_activated",
            "iu4_enforced_authorized",
            "exchange_authorized",
            "live_authorized",
        ):
            self.assertIs(self.record[field], False)

    def test_approved_policy_has_exact_identity_values_and_fingerprint(self) -> None:
        policy_record = self.record["policy"]
        self.assertEqual(
            set(policy_record), set(PaperEntryThrottlePolicy.__dataclass_fields__)
        )
        policy = PaperEntryThrottlePolicy.from_record(policy_record)
        self.assertEqual(policy.policy_model_version, "PEE_RATE_V1")
        self.assertEqual(policy.policy_profile_id, "PEE_RATE_OBSERVED_BOUNDARY_001")
        self.assertEqual(policy.max_entries_per_utc_day, 2)
        self.assertEqual(policy.max_entries_per_rolling_window, 2)
        self.assertEqual(policy.rolling_window_seconds, 21600)
        self.assertEqual(policy.min_reentry_cooldown_seconds, 10800)
        self.assertEqual(
            policy.policy_fingerprint,
            "ed6e55744ce76d4f2e159832a2aeebcd4dbeb0f5dc1cdbbfda6177af119d1ada",
        )
        self.assertEqual(
            self.record["policy_fingerprint"], policy.policy_fingerprint
        )

    def test_calibration_binding_is_exact_and_hash_shaped(self) -> None:
        binding = self.record["calibration_binding"]
        self.assertEqual(set(binding), EXPECTED_BINDING_FIELDS)
        self.assertEqual(
            binding["report_sha256"],
            "c7ecc33ff559ab8c57b15928bc0ad0f98a466bd15130ac9f30f763918454afe8",
        )
        self.assertEqual(
            binding["report_fingerprint"],
            "22da65f4b9752f71cd26807a798f7e674f1236a02aec73a190e5252c8d40092d",
        )
        self.assertEqual(
            binding["decision_replay_sha256"],
            "65f47adaace62a9d9073bc28695d58b09bd7c943f3df94b23f2c67f70ea8114b",
        )
        for field in (
            "report_sha256",
            "report_fingerprint",
            "candidate_policy_fingerprint",
            "decision_replay_sha256",
        ):
            self.assertEqual(len(binding[field]), 64)
            self.assertTrue(all(character in "0123456789abcdef" for character in binding[field]))

    def test_approved_values_match_the_calibrated_candidate_exactly(self) -> None:
        binding = self.record["calibration_binding"]
        selected = next(
            profile
            for profile in self.candidate_set["profiles"]
            if profile["policy_profile_id"]
            == binding["candidate_policy_profile_id"]
        )
        candidate = PaperEntryThrottlePolicy(
            schema_version=1,
            policy_model_version="PEE_RATE_CALIBRATION_V1",
            policy_profile_id=selected["policy_profile_id"],
            max_entries_per_utc_day=selected["max_entries_per_utc_day"],
            max_entries_per_rolling_window=selected[
                "max_entries_per_rolling_window"
            ],
            rolling_window_seconds=self.candidate_set["rolling_window_seconds"],
            min_reentry_cooldown_seconds=selected[
                "min_reentry_cooldown_seconds"
            ],
        )
        approved = PaperEntryThrottlePolicy.from_record(self.record["policy"])
        self.assertEqual(
            candidate.policy_fingerprint,
            binding["candidate_policy_fingerprint"],
        )
        self.assertEqual(
            (
                approved.max_entries_per_utc_day,
                approved.max_entries_per_rolling_window,
                approved.rolling_window_seconds,
                approved.min_reentry_cooldown_seconds,
            ),
            (
                candidate.max_entries_per_utc_day,
                candidate.max_entries_per_rolling_window,
                candidate.rolling_window_seconds,
                candidate.min_reentry_cooldown_seconds,
            ),
        )

    def test_approved_profile_cannot_enter_calibration_only_replay_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "approved.json"
            path.write_text(
                json.dumps(self.record, sort_keys=True) + "\n", encoding="utf-8"
            )
            with self.assertRaises(IU4X1DatasetError):
                _load_calibration_policy(path)


if __name__ == "__main__":
    unittest.main()

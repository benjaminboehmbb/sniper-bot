#!/usr/bin/env python3

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from live_l1.core.paper_entry_throttle_profile import (
    ApprovedThrottleProfileError,
    ApprovedThrottleProfileReasonCode,
    load_approved_paper_entry_throttle_profile,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = (
    PROJECT_ROOT / "config" / "pee" / "PEE_RATE_OBSERVED_BOUNDARY_001.json"
)


class PaperEntryThrottleProfileTests(unittest.TestCase):
    def test_repository_profile_loads_with_exact_immutable_identity(self) -> None:
        loaded = load_approved_paper_entry_throttle_profile(PROFILE_PATH)

        self.assertEqual(
            loaded.approval_id,
            "IU4-THROTTLE-PROFIL-OBSERVED-BOUNDARY-2026-08-11",
        )
        self.assertEqual(
            loaded.file_sha256,
            "b16566970a3d7db4b038085d0b8601e24721fae572fbe7d3159c071680cd91e7",
        )
        self.assertEqual(
            loaded.policy.policy_fingerprint,
            "ed6e55744ce76d4f2e159832a2aeebcd4dbeb0f5dc1cdbbfda6177af119d1ada",
        )

    def test_activation_and_authority_flags_fail_closed(self) -> None:
        record = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        for field in (
            "runtime_activated",
            "iu4_enforced_authorized",
            "exchange_authorized",
            "live_authorized",
        ):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as work:
                path = Path(work) / "profile.json"
                changed = dict(record)
                changed[field] = True
                path.write_text(json.dumps(changed), encoding="utf-8")
                with self.assertRaises(ApprovedThrottleProfileError) as raised:
                    load_approved_paper_entry_throttle_profile(path)
                self.assertEqual(
                    raised.exception.reason_code,
                    ApprovedThrottleProfileReasonCode.AUTHORITY_INVALID,
                )

    def test_changed_policy_and_unknown_fields_fail_closed(self) -> None:
        record = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as work:
            root = Path(work)
            changed_policy = json.loads(json.dumps(record))
            changed_policy["policy"]["max_entries_per_utc_day"] = 3
            policy_path = root / "changed-policy.json"
            policy_path.write_text(json.dumps(changed_policy), encoding="utf-8")
            with self.assertRaises(ApprovedThrottleProfileError) as mismatch:
                load_approved_paper_entry_throttle_profile(policy_path)
            self.assertEqual(
                mismatch.exception.reason_code,
                ApprovedThrottleProfileReasonCode.POLICY_INVALID,
            )

            unknown = dict(record)
            unknown["runtime_override"] = "SHADOW"
            unknown_path = root / "unknown.json"
            unknown_path.write_text(json.dumps(unknown), encoding="utf-8")
            with self.assertRaises(ApprovedThrottleProfileError) as schema:
                load_approved_paper_entry_throttle_profile(unknown_path)
            self.assertEqual(
                schema.exception.reason_code,
                ApprovedThrottleProfileReasonCode.SCHEMA_INVALID,
            )

    def test_symlink_profile_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as work:
            linked = Path(work) / "profile.json"
            linked.symlink_to(PROFILE_PATH)
            with self.assertRaises(ApprovedThrottleProfileError) as raised:
                load_approved_paper_entry_throttle_profile(linked)
            self.assertEqual(
                raised.exception.reason_code,
                ApprovedThrottleProfileReasonCode.INPUT_INVALID,
            )


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from live_l1.core.paper_economics_shadow import load_shadow_settings
from live_l1.core.paper_entry_throttle import PaperEntryThrottleState
from live_l1.core.paper_entry_throttle_profile import (
    load_approved_paper_entry_throttle_profile,
)
from live_l1.core.paper_iu4_shadow_runtime_gate import (
    ENV_APPROVED_THROTTLE_PROFILE,
    ENV_ATOMIC_STATE_DIRECTORY,
    ENV_COORDINATOR_ID,
    ENV_MODE,
    ENV_REPOSITORY_COMMIT,
    ENV_SYMBOL,
    IU4ShadowRuntimeGateError,
    IU4ShadowRuntimeGateReasonCode,
    evaluate_iu4_shadow_runtime_gate,
)
from live_l1.state.paper_artifacts import PaperAccountState, PositionStateS2FlatV2
from live_l1.state.paper_atomic_coordinator import PaperAtomicCoordinator


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ECONOMICS_PATH = (
    PROJECT_ROOT / "config" / "pee" / "PEE_V1_PAPER_CONSERVATIVE_CANDIDATE_001.json"
)
THROTTLE_PATH = (
    PROJECT_ROOT / "config" / "pee" / "PEE_RATE_OBSERVED_BOUNDARY_001.json"
)
COMMIT_SHA = "a" * 40


class PaperIU4ShadowRuntimeGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory(
            prefix="pee-iu4-runtime-gate-"
        )
        self.root = Path(self.temporary_directory.name)
        economics_record = json.loads(ECONOMICS_PATH.read_text(encoding="utf-8"))
        self.environment = {key: str(value) for key, value in economics_record.items()}
        approved = load_approved_paper_entry_throttle_profile(THROTTLE_PATH)
        settings = load_shadow_settings(self.environment)
        assert settings.config is not None
        self.config = settings.config
        self.policy = approved.policy
        self.atomic_root = self.root / "atomic"
        self.coordinator = PaperAtomicCoordinator(
            self.atomic_root,
            self.config,
            self.policy,
            coordinator_id="IU4-RUNTIME-BTCUSDT",
            symbol="BTCUSDT",
        )
        self.coordinator.initialize(
            position=PositionStateS2FlatV2(
                schema_version=2,
                system_state_id="IU4-RUNTIME-INITIAL",
                symbol="BTCUSDT",
                position="FLAT",
                side="",
                last_closed_trade_id="",
                economics_profile_id=self.config.economics_profile_id,
                economics_model_version=self.config.economics_model_version,
                config_fingerprint=self.config.config_fingerprint,
            ),
            account=PaperAccountState.initial(
                account_id="PAPER-IU4-RUNTIME",
                quote_currency=self.config.quote_currency,
                starting_equity_quote=self.config.starting_equity_quote,
                utc_day="2026-08-12",
                economics_profile_id=self.config.economics_profile_id,
                economics_model_version=self.config.economics_model_version,
                config_fingerprint=self.config.config_fingerprint,
            ),
            throttle=PaperEntryThrottleState.initial(
                self.policy,
                utc_day="2026-08-12",
            ),
        )
        self.environment.update(
            {
                ENV_MODE: "SHADOW",
                ENV_ATOMIC_STATE_DIRECTORY: str(self.atomic_root),
                ENV_APPROVED_THROTTLE_PROFILE: str(THROTTLE_PATH),
                ENV_COORDINATOR_ID: self.coordinator.coordinator_id,
                ENV_SYMBOL: self.coordinator.symbol,
                ENV_REPOSITORY_COMMIT: COMMIT_SHA,
            }
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _evaluate(self, **overrides: object):
        arguments = {
            "repo_root": PROJECT_ROOT,
            "environment": self.environment,
            "operational_profile": "PAPER",
            "startup_recovery_enabled": True,
            "reconciliation_gate_enabled": True,
            "startup_timestamp_utc": "2026-08-12T12:00:00Z",
        }
        arguments.update(overrides)
        with patch(
            "live_l1.core.paper_iu4_shadow_runtime_gate._git_head",
            return_value=COMMIT_SHA,
        ):
            return evaluate_iu4_shadow_runtime_gate(**arguments)

    def test_off_is_default_and_requires_no_iu4_files(self) -> None:
        gate = self._evaluate(environment={})

        self.assertEqual(gate.mode, "OFF")
        self.assertFalse(gate.shadow_enabled)
        self.assertFalse(gate.decision.adapter_execution_enabled)
        self.assertFalse(gate.decision.state_mutation_allowed)
        self.assertIsNone(gate.coordinator)

    def test_shadow_binds_exact_profile_commit_and_state_without_mutation(self) -> None:
        before = self.coordinator.state_path.read_bytes()
        gate = self._evaluate()
        after = self.coordinator.state_path.read_bytes()

        self.assertTrue(gate.shadow_enabled)
        self.assertFalse(gate.decision.adapter_execution_enabled)
        self.assertFalse(gate.decision.state_mutation_allowed)
        self.assertFalse(gate.decision.entry_allowed)
        self.assertTrue(gate.decision.exit_allowed)
        self.assertEqual(before, after)
        fields = gate.startup_log_fields()
        self.assertEqual(fields["iu4_exchange_enabled"], 0)
        self.assertEqual(fields["iu4_live_enabled"], 0)
        self.assertEqual(
            fields["iu4_throttle_policy_fingerprint"],
            self.policy.policy_fingerprint,
        )
        gate.assert_current_binding()

    def test_changed_atomic_state_invalidates_prior_runtime_decision(self) -> None:
        gate = self._evaluate()
        self.coordinator.commit_kill_transition(
            transition_event_id="IU4-RUNTIME-KILL",
            expected_from_kill_level="NONE",
            target_kill_level="HARD",
            reason_code="TEST_RACE",
            authorization_reference="TEST",
            transition_timestamp_utc="2026-08-12T12:01:00Z",
            transition_tick_id=1,
        )

        with self.assertRaises(IU4ShadowRuntimeGateError) as raised:
            gate.assert_current_binding()
        self.assertEqual(
            raised.exception.reason_code,
            IU4ShadowRuntimeGateReasonCode.GATE_DENIED,
        )

    def test_enforced_and_non_paper_modes_are_rejected(self) -> None:
        enforced = dict(self.environment)
        enforced[ENV_MODE] = "ENFORCED"
        with self.assertRaises(IU4ShadowRuntimeGateError) as mode:
            self._evaluate(environment=enforced)
        self.assertEqual(
            mode.exception.reason_code,
            IU4ShadowRuntimeGateReasonCode.MODE_INVALID,
        )

        with self.assertRaises(IU4ShadowRuntimeGateError) as profile:
            self._evaluate(operational_profile="PRODUCTION")
        self.assertEqual(
            profile.exception.reason_code,
            IU4ShadowRuntimeGateReasonCode.MODE_INVALID,
        )

    def test_commit_mismatch_and_missing_reconciliation_fail_closed(self) -> None:
        mismatched = dict(self.environment)
        mismatched[ENV_REPOSITORY_COMMIT] = "b" * 40
        with self.assertRaises(IU4ShadowRuntimeGateError) as commit:
            self._evaluate(environment=mismatched)
        self.assertEqual(
            commit.exception.reason_code,
            IU4ShadowRuntimeGateReasonCode.COMMIT_INVALID,
        )

        with self.assertRaises(IU4ShadowRuntimeGateError) as reconciliation:
            self._evaluate(reconciliation_gate_enabled=False)
        self.assertEqual(
            reconciliation.exception.reason_code,
            IU4ShadowRuntimeGateReasonCode.GATE_DENIED,
        )

    def test_dirty_tracked_checkout_fails_closed(self) -> None:
        completed = type("Completed", (), {"stdout": "tracked-change\n"})()
        with patch(
            "live_l1.core.paper_iu4_shadow_runtime_gate.subprocess.run",
            side_effect=[
                type("Completed", (), {"stdout": COMMIT_SHA + "\n"})(),
                completed,
            ],
        ):
            with self.assertRaises(IU4ShadowRuntimeGateError) as raised:
                evaluate_iu4_shadow_runtime_gate(
                    repo_root=PROJECT_ROOT,
                    environment=self.environment,
                    operational_profile="PAPER",
                    startup_recovery_enabled=True,
                    reconciliation_gate_enabled=True,
                    startup_timestamp_utc="2026-08-12T12:00:00Z",
                )
        self.assertEqual(
            raised.exception.reason_code,
            IU4ShadowRuntimeGateReasonCode.COMMIT_INVALID,
        )

    def test_profile_authority_change_and_state_identity_mismatch_fail_closed(self) -> None:
        unsafe_profile = self.root / "unsafe-profile.json"
        record = json.loads(THROTTLE_PATH.read_text(encoding="utf-8"))
        record["runtime_activated"] = True
        unsafe_profile.write_text(json.dumps(record), encoding="utf-8")
        unsafe = dict(self.environment)
        unsafe[ENV_APPROVED_THROTTLE_PROFILE] = str(unsafe_profile)
        with self.assertRaises(IU4ShadowRuntimeGateError) as profile:
            self._evaluate(environment=unsafe)
        self.assertEqual(
            profile.exception.reason_code,
            IU4ShadowRuntimeGateReasonCode.PROFILE_REQUIRED,
        )

        mismatched = dict(self.environment)
        mismatched[ENV_COORDINATOR_ID] = "OTHER-IU4-COORDINATOR"
        with self.assertRaises(IU4ShadowRuntimeGateError) as coordinator:
            self._evaluate(environment=mismatched)
        self.assertEqual(
            coordinator.exception.reason_code,
            IU4ShadowRuntimeGateReasonCode.GATE_DENIED,
        )

    def test_formally_valid_but_unapproved_throttle_identity_fails_closed(self) -> None:
        alternate_profile = self.root / "alternate-profile.json"
        record = json.loads(THROTTLE_PATH.read_text(encoding="utf-8"))
        record["approval_id"] = "OTHER-APPROVAL"
        alternate_profile.write_text(json.dumps(record), encoding="utf-8")
        alternate = dict(self.environment)
        alternate[ENV_APPROVED_THROTTLE_PROFILE] = str(alternate_profile)

        with self.assertRaises(IU4ShadowRuntimeGateError) as raised:
            self._evaluate(environment=alternate)
        self.assertEqual(
            raised.exception.reason_code,
            IU4ShadowRuntimeGateReasonCode.PROFILE_REQUIRED,
        )

    def test_formally_valid_but_unapproved_economics_identity_fails_closed(self) -> None:
        alternate = dict(self.environment)
        alternate["PEE_ECONOMICS_PROFILE_ID"] = "OTHER-ECONOMICS"

        with self.assertRaises(IU4ShadowRuntimeGateError) as raised:
            self._evaluate(environment=alternate)
        self.assertEqual(
            raised.exception.reason_code,
            IU4ShadowRuntimeGateReasonCode.ECONOMICS_INVALID,
        )

    def test_symlink_atomic_source_fails_closed(self) -> None:
        linked_root = self.root / "linked-atomic"
        linked_root.symlink_to(self.atomic_root, target_is_directory=True)
        linked = dict(self.environment)
        linked[ENV_ATOMIC_STATE_DIRECTORY] = str(linked_root)

        with self.assertRaises(IU4ShadowRuntimeGateError) as raised:
            self._evaluate(environment=linked)
        self.assertEqual(
            raised.exception.reason_code,
            IU4ShadowRuntimeGateReasonCode.COORDINATOR_INVALID,
        )


if __name__ == "__main__":
    unittest.main()

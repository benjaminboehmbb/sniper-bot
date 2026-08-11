#!/usr/bin/env python3

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from live_l1.core.paper_entry_throttle import PaperEntryThrottleState
from live_l1.core.paper_iu4_startup_gate import (
    IU4ActivationAuthorizationV1,
    IU4StartupGateError,
    IU4StartupModeRequestV1,
    IU4StartupReasonCode,
    MODE_ENFORCED,
    MODE_OFF,
    MODE_SHADOW,
    evaluate_iu4_startup_gate,
)
from live_l1.state.paper_artifacts import PaperAccountState, PositionStateS2FlatV2
from live_l1.state.paper_atomic_coordinator import (
    PaperAtomicCoordinator,
    SimulatedAtomicTransactionInterruption,
)
from tests.live_l1.test_paper_iu4_adapter import make_config, make_policy


COMMIT_SHA = "a" * 40


class PaperIU4StartupGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.mkdtemp(prefix="pee-iu4-startup-")
        self.root = Path(self.temporary_directory)
        self.config = make_config()
        self.policy = make_policy()
        flat = PositionStateS2FlatV2(
            schema_version=2,
            system_state_id="SYSTEM-0",
            symbol="BTCUSDT",
            position="FLAT",
            side="",
            last_closed_trade_id="",
            economics_profile_id=self.config.economics_profile_id,
            economics_model_version=self.config.economics_model_version,
            config_fingerprint=self.config.config_fingerprint,
        )
        account = PaperAccountState.initial(
            account_id="PAPER-IU4-STARTUP",
            quote_currency=self.config.quote_currency,
            starting_equity_quote=self.config.starting_equity_quote,
            utc_day="2026-08-09",
            economics_profile_id=self.config.economics_profile_id,
            economics_model_version=self.config.economics_model_version,
            config_fingerprint=self.config.config_fingerprint,
        )
        throttle = PaperEntryThrottleState.initial(
            self.policy,
            utc_day="2026-08-09",
        )
        self.coordinator = PaperAtomicCoordinator(
            self.root,
            self.config,
            self.policy,
            coordinator_id="IU4-STARTUP-BTCUSDT",
            symbol="BTCUSDT",
        )
        self.coordinator.initialize(
            position=flat,
            account=account,
            throttle=throttle,
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.temporary_directory, ignore_errors=True)

    def _authorization(self, **overrides: object) -> IU4ActivationAuthorizationV1:
        return IU4ActivationAuthorizationV1(
            schema_version=1,
            authorization_id=str(overrides.get("authorization_id", "")),
            authorization_reference=str(
                overrides.get("authorization_reference", "USER-IU4-GATE-TEST")
            ),
            approved_mode=str(overrides.get("approved_mode", MODE_ENFORCED)),
            coordinator_id=str(
                overrides.get("coordinator_id", self.coordinator.coordinator_id)
            ),
            symbol=str(overrides.get("symbol", self.coordinator.symbol)),
            economics_profile_id=str(
                overrides.get(
                    "economics_profile_id",
                    self.config.economics_profile_id,
                )
            ),
            economics_model_version=str(
                overrides.get(
                    "economics_model_version",
                    self.config.economics_model_version,
                )
            ),
            economics_config_fingerprint=str(
                overrides.get(
                    "economics_config_fingerprint",
                    self.config.config_fingerprint,
                )
            ),
            throttle_policy_profile_id=str(
                overrides.get(
                    "throttle_policy_profile_id",
                    self.policy.policy_profile_id,
                )
            ),
            throttle_policy_model_version=str(
                overrides.get(
                    "throttle_policy_model_version",
                    self.policy.policy_model_version,
                )
            ),
            throttle_policy_fingerprint=str(
                overrides.get(
                    "throttle_policy_fingerprint",
                    self.policy.policy_fingerprint,
                )
            ),
            repository_commit_sha=str(
                overrides.get("repository_commit_sha", COMMIT_SHA)
            ),
            valid_from_utc=str(
                overrides.get("valid_from_utc", "2026-08-09T00:00:00Z")
            ),
            valid_until_utc=str(
                overrides.get("valid_until_utc", "2026-08-10T00:00:00Z")
            ),
        )

    def _request(self, mode: str, **overrides: object) -> IU4StartupModeRequestV1:
        authorization = overrides.get("authorization")
        if mode == MODE_ENFORCED and "authorization" not in overrides:
            authorization = self._authorization()
        return IU4StartupModeRequestV1(
            schema_version=1,
            mode=mode,
            startup_timestamp_utc=str(
                overrides.get("startup_timestamp_utc", "2026-08-09T12:00:00Z")
            ),
            operational_profile=str(
                overrides.get("operational_profile", "PAPER")
            ),
            startup_recovery_enabled=overrides.get(
                "startup_recovery_enabled",
                True,
            ),
            reconciliation_gate_enabled=overrides.get(
                "reconciliation_gate_enabled",
                True,
            ),
            repository_commit_sha=str(
                overrides.get("repository_commit_sha", COMMIT_SHA)
            ),
            expected_coordinator_id=str(
                overrides.get(
                    "expected_coordinator_id",
                    self.coordinator.coordinator_id,
                )
            ),
            expected_symbol=str(
                overrides.get("expected_symbol", self.coordinator.symbol)
            ),
            expected_economics_profile_id=str(
                overrides.get(
                    "expected_economics_profile_id",
                    self.config.economics_profile_id,
                )
            ),
            expected_economics_model_version=str(
                overrides.get(
                    "expected_economics_model_version",
                    self.config.economics_model_version,
                )
            ),
            expected_economics_config_fingerprint=str(
                overrides.get(
                    "expected_economics_config_fingerprint",
                    self.config.config_fingerprint,
                )
            ),
            expected_throttle_policy_profile_id=str(
                overrides.get(
                    "expected_throttle_policy_profile_id",
                    self.policy.policy_profile_id,
                )
            ),
            expected_throttle_policy_model_version=str(
                overrides.get(
                    "expected_throttle_policy_model_version",
                    self.policy.policy_model_version,
                )
            ),
            expected_throttle_policy_fingerprint=str(
                overrides.get(
                    "expected_throttle_policy_fingerprint",
                    self.policy.policy_fingerprint,
                )
            ),
            authorization=authorization,
        )

    @staticmethod
    def _evaluate_enforced(
        request: IU4StartupModeRequestV1,
        coordinator: PaperAtomicCoordinator,
        *,
        trusted_authorization_id: str | None = None,
    ):
        authorization = request.authorization
        trusted_id = (
            trusted_authorization_id
            if trusted_authorization_id is not None
            else authorization.authorization_id if authorization is not None else None
        )
        return evaluate_iu4_startup_gate(
            request,
            coordinator,
            running_repository_commit_sha=COMMIT_SHA,
            trusted_authorization_id=trusted_id,
        )

    def test_off_is_default_safe_without_coordinator_or_identity(self) -> None:
        request = IU4StartupModeRequestV1.off(
            startup_timestamp_utc="2026-08-09T12:00:00Z"
        )
        decision = evaluate_iu4_startup_gate(request, None)

        self.assertTrue(decision.passed)
        self.assertEqual(decision.mode, MODE_OFF)
        self.assertFalse(decision.adapter_execution_enabled)
        self.assertFalse(decision.shadow_observation_enabled)
        self.assertFalse(decision.state_mutation_allowed)
        self.assertFalse(decision.entry_allowed)
        self.assertTrue(decision.exit_allowed)
        self.assertEqual(decision.reason_codes, (IU4StartupReasonCode.OFF,))

    def test_invalid_mode_and_non_boolean_flags_are_rejected(self) -> None:
        with self.assertRaises(IU4StartupGateError):
            self._request("AUTO")
        with self.assertRaises(IU4StartupGateError):
            self._request(MODE_SHADOW, startup_recovery_enabled=1)

    def test_shadow_requires_healthy_exact_state_but_never_allows_mutation(self) -> None:
        before = self.coordinator.load_state()
        decision = evaluate_iu4_startup_gate(
            self._request(MODE_SHADOW),
            self.coordinator,
            running_repository_commit_sha=COMMIT_SHA,
        )

        self.assertTrue(decision.passed)
        self.assertFalse(decision.adapter_execution_enabled)
        self.assertTrue(decision.shadow_observation_enabled)
        self.assertFalse(decision.state_mutation_allowed)
        self.assertFalse(decision.entry_allowed)
        self.assertTrue(decision.exit_allowed)
        self.assertEqual(decision.atomic_state_fingerprint, before.state_fingerprint)
        self.assertEqual(self.coordinator.load_state(), before)

    def test_shadow_fails_closed_on_identity_mismatch(self) -> None:
        decision = evaluate_iu4_startup_gate(
            self._request(
                MODE_SHADOW,
                expected_economics_config_fingerprint="0" * 64,
            ),
            self.coordinator,
            running_repository_commit_sha=COMMIT_SHA,
        )

        self.assertFalse(decision.passed)
        self.assertFalse(decision.adapter_execution_enabled)
        self.assertEqual(
            decision.reason_codes,
            (IU4StartupReasonCode.IDENTITY_MISMATCH,),
        )

    def test_shadow_requires_matching_running_repository_commit(self) -> None:
        request = self._request(MODE_SHADOW)
        missing = evaluate_iu4_startup_gate(request, self.coordinator)
        mismatched = evaluate_iu4_startup_gate(
            request,
            self.coordinator,
            running_repository_commit_sha="b" * 40,
        )

        self.assertEqual(
            missing.reason_codes,
            (IU4StartupReasonCode.REPOSITORY_COMMIT_REQUIRED,),
        )
        self.assertEqual(
            mismatched.reason_codes,
            (IU4StartupReasonCode.REPOSITORY_COMMIT_MISMATCH,),
        )
        self.assertFalse(missing.shadow_observation_enabled)
        self.assertFalse(mismatched.state_mutation_allowed)

    def test_shadow_requires_explicit_reconciliation_gate(self) -> None:
        decision = evaluate_iu4_startup_gate(
            self._request(MODE_SHADOW, reconciliation_gate_enabled=False),
            self.coordinator,
            running_repository_commit_sha=COMMIT_SHA,
        )

        self.assertFalse(decision.passed)
        self.assertEqual(
            decision.reason_codes,
            (IU4StartupReasonCode.RECONCILIATION_GATE_REQUIRED,),
        )

    def test_corrupt_or_wal_ahead_state_blocks_shadow_and_enforced(self) -> None:
        record = json.loads(self.coordinator.state_path.read_text(encoding="utf-8"))
        record["risk"]["position_fingerprint"] = "0" * 64
        self.coordinator.state_path.write_text(json.dumps(record), encoding="utf-8")
        corrupt = evaluate_iu4_startup_gate(
            self._request(MODE_SHADOW),
            self.coordinator,
            running_repository_commit_sha=COMMIT_SHA,
        )
        self.assertFalse(corrupt.passed)
        self.assertEqual(corrupt.reason_codes[0], IU4StartupReasonCode.RECONCILIATION_FAILED)

        other_root = self.root / "wal-ahead"
        other = PaperAtomicCoordinator(
            other_root,
            self.config,
            self.policy,
            coordinator_id=self.coordinator.coordinator_id,
            symbol=self.coordinator.symbol,
        )
        initial = PositionStateS2FlatV2(
            schema_version=2,
            system_state_id="SYSTEM-0",
            symbol="BTCUSDT",
            position="FLAT",
            side="",
            last_closed_trade_id="",
            economics_profile_id=self.config.economics_profile_id,
            economics_model_version=self.config.economics_model_version,
            config_fingerprint=self.config.config_fingerprint,
        )
        account = PaperAccountState.initial(
            account_id="PAPER-IU4-WAL",
            quote_currency=self.config.quote_currency,
            starting_equity_quote=self.config.starting_equity_quote,
            utc_day="2026-08-09",
            economics_profile_id=self.config.economics_profile_id,
            economics_model_version=self.config.economics_model_version,
            config_fingerprint=self.config.config_fingerprint,
        )
        other.initialize(
            position=initial,
            account=account,
            throttle=PaperEntryThrottleState.initial(
                self.policy,
                utc_day="2026-08-09",
            ),
        )
        with self.assertRaises(SimulatedAtomicTransactionInterruption):
            other.commit_kill_transition(
                transition_event_id="KILL-PENDING",
                expected_from_kill_level="NONE",
                target_kill_level="HARD",
                reason_code="TEST",
                authorization_reference="AUTH-PENDING",
                transition_timestamp_utc="2026-08-09T10:00:00Z",
                transition_tick_id=100,
                simulate_interruption_after_journal=True,
            )
        wal_request = self._request(MODE_ENFORCED)
        wal_ahead = self._evaluate_enforced(
            wal_request,
            other,
        )
        self.assertFalse(wal_ahead.passed)
        self.assertEqual(
            wal_ahead.reason_codes[0],
            IU4StartupReasonCode.RECONCILIATION_FAILED,
        )

    def test_enforced_requires_paper_profile_recovery_and_authorization(self) -> None:
        wrong_profile_request = self._request(
            MODE_ENFORCED,
            operational_profile="PRODUCTION",
        )
        wrong_profile = self._evaluate_enforced(
            wrong_profile_request,
            self.coordinator,
        )
        no_recovery_request = self._request(
            MODE_ENFORCED,
            startup_recovery_enabled=False,
        )
        no_recovery = self._evaluate_enforced(
            no_recovery_request,
            self.coordinator,
        )
        with self.assertRaises(IU4StartupGateError) as missing:
            self._request(MODE_ENFORCED, authorization=None)

        self.assertEqual(
            wrong_profile.reason_codes,
            (IU4StartupReasonCode.PAPER_PROFILE_REQUIRED,),
        )
        self.assertEqual(
            no_recovery.reason_codes,
            (IU4StartupReasonCode.RECOVERY_REQUIRED,),
        )
        self.assertEqual(
            missing.exception.reason_code,
            IU4StartupReasonCode.AUTHORIZATION_REQUIRED,
        )

    def test_valid_enforced_gate_enables_adapter_only(self) -> None:
        authorization = self._authorization()
        restored = IU4ActivationAuthorizationV1.from_record(
            authorization.to_record()
        )
        request = self._request(MODE_ENFORCED, authorization=restored)
        decision = self._evaluate_enforced(
            request,
            self.coordinator,
        )

        self.assertTrue(decision.passed)
        self.assertTrue(decision.adapter_execution_enabled)
        self.assertFalse(decision.shadow_observation_enabled)
        self.assertTrue(decision.state_mutation_allowed)
        self.assertTrue(decision.entry_allowed)
        self.assertTrue(decision.exit_allowed)
        self.assertEqual(decision.authorization_id, authorization.authorization_id)
        self.assertEqual(
            decision.reason_codes,
            (IU4StartupReasonCode.ENFORCED_READY,),
        )

    def test_enforced_requires_external_authorization_trust_anchor(self) -> None:
        request = self._request(MODE_ENFORCED)
        missing = evaluate_iu4_startup_gate(
            request,
            self.coordinator,
            running_repository_commit_sha=COMMIT_SHA,
        )
        mismatched = evaluate_iu4_startup_gate(
            request,
            self.coordinator,
            running_repository_commit_sha=COMMIT_SHA,
            trusted_authorization_id="PEE-IU4-AUTH-NOT-APPROVED",
        )

        self.assertEqual(
            missing.reason_codes,
            (IU4StartupReasonCode.AUTHORIZATION_TRUST_REQUIRED,),
        )
        self.assertEqual(
            mismatched.reason_codes,
            (IU4StartupReasonCode.AUTHORIZATION_TRUST_MISMATCH,),
        )
        self.assertFalse(missing.adapter_execution_enabled)
        self.assertFalse(mismatched.state_mutation_allowed)

    def test_authorization_is_content_bound_time_limited_and_commit_pinned(self) -> None:
        authorization = self._authorization()
        with self.assertRaises(IU4StartupGateError):
            replace(authorization, authorization_reference="CHANGED")

        wrong_commit_request = self._request(
            MODE_ENFORCED,
            authorization=self._authorization(repository_commit_sha="b" * 40),
        )
        wrong_commit = self._evaluate_enforced(
            wrong_commit_request,
            self.coordinator,
        )
        not_yet_request = self._request(
            MODE_ENFORCED,
            startup_timestamp_utc="2026-08-08T23:59:59Z",
        )
        not_yet = self._evaluate_enforced(
            not_yet_request,
            self.coordinator,
        )
        expired_request = self._request(
            MODE_ENFORCED,
            startup_timestamp_utc="2026-08-10T00:00:01Z",
        )
        expired = self._evaluate_enforced(
            expired_request,
            self.coordinator,
        )

        self.assertEqual(
            wrong_commit.reason_codes,
            (IU4StartupReasonCode.AUTHORIZATION_MISMATCH,),
        )
        self.assertEqual(
            not_yet.reason_codes,
            (IU4StartupReasonCode.AUTHORIZATION_NOT_YET_VALID,),
        )
        self.assertEqual(
            expired.reason_codes,
            (IU4StartupReasonCode.AUTHORIZATION_EXPIRED,),
        )

    def test_kill_blocks_entries_but_enforced_gate_preserves_exit_path(self) -> None:
        self.coordinator.commit_kill_transition(
            transition_event_id="KILL-STARTUP",
            expected_from_kill_level="NONE",
            target_kill_level="EMERGENCY",
            reason_code="STARTUP_TEST",
            authorization_reference="AUTH-STARTUP-KILL",
            transition_timestamp_utc="2026-08-09T10:00:00Z",
            transition_tick_id=100,
        )
        request = self._request(MODE_ENFORCED)
        decision = self._evaluate_enforced(
            request,
            self.coordinator,
        )

        self.assertTrue(decision.passed)
        self.assertTrue(decision.adapter_execution_enabled)
        self.assertFalse(decision.entry_allowed)
        self.assertTrue(decision.exit_allowed)
        self.assertIn("PEE_S4_KILL_EMERGENCY", decision.reason_codes)


if __name__ == "__main__":
    unittest.main()

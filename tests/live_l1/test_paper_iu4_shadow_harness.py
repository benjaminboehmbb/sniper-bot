#!/usr/bin/env python3

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

from live_l1.core.paper_entry_throttle import (
    AcceptedEntryEventV1,
    PaperEntryThrottleState,
)
from live_l1.core.paper_economics import authorize_entry
from live_l1.core.paper_iu4_shadow_harness import (
    IU4ShadowHarnessError,
    IU4ShadowHarnessReasonCode,
    IU4ShadowIntentStepV1,
    PaperIU4ShadowDryRunHarness,
)
from live_l1.core.paper_iu4_startup_gate import (
    IU4StartupModeRequestV1,
    MODE_SHADOW,
    evaluate_iu4_startup_gate,
)
from live_l1.state.paper_artifacts import (
    PaperAccountState,
    PositionStateS2FlatV2,
    PositionStateS2V2,
)
from live_l1.state.paper_atomic_coordinator import PaperAtomicCoordinator
from tests.live_l1.test_paper_iu4_adapter import make_config, make_policy


D = Decimal
COMMIT_SHA = "a" * 40


class PaperIU4ShadowDryRunHarnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.mkdtemp(prefix="pee-iu4-harness-")
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
            account_id="PAPER-IU4-HARNESS",
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
            coordinator_id="IU4-HARNESS-BTCUSDT",
            symbol="BTCUSDT",
        )
        self.coordinator.initialize(
            position=flat,
            account=account,
            throttle=throttle,
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.temporary_directory, ignore_errors=True)

    def _shadow_decision(self):
        request = IU4StartupModeRequestV1(
            schema_version=1,
            mode=MODE_SHADOW,
            startup_timestamp_utc="2026-08-09T09:00:00Z",
            operational_profile="PAPER",
            startup_recovery_enabled=False,
            reconciliation_gate_enabled=True,
            repository_commit_sha=COMMIT_SHA,
            expected_coordinator_id=self.coordinator.coordinator_id,
            expected_symbol=self.coordinator.symbol,
            expected_economics_profile_id=self.config.economics_profile_id,
            expected_economics_model_version=self.config.economics_model_version,
            expected_economics_config_fingerprint=self.config.config_fingerprint,
            expected_throttle_policy_profile_id=self.policy.policy_profile_id,
            expected_throttle_policy_model_version=self.policy.policy_model_version,
            expected_throttle_policy_fingerprint=self.policy.policy_fingerprint,
            authorization=None,
        )
        return evaluate_iu4_startup_gate(
            request,
            self.coordinator,
            running_repository_commit_sha=COMMIT_SHA,
        )

    @staticmethod
    def _step(**overrides: object) -> IU4ShadowIntentStepV1:
        intent = str(overrides.get("intent", "BUY"))
        stop = overrides.get(
            "stop",
            D("95") if intent == "BUY" else D("105") if intent == "SELL" else None,
        )
        return IU4ShadowIntentStepV1(
            schema_version=1,
            source_intent_id=str(overrides.get("source_intent_id", "INTENT-1")),
            intent_final=intent,
            intent_reason_code=str(overrides.get("reason", "SHADOW_TEST")),
            target_system_state_id=str(
                overrides.get("system_state_id", "SYSTEM-1")
            ),
            timestamp_utc=str(
                overrides.get("timestamp", "2026-08-09T10:00:00Z")
            ),
            tick_id=int(overrides.get("tick_id", 100)),
            reference_price=overrides.get("price", D("100")),
            reference_stop_price=stop,
            trade_id=str(overrides.get("trade_id", "TRADE-1")),
        )

    def _source_bytes(self) -> dict[str, bytes]:
        paths = [self.coordinator.state_path]
        paths.extend(sorted(self.coordinator.transaction_directory.glob("*.json")))
        return {
            path.relative_to(self.root).as_posix(): path.read_bytes()
            for path in paths
        }

    def test_open_prediction_changes_only_disposable_sandbox(self) -> None:
        before_bytes = self._source_bytes()
        before_state = self.coordinator.load_state()
        report = PaperIU4ShadowDryRunHarness(
            self.coordinator,
            self._shadow_decision(),
        ).run((self._step(),))

        self.assertTrue(report.source_unchanged)
        self.assertTrue(report.sandbox_consistent)
        self.assertEqual(report.committed_step_count, 1)
        self.assertEqual(report.simulated_transaction_count, 1)
        self.assertEqual(report.outcomes[0].action, "OPEN_LONG")
        self.assertEqual(report.outcomes[0].state.position.position, "LONG")
        self.assertNotEqual(
            report.sandbox_final_state_fingerprint,
            report.source_final_state_fingerprint,
        )
        self.assertEqual(self._source_bytes(), before_bytes)
        self.assertEqual(self.coordinator.load_state(), before_state)

    def test_open_hold_close_sequence_is_atomic_and_no_reversal_occurs(self) -> None:
        steps = (
            self._step(),
            self._step(
                intent="HOLD",
                source_intent_id="INTENT-2",
                system_state_id="SYSTEM-1",
                timestamp="2026-08-09T10:10:00Z",
                tick_id=110,
                stop=None,
            ),
            self._step(
                intent="SELL",
                source_intent_id="INTENT-3",
                reason="EXIT_LONG",
                system_state_id="SYSTEM-2",
                timestamp="2026-08-09T11:00:00Z",
                tick_id=160,
                price=D("110"),
                stop=None,
            ),
        )
        report = PaperIU4ShadowDryRunHarness(
            self.coordinator,
            self._shadow_decision(),
        ).run(steps)

        self.assertEqual(report.step_count, 3)
        self.assertEqual(report.committed_step_count, 2)
        self.assertEqual(report.noop_step_count, 1)
        self.assertEqual(report.rejected_step_count, 0)
        self.assertEqual(report.simulated_transaction_count, 2)
        self.assertEqual(
            tuple(outcome.action for outcome in report.outcomes),
            ("OPEN_LONG", "NOOP", "CLOSE_LONG"),
        )
        self.assertEqual(report.outcomes[-1].state.position.position, "FLAT")
        self.assertEqual(report.outcomes[-1].state.account.closed_trade_count, 1)
        self.assertEqual(self.coordinator.load_state().position.position, "FLAT")

    def test_proven_autonomous_exit_closes_only_matching_open_position(self) -> None:
        autonomous_close = IU4ShadowIntentStepV1(
            schema_version=2,
            source_intent_id="INTENT-2",
            intent_final="SELL",
            intent_reason_code="LONG_TIME_STOP_HIT",
            target_system_state_id="SYSTEM-2",
            timestamp_utc="2026-08-09T11:00:00Z",
            tick_id=160,
            reference_price=D("110"),
            reference_stop_price=None,
            trade_id="",
            source_event_kind="AUTONOMOUS_EXIT_EXECUTION",
            source_intent_final="HOLD",
            source_execution_action="CLOSE_LONG",
            source_execution_sequence=42,
        )
        report = PaperIU4ShadowDryRunHarness(
            self.coordinator,
            self._shadow_decision(),
        ).run((self._step(), autonomous_close))

        self.assertEqual(
            tuple(outcome.action for outcome in report.outcomes),
            ("OPEN_LONG", "CLOSE_LONG"),
        )
        self.assertEqual(report.outcomes[-1].state.position.position, "FLAT")

    def test_controlled_restart_restores_open_position_and_continues_exactly(self) -> None:
        steps = (
            self._step(),
            self._step(
                intent="SELL",
                source_intent_id="INTENT-2",
                reason="EXIT_AFTER_RESTART",
                system_state_id="SYSTEM-2",
                timestamp="2026-08-09T11:00:00Z",
                tick_id=160,
                price=D("110"),
                stop=None,
            ),
        )
        harness = PaperIU4ShadowDryRunHarness(
            self.coordinator,
            self._shadow_decision(),
        )

        uninterrupted = harness.run(steps)
        restarted = harness.run(steps, restart_after_steps=1)

        self.assertTrue(restarted.restart_enabled)
        self.assertEqual(restarted.restart_after_step, 1)
        self.assertEqual(restarted.restart_count, 1)
        self.assertEqual(restarted.restart_position, "LONG")
        self.assertEqual(restarted.restart_transaction_sequence, 1)
        self.assertTrue(restarted.restart_state_restored)
        self.assertEqual(restarted.outcomes, uninterrupted.outcomes)
        self.assertEqual(
            restarted.sandbox_final_state_fingerprint,
            uninterrupted.sandbox_final_state_fingerprint,
        )
        self.assertEqual(restarted.outcomes[-1].state.position.position, "FLAT")

    def test_invalid_restart_boundaries_fail_before_source_write(self) -> None:
        harness = PaperIU4ShadowDryRunHarness(
            self.coordinator,
            self._shadow_decision(),
        )
        before = self._source_bytes()
        for boundary in (0, 1, 2, True):
            with self.subTest(boundary=boundary):
                with self.assertRaises(IU4ShadowHarnessError) as caught:
                    harness.run((self._step(),), restart_after_steps=boundary)
                self.assertEqual(
                    caught.exception.reason_code,
                    IU4ShadowHarnessReasonCode.STEP_INVALID,
                )
        self.assertEqual(self._source_bytes(), before)

    def test_autonomous_close_can_never_open_or_reverse_from_flat(self) -> None:
        autonomous_close = IU4ShadowIntentStepV1(
            schema_version=2,
            source_intent_id="INTENT-EXIT",
            intent_final="SELL",
            intent_reason_code="LONG_TIME_STOP_HIT",
            target_system_state_id="SYSTEM-2",
            timestamp_utc="2026-08-09T11:00:00Z",
            tick_id=160,
            reference_price=D("110"),
            reference_stop_price=None,
            trade_id="",
            source_event_kind="AUTONOMOUS_EXIT_EXECUTION",
            source_intent_final="HOLD",
            source_execution_action="CLOSE_LONG",
            source_execution_sequence=42,
        )

        with self.assertRaises(IU4ShadowHarnessError) as caught:
            PaperIU4ShadowDryRunHarness(
                self.coordinator,
                self._shadow_decision(),
            ).run((autonomous_close,))
        self.assertEqual(
            caught.exception.reason_code,
            IU4ShadowHarnessReasonCode.STEP_INVALID,
        )
        self.assertEqual(self.coordinator.load_state().position.position, "FLAT")

    def test_repeated_run_is_deterministic(self) -> None:
        harness = PaperIU4ShadowDryRunHarness(
            self.coordinator,
            self._shadow_decision(),
        )
        steps = (self._step(),)

        first = harness.run(steps)
        second = harness.run(steps)

        self.assertEqual(first, second)

    def test_state_bound_requests_continue_after_rejected_entry(self) -> None:
        steps = (
            self._step(stop=D("105")),
            self._step(
                intent="SELL",
                source_intent_id="INTENT-2",
                system_state_id="SYSTEM-2",
                timestamp="2026-08-09T10:01:00Z",
                tick_id=101,
                stop=D("105"),
                trade_id="TRADE-2",
            ),
        )
        report = PaperIU4ShadowDryRunHarness(
            self.coordinator,
            self._shadow_decision(),
        ).run(steps)

        self.assertEqual(
            tuple(outcome.status for outcome in report.outcomes),
            ("REJECTED", "COMMITTED"),
        )
        self.assertEqual(
            tuple(outcome.action for outcome in report.outcomes),
            ("OPEN_LONG", "OPEN_SHORT"),
        )
        self.assertEqual(report.outcomes[-1].state.position.trade_id, "TRADE-2")
        self.assertEqual(self.coordinator.load_state().position.position, "FLAT")

    def test_kill_rejects_shadow_entry_without_source_write(self) -> None:
        self.coordinator.commit_kill_transition(
            transition_event_id="KILL-1",
            expected_from_kill_level="NONE",
            target_kill_level="HARD",
            reason_code="TEST_KILL",
            authorization_reference="AUTH-KILL-1",
            transition_timestamp_utc="2026-08-09T09:00:00Z",
            transition_tick_id=90,
        )
        before = self._source_bytes()
        report = PaperIU4ShadowDryRunHarness(
            self.coordinator,
            self._shadow_decision(),
        ).run((self._step(),))

        self.assertEqual(report.committed_step_count, 0)
        self.assertEqual(report.rejected_step_count, 1)
        self.assertEqual(report.outcomes[0].reason_code, "PEE_S4_KILL_HARD")
        self.assertEqual(report.simulated_transaction_count, 0)
        self.assertEqual(self._source_bytes(), before)

    def test_exit_is_simulated_even_when_source_kill_is_emergency(self) -> None:
        state = self.coordinator.load_state()
        authorization = authorize_entry(
            side="LONG",
            realized_equity_quote=state.account.realized_equity_quote,
            reference_entry_price=D("100"),
            reference_stop_price=D("95"),
            config=self.config,
        )
        assert authorization.quote is not None
        quote = authorization.quote
        position = PositionStateS2V2(
            schema_version=2,
            system_state_id="SYSTEM-1",
            symbol="BTCUSDT",
            position="LONG",
            side="LONG",
            trade_id="TRADE-1",
            reference_entry_price=quote.reference_entry_price,
            modeled_entry_fill_price=quote.modeled_entry_fill_price,
            quantity=quote.quantity,
            entry_notional_quote=quote.entry_notional_quote,
            entry_fee_quote=quote.entry_fee_quote,
            risk_budget_quote=quote.risk_budget_quote,
            modeled_stop_loss_quote=quote.modeled_stop_loss_quote,
            reference_stop_price=quote.reference_stop_price,
            entry_timestamp_utc="2026-08-09T10:00:00Z",
            entry_tick_id=100,
            economics_profile_id=quote.economics_profile_id,
            economics_model_version=quote.economics_model_version,
            config_fingerprint=quote.config_fingerprint,
        )
        entry = AcceptedEntryEventV1(
            schema_version=1,
            entry_sequence=1,
            entry_event_id="SOURCE-OPEN",
            previous_entry_event_id="",
            entry_timestamp_utc="2026-08-09T10:00:00Z",
            policy_model_version=self.policy.policy_model_version,
            policy_profile_id=self.policy.policy_profile_id,
            policy_fingerprint=self.policy.policy_fingerprint,
        )
        self.coordinator.commit_open(
            position_after=position,
            accepted_entry_event=entry,
            transition_tick_id=100,
        )
        self.coordinator.commit_kill_transition(
            transition_event_id="KILL-EMERGENCY",
            expected_from_kill_level="NONE",
            target_kill_level="EMERGENCY",
            reason_code="TEST_EMERGENCY",
            authorization_reference="AUTH-EMERGENCY",
            transition_timestamp_utc="2026-08-09T10:30:00Z",
            transition_tick_id=130,
        )
        before = self._source_bytes()
        close = self._step(
            intent="SELL",
            source_intent_id="INTENT-CLOSE",
            reason="EXIT_DURING_EMERGENCY",
            system_state_id="SYSTEM-2",
            timestamp="2026-08-09T11:00:00Z",
            tick_id=160,
            price=D("110"),
            stop=None,
        )
        report = PaperIU4ShadowDryRunHarness(
            self.coordinator,
            self._shadow_decision(),
        ).run((close,))

        self.assertEqual(report.outcomes[0].action, "CLOSE_LONG")
        self.assertEqual(report.outcomes[0].state.position.position, "FLAT")
        self.assertEqual(report.outcomes[0].state.risk.kill_level, "EMERGENCY")
        self.assertTrue(report.outcomes[0].state.risk.exit_allowed)
        self.assertEqual(self._source_bytes(), before)

    def test_harness_rejects_non_shadow_or_mutating_gate_decision(self) -> None:
        shadow = self._shadow_decision()
        invalid_decisions = (
            replace(shadow, passed=False),
            replace(shadow, mode="OFF", shadow_observation_enabled=False),
            replace(shadow, adapter_execution_enabled=True),
            replace(shadow, state_mutation_allowed=True),
        )
        for decision in invalid_decisions:
            with self.subTest(decision=decision):
                with self.assertRaises(IU4ShadowHarnessError) as caught:
                    PaperIU4ShadowDryRunHarness(self.coordinator, decision)
                self.assertEqual(
                    caught.exception.reason_code,
                    IU4ShadowHarnessReasonCode.GATE_INVALID,
                )

    def test_stale_gate_and_corrupt_source_fail_closed(self) -> None:
        stale_gate = self._shadow_decision()
        self.coordinator.commit_kill_transition(
            transition_event_id="KILL-STALE",
            expected_from_kill_level="NONE",
            target_kill_level="SOFT",
            reason_code="STALE_TEST",
            authorization_reference="AUTH-STALE",
            transition_timestamp_utc="2026-08-09T09:30:00Z",
            transition_tick_id=95,
        )
        with self.assertRaises(IU4ShadowHarnessError) as stale:
            PaperIU4ShadowDryRunHarness(
                self.coordinator,
                stale_gate,
            ).run((self._step(),))
        self.assertEqual(stale.exception.reason_code, IU4ShadowHarnessReasonCode.GATE_INVALID)

        record = json.loads(self.coordinator.state_path.read_text(encoding="utf-8"))
        record["risk"]["position_fingerprint"] = "0" * 64
        self.coordinator.state_path.write_text(json.dumps(record), encoding="utf-8")
        with self.assertRaises(IU4ShadowHarnessError) as corrupt:
            PaperIU4ShadowDryRunHarness(
                self.coordinator,
                replace(
                    stale_gate,
                    atomic_state_fingerprint="0" * 64,
                    atomic_transaction_sequence=1,
                ),
            ).run(())
        self.assertEqual(
            corrupt.exception.reason_code,
            IU4ShadowHarnessReasonCode.SOURCE_INVALID,
        )

    def test_duplicate_or_invalid_steps_fail_without_source_write(self) -> None:
        before = self._source_bytes()
        harness = PaperIU4ShadowDryRunHarness(
            self.coordinator,
            self._shadow_decision(),
        )
        duplicate = replace(self._step(), timestamp_utc="2026-08-09T10:01:00Z")
        with self.assertRaises(IU4ShadowHarnessError) as duplicated:
            harness.run((self._step(), duplicate))
        self.assertEqual(
            duplicated.exception.reason_code,
            IU4ShadowHarnessReasonCode.DUPLICATE_SOURCE_INTENT,
        )

        with self.assertRaises(IU4ShadowHarnessError) as invalid:
            self._step(price=100.0)
        self.assertEqual(
            invalid.exception.reason_code,
            IU4ShadowHarnessReasonCode.STEP_INVALID,
        )
        self.assertEqual(self._source_bytes(), before)

    def test_work_directory_inside_source_is_rejected(self) -> None:
        work = self.root / "unsafe-work"
        work.mkdir()
        with self.assertRaises(IU4ShadowHarnessError) as caught:
            PaperIU4ShadowDryRunHarness(
                self.coordinator,
                self._shadow_decision(),
                work_directory=work,
            )

        self.assertEqual(
            caught.exception.reason_code,
            IU4ShadowHarnessReasonCode.WORK_DIRECTORY_INVALID,
        )

    def test_external_work_directory_is_cleaned_after_run(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pee-iu4-external-work-") as work:
            report = PaperIU4ShadowDryRunHarness(
                self.coordinator,
                self._shadow_decision(),
                work_directory=work,
            ).run(())

            self.assertEqual(list(Path(work).iterdir()), [])
            self.assertEqual(report.step_count, 0)
            self.assertEqual(report.simulated_transaction_count, 0)
            self.assertEqual(
                report.source_final_state_fingerprint,
                report.sandbox_final_state_fingerprint,
            )


if __name__ == "__main__":
    unittest.main()

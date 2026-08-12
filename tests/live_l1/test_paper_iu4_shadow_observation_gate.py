#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from live_l1.core.paper_economics_shadow import load_shadow_settings
from live_l1.core.paper_entry_throttle import PaperEntryThrottleState
from live_l1.core.paper_entry_throttle_profile import (
    load_approved_paper_entry_throttle_profile,
)
from live_l1.core.paper_iu4_shadow_observation_gate import (
    ENV_OBSERVATION_ENABLED,
    ENV_OBSERVATION_EVIDENCE_PATH,
    ENV_OBSERVATION_MAX_RECORDS,
    IU4ShadowObservationError,
    IU4ShadowObservationReasonCode,
    MAX_OBSERVATION_RECORDS,
    evaluate_iu4_shadow_observation_gate,
)
from live_l1.core.paper_iu4_shadow_runtime_gate import (
    ENV_APPROVED_THROTTLE_PROFILE,
    ENV_ATOMIC_STATE_DIRECTORY,
    ENV_COORDINATOR_ID,
    ENV_MODE,
    ENV_REPOSITORY_COMMIT,
    ENV_SYMBOL,
    evaluate_iu4_shadow_runtime_gate,
)
from live_l1.core import loop
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


class PaperIU4ShadowObservationGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory(
            prefix="pee-iu4-observation-gate-"
        )
        self.root = Path(self.temporary_directory.name)
        economics_record = json.loads(ECONOMICS_PATH.read_text(encoding="utf-8"))
        self.environment = {key: str(value) for key, value in economics_record.items()}
        approved = load_approved_paper_entry_throttle_profile(THROTTLE_PATH)
        settings = load_shadow_settings(self.environment)
        assert settings.config is not None
        self.atomic_root = self.root / "atomic"
        self.coordinator = PaperAtomicCoordinator(
            self.atomic_root,
            settings.config,
            approved.policy,
            coordinator_id="IU4-OBSERVATION-BTCUSDT",
            symbol="BTCUSDT",
        )
        self.coordinator.initialize(
            position=PositionStateS2FlatV2(
                schema_version=2,
                system_state_id="IU4-OBSERVATION-INITIAL",
                symbol="BTCUSDT",
                position="FLAT",
                side="",
                last_closed_trade_id="",
                economics_profile_id=settings.config.economics_profile_id,
                economics_model_version=settings.config.economics_model_version,
                config_fingerprint=settings.config.config_fingerprint,
            ),
            account=PaperAccountState.initial(
                account_id="PAPER-IU4-OBSERVATION",
                quote_currency=settings.config.quote_currency,
                starting_equity_quote=settings.config.starting_equity_quote,
                utc_day="2026-08-12",
                economics_profile_id=settings.config.economics_profile_id,
                economics_model_version=settings.config.economics_model_version,
                config_fingerprint=settings.config.config_fingerprint,
            ),
            throttle=PaperEntryThrottleState.initial(
                approved.policy,
                utc_day="2026-08-12",
            ),
        )
        self.evidence_path = self.root / "evidence" / "iu4-shadow.json"
        self.records_journal_path = self.evidence_path.with_name(
            f"{self.evidence_path.name}.records.jsonl"
        )
        self.evidence_path.parent.mkdir()
        self.environment.update(
            {
                ENV_MODE: "SHADOW",
                ENV_ATOMIC_STATE_DIRECTORY: str(self.atomic_root),
                ENV_APPROVED_THROTTLE_PROFILE: str(THROTTLE_PATH),
                ENV_COORDINATOR_ID: self.coordinator.coordinator_id,
                ENV_SYMBOL: self.coordinator.symbol,
                ENV_REPOSITORY_COMMIT: COMMIT_SHA,
                ENV_OBSERVATION_ENABLED: "1",
                ENV_OBSERVATION_EVIDENCE_PATH: str(self.evidence_path),
                ENV_OBSERVATION_MAX_RECORDS: "3",
            }
        )
        with patch(
            "live_l1.core.paper_iu4_shadow_runtime_gate._git_head",
            return_value=COMMIT_SHA,
        ):
            self.runtime_gate = evaluate_iu4_shadow_runtime_gate(
                repo_root=PROJECT_ROOT,
                environment=self.environment,
                operational_profile="PAPER",
                startup_recovery_enabled=True,
                reconciliation_gate_enabled=True,
                startup_timestamp_utc="2026-08-12T12:00:00Z",
            )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _evaluate(self, environment: dict[str, str] | None = None, max_ticks: int = 3):
        with patch(
            "live_l1.core.paper_iu4_shadow_runtime_gate._git_head",
            return_value=COMMIT_SHA,
        ):
            return evaluate_iu4_shadow_observation_gate(
                repo_root=PROJECT_ROOT,
                environment=self.environment if environment is None else environment,
                runtime_gate=self.runtime_gate,
                requested_max_ticks=max_ticks,
            )

    @staticmethod
    def _execution(
        *,
        action: str,
        executed: bool,
        before: str,
        after: str,
        reason: str,
    ) -> SimpleNamespace:
        return SimpleNamespace(
            action=action,
            executed=executed,
            position_before=before,
            position_after=after,
            reason=reason,
        )

    def _observe(
        self,
        gate,
        *,
        tick: int,
        intent: str,
        action: str,
        executed: bool,
        before: str,
        after: str,
    ):
        assert gate.observer is not None
        return gate.observer.observe_tick(
            system_state_id=f"L1-STATE-{tick}",
            tick_id=tick,
            snapshot_id=f"SNAP-{tick}",
            timestamp_utc=f"2026-08-12T12:00:0{tick}Z",
            source_intent_id=f"IN-{tick}",
            intent_final=intent,
            intent_reason_code="TEST",
            reference_price_text="100",
            legacy_execution=self._execution(
                action=action,
                executed=executed,
                before=before,
                after=after,
                reason="TEST_EXECUTION",
            ),
            guard_reason="guard_ok",
            s4_kill_level="NONE",
        )

    def test_disabled_is_safe_default_without_evidence(self) -> None:
        environment = dict(self.environment)
        environment.pop(ENV_OBSERVATION_ENABLED)
        environment.pop(ENV_OBSERVATION_EVIDENCE_PATH)
        environment.pop(ENV_OBSERVATION_MAX_RECORDS)

        gate = self._evaluate(environment=environment)

        self.assertFalse(gate.enabled)
        self.assertIsNone(gate.observer)
        self.assertFalse(self.evidence_path.exists())

    def test_enabled_observation_is_bounded_and_source_stays_byte_equal(self) -> None:
        source_before = self.coordinator.state_path.read_bytes()
        gate = self._evaluate()
        try:
            first = self._observe(
                gate,
                tick=1,
                intent="BUY",
                action="OPEN_LONG",
                executed=True,
                before="FLAT",
                after="LONG",
            )
            second = self._observe(
                gate,
                tick=2,
                intent="HOLD",
                action="NOOP",
                executed=False,
                before="LONG",
                after="LONG",
            )
        finally:
            assert gate.observer is not None
            gate.observer.close()

        self.assertEqual(first["iu4"]["action"], "OPEN_LONG")
        self.assertEqual(second["iu4"]["action"], "NOOP")
        self.assertTrue(first["parity"]["action_equal"])
        self.assertTrue(second["parity"]["position_after_equal"])
        self.assertEqual(self.coordinator.state_path.read_bytes(), source_before)
        evidence = json.loads(self.evidence_path.read_text(encoding="utf-8"))
        fingerprint = evidence.pop("evidence_fingerprint")
        canonical = json.dumps(
            evidence,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
        self.assertEqual(fingerprint, hashlib.sha256(canonical).hexdigest())
        self.assertEqual(evidence["record_count"], 2)
        self.assertEqual(evidence["max_records"], 3)
        self.assertFalse(evidence["source_state_mutation_allowed"])
        self.assertEqual(evidence["schema_version"], 2)
        self.assertEqual(
            evidence["writer_contract"]["mode"],
            "HASH_CHAINED_APPEND_JOURNAL",
        )
        self.assertTrue(evidence["writer_contract"]["finalized"])
        self.assertEqual(
            evidence["writer_contract"]["records_journal_entry_count"],
            2,
        )
        self.assertEqual(
            evidence["writer_contract"]["records_journal_sha256"],
            hashlib.sha256(self.records_journal_path.read_bytes()).hexdigest(),
        )

    def test_active_checkpoint_is_constant_shape_and_records_are_append_only(self) -> None:
        environment = dict(self.environment)
        environment[ENV_OBSERVATION_MAX_RECORDS] = "20"
        gate = self._evaluate(environment=environment, max_ticks=20)
        checkpoint_sizes: list[int] = []
        journal_prefix = b""
        try:
            for tick in range(1, 21):
                self._observe(
                    gate,
                    tick=tick,
                    intent="HOLD",
                    action="NOOP",
                    executed=False,
                    before="FLAT",
                    after="FLAT",
                )
                checkpoint = json.loads(
                    self.evidence_path.read_text(encoding="utf-8")
                )
                current_journal = self.records_journal_path.read_bytes()
                self.assertEqual(
                    checkpoint["artifact_type"],
                    "PEE_IU4_SHADOW_RUNTIME_OBSERVATION_CHECKPOINT",
                )
                self.assertEqual(checkpoint["record_count"], tick)
                self.assertNotIn("records", checkpoint)
                self.assertFalse(checkpoint["finalized"])
                self.assertTrue(current_journal.startswith(journal_prefix))
                journal_prefix = current_journal
                checkpoint_sizes.append(self.evidence_path.stat().st_size)
        finally:
            assert gate.observer is not None
            gate.observer.close()

        self.assertLessEqual(max(checkpoint_sizes) - min(checkpoint_sizes), 8)
        lines = self.records_journal_path.read_bytes().splitlines()
        self.assertEqual(len(lines), 20)
        previous_entry_sha256 = ""
        for sequence, line in enumerate(lines, start=1):
            envelope = json.loads(line)
            entry_sha256 = envelope.pop("entry_sha256")
            self.assertEqual(envelope["sequence"], sequence)
            self.assertEqual(
                envelope["previous_entry_sha256"],
                previous_entry_sha256,
            )
            canonical = json.dumps(
                envelope,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
                allow_nan=False,
            ).encode("utf-8")
            self.assertEqual(entry_sha256, hashlib.sha256(canonical).hexdigest())
            previous_entry_sha256 = entry_sha256
        evidence = json.loads(self.evidence_path.read_text(encoding="utf-8"))
        self.assertEqual(evidence["record_count"], 20)
        self.assertEqual(len(evidence["records"]), 20)

    def test_limit_reached_fails_closed_without_extra_record(self) -> None:
        environment = dict(self.environment)
        environment[ENV_OBSERVATION_MAX_RECORDS] = "1"
        gate = self._evaluate(environment=environment, max_ticks=1)
        try:
            self._observe(
                gate,
                tick=1,
                intent="HOLD",
                action="NOOP",
                executed=False,
                before="FLAT",
                after="FLAT",
            )
            with self.assertRaises(IU4ShadowObservationError) as raised:
                self._observe(
                    gate,
                    tick=2,
                    intent="HOLD",
                    action="NOOP",
                    executed=False,
                    before="FLAT",
                    after="FLAT",
                )
        finally:
            assert gate.observer is not None
            gate.observer.close()
        self.assertEqual(
            raised.exception.reason_code,
            IU4ShadowObservationReasonCode.LIMIT_REACHED,
        )
        evidence = json.loads(self.evidence_path.read_text(encoding="utf-8"))
        self.assertEqual(evidence["record_count"], 1)

    def test_shadow_divergence_is_recorded_without_mutating_source(self) -> None:
        source_before = self.coordinator.state_path.read_bytes()
        gate = self._evaluate()
        try:
            self._observe(
                gate,
                tick=1,
                intent="BUY",
                action="NOOP",
                executed=False,
                before="FLAT",
                after="FLAT",
            )
            second = self._observe(
                gate,
                tick=2,
                intent="HOLD",
                action="NOOP",
                executed=False,
                before="FLAT",
                after="FLAT",
            )
        finally:
            assert gate.observer is not None
            gate.observer.close()

        self.assertFalse(second["parity"]["position_before_equal"])
        self.assertFalse(second["parity"]["position_after_equal"])
        self.assertEqual(second["iu4"]["position_after"], "LONG")
        self.assertEqual(self.coordinator.state_path.read_bytes(), source_before)

    def test_unmatched_autonomous_exit_is_never_converted_to_entry(self) -> None:
        gate = self._evaluate()
        assert gate.observer is not None
        try:
            record = gate.observer.observe_tick(
                system_state_id="L1-STATE-1",
                tick_id=1,
                snapshot_id="SNAP-1",
                timestamp_utc="2026-08-12T12:00:01Z",
                source_intent_id="IN-AUTONOMOUS-1",
                intent_final="HOLD",
                intent_reason_code="HOLD_RAW",
                reference_price_text="100",
                legacy_execution=self._execution(
                    action="CLOSE_LONG",
                    executed=True,
                    before="LONG",
                    after="FLAT",
                    reason="SL_EXIT",
                ),
                guard_reason="guard_ok",
                s4_kill_level="NONE",
            )
        finally:
            gate.observer.close()

        self.assertTrue(record["autonomous_exit"])
        self.assertTrue(record["autonomous_exit_suppressed"])
        self.assertEqual(record["observed_intent_final"], "HOLD")
        self.assertEqual(record["iu4"]["action"], "NOOP")
        self.assertEqual(record["iu4"]["position_after"], "FLAT")

    def test_source_change_fails_closed(self) -> None:
        gate = self._evaluate()
        self.coordinator.commit_kill_transition(
            transition_event_id="IU4-OBSERVATION-KILL",
            expected_from_kill_level="NONE",
            target_kill_level="HARD",
            reason_code="TEST",
            authorization_reference="TEST",
            transition_timestamp_utc="2026-08-12T12:00:01Z",
            transition_tick_id=1,
        )
        try:
            with self.assertRaises(Exception) as raised:
                self._observe(
                    gate,
                    tick=1,
                    intent="HOLD",
                    action="NOOP",
                    executed=False,
                    before="FLAT",
                    after="FLAT",
                )
        finally:
            assert gate.observer is not None
            gate.observer.close()
        self.assertIn("source changed", str(raised.exception).lower())

    def test_external_evidence_change_is_never_overwritten(self) -> None:
        gate = self._evaluate()
        self.evidence_path.write_text("foreign-change\n", encoding="utf-8")
        try:
            with self.assertRaises(IU4ShadowObservationError) as raised:
                self._observe(
                    gate,
                    tick=1,
                    intent="HOLD",
                    action="NOOP",
                    executed=False,
                    before="FLAT",
                    after="FLAT",
                )
        finally:
            assert gate.observer is not None
            gate.observer.close()
        self.assertEqual(
            raised.exception.reason_code,
            IU4ShadowObservationReasonCode.EVIDENCE_INVALID,
        )
        self.assertEqual(
            self.evidence_path.read_text(encoding="utf-8"),
            "foreign-change\n",
        )

    def test_external_journal_append_fails_closed_without_checkpoint_advance(self) -> None:
        gate = self._evaluate()
        self._observe(
            gate,
            tick=1,
            intent="HOLD",
            action="NOOP",
            executed=False,
            before="FLAT",
            after="FLAT",
        )
        checkpoint_before = self.evidence_path.read_bytes()
        with self.records_journal_path.open("ab") as handle:
            handle.write(b"foreign-change\n")
        try:
            with self.assertRaises(IU4ShadowObservationError) as raised:
                self._observe(
                    gate,
                    tick=2,
                    intent="HOLD",
                    action="NOOP",
                    executed=False,
                    before="FLAT",
                    after="FLAT",
                )
        finally:
            assert gate.observer is not None
            gate.observer.close()

        self.assertEqual(
            raised.exception.reason_code,
            IU4ShadowObservationReasonCode.EVIDENCE_INVALID,
        )
        self.assertEqual(self.evidence_path.read_bytes(), checkpoint_before)
        checkpoint = json.loads(checkpoint_before)
        self.assertEqual(checkpoint["record_count"], 1)
        self.assertFalse(checkpoint["finalized"])

    def test_same_size_journal_mutation_fails_closed(self) -> None:
        gate = self._evaluate()
        self._observe(
            gate,
            tick=1,
            intent="HOLD",
            action="NOOP",
            executed=False,
            before="FLAT",
            after="FLAT",
        )
        with self.records_journal_path.open("r+b") as handle:
            first = handle.read(1)
            handle.seek(0)
            handle.write(b"X" if first != b"X" else b"Y")
            handle.flush()
            os.fsync(handle.fileno())
        try:
            with self.assertRaises(IU4ShadowObservationError) as raised:
                self._observe(
                    gate,
                    tick=2,
                    intent="HOLD",
                    action="NOOP",
                    executed=False,
                    before="FLAT",
                    after="FLAT",
                )
        finally:
            assert gate.observer is not None
            gate.observer.close()
        self.assertEqual(
            raised.exception.reason_code,
            IU4ShadowObservationReasonCode.EVIDENCE_INVALID,
        )

    def test_close_validates_journal_and_is_idempotent(self) -> None:
        gate = self._evaluate()
        assert gate.observer is not None
        self._observe(
            gate,
            tick=1,
            intent="HOLD",
            action="NOOP",
            executed=False,
            before="FLAT",
            after="FLAT",
        )
        gate.observer.close()
        evidence_before = self.evidence_path.read_bytes()
        gate.observer.close()
        self.assertEqual(self.evidence_path.read_bytes(), evidence_before)
        evidence = json.loads(evidence_before)
        self.assertTrue(evidence["writer_contract"]["finalized"])

    def test_close_rejects_truncated_journal_and_keeps_checkpoint(self) -> None:
        gate = self._evaluate()
        assert gate.observer is not None
        self._observe(
            gate,
            tick=1,
            intent="HOLD",
            action="NOOP",
            executed=False,
            before="FLAT",
            after="FLAT",
        )
        checkpoint_before = self.evidence_path.read_bytes()
        journal_size = self.records_journal_path.stat().st_size
        with self.records_journal_path.open("r+b") as handle:
            handle.truncate(journal_size - 1)
            handle.flush()
            os.fsync(handle.fileno())
        with self.assertRaises(IU4ShadowObservationError) as raised:
            gate.observer.close()
        self.assertEqual(
            raised.exception.reason_code,
            IU4ShadowObservationReasonCode.EVIDENCE_INVALID,
        )
        self.assertEqual(self.evidence_path.read_bytes(), checkpoint_before)

    def test_invalid_enable_limit_and_existing_evidence_fail_closed(self) -> None:
        invalid = dict(self.environment)
        invalid[ENV_OBSERVATION_ENABLED] = "true"
        with self.assertRaises(IU4ShadowObservationError):
            self._evaluate(environment=invalid)

        excessive = dict(self.environment)
        excessive[ENV_OBSERVATION_MAX_RECORDS] = str(MAX_OBSERVATION_RECORDS + 1)
        with self.assertRaises(IU4ShadowObservationError):
            self._evaluate(environment=excessive)

        self.evidence_path.write_text("foreign\n", encoding="utf-8")
        with self.assertRaises(IU4ShadowObservationError) as existing:
            self._evaluate()
        self.assertEqual(
            existing.exception.reason_code,
            IU4ShadowObservationReasonCode.EVIDENCE_INVALID,
        )

        self.evidence_path.unlink()
        self.records_journal_path.write_text("foreign\n", encoding="utf-8")
        with self.assertRaises(IU4ShadowObservationError) as journal_existing:
            self._evaluate()
        self.assertEqual(
            journal_existing.exception.reason_code,
            IU4ShadowObservationReasonCode.EVIDENCE_INVALID,
        )

    def test_observation_requires_shadow_runtime_gate(self) -> None:
        off = self.runtime_gate.__class__(
            mode="OFF",
            decision=self.runtime_gate.decision,
            running_repository_commit_sha="",
            approved_profile=None,
            coordinator=None,
        )
        with self.assertRaises(IU4ShadowObservationError) as raised:
            evaluate_iu4_shadow_observation_gate(
                repo_root=PROJECT_ROOT,
                environment=self.environment,
                runtime_gate=off,
                requested_max_ticks=1,
            )
        self.assertEqual(
            raised.exception.reason_code,
            IU4ShadowObservationReasonCode.GATE_INVALID,
        )

    def test_active_loop_rejects_observer_without_bound_runtime_gate(self) -> None:
        log_path = self.root / "l1.log"
        observation_gate = SimpleNamespace(
            enabled=True,
            observer=SimpleNamespace(close=lambda: None),
            startup_log_fields=lambda: {},
        )
        environment = {
            "L1_LOG_PATH": str(log_path),
            "L1_REQUIRE_WSL": "0",
        }
        with (
            patch.dict(os.environ, environment, clear=True),
            patch.object(
                loop,
                "load_runtime_config",
                return_value=SimpleNamespace(log_path=str(log_path)),
            ),
            redirect_stdout(io.StringIO()),
        ):
            result = loop.run_l1_loop_step1234567(
                str(self.root),
                max_ticks=1,
                iu4_shadow_observation_gate=observation_gate,
            )

        self.assertEqual(result, 1)
        self.assertIn(
            "reason=iu4_shadow_observation_binding_failed",
            log_path.read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()

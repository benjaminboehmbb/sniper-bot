#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from live_l1.core.paper_entry_throttle import PaperEntryThrottleState
from live_l1.core.paper_iu4_shadow_harness import (
    IU4ShadowIntentStepV1,
    PaperIU4ShadowDryRunHarness,
)
from live_l1.core.paper_iu4_startup_gate import (
    IU4StartupModeRequestV1,
    MODE_SHADOW,
    evaluate_iu4_startup_gate,
)
from live_l1.state.paper_artifacts import PaperAccountState, PositionStateS2FlatV2
from live_l1.state.paper_atomic_coordinator import PaperAtomicCoordinator
from live_l1.tools.paper_iu4_replay_evidence import (
    IU4ReplayEvidenceError,
    IU4ReplayEvidenceReasonCode,
    export_iu4_replay_evidence,
    load_iu4_replay_jsonl,
)
from tests.live_l1.test_paper_iu4_adapter import make_config, make_policy


D = Decimal
COMMIT_SHA = "a" * 40


class PaperIU4ReplayEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.mkdtemp(prefix="pee-iu4-replay-")
        self.root = Path(self.temporary_directory)
        self.source_root = self.root / "source"
        self.artifacts = self.root / "artifacts"
        self.artifacts.mkdir()
        self.config = make_config()
        self.policy = make_policy()
        self.coordinator = PaperAtomicCoordinator(
            self.source_root,
            self.config,
            self.policy,
            coordinator_id="IU4-REPLAY-BTCUSDT",
            symbol="BTCUSDT",
        )
        self.coordinator.initialize(
            position=PositionStateS2FlatV2(
                schema_version=2,
                system_state_id="SYSTEM-0",
                symbol="BTCUSDT",
                position="FLAT",
                side="",
                last_closed_trade_id="",
                economics_profile_id=self.config.economics_profile_id,
                economics_model_version=self.config.economics_model_version,
                config_fingerprint=self.config.config_fingerprint,
            ),
            account=PaperAccountState.initial(
                account_id="PAPER-IU4-REPLAY",
                quote_currency=self.config.quote_currency,
                starting_equity_quote=self.config.starting_equity_quote,
                utc_day="2026-08-09",
                economics_profile_id=self.config.economics_profile_id,
                economics_model_version=self.config.economics_model_version,
                config_fingerprint=self.config.config_fingerprint,
            ),
            throttle=PaperEntryThrottleState.initial(
                self.policy,
                utc_day="2026-08-09",
            ),
        )
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
        decision = evaluate_iu4_startup_gate(
            request,
            self.coordinator,
            running_repository_commit_sha=COMMIT_SHA,
        )
        self.harness = PaperIU4ShadowDryRunHarness(self.coordinator, decision)

    def tearDown(self) -> None:
        shutil.rmtree(self.temporary_directory, ignore_errors=True)

    @staticmethod
    def _step(index: int, intent: str = "BUY") -> IU4ShadowIntentStepV1:
        price = {1: D("100"), 2: D("105"), 3: D("110")}[index]
        stop = D("95") if intent == "BUY" else None
        return IU4ShadowIntentStepV1(
            schema_version=1,
            source_intent_id=f"INTENT-{index}",
            intent_final=intent,
            intent_reason_code="REPLAY_TEST",
            target_system_state_id="SYSTEM-1" if index == 2 else f"SYSTEM-{index}",
            timestamp_utc=f"2026-08-09T1{index}:00:00Z",
            tick_id=index * 100,
            reference_price=price,
            reference_stop_price=stop,
            trade_id="TRADE-1",
        )

    def _write_steps(self, *steps: IU4ShadowIntentStepV1) -> Path:
        path = self.artifacts / "replay.jsonl"
        path.write_text(
            "".join(
                json.dumps(step.to_record(), sort_keys=True, separators=(",", ":")) + "\n"
                for step in steps
            ),
            encoding="utf-8",
        )
        return path

    def _source_bytes(self) -> dict[str, bytes]:
        paths = [self.coordinator.state_path]
        paths.extend(sorted(self.coordinator.transaction_directory.glob("*.json")))
        return {
            path.relative_to(self.source_root).as_posix(): path.read_bytes()
            for path in paths
        }

    def test_strict_jsonl_loads_canonical_steps_and_metadata(self) -> None:
        source = self._write_steps(self._step(1), self._step(2, "HOLD"))
        loaded = load_iu4_replay_jsonl(source)

        self.assertEqual(loaded.line_count, 2)
        self.assertEqual(loaded.size_bytes, len(source.read_bytes()))
        self.assertEqual(loaded.sha256, hashlib.sha256(source.read_bytes()).hexdigest())
        self.assertEqual(loaded.steps[0].reference_price, D("100"))
        self.assertEqual(loaded.steps[0].to_record()["reference_price"], "100")

    def test_invalid_jsonl_shapes_fields_and_numbers_are_rejected(self) -> None:
        valid = self._step(1).to_record()
        cases = {
            "blank": b"\n",
            "malformed": b"{\n",
            "array": b"[]\n",
            "float": json.dumps({**valid, "reference_price": 100.5}).encode() + b"\n",
            "unknown": json.dumps({**valid, "unknown": 1}).encode() + b"\n",
            "missing": json.dumps({k: v for k, v in valid.items() if k != "tick_id"}).encode() + b"\n",
        }
        for name, payload in cases.items():
            with self.subTest(name=name):
                path = self.artifacts / f"{name}.jsonl"
                path.write_bytes(payload)
                with self.assertRaises(IU4ReplayEvidenceError) as caught:
                    load_iu4_replay_jsonl(path)
                self.assertEqual(
                    caught.exception.reason_code,
                    IU4ReplayEvidenceReasonCode.INPUT_INVALID,
                )

    def test_duplicate_or_non_monotone_sequence_is_rejected(self) -> None:
        first = self._step(1).to_record()
        cases = (
            {**self._step(2, "HOLD").to_record(), "source_intent_id": "INTENT-1"},
            {**self._step(2, "HOLD").to_record(), "tick_id": 100},
            {**self._step(2, "HOLD").to_record(), "timestamp_utc": first["timestamp_utc"]},
        )
        for index, second in enumerate(cases):
            with self.subTest(index=index):
                path = self.artifacts / f"order-{index}.jsonl"
                path.write_text(json.dumps(first) + "\n" + json.dumps(second) + "\n")
                with self.assertRaises(IU4ReplayEvidenceError) as caught:
                    load_iu4_replay_jsonl(path)
                self.assertEqual(
                    caught.exception.reason_code,
                    IU4ReplayEvidenceReasonCode.ORDER_INVALID,
                )

    def test_export_records_replay_hashes_outcomes_and_preserves_source(self) -> None:
        source = self._write_steps(
            self._step(1, "BUY"),
            self._step(2, "HOLD"),
            self._step(3, "SELL"),
        )
        output = self.artifacts / "evidence.json"
        before = self._source_bytes()

        result = export_iu4_replay_evidence(
            input_path=source,
            output_path=output,
            harness=self.harness,
            replay_id="REPLAY-1",
            generated_at_utc="2026-08-09T14:00:00Z",
        )

        self.assertTrue(result.newly_written)
        self.assertFalse(result.already_exists)
        self.assertEqual(self._source_bytes(), before)
        self.assertEqual(result.output_sha256, hashlib.sha256(output.read_bytes()).hexdigest())
        evidence = json.loads(output.read_text())
        fingerprint = evidence.pop("evidence_fingerprint")
        canonical = json.dumps(
            evidence, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode()
        self.assertEqual(fingerprint, hashlib.sha256(canonical).hexdigest())
        self.assertEqual(evidence["input"]["sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
        self.assertEqual(evidence["validation"]["step_count"], 3)
        self.assertEqual(evidence["validation"]["committed_step_count"], 2)
        self.assertEqual(
            [item["action"] for item in evidence["outcomes"]],
            ["OPEN_LONG", "NOOP", "CLOSE_LONG"],
        )
        self.assertEqual(evidence["outcomes"][-1]["position"], "FLAT")
        self.assertEqual(evidence["outcomes"][-1]["last_closed_trade_id"], "TRADE-1")

    def test_evidence_binds_autonomous_exit_provenance_and_commit_count(self) -> None:
        autonomous_close = IU4ShadowIntentStepV1(
            schema_version=2,
            source_intent_id="INTENT-2",
            intent_final="SELL",
            intent_reason_code="LONG_TIME_STOP_HIT",
            target_system_state_id="SYSTEM-2",
            timestamp_utc="2026-08-09T12:00:00Z",
            tick_id=200,
            reference_price=D("110"),
            reference_stop_price=None,
            trade_id="",
            source_event_kind="AUTONOMOUS_EXIT_EXECUTION",
            source_intent_final="HOLD",
            source_execution_action="CLOSE_LONG",
            source_execution_sequence=42,
        )
        source = self._write_steps(self._step(1, "BUY"), autonomous_close)
        output = self.artifacts / "autonomous-evidence.json"

        export_iu4_replay_evidence(
            input_path=source,
            output_path=output,
            harness=self.harness,
            replay_id="REPLAY-AUTONOMOUS-EXIT",
            generated_at_utc="2026-08-09T14:00:00Z",
        )
        evidence = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(evidence["validation"]["autonomous_exit_step_count"], 1)
        self.assertEqual(
            evidence["validation"]["autonomous_exit_committed_count"],
            1,
        )
        outcome = evidence["outcomes"][-1]
        self.assertEqual(outcome["action"], "CLOSE_LONG")
        self.assertEqual(
            outcome["source_event_kind"],
            "AUTONOMOUS_EXIT_EXECUTION",
        )
        self.assertEqual(outcome["source_intent_final"], "HOLD")
        self.assertEqual(outcome["source_execution_action"], "CLOSE_LONG")
        self.assertEqual(outcome["source_execution_sequence"], 42)

    def test_identical_export_is_idempotent(self) -> None:
        source = self._write_steps(self._step(1))
        output = self.artifacts / "evidence.json"
        arguments = dict(
            input_path=source,
            output_path=output,
            harness=self.harness,
            replay_id="REPLAY-IDEMPOTENT",
            generated_at_utc="2026-08-09T14:00:00Z",
        )
        first = export_iu4_replay_evidence(**arguments)
        before = output.stat()
        second = export_iu4_replay_evidence(**arguments)

        self.assertTrue(first.newly_written)
        self.assertTrue(second.already_exists)
        self.assertFalse(second.newly_written)
        self.assertEqual(second.output_sha256, first.output_sha256)
        self.assertEqual(output.stat().st_ino, before.st_ino)
        self.assertEqual(output.stat().st_mtime_ns, before.st_mtime_ns)

    def test_conflicting_evidence_is_never_overwritten(self) -> None:
        source = self._write_steps(self._step(1))
        output = self.artifacts / "evidence.json"
        output.write_bytes(b"foreign-evidence\n")
        before = output.read_bytes()

        with self.assertRaises(IU4ReplayEvidenceError) as caught:
            export_iu4_replay_evidence(
                input_path=source,
                output_path=output,
                harness=self.harness,
                replay_id="REPLAY-CONFLICT",
                generated_at_utc="2026-08-09T14:00:00Z",
            )
        self.assertEqual(
            caught.exception.reason_code,
            IU4ReplayEvidenceReasonCode.OUTPUT_CONFLICT,
        )
        self.assertEqual(output.read_bytes(), before)

    def test_publish_failure_leaves_no_partial_output(self) -> None:
        source = self._write_steps(self._step(1))
        output = self.artifacts / "evidence.json"
        before = self._source_bytes()

        with patch(
            "live_l1.tools.paper_iu4_replay_evidence.os.link",
            side_effect=OSError("injected publish interruption"),
        ):
            with self.assertRaises(IU4ReplayEvidenceError) as caught:
                export_iu4_replay_evidence(
                    input_path=source,
                    output_path=output,
                    harness=self.harness,
                    replay_id="REPLAY-INTERRUPTED",
                    generated_at_utc="2026-08-09T14:00:00Z",
                )
        self.assertEqual(
            caught.exception.reason_code,
            IU4ReplayEvidenceReasonCode.WRITE_FAILED,
        )
        self.assertFalse(output.exists())
        self.assertEqual(tuple(self.artifacts.glob("*.tmp")), ())
        self.assertEqual(self._source_bytes(), before)

    def test_unsafe_input_and_output_paths_are_rejected(self) -> None:
        source = self._write_steps(self._step(1))
        inside_source = self.source_root / "evidence.json"
        with self.assertRaises(IU4ReplayEvidenceError):
            export_iu4_replay_evidence(
                input_path=source,
                output_path=inside_source,
                harness=self.harness,
                replay_id="REPLAY-PATH",
                generated_at_utc="2026-08-09T14:00:00Z",
            )
        with self.assertRaises(IU4ReplayEvidenceError):
            export_iu4_replay_evidence(
                input_path=source,
                output_path=source,
                harness=self.harness,
                replay_id="REPLAY-PATH",
                generated_at_utc="2026-08-09T14:00:00Z",
            )
        linked = self.artifacts / "linked.jsonl"
        linked.symlink_to(source)
        with self.assertRaises(IU4ReplayEvidenceError):
            load_iu4_replay_jsonl(linked)
        output_link = self.artifacts / "evidence-link.json"
        output_link.symlink_to(self.artifacts / "missing-target.json")
        with self.assertRaises(IU4ReplayEvidenceError) as linked_output:
            export_iu4_replay_evidence(
                input_path=source,
                output_path=output_link,
                harness=self.harness,
                replay_id="REPLAY-PATH",
                generated_at_utc="2026-08-09T14:00:00Z",
            )
        self.assertEqual(
            linked_output.exception.reason_code,
            IU4ReplayEvidenceReasonCode.OUTPUT_INVALID,
        )


if __name__ == "__main__":
    unittest.main()

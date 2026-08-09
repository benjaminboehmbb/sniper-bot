#!/usr/bin/env python3

from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from live_l1.core import execution
from live_l1.state.loss_cluster import (
    LossClusterReasonCode,
    LossClusterStateError,
    LossClusterStateStore,
    LossClusterStateV2,
    SimulatedLossClusterInterruption,
)
from live_l1.tools.reconcile_runtime_state import check_loss_cluster
from live_l1.tools.recover_runtime_state import recover_runtime_state
from live_l1.tools.validate_runtime_schema import validate_runtime_schema


def make_state(
    *,
    revision: int = 1,
    pnls: tuple[object, ...] = ("1.25", "-0.5"),
    pause: int = 3,
) -> LossClusterStateV2:
    return LossClusterStateV2(
        schema_version=2,
        revision=revision,
        recent_closed_trade_pnls=pnls,
        pause_entries_remaining=pause,
        updated_utc="2026-08-09T10:00:00Z",
    )


class LossClusterStateContractTests(unittest.TestCase):
    def test_v2_roundtrip_checksum_and_decimal_strings_are_stable(self) -> None:
        state = make_state()
        record = state.to_record()
        restored = LossClusterStateV2.from_record(record)

        self.assertEqual(restored, state)
        self.assertEqual(restored.state_fingerprint, state.state_fingerprint)
        self.assertEqual(record["recent_closed_trade_pnls"], ["1.25", "-0.5"])
        self.assertEqual(len(record["state_fingerprint"]), 64)
        self.assertFalse(any(isinstance(value, float) for value in record.values()))

    def test_v2_rejects_tampering_unknown_fields_and_nonfinite_values(self) -> None:
        record = make_state().to_record()
        cases = []
        changed_pause = dict(record)
        changed_pause["pause_entries_remaining"] = 99
        cases.append(changed_pause)
        extra_field = dict(record)
        extra_field["unexpected"] = True
        cases.append(extra_field)
        nonfinite = dict(record)
        nonfinite["recent_closed_trade_pnls"] = ["NaN"]
        cases.append(nonfinite)

        for candidate in cases:
            with self.subTest(candidate=candidate):
                with self.assertRaises(LossClusterStateError):
                    LossClusterStateV2.from_record(candidate)

    def test_schema_and_integer_fields_reject_bool_and_float(self) -> None:
        for changes in (
            {"schema_version": True},
            {"schema_version": 2.0},
            {"revision": True},
            {"pause_entries_remaining": 1.0},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(LossClusterStateError):
                    replace(make_state(), **changes)

    def test_timestamp_is_normalized_to_utc_seconds(self) -> None:
        state = replace(
            make_state(),
            updated_utc="2026-08-09T12:00:00.999999+02:00",
        )

        self.assertEqual(state.updated_utc, "2026-08-09T10:00:00Z")


class LossClusterStateStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory(
            prefix="loss-cluster-store-"
        )
        self.root = Path(self.temporary_directory.name)
        self.path = self.root / "loss_cluster_state.json"
        self.store = LossClusterStateStore(self.path)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_missing_state_is_explicit_and_allowed(self) -> None:
        loaded = self.store.load()

        self.assertFalse(loaded.existed)
        self.assertIsNone(loaded.state)
        self.assertFalse(loaded.migrated_legacy_v1)

    def test_save_and_load_v2(self) -> None:
        state = make_state()
        self.store.save(state)
        loaded = self.store.load()

        self.assertTrue(loaded.existed)
        self.assertEqual(loaded.state, state)
        self.assertFalse(loaded.migrated_legacy_v1)
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)

    def test_valid_legacy_v1_loads_and_next_save_migrates_to_v2(self) -> None:
        legacy = {
            "schema_version": 1,
            "version": 1,
            "recent_closed_trade_pnls": [1.25, -0.5],
            "pause_entries_remaining": 3,
            "updated_utc": "2026-08-09T10:00:00.123456+00:00",
        }
        self.path.write_text(json.dumps(legacy), encoding="utf-8")

        loaded = self.store.load()
        self.store.save(replace(loaded.state, revision=1))
        migrated_record = json.loads(self.path.read_text(encoding="utf-8"))

        self.assertTrue(loaded.migrated_legacy_v1)
        self.assertEqual(loaded.state.revision, 0)
        self.assertEqual(
            loaded.state.recent_closed_trade_pnls,
            (Decimal("1.25"), Decimal("-0.5")),
        )
        self.assertEqual(migrated_record["schema_version"], 2)
        self.assertIn("state_fingerprint", migrated_record)

    def test_interruption_preserves_previous_complete_snapshot(self) -> None:
        previous = make_state(revision=1, pause=5)
        replacement = make_state(revision=2, pause=4)
        self.store.save(previous)
        previous_bytes = self.path.read_bytes()

        with self.assertRaises(SimulatedLossClusterInterruption):
            self.store.save(
                replacement,
                simulate_interruption_before_replace=True,
            )

        self.assertEqual(self.path.read_bytes(), previous_bytes)
        self.assertEqual(self.store.load().state, previous)
        self.assertEqual(list(self.root.glob("*.tmp")), [])
        self.assertEqual(list(self.root.glob(".*.tmp")), [])

    def test_corrupt_json_and_checksum_are_rejected(self) -> None:
        self.path.write_text("{broken", encoding="utf-8")
        with self.assertRaises(LossClusterStateError) as invalid_json:
            self.store.load()
        self.assertEqual(
            invalid_json.exception.reason_code,
            LossClusterReasonCode.JSON_INVALID,
        )

        record = make_state().to_record()
        record["pause_entries_remaining"] = 100
        self.path.write_text(json.dumps(record), encoding="utf-8")
        with self.assertRaises(LossClusterStateError) as checksum:
            self.store.load()
        self.assertEqual(
            checksum.exception.reason_code,
            LossClusterReasonCode.CHECKSUM_MISMATCH,
        )


class LossClusterExecutionIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory(
            prefix="loss-cluster-execution-"
        )
        self.root = Path(self.temporary_directory.name)
        self.path = self.root / "loss_cluster_state.json"
        self.audit_path = self.root / "execution_audit.jsonl"
        self.environment = {
            "L1_LOSS_CLUSTER_STATE_PATH": str(self.path),
            "L1_AUDIT_LOG_PATH": str(self.audit_path),
        }
        self.environment_patch = mock.patch.dict(
            execution.os.environ,
            self.environment,
            clear=False,
        )
        self.environment_patch.start()
        execution._LOSS_GATE_STATE_LOADED_PATH = None
        execution._reset_loss_gate_memory()

    def tearDown(self) -> None:
        self.environment_patch.stop()
        execution._LOSS_GATE_STATE_LOADED_PATH = None
        execution._reset_loss_gate_memory()
        self.temporary_directory.cleanup()

    def test_pause_entry_decrement_is_atomic_and_revisioned(self) -> None:
        LossClusterStateStore(self.path).save(make_state(revision=7, pause=2))

        allowed = execution._loss_gate_allows_entry()
        persisted = LossClusterStateStore(self.path).load().state

        self.assertFalse(allowed)
        self.assertEqual(persisted.pause_entries_remaining, 1)
        self.assertEqual(persisted.revision, 8)
        self.assertTrue(execution._LOSS_GATE_STATE.persistence_healthy)

    def test_checksum_corruption_blocks_entry_without_overwriting_evidence(self) -> None:
        record = make_state(revision=3, pause=0).to_record()
        record["pause_entries_remaining"] = 999
        corrupt_bytes = json.dumps(record).encode("utf-8")
        self.path.write_bytes(corrupt_bytes)

        allowed = execution._loss_gate_allows_entry()
        events = [
            json.loads(line)
            for line in self.audit_path.read_text(encoding="utf-8").splitlines()
        ]

        self.assertFalse(allowed)
        self.assertFalse(execution._LOSS_GATE_STATE.persistence_healthy)
        self.assertEqual(self.path.read_bytes(), corrupt_bytes)
        self.assertEqual(
            [event["event"] for event in events],
            ["LOSS_CLUSTER_STATE_INVALID", "LOSS_CLUSTER_FAIL_CLOSED"],
        )
        self.assertTrue(all(event["entry_fail_closed"] == 1 for event in events))

    def test_corruption_blocks_new_entry_but_never_blocks_existing_position_exit(self) -> None:
        record = make_state(revision=3, pause=0).to_record()
        record["pause_entries_remaining"] = 999
        self.path.write_text(json.dumps(record), encoding="utf-8")
        flat = SimpleNamespace(
            system_state_id="SYSTEM-FLAT",
            s2_position=SimpleNamespace(
                position="FLAT",
                side="",
                size=0.0,
                position_size=0.0,
                entry_price=None,
                entry_timestamp_utc="",
            ),
        )

        blocked = execution.apply_paper_execution(
            state=flat,
            intent_final="BUY",
            price=100.0,
            timestamp_utc="2026-08-09T10:00:00Z",
        )

        self.assertFalse(blocked.executed)
        self.assertEqual(blocked.reason, "LOSS_CLUSTER_GATE_BLOCKED_ENTRY")
        self.assertEqual(flat.s2_position.position, "FLAT")

        execution._LOSS_GATE_STATE_LOADED_PATH = None
        execution._reset_loss_gate_memory()
        opened = SimpleNamespace(
            system_state_id="SYSTEM-OPEN",
            s2_position=SimpleNamespace(
                position="LONG",
                side="long",
                size=1.0,
                position_size=1.0,
                entry_price=100.0,
                entry_timestamp_utc="2026-08-09T09:00:00Z",
            ),
        )
        closed = execution.apply_paper_execution(
            state=opened,
            intent_final="SELL",
            price=101.0,
            timestamp_utc="2026-08-09T10:00:00Z",
            trade_log_path=str(self.root / "trades.jsonl"),
        )

        self.assertTrue(closed.executed)
        self.assertEqual(closed.action, "CLOSE_LONG")
        self.assertEqual(opened.s2_position.position, "FLAT")

    def test_persistence_failure_after_close_blocks_future_entries(self) -> None:
        error = LossClusterStateError(
            LossClusterReasonCode.IO_FAILURE,
            "simulated write failure",
        )
        with mock.patch.object(
            execution.LossClusterStateStore,
            "save",
            side_effect=error,
        ):
            execution._loss_gate_register_closed_trade(-1.0)

        self.assertFalse(execution._LOSS_GATE_STATE.persistence_healthy)
        self.assertFalse(execution._loss_gate_allows_entry())
        self.assertFalse(self.path.exists())

    def test_five_losses_in_ten_triggers_durable_pause_and_clears_window(self) -> None:
        pnls = (-1.0, 1.0, -2.0, 2.0, -3.0, 3.0, -4.0, 4.0, -5.0, 5.0)
        for pnl in pnls:
            execution._loss_gate_register_closed_trade(pnl)

        persisted = LossClusterStateStore(self.path).load().state

        self.assertEqual(persisted.pause_entries_remaining, 35)
        self.assertEqual(persisted.recent_closed_trade_pnls, ())
        self.assertEqual(persisted.revision, 10)

    def test_environment_path_change_reloads_independent_state(self) -> None:
        LossClusterStateStore(self.path).save(make_state(revision=1, pause=2))
        self.assertFalse(execution._loss_gate_allows_entry())
        other_path = self.root / "other.json"
        LossClusterStateStore(other_path).save(make_state(revision=4, pause=0))

        with mock.patch.dict(
            execution.os.environ,
            {"L1_LOSS_CLUSTER_STATE_PATH": str(other_path)},
            clear=False,
        ):
            self.assertTrue(execution._loss_gate_allows_entry())
            self.assertEqual(execution._LOSS_GATE_STATE.revision, 4)


class LossClusterToolingTests(unittest.TestCase):
    def test_reconciliation_validates_checksum_and_accepts_legacy(self) -> None:
        with tempfile.TemporaryDirectory(prefix="loss-cluster-tools-") as root_text:
            root = Path(root_text)
            path = root / "loss.json"
            LossClusterStateStore(path).save(make_state())
            valid = check_loss_cluster(path)
            record = json.loads(path.read_text(encoding="utf-8"))
            record["pause_entries_remaining"] = 99
            path.write_text(json.dumps(record), encoding="utf-8")
            corrupt = check_loss_cluster(path)
            legacy_path = root / "legacy.json"
            legacy_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "version": 1,
                        "recent_closed_trade_pnls": [-1.0],
                        "pause_entries_remaining": 2,
                        "updated_utc": "2026-08-09T10:00:00+00:00",
                    }
                ),
                encoding="utf-8",
            )
            legacy = check_loss_cluster(legacy_path)

        self.assertTrue(valid.passed)
        self.assertFalse(corrupt.passed)
        self.assertIn(LossClusterReasonCode.CHECKSUM_MISMATCH, corrupt.detail)
        self.assertTrue(legacy.passed)
        self.assertIn("legacy_migration=1", legacy.detail)

    def test_recovery_loads_valid_v2_but_not_corrupt_state(self) -> None:
        with tempfile.TemporaryDirectory(prefix="loss-cluster-recovery-") as root_text:
            root = Path(root_text)
            path = root / "loss.json"
            audit = root / "audit.jsonl"
            LossClusterStateStore(path).save(make_state(pause=6))
            valid = recover_runtime_state(
                audit_log_path=audit,
                loss_cluster_state_path=path,
            )
            record = json.loads(path.read_text(encoding="utf-8"))
            record["pause_entries_remaining"] = 0
            path.write_text(json.dumps(record), encoding="utf-8")
            corrupt = recover_runtime_state(
                audit_log_path=audit,
                loss_cluster_state_path=path,
            )

        self.assertEqual(valid.pause_entries_remaining, 6)
        self.assertEqual(valid.loss_cluster_state_loaded, 1)
        self.assertEqual(corrupt.pause_entries_remaining, 0)
        self.assertEqual(corrupt.loss_cluster_state_loaded, 0)

    def test_runtime_schema_validation_rejects_checksum_corruption(self) -> None:
        with tempfile.TemporaryDirectory(prefix="loss-cluster-schema-") as root_text:
            root = Path(root_text)
            path = root / "loss.json"
            record = make_state().to_record()
            record["pause_entries_remaining"] = 99
            path.write_text(json.dumps(record), encoding="utf-8")

            checks = validate_runtime_schema(
                audit_path=root / "audit.jsonl",
                trades_path=root / "trades.jsonl",
                s2_path=root / "s2.jsonl",
                loss_path=path,
                s4_path=root / "s4.jsonl",
            )

        loss_check = next(
            check for check in checks if check.name == "loss_cluster_state_schema"
        )
        self.assertFalse(loss_check.passed)
        self.assertIn(LossClusterReasonCode.CHECKSUM_MISMATCH, loss_check.detail)


if __name__ == "__main__":
    unittest.main()

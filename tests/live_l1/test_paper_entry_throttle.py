#!/usr/bin/env python3

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from live_l1.core.paper_entry_throttle import (
    AcceptedEntryEventV1,
    EntryThrottleReasonCode,
    PaperEntryThrottleError,
    PaperEntryThrottlePolicy,
    PaperEntryThrottleState,
    apply_accepted_entry,
    evaluate_entry_throttle,
)
from live_l1.state.paper_entry_throttle import (
    EntryThrottleStoreReasonCode,
    PaperEntryThrottleStore,
    PaperEntryThrottleStoreError,
    SimulatedEntryThrottleInterruption,
)


def make_policy(**overrides: object) -> PaperEntryThrottlePolicy:
    values: dict[str, object] = {
        "schema_version": 1,
        "policy_model_version": "PEE_RATE_V1",
        "policy_profile_id": "TEST_RATE_PROFILE",
        "max_entries_per_utc_day": 10,
        "max_entries_per_rolling_window": 3,
        "rolling_window_seconds": 3600,
        "min_reentry_cooldown_seconds": 60,
    }
    values.update(overrides)
    return PaperEntryThrottlePolicy(**values)


def make_event(
    state: PaperEntryThrottleState,
    policy: PaperEntryThrottlePolicy,
    *,
    event_id: str,
    timestamp: str,
) -> AcceptedEntryEventV1:
    return AcceptedEntryEventV1(
        schema_version=1,
        entry_sequence=state.total_accepted_entry_count + 1,
        entry_event_id=event_id,
        previous_entry_event_id=state.last_entry_event_id,
        entry_timestamp_utc=timestamp,
        policy_model_version=policy.policy_model_version,
        policy_profile_id=policy.policy_profile_id,
        policy_fingerprint=policy.policy_fingerprint,
    )


class PaperEntryThrottleContractTests(unittest.TestCase):
    def test_policy_roundtrip_and_fingerprint_are_canonical(self) -> None:
        policy = make_policy()
        restored = PaperEntryThrottlePolicy.from_record(policy.to_record())

        self.assertEqual(restored, policy)
        self.assertEqual(restored.policy_fingerprint, policy.policy_fingerprint)
        self.assertEqual(len(policy.policy_fingerprint), 64)

    def test_policy_rejects_invalid_limits_and_schema(self) -> None:
        for overrides in (
            {"schema_version": 2},
            {"schema_version": True},
            {"max_entries_per_utc_day": 0},
            {"max_entries_per_rolling_window": True},
            {"rolling_window_seconds": 0},
            {"min_reentry_cooldown_seconds": 0},
        ):
            with self.subTest(overrides=overrides):
                with self.assertRaises(PaperEntryThrottleError) as caught:
                    make_policy(**overrides)
                self.assertEqual(
                    caught.exception.reason_code,
                    EntryThrottleReasonCode.CONFIG_INVALID,
                )

    def test_initial_state_roundtrip_is_strict_and_empty(self) -> None:
        policy = make_policy()
        state = PaperEntryThrottleState.initial(policy, utc_day="2026-08-09")
        restored = PaperEntryThrottleState.from_record(state.to_record())

        self.assertEqual(restored, state)
        self.assertEqual(restored.entries_today, 0)
        self.assertEqual(restored.recent_entry_events, ())
        self.assertEqual(restored.state_fingerprint, state.state_fingerprint)

    def test_event_timestamp_is_normalized_to_utc(self) -> None:
        policy = make_policy()
        state = PaperEntryThrottleState.initial(policy, utc_day="2026-08-09")
        event = make_event(
            state,
            policy,
            event_id="ENTRY-1",
            timestamp="2026-08-09T12:00:00+02:00",
        )

        self.assertEqual(event.entry_timestamp_utc, "2026-08-09T10:00:00Z")

    def test_daily_limit_blocks_entry_but_never_exit(self) -> None:
        policy = make_policy(
            max_entries_per_utc_day=2,
            max_entries_per_rolling_window=20,
        )
        state = PaperEntryThrottleState.initial(policy, utc_day="2026-08-09")
        state = apply_accepted_entry(
            state,
            policy,
            make_event(state, policy, event_id="ENTRY-1", timestamp="2026-08-09T10:00:00Z"),
        )
        state = apply_accepted_entry(
            state,
            policy,
            make_event(state, policy, event_id="ENTRY-2", timestamp="2026-08-09T10:01:00Z"),
        )

        decision = evaluate_entry_throttle(
            state,
            policy,
            entry_timestamp_utc="2026-08-09T10:02:00Z",
        )

        self.assertFalse(decision.entry_allowed)
        self.assertTrue(decision.exit_allowed)
        self.assertEqual(
            decision.reason_codes,
            (EntryThrottleReasonCode.DAILY_ENTRY_LIMIT,),
        )
        self.assertEqual(decision.disable_until_utc, "2026-08-10T00:00:00Z")

    def test_utc_day_boundary_resets_daily_count(self) -> None:
        policy = make_policy(max_entries_per_utc_day=1)
        state = PaperEntryThrottleState.initial(policy, utc_day="2026-08-09")
        state = apply_accepted_entry(
            state,
            policy,
            make_event(state, policy, event_id="ENTRY-1", timestamp="2026-08-09T23:58:00Z"),
        )

        decision = evaluate_entry_throttle(
            state,
            policy,
            entry_timestamp_utc="2026-08-10T00:00:00Z",
        )
        next_state = apply_accepted_entry(
            state,
            policy,
            make_event(state, policy, event_id="ENTRY-2", timestamp="2026-08-10T00:00:00Z"),
        )

        self.assertTrue(decision.entry_allowed)
        self.assertEqual(decision.entries_today, 0)
        self.assertEqual(next_state.utc_day, "2026-08-10")
        self.assertEqual(next_state.entries_today, 1)

    def test_rolling_window_blocks_then_opens_at_exact_boundary(self) -> None:
        policy = make_policy(
            max_entries_per_rolling_window=2,
            min_reentry_cooldown_seconds=60,
        )
        state = PaperEntryThrottleState.initial(policy, utc_day="2026-08-09")
        state = apply_accepted_entry(
            state,
            policy,
            make_event(state, policy, event_id="ENTRY-1", timestamp="2026-08-09T10:00:00Z"),
        )
        state = apply_accepted_entry(
            state,
            policy,
            make_event(state, policy, event_id="ENTRY-2", timestamp="2026-08-09T10:30:00Z"),
        )

        blocked = evaluate_entry_throttle(
            state,
            policy,
            entry_timestamp_utc="2026-08-09T10:59:59Z",
        )
        boundary = evaluate_entry_throttle(
            state,
            policy,
            entry_timestamp_utc="2026-08-09T11:00:00Z",
        )

        self.assertEqual(
            blocked.reason_codes,
            (EntryThrottleReasonCode.ROLLING_ENTRY_LIMIT,),
        )
        self.assertEqual(blocked.disable_until_utc, "2026-08-09T11:00:00Z")
        self.assertTrue(boundary.entry_allowed)
        self.assertEqual(boundary.entries_in_rolling_window, 1)

    def test_cooldown_opens_at_exact_boundary(self) -> None:
        policy = make_policy(min_reentry_cooldown_seconds=180)
        state = PaperEntryThrottleState.initial(policy, utc_day="2026-08-09")
        state = apply_accepted_entry(
            state,
            policy,
            make_event(state, policy, event_id="ENTRY-1", timestamp="2026-08-09T10:00:00Z"),
        )

        blocked = evaluate_entry_throttle(
            state,
            policy,
            entry_timestamp_utc="2026-08-09T10:02:59Z",
        )
        boundary = evaluate_entry_throttle(
            state,
            policy,
            entry_timestamp_utc="2026-08-09T10:03:00Z",
        )

        self.assertEqual(
            blocked.reason_codes,
            (EntryThrottleReasonCode.REENTRY_COOLDOWN,),
        )
        self.assertEqual(blocked.disable_until_utc, "2026-08-09T10:03:00Z")
        self.assertTrue(boundary.entry_allowed)

    def test_multiple_active_limits_have_stable_order_and_latest_release(self) -> None:
        policy = make_policy(
            max_entries_per_utc_day=1,
            max_entries_per_rolling_window=1,
            rolling_window_seconds=3600,
            min_reentry_cooldown_seconds=7200,
        )
        state = PaperEntryThrottleState.initial(policy, utc_day="2026-08-09")
        state = apply_accepted_entry(
            state,
            policy,
            make_event(state, policy, event_id="ENTRY-1", timestamp="2026-08-09T10:00:00Z"),
        )

        decision = evaluate_entry_throttle(
            state,
            policy,
            entry_timestamp_utc="2026-08-09T10:30:00Z",
        )

        self.assertEqual(
            decision.reason_codes,
            (
                EntryThrottleReasonCode.DAILY_ENTRY_LIMIT,
                EntryThrottleReasonCode.ROLLING_ENTRY_LIMIT,
                EntryThrottleReasonCode.REENTRY_COOLDOWN,
            ),
        )
        self.assertEqual(decision.disable_until_utc, "2026-08-10T00:00:00Z")

    def test_policy_mismatch_and_time_regression_fail_closed(self) -> None:
        policy = make_policy()
        state = PaperEntryThrottleState.initial(policy, utc_day="2026-08-09")
        state = apply_accepted_entry(
            state,
            policy,
            make_event(state, policy, event_id="ENTRY-1", timestamp="2026-08-09T10:00:00Z"),
        )
        changed_policy = replace(policy, max_entries_per_utc_day=9)

        mismatch = evaluate_entry_throttle(
            state,
            changed_policy,
            entry_timestamp_utc="2026-08-09T10:01:00Z",
        )
        regression = evaluate_entry_throttle(
            state,
            policy,
            entry_timestamp_utc="2026-08-09T09:59:59Z",
        )

        self.assertEqual(
            mismatch.reason_codes,
            (EntryThrottleReasonCode.POLICY_MISMATCH,),
        )
        self.assertTrue(mismatch.exit_allowed)
        self.assertEqual(
            regression.reason_codes,
            (EntryThrottleReasonCode.STATE_INVALID,),
        )
        self.assertTrue(regression.exit_allowed)

    def test_blocked_apply_does_not_create_a_new_state(self) -> None:
        policy = make_policy(max_entries_per_utc_day=1)
        initial = PaperEntryThrottleState.initial(policy, utc_day="2026-08-09")
        first = apply_accepted_entry(
            initial,
            policy,
            make_event(initial, policy, event_id="ENTRY-1", timestamp="2026-08-09T10:00:00Z"),
        )
        blocked_event = make_event(
            first,
            policy,
            event_id="ENTRY-2",
            timestamp="2026-08-09T10:01:00Z",
        )

        with self.assertRaises(PaperEntryThrottleError) as caught:
            apply_accepted_entry(first, policy, blocked_event)

        self.assertEqual(
            caught.exception.reason_code,
            EntryThrottleReasonCode.DAILY_ENTRY_LIMIT,
        )
        self.assertEqual(first.total_accepted_entry_count, 1)

    def test_recent_events_are_pruned_after_rolling_window(self) -> None:
        policy = make_policy(rolling_window_seconds=3600)
        state = PaperEntryThrottleState.initial(policy, utc_day="2026-08-09")
        state = apply_accepted_entry(
            state,
            policy,
            make_event(state, policy, event_id="ENTRY-1", timestamp="2026-08-09T10:00:00Z"),
        )
        state = apply_accepted_entry(
            state,
            policy,
            make_event(state, policy, event_id="ENTRY-2", timestamp="2026-08-09T11:00:00Z"),
        )

        self.assertEqual(
            tuple(event.entry_event_id for event in state.recent_entry_events),
            ("ENTRY-2",),
        )
        self.assertEqual(state.total_accepted_entry_count, 2)


class PaperEntryThrottleStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.mkdtemp(prefix="pee-rate-test-")
        self.root = Path(self.temporary_directory)
        self.policy = make_policy()
        self.initial = PaperEntryThrottleState.initial(
            self.policy,
            utc_day="2026-08-09",
        )
        self.store = PaperEntryThrottleStore(self.root, self.policy)
        self.store.initialize(self.initial)

    def tearDown(self) -> None:
        shutil.rmtree(self.temporary_directory, ignore_errors=True)

    def _event(
        self,
        state: PaperEntryThrottleState,
        *,
        event_id: str = "ENTRY-1",
        timestamp: str = "2026-08-09T10:00:00Z",
    ) -> AcceptedEntryEventV1:
        return make_event(
            state,
            self.policy,
            event_id=event_id,
            timestamp=timestamp,
        )

    def test_initialization_is_idempotent_only_for_identical_state(self) -> None:
        self.assertEqual(self.store.initialize(self.initial), self.initial)

        with self.assertRaises(PaperEntryThrottleStoreError) as caught:
            self.store.initialize(replace(self.initial, utc_day="2026-08-10"))
        self.assertEqual(
            caught.exception.reason_code,
            EntryThrottleStoreReasonCode.STATE_ALREADY_INITIALIZED,
        )

        nonempty = apply_accepted_entry(
            self.initial,
            self.policy,
            self._event(self.initial),
        )
        new_store = PaperEntryThrottleStore(self.root / "nonempty", self.policy)
        with self.assertRaises(PaperEntryThrottleStoreError) as nonempty_caught:
            new_store.initialize(nonempty)
        self.assertEqual(
            nonempty_caught.exception.reason_code,
            EntryThrottleStoreReasonCode.STATE_AHEAD_OF_JOURNAL,
        )

    def test_commit_writes_journal_then_state_exactly_once(self) -> None:
        event = self._event(self.initial)
        first = self.store.commit_entry(event)
        second = self.store.commit_entry(event)

        self.assertTrue(first.newly_committed)
        self.assertTrue(second.already_committed)
        self.assertEqual(first.state, second.state)
        self.assertEqual(second.state.total_accepted_entry_count, 1)
        self.assertEqual(len(list(self.store.event_directory.glob("*.json"))), 1)
        self.assertEqual(list(self.root.rglob("*.tmp")), [])

    def test_interruption_is_recovered_exactly_once(self) -> None:
        event = self._event(self.initial)
        with self.assertRaises(SimulatedEntryThrottleInterruption):
            self.store.commit_entry(
                event,
                simulate_interruption_after_journal=True,
            )

        report_before = self.store.reconciliation_report()
        self.assertFalse(report_before.consistent)
        self.assertFalse(report_before.entry_allowed)
        self.assertTrue(report_before.exit_allowed)
        self.assertEqual(
            report_before.reason_codes,
            (EntryThrottleStoreReasonCode.RECOVERY_REQUIRED,),
        )

        first_recovery = self.store.recover()
        second_recovery = self.store.recover()
        duplicate = self.store.commit_entry(event)

        self.assertEqual(first_recovery.recovered_entry_count, 1)
        self.assertEqual(second_recovery.recovered_entry_count, 0)
        self.assertTrue(duplicate.already_committed)
        self.assertEqual(first_recovery.state, second_recovery.state)
        self.assertEqual(first_recovery.state, duplicate.state)

    def test_repeated_event_identity_with_changed_data_is_conflict(self) -> None:
        event = self._event(self.initial)
        self.store.commit_entry(event)
        conflicting = replace(event, entry_timestamp_utc="2026-08-09T10:05:00Z")

        with self.assertRaises(PaperEntryThrottleStoreError) as caught:
            self.store.commit_entry(conflicting)

        self.assertEqual(
            caught.exception.reason_code,
            EntryThrottleStoreReasonCode.JOURNAL_CONFLICT,
        )

    def test_old_duplicate_after_later_commit_is_idempotent(self) -> None:
        first_event = self._event(self.initial)
        first = self.store.commit_entry(first_event).state
        second_event = self._event(
            first,
            event_id="ENTRY-2",
            timestamp="2026-08-09T10:01:00Z",
        )
        second = self.store.commit_entry(second_event).state

        duplicate = self.store.commit_entry(first_event)

        self.assertTrue(duplicate.already_committed)
        self.assertEqual(duplicate.state, second)
        self.assertEqual(self.store.load_state(), second)

    def test_duplicate_event_id_under_new_sequence_is_conflict(self) -> None:
        first = self.store.commit_entry(self._event(self.initial)).state
        duplicate_identity = self._event(
            first,
            event_id="ENTRY-1",
            timestamp="2026-08-09T10:01:00Z",
        )

        with self.assertRaises(PaperEntryThrottleStoreError) as caught:
            self.store.commit_entry(duplicate_identity)

        self.assertEqual(
            caught.exception.reason_code,
            EntryThrottleStoreReasonCode.JOURNAL_CONFLICT,
        )
        self.assertEqual(len(list(self.store.event_directory.glob("*.json"))), 1)

    def test_blocked_event_writes_nothing(self) -> None:
        policy = make_policy(max_entries_per_utc_day=1)
        root = self.root / "blocked"
        initial = PaperEntryThrottleState.initial(policy, utc_day="2026-08-09")
        store = PaperEntryThrottleStore(root, policy)
        store.initialize(initial)
        first_event = make_event(
            initial,
            policy,
            event_id="ENTRY-1",
            timestamp="2026-08-09T10:00:00Z",
        )
        first = store.commit_entry(first_event).state
        blocked_event = make_event(
            first,
            policy,
            event_id="ENTRY-2",
            timestamp="2026-08-09T10:01:00Z",
        )

        with self.assertRaises(PaperEntryThrottleError) as caught:
            store.commit_entry(blocked_event)

        self.assertEqual(
            caught.exception.reason_code,
            EntryThrottleReasonCode.DAILY_ENTRY_LIMIT,
        )
        self.assertEqual(len(list(store.event_directory.glob("*.json"))), 1)
        self.assertEqual(store.load_state(), first)

    def test_corrupt_state_and_policy_mismatch_fail_closed_keep_exits(self) -> None:
        self.store.state_path.write_text("{broken", encoding="utf-8")
        corrupt = self.store.reconciliation_report()

        self.assertFalse(corrupt.consistent)
        self.assertFalse(corrupt.entry_allowed)
        self.assertTrue(corrupt.exit_allowed)
        self.assertEqual(
            corrupt.reason_codes,
            (EntryThrottleStoreReasonCode.JSON_INVALID,),
        )

        other_root = self.root / "mismatch"
        original_store = PaperEntryThrottleStore(other_root, self.policy)
        original_store.initialize(self.initial)
        changed_policy = replace(self.policy, max_entries_per_utc_day=9)
        mismatch_store = PaperEntryThrottleStore(other_root, changed_policy)
        mismatch = mismatch_store.reconciliation_report()

        self.assertFalse(mismatch.consistent)
        self.assertFalse(mismatch.entry_allowed)
        self.assertTrue(mismatch.exit_allowed)
        self.assertEqual(
            mismatch.reason_codes,
            (EntryThrottleReasonCode.POLICY_MISMATCH,),
        )

    def test_unknown_envelope_schema_fails_closed(self) -> None:
        result = self.store.commit_entry(self._event(self.initial))
        record = json.loads(result.journal_path.read_text(encoding="utf-8"))
        record["schema_version"] = 2
        result.journal_path.write_text(json.dumps(record), encoding="utf-8")

        report = self.store.reconciliation_report()

        self.assertFalse(report.consistent)
        self.assertFalse(report.entry_allowed)
        self.assertTrue(report.exit_allowed)
        self.assertEqual(
            report.reason_codes,
            (EntryThrottleReasonCode.STATE_INVALID,),
        )

    def test_non_reproducible_journal_transition_fails_closed(self) -> None:
        policy = make_policy(
            rolling_window_seconds=60,
            min_reentry_cooldown_seconds=60,
        )
        root = self.root / "tampered-transition"
        initial = PaperEntryThrottleState.initial(policy, utc_day="2026-08-09")
        store = PaperEntryThrottleStore(root, policy)
        store.initialize(initial)
        first_event = make_event(
            initial,
            policy,
            event_id="ENTRY-1",
            timestamp="2026-08-09T10:00:00Z",
        )
        first = store.commit_entry(first_event).state
        second_event = make_event(
            first,
            policy,
            event_id="ENTRY-2",
            timestamp="2026-08-09T10:01:00Z",
        )
        second_result = store.commit_entry(second_event)
        record = json.loads(second_result.journal_path.read_text(encoding="utf-8"))
        record["state_after"]["entries_today"] = 1
        second_result.journal_path.write_text(json.dumps(record), encoding="utf-8")

        report = store.reconciliation_report()

        self.assertFalse(report.consistent)
        self.assertFalse(report.entry_allowed)
        self.assertTrue(report.exit_allowed)
        self.assertEqual(
            report.reason_codes,
            (EntryThrottleStoreReasonCode.JOURNAL_CONFLICT,),
        )

    def test_state_ahead_of_empty_journal_is_rejected(self) -> None:
        event = self._event(self.initial)
        state_after = apply_accepted_entry(self.initial, self.policy, event)
        self.store.state_path.write_text(
            json.dumps(state_after.to_record()),
            encoding="utf-8",
        )

        report = self.store.reconciliation_report()
        self.assertFalse(report.consistent)
        self.assertEqual(
            report.reason_codes,
            (EntryThrottleStoreReasonCode.STATE_AHEAD_OF_JOURNAL,),
        )
        with self.assertRaises(PaperEntryThrottleStoreError) as caught:
            self.store.recover()
        self.assertEqual(
            caught.exception.reason_code,
            EntryThrottleStoreReasonCode.STATE_AHEAD_OF_JOURNAL,
        )

    def test_two_event_chain_reconciles_after_restart(self) -> None:
        first = self.store.commit_entry(self._event(self.initial)).state
        second_event = self._event(
            first,
            event_id="ENTRY-2",
            timestamp="2026-08-09T10:01:00Z",
        )
        second = self.store.commit_entry(second_event).state
        restarted = PaperEntryThrottleStore(self.root, self.policy)

        report = restarted.reconciliation_report()

        self.assertTrue(report.consistent)
        self.assertTrue(report.entry_allowed)
        self.assertTrue(report.exit_allowed)
        self.assertEqual(report.state_entry_count, 2)
        self.assertEqual(report.journal_entry_count, 2)
        self.assertEqual(restarted.load_state(), second)


if __name__ == "__main__":
    unittest.main()

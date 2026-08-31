"""Non-authoritative tests for isolated I6 loss-cluster transitions.

Classification: NONAUTHORITATIVE_P2B_PATH_A_TEST_CLOSURE_CANDIDATE.
This module grants no test, evidence, acceptance, publication, execution,
live, or exchange authority.
"""

import unittest
from dataclasses import replace
from decimal import Decimal

from live_l1.state.loss_cluster import (
    LOSS_CLUSTER_SCHEMA_VERSION,
    LossClusterStateError,
    LossClusterStateV2,
    apply_loss_cluster_close,
    apply_loss_cluster_entry_veto,
)


CLASSIFICATION = "NONAUTHORITATIVE_P2B_PATH_A_TEST_CLOSURE_CANDIDATE"
D = Decimal
POLICY_ID = "LOSS-CLUSTER-I6"
POLICY_FINGERPRINT = "a" * 64
T0 = "2026-08-31T08:00:00Z"
T1 = "2026-08-31T08:00:01Z"


def make_state(revision=0, pnls=(), pause=0, updated_utc=T0):
    return LossClusterStateV2(
        schema_version=LOSS_CLUSTER_SCHEMA_VERSION,
        revision=revision,
        recent_closed_trade_pnls=pnls,
        pause_entries_remaining=pause,
        updated_utc=updated_utc,
    )


def close(state, **changes):
    values = {
        "net_pnl_quote": D("1"),
        "updated_utc": T1,
        "policy_id": POLICY_ID,
        "policy_fingerprint": POLICY_FINGERPRINT,
        "lookback": 10,
        "loss_threshold": 5,
        "pause_entries": 3,
    }
    values.update(changes)
    return apply_loss_cluster_close(state, **values)


def veto(state, **changes):
    values = {
        "updated_utc": T1,
        "policy_id": POLICY_ID,
        "policy_fingerprint": POLICY_FINGERPRINT,
    }
    values.update(changes)
    return apply_loss_cluster_entry_veto(state, **values)


class ApplyLossClusterCloseTests(unittest.TestCase):
    def test_pure_revisioned_append_and_determinism(self):
        initial = make_state(pnls=(D("-1"),), pause=1)
        snapshot = initial.to_record()
        first = close(initial, net_pnl_quote=D("1.25"))
        second = close(initial, net_pnl_quote=D("1.25"))
        self.assertEqual(initial.to_record(), snapshot)
        self.assertEqual(first, second)
        self.assertIsNot(first, initial)
        self.assertEqual(first.revision, initial.revision + 1)
        self.assertEqual(first.recent_closed_trade_pnls, (D("-1"), D("1.25")))
        self.assertEqual(first.pause_entries_remaining, 1)
        self.assertEqual(first.updated_utc, T1)

    def test_lookback_is_exactly_bounded(self):
        initial = make_state(pnls=(D("1"), D("2"), D("3")))
        result = close(
            initial, net_pnl_quote=D("4"), lookback=2, loss_threshold=2
        )
        self.assertEqual(result.recent_closed_trade_pnls, (D("3"), D("4")))
        self.assertEqual(result.revision, 1)

    def test_threshold_activates_or_preserves_pause_and_resets_pnls(self):
        initial = make_state(pnls=(D("-1"), D("-2"), D("3"), D("-4")))
        activated = close(
            initial,
            net_pnl_quote=D("-5"),
            lookback=5,
            loss_threshold=4,
            pause_entries=3,
        )
        self.assertEqual(activated.recent_closed_trade_pnls, ())
        self.assertEqual(activated.pause_entries_remaining, 3)
        self.assertEqual(activated.revision, 1)
        preserved = close(
            replace(initial, pause_entries_remaining=7),
            net_pnl_quote=D("-5"),
            lookback=5,
            loss_threshold=4,
            pause_entries=3,
        )
        self.assertEqual(preserved.recent_closed_trade_pnls, ())
        self.assertEqual(preserved.pause_entries_remaining, 7)

    def test_policy_fingerprint_utc_and_numeric_boundaries(self):
        initial = make_state()
        for changes in (
            {"policy_id": ""},
            {"policy_id": 1},
            {"policy_fingerprint": "bad"},
            {"updated_utc": ""},
            {"updated_utc": "2026-08-31T08:00:00"},
            {"net_pnl_quote": True},
            {"net_pnl_quote": 1.0},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(LossClusterStateError):
                    close(initial, **changes)
        normalized = close(
            initial, updated_utc="2026-08-31T10:00:01.900000+02:00"
        )
        self.assertEqual(normalized.updated_utc, T1)
        self.assertEqual(
            close(initial, policy_id="  LOSS-CLUSTER-I6  "),
            close(initial),
        )

    def test_invalid_lookback_threshold_and_pause_values(self):
        initial = make_state()
        for changes in (
            {"lookback": 0},
            {"lookback": True},
            {"loss_threshold": 0},
            {"loss_threshold": True},
            {"pause_entries": 0},
            {"pause_entries": True},
            {"lookback": 2, "loss_threshold": 3},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(LossClusterStateError):
                    close(initial, **changes)


class ApplyLossClusterEntryVetoTests(unittest.TestCase):
    def test_pure_revisioned_token_consumption_and_determinism(self):
        initial = make_state(4, (D("-1"), D("2")), 2)
        snapshot = initial.to_record()
        first = veto(initial)
        second = veto(initial)
        self.assertEqual(initial.to_record(), snapshot)
        self.assertEqual(first, second)
        self.assertIsNot(first, initial)
        self.assertEqual(first.revision, 5)
        self.assertEqual(first.pause_entries_remaining, 1)
        self.assertEqual(first.recent_closed_trade_pnls, initial.recent_closed_trade_pnls)
        self.assertEqual(first.updated_utc, T1)

    def test_inactive_pause_and_invalid_bindings(self):
        active = make_state(pause=1)
        with self.assertRaises(LossClusterStateError):
            veto(make_state())
        for changes in (
            {"policy_id": ""},
            {"policy_id": 1},
            {"policy_fingerprint": "bad"},
            {"updated_utc": ""},
            {"updated_utc": "2026-08-31T08:00:01"},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(LossClusterStateError):
                    veto(active, **changes)
        normalized = veto(
            active, updated_utc="2026-08-31T10:00:01.900000+02:00"
        )
        self.assertEqual(normalized.updated_utc, T1)
        self.assertEqual(
            veto(active, policy_id="  LOSS-CLUSTER-I6  "),
            veto(active),
        )


class LossClusterStateV2RecordTests(unittest.TestCase):
    def test_canonical_existing_record_roundtrip(self):
        state = make_state(7, (D("-1.25"), D("2"), D("0")), 2)
        record = state.to_record()
        self.assertEqual(record["schema_version"], 2)
        self.assertEqual(record["version"], 2)
        self.assertEqual(record["recent_closed_trade_pnls"], ["-1.25", "2", "0"])
        self.assertEqual(len(record["state_fingerprint"]), 64)
        rebuilt = LossClusterStateV2.from_record(record)
        self.assertEqual(rebuilt, state)
        self.assertEqual(rebuilt.to_record(), record)
        self.assertEqual(make_state().state_fingerprint, make_state().state_fingerprint)

    def test_non_string_and_noncanonical_decimal_records(self):
        record = make_state(pnls=(D("1"),)).to_record()
        non_string = dict(record)
        non_string["recent_closed_trade_pnls"] = [1]
        noncanonical = dict(record)
        noncanonical["recent_closed_trade_pnls"] = ["1.0"]
        for candidate in (non_string, noncanonical):
            with self.subTest(candidate=candidate["recent_closed_trade_pnls"]):
                with self.assertRaises(LossClusterStateError):
                    LossClusterStateV2.from_record(candidate)

    def test_missing_unknown_bad_fingerprint_and_noncanonical_record(self):
        record = make_state(pnls=(D("1"),)).to_record()
        candidates = []
        item = dict(record)
        item.pop("revision")
        candidates.append(item)
        item = dict(record)
        item["unknown"] = "blocked"
        candidates.append(item)
        for name, value in (
            ("state_fingerprint", "b" * 64),
            ("updated_utc", "2026-08-31T08:00:00+00:00"),
        ):
            item = dict(record)
            item[name] = value
            candidates.append(item)
        for candidate in candidates:
            with self.subTest(keys=tuple(sorted(candidate))):
                with self.assertRaises(LossClusterStateError):
                    LossClusterStateV2.from_record(candidate)

    def test_legacy_v1_migration_remains_supported(self):
        legacy = {
            "schema_version": 1,
            "version": 1,
            "recent_closed_trade_pnls": [-1, 1.5, 0],
            "pause_entries_remaining": 2,
            "updated_utc": "2026-08-31T10:00:00+02:00",
        }
        migrated = LossClusterStateV2.from_legacy_v1(legacy)
        self.assertEqual(migrated.schema_version, 2)
        self.assertEqual(migrated.revision, 0)
        self.assertEqual(
            migrated.recent_closed_trade_pnls,
            (D("-1"), D("1.5"), D("0")),
        )
        self.assertEqual(migrated.pause_entries_remaining, 2)
        self.assertEqual(migrated.updated_utc, T0)
        self.assertEqual(LossClusterStateV2.from_record(migrated.to_record()), migrated)

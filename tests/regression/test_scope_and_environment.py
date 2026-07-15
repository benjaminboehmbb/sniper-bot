"""Tests for TD005-IU-022 (Scope Boundary) and TD005-IU-007 (Environment Identity)."""

import unittest

from tests.regression.scope import ScopeBoundary, ScopePartition, derive_scope_partition, RETAIN_DEFERRED_SCOPE
from tests.regression.environment_identity import capture, identities_match


class TestScopeBoundary(unittest.TestCase):
    def test_active_count_is_fourteen(self):
        partition = derive_scope_partition()
        self.assertEqual(len(partition.active), 14)

    def test_inactive_count_is_four(self):
        partition = derive_scope_partition()
        self.assertEqual(len(partition.inactive), 4)

    def test_inactive_set_matches_retain_deferred_scope(self):
        partition = derive_scope_partition()
        self.assertEqual(set(partition.inactive), set(RETAIN_DEFERRED_SCOPE))

    def test_four_previously_uncovered_active_modules_are_active(self):
        # FRA Section 13.1's own four previously-uncovered active modules.
        partition = derive_scope_partition()
        for expected in (
            "run_engine/main.py",
            "run_engine/core/state.py",
            "run_engine/core/regime.py",
            "run_engine/core/execution/__init__.py",
        ):
            self.assertIn(expected, partition.active)

    def test_executor_reachable_via_relative_import(self):
        partition = derive_scope_partition()
        self.assertIn("run_engine/core/execution/executor.py", partition.active)

    def test_boundary_starts_stable(self):
        boundary = ScopeBoundary()
        self.assertEqual(boundary.state, "Stable")

    def test_repeated_confirm_with_no_change_remains_stable(self):
        boundary = ScopeBoundary()
        boundary.confirm()
        boundary.confirm()
        self.assertEqual(boundary.state, "Stable")

    def test_confirm_detects_drift_and_reaches_re_confirmed(self):
        real = derive_scope_partition()
        drifted = ScopePartition(
            active=frozenset(set(real.active) | {"run_engine/core/config.py"}),
            inactive=frozenset(set(real.inactive) - {"run_engine/core/config.py"}),
        )
        calls = {"n": 0}

        def provider():
            calls["n"] += 1
            return real if calls["n"] == 1 else drifted

        boundary = ScopeBoundary(partition_provider=provider)
        boundary.confirm()
        self.assertEqual(boundary.state, "Stable")
        boundary.confirm()
        self.assertEqual(boundary.state, "Re-Confirmed")
        self.assertEqual(boundary.partition.active, drifted.active)

    def test_is_active_true_for_main(self):
        boundary = ScopeBoundary()
        self.assertTrue(boundary.is_active("run_engine/main.py"))

    def test_is_active_false_for_retain_deferred_scope(self):
        boundary = ScopeBoundary()
        self.assertFalse(boundary.is_active("run_engine/core/config.py"))

    def test_re_derivation_is_reproducible(self):
        first = derive_scope_partition()
        second = derive_scope_partition()
        self.assertEqual(first.active, second.active)
        self.assertEqual(first.inactive, second.inactive)


class TestEnvironmentIdentity(unittest.TestCase):
    def test_capture_reaches_recorded(self):
        identity = capture("session-1")
        self.assertEqual(identity.state, "Recorded")
        self.assertEqual(identity.session_id, "session-1")

    def test_capture_is_fresh_per_session(self):
        a = capture("session-a")
        b = capture("session-b")
        self.assertNotEqual(a.session_id, b.session_id)

    def test_identical_environment_matches_itself(self):
        a = capture("session-1")
        b = capture("session-2")
        self.assertTrue(identities_match(a, b))

    def test_numpy_pandas_versions_captured(self):
        identity = capture("session-1")
        self.assertTrue(identity.numpy_version)
        self.assertTrue(identity.pandas_version)


if __name__ == "__main__":
    unittest.main()

"""Tests for TD005-IU-010/011/012/013 (Comparison Semantics)."""

import unittest

from tests.regression.comparison import (
    BehaviouralEquivalenceDefinition,
    NumericCategoricalComparator,
    ObjectIdentityIndependentComparator,
    TrajectoryComparator,
    UncategorizedFieldError,
)
from tests.regression.observation import NonInterferenceObserver
from tests.regression.replay import ControlledConditionManifest, ReplaySession


def make_tick_sequence(n):
    return tuple({"tick": i, "price": 30000 + (i % 100)} for i in range(n))


def observed_trajectory(n):
    session = ReplaySession(manifest=ControlledConditionManifest(tick_sequence=make_tick_sequence(n))).run("s")
    return NonInterferenceObserver().observe(session)


class TestNumericCategoricalComparator(unittest.TestCase):
    def setUp(self):
        self.comparator = NumericCategoricalComparator()

    def test_exact_equality_field_requires_exact_match(self):
        self.assertTrue(self.comparator.compare_leaf("event_type", "TRADE_OPENED", "TRADE_OPENED"))
        self.assertFalse(self.comparator.compare_leaf("event_type", "TRADE_OPENED", "SCALE_IN"))

    def test_tolerance_bounded_field_accepts_tiny_difference(self):
        self.assertTrue(self.comparator.compare_leaf("equity", 100.0, 100.0 + 1e-10))

    def test_tolerance_bounded_field_rejects_large_difference(self):
        self.assertFalse(self.comparator.compare_leaf("equity", 100.0, 105.0))

    def test_uncategorized_field_raises(self):
        with self.assertRaises(UncategorizedFieldError):
            self.comparator.category_of("not_a_real_field")

    def test_symmetric_tolerance_application(self):
        # TD005-II-007: identical policy to reference and candidate, no
        # asymmetric treatment - swapping arguments yields the same verdict.
        forward = self.comparator.compare_leaf("equity", 100.0, 100.0 + 5e-7)
        backward = self.comparator.compare_leaf("equity", 100.0 + 5e-7, 100.0)
        self.assertEqual(forward, backward)


class TestObjectIdentityIndependentComparator(unittest.TestCase):
    def setUp(self):
        self.comparator = ObjectIdentityIndependentComparator()

    def test_structurally_equal_but_distinct_objects_are_equal(self):
        a = {"position": "LONG", "quantity": 1.0}
        b = {"position": "LONG", "quantity": 1.0}
        self.assertIsNot(a, b)
        self.assertTrue(self.comparator.structurally_equal(a, b))

    def test_structurally_different_objects_are_unequal(self):
        a = {"position": "LONG"}
        b = {"position": "SHORT"}
        self.assertFalse(self.comparator.structurally_equal(a, b))

    def test_never_uses_identity(self):
        # A dict built via two entirely separate literal constructions.
        a = dict(x=1, y=[1, 2, 3])
        b = dict(y=[1, 2, 3], x=1)
        self.assertNotEqual(id(a), id(b))
        self.assertTrue(self.comparator.structurally_equal(a, b))


class TestBehaviouralEquivalenceDefinition(unittest.TestCase):
    def test_identical_values_yield_no_differences(self):
        eq = BehaviouralEquivalenceDefinition()
        diffs = eq.compare_value("root", {"equity": 100.0, "regime": "CHOP"}, {"equity": 100.0, "regime": "CHOP"})
        self.assertEqual(diffs, [])

    def test_tolerance_bounded_tiny_difference_yields_no_differences(self):
        eq = BehaviouralEquivalenceDefinition()
        diffs = eq.compare_value("root", {"equity": 100.0}, {"equity": 100.0 + 1e-10})
        self.assertEqual(diffs, [])

    def test_categorical_difference_is_reported(self):
        eq = BehaviouralEquivalenceDefinition()
        diffs = eq.compare_value("root", {"regime": "CHOP"}, {"regime": "TREND_UP"})
        self.assertEqual(len(diffs), 1)
        self.assertEqual(diffs[0].path, "root.regime")

    def test_never_defined_as_byte_or_source_identity(self):
        # Two structurally-equal dicts built by different code paths must be
        # equivalent - equivalence is never contingent on how the value was
        # produced (source/byte identity).
        eq = BehaviouralEquivalenceDefinition()
        a = dict([("position", "LONG"), ("quantity", 2.0)])
        b = {"quantity": 2.0, "position": "LONG"}
        self.assertEqual(eq.compare_value("root", a, b), [])


class TestTrajectoryComparator(unittest.TestCase):
    def test_identical_trajectories_are_equivalent(self):
        traj = observed_trajectory(10)
        comparator = TrajectoryComparator(BehaviouralEquivalenceDefinition())
        result = comparator.compare(traj, traj)
        self.assertTrue(result.equivalent)
        self.assertEqual(result.differences, [])

    def test_two_independent_captures_same_ticks_are_equivalent(self):
        traj_a = observed_trajectory(20)
        traj_b = observed_trajectory(20)
        comparator = TrajectoryComparator(BehaviouralEquivalenceDefinition())
        result = comparator.compare(traj_a, traj_b)
        self.assertTrue(result.equivalent, msg=f"unexpected differences: {result.differences}")

    def test_different_length_trajectories_are_not_equivalent(self):
        traj_a = observed_trajectory(5)
        traj_b = observed_trajectory(8)
        comparator = TrajectoryComparator(BehaviouralEquivalenceDefinition())
        result = comparator.compare(traj_a, traj_b)
        self.assertFalse(result.equivalent)
        self.assertEqual(result.differences[0].path, "trajectory.length")

    def test_comparison_ignores_implementation_detail_fields(self):
        # decision/strategy_weights are IMPLEMENTATION_DETAIL, excluded from
        # the comparison domain; a synthetic divergence there must not surface.
        traj_a = observed_trajectory(3)
        traj_b = observed_trajectory(3)
        # Mutate an implementation-detail field on one snapshot's own copy.
        traj_b[0].data["decision"] = {"action": "SOMETHING_ELSE", "confidence": 0.0, "regime": "X"}
        comparator = TrajectoryComparator(BehaviouralEquivalenceDefinition())
        result = comparator.compare(traj_a, traj_b)
        self.assertTrue(result.equivalent, msg=f"unexpected differences: {result.differences}")


if __name__ == "__main__":
    unittest.main()

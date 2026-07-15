"""Tests for TD005-IU-006 (Replay), TD005-IU-008 (Observable Surface
Classification), TD005-IU-009 (Non-Interference Observation)."""

import unittest

from tests.regression.replay import (
    ControlledConditionManifest,
    ReplaySession,
    TrajectoryNotAvailableError,
    UnsupportedManifestError,
    IncompleteManifestError,
)
from tests.regression.observation import (
    NonInterferenceObserver,
    ObservableSurfaceClassifier,
    ObservableCategory,
    COMPARISON_DOMAIN,
)


def make_tick_sequence(n, start_tick=0, price_fn=None):
    if price_fn is None:
        price_fn = lambda t: 30000 + (t % 100)
    return tuple({"tick": start_tick + i, "price": price_fn(start_tick + i)} for i in range(n))


class TestControlledConditionManifest(unittest.TestCase):
    def test_empty_tick_sequence_is_incomplete(self):
        manifest = ControlledConditionManifest(tick_sequence=())
        with self.assertRaises(IncompleteManifestError):
            manifest.validate()

    def test_non_default_initial_position_unsupported(self):
        manifest = ControlledConditionManifest(tick_sequence=make_tick_sequence(1), initial_position="LONG")
        with self.assertRaises(UnsupportedManifestError):
            manifest.validate()

    def test_default_manifest_validates(self):
        manifest = ControlledConditionManifest(tick_sequence=make_tick_sequence(5))
        manifest.validate()  # must not raise


class TestReplaySession(unittest.TestCase):
    def test_reaches_captured_on_success(self):
        manifest = ControlledConditionManifest(tick_sequence=make_tick_sequence(10))
        session = ReplaySession(manifest=manifest).run("s1")
        self.assertEqual(session.state, "Captured")
        self.assertEqual(len(session.captured_trajectory()), 10)

    def test_incomplete_manifest_reaches_failed(self):
        manifest = ControlledConditionManifest(tick_sequence=())
        session = ReplaySession(manifest=manifest).run("s1")
        self.assertEqual(session.state, "Failed")
        self.assertIsNotNone(session.failure_reason)

    def test_failed_session_trajectory_not_available(self):
        manifest = ControlledConditionManifest(tick_sequence=())
        session = ReplaySession(manifest=manifest).run("s1")
        with self.assertRaises(TrajectoryNotAvailableError):
            session.captured_trajectory()

    def test_not_started_trajectory_not_available(self):
        manifest = ControlledConditionManifest(tick_sequence=make_tick_sequence(1))
        session = ReplaySession(manifest=manifest)
        with self.assertRaises(TrajectoryNotAvailableError):
            session.captured_trajectory()

    def test_bounded_duration_exceeded_reaches_failed(self):
        manifest = ControlledConditionManifest(tick_sequence=make_tick_sequence(1000))
        session = ReplaySession(manifest=manifest, bounded_duration_seconds=0.0).run("s1")
        self.assertEqual(session.state, "Failed")
        self.assertIn("bounded duration", session.failure_reason)

    def test_identity_captured_on_execution(self):
        manifest = ControlledConditionManifest(tick_sequence=make_tick_sequence(3))
        session = ReplaySession(manifest=manifest).run("s1")
        self.assertIsNotNone(session.identity)
        self.assertEqual(session.identity.state, "Recorded")

    def test_two_independent_sessions_same_ticks_produce_equal_trajectories(self):
        ticks = make_tick_sequence(25)
        session_a = ReplaySession(manifest=ControlledConditionManifest(tick_sequence=ticks)).run("a")
        session_b = ReplaySession(manifest=ControlledConditionManifest(tick_sequence=ticks)).run("b")
        traj_a = session_a.captured_trajectory()
        traj_b = session_b.captured_trajectory()
        self.assertEqual(len(traj_a), len(traj_b))
        for tick_a, tick_b in zip(traj_a, traj_b):
            self.assertEqual(tick_a["state"], tick_b["state"])
            self.assertEqual(tick_a["position"], tick_b["position"])
            self.assertEqual(tick_a["equity"], tick_b["equity"])


class TestObservableSurfaceClassifier(unittest.TestCase):
    def test_starts_unclassified(self):
        classifier = ObservableSurfaceClassifier()
        self.assertEqual(classifier.state, "Unclassified")

    def test_classify_all_reaches_classified(self):
        classifier = ObservableSurfaceClassifier()
        classifier.classify_all()
        self.assertEqual(classifier.state, "Classified")

    def test_every_lifecycle_field_has_exactly_one_category(self):
        classifier = ObservableSurfaceClassifier()
        mapping = classifier.classify_all()
        for field in ("state.position", "state.equity", "trade_event", "execution"):
            self.assertIn(field, mapping)
            self.assertIsInstance(mapping[field], ObservableCategory)

    def test_comparison_domain_excludes_implementation_detail(self):
        self.assertNotIn("decision", COMPARISON_DOMAIN)
        self.assertNotIn("state.strategy_selection", COMPARISON_DOMAIN)

    def test_comparison_domain_includes_certified_output(self):
        self.assertIn("state.equity", COMPARISON_DOMAIN)
        self.assertIn("trade_event", COMPARISON_DOMAIN)


class TestNonInterferenceObserver(unittest.TestCase):
    def test_observe_returns_one_snapshot_per_tick(self):
        manifest = ControlledConditionManifest(tick_sequence=make_tick_sequence(7))
        session = ReplaySession(manifest=manifest).run("s1")
        observer = NonInterferenceObserver()
        snapshots = observer.observe(session)
        self.assertEqual(len(snapshots), 7)
        self.assertEqual(observer.state, "Idle")

    def test_snapshot_is_independent_deep_copy(self):
        manifest = ControlledConditionManifest(tick_sequence=make_tick_sequence(3))
        session = ReplaySession(manifest=manifest).run("s1")
        observer = NonInterferenceObserver()
        snapshots = observer.observe(session)

        # Mutating the exposed snapshot must not corrupt the session's own
        # underlying trajectory data (the deep-copy boundary is real, not
        # merely a shallow reference).
        snapshots[0].data["position"]["position"] = "MUTATED"
        untouched_trajectory = session.captured_trajectory()
        self.assertNotEqual(untouched_trajectory[0]["position"]["position"], "MUTATED")

        # A second, independent observation of the same untouched session
        # must also be unaffected by the first observation's own mutation.
        second_snapshots = observer.observe(session)
        self.assertNotEqual(second_snapshots[0].data["position"]["position"], "MUTATED")

    def test_observation_does_not_alter_subsequent_replay(self):
        # Two independent sessions; observing the first must not measurably
        # affect the second's own trajectory (TD005-SI-007).
        ticks = make_tick_sequence(15)
        session_a = ReplaySession(manifest=ControlledConditionManifest(tick_sequence=ticks)).run("a")
        NonInterferenceObserver().observe(session_a)
        session_b = ReplaySession(manifest=ControlledConditionManifest(tick_sequence=ticks)).run("b")
        traj_a = session_a.captured_trajectory()
        traj_b = session_b.captured_trajectory()
        for tick_a, tick_b in zip(traj_a, traj_b):
            self.assertEqual(tick_a["state"], tick_b["state"])

    def test_observe_raises_for_failed_session(self):
        manifest = ControlledConditionManifest(tick_sequence=())
        session = ReplaySession(manifest=manifest).run("s1")
        observer = NonInterferenceObserver()
        with self.assertRaises(TrajectoryNotAvailableError):
            observer.observe(session)


if __name__ == "__main__":
    unittest.main()

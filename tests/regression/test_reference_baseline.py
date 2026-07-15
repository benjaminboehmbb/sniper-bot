"""Tests for TD005-IU-003 (Reference Baseline Authority)."""

import unittest

from tests.regression.certification_boundary import CertificationBoundary
from tests.regression.corpus import CertifiedContractCorpus
from tests.regression.observation import NonInterferenceObserver
from tests.regression.reference_baseline import (
    BootstrapRejectedError,
    NotEstablishedError,
    ReferenceBaselineAuthority,
)
from tests.regression.replay import ControlledConditionManifest, ReplaySession


def make_tick_sequence(n):
    return tuple({"tick": i, "price": 30000 + (i % 100)} for i in range(n))


def new_authority():
    corpus = CertifiedContractCorpus()
    boundary = CertificationBoundary(corpus)
    return ReferenceBaselineAuthority(corpus, boundary)


class TestReferenceBaselineAuthority(unittest.TestCase):
    def test_starts_unestablished(self):
        authority = new_authority()
        self.assertEqual(authority.state, "Unestablished")

    def test_establish_from_captured_session_reaches_established(self):
        authority = new_authority()
        session = ReplaySession(manifest=ControlledConditionManifest(tick_sequence=make_tick_sequence(10))).run("bootstrap")
        record = authority.establish(session, NonInterferenceObserver())
        self.assertEqual(authority.state, "Established")
        self.assertEqual(record.source, "freshly-established")
        self.assertEqual(len(record.trajectory), 10)

    def test_establish_from_failed_session_is_rejected(self):
        authority = new_authority()
        session = ReplaySession(manifest=ControlledConditionManifest(tick_sequence=())).run("bootstrap")
        with self.assertRaises(BootstrapRejectedError):
            authority.establish(session, NonInterferenceObserver())
        self.assertEqual(authority.state, "Unestablished")

    def test_require_established_raises_before_establishment(self):
        authority = new_authority()
        with self.assertRaises(NotEstablishedError):
            authority.require_established()

    def test_revise_before_established_raises(self):
        authority = new_authority()
        session = ReplaySession(manifest=ControlledConditionManifest(tick_sequence=make_tick_sequence(5))).run("s")
        with self.assertRaises(NotEstablishedError):
            authority.revise(session, NonInterferenceObserver(), "premature revision")

    def test_revise_replaces_record_with_new_governance_epoch(self):
        authority = new_authority()
        session1 = ReplaySession(manifest=ControlledConditionManifest(tick_sequence=make_tick_sequence(5))).run("s1")
        first = authority.establish(session1, NonInterferenceObserver())

        session2 = ReplaySession(manifest=ControlledConditionManifest(tick_sequence=make_tick_sequence(8))).run("s2")
        second = authority.revise(session2, NonInterferenceObserver(), "revision for coverage change")

        self.assertEqual(authority.state, "Established")
        self.assertGreater(second.governance_epoch, first.governance_epoch)
        self.assertEqual(len(second.trajectory), 8)
        self.assertIn("revision for coverage change", second.revision_history)
        self.assertIn("initial bootstrap", second.revision_history)

    def test_revise_with_failed_session_reverts_to_established_and_keeps_prior_record(self):
        authority = new_authority()
        session1 = ReplaySession(manifest=ControlledConditionManifest(tick_sequence=make_tick_sequence(5))).run("s1")
        first = authority.establish(session1, NonInterferenceObserver())

        failed_session = ReplaySession(manifest=ControlledConditionManifest(tick_sequence=())).run("s2")
        with self.assertRaises(BootstrapRejectedError):
            authority.revise(failed_session, NonInterferenceObserver(), "bad revision")

        self.assertEqual(authority.state, "Established")
        self.assertIs(authority.record, first)

    def test_record_is_immutable_frozen_dataclass(self):
        authority = new_authority()
        session = ReplaySession(manifest=ControlledConditionManifest(tick_sequence=make_tick_sequence(3))).run("s")
        record = authority.establish(session, NonInterferenceObserver())
        with self.assertRaises(Exception):
            record.governance_epoch = 999  # frozen dataclass must reject mutation


if __name__ == "__main__":
    unittest.main()

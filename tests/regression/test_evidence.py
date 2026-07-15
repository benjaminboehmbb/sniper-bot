"""Tests for TD005-IU-015 (Evidence Composition) and TD005-IU-016 (Evidence
Persistence and Continuity)."""

import os
import shutil
import tempfile
import unittest

from tests.regression.evidence import (
    EvidenceComposer,
    EvidencePersistence,
    IncompleteEvidenceError,
    InterruptedPersistError,
    REQUIRED_ELEMENTS,
    UnavailabilityMarker,
)


def complete_elements(**overrides):
    base = {
        "affected_tick": 5,
        "affected_stage_or_component": "PnLEngine",
        "expected_value": 100.0,
        "actual_value": 105.0,
        "input_provenance": "tick_sequence[5]",
        "initial_state_provenance": "fresh RunLoop()",
        "certified_contract_id": "AC-005",
        "execution_environment_identity": "session-1",
    }
    base.update(overrides)
    return base


class TestEvidenceComposer(unittest.TestCase):
    def setUp(self):
        self.composer = EvidenceComposer()

    def test_complete_elements_reach_composed(self):
        record = self.composer.compose(**complete_elements())
        self.assertEqual(record.state, "Composed")

    def test_missing_element_raises(self):
        elements = complete_elements()
        del elements["expected_value"]
        with self.assertRaises(IncompleteEvidenceError):
            self.composer.compose(**elements)

    def test_bare_none_omission_raises(self):
        elements = complete_elements(certified_contract_id=None)
        with self.assertRaises(IncompleteEvidenceError):
            self.composer.compose(**elements)

    def test_unavailability_marker_satisfies_element(self):
        elements = complete_elements(
            certified_contract_id=UnavailabilityMarker("certification boundary cannot place this deviation")
        )
        record = self.composer.compose(**elements)
        self.assertEqual(record.state, "Composed")

    def test_empty_marker_reason_raises(self):
        with self.assertRaises(IncompleteEvidenceError):
            UnavailabilityMarker("")

    def test_all_eight_required_elements_present_in_record(self):
        record = self.composer.compose(**complete_elements())
        for name in REQUIRED_ELEMENTS:
            self.assertIn(name, record.elements)

    def test_each_deviation_gets_a_separate_record(self):
        record_a = self.composer.compose(**complete_elements(affected_tick=1))
        record_b = self.composer.compose(**complete_elements(affected_tick=2))
        self.assertNotEqual(record_a.record_id, record_b.record_id)


class TestEvidencePersistence(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="td005-evidence-test-")
        self.persistence = EvidencePersistence(directory=self.tmpdir)
        self.composer = EvidenceComposer()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_persist_composed_record_reaches_persisted(self):
        record = self.composer.compose(**complete_elements())
        self.persistence.persist(record)
        self.assertTrue(self.persistence.is_persisted(record))

    def test_persist_non_composed_record_raises(self):
        from tests.regression.evidence import EvidenceRecord, EvidenceError

        record = EvidenceRecord(state="Composing")
        with self.assertRaises(EvidenceError):
            self.persistence.persist(record)

    def test_interrupted_persist_leaves_record_unpersisted_not_altered(self):
        record = self.composer.compose(**complete_elements())
        with self.assertRaises(InterruptedPersistError):
            self.persistence.persist(record, simulate_interruption=True)
        # Never Persisted-and-Altered: the record simply never reached
        # Persisted at all, and no partial file is left behind.
        self.assertFalse(self.persistence.is_persisted(record))
        leftover_files = [f for f in os.listdir(self.tmpdir) if not f.startswith(".tmp-")]
        self.assertEqual(leftover_files, [])
        tmp_files = [f for f in os.listdir(self.tmpdir) if f.startswith(".tmp-")]
        self.assertEqual(tmp_files, [], "temp file was not cleaned up after interruption")

    def test_restart_after_interrupted_persistence_succeeds(self):
        record = self.composer.compose(**complete_elements())
        with self.assertRaises(InterruptedPersistError):
            self.persistence.persist(record, simulate_interruption=True)
        self.assertFalse(self.persistence.is_persisted(record))

        # A fresh attempt (as Section 8's own Restart rule requires: full
        # re-run, not a resume) succeeds cleanly.
        self.persistence.persist(record)
        self.assertTrue(self.persistence.is_persisted(record))

    def test_persisted_content_matches_composed_elements(self):
        record = self.composer.compose(**complete_elements(affected_tick=42))
        self.persistence.persist(record)
        loaded = self.persistence.load(record.record_id)
        self.assertEqual(loaded["elements"]["affected_tick"], 42)

    def test_unavailability_marker_serializes_with_reason(self):
        record = self.composer.compose(
            **complete_elements(expected_value=UnavailabilityMarker("no certified expectation exists"))
        )
        self.persistence.persist(record)
        loaded = self.persistence.load(record.record_id)
        self.assertTrue(loaded["elements"]["expected_value"]["__unavailable__"])
        self.assertEqual(loaded["elements"]["expected_value"]["reason"], "no certified expectation exists")

    def test_persisted_record_never_modified_in_place(self):
        record = self.composer.compose(**complete_elements())
        self.persistence.persist(record)
        before = self.persistence.load(record.record_id)
        # No API in this suite offers an in-place edit path; re-loading must
        # be stable.
        after = self.persistence.load(record.record_id)
        self.assertEqual(before, after)

    def test_retained_across_stage_transitions(self):
        record = self.composer.compose(**complete_elements())
        self.persistence.persist(record)
        self.assertTrue(self.persistence.retained_across(record, stage_transitions=6))


if __name__ == "__main__":
    unittest.main()

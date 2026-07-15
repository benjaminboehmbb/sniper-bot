"""Tests for TD005-IU-001 (Corpus), TD005-IU-002 (Certification Boundary),
TD005-IU-004 (Behavioural Vocabulary).
"""

import unittest

from tests.regression import vocabulary
from tests.regression.corpus import CertifiedContractCorpus
from tests.regression.certification_boundary import CertificationBoundary


class TestVocabulary(unittest.TestCase):
    def test_all_terms_defined(self):
        for term in [
            "Position", "Side", "Scale-In", "Partial Close", "Full Close",
            "Tick-Complete", "Canonical Working State", "Authoritative Owner",
            "Computational Authority", "Runtime Failure Event",
        ]:
            self.assertTrue(vocabulary.is_established(term))
            self.assertIsInstance(vocabulary.define(term), str)

    def test_undefined_term_raises(self):
        with self.assertRaises(vocabulary.VocabularyError):
            vocabulary.define("NotATerm")

    def test_lifecycle_event_types_count(self):
        self.assertEqual(len(vocabulary.LIFECYCLE_EVENT_TYPES), 5)

    def test_canonical_update_methods_count(self):
        # FR-004's own twelve update_* methods.
        self.assertEqual(len(vocabulary.CANONICAL_UPDATE_METHODS), 12)


class TestCorpus(unittest.TestCase):
    def setUp(self):
        self.corpus = CertifiedContractCorpus()

    def test_uninitialized_before_enumerate(self):
        self.assertEqual(self.corpus.state, "Uninitialized")

    def test_enumerate_reaches_enumerated(self):
        entries = self.corpus.enumerate()
        self.assertGreater(len(entries), 0)
        self.assertEqual(self.corpus.state, "Enumerated")

    def test_re_enumerate_is_idempotent_and_reproducible(self):
        first = self.corpus.enumerate()
        second = self.corpus.enumerate()
        self.assertEqual([e.contract_id for e in first], [e.contract_id for e in second])

    def test_membership_true_for_known_contract(self):
        self.assertTrue(self.corpus.membership("AC-001"))

    def test_membership_false_for_unknown_contract(self):
        self.assertFalse(self.corpus.membership("NOT-A-CONTRACT"))

    def test_no_drift_against_current_repository(self):
        report = self.corpus.check_drift()
        self.assertFalse(report.drifted, f"unexpected drift: {report.missing}")

    def test_six_certified_units_present(self):
        entries = self.corpus.enumerate()
        certified_units = [e.contract_id for e in entries if e.category == "CERTIFIED_UNIT"]
        for expected in ("P2-02A", "P2-03", "P2-04", "P3-01", "P3-02", "P3-03"):
            self.assertIn(expected, certified_units)


class TestCertificationBoundary(unittest.TestCase):
    def setUp(self):
        self.corpus = CertifiedContractCorpus()
        self.boundary = CertificationBoundary(self.corpus)

    def test_undefined_before_define(self):
        self.assertEqual(self.boundary.state, "Undefined")

    def test_evaluate_auto_defines(self):
        self.boundary.evaluate("AC-001")
        self.assertEqual(self.boundary.state, "Defined")

    def test_certified_contract_determination(self):
        det = self.boundary.evaluate("AC-001")
        self.assertTrue(det.certified)
        self.assertEqual(det.category, "AC")

    def test_uncertified_contract_determination(self):
        det = self.boundary.evaluate("NOT-A-CONTRACT")
        self.assertFalse(det.certified)

    def test_repeated_evaluation_same_version_yields_same_determination(self):
        first = self.boundary.evaluate("AC-001")
        second = self.boundary.evaluate("AC-001")
        self.assertEqual(first.certified, second.certified)
        self.assertEqual(first.boundary_rule_version, second.boundary_rule_version)

    def test_revise_changes_version_and_state(self):
        self.boundary.define()
        self.boundary.revise("TD005-CB-V2")
        self.assertEqual(self.boundary.state, "Revised")
        det = self.boundary.evaluate("AC-001")
        self.assertEqual(det.boundary_rule_version, "TD005-CB-V2")

    def test_three_contract_categories_only(self):
        from tests.regression.certification_boundary import CONTRACT_CATEGORIES
        self.assertEqual(set(CONTRACT_CATEGORIES), {"ADR", "AC", "CERTIFIED_UNIT"})


if __name__ == "__main__":
    unittest.main()

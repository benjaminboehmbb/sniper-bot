"""Tests for TD005-IU-020 (Governance Sequence Conformance), TD005-IU-023
(Executor Namespace Boundary), and TD005-IU-021 (Extension Point Registry)."""

import unittest

from tests.regression.governance import (
    EXECUTOR_NAMESPACE_EXCLUSION,
    GOVERNANCE_CONFORMANCE,
    conformant,
    executor_namespace_excluded,
)
from tests.regression.registry import RESOLVED, STILL_OPEN, is_registered


class TestGovernance(unittest.TestCase):
    def test_conformance_record_is_conformant(self):
        self.assertEqual(GOVERNANCE_CONFORMANCE.state, "Conformant")
        self.assertTrue(conformant())

    def test_exclusion_record_is_excluded(self):
        self.assertEqual(EXECUTOR_NAMESPACE_EXCLUSION.state, "Excluded")
        self.assertTrue(executor_namespace_excluded())

    def test_conformance_statement_is_nonempty(self):
        self.assertTrue(GOVERNANCE_CONFORMANCE.statement.strip())

    def test_exclusion_statement_names_rc_ad_004(self):
        self.assertIn("RC-AD-004", EXECUTOR_NAMESPACE_EXCLUSION.statement)


class TestRegistry(unittest.TestCase):
    def test_resolved_entries_nonempty(self):
        self.assertGreater(len(RESOLVED), 0)

    def test_every_resolved_entry_is_deterministic_and_repository_local(self):
        for entry in RESOLVED:
            self.assertTrue(entry.deterministic, msg=entry.mechanism)
            self.assertTrue(entry.repository_local, msg=entry.mechanism)

    def test_still_open_items_explicitly_named(self):
        self.assertGreater(len(STILL_OPEN), 0)
        for item in STILL_OPEN:
            self.assertIn(":", item)  # "<name>: <reason>" shape - never a bare placeholder

    def test_is_registered_true_for_known_mechanism(self):
        self.assertTrue(is_registered("Numeric tolerance values"))

    def test_is_registered_false_for_unknown_mechanism(self):
        self.assertFalse(is_registered("something never decided"))


if __name__ == "__main__":
    unittest.main()

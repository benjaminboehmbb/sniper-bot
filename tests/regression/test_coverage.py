"""Tests for TD005-IU-017 (Contract-to-Requirement Coverage) and
TD005-IU-018 (Module and State-Transition Coverage)."""

import unittest

from tests.regression.corpus import CertifiedContractCorpus
from tests.regression.coverage import (
    ALL_FR_IDS,
    ContractRequirementCoverage,
    ModuleStateTransitionCoverage,
)
from tests.regression.scope import ScopeBoundary


class TestContractRequirementCoverage(unittest.TestCase):
    def setUp(self):
        self.corpus = CertifiedContractCorpus()
        self.coverage = ContractRequirementCoverage(self.corpus)

    def test_starts_not_computed(self):
        self.assertEqual(self.coverage.state, "Not-Computed")

    def test_compute_with_nothing_exercised_reports_all_gaps(self):
        report = self.coverage.compute()
        self.assertEqual(self.coverage.state, "Computed")
        self.assertGreater(len(report.uncovered_contracts), 0)
        self.assertEqual(report.uncovered_requirements, ALL_FR_IDS)

    def test_recording_reduces_gap(self):
        self.coverage.record_contract_exercised("AC-001")
        self.coverage.record_requirement_exercised("TD005-FR-001")
        report = self.coverage.compute()
        self.assertNotIn("AC-001", report.uncovered_contracts)
        self.assertNotIn("TD005-FR-001", report.uncovered_requirements)

    def test_full_exercise_reaches_complete(self):
        for contract_id in self.corpus.enumerate():
            self.coverage.record_contract_exercised(contract_id.contract_id)
        for fr in ALL_FR_IDS:
            self.coverage.record_requirement_exercised(fr)
        report = self.coverage.compute()
        self.assertTrue(report.complete)

    def test_recording_after_computed_marks_stale(self):
        self.coverage.compute()
        self.assertEqual(self.coverage.state, "Computed")
        self.coverage.record_contract_exercised("AC-001")
        self.assertEqual(self.coverage.state, "Stale")

    def test_recompute_after_stale_reaches_recomputed(self):
        self.coverage.compute()
        self.coverage.record_contract_exercised("AC-001")
        self.coverage.compute()
        self.assertEqual(self.coverage.state, "Recomputed")

    def test_never_overrides_classification(self):
        # Advisory-only: this unit exposes no API that could alter a
        # classification outcome; confirmed by construction (no such method
        # exists on ContractRequirementCoverage).
        self.assertFalse(hasattr(self.coverage, "override_classification"))
        self.assertFalse(hasattr(self.coverage, "set_classification"))


class TestModuleStateTransitionCoverage(unittest.TestCase):
    def setUp(self):
        self.scope = ScopeBoundary()
        self.coverage = ModuleStateTransitionCoverage(self.scope)

    def test_starts_not_computed(self):
        self.assertEqual(self.coverage.state, "Not-Computed")

    def test_compute_with_nothing_exercised_reports_all_active_modules_uncovered(self):
        report = self.coverage.compute()
        self.assertEqual(len(report.uncovered_modules), 14)

    def test_recording_module_reduces_gap(self):
        self.coverage.record_module_exercised("run_engine/main.py")
        report = self.coverage.compute()
        self.assertNotIn("run_engine/main.py", report.uncovered_modules)

    def test_full_module_and_event_exercise_reaches_complete(self):
        partition = self.scope.confirm()
        for module in partition.active:
            self.coverage.record_module_exercised(module)
        for event_type in (
            "TRADE_OPENED", "SCALE_IN", "PARTIAL_CLOSE", "TRADE_CLOSED", "RUNTIME_FAILURE_EVENT",
        ):
            self.coverage.record_event_type_exercised(event_type)
        report = self.coverage.compute()
        self.assertTrue(report.complete, msg=f"remaining gaps: {report}")

    def test_scope_drift_marks_stale(self):
        self.coverage.compute()
        self.assertEqual(self.coverage.state, "Computed")
        self.coverage.on_scope_drift()
        self.assertEqual(self.coverage.state, "Stale")

    def test_never_overrides_classification(self):
        self.assertFalse(hasattr(self.coverage, "override_classification"))
        self.assertFalse(hasattr(self.coverage, "set_classification"))


if __name__ == "__main__":
    unittest.main()

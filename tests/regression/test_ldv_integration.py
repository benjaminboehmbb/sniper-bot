"""Tests for TD005-IU-019 (Long-Duration-Validation Integration)."""

import shutil
import tempfile
import unittest

from tests.regression.certification_boundary import CertificationBoundary
from tests.regression.corpus import CertifiedContractCorpus
from tests.regression.coverage import ContractRequirementCoverage, ModuleStateTransitionCoverage
from tests.regression.evidence import EvidencePersistence
from tests.regression.ldv_integration import LDV_STAGES, LDVIntegration
from tests.regression.observation import NonInterferenceObserver
from tests.regression.orchestrator import RegressionPipelineOrchestrator
from tests.regression.reference_baseline import ReferenceBaselineAuthority
from tests.regression.replay import ControlledConditionManifest, ReplaySession
from tests.regression.scope import ScopeBoundary


def make_tick_sequence(n):
    return tuple({"tick": i, "price": 30000 + (i % 100)} for i in range(n))


class TestLDVIntegration(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="td005-ldv-test-")
        corpus = CertifiedContractCorpus()
        boundary = CertificationBoundary(corpus)
        scope = ScopeBoundary()
        reference_authority = ReferenceBaselineAuthority(corpus, boundary)
        bootstrap = ReplaySession(manifest=ControlledConditionManifest(tick_sequence=make_tick_sequence(10))).run("bootstrap")
        reference_authority.establish(bootstrap, NonInterferenceObserver())

        orchestrator = RegressionPipelineOrchestrator(
            corpus=corpus,
            boundary=boundary,
            scope=scope,
            reference_authority=reference_authority,
            contract_coverage=ContractRequirementCoverage(corpus),
            module_coverage=ModuleStateTransitionCoverage(scope),
            evidence_persistence=EvidencePersistence(directory=self.tmpdir),
        )
        self.ldv = LDVIntegration(
            orchestrator=orchestrator,
            manifest_factory=lambda: ControlledConditionManifest(tick_sequence=make_tick_sequence(10)),
        )

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_six_stages_defined(self):
        self.assertEqual(len(LDV_STAGES), 6)

    def test_starts_not_invoked(self):
        self.assertEqual(self.ldv.state, "Not-Invoked")

    def test_run_stage_reaches_stage_complete(self):
        self.ldv.run_stage("functional_smoke")
        self.assertEqual(self.ldv.state, "Stage-Complete")

    def test_unknown_stage_name_raises(self):
        from tests.regression.ldv_integration import LDVIntegrationError

        with self.assertRaises(LDVIntegrationError):
            self.ldv.run_stage("not_a_real_stage")

    def test_run_all_stages_produces_six_results(self):
        results = self.ldv.run_all_stages()
        self.assertEqual(len(results), 6)

    def test_invocation_contract_identical_across_all_six_stages(self):
        self.ldv.run_all_stages()
        self.assertTrue(self.ldv.contract_is_identical_across_stages())

    def test_execution_time_budget_not_set(self):
        contract = self.ldv._current_contract()
        self.assertIsNone(contract.execution_time_budget_seconds)


if __name__ == "__main__":
    unittest.main()

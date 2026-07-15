"""Tests for TD005-IU-005 (Regression Pipeline Orchestration Unit)."""

import json
import shutil
import tempfile
import unittest

from tests.regression.certification_boundary import CertificationBoundary
from tests.regression.corpus import CertifiedContractCorpus
from tests.regression.coverage import ContractRequirementCoverage, ModuleStateTransitionCoverage
from tests.regression.evidence import EvidencePersistence
from tests.regression.observation import NonInterferenceObserver
from tests.regression.orchestrator import PreconditionNotMetError, RegressionPipelineOrchestrator
from tests.regression.reference_baseline import ReferenceBaselineAuthority
from tests.regression.replay import ControlledConditionManifest, ReplaySession
from tests.regression.scope import ScopeBoundary


def make_tick_sequence(n, price_fn=None):
    if price_fn is None:
        price_fn = lambda t: 30000 + (t % 100)
    return tuple({"tick": i, "price": price_fn(i)} for i in range(n))


class OrchestratorTestBase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="td005-orchestrator-test-")
        self.corpus = CertifiedContractCorpus()
        self.boundary = CertificationBoundary(self.corpus)
        self.scope = ScopeBoundary()
        self.reference_authority = ReferenceBaselineAuthority(self.corpus, self.boundary)
        self.contract_coverage = ContractRequirementCoverage(self.corpus)
        self.module_coverage = ModuleStateTransitionCoverage(self.scope)
        self.orchestrator = RegressionPipelineOrchestrator(
            corpus=self.corpus,
            boundary=self.boundary,
            scope=self.scope,
            reference_authority=self.reference_authority,
            contract_coverage=self.contract_coverage,
            module_coverage=self.module_coverage,
            evidence_persistence=EvidencePersistence(directory=self.tmpdir),
        )

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def establish_reference(self, n=20):
        bootstrap = ReplaySession(manifest=ControlledConditionManifest(tick_sequence=make_tick_sequence(n))).run("bootstrap")
        return self.reference_authority.establish(bootstrap, NonInterferenceObserver())

    def establish_coverage(self, contract_id="AC-001"):
        """Pre-registers `contract_id` as already-exercised, analogous to
        establish_reference(): a determinate (Non-Regression/Regression)
        outcome requires coverage established BEFORE the invocation under
        test, never coverage the invocation records for its own benefit
        (F-01 correction, orchestrator.py)."""
        self.contract_coverage.record_contract_exercised(contract_id)


class TestOrchestrator(OrchestratorTestBase):
    def test_invoke_before_reference_established_raises(self):
        manifest = ControlledConditionManifest(tick_sequence=make_tick_sequence(5))
        with self.assertRaises(PreconditionNotMetError):
            self.orchestrator.invoke(manifest, "candidate-1")

    def test_starts_not_invoked(self):
        self.assertEqual(self.orchestrator.state, "Not-Invoked")

    def test_identical_manifest_yields_non_regression(self):
        self.establish_reference(n=20)
        self.establish_coverage()
        manifest = ControlledConditionManifest(tick_sequence=make_tick_sequence(20))
        result = self.orchestrator.invoke(manifest, "candidate-1")
        self.assertEqual(self.orchestrator.state, "Stage-Complete")
        self.assertEqual(result.classification.outcome.value, "Non-Regression")
        self.assertIsNone(result.evidence_path)

    def test_candidate_failure_yields_invalid_comparison_with_evidence(self):
        self.establish_reference(n=10)
        manifest = ControlledConditionManifest(tick_sequence=())  # incomplete -> Failed
        result = self.orchestrator.invoke(manifest, "candidate-fail")
        self.assertEqual(result.classification.outcome.value, "Invalid Comparison")
        self.assertIsNotNone(result.evidence_path)

    def test_different_price_trajectory_yields_regression_with_evidence(self):
        self.establish_reference(n=20)
        self.establish_coverage()
        different_prices = ControlledConditionManifest(
            tick_sequence=make_tick_sequence(20, price_fn=lambda t: 99999 + t)
        )
        result = self.orchestrator.invoke(different_prices, "candidate-diff")
        self.assertEqual(result.classification.outcome.value, "Regression")
        self.assertIsNotNone(result.evidence_path)

    def test_repeated_invocation_is_independent_per_call(self):
        self.establish_reference(n=15)
        self.establish_coverage()
        manifest = ControlledConditionManifest(tick_sequence=make_tick_sequence(15))
        result_a = self.orchestrator.invoke(manifest, "call-a")
        result_b = self.orchestrator.invoke(manifest, "call-b")
        self.assertEqual(result_a.classification.outcome.value, "Non-Regression")
        self.assertEqual(result_b.classification.outcome.value, "Non-Regression")
        self.assertNotEqual(result_a.candidate_session.identity.session_id, result_b.candidate_session.identity.session_id)

    def test_restart_after_failure_succeeds_with_valid_manifest(self):
        self.establish_reference(n=10)
        self.establish_coverage()
        failed_manifest = ControlledConditionManifest(tick_sequence=())
        failed_result = self.orchestrator.invoke(failed_manifest, "attempt-1")
        self.assertEqual(failed_result.classification.outcome.value, "Invalid Comparison")

        good_manifest = ControlledConditionManifest(tick_sequence=make_tick_sequence(10))
        good_result = self.orchestrator.invoke(good_manifest, "attempt-2")
        self.assertEqual(good_result.classification.outcome.value, "Non-Regression")


class TestCoverageConfidenceSequencing(OrchestratorTestBase):
    """TD-005 Implementation QA Certification V1.0, Finding F-01 correction:
    coverage-confidence is computed from state established BEFORE the
    current invocation, never a self-recording the same invocation
    manufactures for itself. These tests exercise the corrected behaviour
    directly through the full orchestrator (never by calling
    RegressionClassifier.classify() directly, which test_classification.py
    already covers at the unit level)."""

    def test_never_before_covered_certified_contract_yields_indeterminate(self):
        # Requirement 3 (unresolved/incomplete coverage -> Indeterminate):
        # AC-001 is a genuine corpus member (certified) but this orchestrator's
        # own coverage tracker has never recorded it as exercised - coverage,
        # not certification, is the unresolved condition.
        self.establish_reference(n=10)
        manifest = ControlledConditionManifest(tick_sequence=make_tick_sequence(10))
        result = self.orchestrator.invoke(manifest, "first-ever-AC-001")
        self.assertEqual(result.classification.outcome.value, "Indeterminate")
        self.assertIsNotNone(result.evidence_path)

    def test_coverage_established_by_a_prior_invocation_enables_determinate_outcome(self):
        # Requirement 6 (coverage informs classification in advance): the
        # SAME orchestrator's own second invocation of AC-001, after the
        # first invocation's own bookkeeping recorded it, reaches a
        # determinate outcome - proving compute() genuinely reads state
        # established before this call, not a record this call invents for
        # itself.
        self.establish_reference(n=10)
        manifest = ControlledConditionManifest(tick_sequence=make_tick_sequence(10))
        first = self.orchestrator.invoke(manifest, "warm-up-call")
        self.assertEqual(first.classification.outcome.value, "Indeterminate")

        second = self.orchestrator.invoke(manifest, "confident-call")
        self.assertEqual(second.classification.outcome.value, "Non-Regression")

    def test_coverage_recorded_after_classification_never_alters_the_returned_outcome(self):
        # Requirement 5 (coverage cannot change a completed outcome):
        # InvocationResult.classification is already returned by the time
        # any further coverage recording happens; mutating the coverage
        # tracker afterward must never retroactively alter the already-
        # returned classification object.
        self.establish_reference(n=10)
        self.establish_coverage()
        manifest = ControlledConditionManifest(tick_sequence=make_tick_sequence(10))
        result = self.orchestrator.invoke(manifest, "post-classification-probe")
        outcome_before = result.classification.outcome

        # Further coverage activity, well after this invocation returned.
        self.contract_coverage.record_contract_exercised("AC-001")
        self.contract_coverage.record_contract_exercised("AC-005")
        self.contract_coverage.compute()

        self.assertEqual(result.classification.outcome, outcome_before)
        self.assertEqual(result.classification.outcome.value, "Non-Regression")

    def test_uncertified_contract_indeterminate_reason_distinct_from_low_coverage_reason(self):
        # TD005-II-014: the reasoned-unavailability marker must name the
        # specific upstream condition; an uncertified contract and a
        # certified-but-not-yet-covered contract are distinct conditions and
        # must not share one generic marker text.
        self.establish_reference(n=10)
        manifest = ControlledConditionManifest(tick_sequence=make_tick_sequence(10))

        uncertified_result = self.orchestrator.invoke(
            manifest, "uncertified-probe", evaluated_contract_id="NOT-A-CERTIFIED-CONTRACT"
        )
        self.assertEqual(uncertified_result.classification.outcome.value, "Indeterminate")
        with open(uncertified_result.evidence_path, encoding="utf-8") as f:
            uncertified_reason = json.load(f)["elements"]["certified_contract_id"]["reason"]

        low_coverage_result = self.orchestrator.invoke(
            manifest, "low-coverage-probe", evaluated_contract_id="AC-001"
        )
        self.assertEqual(low_coverage_result.classification.outcome.value, "Indeterminate")
        with open(low_coverage_result.evidence_path, encoding="utf-8") as f:
            low_coverage_reason = json.load(f)["elements"]["certified_contract_id"]["reason"]

        self.assertNotEqual(uncertified_reason, low_coverage_reason)
        self.assertIn("certified", uncertified_reason.lower())
        self.assertIn("coverage", low_coverage_reason.lower())


if __name__ == "__main__":
    unittest.main()

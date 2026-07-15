"""TD005-IU-005: Regression Pipeline Orchestration Unit.

Invokes every realization unit in the certified sequence, without owning
any realization unit's own internal behaviour: Replay -> Observation ->
Comparison -> Classification -> Evidence -> Coverage (Coverage informs
Classification in advance, per TD005-AI-014's own advisory-only framing).

Coverage-confidence sequencing (TD-005 Implementation QA Certification
V1.0, Finding F-01, corrected): the coverage-confidence signal consumed by
Classification (TD005-ID-009 Step 2) reflects coverage state established
BEFORE the current invocation - prior invocations' own recorded exercises
- never a self-satisfying record this same invocation creates for its own
benefit. `contract_coverage.compute()` therefore runs, and its result is
consumed by `classifier.classify()`, strictly before
`contract_coverage.record_contract_exercised()` is called for the
contract this invocation is evaluating. Recording happens only after
Classification has already reached its outcome, so it can benefit only
FUTURE invocations' own coverage-confidence check and can never alter,
override, or suppress the classification outcome just produced
(TD005-AI-014, TD005-SI-015). A certified contract with no prior recorded
exercise anywhere in this coverage tracker's own lifetime therefore
genuinely yields Indeterminate on its first evaluation, and a determinate
outcome (Non-Regression or Regression) once coverage for that contract has
been established by an earlier invocation - consistent with TD005-SD-001's
own scientific justification that Indeterminate is required "whenever...
Coverage... cannot yet confidently place a deviation inside or outside the
certified-contract boundary."

Dependencies (Section 7 of the Implementation Specification, corrected):
every realization unit it actually sequences, individually - TD005-IU-006
through TD005-IU-018 - plus the three preconditions confirmed before
sequencing begins (TD005-IU-001, TD005-IU-003, TD005-IU-022). This unit
does NOT depend on, and is never sequenced by, TD005-IU-019, TD005-IU-020,
or TD005-IU-021.

State model (TD005-SO-018-adjacent aggregate, TD005-SD-003's own per-
invocation session model): Not-Invoked -> Invoked -> Stage-Complete, one
instance per candidate execution.

Traceability: aggregate - Architecture Section 11; Specification Section 9;
TD005-AI-013; TD005-ID-001.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from tests.regression.certification_boundary import CertificationBoundary
from tests.regression.classification import ClassificationRecord, RegressionClassifier
from tests.regression.comparison import (
    BehaviouralEquivalenceDefinition,
    ComparisonResult,
    TrajectoryComparator,
)
from tests.regression.corpus import CertifiedContractCorpus
from tests.regression.coverage import ContractRequirementCoverage, ModuleStateTransitionCoverage
from tests.regression.evidence import EvidenceComposer, EvidencePersistence, UnavailabilityMarker
from tests.regression.observation import NonInterferenceObserver
from tests.regression.reference_baseline import ReferenceBaselineAuthority
from tests.regression.replay import ControlledConditionManifest, ReplaySession
from tests.regression.scope import ScopeBoundary


class OrchestrationError(Exception):
    pass


class PreconditionNotMetError(OrchestrationError):
    pass


@dataclass
class InvocationResult:
    candidate_session: ReplaySession
    comparison_result: Optional[ComparisonResult]
    classification: ClassificationRecord
    evidence_path: Optional[str] = None


@dataclass
class RegressionPipelineOrchestrator:
    """TD005-IU-005's own realization: Not-Invoked -> Invoked -> Stage-Complete."""

    corpus: CertifiedContractCorpus
    boundary: CertificationBoundary
    scope: ScopeBoundary
    reference_authority: ReferenceBaselineAuthority
    contract_coverage: ContractRequirementCoverage
    module_coverage: ModuleStateTransitionCoverage
    evidence_persistence: EvidencePersistence = field(default_factory=EvidencePersistence)

    state: str = field(default="Not-Invoked", init=False)

    def invoke(self, manifest: ControlledConditionManifest, session_id: str, evaluated_contract_id: str = "AC-001") -> InvocationResult:
        self.state = "Invoked"

        # Initialization preconditions (Section 8): confirmed before
        # sequencing begins, never assumed unchanged from a prior evaluation.
        self.scope.confirm()
        try:
            self.reference_authority.require_established()
        except Exception as exc:
            raise PreconditionNotMetError(f"reference baseline is not Established: {exc}") from exc
        self.corpus.enumerate()

        # Replay (TD005-IU-006, with TD005-IU-007 attaching identity).
        candidate_session = ReplaySession(manifest=manifest).run(session_id)

        classifier = RegressionClassifier()
        comparison_result: Optional[ComparisonResult] = None

        if candidate_session.state != "Captured":
            # Routed to Invalid Comparison without attempting Comparison at all.
            classification = classifier.classify(
                reference_session_state="Captured",
                candidate_session_state=candidate_session.state,
                certification_determination=None,
                coverage_confident=False,
                comparison_result=None,
            )
        else:
            # Observation (TD005-IU-008, TD005-IU-009).
            observer = NonInterferenceObserver()
            candidate_trajectory = observer.observe(candidate_session)
            reference_record = self.reference_authority.require_established()

            # Comparison (TD005-IU-010 through TD005-IU-013).
            equivalence = BehaviouralEquivalenceDefinition()
            trajectory_comparator = TrajectoryComparator(equivalence)
            comparison_result = trajectory_comparator.compare(reference_record.trajectory, candidate_trajectory)

            # Coverage (TD005-IU-017, TD005-IU-018) informs Classification
            # in advance, never after (TD005-AI-014): compute() is read
            # here, before this invocation records its own exercise below,
            # so coverage_confident reflects only what prior invocations
            # (or explicit pre-registration) already established - never a
            # self-satisfying signal this same call manufactures for
            # itself (F-01 correction; see module docstring).
            contract_report = self.contract_coverage.compute()
            coverage_confident = evaluated_contract_id not in contract_report.uncovered_contracts

            determination = self.boundary.evaluate(evaluated_contract_id)

            # Classification (TD005-IU-014).
            classification = classifier.classify(
                reference_session_state="Captured",
                candidate_session_state=candidate_session.state,
                certification_determination=determination,
                coverage_confident=coverage_confident,
                comparison_result=comparison_result,
            )

            # Coverage bookkeeping: this invocation's own exercise is
            # recorded only AFTER Classification has already reached its
            # outcome, so it can never alter, override, or suppress that
            # outcome (TD005-AI-014, TD005-SI-015) - it benefits only
            # future invocations' own coverage-confidence check.
            self.contract_coverage.record_contract_exercised(evaluated_contract_id)
            for snapshot in candidate_trajectory:
                trade_event = snapshot.data.get("trade_event")
                if trade_event is not None:
                    event_type = trade_event.get("event_type") if isinstance(trade_event, dict) else getattr(trade_event, "event_type", None)
                    if event_type:
                        self.module_coverage.record_event_type_exercised(event_type)

        # Evidence (TD005-IU-015, TD005-IU-016): required for three of the
        # four outcomes (TD005-SD-004), never for Non-Regression.
        evidence_path: Optional[str] = None
        if classification.outcome.value != "Non-Regression":
            evidence_path = self._compose_and_persist_evidence(
                classification, candidate_session, comparison_result, evaluated_contract_id,
                contract_certified=(determination.certified if candidate_session.state == "Captured" else None),
                coverage_confident=(coverage_confident if candidate_session.state == "Captured" else None),
            )

        self.state = "Stage-Complete"
        return InvocationResult(
            candidate_session=candidate_session,
            comparison_result=comparison_result,
            classification=classification,
            evidence_path=evidence_path,
        )

    def _compose_and_persist_evidence(
        self, classification, candidate_session, comparison_result, evaluated_contract_id,
        contract_certified: Optional[bool] = None, coverage_confident: Optional[bool] = None,
    ) -> str:
        composer = EvidenceComposer()

        first_diff = comparison_result.differences[0] if (comparison_result and comparison_result.differences) else None

        def value_or_marker(value, reason):
            return value if value is not None else UnavailabilityMarker(reason)

        elements = dict(
            affected_tick=value_or_marker(
                first_diff.path if first_diff else None,
                "no per-tick deviation available: upstream failure prevented any comparison",
            ),
            affected_stage_or_component=value_or_marker(
                "TrajectoryComparator" if comparison_result else None,
                "no comparison stage was reached: candidate session did not reach Captured",
            ),
            expected_value=value_or_marker(
                first_diff.reference_value if first_diff else None,
                "no certified expectation exists for this deviation (Indeterminate/Invalid Comparison)",
            ),
            actual_value=value_or_marker(
                first_diff.candidate_value if first_diff else None,
                f"no actual value produced: candidate session state is {candidate_session.state!r}",
            ),
            input_provenance="ControlledConditionManifest.tick_sequence",
            initial_state_provenance="fresh RunLoop() construction",
            certified_contract_id=value_or_marker(
                evaluated_contract_id if classification.outcome.value != "Indeterminate" else None,
                self._indeterminate_contract_id_reason(contract_certified, coverage_confident),
            ),
            execution_environment_identity=(
                candidate_session.identity.session_id if candidate_session.identity else UnavailabilityMarker(
                    "no execution-environment identity captured: session never reached Executing"
                )
            ),
        )

        record = composer.compose(**elements)
        return self.evidence_persistence.persist(record)

    @staticmethod
    def _indeterminate_contract_id_reason(contract_certified: Optional[bool], coverage_confident: Optional[bool]) -> str:
        """Names the specific upstream condition that prevented a determinate
        certified_contract_id (TD005-II-014): now that coverage-confidence is
        genuinely, independently computed (F-01 correction), an Indeterminate
        outcome can arise from either an uncertified contract or a certified
        contract with no yet-established coverage - these are distinct
        conditions and are named distinctly, never a single generic marker."""
        if contract_certified is False:
            return "certification boundary does not recognize this contract as certified"
        if contract_certified is True and coverage_confident is False:
            return "contract is certified but has no prior established coverage recorded by this suite"
        return "certification boundary or coverage context cannot confidently place this deviation within a single contract"

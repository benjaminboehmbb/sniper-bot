"""TD005-IU-014: Regression Classification Realization Unit.

Realizes TD005-SO-013's own exhaustive, four-outcome classification
behaviour, via TD005-ID-009's own ordered, short-circuiting four-step
decision sequence: (1) upstream failure -> Invalid Comparison; (2) boundary/
coverage uncertainty -> Indeterminate; (3) apply the formal equivalence
definition; (4) Regression if non-equivalent within the certified-contract
boundary, else Non-Regression.

State model (TD005-SO-013, unmodified, including the Specification's own
V1.1 explicit-re-evaluation clarification): Pending -> Evaluating -> one of
four Classified-* states; a Classified-* state may transition to a
different Classified-* state only given an explicit, independently-recorded
re-evaluation.

Forbidden: never computes severity, waiver, priority, or disposition
(TD005-AI-009, TD005-II-010); never permits Coverage output to override a
reached classification (TD005-AI-014).

Traceability: TD005-SO-013; TD005-ARC-017; TD005-AI-007, TD005-AI-008,
TD005-AI-009, TD005-AI-013, TD005-AI-014, TD005-AI-019; TD005-AD-008;
TD005-SD-001; TD005-ID-009.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from tests.regression.certification_boundary import CertificationDetermination
from tests.regression.comparison import ComparisonResult


class ClassificationOutcome(Enum):
    REGRESSION = "Regression"
    NON_REGRESSION = "Non-Regression"
    INDETERMINATE = "Indeterminate"
    INVALID_COMPARISON = "Invalid Comparison"


class ReEvaluationNotRecordedError(Exception):
    """Raised when a Classified-* -> different Classified-* transition is
    attempted without an explicit, independently-recorded re-evaluation."""


@dataclass
class ClassificationRecord:
    outcome: ClassificationOutcome
    unresolved_condition: Optional[str] = None
    re_evaluation_notes: List[str] = field(default_factory=list)


class RegressionClassifier:
    """TD005-IU-014's own realization: Pending -> Evaluating -> one of four
    Classified-* states."""

    def __init__(self) -> None:
        self._state = "Pending"
        self._record: Optional[ClassificationRecord] = None

    @property
    def state(self) -> str:
        return self._state

    @property
    def record(self) -> Optional[ClassificationRecord]:
        return self._record

    def classify(
        self,
        *,
        reference_session_state: str,
        candidate_session_state: str,
        certification_determination: Optional[CertificationDetermination],
        coverage_confident: bool,
        comparison_result: Optional[ComparisonResult],
    ) -> ClassificationRecord:
        """TD005-ID-009's own ordered, short-circuiting four-step sequence."""
        self._state = "Evaluating"

        # Step 1: any upstream unit's failure to produce its own required
        # output -> Invalid Comparison (TD005-AI-019).
        if reference_session_state != "Captured" or candidate_session_state != "Captured" or comparison_result is None:
            record = ClassificationRecord(
                outcome=ClassificationOutcome.INVALID_COMPARISON,
                unresolved_condition=(
                    f"reference_session_state={reference_session_state!r}, "
                    f"candidate_session_state={candidate_session_state!r}, "
                    f"comparison_result_available={comparison_result is not None}"
                ),
            )
            self._record = record
            self._state = "Classified-Invalid-Comparison"
            return record

        # Step 2: certification boundary or coverage context cannot
        # confidently place the deviation -> Indeterminate.
        if certification_determination is None or not certification_determination.certified or not coverage_confident:
            record = ClassificationRecord(
                outcome=ClassificationOutcome.INDETERMINATE,
                unresolved_condition=(
                    "certification boundary or coverage context cannot confidently place "
                    "the deviation inside or outside the certified-contract boundary"
                ),
            )
            self._record = record
            self._state = "Classified-Indeterminate"
            return record

        # Step 3 + 4: apply the formal equivalence definition (already
        # computed by TD005-IU-011, handed in as comparison_result).
        if comparison_result.equivalent:
            record = ClassificationRecord(outcome=ClassificationOutcome.NON_REGRESSION)
            self._state = "Classified-Non-Regression"
        else:
            record = ClassificationRecord(outcome=ClassificationOutcome.REGRESSION)
            self._state = "Classified-Regression"

        self._record = record
        return record

    def re_evaluate(self, *, re_evaluation_note: str, **classify_kwargs) -> ClassificationRecord:
        """A Classified-* state may transition to a different Classified-*
        state only given an explicit, independently-recorded re-evaluation."""
        if not self._state.startswith("Classified-"):
            raise ReEvaluationNotRecordedError("re_evaluate() requires a prior Classified-* state")
        if not re_evaluation_note:
            raise ReEvaluationNotRecordedError("a re-evaluation note is required to record the re-evaluation")

        prior_outcome = self._record.outcome if self._record else None
        new_record = self.classify(**classify_kwargs)
        new_record.re_evaluation_notes = (self._record.re_evaluation_notes if self._record else []) + [
            f"re-evaluated from {prior_outcome}: {re_evaluation_note}"
        ]
        self._record = new_record
        return new_record

from __future__ import annotations

from collections import Counter
from typing import Any

from tools.ssi.decision_evidence.decision_evidence_result import DecisionEvidenceResult

from .decision_engine_models import (
    DecisionStatistics,
    ScientificDecision,
)


class DecisionValidator:
    """
    Validates DecisionEvidenceResult and generates deterministic
    ScientificDecision objects.
    """

    def validate(
        self,
        evidence_result: DecisionEvidenceResult,
    ) -> tuple[list[ScientificDecision], DecisionStatistics]:

        self._validate_input(evidence_result)
        decisions = self._build_decisions(evidence_result)
        statistics = self._build_statistics(decisions)

        return decisions, statistics

    def _validate_input(
        self,
        evidence_result: DecisionEvidenceResult,
    ) -> None:

        if evidence_result is None:
            raise ValueError("evidence_result must not be None.")

        if evidence_result.evidence is None:
            raise ValueError("evidence must not be None.")

    def _build_decisions(
        self,
        evidence_result: DecisionEvidenceResult,
    ) -> list[ScientificDecision]:

        evidence_ids = [
            item.evidence_id
            for item in evidence_result.evidence
        ]

        if len(evidence_ids) > 0:
            decision_status = "SUPPORTED"
            explanation = (
                "Scientific decision is supported by validated "
                "Decision Evidence."
            )
        else:
            decision_status = "UNDECIDED"
            explanation = (
                "Scientific decision remains undecided because no "
                "validated Decision Evidence is available."
            )

        metadata: dict[str, Any] = {
            "source_evidence_count": len(evidence_ids),
            "source_validation_status": evidence_result.validation_summary.get(
                "status",
                "UNKNOWN",
            ),
        }

        return [
            ScientificDecision(
                decision_id="DECISION-V1-001",
                decision_status=decision_status,
                evidence_ids=evidence_ids,
                explanation=explanation,
                supporting_evidence_count=len(evidence_ids),
                metadata=metadata,
            )
        ]

    def _build_statistics(
        self,
        decisions: list[ScientificDecision],
    ) -> DecisionStatistics:

        counter = Counter(
            item.decision_status
            for item in decisions
        )

        return DecisionStatistics(
            total_decisions=len(decisions),
            decisions_by_status=dict(counter),
        )

from __future__ import annotations

from tools.ssi.decision_evidence.decision_evidence_result import DecisionEvidenceResult

from .decision_engine_result import DecisionResult
from .decision_engine_validator import DecisionValidator


class DecisionEngineProcessor:
    """
    Processes validated Decision Evidence into DecisionResult objects.
    """

    def __init__(self) -> None:
        self._validator = DecisionValidator()

    def process(
        self,
        evidence_result: DecisionEvidenceResult,
    ) -> DecisionResult:
        """
        Execute the Decision Engine pipeline.
        """

        decisions, statistics = self._validator.validate(
            evidence_result
        )

        return DecisionResult(
            decisions=decisions,
            statistics=statistics,
            validation_summary={
                "status": "PASS",
                "validated_decisions": len(decisions),
            },
        )
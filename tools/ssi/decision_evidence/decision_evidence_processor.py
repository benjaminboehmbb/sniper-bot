from __future__ import annotations

from tools.ssi.knowledge.knowledge_extraction_result import KnowledgeExtractionResult

from .decision_evidence_result import DecisionEvidenceResult
from .decision_evidence_validator import EvidenceValidator


class DecisionEvidenceProcessor:
    """
    Processes validated scientific knowledge into
    DecisionEvidenceResult objects.
    """

    def __init__(self) -> None:
        self._validator = EvidenceValidator()

    def process(
        self,
        knowledge_result: KnowledgeExtractionResult,
    ) -> DecisionEvidenceResult:
        """
        Execute the Decision Evidence pipeline.
        """

        evidence, statistics = self._validator.validate(
            knowledge_result
        )

        return DecisionEvidenceResult(
            evidence=evidence,
            statistics=statistics,
            validation_summary={
                "status": "PASS",
                "validated_evidence": len(evidence),
            },
        )
    
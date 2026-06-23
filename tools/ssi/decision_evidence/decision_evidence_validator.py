from __future__ import annotations

from collections import Counter
from typing import Any

from tools.ssi.knowledge.scientific_knowledge import Knowledge
from tools.ssi.knowledge.knowledge_extraction_result import KnowledgeExtractionResult

from .decision_evidence_models import (
    DecisionEvidence,
    DecisionEvidenceStatistics,
)


class EvidenceValidator:
    """
    Validates scientific knowledge and generates deterministic
    DecisionEvidence objects.
    """

    def validate(
        self,
        knowledge_result: KnowledgeExtractionResult,
    ) -> tuple[list[DecisionEvidence], DecisionEvidenceStatistics]:

        self._validate_input(knowledge_result)

        evidence = self._build_evidence(
            knowledge_result.knowledge_items
        )

        statistics = self._build_statistics(
            evidence
        )

        return evidence, statistics

    def _validate_input(
        self,
        knowledge_result: KnowledgeExtractionResult,
    ) -> None:

        if knowledge_result is None:
            raise ValueError("knowledge_result must not be None.")

    def _build_evidence(
        self,
        knowledge_objects: tuple[Knowledge, ...],
    ) -> list[DecisionEvidence]:

        evidence: list[DecisionEvidence] = []

        for knowledge in knowledge_objects:

            metadata: dict[str, Any] = {
                "support_count": knowledge.support_count,
                "support_ratio": knowledge.support_ratio,
                "confidence": knowledge.confidence,
                "scientific_score": knowledge.scientific_score,
                "runtime_id": knowledge.runtime_id,
                "knowledge_version": knowledge.knowledge_version,
                "evidence_source": knowledge.evidence_source,
                "source_candidate_id": knowledge.source_candidate_id,
                "validation_status": knowledge.validation_status,
            }

            evidence.append(
                DecisionEvidence(
                    evidence_id=f"EV-{knowledge.knowledge_id}",
                    knowledge_ids=[knowledge.knowledge_id],
                    evidence_type=self._map_evidence_type(
                        knowledge.knowledge_type
                    ),
                    explanation=knowledge.description,
                    supporting_knowledge_count=1,
                    metadata=metadata,
                )
            )

        return evidence

    def _build_statistics(
        self,
        evidence: list[DecisionEvidence],
    ) -> DecisionEvidenceStatistics:

        counter = Counter(
            item.evidence_type
            for item in evidence
        )

        return DecisionEvidenceStatistics(
            total_evidence=len(evidence),
            evidence_by_type=dict(counter),
        )

    def _map_evidence_type(
        self,
        knowledge_type: str,
    ) -> str:

        mapping = {
            "RepeatedStateBehaviour": "RepeatedStateEvidence",
            "NonRepeatedStateBehaviour": "NonRepeatedStateEvidence",
            "MeanDeltaForecastDominance": "ForecastEvidence",
            "HoldStateForecastEdgeCase": "BehaviourEvidence",
        }

        return mapping.get(
            knowledge_type,
            "CompositeEvidence",
        )

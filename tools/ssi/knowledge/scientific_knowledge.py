from __future__ import annotations

from dataclasses import dataclass

from tools.ssi.common.scientific_object import ScientificObject
from tools.ssi.knowledge.scientific_knowledge_candidate import KnowledgeCandidate


@dataclass(frozen=True, slots=True)
class Knowledge(ScientificObject):
    knowledge_id: str
    knowledge_type: str
    description: str

    support_count: int
    support_ratio: float

    confidence: float
    scientific_score: float

    runtime_id: str
    knowledge_version: str

    evidence_source: str
    source_candidate_id: str
    validation_status: str

    def deterministic_id(self) -> str:
        return self.knowledge_id


def knowledge_from_candidate(
    candidate: KnowledgeCandidate,
    validation_status: str = "PASS",
) -> Knowledge:
    if validation_status.strip() == "":
        raise ValueError("validation_status must not be empty")

    return Knowledge(
        knowledge_id=candidate.candidate_id.replace("|", "|knowledge|", 1),
        knowledge_type=candidate.candidate_type,
        description=candidate.description,
        support_count=candidate.support_count,
        support_ratio=candidate.support_ratio,
        confidence=candidate.confidence,
        scientific_score=candidate.scientific_score,
        runtime_id=candidate.runtime_id,
        knowledge_version=candidate.knowledge_version,
        evidence_source=candidate.evidence_source,
        source_candidate_id=candidate.candidate_id,
        validation_status=validation_status.strip(),
    )
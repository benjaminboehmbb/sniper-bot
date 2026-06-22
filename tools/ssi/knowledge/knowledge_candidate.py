from __future__ import annotations

from dataclasses import dataclass

from tools.ssi.common.scientific_object import ScientificObject


@dataclass(frozen=True, slots=True)
class KnowledgeCandidate(ScientificObject):
    candidate_id: str
    candidate_type: str
    description: str

    support_count: int
    support_ratio: float

    confidence: float
    scientific_score: float

    runtime_id: str
    knowledge_version: str

    evidence_source: str

    def deterministic_id(self) -> str:
        return self.candidate_id


def build_knowledge_candidate(
    candidate_type: str,
    description: str,
    support_count: int,
    support_ratio: float,
    confidence: float,
    scientific_score: float,
    runtime_id: str,
    evidence_source: str,
    knowledge_version: str = "v1",
) -> KnowledgeCandidate:
    if candidate_type.strip() == "":
        raise ValueError("candidate_type must not be empty")

    if description.strip() == "":
        raise ValueError("description must not be empty")

    if support_count < 0:
        raise ValueError("support_count must not be negative")

    if not 0.0 <= support_ratio <= 1.0:
        raise ValueError("support_ratio must be between 0.0 and 1.0")

    if not 0.0 <= confidence <= 1.0:
        raise ValueError("confidence must be between 0.0 and 1.0")

    if not 0.0 <= scientific_score <= 1.0:
        raise ValueError("scientific_score must be between 0.0 and 1.0")

    if runtime_id.strip() == "":
        raise ValueError("runtime_id must not be empty")

    if evidence_source.strip() == "":
        raise ValueError("evidence_source must not be empty")

    normalized_type = candidate_type.strip()

    return KnowledgeCandidate(
        candidate_id=f"{normalized_type}|{runtime_id}|{knowledge_version}",
        candidate_type=normalized_type,
        description=description.strip(),
        support_count=support_count,
        support_ratio=support_ratio,
        confidence=confidence,
        scientific_score=scientific_score,
        runtime_id=runtime_id.strip(),
        knowledge_version=knowledge_version.strip(),
        evidence_source=evidence_source.strip(),
    )
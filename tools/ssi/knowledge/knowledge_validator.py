from __future__ import annotations

from tools.ssi.knowledge.knowledge import Knowledge, knowledge_from_candidate
from tools.ssi.knowledge.knowledge_candidate import KnowledgeCandidate


class KnowledgeValidationError(ValueError):
    pass


def validate_candidate(candidate: KnowledgeCandidate) -> None:
    if candidate.candidate_id.strip() == "":
        raise KnowledgeValidationError("candidate_id must not be empty")

    if candidate.candidate_type.strip() == "":
        raise KnowledgeValidationError("candidate_type must not be empty")

    if candidate.description.strip() == "":
        raise KnowledgeValidationError("description must not be empty")

    if candidate.support_count < 0:
        raise KnowledgeValidationError("support_count must not be negative")

    if not 0.0 <= candidate.support_ratio <= 1.0:
        raise KnowledgeValidationError("support_ratio must be between 0.0 and 1.0")

    if not 0.0 <= candidate.confidence <= 1.0:
        raise KnowledgeValidationError("confidence must be between 0.0 and 1.0")

    if not 0.0 <= candidate.scientific_score <= 1.0:
        raise KnowledgeValidationError("scientific_score must be between 0.0 and 1.0")

    if candidate.runtime_id.strip() == "":
        raise KnowledgeValidationError("runtime_id must not be empty")

    if candidate.knowledge_version.strip() == "":
        raise KnowledgeValidationError("knowledge_version must not be empty")

    if candidate.evidence_source.strip() == "":
        raise KnowledgeValidationError("evidence_source must not be empty")


def validate_candidates(
    candidates: tuple[KnowledgeCandidate, ...],
    runtime_id: str,
) -> None:
    if runtime_id.strip() == "":
        raise KnowledgeValidationError("runtime_id must not be empty")

    if not candidates:
        raise KnowledgeValidationError("at least one KnowledgeCandidate is required")

    candidate_ids = set()

    for candidate in candidates:
        validate_candidate(candidate)

        if candidate.runtime_id != runtime_id:
            raise KnowledgeValidationError(
                f"candidate runtime_id mismatch: {candidate.candidate_id}"
            )

        if candidate.candidate_id in candidate_ids:
            raise KnowledgeValidationError(
                f"duplicate candidate_id: {candidate.candidate_id}"
            )

        candidate_ids.add(candidate.candidate_id)


def validate_knowledge(knowledge: Knowledge) -> None:
    if knowledge.knowledge_id.strip() == "":
        raise KnowledgeValidationError("knowledge_id must not be empty")

    if knowledge.knowledge_type.strip() == "":
        raise KnowledgeValidationError("knowledge_type must not be empty")

    if knowledge.description.strip() == "":
        raise KnowledgeValidationError("description must not be empty")

    if knowledge.support_count < 0:
        raise KnowledgeValidationError("support_count must not be negative")

    if not 0.0 <= knowledge.support_ratio <= 1.0:
        raise KnowledgeValidationError("support_ratio must be between 0.0 and 1.0")

    if not 0.0 <= knowledge.confidence <= 1.0:
        raise KnowledgeValidationError("confidence must be between 0.0 and 1.0")

    if not 0.0 <= knowledge.scientific_score <= 1.0:
        raise KnowledgeValidationError("scientific_score must be between 0.0 and 1.0")

    if knowledge.runtime_id.strip() == "":
        raise KnowledgeValidationError("runtime_id must not be empty")

    if knowledge.knowledge_version.strip() == "":
        raise KnowledgeValidationError("knowledge_version must not be empty")

    if knowledge.evidence_source.strip() == "":
        raise KnowledgeValidationError("evidence_source must not be empty")

    if knowledge.source_candidate_id.strip() == "":
        raise KnowledgeValidationError("source_candidate_id must not be empty")

    if knowledge.validation_status != "PASS":
        raise KnowledgeValidationError(
            f"knowledge validation_status must be PASS: {knowledge.knowledge_id}"
        )


def validate_knowledge_collection(
    knowledge_items: tuple[Knowledge, ...],
    runtime_id: str,
) -> None:
    if runtime_id.strip() == "":
        raise KnowledgeValidationError("runtime_id must not be empty")

    if not knowledge_items:
        raise KnowledgeValidationError("at least one Knowledge item is required")

    knowledge_ids = set()

    for knowledge in knowledge_items:
        validate_knowledge(knowledge)

        if knowledge.runtime_id != runtime_id:
            raise KnowledgeValidationError(
                f"knowledge runtime_id mismatch: {knowledge.knowledge_id}"
            )

        if knowledge.knowledge_id in knowledge_ids:
            raise KnowledgeValidationError(
                f"duplicate knowledge_id: {knowledge.knowledge_id}"
            )

        knowledge_ids.add(knowledge.knowledge_id)


def validate_and_promote_candidates(
    candidates: tuple[KnowledgeCandidate, ...],
    runtime_id: str,
) -> tuple[Knowledge, ...]:
    validate_candidates(
        candidates=candidates,
        runtime_id=runtime_id,
    )

    knowledge_items = tuple(
        knowledge_from_candidate(candidate)
        for candidate in candidates
    )

    validate_knowledge_collection(
        knowledge_items=knowledge_items,
        runtime_id=runtime_id,
    )

    return knowledge_items
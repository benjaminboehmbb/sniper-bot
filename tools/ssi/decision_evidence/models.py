from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DecisionEvidence:
    """
    Validated scientific evidence generated from one or more Knowledge objects.
    """

    evidence_id: str
    knowledge_ids: list[str]
    evidence_type: str
    explanation: str
    supporting_knowledge_count: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DecisionEvidenceStatistics:
    """
    Summary statistics for Decision Evidence generation.
    """

    total_evidence: int
    evidence_by_type: dict[str, int] = field(default_factory=dict)
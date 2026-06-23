from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ScientificDecision:
    """
    Deterministic scientific decision generated from validated evidence.
    """

    decision_id: str
    decision_status: str
    evidence_ids: list[str]
    explanation: str
    supporting_evidence_count: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DecisionStatistics:
    """
    Summary statistics for Decision Engine V1.
    """

    total_decisions: int
    decisions_by_status: dict[str, int] = field(default_factory=dict)

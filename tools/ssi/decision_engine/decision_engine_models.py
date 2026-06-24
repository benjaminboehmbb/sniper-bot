from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ScientificDecision:
    """
    Deterministic scientific decision generated from validated evidence.

    ScientificDecision is a passive data object.
    It contains no decision logic, no execution logic and no trading logic.
    """

    decision_id: str
    decision_status: str
    evidence_ids: list[str]
    explanation: str
    supporting_evidence_count: int

    evidence_sufficiency: str = "UNKNOWN"
    evidence_consistency: str = "UNKNOWN"
    evidence_completeness: str = "UNKNOWN"
    scientific_confidence: str = "UNKNOWN"
    scientific_recommendation: str = "REVIEW_REQUIRED"

    findings: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    reasoning_summary: str = ""

    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DecisionStatistics:
    """
    Summary statistics for Decision Engine.
    """

    total_decisions: int
    decisions_by_status: dict[str, int] = field(default_factory=dict)

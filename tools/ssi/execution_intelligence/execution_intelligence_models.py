from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExecutionIntent:
    """
    Deterministic execution intent generated from ScientificDecision objects.
    """

    intent_id: str
    execution_status: str
    decision_ids: list[str]
    explanation: str
    supporting_decision_count: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionIntelligenceStatistics:
    """
    Summary statistics for Execution Intelligence V1.
    """

    total_intents: int
    intents_by_status: dict[str, int] = field(default_factory=dict)
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .decision_evidence_models import (
    DecisionEvidence,
    DecisionEvidenceStatistics,
)


@dataclass(frozen=True)
class DecisionEvidenceResult:
    """
    Output of the Decision Evidence layer.
    """

    evidence: list[DecisionEvidence]
    statistics: DecisionEvidenceStatistics
    validation_summary: dict[str, Any] = field(default_factory=dict)
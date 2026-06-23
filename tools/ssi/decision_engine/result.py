from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .models import (
    DecisionStatistics,
    ScientificDecision,
)


@dataclass(frozen=True)
class DecisionResult:
    """
    Output of the Decision Engine layer.
    """

    decisions: list[ScientificDecision]
    statistics: DecisionStatistics
    validation_summary: dict[str, Any] = field(default_factory=dict)
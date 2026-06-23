from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .execution_intelligence_models import (
    ExecutionIntent,
    ExecutionIntelligenceStatistics,
)


@dataclass(frozen=True)
class ExecutionIntelligenceResult:
    """
    Output of the Execution Intelligence layer.
    """

    execution_intents: list[ExecutionIntent]
    statistics: ExecutionIntelligenceStatistics
    validation_summary: dict[str, Any] = field(default_factory=dict)
from __future__ import annotations

from tools.ssi.decision_engine.result import DecisionResult

from .execution_intelligence_result import (
    ExecutionIntelligenceResult,
)
from .execution_intelligence_validator import (
    ExecutionIntelligenceValidator,
)


class ExecutionIntelligenceProcessor:
    """
    Processes deterministic ScientificDecision objects into
    ExecutionIntelligenceResult objects.
    """

    def __init__(self) -> None:
        self._validator = ExecutionIntelligenceValidator()

    def process(
        self,
        decision_result: DecisionResult,
    ) -> ExecutionIntelligenceResult:
        """
        Execute the Execution Intelligence pipeline.
        """

        intents, statistics = self._validator.validate(
            decision_result
        )

        return ExecutionIntelligenceResult(
            execution_intents=intents,
            statistics=statistics,
            validation_summary={
                "status": "PASS",
                "validated_execution_intents": len(intents),
            },
        )
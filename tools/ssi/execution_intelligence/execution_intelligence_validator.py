from __future__ import annotations

from collections import Counter
from typing import Any

from tools.ssi.decision_engine.result import DecisionResult

from .execution_intelligence_models import (
    ExecutionIntent,
    ExecutionIntelligenceStatistics,
)


class ExecutionIntelligenceValidator:
    """
    Validates DecisionResult and generates deterministic
    ExecutionIntent objects.
    """

    def validate(
        self,
        decision_result: DecisionResult,
    ) -> tuple[list[ExecutionIntent], ExecutionIntelligenceStatistics]:
        """
        Validate DecisionResult and generate ExecutionIntent objects.
        """

        self._validate_input(decision_result)

        intents = self._build_execution_intents(
            decision_result
        )

        statistics = self._build_statistics(
            intents
        )

        return intents, statistics

    def _validate_input(
        self,
        decision_result: DecisionResult,
    ) -> None:
        """
        Validate processor input.
        """

        if decision_result is None:
            raise ValueError(
                "decision_result must not be None."
            )

        if decision_result.decisions is None:
            raise ValueError(
                "decisions must not be None."
            )

    def _build_execution_intents(
        self,
        decision_result: DecisionResult,
    ) -> list[ExecutionIntent]:
        """
        Build deterministic ExecutionIntent objects.
        """

        intents: list[ExecutionIntent] = []

        for decision in decision_result.decisions:

            if decision.decision_status == "SUPPORTED":
                execution_status = "EXECUTION_APPROVED"

            elif decision.decision_status == "NOT_SUPPORTED":
                execution_status = "EXECUTION_REJECTED"

            else:
                execution_status = "EXECUTION_DEFERRED"

            metadata: dict[str, Any] = {
                "source_decision_status": decision.decision_status,
                "source_supporting_evidence_count": (
                    decision.supporting_evidence_count
                ),
            }

            intents.append(
                ExecutionIntent(
                    intent_id=f"INTENT-{decision.decision_id}",
                    execution_status=execution_status,
                    decision_ids=[decision.decision_id],
                    explanation=decision.explanation,
                    supporting_decision_count=1,
                    metadata=metadata,
                )
            )

        return intents

    def _build_statistics(
        self,
        intents: list[ExecutionIntent],
    ) -> ExecutionIntelligenceStatistics:
        """
        Build execution statistics.
        """

        counter = Counter(
            intent.execution_status
            for intent in intents
        )

        return ExecutionIntelligenceStatistics(
            total_intents=len(intents),
            intents_by_status=dict(counter),
        )
from __future__ import annotations

from pathlib import Path

from tools.ssi.decision_engine.result import DecisionResult

from .execution_intelligence_persistence import ExecutionIntelligencePersistence
from .execution_intelligence_processor import ExecutionIntelligenceProcessor
from .execution_intelligence_renderer import ExecutionIntelligenceRenderer


class ExecutionIntelligenceRunner:
    """
    Orchestrates Execution Intelligence V1 end-to-end execution.
    """

    def __init__(
        self,
        output_dir: Path,
    ) -> None:
        self._output_dir = output_dir
        self._processor = ExecutionIntelligenceProcessor()
        self._renderer = ExecutionIntelligenceRenderer()
        self._persistence = ExecutionIntelligencePersistence()

    def run(
        self,
        decision_result: DecisionResult,
    ) -> None:
        """
        Execute processor, renderer and persistence.
        """

        result = self._processor.process(
            decision_result
        )

        artifacts = self._renderer.render(
            result
        )

        self._persistence.persist(
            artifacts=artifacts,
            output_dir=self._output_dir,
        )
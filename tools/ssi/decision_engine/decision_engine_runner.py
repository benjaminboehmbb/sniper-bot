from __future__ import annotations

from pathlib import Path

from tools.ssi.decision_evidence.decision_evidence_result import DecisionEvidenceResult

from .decision_engine_persistence import DecisionEnginePersistence
from .decision_engine_processor import DecisionEngineProcessor
from .decision_engine_renderer import DecisionEngineRenderer


class DecisionEngineRunner:
    """
    Orchestrates Decision Engine V1 end-to-end execution.
    """

    def __init__(
        self,
        output_dir: Path,
    ) -> None:
        self._output_dir = output_dir
        self._processor = DecisionEngineProcessor()
        self._renderer = DecisionEngineRenderer()
        self._persistence = DecisionEnginePersistence()

    def run(
        self,
        evidence_result: DecisionEvidenceResult,
    ) -> None:
        """
        Execute processor, renderer and persistence.
        """

        result = self._processor.process(
            evidence_result
        )

        artifacts = self._renderer.render(
            result
        )

        self._persistence.persist(
            artifacts=artifacts,
            output_dir=self._output_dir,
        )
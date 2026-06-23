from __future__ import annotations

from pathlib import Path

from tools.ssi.knowledge.knowledge_extraction_result import KnowledgeExtractionResult

from .persistence import DecisionEvidencePersistence
from .processor import DecisionEvidenceProcessor
from .renderer import DecisionEvidenceRenderer


class DecisionEvidenceRunner:
    """
    Orchestrates Decision Evidence V1 end-to-end execution.
    """

    def __init__(
        self,
        output_dir: Path,
    ) -> None:
        self._output_dir = output_dir
        self._processor = DecisionEvidenceProcessor()
        self._renderer = DecisionEvidenceRenderer()
        self._persistence = DecisionEvidencePersistence()

    def run(
        self,
        knowledge_result: KnowledgeExtractionResult,
    ) -> None:
        """
        Execute processor, renderer and persistence.
        """

        result = self._processor.process(
            knowledge_result
        )

        artifacts = self._renderer.render(
            result
        )

        self._persistence.persist(
            artifacts=artifacts,
            output_dir=self._output_dir,
        )
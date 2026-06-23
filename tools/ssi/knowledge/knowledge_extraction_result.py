from __future__ import annotations

from dataclasses import dataclass

from tools.ssi.common.scientific_result import ScientificResult, ScientificResultMetadata
from tools.ssi.knowledge.scientific_knowledge import Knowledge
from tools.ssi.knowledge.scientific_knowledge_candidate import KnowledgeCandidate


@dataclass(frozen=True, slots=True)
class KnowledgeExtractionMetrics:
    candidate_count: int
    knowledge_count: int
    validation_pass_count: int
    validation_fail_count: int

    def is_complete(self) -> bool:
        return (
            self.candidate_count == self.knowledge_count
            and self.validation_fail_count == 0
        )


@dataclass(frozen=True, slots=True)
class KnowledgeExtractionResult(ScientificResult):
    candidates: tuple[KnowledgeCandidate, ...] = tuple()
    knowledge_items: tuple[Knowledge, ...] = tuple()
    metrics: KnowledgeExtractionMetrics | None = None

    def __post_init__(self) -> None:
        if self.metrics is None:
            raise ValueError("KnowledgeExtractionResult requires metrics")

    def candidate_count(self) -> int:
        return len(self.candidates)

    def knowledge_count(self) -> int:
        return len(self.knowledge_items)

    def is_complete(self) -> bool:
        assert self.metrics is not None
        return self.metrics.is_complete()


def build_knowledge_extraction_metadata(
    runtime_id: str,
    input_path: str,
) -> ScientificResultMetadata:
    return ScientificResultMetadata(
        runtime_id=runtime_id,
        input_path=input_path,
        result_version="v1",
        conceptual_layer="Knowledge Extraction Layer",
        processing_layer="Knowledge Extraction",
        source_dataset_type="TrajectoryAnalyticsResult + ForecastingResult",
    )
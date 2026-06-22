from __future__ import annotations

from dataclasses import dataclass

from tools.ssi.analytics.state_space_summary import StateSpaceSummary
from tools.ssi.common.scientific_result import ScientificResult, ScientificResultMetadata


@dataclass(frozen=True, slots=True)
class StateAnalyticsResult(ScientificResult):
    summary: StateSpaceSummary | None = None

    def __post_init__(self) -> None:
        if self.summary is None:
            raise ValueError("StateAnalyticsResult requires summary")

    def row_count(self) -> int:
        assert self.summary is not None
        return self.summary.row_count

    def unique_state_count(self) -> int:
        assert self.summary is not None
        return self.summary.unique_state_count


def build_state_analytics_metadata(
    runtime_id: str,
    input_path: str,
) -> ScientificResultMetadata:
    return ScientificResultMetadata(
        runtime_id=runtime_id,
        input_path=input_path,
        result_version="v1a",
        conceptual_layer="State Layer",
        processing_layer="State Analytics",
        source_dataset_type="TSV",
    )
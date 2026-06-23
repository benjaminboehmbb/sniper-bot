from __future__ import annotations

from dataclasses import dataclass

from tools.ssi.common.scientific_result import ScientificResult, ScientificResultMetadata
from tools.ssi.trajectory_analytics.trajectory_analysis_model import TrajectoryAnalysis


@dataclass(frozen=True, slots=True)
class TrajectoryAnalyticsMetrics:
    trajectory_count: int
    analysis_count: int
    total_state_count: int
    total_transition_count: int
    trajectories_with_repeated_states: int
    trajectories_without_repeated_states: int

    def is_complete(self) -> bool:
        return self.trajectory_count == self.analysis_count


@dataclass(frozen=True, slots=True)
class TrajectoryAnalyticsResult(ScientificResult):
    analyses: tuple[TrajectoryAnalysis, ...] = tuple()
    metrics: TrajectoryAnalyticsMetrics | None = None

    def __post_init__(self) -> None:
        if self.metrics is None:
            raise ValueError("TrajectoryAnalyticsResult requires metrics")

    def analysis_count(self) -> int:
        return len(self.analyses)

    def is_complete(self) -> bool:
        assert self.metrics is not None
        return self.metrics.is_complete()


def build_trajectory_analytics_metadata(
    runtime_id: str,
    input_path: str,
) -> ScientificResultMetadata:
    return ScientificResultMetadata(
        runtime_id=runtime_id,
        input_path=input_path,
        result_version="v1",
        conceptual_layer="Trajectory Analytics Layer",
        processing_layer="Trajectory Analytics",
        source_dataset_type="TrajectoryReconstructionResult + TransitionAnalyticsResult",
    )
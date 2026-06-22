from __future__ import annotations

from dataclasses import dataclass

from tools.ssi.common.scientific_result import ScientificResult, ScientificResultMetadata
from tools.ssi.transition.state_transition import StateTransition


@dataclass(frozen=True, slots=True)
class TransitionAnalyticsMetrics:
    trajectory_count: int
    trajectories_with_transitions: int
    trajectories_without_transitions: int
    expected_transition_count: int
    transition_count: int

    def is_complete(self) -> bool:
        return self.expected_transition_count == self.transition_count


@dataclass(frozen=True, slots=True)
class TransitionAnalyticsResult(ScientificResult):
    transitions: tuple[StateTransition, ...] = tuple()
    metrics: TransitionAnalyticsMetrics | None = None

    def __post_init__(self) -> None:
        if self.metrics is None:
            raise ValueError("TransitionAnalyticsResult requires metrics")

    def transition_count(self) -> int:
        return len(self.transitions)

    def is_complete(self) -> bool:
        assert self.metrics is not None
        return self.metrics.is_complete()


def build_transition_analytics_metadata(
    runtime_id: str,
    input_path: str,
) -> ScientificResultMetadata:
    return ScientificResultMetadata(
        runtime_id=runtime_id,
        input_path=input_path,
        result_version="v1",
        conceptual_layer="Transition Layer",
        processing_layer="Transition Analytics",
        source_dataset_type="TradeTrajectory",
    )

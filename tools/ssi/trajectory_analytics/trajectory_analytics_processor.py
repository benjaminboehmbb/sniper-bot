from __future__ import annotations

from dataclasses import dataclass

from tools.ssi.common.scientific_object import ScientificObject
from tools.ssi.common.scientific_processor import ScientificProcessor
from tools.ssi.trajectory.trajectory_reconstruction_result import (
    TrajectoryReconstructionResult,
)
from tools.ssi.transition.transition_analytics_result import TransitionAnalyticsResult
from tools.ssi.trajectory_analytics.trajectory_analysis import build_trajectory_analysis
from tools.ssi.trajectory_analytics.trajectory_analytics_result import (
    TrajectoryAnalyticsMetrics,
    TrajectoryAnalyticsResult,
    build_trajectory_analytics_metadata,
)


@dataclass(frozen=True, slots=True)
class TrajectoryAnalyticsInput(ScientificObject):
    trajectory_result: TrajectoryReconstructionResult
    transition_result: TransitionAnalyticsResult
    runtime_id: str
    input_path: str


class TrajectoryAnalyticsProcessor(
    ScientificProcessor[TrajectoryAnalyticsInput, TrajectoryAnalyticsResult]
):
    def validate_input(self, input_object: TrajectoryAnalyticsInput) -> None:
        if input_object.runtime_id.strip() == "":
            raise ValueError("runtime_id must not be empty")

        if input_object.input_path.strip() == "":
            raise ValueError("input_path must not be empty")

        if input_object.trajectory_result.metrics is None:
            raise ValueError("trajectory_result requires metrics")

        if input_object.transition_result.metrics is None:
            raise ValueError("transition_result requires metrics")

        if not input_object.trajectory_result.is_complete():
            raise ValueError("trajectory_result is incomplete")

        if not input_object.transition_result.is_complete():
            raise ValueError("transition_result is incomplete")

        if (
            input_object.trajectory_result.metadata.runtime_id
            != input_object.transition_result.metadata.runtime_id
        ):
            raise ValueError("trajectory_result and transition_result runtime_id mismatch")

    def process(
        self,
        input_object: TrajectoryAnalyticsInput,
    ) -> TrajectoryAnalyticsResult:
        self.validate_input(input_object)

        transitions_by_trajectory = _group_transitions_by_trajectory(
            input_object.transition_result
        )

        analyses = []

        for trajectory in input_object.trajectory_result.trajectories:
            transitions = transitions_by_trajectory.get(
                trajectory.trajectory_id,
                tuple(),
            )

            analyses.append(
                build_trajectory_analysis(
                    trajectory=trajectory,
                    transitions=transitions,
                    runtime_id=input_object.runtime_id,
                )
            )

        metrics = TrajectoryAnalyticsMetrics(
            trajectory_count=len(input_object.trajectory_result.trajectories),
            analysis_count=len(analyses),
            total_state_count=sum(analysis.state_count for analysis in analyses),
            total_transition_count=sum(analysis.transition_count for analysis in analyses),
            trajectories_with_repeated_states=sum(
                1 for analysis in analyses if analysis.repeated_state_count > 0
            ),
            trajectories_without_repeated_states=sum(
                1 for analysis in analyses if analysis.repeated_state_count == 0
            ),
        )

        validation_status = "PASS" if metrics.is_complete() else "FAIL"

        return TrajectoryAnalyticsResult(
            metadata=build_trajectory_analytics_metadata(
                runtime_id=input_object.runtime_id,
                input_path=input_object.input_path,
            ),
            validation_status=validation_status,
            analyses=tuple(analyses),
            metrics=metrics,
        )


def _group_transitions_by_trajectory(
    transition_result: TransitionAnalyticsResult,
) -> dict[str, tuple]:
    grouped: dict[str, list] = {}

    for transition in transition_result.transitions:
        grouped.setdefault(transition.trajectory_id, []).append(transition)

    return {
        trajectory_id: tuple(
            sorted(
                transitions,
                key=lambda transition: transition.transition_index,
            )
        )
        for trajectory_id, transitions in grouped.items()
    }
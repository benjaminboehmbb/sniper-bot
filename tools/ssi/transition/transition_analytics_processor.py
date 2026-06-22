from __future__ import annotations

from dataclasses import dataclass

from tools.ssi.common.scientific_object import ScientificObject
from tools.ssi.common.scientific_processor import ScientificProcessor
from tools.ssi.trajectory.trajectory_reconstruction_result import (
    TrajectoryReconstructionResult,
)
from tools.ssi.transition.state_transition import build_transitions_for_trajectory
from tools.ssi.transition.transition_analytics_result import (
    TransitionAnalyticsMetrics,
    TransitionAnalyticsResult,
    build_transition_analytics_metadata,
)


@dataclass(frozen=True, slots=True)
class TransitionAnalyticsInput(ScientificObject):
    trajectory_result: TrajectoryReconstructionResult
    runtime_id: str
    input_path: str


class TransitionAnalyticsProcessor(
    ScientificProcessor[TransitionAnalyticsInput, TransitionAnalyticsResult]
):
    def validate_input(self, input_object: TransitionAnalyticsInput) -> None:
        if input_object.runtime_id.strip() == "":
            raise ValueError("runtime_id must not be empty")

        if input_object.input_path.strip() == "":
            raise ValueError("input_path must not be empty")

        if input_object.trajectory_result.metrics is None:
            raise ValueError("trajectory_result requires metrics")

        if not input_object.trajectory_result.is_complete():
            raise ValueError("trajectory_result is incomplete")

    def process(
        self,
        input_object: TransitionAnalyticsInput,
    ) -> TransitionAnalyticsResult:
        self.validate_input(input_object)

        trajectories = input_object.trajectory_result.trajectories
        transitions = []

        for trajectory in trajectories:
            transitions.extend(
                build_transitions_for_trajectory(
                    trajectory_id=trajectory.trajectory_id,
                    runtime_trade_id=trajectory.runtime_trade_id,
                    states=trajectory.states,
                    reconstruction_method="trajectory_reconstruction_v1",
                )
            )

        expected_transition_count = sum(
            max(0, trajectory.state_count() - 1)
            for trajectory in trajectories
        )

        trajectories_with_transitions = sum(
            1 for trajectory in trajectories if trajectory.has_transitions()
        )

        trajectories_without_transitions = (
            len(trajectories) - trajectories_with_transitions
        )

        metrics = TransitionAnalyticsMetrics(
            trajectory_count=len(trajectories),
            trajectories_with_transitions=trajectories_with_transitions,
            trajectories_without_transitions=trajectories_without_transitions,
            expected_transition_count=expected_transition_count,
            transition_count=len(transitions),
        )

        validation_status = "PASS" if metrics.is_complete() else "FAIL"

        return TransitionAnalyticsResult(
            metadata=build_transition_analytics_metadata(
                runtime_id=input_object.runtime_id,
                input_path=input_object.input_path,
            ),
            validation_status=validation_status,
            transitions=tuple(transitions),
            metrics=metrics,
        )
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from tools.ssi.common.scientific_object import ScientificObject
from tools.ssi.trajectory.trade_trajectory import TradeTrajectory
from tools.ssi.transition.state_transition import StateTransition


@dataclass(frozen=True, slots=True)
class TrajectoryAnalysis(ScientificObject):
    trajectory_id: str
    runtime_trade_id: str

    state_count: int
    transition_count: int
    duration_sec: float

    unique_state_count: int
    repeated_state_count: int

    mean_progress_delta: float
    mean_compatibility_delta: float
    mean_stability_delta: float
    mean_confidence_delta: float

    max_positive_pnl_delta: float
    max_negative_pnl_delta: float
    cumulative_pnl_delta: float

    first_timestamp_utc: datetime
    last_timestamp_utc: datetime

    runtime_id: str
    analysis_version: str

    def deterministic_id(self) -> str:
        return self.trajectory_id


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def build_trajectory_analysis(
    trajectory: TradeTrajectory,
    transitions: tuple[StateTransition, ...],
    runtime_id: str,
    analysis_version: str = "v1",
) -> TrajectoryAnalysis:
    transition_count = len(transitions)

    expected_transition_count = max(0, trajectory.state_count() - 1)
    if transition_count != expected_transition_count:
        raise ValueError(
            "transition_count does not match state_count - 1 "
            f"for trajectory {trajectory.trajectory_id}"
        )

    state_ids = [
        state.state_key.deterministic_id()
        for state in trajectory.states
    ]

    unique_state_count = len(set(state_ids))
    repeated_state_count = len(state_ids) - unique_state_count

    progress_deltas = [t.delta_progress for t in transitions]
    compatibility_deltas = [t.delta_compatibility for t in transitions]
    stability_deltas = [t.delta_stability for t in transitions]
    confidence_deltas = [t.delta_confidence for t in transitions]
    pnl_deltas = [t.delta_unrealized_pnl for t in transitions]

    positive_pnl_deltas = [value for value in pnl_deltas if value > 0]
    negative_pnl_deltas = [value for value in pnl_deltas if value < 0]

    return TrajectoryAnalysis(
        trajectory_id=trajectory.trajectory_id,
        runtime_trade_id=trajectory.runtime_trade_id,

        state_count=trajectory.state_count(),
        transition_count=transition_count,
        duration_sec=trajectory.duration_sec,

        unique_state_count=unique_state_count,
        repeated_state_count=repeated_state_count,

        mean_progress_delta=_mean(progress_deltas),
        mean_compatibility_delta=_mean(compatibility_deltas),
        mean_stability_delta=_mean(stability_deltas),
        mean_confidence_delta=_mean(confidence_deltas),

        max_positive_pnl_delta=max(positive_pnl_deltas) if positive_pnl_deltas else 0.0,
        max_negative_pnl_delta=min(negative_pnl_deltas) if negative_pnl_deltas else 0.0,
        cumulative_pnl_delta=sum(pnl_deltas),

        first_timestamp_utc=trajectory.first_timestamp_utc,
        last_timestamp_utc=trajectory.last_timestamp_utc,

        runtime_id=runtime_id,
        analysis_version=analysis_version,
    )
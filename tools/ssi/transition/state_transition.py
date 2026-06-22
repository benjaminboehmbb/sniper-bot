from __future__ import annotations

from dataclasses import dataclass

from tools.ssi.common.scientific_object import ScientificObject
from tools.ssi.trajectory.trade_trajectory import TrajectoryState


@dataclass(frozen=True, slots=True)
class StateTransition(ScientificObject):
    transition_id: str
    trajectory_id: str
    runtime_trade_id: str

    source_state: TrajectoryState
    target_state: TrajectoryState

    transition_index: int
    reconstruction_method: str

    delta_progress: float
    delta_compatibility: float
    delta_stability: float
    delta_confidence: float
    delta_unrealized_pnl: float
    delta_duration_sec: float

    def deterministic_id(self) -> str:
        return self.transition_id


def _state_value(value: str) -> float:
    return float(value)


def build_state_transition(
    trajectory_id: str,
    runtime_trade_id: str,
    source_state: TrajectoryState,
    target_state: TrajectoryState,
    transition_index: int,
    reconstruction_method: str,
) -> StateTransition:
    source_key = source_state.state_key
    target_key = target_state.state_key

    return StateTransition(
        transition_id=(
            f"{trajectory_id}"
            f"|{source_state.snapshot_id}"
            f"|{target_state.snapshot_id}"
        ),
        trajectory_id=trajectory_id,
        runtime_trade_id=runtime_trade_id,

        source_state=source_state,
        target_state=target_state,

        transition_index=transition_index,
        reconstruction_method=reconstruction_method,

        delta_progress=(
            _state_value(target_key.progress)
            - _state_value(source_key.progress)
        ),
        delta_compatibility=(
            _state_value(target_key.compatibility)
            - _state_value(source_key.compatibility)
        ),
        delta_stability=(
            _state_value(target_key.stability)
            - _state_value(source_key.stability)
        ),
        delta_confidence=(
            _state_value(target_key.confidence)
            - _state_value(source_key.confidence)
        ),
        delta_unrealized_pnl=(
            target_state.unrealized_pnl
            - source_state.unrealized_pnl
        ),
        delta_duration_sec=(
            target_state.duration_sec
            - source_state.duration_sec
        ),
    )


def build_transitions_for_trajectory(
    trajectory_id: str,
    runtime_trade_id: str,
    states: tuple[TrajectoryState, ...],
    reconstruction_method: str,
) -> tuple[StateTransition, ...]:
    if len(states) < 2:
        return tuple()

    transitions = []

    for index in range(len(states) - 1):
        transitions.append(
            build_state_transition(
                trajectory_id=trajectory_id,
                runtime_trade_id=runtime_trade_id,
                source_state=states[index],
                target_state=states[index + 1],
                transition_index=index,
                reconstruction_method=reconstruction_method,
            )
        )

    return tuple(transitions)
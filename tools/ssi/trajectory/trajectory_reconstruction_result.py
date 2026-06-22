from __future__ import annotations

from dataclasses import dataclass

from tools.ssi.common.scientific_result import ScientificResult, ScientificResultMetadata
from tools.ssi.trajectory.trade_trajectory import TradeTrajectory


@dataclass(frozen=True, slots=True)
class TrajectoryReconstructionMetrics:
    runtime_trade_count: int
    trajectory_count: int
    tsv_state_count: int
    assigned_state_count: int
    unassigned_state_count: int
    trajectories_with_transitions: int
    trajectories_without_transitions: int
    side_mismatch_count: int

    def is_complete(self) -> bool:
        return (
            self.runtime_trade_count == self.trajectory_count
            and self.tsv_state_count == self.assigned_state_count
            and self.unassigned_state_count == 0
            and self.side_mismatch_count == 0
        )


@dataclass(frozen=True, slots=True)
class TrajectoryReconstructionResult(ScientificResult):
    trajectories: tuple[TradeTrajectory, ...] = tuple()
    metrics: TrajectoryReconstructionMetrics | None = None

    def __post_init__(self) -> None:
        if self.metrics is None:
            raise ValueError("TrajectoryReconstructionResult requires metrics")

    def trajectory_count(self) -> int:
        return len(self.trajectories)

    def is_complete(self) -> bool:
        assert self.metrics is not None
        return self.metrics.is_complete()


def build_trajectory_reconstruction_metadata(
    runtime_id: str,
    input_path: str,
) -> ScientificResultMetadata:
    return ScientificResultMetadata(
        runtime_id=runtime_id,
        input_path=input_path,
        result_version="v1",
        conceptual_layer="Trajectory Layer",
        processing_layer="Trajectory Reconstruction",
        source_dataset_type="TSV + trades_l1 JSONL",
    )
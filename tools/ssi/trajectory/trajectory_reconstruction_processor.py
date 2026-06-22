from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tools.ssi.analytics.load_tsv import load_tsv_rows, require_columns
from tools.ssi.common.scientific_object import ScientificObject
from tools.ssi.common.scientific_processor import ScientificProcessor
from tools.ssi.trajectory.trade_runtime import RuntimeTrade, load_runtime_trades
from tools.ssi.trajectory.trade_trajectory import (
    TradeTrajectory,
    build_trade_trajectory,
    parse_tsv_datetime,
    trajectory_state_from_tsv_row,
)
from tools.ssi.trajectory.trajectory_reconstruction_result import (
    TrajectoryReconstructionMetrics,
    TrajectoryReconstructionResult,
    build_trajectory_reconstruction_metadata,
)


REQUIRED_TSV_COLUMNS = [
    "snapshot_id",
    "timestamp_utc",
    "tsv_id",
    "source_row_index",
    "side",
    "progress",
    "compatibility",
    "stability",
    "confidence",
    "unrealized_pnl",
    "duration_sec",
]


@dataclass(frozen=True, slots=True)
class TrajectoryReconstructionInput(ScientificObject):
    tsv_input_path: Path
    trades_input_path: Path
    runtime_id: str


class TrajectoryReconstructionProcessor(
    ScientificProcessor[TrajectoryReconstructionInput, TrajectoryReconstructionResult]
):
    def validate_input(self, input_object: TrajectoryReconstructionInput) -> None:
        if input_object.runtime_id.strip() == "":
            raise ValueError("runtime_id must not be empty")

        for path in [input_object.tsv_input_path, input_object.trades_input_path]:
            if not path.exists():
                raise ValueError(f"input path does not exist: {path}")

            if not path.is_file():
                raise ValueError(f"input path is not a file: {path}")

            if path.stat().st_size <= 0:
                raise ValueError(f"input path is empty: {path}")

    def process(
        self,
        input_object: TrajectoryReconstructionInput,
    ) -> TrajectoryReconstructionResult:
        self.validate_input(input_object)

        rows, header = load_tsv_rows(input_object.tsv_input_path)
        require_columns(header, REQUIRED_TSV_COLUMNS)

        trades = load_runtime_trades(input_object.trades_input_path)

        trajectories, assigned_count, side_mismatch_count = _reconstruct_trajectories(
            rows=rows,
            trades=trades,
        )

        trajectories_with_transitions = sum(
            1 for trajectory in trajectories if trajectory.has_transitions()
        )
        trajectories_without_transitions = len(trajectories) - trajectories_with_transitions

        metrics = TrajectoryReconstructionMetrics(
            runtime_trade_count=len(trades),
            trajectory_count=len(trajectories),
            tsv_state_count=len(rows),
            assigned_state_count=assigned_count,
            unassigned_state_count=len(rows) - assigned_count,
            trajectories_with_transitions=trajectories_with_transitions,
            trajectories_without_transitions=trajectories_without_transitions,
            side_mismatch_count=side_mismatch_count,
        )

        validation_status = "PASS" if metrics.is_complete() else "FAIL"

        return TrajectoryReconstructionResult(
            metadata=build_trajectory_reconstruction_metadata(
                runtime_id=input_object.runtime_id,
                input_path=str(input_object.tsv_input_path),
            ),
            validation_status=validation_status,
            trajectories=tuple(trajectories),
            metrics=metrics,
        )


def _reconstruct_trajectories(
    rows: list[dict[str, str]],
    trades: list[RuntimeTrade],
) -> tuple[list[TradeTrajectory], int, int]:
    trajectories: list[TradeTrajectory] = []
    assigned_snapshot_ids: set[str] = set()
    side_mismatch_count = 0

    rows_with_time = [
        (row, parse_tsv_datetime(row["timestamp_utc"]))
        for row in rows
    ]

    for trade in trades:
        matched_states = []

        for row, timestamp_utc in rows_with_time:
            if not (trade.entry_timestamp_utc <= timestamp_utc <= trade.exit_timestamp_utc):
                continue

            snapshot_side = str(row["side"]).strip().upper()

            if snapshot_side != trade.side:
                side_mismatch_count += 1
                continue

            matched_states.append(trajectory_state_from_tsv_row(row))
            assigned_snapshot_ids.add(str(row["snapshot_id"]).strip())

        if not matched_states:
            continue

        trajectories.append(
            build_trade_trajectory(
                runtime_trade_id=trade.trade_id,
                side=trade.side,
                states=matched_states,
                reconstruction_method="timestamp_interval_side_join_v1",
                reconstruction_confidence=1.0,
            )
        )

    return trajectories, len(assigned_snapshot_ids), side_mismatch_count
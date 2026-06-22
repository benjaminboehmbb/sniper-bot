from __future__ import annotations

from datetime import datetime, timezone

from tools.ssi.common.scientific_artifacts import (
    CSVArtifact,
    JSONArtifact,
    ScientificArtifacts,
    TextArtifact,
)
from tools.ssi.common.scientific_renderer import ScientificRenderer
from tools.ssi.trajectory.trajectory_reconstruction_result import (
    TrajectoryReconstructionResult,
)


class TrajectoryReconstructionRenderer(
    ScientificRenderer[TrajectoryReconstructionResult]
):
    def render(
        self,
        result: TrajectoryReconstructionResult,
    ) -> ScientificArtifacts:
        return ScientificArtifacts(
            csv_artifacts=(
                _render_trajectory_summary(result),
            ),
            text_artifacts=(
                _render_report(result),
            ),
            json_artifacts=(
                _render_manifest(result),
            ),
        )


def _render_trajectory_summary(
    result: TrajectoryReconstructionResult,
) -> CSVArtifact:
    rows = []

    for trajectory in result.trajectories:
        rows.append([
            trajectory.trajectory_id,
            trajectory.runtime_trade_id,
            trajectory.side,
            str(trajectory.state_count()),
            trajectory.first_timestamp_utc.isoformat(),
            trajectory.last_timestamp_utc.isoformat(),
            f"{trajectory.duration_sec:.1f}",
            trajectory.reconstruction_method,
            f"{trajectory.reconstruction_confidence:.3f}",
        ])

    return CSVArtifact(
        filename="trajectory_summary_v1.csv",
        header=[
            "trajectory_id",
            "runtime_trade_id",
            "side",
            "state_count",
            "first_timestamp",
            "last_timestamp",
            "duration_sec",
            "reconstruction_method",
            "reconstruction_confidence",
        ],
        rows=rows,
    )


def _render_report(
    result: TrajectoryReconstructionResult,
) -> TextArtifact:
    m = result.metrics
    assert m is not None

    lines = [
        "# SSI TRAJECTORY RECONSTRUCTION REPORT",
        "",
        f"Runtime ID: {result.metadata.runtime_id}",
        "",
        "## Summary",
        "",
        f"Runtime trades: {m.runtime_trade_count}",
        f"Trajectories: {m.trajectory_count}",
        f"TSV states: {m.tsv_state_count}",
        f"Assigned states: {m.assigned_state_count}",
        f"Unassigned states: {m.unassigned_state_count}",
        f"Trajectories with transitions: {m.trajectories_with_transitions}",
        f"Trajectories without transitions: {m.trajectories_without_transitions}",
        f"Side mismatches: {m.side_mismatch_count}",
        "",
        "Validation:",
        result.validation_status,
    ]

    return TextArtifact(
        filename="trajectory_reconstruction_report.md",
        content="\n".join(lines),
    )


def _render_manifest(
    result: TrajectoryReconstructionResult,
) -> JSONArtifact:
    m = result.metrics
    assert m is not None

    return JSONArtifact(
        filename="trajectory_reconstruction_manifest.json",
        content={
            "artifact_type": "trajectory_reconstruction_v1",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "runtime_id": result.metadata.runtime_id,
            "validation_status": result.validation_status,
            "trajectory_count": m.trajectory_count,
            "runtime_trade_count": m.runtime_trade_count,
            "assigned_state_count": m.assigned_state_count,
            "unassigned_state_count": m.unassigned_state_count,
            "side_mismatch_count": m.side_mismatch_count,
        },
    )
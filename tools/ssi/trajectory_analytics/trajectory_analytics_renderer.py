from __future__ import annotations

from datetime import datetime, timezone

from tools.ssi.common.scientific_artifacts import (
    CSVArtifact,
    JSONArtifact,
    ScientificArtifacts,
    TextArtifact,
)
from tools.ssi.common.scientific_renderer import ScientificRenderer
from tools.ssi.trajectory_analytics.trajectory_analytics_result import (
    TrajectoryAnalyticsResult,
)


class TrajectoryAnalyticsRenderer(ScientificRenderer[TrajectoryAnalyticsResult]):
    def render(
        self,
        result: TrajectoryAnalyticsResult,
    ) -> ScientificArtifacts:
        return ScientificArtifacts(
            csv_artifacts=(
                _render_trajectory_analysis(result),
            ),
            text_artifacts=(
                _render_report(result),
            ),
            json_artifacts=(
                _render_manifest(result),
            ),
        )


def _format_float(value: float) -> str:
    return f"{value:.10f}"


def _render_trajectory_analysis(
    result: TrajectoryAnalyticsResult,
) -> CSVArtifact:
    rows = []

    for analysis in result.analyses:
        rows.append([
            analysis.trajectory_id,
            analysis.runtime_trade_id,
            str(analysis.state_count),
            str(analysis.transition_count),
            _format_float(analysis.duration_sec),
            str(analysis.unique_state_count),
            str(analysis.repeated_state_count),
            _format_float(analysis.mean_progress_delta),
            _format_float(analysis.mean_compatibility_delta),
            _format_float(analysis.mean_stability_delta),
            _format_float(analysis.mean_confidence_delta),
            _format_float(analysis.max_positive_pnl_delta),
            _format_float(analysis.max_negative_pnl_delta),
            _format_float(analysis.cumulative_pnl_delta),
            analysis.first_timestamp_utc.isoformat(),
            analysis.last_timestamp_utc.isoformat(),
            analysis.runtime_id,
            analysis.analysis_version,
        ])

    return CSVArtifact(
        filename="trajectory_analysis_v1.csv",
        header=[
            "trajectory_id",
            "runtime_trade_id",
            "state_count",
            "transition_count",
            "duration_sec",
            "unique_state_count",
            "repeated_state_count",
            "mean_progress_delta",
            "mean_compatibility_delta",
            "mean_stability_delta",
            "mean_confidence_delta",
            "max_positive_pnl_delta",
            "max_negative_pnl_delta",
            "cumulative_pnl_delta",
            "first_timestamp_utc",
            "last_timestamp_utc",
            "runtime_id",
            "analysis_version",
        ],
        rows=rows,
    )


def _render_report(
    result: TrajectoryAnalyticsResult,
) -> TextArtifact:
    m = result.metrics
    assert m is not None

    lines = [
        "# SSI TRAJECTORY ANALYTICS V1 REPORT",
        "",
        f"Runtime ID: {result.metadata.runtime_id}",
        "",
        "## Summary",
        "",
        f"Trajectories: {m.trajectory_count}",
        f"Analyses: {m.analysis_count}",
        f"Total states: {m.total_state_count}",
        f"Total transitions: {m.total_transition_count}",
        f"Trajectories with repeated states: {m.trajectories_with_repeated_states}",
        f"Trajectories without repeated states: {m.trajectories_without_repeated_states}",
        "",
        "Validation:",
        result.validation_status,
        "",
        "## Interpretation Boundary",
        "",
        "This report describes deterministic trajectory-level descriptors only.",
        "It does not perform clustering, forecasting, anomaly scoring or execution decisions.",
    ]

    return TextArtifact(
        filename="trajectory_analytics_report.md",
        content="\n".join(lines),
    )


def _render_manifest(
    result: TrajectoryAnalyticsResult,
) -> JSONArtifact:
    m = result.metrics
    assert m is not None

    return JSONArtifact(
        filename="trajectory_analytics_manifest.json",
        content={
            "artifact_type": "trajectory_analytics_v1",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "runtime_id": result.metadata.runtime_id,
            "validation_status": result.validation_status,
            "trajectory_count": m.trajectory_count,
            "analysis_count": m.analysis_count,
            "total_state_count": m.total_state_count,
            "total_transition_count": m.total_transition_count,
            "trajectories_with_repeated_states": m.trajectories_with_repeated_states,
            "trajectories_without_repeated_states": m.trajectories_without_repeated_states,
        },
    )
from __future__ import annotations

from datetime import datetime, timezone

from tools.ssi.common.scientific_artifacts import (
    CSVArtifact,
    JSONArtifact,
    ScientificArtifacts,
    TextArtifact,
)
from tools.ssi.common.scientific_renderer import ScientificRenderer
from tools.ssi.transition.transition_analytics_result import TransitionAnalyticsResult


class TransitionAnalyticsRenderer(ScientificRenderer[TransitionAnalyticsResult]):
    def render(
        self,
        result: TransitionAnalyticsResult,
    ) -> ScientificArtifacts:
        return ScientificArtifacts(
            csv_artifacts=(
                _render_transition_summary(result),
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


def _render_transition_summary(
    result: TransitionAnalyticsResult,
) -> CSVArtifact:
    rows = []

    for transition in result.transitions:
        rows.append([
            transition.transition_id,
            transition.trajectory_id,
            transition.runtime_trade_id,
            str(transition.transition_index),
            transition.source_state.snapshot_id,
            transition.target_state.snapshot_id,
            transition.source_state.timestamp_utc.isoformat(),
            transition.target_state.timestamp_utc.isoformat(),
            transition.source_state.state_key.deterministic_id(),
            transition.target_state.state_key.deterministic_id(),
            _format_float(transition.delta_progress),
            _format_float(transition.delta_compatibility),
            _format_float(transition.delta_stability),
            _format_float(transition.delta_confidence),
            _format_float(transition.delta_unrealized_pnl),
            _format_float(transition.delta_duration_sec),
            transition.reconstruction_method,
        ])

    return CSVArtifact(
        filename="transition_summary_v1.csv",
        header=[
            "transition_id",
            "trajectory_id",
            "runtime_trade_id",
            "transition_index",
            "source_snapshot_id",
            "target_snapshot_id",
            "source_timestamp",
            "target_timestamp",
            "source_state_id",
            "target_state_id",
            "delta_progress",
            "delta_compatibility",
            "delta_stability",
            "delta_confidence",
            "delta_unrealized_pnl",
            "delta_duration_sec",
            "reconstruction_method",
        ],
        rows=rows,
    )


def _render_report(
    result: TransitionAnalyticsResult,
) -> TextArtifact:
    m = result.metrics
    assert m is not None

    lines = [
        "# SSI TRANSITION ANALYTICS V1 REPORT",
        "",
        f"Runtime ID: {result.metadata.runtime_id}",
        "",
        "## Summary",
        "",
        f"Trajectories: {m.trajectory_count}",
        f"Trajectories with transitions: {m.trajectories_with_transitions}",
        f"Trajectories without transitions: {m.trajectories_without_transitions}",
        f"Expected transitions: {m.expected_transition_count}",
        f"Generated transitions: {m.transition_count}",
        "",
        "Validation:",
        result.validation_status,
        "",
        "## Interpretation Boundary",
        "",
        "This report describes deterministic state transitions only.",
        "It does not perform forecasting, clustering, performance attribution or execution decisions.",
    ]

    return TextArtifact(
        filename="transition_analytics_report.md",
        content="\n".join(lines),
    )


def _render_manifest(
    result: TransitionAnalyticsResult,
) -> JSONArtifact:
    m = result.metrics
    assert m is not None

    return JSONArtifact(
        filename="transition_analytics_manifest.json",
        content={
            "artifact_type": "transition_analytics_v1",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "runtime_id": result.metadata.runtime_id,
            "validation_status": result.validation_status,
            "trajectory_count": m.trajectory_count,
            "trajectories_with_transitions": m.trajectories_with_transitions,
            "trajectories_without_transitions": m.trajectories_without_transitions,
            "expected_transition_count": m.expected_transition_count,
            "transition_count": m.transition_count,
        },
    )
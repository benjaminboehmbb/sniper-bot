from __future__ import annotations

from datetime import datetime, timezone

from tools.ssi.analytics.state_analytics_result import StateAnalyticsResult
from tools.ssi.common.scientific_artifacts import (
    CSVArtifact,
    JSONArtifact,
    ScientificArtifacts,
    TextArtifact,
)
from tools.ssi.common.scientific_renderer import ScientificRenderer


class StateAnalyticsRenderer(ScientificRenderer[StateAnalyticsResult]):
    def render(self, result: StateAnalyticsResult) -> ScientificArtifacts:
        if result.summary is None:
            raise ValueError("StateAnalyticsResult has no summary")

        return ScientificArtifacts(
            csv_artifacts=(
                _render_state_frequencies(result),
                _render_dimension_frequencies(result),
                _render_side_summary(result),
                _render_numeric_summary(result),
            ),
            text_artifacts=(
                _render_markdown_report(result),
            ),
            json_artifacts=(
                _render_manifest(result),
            ),
        )


def _format_float(value: float) -> str:
    return f"{value:.10f}"


def _render_state_frequencies(result: StateAnalyticsResult) -> CSVArtifact:
    assert result.summary is not None

    rows = [
        [
            item.state_id,
            str(item.count),
            _format_float(item.share),
        ]
        for item in result.summary.state_frequencies
    ]

    return CSVArtifact(
        filename="state_frequencies_v1a.csv",
        header=["state_id", "count", "share"],
        rows=rows,
    )


def _render_dimension_frequencies(result: StateAnalyticsResult) -> CSVArtifact:
    assert result.summary is not None

    rows = [
        [
            item.dimension,
            item.value,
            str(item.count),
            _format_float(item.share),
        ]
        for item in result.summary.dimension_frequencies
    ]

    return CSVArtifact(
        filename="dimension_frequencies_v1a.csv",
        header=["dimension", "value", "count", "share"],
        rows=rows,
    )


def _render_side_summary(result: StateAnalyticsResult) -> CSVArtifact:
    assert result.summary is not None

    rows = [
        [
            item.side,
            str(item.count),
            _format_float(item.share),
            _format_float(item.avg_unrealized_pnl),
        ]
        for item in result.summary.side_summary
    ]

    return CSVArtifact(
        filename="side_summary_v1a.csv",
        header=["side", "count", "share", "avg_unrealized_pnl"],
        rows=rows,
    )


def _render_numeric_summary(result: StateAnalyticsResult) -> CSVArtifact:
    assert result.summary is not None

    rows = [
        [
            item.column,
            str(item.count),
            _format_float(item.min_value),
            _format_float(item.max_value),
            _format_float(item.mean_value),
        ]
        for item in result.summary.numeric_summary
    ]

    return CSVArtifact(
        filename="numeric_summary_v1a.csv",
        header=["column", "count", "min", "max", "mean"],
        rows=rows,
    )


def _render_markdown_report(result: StateAnalyticsResult) -> TextArtifact:
    assert result.summary is not None

    summary = result.summary
    metadata = result.metadata

    lines: list[str] = []

    lines.append("# SSI STATE ANALYTICS V1A REPORT")
    lines.append("")
    lines.append("Date:")
    lines.append("2026-06-22")
    lines.append("")
    lines.append("Project:")
    lines.append("Sniper-Bot")
    lines.append("")
    lines.append("Platform:")
    lines.append("State Space Intelligence (SSI)")
    lines.append("")
    lines.append("Component:")
    lines.append(metadata.processing_layer)
    lines.append("")
    lines.append("Status:")
    lines.append(result.validation_status)
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("# 1. Input")
    lines.append("")
    lines.append(f"Runtime ID: {metadata.runtime_id}")
    lines.append("")
    lines.append(f"Input TSV: {metadata.input_path}")
    lines.append("")
    lines.append(f"Result Version: {metadata.result_version}")
    lines.append("")
    lines.append(f"Conceptual Layer: {metadata.conceptual_layer}")
    lines.append("")
    lines.append(f"Source Dataset Type: {metadata.source_dataset_type}")
    lines.append("")
    lines.append("# 2. State-Space Summary")
    lines.append("")
    lines.append(f"Rows: {summary.row_count}")
    lines.append("")
    lines.append(f"Unique states: {summary.unique_state_count}")
    lines.append("")
    lines.append("# 3. Top States")
    lines.append("")
    lines.append("| state_id | count | share |")
    lines.append("|---|---:|---:|")

    for item in summary.state_frequencies[:20]:
        lines.append(
            f"| {item.state_id} | {item.count} | {_format_float(item.share)} |"
        )

    lines.append("")
    lines.append("# 4. Side Summary")
    lines.append("")
    lines.append("| side | count | share | avg_unrealized_pnl |")
    lines.append("|---|---:|---:|---:|")

    for item in summary.side_summary:
        lines.append(
            f"| {item.side} | {item.count} | "
            f"{_format_float(item.share)} | "
            f"{_format_float(item.avg_unrealized_pnl)} |"
        )

    lines.append("")
    lines.append("# 5. Numeric Summary")
    lines.append("")
    lines.append("| column | count | min | max | mean |")
    lines.append("|---|---:|---:|---:|---:|")

    for item in summary.numeric_summary:
        lines.append(
            f"| {item.column} | {item.count} | "
            f"{_format_float(item.min_value)} | "
            f"{_format_float(item.max_value)} | "
            f"{_format_float(item.mean_value)} |"
        )

    lines.append("")
    lines.append("# 6. Scientific Interpretation Boundary")
    lines.append("")
    lines.append("This report is descriptive State Layer analytics only.")
    lines.append("")
    lines.append("It does not perform transition analysis.")
    lines.append("")
    lines.append("It does not perform trajectory reconstruction.")
    lines.append("")
    lines.append("It does not perform forecasting.")
    lines.append("")
    lines.append("It does not create execution decisions.")
    lines.append("")
    lines.append("# 7. Final Status")
    lines.append("")
    lines.append("SSI State Analytics V1A completed successfully.")
    lines.append("")

    return TextArtifact(
        filename="state_analytics_v1a_report.md",
        content="\n".join(lines),
    )


def _render_manifest(result: StateAnalyticsResult) -> JSONArtifact:
    assert result.summary is not None

    metadata = result.metadata
    summary = result.summary

    return JSONArtifact(
        filename="state_analytics_v1a_manifest.json",
        content={
            "artifact_type": "ssi_state_analytics_v1a_manifest",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "runtime_id": metadata.runtime_id,
            "input_path": metadata.input_path,
            "result_version": metadata.result_version,
            "conceptual_layer": metadata.conceptual_layer,
            "processing_layer": metadata.processing_layer,
            "source_dataset_type": metadata.source_dataset_type,
            "validation_status": result.validation_status,
            "row_count": summary.row_count,
            "unique_state_count": summary.unique_state_count,
            "csv_artifacts": [
                "state_frequencies_v1a.csv",
                "dimension_frequencies_v1a.csv",
                "side_summary_v1a.csv",
                "numeric_summary_v1a.csv",
            ],
            "text_artifacts": [
                "state_analytics_v1a_report.md",
            ],
        },
    )
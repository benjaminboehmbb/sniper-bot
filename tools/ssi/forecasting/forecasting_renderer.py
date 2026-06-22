from __future__ import annotations

from datetime import datetime, timezone

from tools.ssi.common.scientific_artifacts import (
    CSVArtifact,
    JSONArtifact,
    ScientificArtifacts,
    TextArtifact,
)
from tools.ssi.common.scientific_renderer import ScientificRenderer
from tools.ssi.forecasting.forecasting_result import ForecastingResult


class ForecastingRenderer(ScientificRenderer[ForecastingResult]):
    def render(
        self,
        result: ForecastingResult,
    ) -> ScientificArtifacts:
        return ScientificArtifacts(
            csv_artifacts=(
                _render_forecast_summary(result),
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


def _render_forecast_summary(result: ForecastingResult) -> CSVArtifact:
    rows = []

    for forecast in result.forecasts:
        rows.append([
            forecast.forecast_id,
            forecast.trajectory_id,
            forecast.runtime_trade_id,
            _format_float(forecast.predicted_next_progress),
            _format_float(forecast.predicted_next_compatibility),
            _format_float(forecast.predicted_next_stability),
            _format_float(forecast.predicted_next_confidence),
            forecast.prediction_horizon,
            forecast.prediction_method,
            _format_float(forecast.forecast_confidence),
            _format_float(forecast.forecast_uncertainty),
            forecast.source_state_id,
            str(forecast.transition_count),
            forecast.runtime_id,
            forecast.forecasting_version,
        ])

    return CSVArtifact(
        filename="forecast_summary_v1.csv",
        header=[
            "forecast_id",
            "trajectory_id",
            "runtime_trade_id",
            "predicted_next_progress",
            "predicted_next_compatibility",
            "predicted_next_stability",
            "predicted_next_confidence",
            "prediction_horizon",
            "prediction_method",
            "forecast_confidence",
            "forecast_uncertainty",
            "source_state_id",
            "transition_count",
            "runtime_id",
            "forecasting_version",
        ],
        rows=rows,
    )


def _render_report(result: ForecastingResult) -> TextArtifact:
    m = result.metrics
    assert m is not None

    lines = [
        "# SSI FORECASTING V1 REPORT",
        "",
        f"Runtime ID: {result.metadata.runtime_id}",
        "",
        "## Summary",
        "",
        f"Trajectory analyses: {m.trajectory_analysis_count}",
        f"Forecasts: {m.forecast_count}",
        f"Mean-delta forecasts: {m.mean_delta_forecast_count}",
        f"Hold-state forecasts: {m.hold_state_forecast_count}",
        "",
        "Validation:",
        result.validation_status,
        "",
        "## Interpretation Boundary",
        "",
        "This report describes deterministic baseline forecasts only.",
        "It does not perform forecast evaluation, model training, optimization or execution decisions.",
    ]

    return TextArtifact(
        filename="forecasting_report.md",
        content="\n".join(lines),
    )


def _render_manifest(result: ForecastingResult) -> JSONArtifact:
    m = result.metrics
    assert m is not None

    return JSONArtifact(
        filename="forecasting_manifest.json",
        content={
            "artifact_type": "forecasting_v1",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "runtime_id": result.metadata.runtime_id,
            "validation_status": result.validation_status,
            "trajectory_analysis_count": m.trajectory_analysis_count,
            "forecast_count": m.forecast_count,
            "mean_delta_forecast_count": m.mean_delta_forecast_count,
            "hold_state_forecast_count": m.hold_state_forecast_count,
        },
    )
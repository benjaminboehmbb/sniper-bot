from __future__ import annotations

from dataclasses import dataclass

from tools.ssi.common.scientific_object import ScientificObject
from tools.ssi.trajectory_analytics.trajectory_analysis_model import TrajectoryAnalysis


@dataclass(frozen=True, slots=True)
class Forecast(ScientificObject):
    forecast_id: str
    trajectory_id: str
    runtime_trade_id: str

    predicted_next_progress: float
    predicted_next_compatibility: float
    predicted_next_stability: float
    predicted_next_confidence: float

    prediction_horizon: str
    prediction_method: str

    forecast_confidence: float
    forecast_uncertainty: float

    source_state_id: str
    transition_count: int

    runtime_id: str
    forecasting_version: str

    def deterministic_id(self) -> str:
        return self.forecast_id


def _clamp_unit_interval(value: float) -> float:
    return min(1.0, max(0.0, value))


def build_forecast_from_trajectory_analysis(
    analysis: TrajectoryAnalysis,
    last_progress: float,
    last_compatibility: float,
    last_stability: float,
    last_confidence: float,
    source_state_id: str,
    forecasting_version: str = "v1",
) -> Forecast:
    if analysis.transition_count <= 0:
        predicted_progress = last_progress
        predicted_compatibility = last_compatibility
        predicted_stability = last_stability
        predicted_confidence = last_confidence
        method = "hold_state_baseline_v1"
        confidence = 0.25
        uncertainty = 0.75
    else:
        predicted_progress = _clamp_unit_interval(
            last_progress + analysis.mean_progress_delta
        )
        predicted_compatibility = _clamp_unit_interval(
            last_compatibility + analysis.mean_compatibility_delta
        )
        predicted_stability = _clamp_unit_interval(
            last_stability + analysis.mean_stability_delta
        )
        predicted_confidence = _clamp_unit_interval(
            last_confidence + analysis.mean_confidence_delta
        )
        method = "mean_delta_extrapolation_v1"
        confidence = 0.50
        uncertainty = 0.50

    return Forecast(
        forecast_id=f"{analysis.trajectory_id}|forecast|{forecasting_version}",
        trajectory_id=analysis.trajectory_id,
        runtime_trade_id=analysis.runtime_trade_id,

        predicted_next_progress=predicted_progress,
        predicted_next_compatibility=predicted_compatibility,
        predicted_next_stability=predicted_stability,
        predicted_next_confidence=predicted_confidence,

        prediction_horizon="next_state",
        prediction_method=method,

        forecast_confidence=confidence,
        forecast_uncertainty=uncertainty,

        source_state_id=source_state_id,
        transition_count=analysis.transition_count,

        runtime_id=analysis.runtime_id,
        forecasting_version=forecasting_version,
    )
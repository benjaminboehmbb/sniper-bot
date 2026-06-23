from __future__ import annotations

from dataclasses import dataclass

from tools.ssi.common.scientific_result import ScientificResult, ScientificResultMetadata
from tools.ssi.forecasting.forecast_model import Forecast


@dataclass(frozen=True, slots=True)
class ForecastingMetrics:
    trajectory_analysis_count: int
    forecast_count: int
    mean_delta_forecast_count: int
    hold_state_forecast_count: int

    def is_complete(self) -> bool:
        return self.trajectory_analysis_count == self.forecast_count


@dataclass(frozen=True, slots=True)
class ForecastingResult(ScientificResult):
    forecasts: tuple[Forecast, ...] = tuple()
    metrics: ForecastingMetrics | None = None

    def __post_init__(self) -> None:
        if self.metrics is None:
            raise ValueError("ForecastingResult requires metrics")

    def forecast_count(self) -> int:
        return len(self.forecasts)

    def is_complete(self) -> bool:
        assert self.metrics is not None
        return self.metrics.is_complete()


def build_forecasting_metadata(
    runtime_id: str,
    input_path: str,
) -> ScientificResultMetadata:
    return ScientificResultMetadata(
        runtime_id=runtime_id,
        input_path=input_path,
        result_version="v1",
        conceptual_layer="Forecasting Layer",
        processing_layer="Forecasting",
        source_dataset_type="TrajectoryAnalyticsResult",
    )
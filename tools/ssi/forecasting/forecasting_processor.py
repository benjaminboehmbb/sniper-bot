from __future__ import annotations

from dataclasses import dataclass

from tools.ssi.common.scientific_object import ScientificObject
from tools.ssi.common.scientific_processor import ScientificProcessor
from tools.ssi.forecasting.forecast import build_forecast_from_trajectory_analysis
from tools.ssi.forecasting.forecasting_result import (
    ForecastingMetrics,
    ForecastingResult,
    build_forecasting_metadata,
)
from tools.ssi.trajectory.trajectory_reconstruction_result import (
    TrajectoryReconstructionResult,
)
from tools.ssi.trajectory_analytics.trajectory_analytics_result import (
    TrajectoryAnalyticsResult,
)


@dataclass(frozen=True, slots=True)
class ForecastingInput(ScientificObject):
    trajectory_result: TrajectoryReconstructionResult
    trajectory_analytics_result: TrajectoryAnalyticsResult
    runtime_id: str
    input_path: str


class ForecastingProcessor(
    ScientificProcessor[ForecastingInput, ForecastingResult]
):
    def validate_input(self, input_object: ForecastingInput) -> None:
        if input_object.runtime_id.strip() == "":
            raise ValueError("runtime_id must not be empty")

        if input_object.input_path.strip() == "":
            raise ValueError("input_path must not be empty")

        if input_object.trajectory_result.metrics is None:
            raise ValueError("trajectory_result requires metrics")

        if input_object.trajectory_analytics_result.metrics is None:
            raise ValueError("trajectory_analytics_result requires metrics")

        if not input_object.trajectory_result.is_complete():
            raise ValueError("trajectory_result is incomplete")

        if not input_object.trajectory_analytics_result.is_complete():
            raise ValueError("trajectory_analytics_result is incomplete")

        if (
            input_object.trajectory_result.metadata.runtime_id
            != input_object.trajectory_analytics_result.metadata.runtime_id
        ):
            raise ValueError(
                "trajectory_result and trajectory_analytics_result runtime_id mismatch"
            )

    def process(
        self,
        input_object: ForecastingInput,
    ) -> ForecastingResult:
        self.validate_input(input_object)

        trajectories_by_id = {
            trajectory.trajectory_id: trajectory
            for trajectory in input_object.trajectory_result.trajectories
        }

        forecasts = []

        for analysis in input_object.trajectory_analytics_result.analyses:
            if analysis.trajectory_id not in trajectories_by_id:
                raise ValueError(
                    f"Missing trajectory for analysis: {analysis.trajectory_id}"
                )

            trajectory = trajectories_by_id[analysis.trajectory_id]
            last_state = trajectory.states[-1]

            forecasts.append(
                build_forecast_from_trajectory_analysis(
                    analysis=analysis,
                    last_progress=float(last_state.state_key.progress),
                    last_compatibility=float(last_state.state_key.compatibility),
                    last_stability=float(last_state.state_key.stability),
                    last_confidence=float(last_state.state_key.confidence),
                    source_state_id=last_state.state_key.deterministic_id(),
                )
            )

        metrics = ForecastingMetrics(
            trajectory_analysis_count=input_object.trajectory_analytics_result.analysis_count(),
            forecast_count=len(forecasts),
            mean_delta_forecast_count=sum(
                1 for forecast in forecasts
                if forecast.prediction_method == "mean_delta_extrapolation_v1"
            ),
            hold_state_forecast_count=sum(
                1 for forecast in forecasts
                if forecast.prediction_method == "hold_state_baseline_v1"
            ),
        )

        validation_status = "PASS" if metrics.is_complete() else "FAIL"

        return ForecastingResult(
            metadata=build_forecasting_metadata(
                runtime_id=input_object.runtime_id,
                input_path=input_object.input_path,
            ),
            validation_status=validation_status,
            forecasts=tuple(forecasts),
            metrics=metrics,
        )
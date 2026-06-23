from __future__ import annotations

from dataclasses import dataclass

from tools.ssi.common.scientific_object import ScientificObject
from tools.ssi.common.scientific_processor import ScientificProcessor
from tools.ssi.forecasting.forecasting_result import ForecastingResult
from tools.ssi.knowledge.scientific_knowledge_candidate import (
    KnowledgeCandidate,
    build_knowledge_candidate,
)
from tools.ssi.knowledge.scientific_knowledge_extraction_result import (
    KnowledgeExtractionMetrics,
    KnowledgeExtractionResult,
    build_knowledge_extraction_metadata,
)
from tools.ssi.knowledge.scientific_knowledge_validator import validate_and_promote_candidates
from tools.ssi.trajectory_analytics.trajectory_analytics_result import (
    TrajectoryAnalyticsResult,
)


@dataclass(frozen=True, slots=True)
class KnowledgeExtractionInput(ScientificObject):
    trajectory_analytics_result: TrajectoryAnalyticsResult
    forecasting_result: ForecastingResult
    runtime_id: str
    input_path: str


class KnowledgeExtractionProcessor(
    ScientificProcessor[KnowledgeExtractionInput, KnowledgeExtractionResult]
):
    def validate_input(self, input_object: KnowledgeExtractionInput) -> None:
        if input_object.runtime_id.strip() == "":
            raise ValueError("runtime_id must not be empty")

        if input_object.input_path.strip() == "":
            raise ValueError("input_path must not be empty")

        if input_object.trajectory_analytics_result.metrics is None:
            raise ValueError("trajectory_analytics_result requires metrics")

        if input_object.forecasting_result.metrics is None:
            raise ValueError("forecasting_result requires metrics")

        if not input_object.trajectory_analytics_result.is_complete():
            raise ValueError("trajectory_analytics_result is incomplete")

        if not input_object.forecasting_result.is_complete():
            raise ValueError("forecasting_result is incomplete")

        if (
            input_object.trajectory_analytics_result.metadata.runtime_id
            != input_object.forecasting_result.metadata.runtime_id
        ):
            raise ValueError(
                "trajectory_analytics_result and forecasting_result runtime_id mismatch"
            )

    def process(
        self,
        input_object: KnowledgeExtractionInput,
    ) -> KnowledgeExtractionResult:
        self.validate_input(input_object)

        candidates = _build_knowledge_candidates(
            trajectory_analytics_result=input_object.trajectory_analytics_result,
            forecasting_result=input_object.forecasting_result,
            runtime_id=input_object.runtime_id,
        )

        knowledge_items = validate_and_promote_candidates(
            candidates=candidates,
            runtime_id=input_object.runtime_id,
        )

        metrics = KnowledgeExtractionMetrics(
            candidate_count=len(candidates),
            knowledge_count=len(knowledge_items),
            validation_pass_count=len(knowledge_items),
            validation_fail_count=0,
        )

        validation_status = "PASS" if metrics.is_complete() else "FAIL"

        return KnowledgeExtractionResult(
            metadata=build_knowledge_extraction_metadata(
                runtime_id=input_object.runtime_id,
                input_path=input_object.input_path,
            ),
            validation_status=validation_status,
            candidates=candidates,
            knowledge_items=knowledge_items,
            metrics=metrics,
        )


def _build_knowledge_candidates(
    trajectory_analytics_result: TrajectoryAnalyticsResult,
    forecasting_result: ForecastingResult,
    runtime_id: str,
) -> tuple[KnowledgeCandidate, ...]:
    trajectory_metrics = trajectory_analytics_result.metrics
    forecasting_metrics = forecasting_result.metrics

    assert trajectory_metrics is not None
    assert forecasting_metrics is not None

    candidates: list[KnowledgeCandidate] = []

    total_trajectories = trajectory_metrics.trajectory_count
    total_forecasts = forecasting_metrics.forecast_count

    candidates.append(
        build_knowledge_candidate(
            candidate_type="RepeatedStateBehaviour",
            description=(
                f"{trajectory_metrics.trajectories_with_repeated_states} of "
                f"{total_trajectories} trajectories contained repeated states."
            ),
            support_count=trajectory_metrics.trajectories_with_repeated_states,
            support_ratio=_safe_ratio(
                trajectory_metrics.trajectories_with_repeated_states,
                total_trajectories,
            ),
            confidence=1.0,
            scientific_score=_safe_ratio(
                trajectory_metrics.trajectories_with_repeated_states,
                total_trajectories,
            ),
            runtime_id=runtime_id,
            evidence_source="TrajectoryAnalyticsResult",
        )
    )

    candidates.append(
        build_knowledge_candidate(
            candidate_type="NonRepeatedStateBehaviour",
            description=(
                f"{trajectory_metrics.trajectories_without_repeated_states} of "
                f"{total_trajectories} trajectories contained no repeated states."
            ),
            support_count=trajectory_metrics.trajectories_without_repeated_states,
            support_ratio=_safe_ratio(
                trajectory_metrics.trajectories_without_repeated_states,
                total_trajectories,
            ),
            confidence=1.0,
            scientific_score=_safe_ratio(
                trajectory_metrics.trajectories_without_repeated_states,
                total_trajectories,
            ),
            runtime_id=runtime_id,
            evidence_source="TrajectoryAnalyticsResult",
        )
    )

    candidates.append(
        build_knowledge_candidate(
            candidate_type="MeanDeltaForecastDominance",
            description=(
                f"{forecasting_metrics.mean_delta_forecast_count} of "
                f"{total_forecasts} forecasts used mean-delta extrapolation."
            ),
            support_count=forecasting_metrics.mean_delta_forecast_count,
            support_ratio=_safe_ratio(
                forecasting_metrics.mean_delta_forecast_count,
                total_forecasts,
            ),
            confidence=1.0,
            scientific_score=_safe_ratio(
                forecasting_metrics.mean_delta_forecast_count,
                total_forecasts,
            ),
            runtime_id=runtime_id,
            evidence_source="ForecastingResult",
        )
    )

    candidates.append(
        build_knowledge_candidate(
            candidate_type="HoldStateForecastEdgeCase",
            description=(
                f"{forecasting_metrics.hold_state_forecast_count} of "
                f"{total_forecasts} forecasts used hold-state baseline."
            ),
            support_count=forecasting_metrics.hold_state_forecast_count,
            support_ratio=_safe_ratio(
                forecasting_metrics.hold_state_forecast_count,
                total_forecasts,
            ),
            confidence=1.0,
            scientific_score=_safe_ratio(
                forecasting_metrics.hold_state_forecast_count,
                total_forecasts,
            ),
            runtime_id=runtime_id,
            evidence_source="ForecastingResult",
        )
    )

    return tuple(candidates)


def _safe_ratio(
    numerator: int,
    denominator: int,
) -> float:
    if denominator <= 0:
        return 0.0

    return numerator / denominator
from __future__ import annotations

import argparse
from pathlib import Path

from tools.ssi.decision_engine.decision_engine_persistence import (
    DecisionEnginePersistence,
)
from tools.ssi.decision_engine.decision_engine_processor import (
    DecisionEngineProcessor,
)
from tools.ssi.decision_engine.decision_engine_renderer import (
    DecisionEngineRenderer,
)
from tools.ssi.forecasting.forecasting_processor import (
    ForecastingInput,
    ForecastingProcessor,
)
from tools.ssi.knowledge.scientific_knowledge_extraction_processor import (
    KnowledgeExtractionInput,
    KnowledgeExtractionProcessor,
)
from tools.ssi.trajectory.trajectory_reconstruction_processor import (
    TrajectoryReconstructionInput,
    TrajectoryReconstructionProcessor,
)
from tools.ssi.trajectory_analytics.trajectory_analytics_processor import (
    TrajectoryAnalyticsInput,
    TrajectoryAnalyticsProcessor,
)
from tools.ssi.transition.transition_analytics_processor import (
    TransitionAnalyticsInput,
    TransitionAnalyticsProcessor,
)
from tools.ssi.decision_evidence.decision_evidence_processor import (
    DecisionEvidenceProcessor,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run SSI Decision Engine V1."
    )

    parser.add_argument(
        "--tsv-input",
        required=True,
    )

    parser.add_argument(
        "--trades-input",
        required=True,
    )

    parser.add_argument(
        "--runtime-id",
        required=True,
    )

    parser.add_argument(
        "--output-dir",
        required=True,
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    trajectory_result = TrajectoryReconstructionProcessor().process(
        TrajectoryReconstructionInput(
            tsv_input_path=Path(args.tsv_input),
            trades_input_path=Path(args.trades_input),
            runtime_id=args.runtime_id,
        )
    )

    transition_result = TransitionAnalyticsProcessor().process(
        TransitionAnalyticsInput(
            trajectory_result=trajectory_result,
            runtime_id=args.runtime_id,
            input_path="trajectory_reconstruction_result",
        )
    )

    trajectory_analytics_result = TrajectoryAnalyticsProcessor().process(
        TrajectoryAnalyticsInput(
            trajectory_result=trajectory_result,
            transition_result=transition_result,
            runtime_id=args.runtime_id,
            input_path="trajectory_reconstruction_result+transition_analytics_result",
        )
    )

    forecasting_result = ForecastingProcessor().process(
        ForecastingInput(
            trajectory_result=trajectory_result,
            trajectory_analytics_result=trajectory_analytics_result,
            runtime_id=args.runtime_id,
            input_path="trajectory_reconstruction_result+trajectory_analytics_result",
        )
    )

    knowledge_result = KnowledgeExtractionProcessor().process(
        KnowledgeExtractionInput(
            trajectory_analytics_result=trajectory_analytics_result,
            forecasting_result=forecasting_result,
            runtime_id=args.runtime_id,
            input_path="trajectory_analytics_result+forecasting_result",
        )
    )

    decision_evidence_result = DecisionEvidenceProcessor().process(
        knowledge_result
    )

    decision_result = DecisionEngineProcessor().process(
        decision_evidence_result
    )

    artifacts = DecisionEngineRenderer().render(
        decision_result
    )

    DecisionEnginePersistence().persist(
        artifacts=artifacts,
        output_dir=Path(args.output_dir),
    )

    print("SSI_DECISION_ENGINE_V1_PASS")
    print(f"runtime_id={args.runtime_id}")
    print(f"validation_status={decision_result.validation_summary['status']}")
    print(f"decision_count={len(decision_result.decisions)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
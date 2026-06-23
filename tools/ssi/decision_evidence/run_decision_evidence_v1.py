from __future__ import annotations

import argparse
from pathlib import Path

from tools.ssi.decision_evidence.decision_evidence_persistence import DecisionEvidencePersistence
from tools.ssi.decision_evidence.decision_evidence_processor import DecisionEvidenceProcessor
from tools.ssi.decision_evidence.decision_evidence_renderer import DecisionEvidenceRenderer
from tools.ssi.forecasting.forecast_modeling_processor import (
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run SSI Decision Evidence V1."
    )

    parser.add_argument("--tsv-input", required=True)
    parser.add_argument("--trades-input", required=True)
    parser.add_argument("--runtime-id", required=True)
    parser.add_argument("--output-dir", required=True)

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

    artifacts = DecisionEvidenceRenderer().render(
        decision_evidence_result
    )

    DecisionEvidencePersistence().persist(
        artifacts=artifacts,
        output_dir=Path(args.output_dir),
    )

    print("SSI_DECISION_EVIDENCE_V1_PASS")
    print(f"runtime_id={args.runtime_id}")
    print(f"tsv_input={args.tsv_input}")
    print(f"trades_input={args.trades_input}")
    print(f"output_dir={args.output_dir}")
    print(f"validation_status={decision_evidence_result.validation_summary['status']}")
    print(f"evidence_items={len(decision_evidence_result.evidence)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
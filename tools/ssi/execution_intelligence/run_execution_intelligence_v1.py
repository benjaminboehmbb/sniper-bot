from __future__ import annotations

import argparse
from pathlib import Path

from tools.ssi.decision_engine.decision_engine_processor import (
    DecisionEngineProcessor,
)
from tools.ssi.decision_evidence.decision_evidence_processor import (
    DecisionEvidenceProcessor,
)
from tools.ssi.execution_intelligence.execution_intelligence_persistence import (
    ExecutionIntelligencePersistence,
)
from tools.ssi.execution_intelligence.execution_intelligence_processor import (
    ExecutionIntelligenceProcessor,
)
from tools.ssi.execution_intelligence.execution_intelligence_renderer import (
    ExecutionIntelligenceRenderer,
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run SSI Execution Intelligence V1."
    )

    parser.add_argument(
        "--tsv-input",
        required=True,
        help="Path to SSI TSV dataset CSV.",
    )

    parser.add_argument(
        "--trades-input",
        required=True,
        help="Path to trades JSONL.",
    )

    parser.add_argument(
        "--runtime-id",
        required=True,
        help="Runtime identifier.",
    )

    parser.add_argument(
        "--output-dir",
        required=True,
        help="Output directory.",
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
            input_path=(
                "trajectory_reconstruction_result+"
                "transition_analytics_result"
            ),
        )
    )

    forecasting_result = ForecastingProcessor().process(
        ForecastingInput(
            trajectory_result=trajectory_result,
            trajectory_analytics_result=trajectory_analytics_result,
            runtime_id=args.runtime_id,
            input_path=(
                "trajectory_reconstruction_result+"
                "trajectory_analytics_result"
            ),
        )
    )

    knowledge_result = KnowledgeExtractionProcessor().process(
        KnowledgeExtractionInput(
            trajectory_analytics_result=trajectory_analytics_result,
            forecasting_result=forecasting_result,
            runtime_id=args.runtime_id,
            input_path=(
                "trajectory_analytics_result+"
                "forecasting_result"
            ),
        )
    )

    decision_evidence_result = DecisionEvidenceProcessor().process(
        knowledge_result
    )

    decision_result = DecisionEngineProcessor().process(
        decision_evidence_result
    )

    execution_result = ExecutionIntelligenceProcessor().process(
        decision_result
    )

    artifacts = ExecutionIntelligenceRenderer().render(
        execution_result
    )

    written_paths = ExecutionIntelligencePersistence().persist(
        artifacts=artifacts,
        output_dir=Path(args.output_dir),
    )

    print("SSI_EXECUTION_INTELLIGENCE_V1_PASS")
    print(f"runtime_id={args.runtime_id}")
    print(f"validation_status={execution_result.validation_summary['status']}")
    print(f"execution_intents={len(execution_result.execution_intents)}")
    print(f"artifacts={len(written_paths)}")

    for path in written_paths:
        print(f"artifact={path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
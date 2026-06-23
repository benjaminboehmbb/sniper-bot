from __future__ import annotations

import argparse
from pathlib import Path

from tools.ssi.forecasting.forecasting_processor import (
    ForecastingInput,
    ForecastingProcessor,
)
from tools.ssi.knowledge.scientific_knowledge_extraction_artifact_persistence import (
    KnowledgeExtractionArtifactPersistence,
)
from tools.ssi.knowledge.scientific_knowledge_extraction_processor import (
    KnowledgeExtractionInput,
    KnowledgeExtractionProcessor,
)
from tools.ssi.knowledge.scientific_knowledge_extraction_renderer import (
    KnowledgeExtractionRenderer,
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
        description="Run SSI Knowledge Extraction V1."
    )

    parser.add_argument(
        "--tsv-input",
        required=True,
        help="Path to SSI TSV dataset CSV.",
    )

    parser.add_argument(
        "--trades-input",
        required=True,
        help="Path to trades_l1 JSONL.",
    )

    parser.add_argument(
        "--runtime-id",
        required=True,
        help="Runtime identifier.",
    )

    parser.add_argument(
        "--output-dir",
        required=True,
        help="Output directory for knowledge extraction artifacts.",
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

    artifacts = KnowledgeExtractionRenderer().render(knowledge_result)

    written_paths = KnowledgeExtractionArtifactPersistence().persist(
        artifacts=artifacts,
        output_dir=Path(args.output_dir),
    )

    assert knowledge_result.metrics is not None

    print("SSI_KNOWLEDGE_EXTRACTION_V1_PASS")
    print(f"runtime_id={args.runtime_id}")
    print(f"tsv_input={args.tsv_input}")
    print(f"trades_input={args.trades_input}")
    print(f"output_dir={args.output_dir}")
    print(f"validation_status={knowledge_result.validation_status}")
    print(f"candidates={knowledge_result.candidate_count()}")
    print(f"knowledge_items={knowledge_result.knowledge_count()}")
    print(f"validation_pass_count={knowledge_result.metrics.validation_pass_count}")
    print(f"validation_fail_count={knowledge_result.metrics.validation_fail_count}")
    print(f"artifacts={len(written_paths)}")

    for path in written_paths:
        print(f"artifact={path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
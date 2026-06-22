from __future__ import annotations

import argparse
from pathlib import Path

from tools.ssi.trajectory.trajectory_reconstruction_processor import (
    TrajectoryReconstructionInput,
    TrajectoryReconstructionProcessor,
)
from tools.ssi.transition.transition_analytics_artifact_persistence import (
    TransitionAnalyticsArtifactPersistence,
)
from tools.ssi.transition.transition_analytics_processor import (
    TransitionAnalyticsInput,
    TransitionAnalyticsProcessor,
)
from tools.ssi.transition.transition_analytics_renderer import TransitionAnalyticsRenderer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run SSI Transition Analytics V1."
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
        help="Output directory for transition analytics artifacts.",
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

    artifacts = TransitionAnalyticsRenderer().render(transition_result)

    written_paths = TransitionAnalyticsArtifactPersistence().persist(
        artifacts=artifacts,
        output_dir=Path(args.output_dir),
    )

    assert transition_result.metrics is not None

    print("SSI_TRANSITION_ANALYTICS_V1_PASS")
    print(f"runtime_id={args.runtime_id}")
    print(f"tsv_input={args.tsv_input}")
    print(f"trades_input={args.trades_input}")
    print(f"output_dir={args.output_dir}")
    print(f"validation_status={transition_result.validation_status}")
    print(f"trajectories={transition_result.metrics.trajectory_count}")
    print(f"trajectories_with_transitions={transition_result.metrics.trajectories_with_transitions}")
    print(f"trajectories_without_transitions={transition_result.metrics.trajectories_without_transitions}")
    print(f"expected_transitions={transition_result.metrics.expected_transition_count}")
    print(f"generated_transitions={transition_result.metrics.transition_count}")
    print(f"artifacts={len(written_paths)}")

    for path in written_paths:
        print(f"artifact={path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
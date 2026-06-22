from __future__ import annotations

import argparse
from pathlib import Path

from tools.ssi.trajectory.trajectory_reconstruction_processor import (
    TrajectoryReconstructionInput,
    TrajectoryReconstructionProcessor,
)
from tools.ssi.transition.transition_analytics_processor import (
    TransitionAnalyticsInput,
    TransitionAnalyticsProcessor,
)
from tools.ssi.trajectory_analytics.trajectory_analytics_artifact_persistence import (
    TrajectoryAnalyticsArtifactPersistence,
)
from tools.ssi.trajectory_analytics.trajectory_analytics_processor import (
    TrajectoryAnalyticsInput,
    TrajectoryAnalyticsProcessor,
)
from tools.ssi.trajectory_analytics.trajectory_analytics_renderer import (
    TrajectoryAnalyticsRenderer,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run SSI Trajectory Analytics V1."
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
        help="Output directory for trajectory analytics artifacts.",
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

    artifacts = TrajectoryAnalyticsRenderer().render(trajectory_analytics_result)

    written_paths = TrajectoryAnalyticsArtifactPersistence().persist(
        artifacts=artifacts,
        output_dir=Path(args.output_dir),
    )

    assert trajectory_analytics_result.metrics is not None

    print("SSI_TRAJECTORY_ANALYTICS_V1_PASS")
    print(f"runtime_id={args.runtime_id}")
    print(f"tsv_input={args.tsv_input}")
    print(f"trades_input={args.trades_input}")
    print(f"output_dir={args.output_dir}")
    print(f"validation_status={trajectory_analytics_result.validation_status}")
    print(f"analyses={trajectory_analytics_result.analysis_count()}")
    print(f"total_states={trajectory_analytics_result.metrics.total_state_count}")
    print(f"total_transitions={trajectory_analytics_result.metrics.total_transition_count}")
    print(
        "trajectories_with_repeated_states="
        f"{trajectory_analytics_result.metrics.trajectories_with_repeated_states}"
    )
    print(
        "trajectories_without_repeated_states="
        f"{trajectory_analytics_result.metrics.trajectories_without_repeated_states}"
    )
    print(f"artifacts={len(written_paths)}")

    for path in written_paths:
        print(f"artifact={path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
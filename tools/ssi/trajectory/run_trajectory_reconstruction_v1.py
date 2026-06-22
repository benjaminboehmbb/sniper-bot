from __future__ import annotations

import argparse
from pathlib import Path

from tools.ssi.trajectory.trajectory_reconstruction_artifact_persistence import (
    TrajectoryReconstructionArtifactPersistence,
)
from tools.ssi.trajectory.trajectory_reconstruction_processor import (
    TrajectoryReconstructionInput,
    TrajectoryReconstructionProcessor,
)
from tools.ssi.trajectory.trajectory_reconstruction_renderer import (
    TrajectoryReconstructionRenderer,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run SSI Trajectory Reconstruction V1."
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
        help="Output directory for trajectory reconstruction artifacts.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    processor = TrajectoryReconstructionProcessor()
    renderer = TrajectoryReconstructionRenderer()
    persistence = TrajectoryReconstructionArtifactPersistence()

    result = processor.process(
        TrajectoryReconstructionInput(
            tsv_input_path=Path(args.tsv_input),
            trades_input_path=Path(args.trades_input),
            runtime_id=args.runtime_id,
        )
    )

    artifacts = renderer.render(result)

    written_paths = persistence.persist(
        artifacts=artifacts,
        output_dir=Path(args.output_dir),
    )

    assert result.metrics is not None

    print("SSI_TRAJECTORY_RECONSTRUCTION_V1_PASS")
    print(f"runtime_id={args.runtime_id}")
    print(f"tsv_input={args.tsv_input}")
    print(f"trades_input={args.trades_input}")
    print(f"output_dir={args.output_dir}")
    print(f"validation_status={result.validation_status}")
    print(f"trajectories={result.trajectory_count()}")
    print(f"runtime_trades={result.metrics.runtime_trade_count}")
    print(f"tsv_states={result.metrics.tsv_state_count}")
    print(f"assigned_states={result.metrics.assigned_state_count}")
    print(f"unassigned_states={result.metrics.unassigned_state_count}")
    print(f"side_mismatches={result.metrics.side_mismatch_count}")
    print(f"artifacts={len(written_paths)}")

    for path in written_paths:
        print(f"artifact={path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
from __future__ import annotations

import argparse
from pathlib import Path

from tools.ssi.analytics.state_analytics_artifact_persistence import (
    StateAnalyticsArtifactPersistence,
)
from tools.ssi.analytics.state_analytics_processor import (
    StateAnalyticsInput,
    StateAnalyticsProcessor,
)
from tools.ssi.analytics.state_analytics_renderer import StateAnalyticsRenderer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run SSI State Analytics V1A."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to SSI TSV dataset CSV.",
    )

    parser.add_argument(
        "--runtime-id",
        required=True,
        help="Runtime identifier.",
    )

    parser.add_argument(
        "--output-dir",
        required=True,
        help="Output directory for State Analytics artifacts.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)

    processor = StateAnalyticsProcessor()
    renderer = StateAnalyticsRenderer()
    persistence = StateAnalyticsArtifactPersistence()

    result = processor.process(
        StateAnalyticsInput(
            input_path=input_path,
            runtime_id=args.runtime_id,
        )
    )

    artifacts = renderer.render(result)

    written_paths = persistence.persist(
        artifacts=artifacts,
        output_dir=output_dir,
    )

    print("SSI_STATE_ANALYTICS_V1A_PASS")
    print(f"input={input_path}")
    print(f"runtime_id={args.runtime_id}")
    print(f"output_dir={output_dir}")
    print(f"rows={result.row_count()}")
    print(f"unique_states={result.unique_state_count()}")
    print(f"artifacts={len(written_paths)}")

    for path in written_paths:
        print(f"artifact={path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
from __future__ import annotations

import argparse
from pathlib import Path

from tools.ssi.builder.lifecycle_loader import load_lifecycle_snapshots
from tools.ssi.builder.tsv_dataset_builder import build_tsv_dataset
from tools.ssi.builder.tsv_writer import write_tsv_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build SSI TSV dataset from lifecycle snapshots."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to trade_lifecycle_snapshots.csv",
    )

    parser.add_argument(
        "--runtime-id",
        required=True,
        help="Runtime identifier, e.g. paper_4300000_2026-06-22",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output path for tsv_dataset_v1.csv",
    )

    parser.add_argument(
        "--created-at-utc",
        default=None,
        help="Optional fixed creation timestamp for deterministic tests.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    snapshots = load_lifecycle_snapshots(
        input_path=input_path,
        runtime_id=args.runtime_id,
    )

    tsv_records = build_tsv_dataset(
        snapshots,
        created_at_utc=args.created_at_utc,
    )

    write_tsv_csv(
        records=tsv_records,
        output_path=output_path,
    )

    print("TSV_DATASET_BUILD_PASS")
    print(f"input={input_path}")
    print(f"output={output_path}")
    print(f"snapshots={len(snapshots)}")
    print(f"tsv_records={len(tsv_records)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

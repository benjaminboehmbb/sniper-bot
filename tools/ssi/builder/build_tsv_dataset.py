from __future__ import annotations

import argparse
from pathlib import Path

from tools.ssi.builder.lifecycle_loader import load_lifecycle_snapshots
from tools.ssi.builder.summary import write_tsv_summary
from tools.ssi.builder.tsv_dataset_builder import build_tsv_dataset
from tools.ssi.builder.manifest import build_tsv_manifest, write_manifest
from tools.ssi.builder.tsv_writer import write_tsv_csv
from tools.ssi.builder.validation import (
    assert_valid_manifest,
    assert_valid_output_paths,
    assert_valid_tsv_records,
)


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
        "--manifest-output",
        required=False,
        default=None,
        help="Optional output path for tsv_dataset_v1_manifest.json",
    )

    parser.add_argument(
        "--summary-output",
        required=False,
        default=None,
        help="Optional output path for tsv_dataset_v1_summary.md",
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

    manifest_output = (
        Path(args.manifest_output)
        if args.manifest_output is not None
        else output_path.with_name(output_path.stem + "_manifest.json")
    )

    summary_output = (
        Path(args.summary_output)
        if args.summary_output is not None
        else output_path.with_name(output_path.stem + "_summary.md")
    )

    assert_valid_output_paths(output_path, manifest_output)
    assert_valid_output_paths(output_path, summary_output)
    assert_valid_output_paths(manifest_output, summary_output)

    snapshots = load_lifecycle_snapshots(
        input_path=input_path,
        runtime_id=args.runtime_id,
    )

    tsv_records = build_tsv_dataset(
        snapshots,
        created_at_utc=args.created_at_utc,
    )

    assert_valid_tsv_records(tsv_records)

    write_tsv_csv(
        records=tsv_records,
        output_path=output_path,
    )

    manifest = build_tsv_manifest(
        runtime_id=args.runtime_id,
        input_path=input_path,
        output_path=output_path,
        records=tsv_records,
        validation_status="PASS",
    )

    assert_valid_manifest(manifest)

    write_manifest(
        manifest=manifest,
        output_path=manifest_output,
    )

    write_tsv_summary(
        records=tsv_records,
        runtime_id=args.runtime_id,
        csv_output_path=output_path,
        manifest_output_path=manifest_output,
        summary_output_path=summary_output,
    )

    print("TSV_DATASET_BUILD_PASS")
    print(f"input={input_path}")
    print(f"output={output_path}")
    print(f"snapshots={len(snapshots)}")
    print(f"tsv_records={len(tsv_records)}")
    print(f"manifest={manifest_output}")
    print(f"summary={summary_output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

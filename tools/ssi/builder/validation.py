from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Sequence

from tools.ssi.builder.trade_state_vector import TradeStateVector


REQUIRED_TSV_COLUMNS = [
    "tsv_id",
    "tsv_version",
    "runtime_id",
    "trade_id",
    "snapshot_id",
    "timestamp_utc",
    "tick",
    "side",
    "progress",
    "compatibility",
    "stability",
    "confidence",
    "source_file",
    "source_row_index",
    "created_at_utc",
    "generator_name",
    "generator_version",
]


def validate_tsv_records(records: Sequence[TradeStateVector]) -> List[str]:
    errors: List[str] = []

    if not records:
        errors.append("records must not be empty")
        return errors

    seen_ids = set()
    versions = set()
    runtime_ids = set()

    for index, record in enumerate(records):
        record_errors = record.validate()
        for error in record_errors:
            errors.append(f"record[{index}]: {error}")

        if record.tsv_id in seen_ids:
            errors.append(f"duplicate tsv_id: {record.tsv_id}")
        seen_ids.add(record.tsv_id)

        versions.add(record.tsv_version)
        runtime_ids.add(record.runtime_id)

    if len(versions) != 1:
        errors.append(f"multiple TSV versions in dataset: {sorted(versions)}")

    if len(runtime_ids) != 1:
        errors.append(f"multiple runtime_ids in dataset: {sorted(runtime_ids)}")

    return errors


def assert_valid_tsv_records(records: Sequence[TradeStateVector]) -> None:
    errors = validate_tsv_records(records)
    if errors:
        joined = "\n".join(f"- {error}" for error in errors)
        raise ValueError(f"TSV dataset validation failed:\n{joined}")


def validate_manifest(manifest: Dict[str, object]) -> List[str]:
    errors: List[str] = []

    required_keys = [
        "runtime_id",
        "source_files",
        "output_files",
        "row_counts",
        "snapshot_count",
        "tsv_count",
        "trade_count",
        "tsv_versions",
        "generator_names",
        "generator_versions",
        "validation_status",
        "validation_errors",
        "validation_warnings",
        "input_hashes",
        "output_hashes",
    ]

    for key in required_keys:
        if key not in manifest:
            errors.append(f"manifest missing required key: {key}")

    if manifest.get("validation_status") not in {"PASS", "FAIL", "WARN"}:
        errors.append(
            f"manifest has invalid validation_status: {manifest.get('validation_status')}"
        )

    tsv_count = manifest.get("tsv_count")
    snapshot_count = manifest.get("snapshot_count")

    if isinstance(tsv_count, int) and tsv_count <= 0:
        errors.append("manifest tsv_count must be > 0")

    if isinstance(snapshot_count, int) and snapshot_count <= 0:
        errors.append("manifest snapshot_count must be > 0")

    return errors


def assert_valid_manifest(manifest: Dict[str, object]) -> None:
    errors = validate_manifest(manifest)
    if errors:
        joined = "\n".join(f"- {error}" for error in errors)
        raise ValueError(f"TSV manifest validation failed:\n{joined}")


def validate_output_paths(output_path: Path, manifest_path: Path) -> List[str]:
    errors: List[str] = []

    if output_path.exists() and not output_path.is_file():
        errors.append(f"output path exists but is not a file: {output_path}")

    if manifest_path.exists() and not manifest_path.is_file():
        errors.append(f"manifest path exists but is not a file: {manifest_path}")

    if output_path.resolve() == manifest_path.resolve():
        errors.append("output path and manifest path must be different")

    return errors


def assert_valid_output_paths(output_path: Path, manifest_path: Path) -> None:
    errors = validate_output_paths(output_path, manifest_path)
    if errors:
        joined = "\n".join(f"- {error}" for error in errors)
        raise ValueError(f"Output path validation failed:\n{joined}")

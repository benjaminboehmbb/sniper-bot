from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

from tools.ssi.builder.trade_state_vector import TradeStateVector


def file_sha256(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"file not found: {path}")

    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def build_tsv_manifest(
    *,
    runtime_id: str,
    input_path: Path,
    output_path: Path,
    records: List[TradeStateVector],
    validation_status: str,
    validation_errors: List[str] | None = None,
    validation_warnings: List[str] | None = None,
) -> Dict[str, Any]:
    if not records:
        raise ValueError("records must not be empty")

    tsv_versions = sorted({record.tsv_version for record in records})
    generator_names = sorted({record.generator_name for record in records})
    generator_versions = sorted({record.generator_version for record in records})
    trade_ids = sorted({record.trade_id for record in records if record.trade_id})

    manifest: Dict[str, Any] = {
        "runtime_id": runtime_id,
        "source_files": [str(input_path)],
        "output_files": [str(output_path)],
        "row_counts": {
            "tsv_count": len(records),
            "trade_count": len(trade_ids),
        },
        "snapshot_count": len(records),
        "tsv_count": len(records),
        "trade_count": len(trade_ids),
        "tsv_versions": tsv_versions,
        "generator_names": generator_names,
        "generator_versions": generator_versions,
        "validation_status": validation_status,
        "validation_errors": validation_errors or [],
        "validation_warnings": validation_warnings or [],
        "input_hashes": {
            str(input_path): file_sha256(input_path),
        },
        "output_hashes": {
            str(output_path): file_sha256(output_path),
        },
    }

    return manifest


def write_manifest(
    *,
    manifest: Dict[str, Any],
    output_path: Path,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output_path

"""Fail-closed Trade Inspector archive-intake validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

if __package__:
    from .inspection_primitives import safe_int, safe_text
else:
    from inspection_primitives import safe_int, safe_text


__all__ = ["count_valid_jsonl", "run_archive_intake_validation"]


def count_valid_jsonl(path: Path) -> tuple[int, int]:
    count = 0
    bad = 0

    if not path.exists():
        return 0, 0

    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                json.loads(line)
                count += 1
            except json.JSONDecodeError:
                bad += 1

    return count, bad


def run_archive_intake_validation(args: Any) -> int:
    archive_dir = Path(args.archive_dir)

    print("TRADE INSPECTOR V7I ARCHIVE INTAKE VALIDATION")
    print("archive_dir:", archive_dir)
    print("")

    errors: list[str] = []
    warnings: list[str] = []

    required_files = [
        "trades_l1.jsonl",
        "execution_audit.jsonl",
        "l1_paper.log",
        "archive_metadata.json",
    ]

    optional_files = [
        "trade_lifecycle_snapshots.csv",
        "monitor_status.json",
        "runtime_control.json",
        "loss_cluster_state.json",
        "trades_l1_auto_analysis.csv",
    ]

    if not archive_dir.exists():
        errors.append(f"archive directory missing: {archive_dir}")

    if not archive_dir.is_dir():
        errors.append(f"archive path is not a directory: {archive_dir}")

    for name in required_files:
        p = archive_dir / name
        if not p.exists():
            errors.append(f"required file missing: {name}")

    for name in optional_files:
        p = archive_dir / name
        if not p.exists():
            warnings.append(f"optional file missing: {name}")

    metadata: dict[str, Any] = {}
    metadata_path = archive_dir / "archive_metadata.json"

    if metadata_path.exists():
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"archive_metadata.json invalid JSON: {exc}")

    required_metadata_fields = [
        "archive_id",
        "archive_path",
        "created_at",
        "source_device",
        "run_type",
        "strategy_profile",
        "market_symbol",
        "market_csv",
        "seeds_5m_csv",
        "max_ticks",
        "tick_offset",
        "decision_tick_seconds",
        "start_time_utc",
        "end_time_utc",
        "trade_count",
        "audit_event_count",
        "status",
        "notes",
    ]

    if metadata:
        for field in required_metadata_fields:
            if field not in metadata:
                errors.append(f"metadata field missing: {field}")

    archive_id = safe_text(metadata.get("archive_id")) if metadata else ""
    metadata_archive_path = safe_text(metadata.get("archive_path")) if metadata else ""

    if metadata and metadata_archive_path and metadata_archive_path != str(archive_dir):
        warnings.append(
            f"metadata archive_path differs from input path: metadata={metadata_archive_path} input={archive_dir}"
        )

    trades_path = archive_dir / "trades_l1.jsonl"
    audit_path = archive_dir / "execution_audit.jsonl"

    trade_count, trade_bad = count_valid_jsonl(trades_path)
    audit_count, audit_bad = count_valid_jsonl(audit_path)

    print("CHECK required_files:", "PASS" if not any("required file missing" in e for e in errors) else "FAIL")
    print("CHECK archive_metadata_json:", "PASS" if metadata else "FAIL")
    print("CHECK archive_id:", archive_id if archive_id else "MISSING")
    print("CHECK trades_valid_jsonl:", trade_count)
    print("CHECK trades_bad_jsonl:", trade_bad)
    print("CHECK audit_valid_jsonl:", audit_count)
    print("CHECK audit_bad_jsonl:", audit_bad)

    if trade_bad > 0:
        errors.append(f"trades_l1.jsonl bad JSON lines: {trade_bad}")

    if audit_bad > 0:
        errors.append(f"execution_audit.jsonl bad JSON lines: {audit_bad}")

    if metadata:
        meta_trade_count = safe_int(metadata.get("trade_count"), -1)
        meta_audit_count = safe_int(metadata.get("audit_event_count"), -1)

        if meta_trade_count >= 0 and meta_trade_count != trade_count:
            errors.append(f"metadata trade_count mismatch: metadata={meta_trade_count} actual={trade_count}")

        if meta_audit_count >= 0 and meta_audit_count != audit_count:
            errors.append(f"metadata audit_event_count mismatch: metadata={meta_audit_count} actual={audit_count}")

        status = safe_text(metadata.get("status"))
        if status not in {"created", "validated", "rejected", "archived", "superseded"}:
            errors.append(f"metadata status invalid: {status}")

    print("CHECK warnings:", len(warnings))
    for warning in warnings:
        print("WARNING:", warning)

    if errors:
        print("")
        print("ARCHIVE_INTAKE: FAIL")
        for error in errors:
            print("ERROR:", error)
        return 1

    print("")
    print("ARCHIVE_INTAKE: PASS")
    return 0

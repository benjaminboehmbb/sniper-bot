#!/usr/bin/env python3
# live_l1/tools/create_runtime_backup.py
# P17C Live L1 runtime backup tool.
# ASCII-only. Read-only for source files.

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


TIER1_FILES = [
    "live_logs/execution_audit.jsonl",
    "live_logs/trades_l1.jsonl",
    "live_state/s2_position.jsonl",
    "live_state/loss_cluster_state.json",
    "live_state/s4_risk.jsonl",
]

TIER2_FILES = [
    "live_logs/l1_paper.log",
    "live_logs/trade_lifecycle_snapshots.csv",
    "live_logs/passive_shadow_close_accounting.csv",
    "live_logs/passive_shadow_entry_multipliers.csv",
    "live_logs/passive_shadow_risk_snapshots.csv",
    "live_logs/trades_l1_auto_analysis.csv",
]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _safe_label(value: str) -> str:
    s = str(value).strip()
    if s == "":
        return "runtime_backup"
    out = []
    for ch in s:
        if ch.isalnum() or ch in ("-", "_"):
            out.append(ch)
        else:
            out.append("_")
    return "".join(out)


def create_backup(*, repo_root: Path, label: str, include_tier2: bool) -> tuple[int, Path]:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    safe_label = _safe_label(label)
    backup_dir = repo_root / "backups" / "live_l1" / f"{timestamp}_{safe_label}"
    backup_dir.mkdir(parents=True, exist_ok=False)

    files = list(TIER1_FILES)
    if include_tier2:
        files.extend(TIER2_FILES)

    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "label": safe_label,
        "include_tier2": int(include_tier2),
        "backup_dir": str(backup_dir),
        "files": [],
        "missing_files": [],
    }

    for rel in files:
        src = repo_root / rel
        if not src.exists():
            manifest["missing_files"].append(rel)
            continue

        dst = backup_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

        manifest["files"].append(
            {
                "source": rel,
                "backup_path": str(dst.relative_to(backup_dir)),
                "size_bytes": int(dst.stat().st_size),
                "sha256": _sha256(dst),
            }
        )

    manifest_path = backup_dir / "backup_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    required_missing = [x for x in manifest["missing_files"] if x in TIER1_FILES]

    print("P17C RUNTIME BACKUP")
    print("backup_dir:", backup_dir)
    print("files_copied:", len(manifest["files"]))
    print("missing_files:", len(manifest["missing_files"]))
    for item in manifest["missing_files"]:
        print("MISSING:", item)

    if required_missing:
        print("RESULT: FAIL")
        return 1, backup_dir

    print("RESULT: PASS")
    return 0, backup_dir


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--label", default="runtime_backup")
    parser.add_argument("--include-tier2", type=int, default=1)
    args = parser.parse_args()

    rc, _ = create_backup(
        repo_root=Path(args.repo_root),
        label=args.label,
        include_tier2=bool(args.include_tier2),
    )
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

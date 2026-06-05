#!/usr/bin/env python3
# live_l1/tools/validate_runtime_backup.py
# P17D Live L1 runtime backup validation tool.
# ASCII-only. Read-only.

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_backup(backup_dir: Path) -> int:
    manifest_path = backup_dir / "backup_manifest.json"

    print("P17D RUNTIME BACKUP VALIDATION")
    print("backup_dir:", backup_dir)

    if not manifest_path.is_file():
        print("FAIL: missing_manifest")
        print("RESULT: FAIL")
        return 1

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print("FAIL: bad_manifest_json:", str(exc))
        print("RESULT: FAIL")
        return 1

    if not isinstance(manifest, dict):
        print("FAIL: manifest_not_dict")
        print("RESULT: FAIL")
        return 1

    files = manifest.get("files", [])
    if not isinstance(files, list):
        print("FAIL: manifest_files_not_list")
        print("RESULT: FAIL")
        return 1

    failed = 0

    for item in files:
        if not isinstance(item, dict):
            print("FAIL: bad_file_entry")
            failed += 1
            continue

        rel = str(item.get("backup_path", "")).strip()
        expected_sha = str(item.get("sha256", "")).strip()
        expected_size = int(item.get("size_bytes", -1))

        if rel == "":
            print("FAIL: empty_backup_path")
            failed += 1
            continue

        path = backup_dir / rel

        if not path.is_file():
            print("FAIL: missing_file:", rel)
            failed += 1
            continue

        actual_size = int(path.stat().st_size)
        actual_sha = _sha256(path)

        if actual_size != expected_size:
            print("FAIL: size_mismatch:", rel)
            failed += 1

        if actual_sha != expected_sha:
            print("FAIL: sha256_mismatch:", rel)
            failed += 1

    print("files_checked:", len(files))
    print("failures:", failed)

    if failed:
        print("RESULT: FAIL")
        return 1

    print("RESULT: PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("backup_dir")
    args = parser.parse_args()

    return validate_backup(Path(args.backup_dir))


if __name__ == "__main__":
    raise SystemExit(main())

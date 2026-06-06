#!/usr/bin/env python3
# live_l1/tools/test_monitor_failure_injection.py
# P19E failure injection tests for Live L1 monitoring.
# ASCII-only. Uses isolated copied runtime files only.

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


SOURCE_FILES = [
    "live_logs/execution_audit.jsonl",
    "live_logs/trades_l1.jsonl",
    "live_state/s2_position.jsonl",
    "live_state/s4_risk.jsonl",
    "live_state/loss_cluster_state.json",
]


def copy_runtime_files(dst_root: Path) -> None:
    for rel in SOURCE_FILES:
        src = PROJECT_ROOT / rel
        dst = dst_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.exists():
            shutil.copy2(src, dst)


def run_monitor(tmp_root: Path) -> tuple[int, dict]:
    monitor_path = tmp_root / "live_state" / "monitor_status.json"

    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "live_l1" / "tools" / "monitor_runtime.py"),
        "--repo-root",
        str(tmp_root),
        "--market-csv-path",
        str(PROJECT_ROOT / "data" / "l1_paper_short_gate_test.csv"),
        "--seeds-5m-csv",
        str(PROJECT_ROOT / "seeds" / "5m" / "btcusdt_5m_long_timing_core_v1.csv"),
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if not monitor_path.is_file():
        return proc.returncode, {}

    try:
        data = json.loads(monitor_path.read_text(encoding="utf-8"))
    except Exception:
        data = {}

    return proc.returncode, data


def assert_status(name: str, data: dict, expected_status: str) -> bool:
    actual = str(data.get("status", "MISSING"))
    if actual != expected_status:
        print("FAIL:", name, "expected_status=", expected_status, "actual_status=", actual)
        return False
    print("PASS:", name, "status=", actual)
    return True


def test_baseline() -> bool:
    with tempfile.TemporaryDirectory(prefix="p19e_baseline_") as td:
        tmp = Path(td)
        copy_runtime_files(tmp)
        rc, data = run_monitor(tmp)
        if rc not in (0, 1):
            print("FAIL: baseline unexpected_rc=", rc)
            return False
        return assert_status("baseline", data, "WARN")


def test_bad_s2_json() -> bool:
    with tempfile.TemporaryDirectory(prefix="p19e_bad_s2_") as td:
        tmp = Path(td)
        copy_runtime_files(tmp)
        path = tmp / "live_state" / "s2_position.jsonl"
        with path.open("a", encoding="utf-8") as fh:
            fh.write("{bad json line\n")
        rc, data = run_monitor(tmp)
        if rc != 1:
            print("FAIL: bad_s2_json expected_rc=1 actual_rc=", rc)
            return False
        return assert_status("bad_s2_json", data, "FAIL")


def test_missing_s2() -> bool:
    with tempfile.TemporaryDirectory(prefix="p19e_missing_s2_") as td:
        tmp = Path(td)
        copy_runtime_files(tmp)
        path = tmp / "live_state" / "s2_position.jsonl"
        if path.exists():
            path.unlink()
        rc, data = run_monitor(tmp)
        if rc != 1:
            print("FAIL: missing_s2 expected_rc=1 actual_rc=", rc)
            return False
        return assert_status("missing_s2", data, "FAIL")


def test_bad_loss_json() -> bool:
    with tempfile.TemporaryDirectory(prefix="p19e_bad_loss_") as td:
        tmp = Path(td)
        copy_runtime_files(tmp)
        path = tmp / "live_state" / "loss_cluster_state.json"
        path.write_text("{bad json\n", encoding="utf-8")
        rc, data = run_monitor(tmp)
        if rc != 1:
            print("FAIL: bad_loss_json expected_rc=1 actual_rc=", rc)
            return False
        return assert_status("bad_loss_json", data, "FAIL")


def test_loss_cluster_warn() -> bool:
    with tempfile.TemporaryDirectory(prefix="p19e_loss_warn_") as td:
        tmp = Path(td)
        copy_runtime_files(tmp)
        path = tmp / "live_state" / "loss_cluster_state.json"
        obj = {}
        if path.is_file():
            try:
                obj = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                obj = {}
        if not isinstance(obj, dict):
            obj = {}
        obj["schema_version"] = 1
        obj["pause_entries_remaining"] = 5
        path.write_text(json.dumps(obj, ensure_ascii=True, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        rc, data = run_monitor(tmp)
        if rc != 0:
            print("FAIL: loss_cluster_warn expected_rc=0 actual_rc=", rc)
            return False
        return assert_status("loss_cluster_warn", data, "WARN")


def main() -> int:
    print("P19E MONITOR FAILURE INJECTION TESTS")
    tests = [
        test_baseline,
        test_bad_s2_json,
        test_missing_s2,
        test_bad_loss_json,
        test_loss_cluster_warn,
    ]

    failed = 0
    for fn in tests:
        ok = fn()
        if not ok:
            failed += 1

    if failed:
        print("RESULT: FAIL")
        print("failed_tests:", failed)
        return 1

    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

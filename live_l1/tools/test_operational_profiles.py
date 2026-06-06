#!/usr/bin/env python3
# live_l1/tools/test_operational_profiles.py
# P20E negative tests for Live L1 operational profiles.
# ASCII-only.

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def run_cmd(env_updates: dict[str, str], args: list[str]) -> tuple[int, str]:
    env = os.environ.copy()
    env.update(env_updates)

    proc = subprocess.run(
        args,
        cwd=str(PROJECT_ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    output = (proc.stdout + "\n" + proc.stderr).strip()
    return proc.returncode, output


def expect_contains(name: str, output: str, needle: str) -> bool:
    if needle not in output:
        print("FAIL:", name, "missing:", needle)
        print(output)
        return False
    return True


def test_invalid_profile_falls_back_to_paper() -> bool:
    rc, output = run_cmd(
        {"L1_OPERATIONAL_PROFILE": "INVALID_PROFILE"},
        [
            sys.executable,
            "-c",
            "from live_l1.operational_profiles import profile_summary; print(profile_summary())",
        ],
    )

    ok = rc == 0 and expect_contains("invalid_profile_fallback", output, "'profile': 'PAPER'")
    print(("PASS:" if ok else "FAIL:"), "invalid_profile_fallback")
    return ok


def test_production_safe_launch_blocked() -> bool:
    rc, output = run_cmd(
        {"L1_OPERATIONAL_PROFILE": "PRODUCTION"},
        [
            sys.executable,
            "live_l1/tools/safe_launch.py",
            "--max-ticks",
            "1",
        ],
    )

    ok = (
        rc == 1
        and expect_contains("production_safe_launch_blocked", output, "PROFILE_POLICY: PRODUCTION is not enabled yet")
    )
    print(("PASS:" if ok else "FAIL:"), "production_safe_launch_blocked")
    return ok


def test_production_monitor_fails() -> bool:
    rc, output = run_cmd(
        {"L1_OPERATIONAL_PROFILE": "PRODUCTION"},
        [
            sys.executable,
            "live_l1/tools/monitor_runtime.py",
        ],
    )

    ok = (
        rc == 1
        and expect_contains("production_monitor_fails", output, "status: FAIL")
        and expect_contains("production_monitor_fails", output, "RESULT: FAIL")
    )
    print(("PASS:" if ok else "FAIL:"), "production_monitor_fails")
    return ok


def test_paper_without_safety_flags_blocked() -> bool:
    env = {
        "L1_OPERATIONAL_PROFILE": "PAPER",
        "L1_STARTUP_RECOVERY": "0",
        "L1_STARTUP_RECONCILIATION_GATE": "0",
    }

    rc, output = run_cmd(
        env,
        [
            sys.executable,
            "live_l1/tools/safe_launch.py",
            "--max-ticks",
            "1",
        ],
    )

    ok = (
        rc == 1
        and expect_contains("paper_without_safety_flags_blocked", output, "FAILED_STEP: required_safety_flags")
    )
    print(("PASS:" if ok else "FAIL:"), "paper_without_safety_flags_blocked")
    return ok


def main() -> int:
    print("P20E OPERATIONAL PROFILE NEGATIVE TESTS")

    tests = [
        test_invalid_profile_falls_back_to_paper,
        test_production_safe_launch_blocked,
        test_production_monitor_fails,
        test_paper_without_safety_flags_blocked,
    ]

    failed = 0

    for test in tests:
        if not test():
            failed += 1

    if failed:
        print("RESULT: FAIL")
        print("failed_tests:", failed)
        return 1

    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

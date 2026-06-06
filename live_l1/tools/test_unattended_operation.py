#!/usr/bin/env python3
# P21E unattended operation tests.
# ASCII-only.

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def run_control(profile: str) -> tuple[int, dict]:
    env = os.environ.copy()
    env["L1_OPERATIONAL_PROFILE"] = profile

    proc = subprocess.run(
        [
            sys.executable,
            "live_l1/tools/runtime_control_loop.py",
        ],
        cwd=str(PROJECT_ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    control_file = PROJECT_ROOT / "live_state" / "runtime_control.json"

    if not control_file.is_file():
        return proc.returncode, {}

    data = json.loads(
        control_file.read_text(encoding="utf-8")
    )

    return proc.returncode, data


def assert_equal(name: str, actual: str, expected: str) -> bool:
    if actual != expected:
        print(
            "FAIL:",
            name,
            "expected=",
            expected,
            "actual=",
            actual,
        )
        return False

    print(
        "PASS:",
        name,
        actual,
    )
    return True


def test_paper_profile() -> bool:
    rc, data = run_control("PAPER")

    ok = True

    ok &= assert_equal(
        "paper_control_state",
        str(data.get("control_state")),
        "DEGRADED",
    )

    ok &= assert_equal(
        "paper_control_action",
        str(data.get("control_action")),
        "CONTINUE",
    )

    ok &= assert_equal(
        "paper_escalation_level",
        str(data.get("escalation_level")),
        "WARN",
    )

    return ok


def test_production_profile() -> bool:
    rc, data = run_control("PRODUCTION")

    ok = True

    ok &= assert_equal(
        "production_control_state",
        str(data.get("control_state")),
        "RECOVERY_REQUIRED",
    )

    ok &= assert_equal(
        "production_control_action",
        str(data.get("control_action")),
        "STOP",
    )

    ok &= assert_equal(
        "production_escalation_level",
        str(data.get("escalation_level")),
        "FAIL",
    )

    return ok


def main() -> int:
    print("P21E UNATTENDED OPERATION TESTS")

    failed = 0

    if not test_paper_profile():
        failed += 1

    if not test_production_profile():
        failed += 1

    if failed:
        print("RESULT: FAIL")
        return 1

    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

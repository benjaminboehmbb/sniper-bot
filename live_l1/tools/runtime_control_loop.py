#!/usr/bin/env python3
# P21B Automated Monitoring Loop
# ASCII-only.

from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SCHEMA_VERSION = 1


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_control_file(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    monitor_cmd = [
        sys.executable,
        str(PROJECT_ROOT / "live_l1" / "tools" / "monitor_runtime.py"),
    ]

    proc = subprocess.run(
        monitor_cmd,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )

    monitor_file = PROJECT_ROOT / "live_state" / "monitor_status.json"

    if not monitor_file.is_file():
        payload = {
            "schema_version": SCHEMA_VERSION,
            "generated_utc": utc_now(),
            "control_state": "RECOVERY_REQUIRED",
            "control_action": "ESCALATE",
            "control_reason": "missing_monitor_status",
            "alerts": [],
        }

        write_control_file(
            PROJECT_ROOT / "live_state" / "runtime_control.json",
            payload,
        )

        return 1

    monitor = json.loads(
        monitor_file.read_text(encoding="utf-8")
    )

    status = str(
        monitor.get("status", "UNKNOWN")
    ).upper()

    if status == "PASS":
        control_state = "RUNNING"
        control_action = "CONTINUE"

    elif status == "WARN":
        control_state = "DEGRADED"
        control_action = "CONTINUE"

    else:
        control_state = "RECOVERY_REQUIRED"
        control_action = "ESCALATE"

    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_utc": utc_now(),
        "control_state": control_state,
        "control_action": control_action,
        "control_reason": status,
        "profile": monitor.get("profile", {}),
        "alerts": monitor.get("alerts", []),
    }

    write_control_file(
        PROJECT_ROOT / "live_state" / "runtime_control.json",
        payload,
    )

    print("P21B RUNTIME CONTROL LOOP")
    print("monitor_status:", status)
    print("control_state:", control_state)
    print("control_action:", control_action)
    print("RESULT: PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

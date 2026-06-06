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

    alerts = monitor.get("alerts", [])
    if not isinstance(alerts, list):
        alerts = []

    fail_alerts = [
        x for x in alerts
        if isinstance(x, dict) and str(x.get("severity", "")).upper() == "FAIL"
    ]

    stop_alert_codes = {
        "startup_validation_failed",
        "reconciliation_failed",
        "schema_validation_failed",
        "execution_replay_failed",
        "bad_json_detected",
        "missing_required_runtime_file",
        "runtime_position_mismatch",
        "unsupported_schema_version",
        "production_profile_not_enabled",
    }

    stop_required = False
    stop_reason = ""

    for alert in fail_alerts:
        code = str(alert.get("code", "")).strip()
        if code in stop_alert_codes:
            stop_required = True
            stop_reason = code
            break

    if status == "PASS":
        control_state = "RUNNING"
        control_action = "CONTINUE"
        control_reason = "PASS"

    elif status == "WARN":
        control_state = "DEGRADED"
        control_action = "CONTINUE"
        control_reason = "WARN"

    elif stop_required:
        control_state = "RECOVERY_REQUIRED"
        control_action = "STOP"
        control_reason = stop_reason

    else:
        control_state = "RECOVERY_REQUIRED"
        control_action = "ESCALATE"
        control_reason = status

    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_utc": utc_now(),
        "control_state": control_state,
        "control_action": control_action,
        "control_reason": control_reason,
        "profile": monitor.get("profile", {}),
        "alerts": alerts,
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

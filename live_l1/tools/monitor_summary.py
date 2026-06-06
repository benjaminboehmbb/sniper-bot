#!/usr/bin/env python3
# live_l1/tools/monitor_summary.py
# P19D Live L1 monitoring summary dashboard.
# ASCII-only. Read-only.

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(str(path))

    obj = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(obj, dict):
        raise ValueError("monitor status is not a JSON object")

    return obj


def safe_text(value: object, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--monitor-status-path", default="live_state/monitor_status.json")
    args = parser.parse_args()

    path = Path(args.monitor_status_path)

    try:
        data = load_json(path)
    except Exception as exc:
        print("LIVE L1 MONITOR SUMMARY")
        print("RESULT: FAIL")
        print("reason: cannot_read_monitor_status")
        print("detail:", str(exc))
        return 1

    status = safe_text(data.get("status"), "UNKNOWN")
    reason = safe_text(data.get("status_reason"), "")
    generated_utc = safe_text(data.get("generated_utc"), "")

    runtime = data.get("runtime", {})
    if not isinstance(runtime, dict):
        runtime = {}

    checks = data.get("checks", {})
    if not isinstance(checks, dict):
        checks = {}

    alerts = data.get("alerts", [])
    if not isinstance(alerts, list):
        alerts = []

    print("LIVE L1 MONITOR SUMMARY")
    print("status:", status)
    print("reason:", reason)
    print("generated_utc:", generated_utc)
    print("")

    print("RUNTIME")
    print("position:", safe_text(runtime.get("position"), "UNKNOWN"))
    print("side:", safe_text(runtime.get("side"), ""))
    print("trade_count:", safe_text(runtime.get("trade_count"), "0"))
    print("last_tick_id:", safe_text(runtime.get("last_tick_id"), "0"))
    print("last_timestamp_utc:", safe_text(runtime.get("last_timestamp_utc"), ""))
    print("kill_level:", safe_text(runtime.get("kill_level"), "UNKNOWN"))
    print("loss_cluster_pause_entries_remaining:", safe_text(runtime.get("loss_cluster_pause_entries_remaining"), "0"))
    print("")

    print("CHECKS")
    for name in sorted(checks.keys()):
        item = checks.get(name, {})
        if not isinstance(item, dict):
            print(name + ": FAIL invalid_check_payload")
            continue
        print(name + ":", safe_text(item.get("status"), "UNKNOWN"), "-", safe_text(item.get("detail"), ""))

    print("")

    print("ALERTS")
    if not alerts:
        print("none")
    else:
        for alert in alerts:
            if not isinstance(alert, dict):
                print("WARN unknown_alert invalid_alert_payload")
                continue
            print(
                safe_text(alert.get("severity"), "UNKNOWN")
                + " "
                + safe_text(alert.get("code"), "unknown_code")
                + " - "
                + safe_text(alert.get("detail"), "")
            )

    print("")

    if status in ("PASS", "WARN"):
        print("RESULT: PASS")
        return 0

    print("RESULT: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

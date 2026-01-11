#!/usr/bin/env python3
# tools/l1_health_check.py
#
# L1 Passive Health-Check
# Implements:
# - LIVE_DESIGN_L1_ALARM_CRITERIA_FINAL.md
# - LIVE_DESIGN_L1_ALARM_FLAG_SCHEMA_FINAL.md
#
# Properties:
# - read-only
# - no trading
# - no restart
# - no side effects except optional alert flag
# - ASCII-only

from __future__ import annotations

import os
import json
import time
from typing import List, Dict, Any

# -----------------------
# CONFIG (explicit paths)
# -----------------------

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

LOG_PATH = os.path.join(REPO_ROOT, "live_logs", "l1_paper.log")
STATE_S2_PATH = os.path.join(REPO_ROOT, "live_state", "s2_position.jsonl")
STATE_S4_PATH = os.path.join(REPO_ROOT, "live_state", "s4_risk.jsonl")

ALERT_FLAG_PATH = os.path.join(REPO_ROOT, "live_l1_alert.flag")

# No new logs for this many seconds -> alarm (only if log exists)
MAX_LOG_STALE_SECONDS = 600  # 10 minutes


# -----------------------
# Helpers
# -----------------------

def _read_lines(path: str) -> List[str]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        return [ln.strip() for ln in fh if ln.strip()]


def _read_jsonl_last(path: str) -> Dict[str, Any] | None:
    if not os.path.exists(path):
        return None
    lines = _read_lines(path)
    if not lines:
        return None
    try:
        return json.loads(lines[-1])
    except Exception:
        return None


def _extract_system_state_id(lines: List[str]) -> str:
    for ln in reversed(lines[-200:]):
        if "system_state_id" in ln:
            return ln.split("system_state_id", 1)[-1].strip(" :=,\"{}")
    return "unknown"


def _write_alert(
    reason: str,
    category: str,
    system_state_id: str,
    details: Dict[str, Any] | None = None,
) -> None:
    payload = {
        "status": "ALERT",
        "reason": reason,
        "category": category,
        "system_state_id": system_state_id or "unknown",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "action": "STOP_RECOMMENDED",
        "source": "l1_health_check",
    }
    if details:
        payload["details"] = details

    with open(ALERT_FLAG_PATH, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=True, separators=(",", ":"))


# -----------------------
# Alarm Checks
# -----------------------

def check_log_integrity(lines: List[str], log_path: str) -> str | None:
    # OPTION A:
    # If log file does not exist, L1 is not running -> no alarm
    if not os.path.exists(log_path):
        return None

    # Log exists but empty -> alarm
    if not lines:
        return "log_missing_or_empty"

    if not any("system_start" in ln for ln in lines):
        return "missing_system_start"

    required_events = [
        "snapshot_received",
        "data_valid",
        "intent_created",
        "order_not_sent",
        "state_update",
        "state_persisted",
        "loop_delay",
    ]

    joined = "\n".join(lines[-200:])
    for ev in required_events:
        if ev not in joined:
            return f"incomplete_tick_missing_{ev}"

    return None


def check_time_rhythm(log_path: str) -> str | None:
    if not os.path.exists(log_path):
        return None

    try:
        mtime = os.path.getmtime(log_path)
    except Exception:
        return "log_not_accessible"

    age = time.time() - mtime
    if age > MAX_LOG_STALE_SECONDS:
        return "log_stale_no_recent_entries"

    return None


def check_state_invariants() -> str | None:
    s2 = _read_jsonl_last(STATE_S2_PATH)
    if s2 is not None:
        if s2.get("position") != "FLAT":
            return "state_s2_position_not_flat"
        if float(s2.get("size", 0.0)) != 0.0:
            return "state_s2_size_not_zero"

    s4 = _read_jsonl_last(STATE_S4_PATH)
    if s4 is not None:
        if s4.get("kill_level") != "NONE":
            return "state_s4_kill_level_not_none"

    return None


def check_jsonl_integrity(path: str) -> str | None:
    if not os.path.exists(path):
        return None
    lines = _read_lines(path)
    for ln in lines[-50:]:
        try:
            json.loads(ln)
        except Exception:
            return f"invalid_jsonl_in_{os.path.basename(path)}"
    return None


# -----------------------
# Main
# -----------------------

def main() -> int:
    # Fresh evaluation
    if os.path.exists(ALERT_FLAG_PATH):
        os.remove(ALERT_FLAG_PATH)

    log_lines = _read_lines(LOG_PATH)
    system_state_id = _extract_system_state_id(log_lines)

    reason = check_log_integrity(log_lines, LOG_PATH)
    if reason:
        _write_alert(reason, "A_LOG_INTEGRITY", system_state_id)
        return 1

    reason = check_time_rhythm(LOG_PATH)
    if reason:
        _write_alert(reason, "D_TIME_RHYTHM", system_state_id)
        return 1

    reason = check_state_invariants()
    if reason:
        _write_alert(reason, "B_STATE_INVARIANTS", system_state_id)
        return 1

    reason = check_jsonl_integrity(STATE_S2_PATH)
    if reason:
        _write_alert(reason, "E_PERSISTENCE", system_state_id)
        return 1

    reason = check_jsonl_integrity(STATE_S4_PATH)
    if reason:
        _write_alert(reason, "E_PERSISTENCE", system_state_id)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())



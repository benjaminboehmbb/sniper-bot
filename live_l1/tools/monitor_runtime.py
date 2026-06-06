#!/usr/bin/env python3
# live_l1/tools/monitor_runtime.py
# P19B Live L1 monitoring snapshot generator.
# ASCII-only. Read-only for source runtime files. Writes monitor_status.json only.

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from live_l1.tools.reconcile_runtime_state import run_reconciliation
from live_l1.tools.replay_execution_state import replay_execution_state
from live_l1.tools.startup_validator import validate_startup
import subprocess


SCHEMA_VERSION = 1


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_jsonl_last(path: Path) -> tuple[dict[str, Any] | None, int, int]:
    if not path.exists():
        return None, 0, 0

    last = None
    good = 0
    bad = 0

    try:
        with path.open("r", encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if line == "":
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    bad += 1
                    continue
                if not isinstance(obj, dict):
                    bad += 1
                    continue
                good += 1
                last = obj
    except Exception:
        return None, good, bad + 1

    return last, good, bad


def read_json_file(path: Path) -> tuple[dict[str, Any] | None, int]:
    if not path.exists():
        return None, 0

    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None, 1

    if not isinstance(obj, dict):
        return None, 1

    return obj, 0


def safe_text(value: object, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def safe_float(value: object, default: float | None = None) -> float | None:
    if value is None:
        return default
    s = str(value).strip()
    if s == "":
        return default
    try:
        return float(s)
    except Exception:
        return default


def safe_int(value: object, default: int = 0) -> int:
    if value is None:
        return default
    s = str(value).strip()
    if s == "":
        return default
    try:
        return int(float(s))
    except Exception:
        return default


def check_status(passed: bool, detail: str) -> dict[str, str]:
    return {
        "status": "PASS" if passed else "FAIL",
        "detail": str(detail),
    }


def add_alert(alerts: list[dict[str, str]], severity: str, code: str, detail: str) -> None:
    alerts.append(
        {
            "severity": str(severity),
            "code": str(code),
            "detail": str(detail),
        }
    )


def worst_status(checks: dict[str, dict[str, str]], alerts: list[dict[str, str]]) -> tuple[str, str]:
    if any(a.get("severity") == "FAIL" for a in alerts):
        return "FAIL", "fail_alert_present"

    if any(c.get("status") == "FAIL" for c in checks.values()):
        return "FAIL", "check_failed"

    if any(a.get("severity") == "WARN" for a in alerts):
        return "WARN", "warn_alert_present"

    if any(c.get("status") == "WARN" for c in checks.values()):
        return "WARN", "check_warn"

    return "PASS", "all_checks_passed"


def build_monitor_status(
    *,
    repo_root: Path,
    market_csv_path: str,
    seeds_5m_csv: str,
    audit_log_path: str,
    s2_position_path: str,
    trades_path: str,
    loss_cluster_state_path: str,
    s4_risk_path: str,
    monitor_status_path: str,
    require_wsl: bool,
) -> dict[str, Any]:
    audit_path = repo_root / audit_log_path
    s2_path = repo_root / s2_position_path
    trades_file = repo_root / trades_path
    loss_path = repo_root / loss_cluster_state_path
    s4_path = repo_root / s4_risk_path
    monitor_path = repo_root / monitor_status_path

    alerts: list[dict[str, str]] = []
    checks: dict[str, dict[str, str]] = {}

    startup = validate_startup(
        repo_root=repo_root,
        market_csv_path=market_csv_path,
        seeds_5m_csv=seeds_5m_csv,
        require_wsl=require_wsl,
    )

    if startup.passed:
        checks["startup_validation"] = check_status(True, "startup validation passed")
    else:
        detail = "; ".join([x.code + ":" + x.detail for x in startup.issues])
        checks["startup_validation"] = check_status(False, detail)
        add_alert(alerts, "FAIL", "startup_validation_failed", detail)

    reconciliation = run_reconciliation(
        audit_path=audit_path,
        s2_path=s2_path,
        trades_path=trades_file,
        loss_path=loss_path,
    )
    reconciliation_failed = [x for x in reconciliation if not x.passed]

    if reconciliation_failed:
        detail = "; ".join([x.name + ":" + x.detail for x in reconciliation_failed])
        checks["reconciliation"] = check_status(False, detail)
        add_alert(alerts, "FAIL", "reconciliation_failed", detail)
    else:
        checks["reconciliation"] = check_status(True, "reconciliation passed")

    schema_cmd = [
        sys.executable,
        str(PROJECT_ROOT / "live_l1" / "tools" / "validate_runtime_schema.py"),
        "--audit-log-path",
        str(audit_path),
        "--trades-path",
        str(trades_file),
        "--s2-position-path",
        str(s2_path),
        "--loss-cluster-state-path",
        str(loss_path),
        "--s4-risk-path",
        str(s4_path),
    ]

    schema_proc = subprocess.run(
        schema_cmd,
        capture_output=True,
        text=True,
        check=False,
    )

    schema_output = (schema_proc.stdout + "\n" + schema_proc.stderr).strip()

    if schema_proc.returncode != 0:
        detail = schema_output if schema_output else "schema validator failed"
        checks["schema_validation"] = check_status(False, detail)
        add_alert(alerts, "FAIL", "schema_validation_failed", detail)
    else:
        checks["schema_validation"] = check_status(True, "schema validation passed")

    replay = replay_execution_state(audit_path)

    if replay.bad_json_lines != 0:
        detail = "bad_json_lines=" + str(replay.bad_json_lines)
        checks["execution_replay"] = check_status(False, detail)
        add_alert(alerts, "FAIL", "execution_replay_failed", detail)
    else:
        checks["execution_replay"] = check_status(True, "events_read=" + str(replay.events_read))

    s2_last, s2_count, s2_bad = read_jsonl_last(s2_path)
    s4_last, s4_count, s4_bad = read_jsonl_last(s4_path)
    trade_last, trade_count, trade_bad = read_jsonl_last(trades_file)
    loss_state, loss_bad = read_json_file(loss_path)

    if s2_bad != 0:
        checks["s2_state"] = check_status(False, "bad_json_lines=" + str(s2_bad))
        add_alert(alerts, "FAIL", "bad_json_detected", "s2_position bad_json_lines=" + str(s2_bad))
    elif s2_last is None:
        checks["s2_state"] = check_status(False, "missing_or_empty")
        add_alert(alerts, "FAIL", "missing_required_runtime_file", str(s2_path))
    else:
        checks["s2_state"] = check_status(True, "records=" + str(s2_count))

    if s4_bad != 0:
        checks["s4_risk"] = check_status(False, "bad_json_lines=" + str(s4_bad))
        add_alert(alerts, "FAIL", "bad_json_detected", "s4_risk bad_json_lines=" + str(s4_bad))
    elif s4_last is None:
        checks["s4_risk"] = check_status(False, "missing_or_empty")
        add_alert(alerts, "FAIL", "missing_required_runtime_file", str(s4_path))
    else:
        checks["s4_risk"] = check_status(True, "records=" + str(s4_count))

    if trade_bad != 0:
        checks["trades_log"] = check_status(False, "bad_json_lines=" + str(trade_bad))
        add_alert(alerts, "FAIL", "bad_json_detected", "trades_l1 bad_json_lines=" + str(trade_bad))
    else:
        checks["trades_log"] = check_status(True, "records=" + str(trade_count))

    if loss_bad != 0:
        checks["loss_cluster_state"] = check_status(False, "bad_json")
        add_alert(alerts, "FAIL", "bad_json_detected", "loss_cluster_state bad_json")
    elif loss_state is None:
        checks["loss_cluster_state"] = check_status("WARN" == "PASS", "missing_allowed")
    else:
        checks["loss_cluster_state"] = check_status(True, "loaded")

    loss_pause = 0
    if isinstance(loss_state, dict):
        loss_pause = safe_int(loss_state.get("pause_entries_remaining"), 0)
        if loss_pause > 0:
            add_alert(
                alerts,
                "WARN",
                "loss_cluster_active",
                "pause_entries_remaining=" + str(loss_pause),
            )

    kill_level = "NONE"
    cooldown_until_utc = None

    if isinstance(s4_last, dict):
        kill_level = safe_text(s4_last.get("kill_level"), "NONE").upper()
        cooldown_until_utc = s4_last.get("cooldown_until_utc", None)
        if kill_level != "NONE":
            add_alert(alerts, "WARN", "kill_level_active", "kill_level=" + kill_level)

    runtime = {
        "position": safe_text(s2_last.get("position") if isinstance(s2_last, dict) else replay.position, replay.position),
        "side": safe_text(s2_last.get("side") if isinstance(s2_last, dict) else replay.side, replay.side),
        "entry_price": safe_float(s2_last.get("entry_price") if isinstance(s2_last, dict) else replay.entry_price, replay.entry_price),
        "entry_timestamp_utc": safe_text(s2_last.get("entry_timestamp_utc") if isinstance(s2_last, dict) else replay.entry_timestamp_utc, replay.entry_timestamp_utc),
        "trade_count": int(trade_count),
        "last_trade_timestamp_utc": safe_text(trade_last.get("exit_timestamp_utc") if isinstance(trade_last, dict) else "", ""),
        "last_tick_id": safe_int(s2_last.get("last_tick_id") if isinstance(s2_last, dict) else 0, 0),
        "last_timestamp_utc": safe_text(s2_last.get("last_timestamp_utc") if isinstance(s2_last, dict) else "", ""),
        "kill_level": kill_level,
        "cooldown_until_utc": cooldown_until_utc,
        "loss_cluster_pause_entries_remaining": int(loss_pause),
    }

    status, status_reason = worst_status(checks, alerts)

    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_utc": utc_now(),
        "status": status,
        "status_reason": status_reason,
        "checks": checks,
        "runtime": runtime,
        "alerts": alerts,
        "source_files": {
            "execution_audit": str(audit_path),
            "trades": str(trades_file),
            "s2_position": str(s2_path),
            "s4_risk": str(s4_path),
            "loss_cluster_state": str(loss_path),
            "monitor_status": str(monitor_path),
        },
    }

    return payload


def write_monitor_status(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--market-csv-path", default="data/l1_paper_short_gate_test.csv")
    parser.add_argument("--seeds-5m-csv", default="seeds/5m/btcusdt_5m_long_timing_core_v1.csv")
    parser.add_argument("--audit-log-path", default="live_logs/execution_audit.jsonl")
    parser.add_argument("--s2-position-path", default="live_state/s2_position.jsonl")
    parser.add_argument("--trades-path", default="live_logs/trades_l1.jsonl")
    parser.add_argument("--loss-cluster-state-path", default="live_state/loss_cluster_state.json")
    parser.add_argument("--s4-risk-path", default="live_state/s4_risk.jsonl")
    parser.add_argument("--monitor-status-path", default="live_state/monitor_status.json")
    parser.add_argument("--require-wsl", type=int, default=1)
    args = parser.parse_args()

    repo_root = Path(args.repo_root)
    monitor_path = repo_root / args.monitor_status_path

    payload = build_monitor_status(
        repo_root=repo_root,
        market_csv_path=args.market_csv_path,
        seeds_5m_csv=args.seeds_5m_csv,
        audit_log_path=args.audit_log_path,
        s2_position_path=args.s2_position_path,
        trades_path=args.trades_path,
        loss_cluster_state_path=args.loss_cluster_state_path,
        s4_risk_path=args.s4_risk_path,
        monitor_status_path=args.monitor_status_path,
        require_wsl=bool(args.require_wsl),
    )

    write_monitor_status(monitor_path, payload)

    print("P19B MONITORING SNAPSHOT")
    print("monitor_status_path:", monitor_path)
    print("status:", payload["status"])
    print("status_reason:", payload["status_reason"])
    print("alerts:", len(payload["alerts"]))
    print("RESULT:", "PASS" if payload["status"] in ("PASS", "WARN") else "FAIL")

    if payload["status"] == "FAIL":
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

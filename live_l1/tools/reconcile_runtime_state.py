#!/usr/bin/env python3
# live_l1/tools/reconcile_runtime_state.py
# P8B Runtime State Reconciliation
# ASCII-only. Read-only. Does not modify state/log files.

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from live_l1.tools.replay_execution_state import replay_execution_state


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    detail: str


def _safe_text(value: object, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _safe_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _read_jsonl(path: Path) -> tuple[list[dict[str, Any]], int]:
    rows: list[dict[str, Any]] = []
    bad = 0

    if not path.exists():
        return rows, bad

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
            rows.append(obj)

    return rows, bad


def _read_json(path: Path) -> tuple[dict[str, Any] | None, int]:
    if not path.exists():
        return None, 0

    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None, 1

    if not isinstance(obj, dict):
        return None, 1

    return obj, 0


def _last_jsonl_object(path: Path) -> tuple[dict[str, Any] | None, int]:
    rows, bad = _read_jsonl(path)
    if not rows:
        return None, bad
    return rows[-1], bad


def _norm_position(value: object) -> str:
    s = _safe_text(value).upper()
    if s in ("LONG", "SHORT", "FLAT"):
        return s
    return "FLAT"


def _compare_float(a: object, b: object, tolerance: float = 1e-9) -> bool:
    return abs(_safe_float(a) - _safe_float(b)) <= tolerance


def _build_expected_closed_trades_from_audit(audit_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    expected: list[dict[str, Any]] = []
    open_pos: dict[str, Any] | None = None

    for row in audit_rows:
        event = _safe_text(row.get("event"))

        if event == "ENTRY_ACCEPTED":
            side = _safe_text(row.get("side")).lower()
            if side not in ("long", "short"):
                continue

            open_pos = {
                "side": side,
                "entry_price": _safe_float(row.get("price")),
                "entry_timestamp_utc": _safe_text(row.get("timestamp_utc")),
            }

        elif event == "EXIT_EXECUTED":
            if open_pos is None:
                continue

            expected.append(
                {
                    "side": open_pos["side"],
                    "entry_price": open_pos["entry_price"],
                    "entry_timestamp_utc": open_pos["entry_timestamp_utc"],
                    "exit_price": _safe_float(row.get("price")),
                    "exit_timestamp_utc": _safe_text(row.get("timestamp_utc")),
                    "audit_exit_reason": _safe_text(row.get("reason")),
                }
            )
            open_pos = None

    return expected


def check_audit_json(audit_path: Path) -> CheckResult:
    rows, bad = _read_jsonl(audit_path)
    if bad != 0:
        return CheckResult("audit_json_valid", False, f"bad_json_lines={bad}")
    return CheckResult("audit_json_valid", True, f"events={len(rows)} bad_json_lines=0")


def check_audit_vs_s2(audit_path: Path, s2_path: Path) -> CheckResult:
    replay = replay_execution_state(audit_path)
    s2_last, s2_bad = _last_jsonl_object(s2_path)

    if replay.bad_json_lines != 0:
        return CheckResult("audit_vs_s2_position", False, f"audit_bad_json_lines={replay.bad_json_lines}")

    if s2_bad != 0:
        return CheckResult("audit_vs_s2_position", False, f"s2_bad_json_lines={s2_bad}")

    if s2_last is None:
        if replay.position == "FLAT":
            return CheckResult("audit_vs_s2_position", True, "s2_missing_or_empty and audit_replay=FLAT")
        return CheckResult("audit_vs_s2_position", False, f"s2_missing_or_empty but audit_replay={replay.position}")

    s2_position = _norm_position(s2_last.get("position"))
    s2_side = _safe_text(s2_last.get("side")).lower()
    s2_entry_price = s2_last.get("entry_price")
    s2_entry_ts = _safe_text(s2_last.get("entry_timestamp_utc"))

    diffs: list[str] = []

    if replay.position != s2_position:
        diffs.append(f"position audit={replay.position} s2={s2_position}")

    if replay.position in ("LONG", "SHORT"):
        if replay.side != s2_side:
            diffs.append(f"side audit={replay.side} s2={s2_side}")
        if not _compare_float(replay.entry_price, s2_entry_price):
            diffs.append(f"entry_price audit={replay.entry_price} s2={s2_entry_price}")
        if replay.entry_timestamp_utc != s2_entry_ts:
            diffs.append(f"entry_ts audit={replay.entry_timestamp_utc} s2={s2_entry_ts}")

    if diffs:
        return CheckResult("audit_vs_s2_position", False, "; ".join(diffs))

    return CheckResult(
        "audit_vs_s2_position",
        True,
        f"position={replay.position} side={replay.side} entry_ts={replay.entry_timestamp_utc}",
    )


def check_audit_vs_trades(audit_path: Path, trades_path: Path) -> CheckResult:
    audit_rows, audit_bad = _read_jsonl(audit_path)
    trade_rows, trade_bad = _read_jsonl(trades_path)

    if audit_bad != 0:
        return CheckResult("audit_vs_trades", False, f"audit_bad_json_lines={audit_bad}")

    if trade_bad != 0:
        return CheckResult("audit_vs_trades", False, f"trade_bad_json_lines={trade_bad}")

    expected = _build_expected_closed_trades_from_audit(audit_rows)

    if len(expected) != len(trade_rows):
        return CheckResult(
            "audit_vs_trades",
            False,
            f"closed_trade_count audit_expected={len(expected)} trades={len(trade_rows)}",
        )

    diffs: list[str] = []

    for i, (exp, tr) in enumerate(zip(expected, trade_rows), start=1):
        if _safe_text(exp.get("side")).lower() != _safe_text(tr.get("side")).lower():
            diffs.append(f"trade_{i}_side audit={exp.get('side')} trade={tr.get('side')}")

        if _safe_text(exp.get("entry_timestamp_utc")) != _safe_text(tr.get("entry_timestamp_utc")):
            diffs.append(
                f"trade_{i}_entry_ts audit={exp.get('entry_timestamp_utc')} trade={tr.get('entry_timestamp_utc')}"
            )

        if _safe_text(exp.get("exit_timestamp_utc")) != _safe_text(tr.get("exit_timestamp_utc")):
            diffs.append(
                f"trade_{i}_exit_ts audit={exp.get('exit_timestamp_utc')} trade={tr.get('exit_timestamp_utc')}"
            )

        if not _compare_float(exp.get("entry_price"), tr.get("entry_price")):
            diffs.append(f"trade_{i}_entry_price audit={exp.get('entry_price')} trade={tr.get('entry_price')}")

        if not _compare_float(exp.get("exit_price"), tr.get("exit_price")):
            diffs.append(f"trade_{i}_exit_price audit={exp.get('exit_price')} trade={tr.get('exit_price')}")

    if diffs:
        return CheckResult("audit_vs_trades", False, "; ".join(diffs))

    return CheckResult("audit_vs_trades", True, f"closed_trades={len(trade_rows)}")


def check_trade_time_order(trades_path: Path) -> CheckResult:
    trade_rows, bad = _read_jsonl(trades_path)

    if bad != 0:
        return CheckResult("trade_time_order", False, f"trade_bad_json_lines={bad}")

    bad_rows: list[str] = []

    for i, row in enumerate(trade_rows, start=1):
        duration = _safe_float(row.get("duration_sec"), 0.0)
        entry_ts = _safe_text(row.get("entry_timestamp_utc"))
        exit_ts = _safe_text(row.get("exit_timestamp_utc"))

        if duration < 0.0:
            bad_rows.append(f"trade_{i}_negative_duration")

        if entry_ts != "" and exit_ts != "" and exit_ts < entry_ts:
            bad_rows.append(f"trade_{i}_exit_before_entry")

    if bad_rows:
        return CheckResult("trade_time_order", False, "; ".join(bad_rows))

    return CheckResult("trade_time_order", True, f"trades_checked={len(trade_rows)}")


def check_loss_cluster(loss_path: Path) -> CheckResult:
    obj, bad = _read_json(loss_path)

    if bad != 0:
        return CheckResult("loss_cluster_state", False, "loss_cluster_bad_json")

    if obj is None:
        return CheckResult("loss_cluster_state", True, "missing_allowed")

    pause = _safe_int(obj.get("pause_entries_remaining"), 0)
    pnls = obj.get("recent_closed_trade_pnls", [])

    if pause < 0:
        return CheckResult("loss_cluster_state", False, f"negative_pause_entries_remaining={pause}")

    if not isinstance(pnls, list):
        return CheckResult("loss_cluster_state", False, "recent_closed_trade_pnls_not_list")

    for i, value in enumerate(pnls, start=1):
        try:
            float(value)
        except Exception:
            return CheckResult("loss_cluster_state", False, f"pnl_{i}_not_float")

    return CheckResult(
        "loss_cluster_state",
        True,
        f"pause_entries_remaining={pause} recent_closed_trade_pnls={len(pnls)}",
    )


def run_reconciliation(
    *,
    audit_path: Path,
    s2_path: Path,
    trades_path: Path,
    loss_path: Path,
) -> list[CheckResult]:
    return [
        check_audit_json(audit_path),
        check_audit_vs_s2(audit_path, s2_path),
        check_audit_vs_trades(audit_path, trades_path),
        check_trade_time_order(trades_path),
        check_loss_cluster(loss_path),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-log-path", default="live_logs/execution_audit.jsonl")
    parser.add_argument("--s2-position-path", default="live_state/s2_position.jsonl")
    parser.add_argument("--trades-path", default="live_logs/trades_l1.jsonl")
    parser.add_argument("--loss-cluster-state-path", default="live_state/loss_cluster_state.json")
    args = parser.parse_args()

    results = run_reconciliation(
        audit_path=Path(args.audit_log_path),
        s2_path=Path(args.s2_position_path),
        trades_path=Path(args.trades_path),
        loss_path=Path(args.loss_cluster_state_path),
    )

    print("P8B RUNTIME STATE RECONCILIATION")
    print("audit_log_path:", args.audit_log_path)
    print("s2_position_path:", args.s2_position_path)
    print("trades_path:", args.trades_path)
    print("loss_cluster_state_path:", args.loss_cluster_state_path)
    print("")

    passed_all = True

    for item in results:
        status = "PASS" if item.passed else "FAIL"
        print(f"{status}: {item.name}: {item.detail}")
        if not item.passed:
            passed_all = False

    print("")
    print("RESULT:", "PASS" if passed_all else "FAIL")

    return 0 if passed_all else 1


if __name__ == "__main__":
    raise SystemExit(main())

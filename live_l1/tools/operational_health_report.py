#!/usr/bin/env python3
# live_l1/tools/operational_health_report.py
# P11A Live L1 operational health report.
# ASCII-only. Read-only.

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from live_l1.tools.reconcile_runtime_state import run_reconciliation
from live_l1.tools.replay_execution_state import replay_execution_state
from live_l1.tools.startup_validator import validate_startup


def _read_last_jsonl(path: Path):
    if not path.exists():
        return None, 0, 0

    last = None
    count = 0
    bad = 0

    with path.open("r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                bad += 1
                continue
            if not isinstance(obj, dict):
                bad += 1
                continue
            count += 1
            last = obj

    return last, count, bad


def _read_json(path: Path):
    if not path.exists():
        return None, 0
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None, 1
    if not isinstance(obj, dict):
        return None, 1
    return obj, 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--market-csv-path", default="data/l1_paper_short_gate_test.csv")
    parser.add_argument("--seeds-5m-csv", default="seeds/5m/btcusdt_5m_long_timing_core_v1.csv")
    parser.add_argument("--audit-log-path", default="live_logs/execution_audit.jsonl")
    parser.add_argument("--s2-position-path", default="live_state/s2_position.jsonl")
    parser.add_argument("--trades-path", default="live_logs/trades_l1.jsonl")
    parser.add_argument("--loss-cluster-state-path", default="live_state/loss_cluster_state.json")
    parser.add_argument("--require-wsl", type=int, default=1)
    args = parser.parse_args()

    repo = Path(args.repo_root)

    audit_path = repo / args.audit_log_path
    s2_path = repo / args.s2_position_path
    trades_path = repo / args.trades_path
    loss_path = repo / args.loss_cluster_state_path

    startup = validate_startup(
        repo_root=repo,
        market_csv_path=args.market_csv_path,
        seeds_5m_csv=args.seeds_5m_csv,
        require_wsl=bool(args.require_wsl),
    )

    reconciliation = run_reconciliation(
        audit_path=audit_path,
        s2_path=s2_path,
        trades_path=trades_path,
        loss_path=loss_path,
    )

    replay = replay_execution_state(audit_path)

    last_s2, s2_count, s2_bad = _read_last_jsonl(s2_path)
    last_trade, trade_count, trade_bad = _read_last_jsonl(trades_path)
    loss_state, loss_bad = _read_json(loss_path)

    reconciliation_pass = all(x.passed for x in reconciliation)
    startup_pass = startup.passed
    replay_pass = replay.bad_json_lines == 0
    s2_pass = s2_bad == 0
    trade_pass = trade_bad == 0
    loss_pass = loss_bad == 0

    overall_pass = all([
        startup_pass,
        reconciliation_pass,
        replay_pass,
        s2_pass,
        trade_pass,
        loss_pass,
    ])

    print("P11A LIVE L1 OPERATIONAL HEALTH REPORT")
    print("repo_root:", args.repo_root)
    print("")

    print("STARTUP_VALIDATION:", "PASS" if startup_pass else "FAIL")
    for issue in startup.issues:
        print("STARTUP_ISSUE:", issue.code, issue.detail)

    print("RECONCILIATION:", "PASS" if reconciliation_pass else "FAIL")
    for item in reconciliation:
        status = "PASS" if item.passed else "FAIL"
        print(f"RECONCILIATION_CHECK: {status}: {item.name}: {item.detail}")

    print("REPLAY:", "PASS" if replay_pass else "FAIL")
    print("REPLAY_POSITION:", replay.position)
    print("REPLAY_SIDE:", replay.side)
    print("REPLAY_ENTRY_PRICE:", "" if replay.entry_price is None else replay.entry_price)
    print("REPLAY_ENTRY_TIMESTAMP_UTC:", replay.entry_timestamp_utc)
    print("REPLAY_EVENTS_READ:", replay.events_read)
    print("REPLAY_BAD_JSON_LINES:", replay.bad_json_lines)

    print("S2_POSITION_LOG:", "PASS" if s2_pass else "FAIL")
    print("S2_POSITION_ROWS:", s2_count)
    print("S2_POSITION_BAD_JSON_LINES:", s2_bad)
    if last_s2 is not None:
        print("S2_LAST_POSITION:", last_s2.get("position", ""))
        print("S2_LAST_SIDE:", last_s2.get("side", ""))
        print("S2_LAST_ENTRY_PRICE:", last_s2.get("entry_price", ""))
        print("S2_LAST_ENTRY_TIMESTAMP_UTC:", last_s2.get("entry_timestamp_utc", ""))
        print("S2_LAST_SNAPSHOT_ID:", last_s2.get("last_snapshot_id", last_s2.get("snapshot_id", "")))

    print("TRADES_LOG:", "PASS" if trade_pass else "FAIL")
    print("TRADES_ROWS:", trade_count)
    print("TRADES_BAD_JSON_LINES:", trade_bad)
    if last_trade is not None:
        print("LAST_TRADE_SIDE:", last_trade.get("side", ""))
        print("LAST_TRADE_ENTRY_TIMESTAMP_UTC:", last_trade.get("entry_timestamp_utc", ""))
        print("LAST_TRADE_EXIT_TIMESTAMP_UTC:", last_trade.get("exit_timestamp_utc", ""))
        print("LAST_TRADE_PNL:", last_trade.get("pnl", ""))

    print("LOSS_CLUSTER_STATE:", "PASS" if loss_pass else "FAIL")
    if loss_state is not None:
        print("LOSS_CLUSTER_PAUSE_ENTRIES_REMAINING:", loss_state.get("pause_entries_remaining", ""))
        pnls = loss_state.get("recent_closed_trade_pnls", [])
        print("LOSS_CLUSTER_RECENT_PNLS_COUNT:", len(pnls) if isinstance(pnls, list) else "invalid")
    else:
        print("LOSS_CLUSTER_STATE_MISSING:", int(not loss_path.exists()))

    print("")
    print("OVERALL:", "PASS" if overall_pass else "FAIL")

    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())

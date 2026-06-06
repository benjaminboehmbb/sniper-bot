#!/usr/bin/env python3
# live_l1/tools/safe_launch.py
# P12A Live L1 safe operational launch workflow.
# ASCII-only.

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from live_l1.core.loop import run_l1_loop_step1234567
from live_l1.tools.reconcile_runtime_state import run_reconciliation
from live_l1.tools.startup_validator import validate_startup
from live_l1.operational_profiles import profile_summary


def _env_bool(key: str, default: bool = False) -> bool:
    value = os.environ.get(key)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "y", "on")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--max-ticks", type=int, default=1)
    parser.add_argument("--max-run-seconds", type=float, default=0.0)
    parser.add_argument("--market-csv-path", default=os.environ.get("L1_MARKET_CSV_PATH", "data/l1_paper_short_gate_test.csv"))
    parser.add_argument("--seeds-5m-csv", default=os.environ.get("SEEDS_5M_CSV", "seeds/5m/btcusdt_5m_long_timing_core_v1.csv"))
    parser.add_argument("--audit-log-path", default=os.environ.get("L1_AUDIT_LOG_PATH", "live_logs/execution_audit.jsonl"))
    parser.add_argument("--s2-position-path", default=os.environ.get("L1_S2_POSITION_PATH", "live_state/s2_position.jsonl"))
    parser.add_argument("--trades-path", default=os.environ.get("L1_TRADE_LOG_PATH", "live_logs/trades_l1.jsonl"))
    parser.add_argument("--loss-cluster-state-path", default=os.environ.get("L1_LOSS_CLUSTER_STATE_PATH", "live_state/loss_cluster_state.json"))
    parser.add_argument("--require-wsl", type=int, default=1)
    args = parser.parse_args()

    repo = Path(args.repo_root)

    profile = profile_summary()

    print("P12A SAFE OPERATIONAL LAUNCH")
    print("repo_root:", args.repo_root)
    print("max_ticks:", args.max_ticks)
    print("max_run_seconds:", args.max_run_seconds)
    print("operational_profile:", profile["profile"])
    print("")

    if profile["profile"] == "PRODUCTION":
        print("SAFE_LAUNCH: FAIL")
        print("FAILED_STEP: profile_policy")
        print("PROFILE_POLICY: PRODUCTION is not enabled yet")
        return 1

    print("STEP 1: startup validation")

    if profile["startup_validation_required"]:
        startup = validate_startup(
            repo_root=repo,
            market_csv_path=args.market_csv_path,
            seeds_5m_csv=args.seeds_5m_csv,
            require_wsl=bool(args.require_wsl),
        )

        if not startup.passed:
            print("SAFE_LAUNCH: FAIL")
            print("FAILED_STEP: startup_validation")
            for issue in startup.issues:
                print("STARTUP_ISSUE:", issue.code, issue.detail)
            return 1

        print("STARTUP_VALIDATION: PASS")
    else:
        print("STARTUP_VALIDATION: SKIP profile_allows_skip")

    print("STEP 2: reconciliation")

    if not profile["reconciliation_required"]:
        print("RECONCILIATION: SKIP profile_allows_skip")
        reconciliation = []
    else:
        reconciliation = run_reconciliation(
        audit_path=repo / args.audit_log_path,
        s2_path=repo / args.s2_position_path,
        trades_path=repo / args.trades_path,
        loss_path=repo / args.loss_cluster_state_path,
    )

    failed_reconciliation = [x for x in reconciliation if not x.passed]

    if failed_reconciliation:
        print("SAFE_LAUNCH: FAIL")
        print("FAILED_STEP: reconciliation")
        for item in reconciliation:
            status = "PASS" if item.passed else "FAIL"
            print(f"RECONCILIATION_CHECK: {status}: {item.name}: {item.detail}")
        return 1

    print("RECONCILIATION: PASS")

    print("STEP 3: required safety flags")
    startup_recovery = _env_bool("L1_STARTUP_RECOVERY", False)
    reconciliation_gate = _env_bool("L1_STARTUP_RECONCILIATION_GATE", False)

    if not startup_recovery:
        print("SAFE_LAUNCH: FAIL")
        print("FAILED_STEP: required_safety_flags")
        print("FLAG_ISSUE: L1_STARTUP_RECOVERY must be enabled")
        return 1

    if not reconciliation_gate:
        print("SAFE_LAUNCH: FAIL")
        print("FAILED_STEP: required_safety_flags")
        print("FLAG_ISSUE: L1_STARTUP_RECONCILIATION_GATE must be enabled")
        return 1

    print("REQUIRED_SAFETY_FLAGS: PASS")
    print("SAFE_LAUNCH: PASS")
    print("STARTING LIVE L1")

    max_run_seconds = None
    if args.max_run_seconds > 0.0:
        max_run_seconds = float(args.max_run_seconds)

    rc = run_l1_loop_step1234567(
        repo_root=str(repo),
        max_ticks=int(args.max_ticks),
        max_run_seconds=max_run_seconds,
    )

    print("RUNTIME_RC:", rc)
    return int(rc)


if __name__ == "__main__":
    raise SystemExit(main())

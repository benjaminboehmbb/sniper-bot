#!/usr/bin/env python3
# live_l1/tools/startup_validator.py
# P10A Live L1 startup validator.
# ASCII-only. Read-only. Does not modify state/log files.

from __future__ import annotations

import argparse
import os
import platform
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    detail: str


@dataclass(frozen=True)
class StartupValidationResult:
    passed: bool
    issues: list[ValidationIssue]


def _env_bool(key: str, default: bool = False) -> bool:
    value = os.environ.get(key)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "y", "on")


def _is_wsl() -> bool:
    if platform.system().lower() != "linux":
        return False

    candidates = [
        Path("/proc/version"),
        Path("/proc/sys/kernel/osrelease"),
    ]

    for path in candidates:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
        except Exception:
            continue

        if "microsoft" in text or "wsl" in text:
            return True

    return False


def validate_startup(
    *,
    repo_root: Path,
    market_csv_path: str,
    seeds_5m_csv: str,
    require_wsl: bool,
) -> StartupValidationResult:
    issues: list[ValidationIssue] = []

    market_path = repo_root / market_csv_path
    seeds_path = repo_root / seeds_5m_csv

    startup_recovery = _env_bool("L1_STARTUP_RECOVERY", False)
    reconciliation_gate = _env_bool("L1_STARTUP_RECONCILIATION_GATE", False)

    if require_wsl and not _is_wsl():
        issues.append(
            ValidationIssue(
                code="not_wsl_environment",
                detail="Live L1 runs are only allowed in WSL.",
            )
        )

    if not market_path.is_file():
        issues.append(
            ValidationIssue(
                code="missing_market_csv",
                detail=str(market_path),
            )
        )

    if not seeds_path.is_file():
        issues.append(
            ValidationIssue(
                code="missing_seed_csv",
                detail=str(seeds_path),
            )
        )

    if startup_recovery and not reconciliation_gate:
        issues.append(
            ValidationIssue(
                code="startup_recovery_without_reconciliation_gate",
                detail="L1_STARTUP_RECOVERY=1 requires L1_STARTUP_RECONCILIATION_GATE=1.",
            )
        )

    return StartupValidationResult(
        passed=len(issues) == 0,
        issues=issues,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--market-csv-path",
        default=os.environ.get("L1_MARKET_CSV_PATH", "data/l1_paper_short_gate_test.csv"),
    )
    parser.add_argument(
        "--seeds-5m-csv",
        default=os.environ.get("SEEDS_5M_CSV", "seeds/5m/btcusdt_5m_long_timing_core_v1.csv"),
    )
    parser.add_argument("--require-wsl", type=int, default=1)
    args = parser.parse_args()

    result = validate_startup(
        repo_root=Path(args.repo_root),
        market_csv_path=args.market_csv_path,
        seeds_5m_csv=args.seeds_5m_csv,
        require_wsl=bool(int(args.require_wsl)),
    )

    print("P10A STARTUP VALIDATION")
    print("repo_root:", args.repo_root)
    print("market_csv_path:", args.market_csv_path)
    print("seeds_5m_csv:", args.seeds_5m_csv)
    print("require_wsl:", int(bool(int(args.require_wsl))))
    print("")

    if result.passed:
        print("PASS: startup validation")
        return 0

    print("FAIL: startup validation")
    for issue in result.issues:
        print(f"FAIL: {issue.code}: {issue.detail}")

    return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# tools/l1c_smoke_test.py
#
# L1-C Smoke Test (deterministic, fast)
# - Verifiziert, dass timing_5m fuer LONG/SHORT Seeds korrekt votet
# - Fuehrt zwei Mini-Paper-Runs mit Forced-Intents aus (LONG + SHORT)
# - Parsed die Logs und prueft, ob BUY durch LONG bestaetigt wird und SELL durch SHORT bestaetigt wird
#
# Exit codes:
#   0 = OK
#   2 = FAIL (assertions)
#   3 = ERROR (unexpected runtime error)
#
# Usage (WSL, repo-root):
#   python3 tools/l1c_smoke_test.py
#
# Optional:
#   python3 tools/l1c_smoke_test.py --keep-logs
#   python3 tools/l1c_smoke_test.py --max-ticks 120 --thresh 0.60

from __future__ import annotations

import argparse
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple


DEFAULT_LONG_SEEDS = "seeds/5m/btcusdt_5m_long_timing_core_v1.csv"
DEFAULT_SHORT_SEEDS = "seeds/5m/btcusdt_5m_short_timing_core_v1.csv"


@dataclass
class RunResult:
    ok: bool
    label: str
    log_path: str
    timing_cli_direction: str
    timing_cli_seed_id: str
    confirm_buy: int
    confirm_sell: int
    block_buy: int
    block_sell: int
    vote_long: int
    vote_short: int
    vote_none: int
    reason_counts: Dict[str, int]
    err: str = ""


def _now_tag() -> str:
    # timezone-aware UTC, avoids DeprecationWarning
    return datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")


def _run_cmd(cmd: List[str], env: Dict[str, str], cwd: str) -> Tuple[int, str, str]:
    p = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return p.returncode, p.stdout, p.stderr


def _parse_kv_line(line: str) -> Dict[str, str]:
    """
    Parses key=value tokens separated by spaces.
    Values are assumed to not contain unescaped spaces.
    """
    out: Dict[str, str] = {}
    for tok in line.strip().split():
        if "=" not in tok:
            continue
        k, v = tok.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def _parse_intent_fused_events(log_path: str) -> List[Dict[str, str]]:
    events: List[Dict[str, str]] = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            if "event=intent_fused" not in line:
                continue
            kv = _parse_kv_line(line)
            if kv.get("event") != "intent_fused":
                continue
            events.append(kv)
    return events


def _summarize(events: List[Dict[str, str]]) -> Tuple[int, int, int, int, int, int, int, Dict[str, int]]:
    confirm_buy = 0
    confirm_sell = 0
    block_buy = 0
    block_sell = 0

    vote_long = 0
    vote_short = 0
    vote_none = 0

    reason_counts: Dict[str, int] = {}

    for e in events:
        raw = (e.get("intent_1m_raw") or "").upper()
        final = (e.get("intent_final") or "").upper()

        vd = (e.get("vote_5m_direction") or "none").lower()
        if vd == "long":
            vote_long += 1
        elif vd == "short":
            vote_short += 1
        else:
            vote_none += 1

        rc = e.get("reason_code") or ""
        if rc:
            reason_counts[rc] = reason_counts.get(rc, 0) + 1

        if raw == "BUY":
            if final == "BUY":
                confirm_buy += 1
            elif final == "HOLD":
                block_buy += 1
        elif raw == "SELL":
            if final == "SELL":
                confirm_sell += 1
            elif final == "HOLD":
                block_sell += 1

    return confirm_buy, confirm_sell, block_buy, block_sell, vote_long, vote_short, vote_none, reason_counts


def _timing_cli(repo_root: str, seeds_csv: str) -> Tuple[bool, str, str, str]:
    """
    Runs:
      python3 -m live_l1.core.timing_5m --seeds <csv>
    """
    env = os.environ.copy()
    cmd = ["python3", "-m", "live_l1.core.timing_5m", "--seeds", seeds_csv]
    code, out, err = _run_cmd(cmd, env=env, cwd=repo_root)
    if code != 0:
        return False, "", "", f"timing_5m CLI failed (code={code}): {err.strip() or out.strip()}"

    line = (out.strip().splitlines() or [""])[-1].strip()
    m_dir = re.search(r"direction=([a-zA-Z]+)", line)
    m_seed = re.search(r"seed_id=([A-Za-z0-9_\-]+)", line)

    direction = (m_dir.group(1).lower() if m_dir else "")
    seed_id = (m_seed.group(1) if m_seed else "")
    if not direction:
        return False, "", "", f"timing_5m CLI output not parseable: {line}"
    return True, direction, seed_id, ""


def _paper_run(
    repo_root: str,
    label: str,
    seeds_csv: str,
    thresh: float,
    max_ticks: int,
    keep_logs: bool,
) -> RunResult:
    tag = _now_tag()
    log_path = os.path.join(repo_root, "live_logs", f"l1_paper_smoke_{label}_{tag}.log")

    ok_cli, cli_dir, cli_seed, cli_err = _timing_cli(repo_root, seeds_csv)
    if not ok_cli:
        return RunResult(
            ok=False,
            label=label,
            log_path=log_path,
            timing_cli_direction="",
            timing_cli_seed_id="",
            confirm_buy=0,
            confirm_sell=0,
            block_buy=0,
            block_sell=0,
            vote_long=0,
            vote_short=0,
            vote_none=0,
            reason_counts={},
            err=cli_err,
        )

    env = os.environ.copy()
    env["L1_LOG_PATH"] = log_path
    env["THRESH_5M"] = str(thresh)
    env["SEEDS_5M_CSV"] = seeds_csv

    env["L1_TEST_FORCE_INTENTS"] = "1"
    env["L1_TEST_FORCE_BUY_EVERY"] = "10"
    env["L1_TEST_FORCE_SELL_EVERY"] = "15"
    env["L1_TEST_FORCE_WARMUP_TICKS"] = "0"

    cmd = [
        "python3",
        "-m",
        "scripts.run_live_l1_paper",
        "--repo-root",
        ".",
        "--max-ticks",
        str(max_ticks),
        "--decision-tick-seconds",
        "0.0",
        "--thresh-5m",
        str(thresh),
        "--seeds-5m-csv",
        seeds_csv,
    ]

    code, out, err = _run_cmd(cmd, env=env, cwd=repo_root)
    if code != 0:
        msg = (err.strip() or out.strip())
        return RunResult(
            ok=False,
            label=label,
            log_path=log_path,
            timing_cli_direction=cli_dir,
            timing_cli_seed_id=cli_seed,
            confirm_buy=0,
            confirm_sell=0,
            block_buy=0,
            block_sell=0,
            vote_long=0,
            vote_short=0,
            vote_none=0,
            reason_counts={},
            err=f"paper run failed (code={code}): {msg}",
        )

    if not os.path.isfile(log_path):
        return RunResult(
            ok=False,
            label=label,
            log_path=log_path,
            timing_cli_direction=cli_dir,
            timing_cli_seed_id=cli_seed,
            confirm_buy=0,
            confirm_sell=0,
            block_buy=0,
            block_sell=0,
            vote_long=0,
            vote_short=0,
            vote_none=0,
            reason_counts={},
            err="paper log not found: " + log_path,
        )

    events = _parse_intent_fused_events(log_path)
    (
        confirm_buy,
        confirm_sell,
        block_buy,
        block_sell,
        vote_long,
        vote_short,
        vote_none,
        reason_counts,
    ) = _summarize(events)

    ok = True
    err_msg = ""

    if len(events) < 5:
        ok = False
        err_msg += f"too few intent_fused events: {len(events)}; "

    if label == "LONG":
        if cli_dir != "long":
            ok = False
            err_msg += f"timing_cli_direction expected long, got {cli_dir}; "
        if confirm_buy < 1:
            ok = False
            err_msg += "expected confirm_buy>=1 for LONG; "
        if confirm_sell != 0:
            ok = False
            err_msg += f"unexpected confirm_sell={confirm_sell} for LONG; "
        if vote_long < 1:
            ok = False
            err_msg += "expected vote_long>=1 for LONG; "

    elif label == "SHORT":
        if cli_dir != "short":
            ok = False
            err_msg += f"timing_cli_direction expected short, got {cli_dir}; "
        if confirm_sell < 1:
            ok = False
            err_msg += "expected confirm_sell>=1 for SHORT; "
        if confirm_buy != 0:
            ok = False
            err_msg += f"unexpected confirm_buy={confirm_buy} for SHORT; "
        if vote_short < 1:
            ok = False
            err_msg += "expected vote_short>=1 for SHORT; "

    else:
        ok = False
        err_msg += f"unknown label {label}; "

    if ok and (not keep_logs):
        try:
            os.remove(log_path)
        except Exception:
            pass

    return RunResult(
        ok=ok,
        label=label,
        log_path=log_path,
        timing_cli_direction=cli_dir,
        timing_cli_seed_id=cli_seed,
        confirm_buy=confirm_buy,
        confirm_sell=confirm_sell,
        block_buy=block_buy,
        block_sell=block_sell,
        vote_long=vote_long,
        vote_short=vote_short,
        vote_none=vote_none,
        reason_counts=reason_counts,
        err=err_msg.strip(),
    )


def _print_result(rr: RunResult) -> None:
    status = "OK" if rr.ok else "FAIL"
    print(f"[{status}] {rr.label} seeds: timing_cli_direction={rr.timing_cli_direction} timing_cli_seed_id={rr.timing_cli_seed_id}")
    print(f"       confirm_buy={rr.confirm_buy} block_buy={rr.block_buy} confirm_sell={rr.confirm_sell} block_sell={rr.block_sell}")
    print(f"       votes: long={rr.vote_long} short={rr.vote_short} none={rr.vote_none}")
    if rr.err:
        print(f"       error={rr.err}")
    if (not rr.ok) or os.path.isfile(rr.log_path):
        print(f"       log={rr.log_path}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".", help="repo root (default: .)")
    ap.add_argument("--symbol", default="BTCUSDT", help="symbol (default: BTCUSDT)")
    ap.add_argument("--long-seeds", default=DEFAULT_LONG_SEEDS, help=f"LONG seeds csv (default: {DEFAULT_LONG_SEEDS})")
    ap.add_argument("--short-seeds", default=DEFAULT_SHORT_SEEDS, help=f"SHORT seeds csv (default: {DEFAULT_SHORT_SEEDS})")
    ap.add_argument("--thresh", type=float, default=0.60, help="5m thresh (default: 0.60)")
    ap.add_argument("--max-ticks", type=int, default=120, help="ticks per mini-run (default: 120)")
    ap.add_argument("--keep-logs", action="store_true", help="do not delete successful smoke logs")
    args = ap.parse_args()

    repo_root = os.path.abspath(args.repo_root)

    try:
        os.makedirs(os.path.join(repo_root, "live_logs"), exist_ok=True)

        long_rr = _paper_run(
            repo_root=repo_root,
            label="LONG",
            seeds_csv=args.long_seeds,
            thresh=float(args.thresh),
            max_ticks=int(args.max_ticks),
            keep_logs=bool(args.keep_logs),
        )
        _print_result(long_rr)

        short_rr = _paper_run(
            repo_root=repo_root,
            label="SHORT",
            seeds_csv=args.short_seeds,
            thresh=float(args.thresh),
            max_ticks=int(args.max_ticks),
            keep_logs=bool(args.keep_logs),
        )
        _print_result(short_rr)

        if long_rr.ok and short_rr.ok:
            print("[OK] L1-C smoke test passed.")
            return 0

        print("[FAIL] L1-C smoke test failed.")
        return 2

    except Exception as e:
        print("[ERROR] Unexpected error:", str(e))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())


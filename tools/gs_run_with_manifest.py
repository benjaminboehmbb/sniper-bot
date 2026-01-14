#!/usr/bin/env python3
# tools/gs_run_with_manifest.py
#
# Purpose:
#   One-shot GS runner that:
#     1) writes a run manifest to results/GS/meta/
#     2) runs GS input preflight (tools/gs_input_preflight.py)
#     3) runs exactly one evaluation via engine/simtraderGS.py
#     4) writes eval JSON to results/GS/meta/
#
# Key requirements:
#   - Works in WSL
#   - Robust "engine import" even when executed as a script (adds repo_root to sys.path)
#   - Deterministic metadata capture (git commit, engine sha256, args)
#   - Explicit gate control:
#       --gate auto|none|allow_long|allow_short
#     Gate semantics (when enabled):
#       - Gate=0 forces score to extreme value to prevent entries AND force immediate exit.
#         long:  score = -1e9 when gate=0
#         short: score = +1e9 when gate=0
#
# ASCII-only output by design.

import argparse
import ast
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import pandas as pd
import numpy as np


# ---------------------------
# helpers
# ---------------------------

def utc_now_compact() -> str:
    # 2026-01-14T08-46-26Z
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


def die(msg: str, code: int = 2) -> None:
    print(f"[fatal] {msg}", file=sys.stderr)
    raise SystemExit(code)


def ensure_repo_root() -> Path:
    # We assume this file lives under <repo_root>/tools/...
    here = Path(__file__).resolve()
    repo_root = here.parents[1]
    if not (repo_root / "engine").exists():
        # fallback to CWD
        repo_root = Path.cwd().resolve()
    if not (repo_root / "engine").exists():
        die("could not locate repo_root (missing engine/). Run from repo root.")
    return repo_root


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_cmd_capture(cmd: list, cwd: Path) -> Tuple[int, str]:
    try:
        out = subprocess.check_output(cmd, cwd=str(cwd), stderr=subprocess.STDOUT).decode("utf-8", errors="replace")
        return 0, out.strip()
    except subprocess.CalledProcessError as e:
        out = (e.output or b"").decode("utf-8", errors="replace").strip()
        return int(e.returncode), out


def git_commit(repo_root: Path) -> str:
    rc, out = run_cmd_capture(["git", "rev-parse", "HEAD"], cwd=repo_root)
    return out if rc == 0 and out else "UNKNOWN"


def parse_comb(s: str) -> Dict[str, float]:
    try:
        obj = ast.literal_eval(s)
    except Exception as e:
        die(f"could not parse --comb-json (must be python dict literal). err={e}")
    if not isinstance(obj, dict):
        die("--comb-json must parse to dict")
    out: Dict[str, float] = {}
    for k, v in obj.items():
        if not isinstance(k, str):
            continue
        try:
            out[k] = float(v)
        except Exception:
            continue
    if not out:
        die("comb parsed but empty after float conversion")
    return out


def read_comb_file(p: Path) -> Dict[str, float]:
    if not p.exists():
        die(f"--comb-file not found: {p}")
    txt = p.read_text(encoding="utf-8", errors="replace").strip()
    if not txt:
        die(f"--comb-file empty: {p}")
    return parse_comb(txt)


def ensure_outdir(repo_root: Path) -> Path:
    outdir = repo_root / "results" / "GS" / "meta"
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir


def preflight_cmd(repo_root: Path,
                  price_csv: str,
                  rows: int,
                  offset: int,
                  timestamp_col: str,
                  require_signals: str,
                  fail_on_all_zero: bool) -> list:
    cmd = [
        sys.executable, "tools/gs_input_preflight.py",
        "--csv", price_csv,
        "--rows", str(rows),
        "--offset", str(offset),
        "--timestamp_col", timestamp_col,
        "--require_signals", require_signals,
    ]
    if fail_on_all_zero:
        cmd.append("--fail_on_all_zero_signals")
    return cmd


def compute_gate_stats(df: pd.DataFrame, gate_col: str, rows: int) -> Dict[str, Any]:
    if gate_col not in df.columns:
        return {"present": False, "rows_checked": int(rows), "ones": 0, "allow_rate": 0.0}
    s = pd.to_numeric(df[gate_col], errors="coerce").fillna(0.0)
    # treat >0 as 1
    ones = int((s.values[:rows] > 0.0).sum())
    rate = float(ones / float(rows)) if rows > 0 else 0.0
    return {"present": True, "rows_checked": int(rows), "ones": ones, "allow_rate": rate}


def pick_gate_mode(mode: str, direction: str, df: pd.DataFrame) -> str:
    mode = (mode or "").strip().lower()
    if mode in ("none", "allow_long", "allow_short"):
        return mode
    if mode != "auto":
        die("--gate must be one of: auto, none, allow_long, allow_short")
    # auto:
    if direction == "long" and "allow_long" in df.columns:
        return "allow_long"
    if direction == "short" and "allow_short" in df.columns:
        return "allow_short"
    return "none"


def gate_mask_array(df: pd.DataFrame, gate_mode: str) -> Optional[np.ndarray]:
    if gate_mode == "none":
        return None
    col = gate_mode
    if col not in df.columns:
        die(f"gate requested but missing column '{col}' in price_df")
    s = pd.to_numeric(df[col], errors="coerce").fillna(0.0).to_numpy(dtype=float)
    return (s > 0.0).astype(np.int8)


# ---------------------------
# GS evaluation (internal)
# ---------------------------

def import_simtraderGS(repo_root: Path):
    # Fix "No module named 'engine'" when executed as a script from non-root.
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    try:
        from engine import simtraderGS  # type: ignore
        return simtraderGS
    except Exception as e:
        die(f"could not import engine.simtraderGS: {e}")


def eval_one(simtraderGS,
             df: pd.DataFrame,
             comb: Dict[str, float],
             direction: str,
             tp: float,
             sl: float,
             max_hold: int,
             enter_z: float,
             exit_z: float,
             fee_rt: float,
             gate_mode_effective: str) -> Dict[str, Any]:
    # Use GS internal signal prep to stay consistent with GS contract.
    # We intentionally reproduce the GS score building (based on KEYMAP + SIGNALS) here
    # so we can apply a gate transformation to the score before calling _simulate_*.
    if not hasattr(simtraderGS, "_set_df") or not hasattr(simtraderGS, "_prep_signals"):
        # fallback: try public entrypoints
        if hasattr(simtraderGS, "evaluate_strategy"):
            res = simtraderGS.evaluate_strategy(price_df=df, comb=comb, direction=direction)
            return dict(res)
        if hasattr(simtraderGS, "evaluate"):
            res = simtraderGS.evaluate(price_df=df, comb=comb, direction=direction)
            return dict(res)
        if hasattr(simtraderGS, "_eval_core"):
            res = simtraderGS._eval_core(comb=comb, direction=direction, df=df)
            return dict(res)
        die("engine.simtraderGS has no usable evaluation function")

    simtraderGS._set_df(df)
    simtraderGS._prep_signals()

    close = simtraderGS._CLOSE  # pylint: disable=protected-access
    z = simtraderGS._SIG        # pylint: disable=protected-access
    if close is None:
        die("GS internal close array is None after _prep_signals()")

    score = np.zeros_like(close, dtype=float)

    keymap = getattr(simtraderGS, "KEYMAP", {})
    # z keys are *_signal column names
    for k, w in comb.items():
        col = keymap.get(k, k)
        if col in z:
            try:
                weight = float(w)
            except Exception:
                continue
            score += weight * z[col]

    # ensure finite
    if hasattr(simtraderGS, "_finite_array"):
        score = simtraderGS._finite_array(score, fill=0.0)

    # Apply gate to the score (prevents entry and forces exit when gate=0).
    mask = gate_mask_array(df, gate_mode_effective)
    if mask is not None:
        if direction == "long":
            score = np.where(mask > 0, score, -1e9)
        else:
            score = np.where(mask > 0, score, +1e9)

    # Run sim
    direction = direction.lower().strip()
    if direction == "long":
        if not hasattr(simtraderGS, "_simulate_long"):
            die("GS missing internal _simulate_long")
        res = simtraderGS._simulate_long(score, close, tp, sl, max_hold, enter_z, exit_z, fee_rt)
    elif direction == "short":
        if not hasattr(simtraderGS, "_simulate_short"):
            die("GS missing internal _simulate_short")
        res = simtraderGS._simulate_short(score, close, tp, sl, max_hold, enter_z, exit_z, fee_rt)
    else:
        die("direction must be long or short")

    # Normalize output fields similar to GS _eval_core
    out = dict(res)
    out["pnl_sum"] = float(out.get("roi", 0.0))
    out["num_trades"] = int(out.get("num_trades", 0) or 0)
    nt = out["num_trades"]
    ps = float(out.get("pnl_sum", 0.0))
    out["avg_trade"] = float(ps / nt) if nt else 0.0

    for k in ("roi", "winrate", "sharpe", "pnl_sum", "avg_trade"):
        v = out.get(k, 0.0)
        try:
            fv = float(v)
            if not np.isfinite(fv):
                fv = 0.0
        except Exception:
            fv = 0.0
        out[k] = fv

    return out


# ---------------------------
# main
# ---------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--price-csv", required=True, help="Price CSV (GS format, with *_signal + gates).")
    ap.add_argument("--direction", required=True, choices=["long", "short"])
    ap.add_argument("--comb-json", default="", help="Combination as python dict literal, e.g. \"{'macd':0.6,'ma200':0.6}\"")
    ap.add_argument("--comb-file", default="", help="Path to file containing python dict literal.")
    ap.add_argument("--timestamp-col", default="timestamp_utc")
    ap.add_argument("--fee-roundtrip", type=float, default=0.0)
    ap.add_argument("--tp", type=float, default=0.04)
    ap.add_argument("--sl", type=float, default=0.02)
    ap.add_argument("--max-hold", type=int, default=1440)
    ap.add_argument("--enter-z", type=float, default=1.0)
    ap.add_argument("--exit-z", type=float, default=0.0)
    ap.add_argument("--preflight-rows", type=int, default=200000)
    ap.add_argument("--preflight-offset", type=int, default=0)
    ap.add_argument("--fail-on-all-zero-signals", action="store_true")
    ap.add_argument("--allow-impossible-enter-z", action="store_true",
                    help="Allow extreme enter_z that likely yields zero trades (still writes manifest).")

    # NEW: explicit gate mode
    ap.add_argument("--gate", default="auto", choices=["auto", "none", "allow_long", "allow_short"],
                    help="Gate mode: auto uses allow_long/allow_short based on direction if present; none disables gating; allow_long/allow_short forces that gate column.")

    args = ap.parse_args()

    repo_root = ensure_repo_root()
    outdir = ensure_outdir(repo_root)

    # comb
    comb: Dict[str, float] = {}
    if args.comb_json.strip():
        comb = parse_comb(args.comb_json.strip())
    elif args.comb_file.strip():
        comb = read_comb_file(Path(args.comb_file.strip()))
    else:
        die("Provide --comb-json or --comb-file")

    if (not args.allow_impossible_enter_z) and float(args.enter_z) > 50.0:
        die("enter_z looks impossible (>50). Pass --allow-impossible-enter-z if intentional.")

    # Load df (for gates stats + evaluation)
    price_csv = args.price_csv.strip()
    if not price_csv:
        die("--price-csv empty")

    # Read price csv
    try:
        df = pd.read_csv(price_csv)
    except Exception as e:
        die(f"could not read price csv: {price_csv}. err={e}")

    # Determine effective gate mode
    gate_eff = pick_gate_mode(args.gate, args.direction, df)

    # Preflight requires signals list from comb keys (base names)
    # We pass base names that look like "rsi" "macd" "ma200" etc.
    # If user provided *_signal keys, we strip suffix for preflight.
    req = []
    for k in comb.keys():
        kk = k.strip()
        if kk.endswith("_signal"):
            kk = kk[:-7]
        req.append(kk)
    require_signals = ",".join(sorted(set(req)))

    # Manifest
    run_ts = utc_now_compact()
    manifest_path = outdir / f"run_manifest_{run_ts}.json"
    eval_path = outdir / f"gs_eval_{run_ts}.json"

    engine_path = repo_root / "engine" / "simtraderGS.py"
    engine_hash = sha256_file(engine_path) if engine_path.exists() else "MISSING"

    # Gate stats (on preflight window)
    rows = int(args.preflight_rows)
    off = int(args.preflight_offset)
    df_win = df.iloc[off:off + rows].copy() if rows > 0 else df.iloc[0:0].copy()

    gates_block: Dict[str, Any] = {
        "window": {"offset": off, "rows": rows},
        "computed": True,
        "rows_checked": int(len(df_win)),
        "effective_gate_mode": gate_eff,
    }
    # Always report allow_long/allow_short presence if available
    if len(df_win):
        gates_block["allow_long"] = compute_gate_stats(df_win, "allow_long", int(len(df_win)))
        gates_block["allow_short"] = compute_gate_stats(df_win, "allow_short", int(len(df_win)))

    manifest = {
        "run_ts_utc": run_ts,
        "git_commit": git_commit(repo_root),
        "repo_root": str(repo_root),
        "engine_sha256": engine_hash,
        "price_csv": price_csv,
        "timestamp_col": args.timestamp_col,
        "window": {"offset": off, "rows": rows},
        "direction": args.direction,
        "use_forward": None,  # not inferred here; keep explicit runner arg if you later add it
        "comb": comb,
        "enter_z": float(args.enter_z),
        "exit_z": float(args.exit_z),
        "take_profit_pct": float(args.tp),
        "stop_loss_pct": float(args.sl),
        "max_hold_bars": int(args.max_hold),
        "fee_roundtrip": float(args.fee_roundtrip),
        "slippage_model": "none",  # explicit
        "gate_mode": args.gate,
        "gate_mode_effective": gate_eff,
        "gates": gates_block,
        "preflight": {
            "rows": rows,
            "offset": off,
            "require_signals": require_signals,
            "fail_on_all_zero_signals": bool(args.fail_on_all_zero_signals),
        },
    }

    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[ok] wrote manifest: {manifest_path}")

    # Run preflight (subprocess)
    cmd = preflight_cmd(
        repo_root=repo_root,
        price_csv=price_csv,
        rows=rows,
        offset=off,
        timestamp_col=args.timestamp_col,
        require_signals=require_signals,
        fail_on_all_zero=bool(args.fail_on_all_zero_signals),
    )
    print("[info] preflight: " + " ".join(cmd))
    rc = subprocess.call(cmd, cwd=str(repo_root))
    if rc != 0:
        die(f"preflight failed rc={rc}", code=rc)

    # Run evaluation
    simtraderGS = import_simtraderGS(repo_root)
    res = eval_one(
        simtraderGS=simtraderGS,
        df=df,
        comb=comb,
        direction=args.direction,
        tp=float(args.tp),
        sl=float(args.sl),
        max_hold=int(args.max_hold),
        enter_z=float(args.enter_z),
        exit_z=float(args.exit_z),
        fee_rt=float(args.fee_roundtrip),
        gate_mode_effective=gate_eff,
    )

    eval_obj = {
        "run_ts_utc": run_ts,
        "manifest_path": str(manifest_path),
        "eval": res,
    }
    eval_path.write_text(json.dumps(eval_obj, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[ok] wrote eval: {eval_path}")
    print("[result] " + json.dumps(res, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


#!/usr/bin/env python3
# tools/gs_run_with_manifest.py
#
# External runner that:
#  (1) writes run manifest (results/GS/meta/run_manifest_<UTC>.json)
#  (2) runs CSV preflight (tools/gs_input_preflight.py)
#  (3) evaluates one GS comb via engine/simtraderGS.py (NO engine modifications on disk)

import argparse
import ast
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd

# Ensure repo-root importability (avoid ModuleNotFoundError in WSL when running as script)
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine import simtraderGS  # type: ignore


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_cmd(cmd: List[str], cwd: Path) -> Tuple[int, str]:
    try:
        cp = subprocess.run(cmd, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return int(cp.returncode), (cp.stdout or "").strip()
    except Exception as e:
        return 99, f"EXCEPTION: {e}"


def git_commit(repo_root: Path) -> str:
    rc, out = run_cmd(["git", "rev-parse", "HEAD"], cwd=repo_root)
    return out if rc == 0 and out else "UNKNOWN"


def parse_comb(s: str) -> Dict[str, float]:
    s = s.strip()
    if not s:
        raise ValueError("empty comb string")
    try:
        obj = json.loads(s)
    except Exception:
        obj = ast.literal_eval(s)
    if not isinstance(obj, dict):
        raise ValueError("comb must be a dict")
    out: Dict[str, float] = {}
    for k, v in obj.items():
        try:
            out[str(k)] = float(v)
        except Exception:
            continue
    if not out:
        raise ValueError("comb parsed but empty after float conversion")
    return out


def required_signals_from_comb(comb: Dict[str, float]) -> List[str]:
    req: List[str] = []
    for k in comb.keys():
        kk = str(k).strip()
        if not kk:
            continue
        if kk.endswith("_signal"):
            kk = kk[:-7]
        req.append(kk)
    seen = set()
    out: List[str] = []
    for x in req:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def set_engine_cfg(tp: float, sl: float, max_hold: int, enter_z: float, exit_z: float, fee_roundtrip: float) -> None:
    # Runtime mutation only (NO disk changes)
    simtraderGS._CFG.setdefault("strategy", {})
    simtraderGS._CFG["strategy"].setdefault("risk", {})
    simtraderGS._CFG["strategy"]["risk"]["take_profit_pct"] = float(tp)
    simtraderGS._CFG["strategy"]["risk"]["stop_loss_pct"] = float(sl)
    simtraderGS._CFG["strategy"]["max_hold_bars"] = int(max_hold)
    simtraderGS._CFG["strategy"]["enter_z"] = float(enter_z)
    simtraderGS._CFG["strategy"]["exit_z"] = float(exit_z)
    simtraderGS._CFG["strategy"]["fee_roundtrip_pct"] = float(fee_roundtrip)


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def engine_eval(price_df: pd.DataFrame, comb: Any, direction: str) -> Dict[str, Any]:
    # Prefer public API in GS: evaluate_strategy(price_df, comb, direction)
    if hasattr(simtraderGS, "evaluate_strategy"):
        return simtraderGS.evaluate_strategy(price_df=price_df, comb=comb, direction=direction)  # type: ignore
    # Legacy/alternate names (defensive)
    if hasattr(simtraderGS, "evaluate"):
        return simtraderGS.evaluate(price_df=price_df, comb=comb, direction=direction)  # type: ignore
    if hasattr(simtraderGS, "_eval_core"):
        return simtraderGS._eval_core(comb=comb, direction=direction, df=price_df)  # type: ignore
    raise AttributeError("No supported eval entrypoint found in engine/simtraderGS.py")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--price-csv", required=True, help="GS-compatible CSV with *_signal columns")
    ap.add_argument("--direction", required=True, choices=["long", "short"], help="Evaluation direction")
    ap.add_argument("--comb-json", default="", help="Combination dict as JSON or Python-literal string")
    ap.add_argument("--comb-file", default="", help="Path to a file containing a comb dict string/JSON")
    ap.add_argument("--fee-roundtrip", type=float, default=0.0, help="Roundtrip fee (entry+exit), e.g. 0.0004")
    ap.add_argument("--tp", type=float, default=0.04, help="Take profit pct")
    ap.add_argument("--sl", type=float, default=0.02, help="Stop loss pct")
    ap.add_argument("--max-hold", type=int, default=1440, help="Max hold bars")
    ap.add_argument("--enter-z", type=float, default=1.0, help="Entry threshold (z)")
    ap.add_argument("--exit-z", type=float, default=0.0, help="Exit threshold (z)")
    ap.add_argument("--timestamp-col", default="timestamp_utc", help="Timestamp column name for preflight")
    ap.add_argument("--preflight-rows", type=int, default=200000, help="Preflight window rows")
    ap.add_argument("--preflight-offset", type=int, default=0, help="Preflight window offset rows")
    ap.add_argument("--regime-cols", default="", help="Comma list of regime cols for preflight (optional)")
    ap.add_argument("--fail-on-all-zero-signals", action="store_true",
                    help="Preflight fails if any required signal is all-zero")
    args = ap.parse_args()

    run_utc = utc_now_iso()
    price_csv = str(args.price_csv).strip()

    # Load comb string
    if args.comb_file:
        comb_str = Path(args.comb_file).read_text(encoding="utf-8").strip()
    else:
        comb_str = args.comb_json.strip()
    if not comb_str:
        print("[fatal] missing --comb-json or --comb-file", file=sys.stderr)
        return 2

    comb = parse_comb(comb_str)
    req_signals = required_signals_from_comb(comb)

    # Manifest
    engine_path = (REPO_ROOT / "engine" / "simtraderGS.py").resolve()
    manifest: Dict[str, Any] = {
        "git_commit": git_commit(REPO_ROOT),
        "repo_root": str(REPO_ROOT),
        "engine_sha256": sha256_file(engine_path) if engine_path.exists() else "MISSING",
        "price_csv": price_csv,
        "timestamp_col": str(args.timestamp_col),
        "window": {"offset": int(args.preflight_offset), "rows": int(args.preflight_rows)},
        "direction": str(args.direction),
        "use_forward": False,  # df passed directly; keep field for schema stability
        "enter_z": float(args.enter_z),
        "exit_z": float(args.exit_z),
        "take_profit_pct": float(args.tp),
        "stop_loss_pct": float(args.sl),
        "max_hold_bars": int(args.max_hold),
        "fee_roundtrip": float(args.fee_roundtrip),
        "slippage_model": "NONE",
        "required_signals": req_signals,
        "created_utc": run_utc
    }

    out_dir = REPO_ROOT / "results" / "GS" / "meta"
    manifest_path = out_dir / f"run_manifest_{run_utc.replace(':','-')}.json"
    write_json(manifest_path, manifest)
    print(f"[ok] wrote manifest: {manifest_path}")

    # Preflight
    preflight_cmd = [
        sys.executable, "tools/gs_input_preflight.py",
        "--csv", price_csv,
        "--rows", str(int(args.preflight_rows)),
        "--offset", str(int(args.preflight_offset)),
        "--timestamp_col", str(args.timestamp_col),
    ]
    if args.regime_cols.strip():
        preflight_cmd += ["--regime_cols", args.regime_cols.strip()]
    if req_signals:
        preflight_cmd += ["--require_signals", ",".join(req_signals)]
    if args.fail_on_all_zero_signals:
        preflight_cmd += ["--fail_on_all_zero_signals"]

    print("[info] preflight:", " ".join(preflight_cmd))
    rc, out = run_cmd(preflight_cmd, cwd=REPO_ROOT)
    if out:
        print(out)
    if rc != 0:
        print(f"[fatal] preflight failed rc={rc}", file=sys.stderr)
        return 3

    # Evaluate
    df = pd.read_csv(price_csv)
    set_engine_cfg(tp=args.tp, sl=args.sl, max_hold=args.max_hold, enter_z=args.enter_z, exit_z=args.exit_z, fee_roundtrip=args.fee_roundtrip)
    res = engine_eval(price_df=df, comb=comb, direction=args.direction)

    eval_path = out_dir / f"gs_eval_{run_utc.replace(':','-')}.json"
    write_json(eval_path, {"created_utc": run_utc, "args": vars(args), "comb": comb, "result": res})
    print(f"[ok] wrote eval: {eval_path}")
    print("[result]", json.dumps(res, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

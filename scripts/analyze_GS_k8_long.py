import argparse
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

ENV_FEE_KEY = "SIMTRADERGS_FEE_ROUNDTRIP"


def repo_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def import_simtrader_gs():
    rr = repo_root()
    if rr not in sys.path:
        sys.path.insert(0, rr)
    try:
        from engine import simtraderGS  # type: ignore
    except Exception as e:
        raise RuntimeError(f"Failed to import engine/simtraderGS.py: {e}")
    return simtraderGS


class EnvVar:
    def __init__(self, key: str, value: Optional[str]):
        self.key = key
        self.value = value
        self.prev: Optional[str] = None

    def __enter__(self):
        self.prev = os.environ.get(self.key)
        if self.value is None:
            os.environ.pop(self.key, None)
        else:
            os.environ[self.key] = str(self.value)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.prev is None:
            os.environ.pop(self.key, None)
        else:
            os.environ[self.key] = self.prev
        return False


def parse_offsets(s: str) -> List[int]:
    return [int(x.strip()) for x in s.split(",") if x.strip()]


def read_window(csv_path: str, offset: int, nrows: int) -> pd.DataFrame:
    need_start = offset
    need_end = offset + nrows
    chunks: List[pd.DataFrame] = []
    seen = 0

    for chunk in pd.read_csv(csv_path, chunksize=200_000):
        clen = len(chunk)
        if seen + clen <= need_start:
            seen += clen
            continue

        start = max(0, need_start - seen)
        end = min(clen, need_end - seen)
        if end > start:
            chunks.append(chunk.iloc[start:end].copy())

        seen += clen
        if seen >= need_end:
            break

    if not chunks:
        return pd.DataFrame()
    return pd.concat(chunks, ignore_index=True)


def apply_gate(
    df: pd.DataFrame,
    direction: str,
    apply_regime_gate: bool,
    regime_col: Optional[str],
) -> pd.DataFrame:
    if not apply_regime_gate or df.empty:
        return df

    if "allow_long" in df.columns and "allow_short" in df.columns:
        if direction == "long":
            return df[df["allow_long"] == 1].copy()
        return df[df["allow_short"] == 1].copy()

    col = regime_col or "regime_v1"
    if col not in df.columns:
        return df

    want = 1 if direction == "long" else -1
    return df[df[col] == want].copy()


def ts() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--strategies_csv", required=True)
    ap.add_argument("--rows", type=int, default=200000)
    ap.add_argument("--offsets", default="0")
    ap.add_argument("--direction", choices=["long", "short"], required=True)
    ap.add_argument("--fee", type=float, default=0.0)
    ap.add_argument("--apply_regime_gate", action="store_true")
    ap.add_argument("--regime_col", default=None)
    ap.add_argument("--limit", type=int, default=0, help="Smoke: first N strategies only")
    args = ap.parse_args()

    if args.direction != "long":
        raise RuntimeError("This analyzer is for K8 LONG only.")

    rr = repo_root()
    simtraderGS = import_simtrader_gs()

    offsets = parse_offsets(args.offsets)
    fee = float(args.fee)

    out_dir = os.path.join(rr, "results", "GS", "k8_long")
    os.makedirs(out_dir, exist_ok=True)

    print("REPO_ROOT:", rr)
    print("CSV:", args.csv)
    print("STRATEGIES_CSV:", args.strategies_csv)
    print("ROWS(per window):", int(args.rows))
    print("OFFSETS:", offsets)
    print("DIRECTION:", args.direction)
    print("FEE(roundtrip):", fee)
    print("REGIME_GATE:", "ON" if args.apply_regime_gate else "OFF")
    print("OUT_DIR:", out_dir)
    print("")

    strat = pd.read_csv(args.strategies_csv)
    if "combination" not in strat.columns:
        raise RuntimeError("strategies_csv must contain column 'combination'")

    if args.limit > 0:
        strat = strat.head(int(args.limit)).copy()

    total = len(strat)
    print("STRATEGIES_RUN:", total)
    print("")

    windows: List[Tuple[int, pd.DataFrame]] = []
    for off in offsets:
        dfw = read_window(args.csv, off, int(args.rows))
        dfw = apply_gate(dfw, args.direction, args.apply_regime_gate, args.regime_col)
        windows.append((int(off), dfw))
        print(f"WINDOW offset={off} post_rows={len(dfw)}")

    print("")

    results: List[Dict[str, Any]] = []

    with EnvVar(ENV_FEE_KEY, "0"):
        for i, r in enumerate(strat.itertuples(index=False), start=1):
            comb = json.loads(getattr(r, "combination"))

            roi_fee_list: List[float] = []
            trades_list: List[int] = []
            per_win: Dict[str, Any] = {}

            for off, wdf in windows:
                if wdf.empty:
                    roi = 0.0
                    trades = 0
                else:
                    res = simtraderGS.evaluate_strategy(wdf, comb, args.direction)
                    roi = float(res.get("roi", 0.0))
                    trades = int(res.get("num_trades", 0))

                roi_fee = roi - fee * trades
                roi_fee_list.append(roi_fee)
                trades_list.append(trades)

                per_win[f"roi_fee_off_{off}"] = roi_fee
                per_win[f"trades_off_{off}"] = trades

            out = {
                "engine": "simtraderGS",
                "k": 8,
                "direction": "long",
                "roi_fee_mean": sum(roi_fee_list) / len(roi_fee_list),
                "trades_sum": int(sum(trades_list)),
                "combination": json.dumps(comb, sort_keys=True),
            }
            out.update(per_win)
            results.append(out)

            if i % 200 == 0 or i == total:
                pct = 100.0 * i / total
                print(f"PROGRESS {i}/{total} ({pct:.1f}%)")

    label = "SMOKE" if args.limit > 0 else "FULL"
    out_path = os.path.join(out_dir, f"strategy_results_GS_k8_long_{label}_{ts()}.csv")
    pd.DataFrame(results).to_csv(out_path, index=False)

    print("")
    print("OK WROTE:", out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

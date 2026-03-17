import argparse
import json
import os
import sys
from datetime import datetime
from itertools import combinations
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


def apply_gate(df: pd.DataFrame, direction: str, apply_regime_gate: bool, regime_col: Optional[str]) -> pd.DataFrame:
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


def discover_signals(csv_path: str) -> List[str]:
    df_head = pd.read_csv(csv_path, nrows=1)
    sig_cols = [c for c in df_head.columns if c.endswith("_signal")]
    sig_names = sorted([c[:-7] for c in sig_cols])  # strip "_signal"
    return sig_names


def comb_to_dict(tri: Tuple[str, str, str]) -> Dict[str, float]:
    return {tri[0]: 1.0, tri[1]: 1.0, tri[2]: 1.0}


def timestamp_tag() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--rows", type=int, default=200000)
    ap.add_argument("--offsets", default="0")
    ap.add_argument("--direction", choices=["long", "short"], required=True)
    ap.add_argument("--fee", type=float, default=0.0, help="roi_fee = roi - fee * num_trades")
    ap.add_argument("--apply_regime_gate", action="store_true")
    ap.add_argument("--regime_col", default=None)
    ap.add_argument("--max_strategies", type=int, default=200, help="Smoke limit (first N combos, deterministic)")
    args = ap.parse_args()

    rr = repo_root()
    simtraderGS = import_simtrader_gs()

    csv_path = args.csv
    rows = int(args.rows)
    offsets = parse_offsets(args.offsets)
    direction = args.direction
    fee = float(args.fee)
    apply_rg = bool(args.apply_regime_gate)
    regime_col = args.regime_col

    # Enforce GS naming and folder scheme
    out_dir = os.path.join(rr, "results", "GS", f"k3_{direction}")
    os.makedirs(out_dir, exist_ok=True)

    print("REPO_ROOT:", rr)
    print("CSV:", csv_path)
    print("ROWS(per window):", rows)
    print("OFFSETS:", offsets)
    print("DIRECTION:", direction)
    print("FEE(roundtrip):", fee)
    print("REGIME_GATE:", "ON" if apply_rg else "OFF", "col=" + (regime_col if regime_col else "(auto)"))
    print("OUT_DIR:", out_dir)
    print("")

    sigs = discover_signals(csv_path)
    if len(sigs) < 3:
        raise RuntimeError("Need at least 3 *_signal columns in CSV to run K3.")

    all_triplets = list(combinations(sigs, 3))
    all_triplets = sorted(all_triplets)
    triplets = all_triplets[: max(0, int(args.max_strategies))]

    print("SIGNALS_FOUND:", len(sigs))
    print("K3_TRIPLETS_TOTAL:", len(all_triplets))
    print("K3_TRIPLETS_SMOKE:", len(triplets))
    print("")

    windows: List[Tuple[int, pd.DataFrame]] = []
    for off in offsets:
        df = read_window(csv_path, off, rows)
        df_g = apply_gate(df, direction, apply_rg, regime_col)
        windows.append((off, df_g))
        print(f"WINDOW offset={off} post_rows={len(df_g)}")

    print("")

    results: List[Dict[str, Any]] = []

    with EnvVar(ENV_FEE_KEY, "0"):
        for idx, tri in enumerate(triplets, start=1):
            comb = comb_to_dict(tri)

            roi_fee_list: List[float] = []
            trades_list: List[int] = []
            per_win: Dict[str, Any] = {}

            for off, wdf in windows:
                if wdf.empty:
                    roi_fee = 0.0
                    trades = 0
                else:
                    res = simtraderGS.evaluate_strategy(wdf, comb, direction)
                    roi = float(res.get("roi", 0.0))
                    trades = int(res.get("num_trades", 0))
                    roi_fee = roi - fee * trades

                roi_fee_list.append(roi_fee)
                trades_list.append(trades)
                per_win[f"roi_fee_off_{off}"] = roi_fee
                per_win[f"trades_off_{off}"] = trades

            row: Dict[str, Any] = {
                "engine": "simtraderGS",
                "k": 3,
                "direction": direction,
                "roi_fee_mean": sum(roi_fee_list) / float(len(roi_fee_list)),
                "trades_sum": int(sum(trades_list)),
                "signals": ",".join(tri),
                "combination": json.dumps(comb, sort_keys=True),
            }
            row.update(per_win)
            results.append(row)

            if idx % 25 == 0 or idx == len(triplets):
                pct = 100.0 * idx / float(len(triplets))
                print(f"PROGRESS {idx}/{len(triplets)} ({pct:.1f}%)")

    tag = timestamp_tag()
    out_name = f"strategy_results_GS_k3_{direction}_SMOKE_{tag}.csv"
    out_path = os.path.join(out_dir, out_name)

    pd.DataFrame(results).to_csv(out_path, index=False)

    print("")
    print("OK WROTE:", out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


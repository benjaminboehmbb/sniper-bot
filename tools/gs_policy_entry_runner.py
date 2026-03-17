import argparse
import ast
import os
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

# =========================
# Defaults (GS contract)
# =========================

DEFAULT_TP = 0.04
DEFAULT_SL = 0.02
DEFAULT_MAX_HOLD = 1440
DEFAULT_ENTER_Z = 1.0
DEFAULT_EXIT_Z = 0.0

ENV_FEE_KEY = "SIMTRADERGS_FEE_ROUNDTRIP"
_MISSING = object()


# =========================
# Helpers
# =========================

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


def get_nested(d: Dict[str, Any], path: List[str]) -> Any:
    cur: Any = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return _MISSING
        cur = cur[k]
    return cur


def set_nested(d: Dict[str, Any], path: List[str], value: Any) -> None:
    cur: Any = d
    for k in path[:-1]:
        if k not in cur or not isinstance(cur[k], dict):
            cur[k] = {}
        cur = cur[k]
    cur[path[-1]] = value


def del_nested(d: Dict[str, Any], path: List[str]) -> None:
    cur: Any = d
    for k in path[:-1]:
        if not isinstance(cur, dict) or k not in cur:
            return
        cur = cur[k]
    if isinstance(cur, dict):
        cur.pop(path[-1], None)


class CfgOverride:
    """
    Temporarily override simtraderGS._CFG and restore afterwards.
    """
    def __init__(self, simtraderGS, overrides: Dict[Tuple[str, ...], Any]):
        self.simtraderGS = simtraderGS
        self.overrides = overrides
        self.prev: Dict[Tuple[str, ...], Any] = {}

    def __enter__(self):
        cfg = getattr(self.simtraderGS, "_CFG", None)
        if not isinstance(cfg, dict):
            raise RuntimeError("simtraderGS._CFG missing or not a dict")

        for path, val in self.overrides.items():
            self.prev[path] = get_nested(cfg, list(path))
            set_nested(cfg, list(path), val)
        return self

    def __exit__(self, exc_type, exc, tb):
        cfg = getattr(self.simtraderGS, "_CFG", None)
        if isinstance(cfg, dict):
            for path, old in self.prev.items():
                if old is _MISSING:
                    del_nested(cfg, list(path))
                else:
                    set_nested(cfg, list(path), old)
        return False


@dataclass
class EvalOut:
    roi_gross: float
    roi_fee: float
    trades: int


# =========================
# Parsing
# =========================

def parse_offsets(s: str) -> List[int]:
    return [int(x.strip()) for x in s.split(",") if x.strip()]


def parse_grid(s: Optional[str]) -> Optional[List[float]]:
    if not s:
        return None
    return [float(x.strip()) for x in s.split(",") if x.strip()]


def parse_comb(s: str) -> Any:
    return ast.literal_eval(s)


# =========================
# Data
# =========================

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


def apply_gate(df: pd.DataFrame, direction: str,
               apply_regime_gate: bool, regime_col: Optional[str]) -> pd.DataFrame:
    if not apply_regime_gate or df.empty:
        return df

    if "allow_long" in df.columns and "allow_short" in df.columns:
        return df[df["allow_long"] == 1].copy() if direction == "long" \
            else df[df["allow_short"] == 1].copy()

    col = regime_col or "regime_v1"
    if col not in df.columns:
        return df

    return df[df[col] == (1 if direction == "long" else -1)].copy()


# =========================
# Evaluation
# =========================

def eval_one(simtraderGS, df: pd.DataFrame, comb: Any, direction: str,
             fee: float, tp: float, sl: float, max_hold: int,
             enter_z: float, exit_z: float) -> EvalOut:

    overrides = {
        ("strategy", "risk", "take_profit_pct"): tp,
        ("strategy", "risk", "stop_loss_pct"): sl,
        ("strategy", "max_hold_bars"): max_hold,
        ("strategy", "enter_z"): enter_z,
        ("strategy", "exit_z"): exit_z,
    }

    with EnvVar(ENV_FEE_KEY, "0"), CfgOverride(simtraderGS, overrides):
        res = simtraderGS.evaluate_strategy(df, comb, direction)

    roi = float(res.get("roi", 0.0))
    trades = int(res.get("num_trades", 0))
    roi_fee = roi - fee * trades
    return EvalOut(roi, roi_fee, trades)


# =========================
# Runner
# =========================

def run_policy(csv_path: str, offsets: List[int], rows: int, direction: str,
               fee: float, comb: Any, apply_regime_gate: bool,
               regime_col: Optional[str], enter_z: float, exit_z: float):

    simtraderGS = import_simtrader_gs()

    print(f"REPO_ROOT: {repo_root()}")
    print(f"CSV: {csv_path}")
    print(f"OFFSETS: {offsets}")
    print(f"DIRECTION: {direction}")
    print(f"FEE(roundtrip): {fee}")
    print(f"COMB: {comb}")
    print(f"REGIME_GATE: {'ON' if apply_regime_gate else 'OFF'}")
    print("")
    print(f"DEFAULTS: enter_z={DEFAULT_ENTER_Z} exit_z={DEFAULT_EXIT_Z}")
    print(f"POLICY  : enter_z={enter_z} exit_z={exit_z}")
    print("")

    for off in offsets:
        df = read_window(csv_path, off, rows)
        df = apply_gate(df, direction, apply_regime_gate, regime_col)

        d = eval_one(simtraderGS, df, comb, direction, fee,
                     DEFAULT_TP, DEFAULT_SL, DEFAULT_MAX_HOLD,
                     DEFAULT_ENTER_Z, DEFAULT_EXIT_Z)

        p = eval_one(simtraderGS, df, comb, direction, fee,
                     DEFAULT_TP, DEFAULT_SL, DEFAULT_MAX_HOLD,
                     enter_z, exit_z)

        print(
            f"WF offset={off} post_rows={len(df)} "
            f"default_roi={d.roi_fee:.6f} policy_roi={p.roi_fee:.6f} "
            f"default_trades={d.trades} policy_trades={p.trades}"
        )


# =========================
# Main
# =========================

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--rows", type=int, default=200_000)
    ap.add_argument("--offsets", default="0")
    ap.add_argument("--direction", required=True, choices=["long", "short"])
    ap.add_argument("--fee", type=float, default=0.0)
    ap.add_argument("--comb", required=True)

    ap.add_argument("--apply_regime_gate", action="store_true")
    ap.add_argument("--regime_col", default=None)

    ap.add_argument("--enter_z_grid", default=None)
    ap.add_argument("--exit_z_grid", default=None)

    args = ap.parse_args()

    offsets = parse_offsets(args.offsets)
    comb = parse_comb(args.comb)

    ez_grid = parse_grid(args.enter_z_grid) or [DEFAULT_ENTER_Z]
    xz_grid = parse_grid(args.exit_z_grid) or [DEFAULT_EXIT_Z]

    for ez in ez_grid:
        for xz in xz_grid:
            print("=" * 60)
            print(f"GRID: enter_z={ez} exit_z={xz}")
            run_policy(
                csv_path=args.csv,
                offsets=offsets,
                rows=args.rows,
                direction=args.direction,
                fee=args.fee,
                comb=comb,
                apply_regime_gate=args.apply_regime_gate,
                regime_col=args.regime_col,
                enter_z=ez,
                exit_z=xz,
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


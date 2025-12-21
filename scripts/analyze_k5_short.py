# scripts/analyze_k5_short.py
# ASCII-only. Minimal smoke-test analyzer for K5 SHORT candidates.

import argparse
import csv
import json
import sys
import inspect
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def utc_now_str():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def log(msg: str):
    print(f"[{utc_now_str()} UTC] {msg}", flush=True)


def ensure_parent_dir(path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def load_candidates(path: str) -> list[dict]:
    df = pd.read_csv(path)
    if "Combination" not in df.columns:
        raise ValueError("Candidates CSV must contain column 'Combination'")
    return [json.loads(s) for s in df["Combination"].astype(str).tolist()]


def try_import_evaluator():
    tried = []

    try:
        from engine.simtrader import evaluate_strategy  # type: ignore
        return evaluate_strategy, "engine.simtrader.evaluate_strategy"
    except Exception as e:
        tried.append(f"engine.simtrader.evaluate_strategy: {e}")

    try:
        from engine.simtrader2 import evaluate_strategy  # type: ignore
        return evaluate_strategy, "engine.simtrader2.evaluate_strategy"
    except Exception as e:
        tried.append(f"engine.simtrader2.evaluate_strategy: {e}")

    try:
        import simtrader  # type: ignore
        if hasattr(simtrader, "evaluate_strategy"):
            return simtrader.evaluate_strategy, "simtrader.evaluate_strategy"
    except Exception as e:
        tried.append(f"simtrader.evaluate_strategy: {e}")

    raise ImportError("Could not import evaluator. Tried:\n  - " + "\n  - ".join(tried))


def call_evaluate_strategy(fn, i: int, combo: dict, direction: str) -> dict:
    """
    Robustly call evaluate_strategy across different signatures seen in this repo.

    Current confirmed signature (engine/simtrader.py):
      evaluate_strategy(i: int, comb: Any, direction: str, df: pd.DataFrame | None = None)

    Other historical variants may exist; we handle them defensively.
    """
    sig = None
    params = {}
    try:
        sig = inspect.signature(fn)
        params = sig.parameters
    except Exception:
        params = {}

    # Preferred: explicit i + comb + direction
    if "i" in params and "comb" in params and "direction" in params:
        return fn(i=i, comb=combo, direction=direction)  # type: ignore

    # Sometimes "strategy" instead of "comb"
    if "i" in params and "strategy" in params and "direction" in params:
        return fn(i=i, strategy=combo, direction=direction)  # type: ignore

    # If function expects comb + direction (no i)
    if "comb" in params and "direction" in params:
        return fn(comb=combo, direction=direction)  # type: ignore
    if "strategy" in params and "direction" in params:
        return fn(strategy=combo, direction=direction)  # type: ignore

    # Side instead of direction
    if "i" in params and "comb" in params and "side" in params:
        return fn(i=i, comb=combo, side=direction)  # type: ignore
    if "comb" in params and "side" in params:
        return fn(comb=combo, side=direction)  # type: ignore

    # Positional fallbacks (most likely: (i, comb, direction))
    try:
        return fn(i, combo, direction)  # type: ignore
    except TypeError:
        pass
    try:
        return fn(combo, direction)  # type: ignore
    except TypeError:
        pass
    try:
        return fn(combo, side=direction)  # type: ignore
    except TypeError:
        pass

    raise TypeError(f"Unsupported evaluate_strategy signature: {sig}")


def normalize_result(res: dict) -> dict:
    def pick(*keys, default=None):
        for k in keys:
            if k in res:
                return res[k]
        return default

    roi = pick("roi", "roi_total", "roi_pct", "total_roi")
    winrate = pick("winrate", "accuracy", "hit_rate")
    num_trades = pick("num_trades", "trades", "n_trades")
    pnl_sum = pick("pnl_sum", "pnl", "profit", "net_profit", default=roi)

    return {
        "roi": float(roi) if roi is not None else float("nan"),
        "winrate": float(winrate) if winrate is not None else float("nan"),
        "num_trades": int(num_trades) if num_trades is not None else 0,
        "pnl_sum": float(pnl_sum) if pnl_sum is not None else float("nan"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--side", default="short", choices=["short"])
    ap.add_argument("--batch-write", type=int, default=1000)
    args = ap.parse_args()

    log(f"Repo root on sys.path: {REPO_ROOT}")
    log(f"Loading candidates: {args.candidates}")
    combos = load_candidates(args.candidates)
    log(f"Candidates loaded: {len(combos)}")

    fn, name = try_import_evaluator()
    log(f"Using {name}")

    ensure_parent_dir(args.out)

    out_fields = ["Combination", "roi", "winrate", "num_trades", "pnl_sum"]
    wrote_header = False
    buf = []
    errors = []

    for i, combo in enumerate(combos, 1):
        try:
            res = call_evaluate_strategy(fn, i=i, combo=combo, direction="short")
            if not isinstance(res, dict):
                raise TypeError("evaluate_strategy returned non-dict")
            row = {"Combination": json.dumps(combo, separators=(",", ":"))}
            row.update(normalize_result(res))
            buf.append(row)
        except Exception as e:
            errors.append((i, str(e)))
            buf.append({
                "Combination": json.dumps(combo, separators=(",", ":")),
                "roi": float("nan"),
                "winrate": float("nan"),
                "num_trades": 0,
                "pnl_sum": float("nan"),
            })

        if (i % args.batch_write) == 0 or i == len(combos):
            mode = "w" if not wrote_header else "a"
            with open(args.out, mode, newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=out_fields)
                if not wrote_header:
                    w.writeheader()
                    wrote_header = True
                w.writerows(buf)
            buf = []
            log(f"Progress {i}/{len(combos)} wrote {args.out}")

    if errors:
        log(f"Errors: {len(errors)} (showing up to 10)")
        for idx, msg in errors[:10]:
            log(f"  idx={idx} err={msg}")

    log("Done.")
    log(f"Wrote results to: {args.out}")


if __name__ == "__main__":
    main()



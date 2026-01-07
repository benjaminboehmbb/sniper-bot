# analyze_k5_short.py
# K5 SHORT Regime analyzer (MP, batch writes, no tqdm, ASCII-only).
# Supports --input-glob with shell-independent glob expansion (like K5-long).
# Robust evaluator import and signature mapping (df/comb/direction/i/etc.).
# Injects project root into sys.path for engine imports.

import argparse
import ast
import csv
import glob
import importlib
import inspect
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import multiprocessing as mp


def utc_now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def utc_ts_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")


def ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)


def backup_if_exists(path: str) -> Optional[str]:
    if os.path.exists(path) and os.path.isfile(path):
        base, ext = os.path.splitext(path)
        bkp = f"{base}_backup_{utc_ts_compact()}{ext}"
        os.rename(path, bkp)
        return bkp
    return None


def expand_input_globs(glob_expr: str) -> List[str]:
    patterns = [p.strip() for p in glob_expr.split(";") if p.strip()]
    paths: List[str] = []
    for pat in patterns:
        matches = sorted(glob.glob(pat))
        if matches:
            paths.extend(matches)
        elif os.path.isfile(pat):
            paths.append(pat)
    seen = set()
    out = []
    for p in paths:
        if p not in seen:
            out.append(p)
            seen.add(p)
    return out


def load_strategies(paths: List[str], column: str, limit: int = 0) -> List[Dict[str, float]]:
    out: List[Dict[str, float]] = []
    for p in paths:
        with open(p, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if column not in reader.fieldnames:
                raise ValueError(f"Input file '{p}' missing column '{column}'. Found: {reader.fieldnames}")
            for row in reader:
                raw = (row.get(column) or "").strip()
                if not raw:
                    continue
                try:
                    d = json.loads(raw)
                except Exception:
                    d = ast.literal_eval(raw)
                if not isinstance(d, dict):
                    continue
                combo: Dict[str, float] = {}
                for k, v in d.items():
                    combo[str(k)] = float(v)
                out.append(combo)
                if limit > 0 and len(out) >= limit:
                    return out
    return out


def inject_project_root_into_syspath() -> str:
    here = os.path.abspath(__file__)
    scripts_dir = os.path.dirname(here)
    project_root = os.path.abspath(os.path.join(scripts_dir, ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    print(f"[{utc_now_str()}] Repo root on sys.path: {project_root}")
    return project_root


def _pick_callable_from_module(mod: Any) -> Optional[Tuple[str, Any]]:
    for name in ["evaluate_strategy", "evaluate", "run_strategy", "score_strategy"]:
        fn = getattr(mod, name, None)
        if callable(fn):
            return name, fn
    return None


def _pick_simtrader_class(mod: Any) -> Optional[Tuple[str, Any]]:
    cls = getattr(mod, "SimTrader", None)
    if cls is None:
        return None
    if not inspect.isclass(cls):
        return None
    return "SimTrader", cls


def try_import_evaluator() -> Tuple[str, str]:
    modules = ["engine.simtrader", "engine.simtrader2", "simtrader", "simtrader2"]
    last_errors: List[str] = []
    for mod_name in modules:
        try:
            mod = importlib.import_module(mod_name)
            picked = _pick_callable_from_module(mod)
            if picked is not None:
                fn_name, _ = picked
                return "func", f"{mod_name}.{fn_name}"
            picked_cls = _pick_simtrader_class(mod)
            if picked_cls is not None:
                cls_name, _ = picked_cls
                return "class", f"{mod_name}.{cls_name}"
        except Exception as e:
            last_errors.append(f"{mod_name}: {type(e).__name__}: {str(e)}")
    raise ImportError(
        "Could not import evaluator from engine.simtrader/engine.simtrader2/simtrader/simtrader2.\n"
        + "\n".join(last_errors[:10])
    )


def _to_dict(res: Any) -> Dict[str, Any]:
    if isinstance(res, dict):
        return dict(res)
    if hasattr(res, "__dict__"):
        d = dict(res.__dict__)
        if d:
            return d
    if isinstance(res, (list, tuple)):
        return {"result": res}
    return {"result": res}


def _call_func_by_signature(fn: Any, i: int, strategy: Dict[str, float], df: pd.DataFrame, side: str, use_regime: int) -> Any:
    try:
        sig = inspect.signature(fn)
        params = list(sig.parameters.values())
    except Exception:
        return fn(df, strategy, side, i)

    args: List[Any] = []
    kwargs: Dict[str, Any] = {}
    has_varkw = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params)

    def map_value(pname: str) -> Tuple[bool, Any]:
        n = pname.lower()
        if n in ("i", "idx", "index"):
            return True, int(i)
        if n in ("df", "data", "price_df", "prices", "price_data", "price_data_df"):
            return True, df
        if n in ("comb", "combo", "combination", "strategy", "weights", "signal_weights"):
            return True, strategy
        if n in ("direction", "side", "mode"):
            return True, side
        if n in ("use_regime", "regime"):
            return True, int(use_regime)
        return False, None

    for p in params:
        if p.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue
        ok, val = map_value(p.name)
        if ok:
            if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                args.append(val)
            else:
                kwargs[p.name] = val
        else:
            if p.default is inspect._empty and not has_varkw:
                raise TypeError(f"Cannot map required evaluator param '{p.name}'")

    if has_varkw:
        kwargs.setdefault("i", int(i))
        kwargs.setdefault("df", df)
        kwargs.setdefault("comb", strategy)
        kwargs.setdefault("direction", side)
        kwargs.setdefault("use_regime", int(use_regime))

    return fn(*args, **kwargs)


def _call_class_method_by_signature(meth: Any, i: int, strategy: Dict[str, float], side: str, use_regime: int) -> Any:
    try:
        sig = inspect.signature(meth)
        params = list(sig.parameters.values())
    except Exception:
        return meth(strategy)

    args: List[Any] = []
    kwargs: Dict[str, Any] = {}
    has_varkw = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params)

    def map_value(pname: str) -> Tuple[bool, Any]:
        n = pname.lower()
        if n in ("i", "idx", "index"):
            return True, int(i)
        if n in ("comb", "combo", "combination", "strategy", "weights", "signal_weights"):
            return True, strategy
        if n in ("direction", "side", "mode"):
            return True, side
        if n in ("use_regime", "regime"):
            return True, int(use_regime)
        return False, None

    for p in params:
        if p.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue
        ok, val = map_value(p.name)
        if ok:
            if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                args.append(val)
            else:
                kwargs[p.name] = val
        else:
            if p.default is inspect._empty and not has_varkw:
                raise TypeError(f"Cannot map required evaluator param '{p.name}'")

    if has_varkw:
        kwargs.setdefault("i", int(i))
        kwargs.setdefault("comb", strategy)
        kwargs.setdefault("direction", side)
        kwargs.setdefault("use_regime", int(use_regime))

    return meth(*args, **kwargs)


def call_evaluator(evaluator: Any, evaluator_kind: str, i: int, strategy: Dict[str, float], df: pd.DataFrame, side: str, use_regime: int) -> Dict[str, Any]:
    if evaluator_kind == "func":
        res = _call_func_by_signature(evaluator, i, strategy, df, side, use_regime)
        return _to_dict(res)
    if evaluator_kind == "class":
        st = evaluator
        for meth_name in ["evaluate_strategy", "evaluate", "run_strategy", "score_strategy"]:
            meth = getattr(st, meth_name, None)
            if callable(meth):
                res = _call_class_method_by_signature(meth, i, strategy, side, use_regime)
                return _to_dict(res)
        raise RuntimeError("SimTrader instance found, but no usable evaluate method found.")
    raise RuntimeError(f"Unknown evaluator kind: {evaluator_kind}")


def normalize_metrics(d: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    out["roi"] = d.get("roi", d.get("ROI", None))
    out["winrate"] = d.get("winrate", d.get("accuracy", d.get("hit_rate", None)))
    out["num_trades"] = d.get("num_trades", d.get("trades", d.get("n_trades", None)))
    out["profit_factor"] = d.get("profit_factor", None)
    out["sharpe"] = d.get("sharpe", d.get("sharpe_ratio", None))
    out["max_drawdown"] = d.get("max_drawdown", d.get("mdd", None))
    out["avg_trade"] = d.get("avg_trade", None)
    out["avg_win"] = d.get("avg_win", None)
    out["avg_loss"] = d.get("avg_loss", None)
    out["pnl"] = d.get("pnl", None)
    return out


def dict_to_json_sorted(d: Dict[str, float]) -> str:
    return json.dumps({k: float(v) for k, v in sorted(d.items())}, separators=(",", ":"))


_G_DF = None
_G_EVAL = None
_G_EVAL_KIND = None
_G_SIDE = None
_G_USE_REGIME = None


def _init_worker(price_csv: str, eval_kind: str, eval_source: str, side: str, use_regime: int) -> None:
    global _G_DF, _G_EVAL, _G_EVAL_KIND, _G_SIDE, _G_USE_REGIME
    _G_DF = pd.read_csv(price_csv)

    mod_name, obj_name = eval_source.rsplit(".", 1)
    mod = importlib.import_module(mod_name)

    if eval_kind == "func":
        _G_EVAL = getattr(mod, obj_name)
        _G_EVAL_KIND = "func"
    elif eval_kind == "class":
        cls = getattr(mod, obj_name)
        inst = None
        try:
            inst = cls(df=_G_DF)
        except Exception:
            try:
                inst = cls(data=_G_DF)
            except Exception:
                try:
                    inst = cls(price_df=_G_DF)
                except Exception:
                    try:
                        inst = cls(_G_DF)
                    except Exception:
                        inst = cls()
        _G_EVAL = inst
        _G_EVAL_KIND = "class"
    else:
        raise RuntimeError(f"Unknown eval_kind: {eval_kind}")

    _G_SIDE = side
    _G_USE_REGIME = int(use_regime)


def _worker(item: Tuple[int, Dict[str, float]]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    global _G_DF, _G_EVAL, _G_EVAL_KIND, _G_SIDE, _G_USE_REGIME
    i, strategy = item
    try:
        res = call_evaluator(_G_EVAL, _G_EVAL_KIND, i, strategy, _G_DF, _G_SIDE, _G_USE_REGIME)
        metrics = normalize_metrics(res)
        metrics["Combination"] = dict_to_json_sorted(strategy)
        return metrics, None
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)}"


def write_batch_csv(path: str, rows: List[Dict[str, Any]], fieldnames: List[str], write_header_if_new: bool) -> None:
    ensure_parent_dir(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header_if_new:
            w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, None) for k in fieldnames})


def main() -> None:
    inject_project_root_into_syspath()

    ap = argparse.ArgumentParser()
    ap.add_argument("--input-glob", required=True)
    ap.add_argument("--input-column", default="Combination")
    ap.add_argument("--price-csv", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--num-procs", type=int, default=12)
    ap.add_argument("--batch-write", type=int, default=5000)
    ap.add_argument("--progress-step", type=int, default=2)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--use-regime", type=int, default=1)
    args = ap.parse_args()

    input_paths = expand_input_globs(args.input_glob)
    if not input_paths:
        raise SystemExit(f"No input files found for --input-glob: {args.input_glob}")

    eval_kind, eval_source = try_import_evaluator()

    print(f"[{utc_now_str()}] Evaluator: {eval_source} (kind={eval_kind})")
    print(f"[{utc_now_str()}] Loading strategies...")
    strategies = load_strategies(input_paths, args.input_column, limit=args.limit)
    n = len(strategies)
    if n == 0:
        raise SystemExit("No strategies loaded.")

    indexed_items = list(enumerate(strategies))

    ensure_parent_dir(args.out)
    bkp = backup_if_exists(args.out)
    if bkp:
        print(f"[{utc_now_str()}] Existing output backed up to: {bkp}")

    fieldnames = ["Combination", "roi", "winrate", "num_trades", "profit_factor", "sharpe", "max_drawdown", "avg_trade", "avg_win", "avg_loss", "pnl"]

    print(f"[{utc_now_str()}] Strategies loaded: {n}")
    print(f"[{utc_now_str()}] Starting multiprocessing: num_procs={args.num_procs}, batch_write={args.batch_write}")

    t0 = time.time()
    last_print_pct = -1

    error_counts: Dict[str, int] = {}
    error_examples: List[str] = []

    ctx = mp.get_context("spawn")
    pool = ctx.Pool(
        processes=args.num_procs,
        initializer=_init_worker,
        initargs=(args.price_csv, eval_kind, eval_source, "short", int(args.use_regime)),
        maxtasksperchild=2000,
    )

    wrote_header = False
    batch: List[Dict[str, Any]] = []
    done = 0

    try:
        for metrics, err in pool.imap_unordered(_worker, indexed_items, chunksize=200):
            done += 1

            if err:
                error_counts[err] = error_counts.get(err, 0) + 1
                if len(error_examples) < 15:
                    error_examples.append(err)
            else:
                batch.append({k: metrics.get(k, None) for k in fieldnames})

            pct = int((done * 100) / n)
            if args.progress_step > 0 and pct != last_print_pct and (pct % args.progress_step == 0 or done == n):
                elapsed = time.time() - t0
                rate = done / elapsed if elapsed > 0 else 0.0
                eta = (n - done) / rate if rate > 0 else 0.0
                print(f"[{utc_now_str()}] Progress: {pct}% ({done}/{n}) elapsed={int(elapsed)}s eta={int(eta)}s")
                last_print_pct = pct

            if len(batch) >= args.batch_write:
                write_batch_csv(args.out, batch, fieldnames, write_header_if_new=not wrote_header)
                wrote_header = True
                batch = []

        if batch:
            write_batch_csv(args.out, batch, fieldnames, write_header_if_new=not wrote_header)

    finally:
        pool.close()
        pool.join()

    elapsed = time.time() - t0
    print(f"[{utc_now_str()}] Done. Elapsed: {int(elapsed)}s")
    print(f"[{utc_now_str()}] Output: {args.out}")

    if error_counts:
        print(f"[{utc_now_str()}] Errors encountered (aggregated): {len(error_counts)} unique")
        top = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for msg, cnt in top:
            print(f"  {cnt}x  {msg}")
        if error_examples:
            print(f"[{utc_now_str()}] Error examples (up to 15):")
            for ex in error_examples:
                print(f"  - {ex}")


if __name__ == "__main__":
    try:
        import locale
        locale.setlocale(locale.LC_ALL, "C")
    except Exception:
        pass
    main()




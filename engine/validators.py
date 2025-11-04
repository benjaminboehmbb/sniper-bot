# engine/validators.py
# ASCII only. Preflight checks for price and strategy CSVs.
# Usage:
#   python -m engine.validators --price data/price/price_data_with_signals.csv --strategies data/strategies/k3/strategies_k3_shard1.csv
#   python -m engine.validators --price data/price/price_data_with_signals.csv --strategies-glob "data/strategies/k3/strategies_k3_*.csv"

import argparse
import csv
import glob
import os
import sys

REQUIRED_PRICE_COLS_ANY = [
    # we accept either open_time or timestamp as the time column
    ["open_time"],
    ["timestamp"],
]
REQUIRED_PRICE_COLS_ALL = [
    "open", "high", "low", "close", "volume"
]

# minimal set of known signal columns is flexible; we only warn if none present
KNOWN_SIGNAL_PREFIXES = [
    "rsi", "macd", "bollinger", "ma200", "stoch", "atr",
    "ema50", "adx", "cci", "mfi", "obv", "roc",
    # allow both raw and *_signal style
    "rsi_signal", "macd_signal", "bollinger_signal", "ma200_signal",
    "stoch_signal", "atr_signal", "ema50_signal", "adx_signal",
    "cci_signal", "mfi_signal", "obv_signal", "roc_signal",
]

# strategies file must have a column named Combination containing a dict-like string
REQUIRED_STRATEGY_COL = "Combination"

def _read_header(path):
    with open(path, "r", newline="") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            raise RuntimeError(f"Empty CSV: {path}")
    return [h.strip() for h in header]

def _file_exists(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

def _has_any_required_group(header, groups):
    for group in groups:
        if all(col in header for col in group):
            return True
    return False

def _warn(msg):
    sys.stderr.write("[WARN] " + msg + "\n")

def _info(msg):
    sys.stdout.write("[INFO] " + msg + "\n")

def validate_price_csv(price_path):
    _file_exists(price_path)
    header = _read_header(price_path)

    # time column
    if not _has_any_required_group(header, REQUIRED_PRICE_COLS_ANY):
        raise RuntimeError(
            f"Missing time column. Expected one of: {REQUIRED_PRICE_COLS_ANY}. File: {price_path}"
        )
    time_col = "open_time" if "open_time" in header else "timestamp"

    # ohlcv
    missing_all = [c for c in REQUIRED_PRICE_COLS_ALL if c not in header]
    if missing_all:
        raise RuntimeError(
            f"Missing required OHLCV columns: {missing_all}. File: {price_path}"
        )

    # signals presence (soft check)
    has_any_signal = any(any(h.startswith(pfx) for h in header) for pfx in KNOWN_SIGNAL_PREFIXES)
    if not has_any_signal:
        _warn("No known signal columns detected. Proceeding, but simulations may produce no trades.")

    _info(f"Price CSV OK. Time column: {time_col}. Columns: {len(header)}")
    return {"time_col": time_col, "columns": header}

def validate_strategy_csv(strategy_path):
    _file_exists(strategy_path)
    header = _read_header(strategy_path)

    if REQUIRED_STRATEGY_COL not in header:
        # common historical pitfall: column named 'strategy' instead of 'Combination'
        if "strategy" in header:
            raise RuntimeError(
                f"Column mismatch. Found 'strategy' but expected '{REQUIRED_STRATEGY_COL}'. "
                f"Please rename the column in: {strategy_path}"
            )
        raise RuntimeError(
            f"Missing required column '{REQUIRED_STRATEGY_COL}' in: {strategy_path}"
        )

    _info(f"Strategies CSV OK: {strategy_path}")
    return {"columns": header}

def main():
    ap = argparse.ArgumentParser(description="Preflight validators for price and strategy CSVs")
    ap.add_argument("--price", type=str, required=True, help="Path to price CSV")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--strategies", type=str, help="Path to a single strategies CSV")
    g.add_argument("--strategies-glob", type=str, help="Glob for multiple strategies CSVs")

    args = ap.parse_args()

    price_res = validate_price_csv(args.price)

    strategy_files = []
    if args.strategies:
        strategy_files = [args.strategies]
    else:
        strategy_files = sorted(glob.glob(args.strategies_glob))

    if not strategy_files:
        raise RuntimeError("No strategies files found.")

    ok_count = 0
    for sp in strategy_files:
        try:
            validate_strategy_csv(sp)
            ok_count += 1
        except Exception as e:
            sys.stderr.write(f"[ERROR] {sp}: {e}\n")
    _info(f"Validated strategies: {ok_count}/{len(strategy_files)} OK")

    # hard fail if any missing, to stop the pipeline early
    if ok_count != len(strategy_files):
        raise SystemExit(2)

    _info("Preflight checks passed.")

if __name__ == "__main__":
    main()

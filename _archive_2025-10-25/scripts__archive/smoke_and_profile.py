# scripts/smoke_and_profile.py
# Zweck:
#  - Sanity-Checks: Config/CSV/Spalten/Imports
#  - Mini-Durchlauf (z.B. 200 Strategien) zum Profiling
#  - Report mit ops/sec, per-strategy ms, ETA-Formel
# Nutzung:
#    python -m scripts.smoke_and_profile data/strategies_5er.csv --n 200

import os, sys, time, json, yaml, traceback, ast
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CFG_PATH = os.path.join(ROOT, "configs", "base_config.yaml")
OUT_DIR = os.path.join(ROOT, "out")
os.makedirs(OUT_DIR, exist_ok=True)

# ---- helpers ----
def load_cfg():
    try:
        with open(CFG_PATH, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
        return cfg
    except Exception as e:
        print("WARN: konnte Config nicht laden:", e)
        return {}

def ok(b, msg):
    print(("✅ " if b else "❌ ") + msg)

def require(b, msg):
    ok(b, msg)
    if not b:
        sys.exit(2)

def parse_args():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("strategies_csv", help="Pfad zur Strategien-CSV (z.B. data/strategies_5er.csv)")
    ap.add_argument("--n", type=int, default=200, help="Anzahl Strategien zum Profiling (nur Messung)")
    return ap.parse_args()

# ---- main ----
def main():
    args = parse_args()
    cfg = load_cfg()

    # config basics
    data_cfg = cfg.get("data", {}) if isinstance(cfg, dict) else {}
    csv_path = data_cfg.get("csv_path") or data_cfg.get("price_csv") or "data/btcusdt_1m_spot.csv"
    full_price = csv_path if os.path.isabs(csv_path) else os.path.join(ROOT, csv_path)
    require(os.path.isfile(full_price), f"Preis-CSV vorhanden: {full_price}")

    # price columns check
    dfp = pd.read_csv(full_price, nrows=1000)
    need_cols = ["close","high","low"]
    rename_map = {c.capitalize(): c for c in need_cols}
    for c in need_cols:
        if c not in dfp.columns and c.capitalize() in dfp.columns:
            dfp.rename(columns={c.capitalize(): c}, inplace=True)
    missing = [c for c in need_cols if c not in dfp.columns]
    require(len(missing)==0, f"Preis-CSV enthält Pflichtspalten {need_cols}")

    # strategies csv
    strat_path = args.strategies_csv if os.path.isabs(args.strategies_csv) else os.path.join(ROOT, args.strategies_csv)
    require(os.path.isfile(strat_path), f"Strategien-CSV vorhanden: {strat_path}")
    ds = pd.read_csv(strat_path)
    comb_col = "Combination" if "Combination" in ds.columns else ("combination" if "combination" in ds.columns else None)
    require(comb_col is not None, "Spalte 'Combination' (oder 'combination') existiert")

    # evaluate import
    try:
        from scripts.evaluate_strategy import evaluate_strategy
        ok(True, "evaluate_strategy importierbar")
    except Exception as e:
        ok(False, f"evaluate_strategy Import-Fehler: {e}")
        sys.exit(2)

    # prepare sample
    n = min(args.n, len(ds))
    sample = ds.head(n).copy()

    # warmup
    try:
        _ = evaluate_strategy(0, sample.iloc[0][comb_col], "short")
        ok(True, "Warmup erfolgreich (evaluate_strategy)")
    except Exception as e:
        ok(False, f"Warmup-Fehler: {e}")
        traceback.print_exc()
        sys.exit(2)

    # time loop
    t0 = time.perf_counter()
    ok_count = 0
    err_count = 0
    for i, row in sample.iterrows():
        try:
            _ = evaluate_strategy(int(i), row[comb_col], "short")
            ok_count += 1
        except Exception:
            err_count += 1
    dt = time.perf_counter() - t0
    ops = ok_count / dt if dt > 0 else 0.0
    ms_per = (dt / max(ok_count,1)) * 1000

    print("\n--- Profiling ---")
    print(f"Strategien gemessen: {ok_count} OK, {err_count} Fehler")
    print(f"Zeit: {dt:.2f} s  |  Throughput: {ops:.2f} strategies/s  |  ~{ms_per:.2f} ms/strategy")

    # ETA formula (for your own numbers later)
    print("\nETA-Formel (Faustregel):  ETA [s] ≈ (N_strategien / strategies_per_second)")
    report = {
        "strategies_csv": os.path.relpath(strat_path, ROOT),
        "price_csv": os.path.relpath(full_price, ROOT),
        "measured_n": ok_count,
        "seconds": dt,
        "strategies_per_second": ops,
        "ms_per_strategy": ms_per,
        "errors": err_count,
        "timestamp": pd.Timestamp.now().isoformat()
    }
    out_json = os.path.join(OUT_DIR, "smoke_profile_report.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport gespeichert: {os.path.relpath(out_json, ROOT)}")

if __name__ == "__main__":
    main()

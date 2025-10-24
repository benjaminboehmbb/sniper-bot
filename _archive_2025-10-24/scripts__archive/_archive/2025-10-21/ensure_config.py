# scripts/ensure_config.py
# Vollständiges Auto-Fix für configs/base_config.yaml
# - Backup der Originaldatei
# - Ergänzt fehlende Keys, ohne vorhandene Werte zu überschreiben
# - Fügt nun auch 'strategy.direction_modes' hinzu (erwartet von analyze_template.py)
# - Ende: gibt kurze Status-Meldung aus

import os, sys, shutil, datetime
from typing import Any, Dict

try:
    import yaml
except ImportError:
    print("PyYAML fehlt im venv. Bitte: pip install pyyaml")
    sys.exit(2)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CFG_DIR = os.path.join(ROOT, "configs")
CFG_PATH = os.path.join(CFG_DIR, "base_config.yaml")

REQUIRED_DEFAULTS: Dict[str, Any] = {
    "project": {"name": "sniper-bot", "author": "benjamin", "version": "0.1"},
    "general": {"results_dir": "out", "tmp_dir": "tmp", "seed": 42},
    "data": {
        # both keys provided: price_csv (older) and csv_path (expected by some scripts)
        "price_csv": "data/btcusdt_1m_spot.csv",
        "csv_path": "data/btcusdt_1m_spot.csv",
        "timeframe": "1m",
        "max_rows": None,
        "timestamp_col": "open_time",
        "timezone": "UTC",
    },
    "runtime": {
        "timezone": "Europe/Berlin",
        "save_trades": True,
        "verbose": True,
    },
    "strategy": {
        "mode": "short",
        "min_hold_bars": 1,
        "max_hold_bars": 1440,
        "risk": {"stop_loss_pct": 0.02, "take_profit_pct": 0.04},
        # direction_modes erwartet von analyze_template.py
        "direction_modes": ["long", "short", "both"],
    },
    "signals": {
        # Default available signals
        "available": ["rsi", "macd", "bollinger", "ma200", "stoch", "atr", "ema50"],
        # Default weights: historische Default (0.0,0.5,1.0)
        "weights": [0.0, 0.5, 1.0],
        "params": {
            "rsi": {"period": 14, "overbought": 70, "oversold": 30},
            "macd": {"fast": 12, "slow": 26, "signal": 9},
            "bollinger": {"period": 20, "stddev": 2},
            "ma200": {"period": 200},
            "stoch": {"k": 14, "d": 3},
            "atr": {"period": 14},
            "ema50": {"period": 50},
        },
    },
    "filters": {"min_volume": 0, "require_regime": True, "regime_type": "short_fix"},
    "output": {
        "results_dir": "out",
        "strategy_results_csv": "out/strategy_results.csv",
        "save_trade_history": True,
    },
    "logging": {"level": "INFO", "progress_step": 1},
}

def deep_merge(dst: Dict[str, Any], src: Dict[str, Any]) -> Dict[str, Any]:
    for k, v in src.items():
        if k not in dst:
            dst[k] = v
        else:
            if isinstance(dst[k], dict) and isinstance(v, dict):
                deep_merge(dst[k], v)
            # vorhandene nicht-dict Werte respektieren
    return dst

def ensure_signals(cfg: Dict[str, Any]) -> None:
    sigs = cfg.setdefault("signals", {})
    # available
    if "available" not in sigs or not isinstance(sigs.get("available"), list) or len(sigs.get("available")) == 0:
        params = sigs.get("params", {})
        if isinstance(params, dict) and params:
            sigs["available"] = sorted(list(params.keys()))
        else:
            sigs["available"] = REQUIRED_DEFAULTS["signals"]["available"]
    # weights
    if "weights" not in sigs or not isinstance(sigs.get("weights"), list) or len(sigs.get("weights")) == 0:
        sigs["weights"] = REQUIRED_DEFAULTS["signals"]["weights"]
    # ensure params exist
    if "params" not in sigs or not isinstance(sigs.get("params"), dict):
        sigs["params"] = REQUIRED_DEFAULTS["signals"]["params"]

def ensure_data(cfg: Dict[str, Any]) -> None:
    data = cfg.setdefault("data", {})
    # if csv_path missing but price_csv exists, copy to csv_path
    if "csv_path" not in data and "price_csv" in data:
        data["csv_path"] = data["price_csv"]
    # if price_csv missing but csv_path exists, copy to price_csv
    if "price_csv" not in data and "csv_path" in data:
        data["price_csv"] = data["csv_path"]
    # fill other defaults
    for k, v in REQUIRED_DEFAULTS["data"].items():
        data.setdefault(k, v)

def ensure_strategy(cfg: Dict[str, Any]) -> None:
    strat = cfg.setdefault("strategy", {})
    # ensure direction_modes (expected by analyze_template)
    if "direction_modes" not in strat or not isinstance(strat.get("direction_modes"), list):
        strat["direction_modes"] = REQUIRED_DEFAULTS["strategy"]["direction_modes"]
    # keep 'mode' if present; else set default
    strat.setdefault("mode", REQUIRED_DEFAULTS["strategy"]["mode"])
    strat.setdefault("min_hold_bars", REQUIRED_DEFAULTS["strategy"]["min_hold_bars"])
    strat.setdefault("max_hold_bars", REQUIRED_DEFAULTS["strategy"]["max_hold_bars"])
    strat.setdefault("risk", REQUIRED_DEFAULTS["strategy"]["risk"])

def ensure_required(cfg: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(cfg, dict):
        cfg = {}
    # Merge defaults (only missing keys are added)
    fixed = deep_merge(cfg, {})
    deep_merge(fixed, REQUIRED_DEFAULTS)
    # Ensure signals and data consistency
    ensure_signals(fixed)
    ensure_data(fixed)
    ensure_strategy(fixed)
    return fixed

def main():
    os.makedirs(CFG_DIR, exist_ok=True)
    if not os.path.isfile(CFG_PATH):
        print(f"Fehlt: {CFG_PATH}. Lege neue Standarddatei an.")
        with open(CFG_PATH, "w", encoding="utf-8") as f:
            yaml.safe_dump(REQUIRED_DEFAULTS, f, sort_keys=False)
        print("Neu erstellt:", CFG_PATH)
        sys.exit(0)

    # Backup original
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_dir = os.path.join(CFG_DIR, "_backup")
    os.makedirs(backup_dir, exist_ok=True)
    backup_path = os.path.join(backup_dir, f"base_config.yaml.bak_{ts}")
    shutil.copy2(CFG_PATH, backup_path)

    # Load original (safely)
    try:
        with open(CFG_PATH, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
    except Exception as e:
        print("Konnte YAML nicht laden:", e)
        print("Original gesichert unter:", backup_path)
        print("Erstelle saubere Default-Datei.")
        with open(CFG_PATH, "w", encoding="utf-8") as f:
            yaml.safe_dump(REQUIRED_DEFAULTS, f, sort_keys=False)
        sys.exit(0)

    if raw is None:
        raw = {}

    fixed = ensure_required(raw)

    # Write back
    with open(CFG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(fixed, f, sort_keys=False)

    # Report
    print("✅ ensure_config: ausgeführt")
    print("Backup der Originaldatei:", backup_path)
    print("Aktuelle keys (kurz):")
    print(" - signals.available =", fixed["signals"]["available"])
    print(" - signals.weights   =", fixed["signals"]["weights"])
    print(" - data.csv_path     =", fixed["data"]["csv_path"])
    print(" - data.price_csv    =", fixed["data"]["price_csv"])
    print(" - general.results_dir =", fixed["general"]["results_dir"])
    print(" - strategy.direction_modes =", fixed["strategy"].get("direction_modes"))
    sys.exit(0)

if __name__ == '__main__':
    main()



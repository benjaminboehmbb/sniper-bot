# scripts/evaluate_strategy.py
# Delegiert an simtrader-Implementierung, sonst klarer Fehlerhinweis.
# Lädt Kursdaten 1x aus CFG, falls dein simtrader eine DataFrame braucht.

import os, yaml, pandas as pd, ast, traceback

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CFG_PATH = os.path.join(ROOT, "configs", "base_config.yaml")

def _load_cfg():
    try:
        with open(CFG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}

_CFG = _load_cfg()
_DATA = None

def _csv_path():
    d = _CFG.get("data", {}) if isinstance(_CFG, dict) else {}
    return d.get("csv_path") or d.get("price_csv") or "data/btcusdt_1m_spot.csv"

def _get_df():
    global _DATA
    if _DATA is None:
        path = _csv_path()
        full = path if os.path.isabs(path) else os.path.join(ROOT, path)
        _DATA = pd.read_csv(full)
    return _DATA

def _try_delegate(i, comb, direction):
    # Versuche gängige Varianten:
    # 1) Funktion evaluate_strategy(i, comb, direction)
    # 2) Klasse SimTrader mit Methoden evaluate(...) oder run_strategy(...)
    # 3) Funktion evaluate_strategy(i, comb, direction, df=...)
    candidates = [
        ("scripts.simtrader", "evaluate_strategy"),
        ("simtrader", "evaluate_strategy"),
        ("scripts.simtrader", "SimTrader"),
        ("simtrader", "SimTrader"),
    ]
    for mod_name, attr in candidates:
        try:
            mod = __import__(mod_name, fromlist=[attr])
            if hasattr(mod, attr):
                obj = getattr(mod, attr)
                if callable(obj):
                    try:
                        # Variante ohne df
                        return obj(i, comb, direction)
                    except TypeError:
                        # Variante mit df-Kwarg versuchen
                        return obj(i, comb, direction, df=_get_df())
                else:
                    # Klasse
                    inst = obj()
                    if hasattr(inst, "evaluate") and callable(inst.evaluate):
                        try:
                            return inst.evaluate(i, comb, direction)
                        except TypeError:
                            return inst.evaluate(i, comb, direction, df=_get_df())
                    if hasattr(inst, "run_strategy") and callable(inst.run_strategy):
                        try:
                            return inst.run_strategy(i, comb, direction)
                        except TypeError:
                            return inst.run_strategy(i, comb, direction, df=_get_df())
        except Exception:
            continue
    return None

def evaluate_strategy(i, comb_str, direction):
    try:
        comb = ast.literal_eval(comb_str) if isinstance(comb_str, str) else comb_str
    except Exception:
        comb = comb_str

    res = _try_delegate(i, comb, direction)
    if res is None:
        raise RuntimeError(
            "Keine passende simtrader-Implementierung gefunden. "
            "Erwarte z.B. scripts/simtrader.py mit def evaluate_strategy(i, comb, direction, df=None) "
            "oder eine Klasse SimTrader mit .evaluate(...)"
        )
    return res


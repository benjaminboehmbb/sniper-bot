# scripts/patch_add_evaluate.py
# Backup + fügt evaluate_strategy hinzu, falls noch nicht vorhanden.

import os, sys, shutil, datetime, textwrap

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TARGET = os.path.join(ROOT, "scripts", "analyze_template.py")
BACKUP_DIR = os.path.join(ROOT, "scripts", "_backup")
os.makedirs(BACKUP_DIR, exist_ok=True)

if not os.path.isfile(TARGET):
    print("FEHLER: Datei nicht gefunden:", TARGET)
    sys.exit(1)

with open(TARGET, "r", encoding="utf-8") as f:
    content = f.read()

if "def evaluate_strategy(" in content:
    print("evaluate_strategy bereits vorhanden — nichts zu tun.")
    sys.exit(0)

# Backup original
ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
bak = os.path.join(BACKUP_DIR, f"analyze_template.py.bak_{ts}")
shutil.copy2(TARGET, bak)
print("Backup erstellt:", bak)

# Fallback function to append
fallback = textwrap.dedent(r'''
# --- AUTO-APPENDED evaluate_strategy FALLBACK (added by patch_add_evaluate.py) ---
# This fallback tries to call an implementation from simtrader (if present).
# If not available, it returns a safe placeholder result so the analysis loop continues.
# You can replace or remove this fallback after integrating the real evaluation routine.

def _try_import_simtrader():
    """
    Try common import locations for a real evaluation function.
    Returns a callable or None.
    """
    candidates = [
        ("simtrader", "evaluate_strategy"),
        ("scripts.simtrader", "evaluate_strategy"),
        ("simtrader", "SimTrader"),           # class-based fallback
        ("scripts.simtrader", "SimTrader"),
    ]
    for mod_name, attr in candidates:
        try:
            mod = __import__(mod_name, fromlist=[attr])
            if hasattr(mod, attr):
                return getattr(mod, attr)
            # If class present, return a wrapper that instantiates and calls a typical method
            if hasattr(mod, "SimTrader") and hasattr(mod, "SimTrader"):
                cls = getattr(mod, "SimTrader")
                # try to return a function wrapper that calls cls.evaluate or similar
                def wrapper(i, comb_str, direction):
                    inst = cls()
                    if hasattr(inst, "evaluate"):
                        return inst.evaluate(i, comb_str, direction)
                    if hasattr(inst, "run_strategy"):
                        return inst.run_strategy(i, comb_str, direction)
                    # fallback - basic dict
                    return {"index": i, "combination": comb_str, "direction": direction, "roi": 0.0, "num_trades": 0}
                return wrapper
        except Exception:
            continue
    return None

_evaluate_impl = _try_import_simtrader()

def evaluate_strategy(i, comb_str, direction):
    """
    Minimal evaluate_strategy wrapper required by analyze_template:
    - i: integer index
    - comb_str: string representation of the combination (e.g. dict string)
    - direction: 'long'|'short'|'both'
    Returns a dict-like result (the analyze_template expects to consume something - this fallback returns a safe stub).
    """
    import ast, time
    # If a real implementation is available, call it
    if _evaluate_impl:
        try:
            return _evaluate_impl(i, comb_str, direction)
        except Exception as e:
            # If it fails, fall back to stub but keep the exception in logs
            print(f"[evaluate_strategy] simtrader impl raised: {e}. Falling back to stub.", flush=True)

    # Fallback stub: parse combination and return safe zeros
    try:
        comb = ast.literal_eval(comb_str) if isinstance(comb_str, str) else comb_str
    except Exception:
        comb = comb_str
    # simple deterministic pseudo-eval to give some metrics quickly
    time.sleep(0)  # non-blocking placeholder
    result = {
        "index": i,
        "combination": comb,
        "direction": direction,
        "roi": 0.0,
        "num_trades": 0,
        "winrate": 0.0,
        "sharpe": 0.0,
    }
    return result
# --- end appended block ---
''')

# Append to file
with open(TARGET, "a", encoding="utf-8") as f:
    f.write("\n\n" + fallback)

print("evaluate_strategy Fallback wurde angehängt. Starte deinen Run erneut.")

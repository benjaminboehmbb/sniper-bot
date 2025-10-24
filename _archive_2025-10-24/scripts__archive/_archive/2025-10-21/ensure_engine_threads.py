# scripts/ensure_engine_threads.py
# Fügt configs/base_config.yaml -> engine.processes hinzu (falls fehlt)
# Backup wird automatisch erstellt.

import os, sys, shutil, datetime
try:
    import yaml
except ImportError:
    print("PyYAML fehlt. Bitte im venv: pip install pyyaml")
    sys.exit(2)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CFG = os.path.join(ROOT, "configs", "base_config.yaml")
BACKUP_DIR = os.path.join(ROOT, "configs", "_backup")
DEFAULT_PROCESSES = 28  # Ziel: ~28–32 (wie du vorher wolltest)

def backup(path):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dst = os.path.join(BACKUP_DIR, f"base_config.yaml.bak_{ts}")
    shutil.copy2(path, dst)
    return dst

if not os.path.isfile(CFG):
    print("configs/base_config.yaml fehlt. Erstelle Default mit engine.processes =", DEFAULT_PROCESSES)
    os.makedirs(os.path.dirname(CFG), exist_ok=True)
    default = {
        "engine": {"processes": DEFAULT_PROCESSES}
    }
    with open(CFG, "w", encoding="utf-8") as f:
        yaml.safe_dump(default, f, sort_keys=False)
    print("Erstellt:", CFG)
    sys.exit(0)

# load
with open(CFG, "r", encoding="utf-8") as f:
    try:
        cfg = yaml.safe_load(f) or {}
    except Exception as e:
        print("Konnte YAML nicht laden:", e)
        print("Bitte sichere die Datei manuell.")
        sys.exit(1)

# backup
bak = backup(CFG)

# ensure engine dict
engine = cfg.setdefault("engine", {})
if "processes" in engine:
    print(f"engine.processes bereits gesetzt: {engine['processes']} (keine Änderung).")
else:
    engine["processes"] = DEFAULT_PROCESSES
    with open(CFG, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)
    print("✅ engine.processes gesetzt auf", DEFAULT_PROCESSES)

print("Backup deiner Originaldatei: ", bak)

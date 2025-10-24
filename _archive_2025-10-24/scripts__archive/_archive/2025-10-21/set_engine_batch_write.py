# scripts/set_engine_batch_write.py
# Setzt configs/base_config.yaml -> engine.batch_write = 5000 falls fehlt (mit Backup)

import os, sys, shutil, datetime, yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CFG = os.path.join(ROOT, "configs", "base_config.yaml")
BACKUP_DIR = os.path.join(ROOT, "configs", "_backup")
os.makedirs(BACKUP_DIR, exist_ok=True)

if not os.path.isfile(CFG):
    print("FEHLER: configs/base_config.yaml nicht gefunden:", CFG)
    sys.exit(1)

# Backup
ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
bak = os.path.join(BACKUP_DIR, f"base_config.yaml.bak_{ts}")
shutil.copy2(CFG, bak)
print("Backup gespeichert:", bak)

# Load
with open(CFG, "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f) or {}

# Ensure engine block
engine = cfg.setdefault("engine", {})

if "batch_write" not in engine:
    engine["batch_write"] = 5000
    print("Setze engine.batch_write = 5000")
else:
    print("engine.batch_write bereits vorhanden =", engine["batch_write"])

# ensure processes exists (safety)
if "processes" not in engine:
    engine["processes"] = 16
    print("Setze engine.processes = 16 (Fallback)")
else:
    print("engine.processes =", engine["processes"])

# write back
with open(CFG, "w", encoding="utf-8") as f:
    yaml.safe_dump(cfg, f, sort_keys=False)

print("configs/base_config.yaml aktualisiert.")

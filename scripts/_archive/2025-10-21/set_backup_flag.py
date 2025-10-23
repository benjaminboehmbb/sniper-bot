# scripts/set_backup_flag.py
# Setzt configs/base_config.yaml -> general.backup_existing_results = True (mit Backup)

import os, yaml, shutil, datetime, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
P = os.path.join(ROOT, "configs", "base_config.yaml")
BAK_DIR = os.path.join(ROOT, "configs", "_backup")
os.makedirs(BAK_DIR, exist_ok=True)

if not os.path.isfile(P):
    print("Fehler: configs/base_config.yaml existiert nicht:", P)
    sys.exit(1)

# Backup
ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
shutil.copy2(P, os.path.join(BAK_DIR, f"base_config.yaml.bak_{ts}"))

# Load, set flag, write back
with open(P, "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f) or {}

gen = cfg.setdefault("general", {})
if "backup_existing_results" not in gen:
    gen["backup_existing_results"] = True
    print("Setze general.backup_existing_results = True")
else:
    print("general.backup_existing_results already present =", gen["backup_existing_results"])

with open(P, "w", encoding="utf-8") as f:
    yaml.safe_dump(cfg, f, sort_keys=False)
print("Backup gespeichert. Datei aktualisiert:", P)

# scripts/ensure_eval_import.py
# Ensures `from scripts.evaluate_strategy import evaluate_strategy` is imported
# at top of scripts/analyze_template.py. Makes a backup first.

import os, sys, shutil, datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TARGET = os.path.join(ROOT, "scripts", "analyze_template.py")
BACKUP_DIR = os.path.join(ROOT, "scripts", "_backup")
os.makedirs(BACKUP_DIR, exist_ok=True)

IMPORT_LINE = "from scripts.evaluate_strategy import evaluate_strategy"

if not os.path.isfile(TARGET):
    print("ERROR: target not found:", TARGET)
    sys.exit(1)

# Read file
with open(TARGET, "r", encoding="utf-8") as f:
    txt = f.read()

# If import already present, done
if IMPORT_LINE in txt:
    print("Import already present in analyze_template.py — nothing to do.")
    sys.exit(0)

# Backup
ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
bak = os.path.join(BACKUP_DIR, f"analyze_template.py.bak_{ts}")
shutil.copy2(TARGET, bak)
print("Backup created:", bak)

# Insert import after any initial #! or encoding lines and before other imports
lines = txt.splitlines()
insert_at = 0
# skip shebang or empty lines or comments at top
while insert_at < len(lines) and (lines[insert_at].strip().startswith("#!") or lines[insert_at].strip().startswith("#") or lines[insert_at].strip() == ""):
    insert_at += 1

# Also skip initial docstring if present
if insert_at < len(lines) and lines[insert_at].strip().startswith('"""'):
    # find closing docstring
    insert_at += 1
    while insert_at < len(lines) and '"""' not in lines[insert_at]:
        insert_at += 1
    insert_at += 1

# Insert the import line at insert_at
lines.insert(insert_at, IMPORT_LINE)

# Write back
with open(TARGET, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print("Inserted import line into analyze_template.py at line", insert_at+1)
print("Please run your analysis again.")

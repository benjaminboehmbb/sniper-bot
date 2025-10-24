# scripts/patch_unpack_future.py
# Backup + ersetzt "status, out = fut.result()" durch robusten Unpack-Code

import os, sys, shutil, datetime, re, textwrap

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TARGET = os.path.join(ROOT, "scripts", "analyze_template.py")
BACKUP_DIR = os.path.join(ROOT, "scripts", "_backup")
os.makedirs(BACKUP_DIR, exist_ok=True)

if not os.path.isfile(TARGET):
    print("FEHLER: Datei nicht gefunden:", TARGET)
    sys.exit(1)

# Backup original
ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
bak = os.path.join(BACKUP_DIR, f"analyze_template.py.bak_{ts}")
shutil.copy2(TARGET, bak)
print("Backup erstellt:", bak)

with open(TARGET, "r", encoding="utf-8") as f:
    src = f.read()

pattern = r"status\s*,\s*out\s*=\s*fut\.result\s*\(\s*\)"
if not re.search(pattern, src):
    print("Muster 'status, out = fut.result()' nicht gefunden. Datei nicht verändert.")
    sys.exit(0)

replacement = textwrap.dedent(r'''
# robustes Unpackieren von möglichen Future-Resultaten (ersetzt status, out = fut.result())
_res = None
try:
    _res = fut.result()
except Exception as _e:
    # Futur-Exception — markiere als error und logge
    print(f"[ERROR] future raised exception: {_e}", flush=True)
    status = "error"
    out = None
else:
    # falls es bereits ein (status, out) tuple ist, benutze es
    if isinstance(_res, tuple) and len(_res) >= 2:
        try:
            status, out = _res[0], _res[1]
        except Exception:
            status = "error"
            out = None
    # falls ein dict oder sonstiges Objekt: interpretiere als successful result
    elif isinstance(_res, dict) or not isinstance(_res, (list, tuple)):
        status = "ok"
        out = _res
    # falls list/tuple mit nur einem element
    elif isinstance(_res, (list, tuple)) and len(_res) == 1:
        status = "ok"
        out = _res[0]
    else:
        # Fallback
        status = "ok"
        out = _res
''')

# Do the replacement (first occurrence)
new_src = re.sub(pattern, replacement, src, count=1)

with open(TARGET, "w", encoding="utf-8") as f:
    f.write(new_src)

print("Patch angewendet: robustes Unpack eingefügt in analyze_template.py")
print("Starte jetzt deinen Run erneut (generate_combinations -> analyze_template).")

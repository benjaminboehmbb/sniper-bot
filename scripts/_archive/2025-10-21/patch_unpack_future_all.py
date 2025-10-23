# scripts/patch_unpack_future_all.py
# Robust patch: ersetzt verschiedene Formen von "status, out = fut.result(...)" durch sichere, fehlertolerante Variante.
# Macht Backup in scripts/_backup/.

import os, re, shutil, datetime, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TARGET = os.path.join(ROOT, "scripts", "analyze_template.py")
BACKUP_DIR = os.path.join(ROOT, "scripts", "_backup")
os.makedirs(BACKUP_DIR, exist_ok=True)

if not os.path.isfile(TARGET):
    print("FEHLER: Ziel nicht gefunden:", TARGET)
    sys.exit(1)

# Backup
ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
bak = os.path.join(BACKUP_DIR, f"analyze_template.py.bak_{ts}")
shutil.copy2(TARGET, bak)
print("Backup erstellt:", bak)

with open(TARGET, "r", encoding="utf-8") as f:
    src = f.read()

# Patterns to find (multiple common whitespace / timeout variants)
patterns = [
    r"status\s*,\s*out\s*=\s*fut\.result\s*\(\s*\)",
    r"status\s*,\s*out\s*=\s*fut\.result\s*\(\s*timeout\s*=\s*[^\)]*\)",
    r"status\s*,\s*out\s*=\s*fut\.result\s*\([^\)]*\)",   # generic inside ()
    r"status\s*,\s*out\s*=\s*fut\.result",                # defensively handle no-parens (unlikely)
    r"status\s*,\s*out\s*=\s*fut\.result\s*\([^)]*?\)\s*#.*", # with inline comment
    # also possible no-space variant
    r"status\s*,\s*out\s*=\s*fut\.result\s*\([^\)]*?\)",
]

# A robust replacement block (keeps indentation of original line)
replacement_block = r"""_res = None
try:
    _res = fut.result()
except Exception as _e:
    print(f"[ERROR] future raised exception: {_e}", flush=True)
    status = "error"
    out = None
else:
    if isinstance(_res, tuple) and len(_res) >= 2:
        try:
            status, out = _res[0], _res[1]
        except Exception:
            status = "error"
            out = None
    elif isinstance(_res, dict) or not isinstance(_res, (list, tuple)):
        status = "ok"
        out = _res
    elif isinstance(_res, (list, tuple)) and len(_res) == 1:
        status = "ok"
        out = _res[0]
    else:
        status = "ok"
        out = _res
"""

# We will attempt replacement preserving indentation:
def replace_all(src_text):
    new = src_text
    count_total = 0
    for pat in patterns:
        # find all occurrences
        for m in re.finditer(pat, new):
            span = m.span()
            # Determine indentation by scanning backward to the line start
            line_start = new.rfind("\n", 0, span[0]) + 1
            indent = new[line_start:span[0]]
            # compute indent characters (spaces or tabs at beginning of match)
            indent_ws = ""
            for ch in indent:
                if ch in (" ", "\t"):
                    indent_ws += ch
                else:
                    indent_ws = ""
            # build indented replacement
            indented_block = "\n".join(indent_ws + line for line in replacement_block.splitlines())
            # perform single replacement at first occurrence of this match text
            new = new[:span[0]] + indented_block + new[span[1]:]
            count_total += 1
            # restart search for this pattern because text changed
            break
    return new, count_total

new_src, replaced = replace_all(src)

if replaced == 0:
    print("Keine passende Zuweisung gefunden ('status, out = fut.result(...)'). Datei unverändert.")
    print("Wenn der Fehler weiter besteht, bitte kompletten Traceback hierher kopieren.")
else:
    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(new_src)
    print(f"Patch angewendet: {replaced} Ersetzungen durchgeführt in {TARGET}")
    print("Bitte führe jetzt erneut deinen Run aus (generate_combinations -> analyze_template).")

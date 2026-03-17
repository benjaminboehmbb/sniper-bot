#!/usr/bin/env python3
# tools/fix_5m_short_seeds_add_dir.py
#
# Purpose:
#   In-place fix for 5m SHORT timing seeds:
#   Adds {"dir": "short"} into each row's comb_json dict (if missing),
#   so timing_5m can emit direction=short deterministically.
#
# Usage:
#   python3 tools/fix_5m_short_seeds_add_dir.py \
#     --csv seeds/5m/btcusdt_5m_short_timing_core_v1.csv
#
# Notes:
#   - Creates a backup рядом: <file>.bak
#   - ASCII-only output

from __future__ import annotations

import argparse
import ast
import csv
import os
import shutil
from typing import Any, Dict


def _load_dict(s: str) -> Dict[str, Any]:
    try:
        obj = ast.literal_eval(s)
    except Exception:
        return {}
    if not isinstance(obj, dict):
        return {}
    return obj


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="Path to SHORT seeds CSV (seed_id, comb_json)")
    args = ap.parse_args(argv)

    path = args.csv
    if not os.path.isfile(path):
        raise SystemExit("ERROR: file not found: {}".format(path))

    backup = path + ".bak"
    tmp = path + ".tmp"

    shutil.copy2(path, backup)

    rows_in = 0
    rows_out = 0
    rows_changed = 0

    with open(path, "r", newline="", encoding="utf-8") as f_in:
        r = csv.DictReader(f_in)
        if r.fieldnames is None:
            raise SystemExit("ERROR: CSV has no header: {}".format(path))

        # We keep the same columns (do not add new CSV columns)
        fieldnames = list(r.fieldnames)

        with open(tmp, "w", newline="", encoding="utf-8") as f_out:
            w = csv.DictWriter(f_out, fieldnames=fieldnames)
            w.writeheader()

            for row in r:
                rows_in += 1
                comb_raw = row.get("comb_json", "")
                d = _load_dict(comb_raw)

                before = d.get("dir", None) or d.get("direction", None)
                if isinstance(before, str) and before.strip().lower() in ("long", "short"):
                    # already has explicit direction
                    pass
                else:
                    # enforce short
                    d["dir"] = "short"
                    rows_changed += 1

                # write back as a deterministic python-literal dict string
                # keep simple ordering for readability (dir first if present)
                if "dir" in d:
                    dir_val = d["dir"]
                    rest = {k: d[k] for k in d.keys() if k != "dir"}
                    d_out = {"dir": dir_val}
                    d_out.update(rest)
                else:
                    d_out = d

                row["comb_json"] = str(d_out)
                w.writerow(row)
                rows_out += 1

    os.replace(tmp, path)

    print("OK: updated {}".format(path))
    print("backup: {}".format(backup))
    print("rows_in={} rows_out={} rows_changed={}".format(rows_in, rows_out, rows_changed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

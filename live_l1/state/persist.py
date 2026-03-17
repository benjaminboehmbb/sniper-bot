# live_l1/state/persist.py
#
# L1 Persistenz (Step 7/8)
# - Atomar (write temp + rename)
# - Append-only JSONL
# - Nur S2 und S4
#
# ASCII-only.

from __future__ import annotations

import json
import os
import tempfile
from typing import Dict, Any


def _atomic_append_jsonl(path: str, record: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    line = json.dumps(record, separators=(",", ":"), ensure_ascii=True)

    # Atomarer Append: temp file + append
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")
        fh.flush()
        os.fsync(fh.fileno())

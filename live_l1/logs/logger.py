# live_l1/logs/logger.py
#
# L1 Logging & Observability (verbindlich):
# - strukturierte Logs (key=value)
# - zeitlich monoton (UTC)
# - deterministische Reihenfolge
# - keine stillen Fehler
# - Pflichtfelder: timestamp_utc, category, event, severity, system_state_id, intent_id (falls vorhanden)
#
# Keine Performance/GS-Begriffe. ASCII-only.

from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any

# Deterministische, monotone-ish Sequenznummer (pro Prozess)
_SEQ = 0

_ALLOWED_SEVERITY = {"DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _kv_escape(v: Any) -> str:
    # key=value, spaces become underscores; keep ASCII-friendly output.
    if v is None:
        return ""
    s = str(v)
    s = s.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
    s = s.replace(" ", "_")
    return s


class L1Logger:
    def __init__(self, log_path: str):
        self.log_path = log_path
        self._fh = None

        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        self._fh = open(log_path, "a", encoding="utf-8", buffering=1)  # line-buffered

    def close(self) -> None:
        if self._fh:
            try:
                self._fh.flush()
            finally:
                self._fh.close()
                self._fh = None

    def log(
        self,
        *,
        category: str,
        event: str,
        severity: str,
        system_state_id: str,
        intent_id: Optional[str] = None,
        fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        global _SEQ
        _SEQ += 1

        sev = str(severity).upper().strip()
        if sev not in _ALLOWED_SEVERITY:
            sev = "INFO"

        ts = _utc_now_iso()

        # Pflichtfelder
        parts = [
            f"timestamp_utc={ts}",
            f"seq={_SEQ}",
            f"category={_kv_escape(category)}",
            f"event={_kv_escape(event)}",
            f"severity={sev}",
            f"system_state_id={_kv_escape(system_state_id)}",
        ]
        if intent_id is not None:
            parts.append(f"intent_id={_kv_escape(intent_id)}")

        if fields:
            # deterministic key order
            for k in sorted(fields.keys()):
                parts.append(f"{_kv_escape(k)}={_kv_escape(fields[k])}")

        line = " ".join(parts)

        # Append-only: file + stdout (no filtering)
        self._fh.write(line + "\n")
        sys.stdout.write(line + "\n")
        sys.stdout.flush()

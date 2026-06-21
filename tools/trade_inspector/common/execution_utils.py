#!/usr/bin/env python3
"""
Common execution-layer utilities for Trade Inspector V16.

Scope:
- CSV IO
- stable hashing
- row indexing
- safe integer parsing
- output summary writing

Guardrail:
This module contains only technical helpers.
It must not contain scientific decision, policy, execution, monitor, control,
or audit logic.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Tuple


def read_csv(path: Path) -> Tuple[List[Dict[str, str]], List[str]]:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [dict(row) for row in reader]
        fieldnames = list(reader.fieldnames or [])

    if not fieldnames:
        raise ValueError(f"Input file has no header: {path}")

    return rows, fieldnames


def write_csv(path: Path, rows: List[Dict[str, str]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def stable_hash(payload: Dict[str, object], prefix: str) -> str:
    normalized = json.dumps(payload, sort_keys=True, ensure_ascii=True)
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}-{digest}"


def index_by(rows: List[Dict[str, str]], key: str) -> Dict[str, Dict[str, str]]:
    indexed: Dict[str, Dict[str, str]] = {}
    for row in rows:
        value = row.get(key, "").strip()
        if value:
            indexed[value] = row
    return indexed


def safe_int(value: str, default: int) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

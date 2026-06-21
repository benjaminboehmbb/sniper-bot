#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Shared collection helpers for Trade Inspector scripts.

ASCII only.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def index_by(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        value = row.get(key, "")
        if value:
            out[str(value)] = row
    return out


def group_by(rows: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        value = row.get(key, "")
        if value:
            out[str(value)].append(row)
    return dict(out)


def count_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in rows:
        value = row.get(key, "")
        if value:
            value = str(value)
            out[value] = out.get(value, 0) + 1
    return out

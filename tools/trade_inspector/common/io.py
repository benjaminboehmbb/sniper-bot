"""CSV I/O helpers for Trade Inspector modules."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable


def read_csv(path: str | Path) -> list[dict[str, str]]:
    """Read a UTF-8 CSV file as a list of dictionaries.

    Missing files and header-only/empty files return an empty list.
    """
    p = Path(path)
    if not p.exists() or p.stat().st_size == 0:
        return []

    with p.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return []
        return [dict(row) for row in reader]


def write_csv(path: str | Path, rows: Iterable[dict], fieldnames: list[str]) -> None:
    """Write a UTF-8 CSV file.

    Always writes a header, even when rows is empty.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    with p.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

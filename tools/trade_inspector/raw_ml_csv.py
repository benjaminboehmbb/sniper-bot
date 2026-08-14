from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def export_ml_csv(rows: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError("No trades to export.")

    fieldnames = list(rows[0].keys())
    with output_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("ML CSV exported:", output_path)
    print("rows:", len(rows))

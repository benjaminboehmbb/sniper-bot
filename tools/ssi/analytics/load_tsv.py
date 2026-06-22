from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


class TSVLoadError(ValueError):
    pass


def load_tsv_rows(input_path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not input_path.exists():
        raise TSVLoadError(f"Input file does not exist: {input_path}")

    if not input_path.is_file():
        raise TSVLoadError(f"Input path is not a file: {input_path}")

    if input_path.stat().st_size <= 0:
        raise TSVLoadError(f"Input file is empty: {input_path}")

    with input_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames

        if header is None or len(header) == 0:
            raise TSVLoadError("Input CSV has no header")

        rows: list[dict[str, str]] = []
        for row in reader:
            rows.append(
                {
                    key: (value if value is not None else "")
                    for key, value in row.items()
                }
            )

    if len(rows) == 0:
        raise TSVLoadError("Input CSV has no data rows")

    return rows, list(header)


def require_columns(header: list[str], required_columns: list[str]) -> None:
    missing = [col for col in required_columns if col not in header]
    if missing:
        raise TSVLoadError("Missing required columns: " + ", ".join(missing))


def parse_float(value: Any) -> float | None:
    try:
        text = str(value).strip()
        if text == "":
            return None
        return float(text)
    except (TypeError, ValueError):
        return None
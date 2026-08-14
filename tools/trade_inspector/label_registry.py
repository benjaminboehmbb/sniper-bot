"""Human-label validation, registry persistence, and deterministic assignment."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

if __package__:
    from .inspection_primitives import safe_text
    from .regime_identity_rows import build_trade_id
else:
    from inspection_primitives import safe_text
    from regime_identity_rows import build_trade_id


__all__ = [
    "load_human_labels",
    "load_label_registry",
    "save_label_registry",
    "assign_human_labels",
]


def load_human_labels(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Missing human label list: {path}")

    labels: list[str] = []
    seen: set[str] = set()

    with path.open("r", encoding="utf-8") as fh:
        for raw in fh:
            label = raw.strip().lower()
            if not label or label.startswith("#"):
                continue
            if not label.isascii():
                raise ValueError(f"Non-ASCII label: {label}")
            if len(label) > 8:
                raise ValueError(f"Label too long: {label}")
            if " " in label:
                raise ValueError(f"Label contains space: {label}")
            if label in seen:
                raise ValueError(f"Duplicate label: {label}")
            seen.add(label)
            labels.append(label)

    if not labels:
        raise ValueError(f"No labels loaded from: {path}")

    return labels


def load_label_registry(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    registry: dict[str, str] = {}

    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            trade_id = safe_text(row.get("trade_id"))
            label = safe_text(row.get("human_label")).lower()
            if trade_id and label:
                registry[trade_id] = label

    return registry


def save_label_registry(path: Path, registry: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["trade_id", "human_label"])
        writer.writeheader()
        for trade_id in sorted(registry):
            writer.writerow({"trade_id": trade_id, "human_label": registry[trade_id]})


def assign_human_labels(
    trades: list[dict[str, Any]],
    label_list: list[str],
    registry: dict[str, str],
) -> dict[str, str]:
    used_labels = set(registry.values())

    if len(used_labels) != len(registry.values()):
        raise ValueError("Label registry contains duplicate labels.")

    available = [label for label in label_list if label not in used_labels]
    trade_ids = sorted({build_trade_id(trade) for trade in trades})

    assigned = dict(registry)

    for idx, trade_id in enumerate(trade_ids):
        if trade_id in assigned:
            continue
        if available:
            assigned[trade_id] = available.pop(0)
        else:
            assigned[trade_id] = f"auto_label_{len(assigned) + idx + 1:06d}"

    return assigned

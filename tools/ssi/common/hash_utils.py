from __future__ import annotations

import hashlib
from typing import Any


def normalize_hash_part(value: Any) -> str:
    if value is None:
        return "<NONE>"

    text = str(value).strip()
    if text == "":
        return "<EMPTY>"

    return text


def stable_hash(*parts: Any, length: int = 16) -> str:
    if length <= 0:
        raise ValueError("hash length must be > 0")

    normalized = [normalize_hash_part(part) for part in parts]
    payload = "|".join(normalized).encode("utf-8")

    digest = hashlib.sha256(payload).hexdigest()

    if length > len(digest):
        raise ValueError(f"hash length must be <= {len(digest)}")

    return digest[:length]


def build_tsv_id(
    *,
    runtime_id: str,
    trade_id: str | None,
    snapshot_id: str,
    timestamp_utc: str,
    tsv_version: str,
) -> str:
    return stable_hash(
        "TSV",
        runtime_id,
        trade_id,
        snapshot_id,
        timestamp_utc,
        tsv_version,
        length=24,
    )

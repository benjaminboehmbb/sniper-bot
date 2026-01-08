#!/usr/bin/env python3
"""
BTCUSDT 1m Bulk Downloader (Binance Spot) - Goldstandard Dataset

Dataset root:
  data/btcusdt_1m_2026-01-07

Source (official):
  - Monthly klines: data/spot/monthly/klines/BTCUSDT/1m/
  - Daily klines:   data/spot/daily/klines/BTCUSDT/1m/
  - Checksums:      <file>.zip.CHECKSUM (sha256)

Design:
  - Deterministic, reproducible download
  - Raw files stored unmodified
  - Monthly for full history; Daily for current-month gap up to yesterday (UTC)
  - Validates sha256 via .CHECKSUM when available
  - Safe re-run: skips files that already exist AND verify checksum (when available)

Notes:
  - Binance public data timestamps for SPOT from 2025-01-01 onwards may be in microseconds
    (relevant for later processing, not for raw download).
"""

from __future__ import annotations

import hashlib
import os
import sys
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Tuple


# -------------------------
# CONFIG (edit only if needed)
# -------------------------
SYMBOL = "BTCUSDT"
INTERVAL = "1m"

DATASET_ROOT = Path("data/btcusdt_1m_2026-01-07")
RAW_DIR = DATASET_ROOT / "raw"
RAW_MONTHLY_DIR = RAW_DIR / "monthly"
RAW_DAILY_DIR = RAW_DIR / "daily"
META_DIR = DATASET_ROOT / "meta"

BASE = "https://data.binance.vision/data/spot"
MONTHLY_PREFIX = f"{BASE}/monthly/klines/{SYMBOL}/{INTERVAL}"
DAILY_PREFIX = f"{BASE}/daily/klines/{SYMBOL}/{INTERVAL}"

# Earliest month for spot monthly klines is commonly available from 2017-08 (Binance public data).
# If you later want to hard-verify earliest availability, we can add a probing mode.
START_MONTH = (2017, 8)  # YYYY, MM


# -------------------------
# Helpers
# -------------------------
def utc_today() -> date:
    return datetime.now(timezone.utc).date()


def ym_iter(start_y: int, start_m: int, end_y: int, end_m: int):
    y, m = start_y, start_m
    while (y, m) <= (end_y, end_m):
        yield y, m
        m += 1
        if m == 13:
            m = 1
            y += 1


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def http_get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "sniper-bot-gs-downloader/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def download_to(url: str, out_path: Path, timeout: int = 120) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "sniper-bot-gs-downloader/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp, out_path.open("wb") as f:
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)


def parse_checksum_file(content: bytes) -> Optional[str]:
    """
    Binance .CHECKSUM files are typically like:
      <sha256>  <filename>
    We extract the first 64-hex token.
    """
    try:
        text = content.decode("utf-8", errors="replace").strip()
    except Exception:
        return None
    if not text:
        return None
    first = text.split()[0].strip()
    if len(first) == 64 and all(c in "0123456789abcdef" for c in first.lower()):
        return first.lower()
    return None


@dataclass
class Artifact:
    kind: str  # "monthly" or "daily"
    y: int
    m: int
    d: Optional[int] = None  # for daily

    @property
    def filename(self) -> str:
        if self.kind == "monthly":
            return f"{SYMBOL}-{INTERVAL}-{self.y:04d}-{self.m:02d}.zip"
        if self.kind == "daily":
            if self.d is None:
                raise ValueError("daily artifact requires day")
            return f"{SYMBOL}-{INTERVAL}-{self.y:04d}-{self.m:02d}-{self.d:02d}.zip"
        raise ValueError("unknown kind")

    @property
    def url(self) -> str:
        prefix = MONTHLY_PREFIX if self.kind == "monthly" else DAILY_PREFIX
        return f"{prefix}/{self.filename}"

    @property
    def checksum_url(self) -> str:
        return f"{self.url}.CHECKSUM"

    @property
    def out_path(self) -> Path:
        base = RAW_MONTHLY_DIR if self.kind == "monthly" else RAW_DAILY_DIR
        return base / self.filename


def verify_or_download(a: Artifact) -> Tuple[bool, str]:
    """
    Returns: (ok, message)
    ok=True means file exists and verified (when checksum exists), or downloaded and verified.
    """
    outp = a.out_path

    # Try to obtain checksum (may 404 for some items)
    checksum_hex = None
    try:
        checksum_hex = parse_checksum_file(http_get(a.checksum_url, timeout=30))
    except Exception:
        checksum_hex = None

    if outp.exists():
        if checksum_hex:
            got = sha256_file(outp)
            if got != checksum_hex:
                return False, f"[BAD] {a.kind} {a.filename}: checksum mismatch (local {got} != remote {checksum_hex})"
            return True, f"[OK]  {a.kind} {a.filename}: exists + checksum ok"
        return True, f"[OK]  {a.kind} {a.filename}: exists (no checksum available to verify)"

    # Download
    try:
        download_to(a.url, outp, timeout=180)
    except Exception as e:
        # If daily file not available (common), report clearly.
        return False, f"[MISS] {a.kind} {a.filename}: download failed ({e})"

    if checksum_hex:
        got = sha256_file(outp)
        if got != checksum_hex:
            return False, f"[BAD] {a.kind} {a.filename}: checksum mismatch after download (local {got} != remote {checksum_hex})"
        return True, f"[OK]  {a.kind} {a.filename}: downloaded + checksum ok"
    return True, f"[OK]  {a.kind} {a.filename}: downloaded (no checksum available to verify)"


def main() -> int:
    # Ensure dirs exist
    RAW_MONTHLY_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DAILY_DIR.mkdir(parents=True, exist_ok=True)
    META_DIR.mkdir(parents=True, exist_ok=True)

    today = utc_today()
    y, m = today.year, today.month

    # Monthly range: from START_MONTH through previous month (UTC)
    # Example: if today is 2026-01-07 -> last full month is 2025-12
    prev_month = (y, m - 1) if m > 1 else (y - 1, 12)

    print(f"[info] UTC today: {today.isoformat()}")
    print(f"[info] Monthly range: {START_MONTH[0]:04d}-{START_MONTH[1]:02d} .. {prev_month[0]:04d}-{prev_month[1]:02d}")
    print(f"[info] Daily range (gap-fill): {y:04d}-{m:02d}-01 .. { (today - timedelta(days=1)).isoformat() } (if available)")
    print("")

    ok_count = 0
    bad_count = 0
    miss_count = 0

    # 1) Monthly downloads
    for yy, mm in ym_iter(START_MONTH[0], START_MONTH[1], prev_month[0], prev_month[1]):
        a = Artifact(kind="monthly", y=yy, m=mm)
        ok, msg = verify_or_download(a)
        print(msg)
        if ok:
            ok_count += 1
        else:
            if msg.startswith("[MISS]"):
                miss_count += 1
            else:
                bad_count += 1

    print("")

    # 2) Daily gap-fill for current month up to yesterday
    start_day = date(y, m, 1)
    end_day = today - timedelta(days=1)
    if end_day >= start_day:
        cur = start_day
        while cur <= end_day:
            a = Artifact(kind="daily", y=cur.year, m=cur.month, d=cur.day)
            ok, msg = verify_or_download(a)
            # Daily availability historically starts later than monthly; missing is acceptable.
            print(msg)
            if ok:
                ok_count += 1
            else:
                if msg.startswith("[MISS]"):
                    miss_count += 1
                else:
                    bad_count += 1
            cur += timedelta(days=1)

    print("")
    print(f"[summary] ok={ok_count} bad={bad_count} missing={miss_count}")
    if bad_count > 0:
        print("[error] One or more files failed checksum verification. Do NOT continue to processing.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

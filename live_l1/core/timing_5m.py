#!/usr/bin/env python3
# live_l1/core/timing_5m.py
#
# Deterministic 5m Timing Core (v1 stub) for L1 Paper.
# ASCII-only.

from __future__ import annotations

import argparse
import csv
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from live_l1.core.intent_fusion import TimingVote


@dataclass(frozen=True)
class SeedRow:
    seed_id: str
    comb: Dict[str, float]
    direction: str  # long | short | none


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _normalize_direction(d: Optional[str]) -> str:
    if d is None:
        return "long"
    dd = str(d).strip().lower()
    if dd in ("long", "short", "none"):
        return dd
    if dd in ("l", "buy"):
        return "long"
    if dd in ("s", "sell"):
        return "short"
    return "long"


def _parse_comb_json(s: str) -> Dict[str, Any]:
    import ast

    if s is None:
        return {}
    s = str(s).strip()
    if not s:
        return {}
    try:
        obj = ast.literal_eval(s)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def _extract_dir_from_comb(raw: Dict[str, Any]) -> Optional[str]:
    for k in ("dir", "direction"):
        if k in raw:
            return str(raw.get(k)).strip()
    return None


def _weights_from_comb_raw(raw: Dict[str, Any]) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for k, v in raw.items():
        if k is None:
            continue
        kk = str(k)
        if kk in ("dir", "direction"):
            continue
        out[kk] = _safe_float(v, 0.0)
    return out


def _read_seeds_csv(path: str) -> List[SeedRow]:
    if not os.path.isfile(path):
        raise FileNotFoundError("seeds csv not found: {0}".format(path))

    rows: List[SeedRow] = []

    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            return []

        for line in reader:
            seed_id = str(line.get("seed_id", "")).strip()
            if not seed_id:
                continue

            comb_json = line.get("comb_json", "")

            dir_from_col = line.get("direction", None)
            direction = _normalize_direction(dir_from_col)

            raw = _parse_comb_json(comb_json)

            dir_from_comb = _extract_dir_from_comb(raw)
            if (dir_from_col is None or str(dir_from_col).strip() == "") and dir_from_comb is not None:
                direction = _normalize_direction(dir_from_comb)

            comb = _weights_from_comb_raw(raw)

            rows.append(
                SeedRow(
                    seed_id=seed_id,
                    comb=comb,
                    direction=direction,
                )
            )

    return rows


def _seed_score(seed: SeedRow) -> float:
    base = 0.0

    for _, w in seed.comb.items():
        base += _safe_float(w, 0.0)

    if seed.direction == "short":
        return -abs(base)

    if seed.direction == "none":
        return 0.0

    return abs(base)


def _strength_from_score(score: float) -> float:
    a = abs(_safe_float(score, 0.0))

    if a <= 0.0:
        return 0.0

    if a >= 1.0:
        return 1.0

    return a


def _pick_best_seed(seeds: List[SeedRow]) -> Tuple[Optional[SeedRow], float]:
    best: Optional[SeedRow] = None
    best_score = 0.0

    for s in seeds:
        sc = _seed_score(s)

        if best is None:
            best = s
            best_score = sc
            continue

        if abs(sc) > abs(best_score):
            best = s
            best_score = sc
            continue

        if abs(sc) == abs(best_score):
            if s.seed_id < best.seed_id:
                best = s
                best_score = sc

    return best, best_score


def compute_5m_timing_vote(
    *,
    seeds_csv: str,
    repo_root: str = ".",
    symbol: str = "BTCUSDT",
    now_utc: Optional[str] = None,
    timeframe: Optional[str] = None,
    thresh: Optional[float] = None,
    **kwargs: Any,
) -> TimingVote:
    """
    API expected by live_l1/core/loop.py
    """

    _ = repo_root
    _ = symbol
    _ = now_utc
    _ = timeframe
    _ = thresh
    _ = kwargs

    seeds = _read_seeds_csv(seeds_csv)

    if not seeds:
        return TimingVote(direction="none", strength=0.0, seed_id=None)

    best, score = _pick_best_seed(seeds)

    if best is None:
        return TimingVote(direction="none", strength=0.0, seed_id=None)

    direction = best.direction
    strength = _strength_from_score(score)

    if direction not in ("long", "short") or strength <= 0.0:
        return TimingVote(direction="none", strength=0.0, seed_id=None)

    return TimingVote(
        direction=direction,
        strength=strength,
        seed_id=best.seed_id,
    )


def _cli_main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--seeds", required=True)

    args = parser.parse_args()

    vote = compute_5m_timing_vote(
        repo_root=args.repo_root,
        symbol=args.symbol,
        seeds_csv=args.seeds,
        now_utc=None,
    )

    seeds = _read_seeds_csv(args.seeds)
    best, best_score = _pick_best_seed(seeds)

    sid = vote.seed_id if vote.seed_id is not None else ""
    best_dir = best.direction if best is not None else ""

    print(
        "vote_5m direction={d} strength={s:.6f} seed_id={sid} best_seed_dir={bd} score={sc:.6f}".format(
            d=vote.direction,
            s=vote.strength,
            sid=sid,
            bd=best_dir,
            sc=_safe_float(best_score, 0.0),
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(_cli_main())





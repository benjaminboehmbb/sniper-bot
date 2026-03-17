#!/usr/bin/env python3
# tools/l1c_fusion_stats.py
#
# L1-C Validation: statistics for event=intent_fused from live_logs/l1_paper.log
# ASCII-only. Read-only. No external deps.

from __future__ import annotations

import argparse
import os
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Tuple


@dataclass
class Agg:
    n: int = 0
    sum_v: float = 0.0
    min_v: float = 1e9
    max_v: float = -1e9

    def add(self, x: float) -> None:
        self.n += 1
        self.sum_v += x
        if x < self.min_v:
            self.min_v = x
        if x > self.max_v:
            self.max_v = x

    def mean(self) -> float:
        return (self.sum_v / float(self.n)) if self.n > 0 else 0.0

    def min(self) -> float:
        return self.min_v if self.n > 0 else 0.0

    def max(self) -> float:
        return self.max_v if self.n > 0 else 0.0


def _safe_float(s: str, default: float = 0.0) -> float:
    try:
        return float(s)
    except Exception:
        return default


def _parse_kv_line(line: str) -> Dict[str, str]:
    """
    Parse "k=v" tokens separated by spaces.
    Keeps only tokens that contain "=".
    Strips trailing whitespace/newlines.
    """
    out: Dict[str, str] = {}
    line = line.strip()
    if not line:
        return out
    parts = line.split()
    for p in parts:
        if "=" not in p:
            continue
        k, v = p.split("=", 1)
        k = k.strip()
        v = v.strip()
        if not k:
            continue
        out[k] = v
    return out


def _iter_fused_rows(log_path: str) -> Iterable[Dict[str, str]]:
    with open(log_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if "event=intent_fused" not in line:
                continue
            row = _parse_kv_line(line)
            if row.get("event") != "intent_fused":
                continue
            yield row


def _pct(a: int, b: int) -> float:
    if b <= 0:
        return 0.0
    return 100.0 * float(a) / float(b)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True, help="Path to live log file, e.g. live_logs/l1_paper.log")
    ap.add_argument("--thresh", type=float, default=0.60, help="Confirmation threshold used in fusion (default: 0.60)")
    args = ap.parse_args()

    log_path = args.log
    if not os.path.isfile(log_path):
        raise SystemExit("log not found: %s" % log_path)

    total = 0

    c_intent_raw = Counter()
    c_intent_final = Counter()
    c_vote_dir = Counter()
    c_reason = Counter()

    # transitions: raw->final
    c_trans = Counter()

    # confirmations / blocks for BUY/SELL
    buy_raw = 0
    buy_confirm = 0
    buy_block = 0

    sell_raw = 0
    sell_confirm = 0
    sell_block = 0

    # vote strength aggregates overall and by vote direction
    agg_strength_all = Agg()
    agg_strength_by_dir: Dict[str, Agg] = defaultdict(Agg)

    # strength above threshold (by dir)
    c_dir_ge_thresh = Counter()
    c_dir_lt_thresh = Counter()

    # seed id counts
    c_seed = Counter()

    for row in _iter_fused_rows(log_path):
        total += 1

        intent_raw = row.get("intent_1m_raw", "NA")
        intent_final = row.get("intent_final", "NA")
        vote_dir = row.get("vote_5m_direction", "NA")
        reason = row.get("reason_code", "NA")
        seed_id = row.get("vote_5m_seed_id", "")

        c_intent_raw[intent_raw] += 1
        c_intent_final[intent_final] += 1
        c_vote_dir[vote_dir] += 1
        c_reason[reason] += 1
        c_trans["%s->%s" % (intent_raw, intent_final)] += 1

        if seed_id:
            c_seed[seed_id] += 1

        s = _safe_float(row.get("vote_5m_strength", "0.0"), 0.0)
        if s < 0.0:
            s = 0.0
        if s > 1.0:
            s = 1.0

        agg_strength_all.add(s)
        agg_strength_by_dir[vote_dir].add(s)

        if s >= float(args.thresh):
            c_dir_ge_thresh[vote_dir] += 1
        else:
            c_dir_lt_thresh[vote_dir] += 1

        if intent_raw == "BUY":
            buy_raw += 1
            if intent_final == "BUY":
                buy_confirm += 1
            else:
                buy_block += 1

        if intent_raw == "SELL":
            sell_raw += 1
            if intent_final == "SELL":
                sell_confirm += 1
            else:
                sell_block += 1

    if total == 0:
        print("No intent_fused events found in log.")
        return 0

    print("L1-C FUSION STATS")
    print("log=%s" % log_path)
    print("n_events=%d" % total)
    print("thresh=%.2f" % float(args.thresh))
    print("")

    # Headline rates
    print("RAW INTENT DISTRIBUTION")
    for k in ("BUY", "SELL", "HOLD", "NA"):
        if c_intent_raw[k] > 0:
            print("  %s: %d (%.2f%%)" % (k, c_intent_raw[k], _pct(c_intent_raw[k], total)))
    # any others
    for k, v in c_intent_raw.most_common():
        if k in ("BUY", "SELL", "HOLD", "NA"):
            continue
        print("  %s: %d (%.2f%%)" % (k, v, _pct(v, total)))
    print("")

    print("FINAL INTENT DISTRIBUTION")
    for k in ("BUY", "SELL", "HOLD", "NA"):
        if c_intent_final[k] > 0:
            print("  %s: %d (%.2f%%)" % (k, c_intent_final[k], _pct(c_intent_final[k], total)))
    for k, v in c_intent_final.most_common():
        if k in ("BUY", "SELL", "HOLD", "NA"):
            continue
        print("  %s: %d (%.2f%%)" % (k, v, _pct(v, total)))
    print("")

    print("CONFIRM / BLOCK RATES")
    if buy_raw > 0:
        print("  BUY:  confirm=%d (%.2f%%)  block=%d (%.2f%%)" % (buy_confirm, _pct(buy_confirm, buy_raw), buy_block, _pct(buy_block, buy_raw)))
    else:
        print("  BUY:  raw=0")
    if sell_raw > 0:
        print("  SELL: confirm=%d (%.2f%%)  block=%d (%.2f%%)" % (sell_confirm, _pct(sell_confirm, sell_raw), sell_block, _pct(sell_block, sell_raw)))
    else:
        print("  SELL: raw=0")
    print("")

    print("5M VOTE DIRECTION DISTRIBUTION")
    for k, v in c_vote_dir.most_common():
        print("  %s: %d (%.2f%%)" % (k, v, _pct(v, total)))
    print("")

    print("5M STRENGTH SUMMARY")
    print("  all: n=%d mean=%.6f min=%.6f max=%.6f" % (agg_strength_all.n, agg_strength_all.mean(), agg_strength_all.min(), agg_strength_all.max()))
    for d, agg in sorted(agg_strength_by_dir.items(), key=lambda x: x[0]):
        print("  %s: n=%d mean=%.6f min=%.6f max=%.6f" % (d, agg.n, agg.mean(), agg.min(), agg.max()))
    print("")

    print("5M STRENGTH VS THRESH (by direction)")
    dirs = sorted(set(list(c_vote_dir.keys()) + list(c_dir_ge_thresh.keys()) + list(c_dir_lt_thresh.keys())))
    for d in dirs:
        ge = c_dir_ge_thresh[d]
        lt = c_dir_lt_thresh[d]
        n = ge + lt
        if n <= 0:
            continue
        print("  %s: >=thresh=%d (%.2f%%)  <thresh=%d (%.2f%%)" % (d, ge, _pct(ge, n), lt, _pct(lt, n)))
    print("")

    print("TOP REASON CODES (top 12)")
    for k, v in c_reason.most_common(12):
        print("  %s: %d (%.2f%%)" % (k, v, _pct(v, total)))
    print("")

    print("TOP TRANSITIONS raw->final (top 12)")
    for k, v in c_trans.most_common(12):
        print("  %s: %d (%.2f%%)" % (k, v, _pct(v, total)))
    print("")

    if len(c_seed) > 0:
        print("TOP 5M SEEDS (top 12)")
        for k, v in c_seed.most_common(12):
            print("  %s: %d (%.2f%%)" % (k, v, _pct(v, total)))
        print("")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

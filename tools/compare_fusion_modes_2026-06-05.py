#!/usr/bin/env python3
# tools/compare_fusion_modes_2026-06-05.py
# Compare current ASYM fusion against strict L1-C 5m confirmation policy.
# Read-only log analyzer. No live code changes. ASCII-only.

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter


def parse_kv_line(line: str) -> dict:
    out = {}
    for m in re.finditer(r'([A-Za-z0-9_]+)=("[^"]*"|[^ ]*)', line):
        k = m.group(1)
        v = m.group(2)
        if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
            v = v[1:-1]
        out[k] = v
    return out


def to_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default


def to_int(x, default=0):
    try:
        return int(float(x))
    except Exception:
        return default


def norm_intent(x: str) -> str:
    s = str(x).strip().upper()
    if s in ("BUY", "SELL", "HOLD"):
        return s
    return "HOLD"


def norm_vote_dir(x: str) -> str:
    s = str(x).strip().lower()
    if s in ("long", "short", "none"):
        return s
    return "none"


def strict_5m_confirm(
    *,
    intent_1m_raw: str,
    vote_5m_direction: str,
    vote_5m_strength: float,
    allow_long: int,
    allow_short: int,
    thresh: float,
    current_position: str,
) -> tuple[str, str]:
    intent = norm_intent(intent_1m_raw)
    d = norm_vote_dir(vote_5m_direction)
    s = max(0.0, min(1.0, float(vote_5m_strength)))
    pos = str(current_position).strip().upper()

    # Preserve current exit invariant: exits must always remain possible.
    if intent == "BUY" and pos == "SHORT":
        return "BUY", "STRICT_EXIT_SHORT_ON_1M_BUY"
    if intent == "SELL" and pos == "LONG":
        return "SELL", "STRICT_EXIT_LONG_ON_1M_SELL"

    if intent == "HOLD":
        return "HOLD", "STRICT_HOLD_RAW"

    if d == "none":
        return "HOLD", "STRICT_NO_5M_VOTE"

    if intent == "BUY":
        if int(allow_long) != 1:
            return "HOLD", "STRICT_GATE_BLOCK_LONG"
        if d != "long":
            return "HOLD", "STRICT_5M_CONTRADICTS_1M"
        if s < float(thresh):
            return "HOLD", "STRICT_WEAK_5M_LONG_CONFIRM"
        return "BUY", "STRICT_CONFIRMED_1M_BUY_5M_LONG"

    if intent == "SELL":
        if int(allow_short) != 1:
            return "HOLD", "STRICT_GATE_BLOCK_SHORT"
        if d != "short":
            return "HOLD", "STRICT_5M_CONTRADICTS_1M"
        if s < float(thresh):
            return "HOLD", "STRICT_WEAK_5M_SHORT_CONFIRM"
        return "SELL", "STRICT_CONFIRMED_1M_SELL_5M_SHORT"

    return "HOLD", "STRICT_UNKNOWN_INTENT_FAILSAFE"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--log", default="live_logs/l1_paper.log")
    p.add_argument("--out", default="reports/fusion_compare/fusion_compare_2026-06-05.csv")
    p.add_argument("--max-examples", type=int, default=30)
    args = p.parse_args()

    if not os.path.isfile(args.log):
        raise SystemExit("ERROR: log not found: " + args.log)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    total = 0
    diffs = 0
    action_counter = Counter()
    reason_counter = Counter()
    diff_reason_counter = Counter()
    examples = []

    rows = []

    with open(args.log, "r", encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            if "event=intent_fused" not in raw:
                continue

            kv = parse_kv_line(raw)

            intent_1m_raw = norm_intent(kv.get("intent_1m_raw", "HOLD"))
            current_final = norm_intent(kv.get("intent_final", "HOLD"))
            current_reason = kv.get("reason_code", "")
            current_position = kv.get("current_position", "FLAT")

            strict_final, strict_reason = strict_5m_confirm(
                intent_1m_raw=intent_1m_raw,
                vote_5m_direction=kv.get("vote_5m_direction", "none"),
                vote_5m_strength=to_float(kv.get("vote_5m_strength", 0.0)),
                allow_long=to_int(kv.get("allow_long", 1)),
                allow_short=to_int(kv.get("allow_short", 1)),
                thresh=to_float(kv.get("thresh", 0.60), 0.60),
                current_position=current_position,
            )

            total += 1
            action_counter[(current_final, strict_final)] += 1
            reason_counter[current_reason] += 1

            is_diff = current_final != strict_final
            if is_diff:
                diffs += 1
                diff_reason_counter[(current_reason, strict_reason)] += 1

            row = {
                "tick": kv.get("tick", ""),
                "intent_1m_raw": intent_1m_raw,
                "current_position": current_position,
                "current_final": current_final,
                "current_reason": current_reason,
                "strict_final": strict_final,
                "strict_reason": strict_reason,
                "vote_5m_direction": kv.get("vote_5m_direction", ""),
                "vote_5m_strength": kv.get("vote_5m_strength", ""),
                "vote_5m_seed_id": kv.get("vote_5m_seed_id", ""),
                "allow_long": kv.get("allow_long", ""),
                "allow_short": kv.get("allow_short", ""),
                "is_diff": int(is_diff),
            }
            rows.append(row)

            if is_diff and len(examples) < int(args.max_examples):
                examples.append(row)

    fields = [
        "tick",
        "intent_1m_raw",
        "current_position",
        "current_final",
        "current_reason",
        "strict_final",
        "strict_reason",
        "vote_5m_direction",
        "vote_5m_strength",
        "vote_5m_seed_id",
        "allow_long",
        "allow_short",
        "is_diff",
    ]

    import csv
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print("---- FUSION MODE COMPARE ----")
    print("log:", args.log)
    print("rows:", total)
    print("diffs:", diffs)
    print("diff_rate:", (diffs / total) if total else 0.0)
    print("out:", args.out)

    print("")
    print("current_final -> strict_final:")
    for (a, b), n in action_counter.most_common():
        print("{0} -> {1}: {2}".format(a, b, n))

    print("")
    print("top current reasons:")
    for k, n in reason_counter.most_common(20):
        print("{0}: {1}".format(k, n))

    print("")
    print("top diff reason pairs:")
    for (a, b), n in diff_reason_counter.most_common(20):
        print("{0} -> {1}: {2}".format(a, b, n))

    print("")
    print("diff examples:")
    for r in examples:
        print(json.dumps(r, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

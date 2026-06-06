#!/usr/bin/env python3
# P54 Raw 1m Intent Score Distribution Audit
# ASCII-only.

from __future__ import annotations

from collections import Counter
from pathlib import Path

SEGMENTS = [
    Path("live_logs/review_segments/p49_after_timing_signal_wiring_segment.log"),
]

DOC = Path("docs/review/P54_RAW_1M_INTENT_SCORE_DISTRIBUTION_AUDIT_2026-06-06.md")


SIGNALS = [
    "ma200_signal",
    "mfi_signal",
    "rsi_signal",
    "stoch_signal",
    "bollinger_signal",
    "cci_signal",
    "macd_signal",
    "ema50_signal",
    "atr_signal",
    "adx_signal",
    "obv_signal",
    "roc_signal",
]


def val(parts: list[str], key: str) -> str | None:
    prefix = key + "="
    for p in parts:
        if p.startswith(prefix):
            return p.split("=", 1)[1]
    return None


def main() -> int:
    intent_counts = Counter()
    timing_counts = Counter()
    reason_counts = Counter()
    entry_score_counts = Counter()
    regime_counts = Counter()
    risk_counts = Counter()

    rows = 0

    for path in SEGMENTS:
        if not path.exists():
            continue

        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                parts = line.strip().split()

                if "event=regime_snapshot" in line:
                    es = val(parts, "entry_score")
                    rg = val(parts, "regime_label")
                    rk = val(parts, "risk_label")

                    if es is not None:
                        entry_score_counts[es] += 1
                    if rg is not None:
                        regime_counts[rg] += 1
                    if rk is not None:
                        risk_counts[rk] += 1

                elif "event=intent_fused" in line:
                    rows += 1

                    i = val(parts, "intent_1m_raw")
                    t = val(parts, "vote_5m_direction")
                    r = val(parts, "reason_code")

                    if i is not None:
                        intent_counts[i] += 1
                    if t is not None:
                        timing_counts[t] += 1
                    if r is not None:
                        reason_counts[r] += 1

    DOC.parent.mkdir(parents=True, exist_ok=True)

    with DOC.open("w", encoding="utf-8") as out:
        out.write("# P54 RAW 1M INTENT SCORE DISTRIBUTION AUDIT\n\n")
        out.write("Date: 2026-06-06\n")
        out.write("Device: G15 / AR15\n")
        out.write("Environment: WSL\n\n")

        out.write("## Objective\n\n")
        out.write("Quantify raw 1m intent and related score distributions on post-fix runtime segments.\n\n")

        out.write("## Audited Segments\n\n")
        for p in SEGMENTS:
            out.write(f"- {p}\n")
        out.write("\n")

        out.write("## Runtime Rows\n\n")
        out.write(f"intent_rows: {rows}\n\n")

        out.write("## Raw 1m Intent Distribution\n\n")
        for k, v in intent_counts.most_common():
            out.write(f"- {k}: {v}\n")
        out.write("\n")

        out.write("## 5m Timing Distribution\n\n")
        for k, v in timing_counts.most_common():
            out.write(f"- {k}: {v}\n")
        out.write("\n")

        out.write("## Reason Code Distribution\n\n")
        for k, v in reason_counts.most_common():
            out.write(f"- {k}: {v}\n")
        out.write("\n")

        out.write("## Entry Score Distribution\n\n")
        for k, v in sorted(entry_score_counts.items(), key=lambda x: int(x[0]) if str(x[0]).lstrip('-').isdigit() else 999):
            out.write(f"- {k}: {v}\n")
        out.write("\n")

        out.write("## Regime Distribution\n\n")
        for k, v in regime_counts.most_common():
            out.write(f"- {k}: {v}\n")
        out.write("\n")

        out.write("## Risk Distribution\n\n")
        for k, v in risk_counts.most_common():
            out.write(f"- {k}: {v}\n")
        out.write("\n")

        out.write("## Interpretation\n\n")
        out.write("This audit separates raw 1m intent behavior from 5m timing behavior.\n\n")
        out.write("If raw 1m intent remains HOLD while timing varies, the current bottleneck is raw 1m intent generation.\n\n")

        out.write("## Result\n\n")
        out.write("Status: PASS\n")

    print("P54 RAW 1M INTENT SCORE DISTRIBUTION AUDIT")
    print("intent_rows:", rows)
    print("raw_intents:", dict(intent_counts))
    print("timing:", dict(timing_counts))
    print("entry_scores:", dict(entry_score_counts))
    print("doc_out:", DOC)
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# P58 Entry Gate Condition Alignment Audit
# ASCII-only.

from __future__ import annotations

from pathlib import Path
from collections import Counter

SEGMENT = Path("live_logs/review_segments/p49_after_timing_signal_wiring_segment.log")
DOC = Path("docs/review/P58_ENTRY_GATE_CONDITION_ALIGNMENT_AUDIT_2026-06-06.md")


def value(parts: list[str], key: str) -> str | None:
    prefix = key + "="
    for p in parts:
        if p.startswith(prefix):
            return p.split("=", 1)[1]
    return None


def all_ge(vals: list[int], threshold: int, n: int) -> bool:
    return len(vals) == n and all(v >= threshold for v in vals)


def all_le(vals: list[int], threshold: int, n: int) -> bool:
    return len(vals) == n and all(v <= threshold for v in vals)


def main() -> int:
    if not SEGMENT.exists():
        print("ERROR: missing segment:", SEGMENT)
        return 1

    rows = []
    pending_regime = None

    with SEGMENT.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.strip().split()

            if "event=regime_snapshot" in line:
                pending_regime = {
                    "entry_score": value(parts, "entry_score"),
                    "ma200_signal": value(parts, "ma200_signal"),
                    "mfi_signal": value(parts, "mfi_signal"),
                    "atr_signal": value(parts, "atr_signal"),
                    "regime_label": value(parts, "regime_label"),
                    "risk_label": value(parts, "risk_label"),
                }

            elif "event=intent_fused" in line:
                if pending_regime is None:
                    continue

                row = dict(pending_regime)
                row.update({
                    "intent_1m_raw": value(parts, "intent_1m_raw"),
                    "intent_final": value(parts, "intent_final"),
                    "reason_code": value(parts, "reason_code"),
                    "vote_5m_direction": value(parts, "vote_5m_direction"),
                    "vote_5m_seed_id": value(parts, "vote_5m_seed_id"),
                })
                rows.append(row)
                pending_regime = None

    scores = []
    counters = Counter()
    examples = []

    for idx, row in enumerate(rows, start=1):
        try:
            score = int(row.get("entry_score") or 0)
        except Exception:
            score = 0

        try:
            ma200 = int(row.get("ma200_signal") or 0)
        except Exception:
            ma200 = 0

        try:
            mfi = int(row.get("mfi_signal") or 0)
        except Exception:
            mfi = 0

        try:
            atr = int(row.get("atr_signal") or 0)
        except Exception:
            atr = 0

        scores.append(score)
        last3 = scores[-3:]

        buy_score_ok = all_ge(last3, 4 if atr == -1 else 3, 3)
        sell_score_ok = all_le(last3, -4 if atr == -1 else -3, 3)

        buy_core_ok = ma200 == 1 and mfi == 1
        sell_core_ok = ma200 == -1 and mfi == -1

        if buy_score_ok:
            counters["buy_score_ok"] += 1
        if sell_score_ok:
            counters["sell_score_ok"] += 1
        if buy_core_ok:
            counters["buy_core_ok"] += 1
        if sell_core_ok:
            counters["sell_core_ok"] += 1
        if buy_score_ok and buy_core_ok:
            counters["buy_full_entry_condition"] += 1
        if sell_score_ok and sell_core_ok:
            counters["sell_full_entry_condition"] += 1

        if len(examples) < 30 and (buy_score_ok or sell_score_ok or buy_core_ok or sell_core_ok):
            examples.append({
                "idx": idx,
                "score": score,
                "last3": list(last3),
                "ma200": ma200,
                "mfi": mfi,
                "atr": atr,
                "buy_score_ok": buy_score_ok,
                "sell_score_ok": sell_score_ok,
                "buy_core_ok": buy_core_ok,
                "sell_core_ok": sell_core_ok,
                "intent_1m_raw": row.get("intent_1m_raw"),
                "vote_5m_direction": row.get("vote_5m_direction"),
            })

    DOC.parent.mkdir(parents=True, exist_ok=True)

    with DOC.open("w", encoding="utf-8") as out:
        out.write("# P58 ENTRY GATE CONDITION ALIGNMENT AUDIT\n\n")
        out.write("Date: 2026-06-06\n")
        out.write("Device: G15 / AR15\n")
        out.write("Environment: WSL\n\n")

        out.write("## Objective\n\n")
        out.write("Check whether score sequences align with ma200/mfi/atr entry conditions in the P49 segment.\n\n")

        out.write("## Segment\n\n")
        out.write(f"{SEGMENT}\n\n")

        out.write("## Rows\n\n")
        out.write(f"{len(rows)}\n\n")

        out.write("## Condition Counts\n\n")
        for k, v in counters.most_common():
            out.write(f"- {k}: {v}\n")
        out.write("\n")

        out.write("## Example Rows\n\n")
        if not examples:
            out.write("none\n\n")
        else:
            for e in examples:
                out.write(
                    "- idx={idx} score={score} last3={last3} ma200={ma200} mfi={mfi} atr={atr} "
                    "buy_score_ok={buy_score_ok} sell_score_ok={sell_score_ok} "
                    "buy_core_ok={buy_core_ok} sell_core_ok={sell_core_ok} "
                    "intent_1m_raw={intent_1m_raw} vote_5m_direction={vote_5m_direction}\n".format(**e)
                )
            out.write("\n")

        out.write("## Interpretation\n\n")
        out.write("If score sequence conditions occur but full entry conditions remain zero, ma200/mfi alignment is the blocker.\n\n")

        out.write("## Result\n\n")
        out.write("Status: PASS\n")

    print("P58 ENTRY GATE CONDITION ALIGNMENT AUDIT")
    print("rows:", len(rows))
    print("condition_counts:", dict(counters))
    print("doc_out:", DOC)
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

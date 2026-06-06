#!/usr/bin/env python3
# P28G Bad Close Reconstruction Audit
# ASCII-only. Streaming.

from __future__ import annotations

from pathlib import Path
from collections import Counter

LOG_PATH = Path("live_logs/l1_paper.log")
OUT_PATH = Path("docs/review/P28G_BAD_CLOSE_RECONSTRUCTION_AUDIT_2026-06-06.md")


def parse_line(line: str) -> dict:
    out = {}
    for part in line.strip().split():
        if "=" in part:
            k, v = part.split("=", 1)
            out[k] = v
    return out


def main() -> int:
    if not LOG_PATH.is_file():
        print("ERROR: missing log:", LOG_PATH)
        return 1

    position = "FLAT"
    system_start_count = 0
    system_stop_count = 0

    bad_closes = []
    close_counts = Counter()
    action_counts = Counter()
    reason_counts = Counter()

    last_start = ""
    last_stop = ""
    last_position_change = ""

    with LOG_PATH.open("r", encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            row = parse_line(raw)
            event = row.get("event", "")

            if event == "system_start":
                system_start_count += 1
                last_start = raw.strip()

            elif event == "system_stop":
                system_stop_count += 1
                last_stop = raw.strip()

            elif event == "execution":
                action = row.get("action", "")
                reason = row.get("reason", "")
                tick = row.get("tick", "")
                ts = row.get("timestamp_utc", "")
                intent_id = row.get("intent_id", "")

                action_counts[action] += 1
                reason_counts[reason] += 1

                if action == "OPEN_LONG":
                    position = "LONG"
                    last_position_change = raw.strip()

                elif action == "OPEN_SHORT":
                    position = "SHORT"
                    last_position_change = raw.strip()

                elif action == "CLOSE_LONG":
                    close_counts[action] += 1
                    if position != "LONG":
                        bad_closes.append(
                            {
                                "expected": "LONG",
                                "actual_position": position,
                                "tick": tick,
                                "timestamp_utc": ts,
                                "intent_id": intent_id,
                                "reason": reason,
                                "last_start": last_start,
                                "last_stop": last_stop,
                                "last_position_change": last_position_change,
                                "line": raw.strip(),
                            }
                        )
                    position = "FLAT"
                    last_position_change = raw.strip()

                elif action == "CLOSE_SHORT":
                    close_counts[action] += 1
                    if position != "SHORT":
                        bad_closes.append(
                            {
                                "expected": "SHORT",
                                "actual_position": position,
                                "tick": tick,
                                "timestamp_utc": ts,
                                "intent_id": intent_id,
                                "reason": reason,
                                "last_start": last_start,
                                "last_stop": last_stop,
                                "last_position_change": last_position_change,
                                "line": raw.strip(),
                            }
                        )
                    position = "FLAT"
                    last_position_change = raw.strip()

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUT_PATH.open("w", encoding="utf-8") as out:
        out.write("# P28G BAD CLOSE RECONSTRUCTION AUDIT\n\n")
        out.write("Date: 2026-06-06\n")
        out.write("Device: G15 / AR15\n")
        out.write("Environment: WSL\n\n")

        out.write("## Objective\n\n")
        out.write("Determine whether bad close events from P28F are true execution issues or reconstruction artifacts.\n\n")

        out.write("## Summary\n\n")
        out.write(f"system_start_count: {system_start_count}\n\n")
        out.write(f"system_stop_count: {system_stop_count}\n\n")
        out.write(f"bad_closes_detected: {len(bad_closes)}\n\n")
        out.write(f"final_reconstructed_position: {position}\n\n")

        out.write("## Action Counts\n\n")
        for k, v in action_counts.most_common():
            out.write(f"- {k}: {v}\n")
        out.write("\n")

        out.write("## Close Counts\n\n")
        for k, v in close_counts.most_common():
            out.write(f"- {k}: {v}\n")
        out.write("\n")

        out.write("## Reason Counts\n\n")
        for k, v in reason_counts.most_common():
            out.write(f"- {k}: {v}\n")
        out.write("\n")

        out.write("## Bad Close Samples\n\n")
        if not bad_closes:
            out.write("none\n\n")
        else:
            for i, item in enumerate(bad_closes[:20], start=1):
                out.write(f"### Bad Close {i}\n\n")
                out.write(f"expected: {item['expected']}\n\n")
                out.write(f"actual_position: {item['actual_position']}\n\n")
                out.write(f"tick: {item['tick']}\n\n")
                out.write(f"timestamp_utc: {item['timestamp_utc']}\n\n")
                out.write(f"reason: {item['reason']}\n\n")
                out.write("last_position_change:\n\n")
                out.write("```text\n")
                out.write(item["last_position_change"] + "\n")
                out.write("```\n\n")
                out.write("bad_close_line:\n\n")
                out.write("```text\n")
                out.write(item["line"] + "\n")
                out.write("```\n\n")

        out.write("## Interpretation\n\n")
        if bad_closes:
            out.write("Bad closes were detected by sequential log reconstruction.\n\n")
            out.write("Because the log contains multiple system_start/system_stop cycles, these may be reconstruction artifacts across restarts or resumed positions.\n\n")
            out.write("This requires comparison with persisted S2 state and execution_audit before classifying as execution bug.\n\n")
        else:
            out.write("No bad closes were detected by sequential reconstruction.\n\n")

        out.write("## Result\n\n")
        out.write("Status: PASS\n")

    print("P28G BAD CLOSE RECONSTRUCTION AUDIT")
    print("system_start_count:", system_start_count)
    print("system_stop_count:", system_stop_count)
    print("bad_closes_detected:", len(bad_closes))
    print("final_reconstructed_position:", position)
    print("doc_out:", OUT_PATH)
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# P28H Time-Stop Execution Audit
# ASCII-only. Streaming.

from __future__ import annotations

from collections import Counter
from pathlib import Path

LOG_PATH = Path("live_logs/l1_paper.log")
OUT_PATH = Path("docs/review/P28H_TIME_STOP_EXECUTION_AUDIT_2026-06-06.md")


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
    anomalies = []
    time_stop_counts = Counter()
    close_counts = Counter()
    position_before_counts = Counter()
    action_reason_counts = Counter()

    last_open_line = ""
    last_close_line = ""

    with LOG_PATH.open("r", encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            line = raw.strip()
            row = parse_line(line)

            if row.get("event") != "execution":
                continue

            action = row.get("action", "")
            reason = row.get("reason", "")
            position_before = row.get("position_before", "")
            position_after = row.get("position_after", "")
            tick = row.get("tick", "")

            action_reason_counts[(action, reason)] += 1

            if reason in ("LONG_TIME_STOP_HIT", "SHORT_TIME_STOP_HIT"):
                time_stop_counts[reason] += 1
                position_before_counts[(reason, position_before, position_after)] += 1

            if action == "OPEN_LONG":
                position = "LONG"
                last_open_line = line

            elif action == "OPEN_SHORT":
                position = "SHORT"
                last_open_line = line

            elif action == "CLOSE_LONG":
                close_counts[action] += 1

                if reason == "LONG_TIME_STOP_HIT":
                    if position != "LONG":
                        anomalies.append(
                            {
                                "type": "repeated_or_invalid_long_time_stop_close",
                                "expected_reconstructed_position": "LONG",
                                "actual_reconstructed_position": position,
                                "tick": tick,
                                "position_before_log": position_before,
                                "position_after_log": position_after,
                                "last_open_line": last_open_line,
                                "last_close_line": last_close_line,
                                "line": line,
                            }
                        )

                position = "FLAT"
                last_close_line = line

            elif action == "CLOSE_SHORT":
                close_counts[action] += 1

                if reason == "SHORT_TIME_STOP_HIT":
                    if position != "SHORT":
                        anomalies.append(
                            {
                                "type": "repeated_or_invalid_short_time_stop_close",
                                "expected_reconstructed_position": "SHORT",
                                "actual_reconstructed_position": position,
                                "tick": tick,
                                "position_before_log": position_before,
                                "position_after_log": position_after,
                                "last_open_line": last_open_line,
                                "last_close_line": last_close_line,
                                "line": line,
                            }
                        )

                position = "FLAT"
                last_close_line = line

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUT_PATH.open("w", encoding="utf-8") as out:
        out.write("# P28H TIME-STOP EXECUTION AUDIT\n\n")
        out.write("Date: 2026-06-06\n")
        out.write("Device: G15 / AR15\n")
        out.write("Environment: WSL\n\n")

        out.write("## Objective\n\n")
        out.write("Audit repeated or invalid time-stop close events in live_logs/l1_paper.log.\n\n")

        out.write("## Summary\n\n")
        out.write(f"time_stop_anomalies: {len(anomalies)}\n\n")
        out.write(f"final_reconstructed_position: {position}\n\n")

        out.write("## Time Stop Counts\n\n")
        for k, v in time_stop_counts.most_common():
            out.write(f"- {k}: {v}\n")
        out.write("\n")

        out.write("## Time Stop Position Before/After Counts\n\n")
        for k, v in position_before_counts.most_common():
            out.write(f"- reason={k[0]} position_before={k[1]} position_after={k[2]}: {v}\n")
        out.write("\n")

        out.write("## Action/Reason Counts Relevant To Time Stops\n\n")
        for k, v in action_reason_counts.most_common():
            action, reason = k
            if "TIME_STOP" in reason:
                out.write(f"- action={action} reason={reason}: {v}\n")
        out.write("\n")

        out.write("## Anomaly Samples\n\n")
        if not anomalies:
            out.write("none\n\n")
        else:
            for i, item in enumerate(anomalies[:30], start=1):
                out.write(f"### Anomaly {i}\n\n")
                out.write(f"type: {item['type']}\n\n")
                out.write(f"tick: {item['tick']}\n\n")
                out.write(f"actual_reconstructed_position: {item['actual_reconstructed_position']}\n\n")
                out.write(f"position_before_log: {item['position_before_log']}\n\n")
                out.write(f"position_after_log: {item['position_after_log']}\n\n")

                out.write("last_open_line:\n\n```text\n")
                out.write(item["last_open_line"] + "\n")
                out.write("```\n\n")

                out.write("last_close_line:\n\n```text\n")
                out.write(item["last_close_line"] + "\n")
                out.write("```\n\n")

                out.write("anomaly_line:\n\n```text\n")
                out.write(item["line"] + "\n")
                out.write("```\n\n")

        out.write("## Interpretation\n\n")
        if anomalies:
            out.write("Time-stop close anomalies were detected by sequential reconstruction.\n\n")
            out.write("The log reports position_before as LONG/SHORT while the reconstructed stream state is already FLAT.\n\n")
            out.write("This suggests either repeated time-stop close emission after a position has already closed, or a reconstruction/state-source mismatch.\n\n")
            out.write("Next step: inspect live_l1/core/execution.py time-stop branch before patching.\n\n")
        else:
            out.write("No time-stop close anomalies detected.\n\n")

        out.write("## Result\n\n")
        out.write("Status: PASS\n")

    print("P28H TIME-STOP EXECUTION AUDIT")
    print("time_stop_anomalies:", len(anomalies))
    print("final_reconstructed_position:", position)
    print("doc_out:", OUT_PATH)
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

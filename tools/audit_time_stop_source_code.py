#!/usr/bin/env python3
# P28I Time-Stop Source Code Audit
# ASCII-only.

from __future__ import annotations

from pathlib import Path

TARGETS = [
    "live_l1/core/execution.py",
    "live_l1/core/loop.py",
    "live_l1/state/state_store.py",
    "live_l1/state/models.py",
]

OUT_PATH = Path("docs/review/P28I_TIME_STOP_SOURCE_CODE_AUDIT_2026-06-06.md")


KEYWORDS = [
    "LONG_TIME_STOP_HIT",
    "SHORT_TIME_STOP_HIT",
    "duration",
    "entry_timestamp",
    "position_before",
    "position_after",
    "CLOSE_LONG",
    "CLOSE_SHORT",
    "position =",
    "side =",
    "entry_price",
]


def collect_matches(path: Path) -> list[tuple[int, str]]:
    matches = []
    if not path.is_file():
        return matches

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()

    for i, line in enumerate(lines, start=1):
        if any(k in line for k in KEYWORDS):
            start = max(1, i - 3)
            end = min(len(lines), i + 3)

            for j in range(start, end + 1):
                matches.append((j, lines[j - 1]))
            matches.append((-1, ""))

    seen = set()
    out = []
    for item in matches:
        if item == (-1, ""):
            out.append(item)
            continue
        if item not in seen:
            seen.add(item)
            out.append(item)

    return out


def main() -> int:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUT_PATH.open("w", encoding="utf-8") as out:
        out.write("# P28I TIME-STOP SOURCE CODE AUDIT\n\n")
        out.write("Date: 2026-06-06\n")
        out.write("Device: G15 / AR15\n")
        out.write("Environment: WSL\n\n")

        out.write("## Objective\n\n")
        out.write("Inspect source code related to LONG_TIME_STOP_HIT and SHORT_TIME_STOP_HIT before applying any patch.\n\n")

        for rel in TARGETS:
            path = Path(rel)
            out.write(f"## {rel}\n\n")
            out.write(f"exists: {path.is_file()}\n\n")

            matches = collect_matches(path)

            if not matches:
                out.write("No relevant keyword matches.\n\n")
                continue

            out.write("```text\n")
            for line_no, text in matches:
                if line_no == -1:
                    out.write("\n")
                else:
                    out.write(f"{line_no}: {text}\n")
            out.write("```\n\n")

        out.write("## Preliminary Interpretation\n\n")
        out.write("P28H showed repeated time-stop close events after reconstructed position was already FLAT.\n\n")
        out.write("P28I collects the relevant source-code areas for manual review before patching.\n\n")
        out.write("No code changes are introduced in this step.\n\n")

        out.write("## Result\n\n")
        out.write("Status: PASS\n")

    print("P28I TIME-STOP SOURCE CODE AUDIT")
    print("doc_out:", OUT_PATH)
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# P57 Exact Raw Intent Rule Extraction
# ASCII-only.

from __future__ import annotations

from pathlib import Path

TARGET = Path("live_l1/core/intent.py")
DOC = Path("docs/review/P57_EXACT_RAW_INTENT_RULE_EXTRACTION_2026-06-06.md")


def main() -> int:
    if not TARGET.exists():
        print("ERROR: missing target:", TARGET)
        return 1

    lines = TARGET.read_text(encoding="utf-8", errors="replace").splitlines()

    start = 240
    end = 296

    extracted = []
    for line_no in range(start, end + 1):
        if 1 <= line_no <= len(lines):
            extracted.append((line_no, lines[line_no - 1]))

    DOC.parent.mkdir(parents=True, exist_ok=True)

    with DOC.open("w", encoding="utf-8") as out:
        out.write("# P57 EXACT RAW INTENT RULE EXTRACTION\n\n")
        out.write("Date: 2026-06-06\n")
        out.write("Device: G15 / AR15\n")
        out.write("Environment: WSL\n\n")

        out.write("## Objective\n\n")
        out.write("Extract the exact raw 1m intent decision block from live_l1/core/intent.py.\n\n")

        out.write("## Source\n\n")
        out.write(f"{TARGET}\n\n")

        out.write("## Extracted Rule Block\n\n")
        out.write("```text\n")
        for line_no, text in extracted:
            out.write(f"{line_no}: {text}\n")
        out.write("```\n\n")

        out.write("## Result\n\n")
        out.write("Status: PASS\n")

    print("P57 EXACT RAW INTENT RULE EXTRACTION")
    print("source:", TARGET)
    print("lines:", str(start) + "-" + str(end))
    print("doc_out:", DOC)
    print("RESULT: PASS")

    print("---- EXTRACTED RULE BLOCK ----")
    for line_no, text in extracted:
        print(f"{line_no}: {text}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

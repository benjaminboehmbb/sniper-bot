#!/usr/bin/env python3
# tools/gs_checklist_runner.py
#
# Purpose (v0):
#   Read-only GS checklist runner that evaluates the machine-readable checklist
#   (docs/POLICIES/gs_acceptance_checklist.yaml) against provided evidence.
#
# Design constraints:
#   - ASCII-only output (avoid Unicode/emoji)
#   - Read-only: does not modify engine, strategies, or run state
#   - v0 focuses on structured reporting; automated evidence extraction is minimal
#
# Usage examples (WSL, from repo root):
#   python3 tools/gs_checklist_runner.py \
#       --checklist docs/POLICIES/gs_acceptance_checklist.yaml \
#       --evidence results/GS/meta/run_metadata.json \
#       --outdir results/GS/meta
#
# Evidence format:
#   Evidence is a JSON file with:
#     {
#       "ml_used": false,
#       "answers": {
#         "A1": true,
#         "A2": true,
#         ...
#       },
#       "meta": {
#         "strategy_id": "GS_k12_long_FULL_CANONICAL",
#         "run_timestamp_utc": "2026-01-10T08:35:40Z",
#         "code_commit": "abc123",
#         "dataset_id": "btc_1m_2017_2025_GS_PLUS_FORWARD",
#         "params_id": "enter_z=1.0,exit_z=0.0,tp=0.04,sl=0.02,max_hold=1440"
#       }
#     }
#
# Notes:
#   - In v0, automated checking of artifacts (logs/csv) is optional and minimal.
#   - Any mandatory item missing an explicit answer is treated as FAIL.
#   - Non-applicable section items (e.g., ML section when ml_used=false) are NA.

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

# --- Minimal YAML loader (prefers PyYAML if installed) ---
def load_yaml(path: str) -> Dict[str, Any]:
    try:
        import yaml  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "PyYAML is required for v0. Install with: pip install pyyaml"
        ) from e
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def now_utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def is_true(v: Any) -> bool:
    return v is True


def is_false(v: Any) -> bool:
    return v is False


def clamp_status(status: str) -> str:
    # Only allow PASS/FAIL/NA
    if status not in ("PASS", "FAIL", "NA"):
        return "FAIL"
    return status


@dataclass
class ItemResult:
    item_id: str
    text: str
    mandatory: bool
    applies: bool
    status: str  # PASS/FAIL/NA
    evidence_value: Optional[bool]
    note: str


def eval_applies(expr: str, ctx: Dict[str, Any]) -> bool:
    """
    v0 supports only:
      - "always"
      - "ml_used == true"
      - "ml_used == false"
    Anything else -> default True (conservative).
    """
    if not expr or expr == "always":
        return True
    expr = expr.strip().lower()
    ml_used = bool(ctx.get("ml_used", False))
    if expr == "ml_used == true":
        return ml_used
    if expr == "ml_used == false":
        return not ml_used
    # Conservative default
    return True


def flatten_items(section: Dict[str, Any], applies: bool) -> List[Tuple[str, str, bool]]:
    """
    Returns list of (id, text, mandatory).
    Section may have:
      - items: [...]
      - subsections: [{items: [...]}, ...]
    """
    out: List[Tuple[str, str, bool]] = []

    if "items" in section and isinstance(section["items"], list):
        for it in section["items"]:
            out.append((str(it.get("id", "")).strip(), str(it.get("text", "")).strip(), bool(it.get("mandatory", False))))

    if "subsections" in section and isinstance(section["subsections"], list):
        for sub in section["subsections"]:
            if "items" in sub and isinstance(sub["items"], list):
                for it in sub["items"]:
                    out.append((str(it.get("id", "")).strip(), str(it.get("text", "")).strip(), bool(it.get("mandatory", False))))

    return out


def evaluate_checklist(checklist: Dict[str, Any], evidence: Dict[str, Any]) -> Dict[str, Any]:
    ctx = {
        "ml_used": bool(evidence.get("ml_used", False))
    }
    answers: Dict[str, Any] = evidence.get("answers", {}) or {}
    meta: Dict[str, Any] = evidence.get("meta", {}) or {}

    results: List[ItemResult] = []
    failures: List[str] = []
    mandatory_total = 0
    mandatory_pass = 0
    mandatory_fail = 0
    mandatory_na = 0

    sections = checklist.get("sections", [])
    if not isinstance(sections, list):
        raise RuntimeError("Checklist YAML: 'sections' must be a list")

    for sec in sections:
        sec_id = str(sec.get("id", "")).strip()
        sec_title = str(sec.get("title", "")).strip()
        applies_if = str(sec.get("applies_if", "always")).strip()
        applies = eval_applies(applies_if, ctx)

        items = flatten_items(sec, applies)
        for item_id, text, mandatory in items:
            if not item_id:
                continue

            item_applies = applies
            if not item_applies:
                status = "NA"
                ev = None
                note = "Not applicable due to section applies_if: %s" % applies_if
            else:
                ev_raw = answers.get(item_id, None)
                # Accept only boolean evidence
                ev = ev_raw if isinstance(ev_raw, bool) else None

                if mandatory:
                    mandatory_total += 1
                    if ev is None:
                        status = "FAIL"
                        note = "Missing mandatory answer in evidence.answers"
                    elif is_true(ev):
                        status = "PASS"
                        note = ""
                    else:
                        status = "FAIL"
                        note = "Answered false for mandatory item"
                else:
                    # Non-mandatory items are not used for GS acceptance in v0.
                    if ev is None:
                        status = "NA"
                        note = "Optional item not answered"
                    elif is_true(ev):
                        status = "PASS"
                        note = ""
                    else:
                        status = "FAIL"
                        note = "Optional item answered false"

            status = clamp_status(status)
            if mandatory:
                if status == "PASS":
                    mandatory_pass += 1
                elif status == "FAIL":
                    mandatory_fail += 1
                else:
                    mandatory_na += 1

            if mandatory and status == "FAIL" and item_applies:
                failures.append(item_id)

            results.append(ItemResult(
                item_id=item_id,
                text=text,
                mandatory=mandatory,
                applies=item_applies,
                status=status,
                evidence_value=ev if item_applies else None,
                note=note
            ))

    accepted = (mandatory_fail == 0)

    report = {
        "tool": {
            "name": "gs_checklist_runner",
            "version": "v0",
            "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        },
        "inputs": {
            "checklist_version": str(checklist.get("version", "")),
            "checklist_name": str(checklist.get("name", "")),
            "ml_used": ctx["ml_used"]
        },
        "meta": meta,
        "summary": {
            "accepted": bool(accepted),
            "mandatory_total": int(mandatory_total),
            "mandatory_pass": int(mandatory_pass),
            "mandatory_fail": int(mandatory_fail),
            "mandatory_na": int(mandatory_na),
            "failed_item_ids": failures
        },
        "items": [
            {
                "id": r.item_id,
                "text": r.text,
                "mandatory": r.mandatory,
                "applies": r.applies,
                "status": r.status,
                "evidence": r.evidence_value,
                "note": r.note
            }
            for r in results
        ]
    }
    return report


def write_report(report: Dict[str, Any], outdir: str) -> Tuple[str, str]:
    ensure_dir(outdir)
    stamp = now_utc_stamp()
    base = "gs_check_report_%s" % stamp
    json_path = os.path.join(outdir, base + ".json")
    txt_path = os.path.join(outdir, base + ".txt")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=False)

    # Human-readable summary
    s = report["summary"]
    lines: List[str] = []
    lines.append("GS CHECK REPORT (v0)")
    lines.append("timestamp_utc: %s" % report["tool"]["timestamp_utc"])
    lines.append("accepted: %s" % ("YES" if s["accepted"] else "NO"))
    lines.append("ml_used: %s" % ("YES" if report["inputs"]["ml_used"] else "NO"))
    lines.append("mandatory_total: %d" % s["mandatory_total"])
    lines.append("mandatory_pass: %d" % s["mandatory_pass"])
    lines.append("mandatory_fail: %d" % s["mandatory_fail"])
    if s["failed_item_ids"]:
        lines.append("failed_item_ids: %s" % ",".join(s["failed_item_ids"]))
    else:
        lines.append("failed_item_ids: (none)")

    # Include minimal meta fields if present
    meta = report.get("meta", {}) or {}
    for k in ("strategy_id", "run_timestamp_utc", "code_commit", "dataset_id", "params_id"):
        if k in meta:
            lines.append("%s: %s" % (k, str(meta.get(k))))

    lines.append("")
    lines.append("ITEMS (mandatory first):")
    # Sort: mandatory first, then by id
    items = report.get("items", [])
    items_sorted = sorted(items, key=lambda x: (0 if x.get("mandatory") else 1, str(x.get("id", ""))))
    for it in items_sorted:
        if not it.get("applies", True):
            continue
        line = "%s [%s]%s %s" % (
            it.get("id"),
            it.get("status"),
            " (M)" if it.get("mandatory") else "",
            it.get("text", "")
        )
        if it.get("note"):
            line += " | note: %s" % it.get("note")
        lines.append(line)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return json_path, txt_path


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="GS checklist runner (v0) - read-only acceptance report."
    )
    p.add_argument("--checklist", required=True, help="Path to gs_acceptance_checklist.yaml")
    p.add_argument("--evidence", required=True, help="Path to evidence JSON (answers + meta)")
    p.add_argument("--outdir", required=True, help="Output directory for report files")
    p.add_argument("--strict", action="store_true",
                   help="If set, exit code 2 on FAIL; otherwise always exit 0")
    return p


def main() -> int:
    ap = build_argparser()
    args = ap.parse_args()

    if not os.path.isfile(args.checklist):
        print("ERROR: checklist not found: %s" % args.checklist)
        return 1
    if not os.path.isfile(args.evidence):
        print("ERROR: evidence not found: %s" % args.evidence)
        return 1

    try:
        checklist = load_yaml(args.checklist)
    except Exception as e:
        print("ERROR: failed to load checklist yaml: %s" % str(e))
        return 1

    try:
        evidence = load_json(args.evidence)
    except Exception as e:
        print("ERROR: failed to load evidence json: %s" % str(e))
        return 1

    try:
        report = evaluate_checklist(checklist, evidence)
    except Exception as e:
        print("ERROR: evaluation failed: %s" % str(e))
        return 1

    json_path, txt_path = write_report(report, args.outdir)
    accepted = bool(report["summary"]["accepted"])

    print("OK: wrote report json: %s" % json_path)
    print("OK: wrote report txt : %s" % txt_path)
    print("RESULT: accepted=%s" % ("YES" if accepted else "NO"))

    if args.strict and (not accepted):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

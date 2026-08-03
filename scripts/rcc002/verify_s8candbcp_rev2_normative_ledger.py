#!/usr/bin/env python3
"""RCC-002 S8-CAND-BCP-001-REV9 normative-ledger mechanical verifier.

Independently re-derives and verifies the exact 188-entry SHA256SUMS
successor for correction candidate RCC-002-S8-CAND-BCP-001-REV9
(Section 6.7, Section 6.6 step 9). Standard library only.

Run from repository root:
    python3 scripts/rcc002/verify_s8candbcp_rev2_normative_ledger.py
"""
import hashlib
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SCOPE_ID = "RCC002_S8CANDBCP_REV2_NORMATIVE_LEDGER_SCOPE_V1"
CORRECTION_ID = "RCC-002-S8-CAND-BCP-001-REV9"
LEDGER_PATH = "SHA256SUMS"
SCOPE_MANIFEST_PATH = "docs/review/evidence/RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_SCOPE_V1.json"
HISTORICAL_EVIDENCE_PATH = "docs/review/evidence/RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_HISTORICAL_COPY_2026-08-01.txt"
PROTECTED_BUILDER_PATH = "scripts/build_rcc002_spec_bundle.py"

EXPECTED_BASELINE = 145
EXPECTED_ADDED = 43
EXPECTED_REMOVED = 0
EXPECTED_REPLACED = 2
EXPECTED_SUCCESSOR = 188


class LedgerVerificationError(Exception):
    pass


def _parse_ledger_lines(text):
    entries = []
    for lineno, line in enumerate(text.split("\n"), start=1):
        if line == "":
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            raise LedgerVerificationError(f"line {lineno}: malformed ledger line {line!r}")
        digest, path = parts
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise LedgerVerificationError(f"line {lineno}: invalid digest {digest!r}")
        if "\n" in path or "\r" in path:
            raise LedgerVerificationError(f"line {lineno}: control character in path")
        entries.append((path, digest))
    return entries


def load_historical_baseline():
    full_path = os.path.join(REPO_ROOT, HISTORICAL_EVIDENCE_PATH)
    with open(full_path, "r", encoding="ascii", newline="") as f:
        text = f.read()
    entries = _parse_ledger_lines(text)
    if len(entries) != EXPECTED_BASELINE:
        raise LedgerVerificationError(
            f"historical baseline: {len(entries)} entries != expected {EXPECTED_BASELINE}"
        )
    return entries


def load_scope_manifest():
    full_path = os.path.join(REPO_ROOT, SCOPE_MANIFEST_PATH)
    with open(full_path, "r", encoding="ascii") as f:
        manifest = json.load(f)
    if manifest.get("scope_id") != SCOPE_ID:
        raise LedgerVerificationError(f"scope_id mismatch: {manifest.get('scope_id')!r}")
    if manifest.get("correction_id") != CORRECTION_ID:
        raise LedgerVerificationError(
            f"correction_id mismatch: {manifest.get('correction_id')!r}"
        )
    if manifest.get("ledger_path") != LEDGER_PATH:
        raise LedgerVerificationError(
            f"ledger_path mismatch: {manifest.get('ledger_path')!r}"
        )
    if manifest.get("self_entry_excluded") is not True:
        raise LedgerVerificationError(
            "scope manifest does not require ledger self-exclusion"
        )
    for key, expected in (
        ("baseline_entry_count", EXPECTED_BASELINE),
        ("added_entry_count", EXPECTED_ADDED),
        ("removed_entry_count", EXPECTED_REMOVED),
        ("replaced_entry_count", EXPECTED_REPLACED),
        ("successor_entry_count", EXPECTED_SUCCESSOR),
    ):
        if manifest.get(key) != expected:
            raise LedgerVerificationError(
                f"scope manifest {key}={manifest.get(key)!r} != expected {expected}"
            )
    entries = manifest.get("entries", [])
    if len(entries) != EXPECTED_SUCCESSOR:
        raise LedgerVerificationError(
            f"scope manifest entries count {len(entries)} != {EXPECTED_SUCCESSOR}"
        )
    if LEDGER_PATH in entries or ("./" + LEDGER_PATH) in entries:
        raise LedgerVerificationError(
            "scope manifest lists the ledger's own self-entry"
        )
    if (
        PROTECTED_BUILDER_PATH in entries
        or ("./" + PROTECTED_BUILDER_PATH) in entries
    ):
        raise LedgerVerificationError(
            "scope manifest lists the protected builder path"
        )
    if entries != sorted(entries):
        raise LedgerVerificationError("scope manifest entries not in LC_ALL=C order")
    if len(set(entries)) != len(entries):
        raise LedgerVerificationError("scope manifest contains a duplicate entry")
    return entries


def load_successor_ledger():
    full_path = os.path.join(REPO_ROOT, LEDGER_PATH)
    with open(full_path, "r", encoding="ascii", newline="") as f:
        text = f.read()
    entries = _parse_ledger_lines(text)
    paths = [p for p, _ in entries]
    if len(entries) != EXPECTED_SUCCESSOR:
        raise LedgerVerificationError(
            f"successor ledger: {len(entries)} entries != expected {EXPECTED_SUCCESSOR}"
        )
    if len(set(paths)) != len(paths):
        raise LedgerVerificationError("successor ledger contains a duplicate path")
    if paths != sorted(paths):
        raise LedgerVerificationError("successor ledger not in LC_ALL=C order")
    if LEDGER_PATH in paths or ("./" + LEDGER_PATH) in paths:
        raise LedgerVerificationError("successor ledger lists its own self-entry")
    if PROTECTED_BUILDER_PATH in paths or ("./" + PROTECTED_BUILDER_PATH) in paths:
        raise LedgerVerificationError("successor ledger lists the protected builder path")
    return dict(entries)


def verify_hashes(successor_map):
    """Recompute every entry's real byte hash, reading only the exact
    188 named paths and performing no directory traversal."""
    for path, expected_digest in successor_map.items():
        full_path = os.path.join(REPO_ROOT, path)
        if not os.path.isfile(full_path):
            raise LedgerVerificationError(f"ledgered path missing from tree: {path!r}")
        with open(full_path, "rb") as f:
            actual_digest = hashlib.sha256(f.read()).hexdigest()
        if actual_digest != expected_digest:
            raise LedgerVerificationError(
                f"hash mismatch for {path!r}: ledger has {expected_digest}, "
                f"actual file hash is {actual_digest}"
            )


def verify_arithmetic(baseline_entries, scope_paths, successor_map):
    baseline_paths = {p for p, _ in baseline_entries}
    baseline_hashes = dict(baseline_entries)

    added = sorted(p for p in successor_map if p not in baseline_paths)
    removed = sorted(p for p in baseline_paths if p not in successor_map)
    replaced = sorted(
        p for p in successor_map
        if p in baseline_paths and successor_map[p] != baseline_hashes[p]
    )
    unchanged = sorted(
        p for p in successor_map
        if p in baseline_paths and successor_map[p] == baseline_hashes[p]
    )

    if len(added) != EXPECTED_ADDED:
        raise LedgerVerificationError(f"added count {len(added)} != expected {EXPECTED_ADDED}")
    if len(removed) != EXPECTED_REMOVED:
        raise LedgerVerificationError(f"removed count {len(removed)} != expected {EXPECTED_REMOVED}")
    if len(replaced) != EXPECTED_REPLACED:
        raise LedgerVerificationError(f"replaced count {len(replaced)} != expected {EXPECTED_REPLACED}")
    if len(unchanged) != EXPECTED_BASELINE - EXPECTED_REPLACED - EXPECTED_REMOVED:
        raise LedgerVerificationError(
            f"unchanged count {len(unchanged)} != expected "
            f"{EXPECTED_BASELINE - EXPECTED_REPLACED - EXPECTED_REMOVED}"
        )
    if EXPECTED_BASELINE + EXPECTED_ADDED - EXPECTED_REMOVED != EXPECTED_SUCCESSOR:
        raise LedgerVerificationError("hardcoded arithmetic itself does not balance")
    if len(successor_map) != EXPECTED_SUCCESSOR:
        raise LedgerVerificationError("successor total does not match arithmetic")

    if set(successor_map) != set(scope_paths):
        missing = sorted(set(scope_paths) - set(successor_map))
        extra = sorted(set(successor_map) - set(scope_paths))
        raise LedgerVerificationError(
            f"successor ledger does not match ledger scope manifest: "
            f"missing={missing}, extra={extra}"
        )


def main():
    try:
        baseline_entries = load_historical_baseline()
        scope_paths = load_scope_manifest()
        successor_map = load_successor_ledger()
        verify_arithmetic(baseline_entries, scope_paths, successor_map)
        verify_hashes(successor_map)
    except LedgerVerificationError as exc:
        print(f"FAIL: {CORRECTION_ID} normative ledger: {exc}")
        return 1
    print(
        f"PASS: {CORRECTION_ID} normative ledger verified: "
        f"{EXPECTED_BASELINE} baseline + {EXPECTED_ADDED} added - {EXPECTED_REMOVED} removed "
        f"= {EXPECTED_SUCCESSOR} successor entries ({EXPECTED_REPLACED} replaced, count-neutral), "
        f"strict LC_ALL=C order, self-excluded, all hashes independently recomputed and matched."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

# Pre-IU-4 Observation Writer Scaling Evidence — 2026-08-12

## Status

**IMPLEMENTED AND LOCALLY VERIFIED — LINEAR APPEND WRITER, FAIL-CLOSED**

The user explicitly approved
`IU4-OBSERVATION-WRITER-SKALIERUNG FREIGEBEN` on 2026-08-12.

The change is implemented on branch
`codex/iu4-observation-writer-scaling-2026-08-12`, based on the reviewed
10,000-observation baseline at parent commit
`897e35a7d237f5658de0516542a0519831e5b45c`.

IU4 ENFORCED, Exchange, Live, and mutation of the bound source state remain
disabled.

## Corrected scaling defect

The previous writer serialized, atomically replaced, and re-hashed the entire
accumulated observation array after every tick. For `n` records this caused
quadratic `O(n^2)` evidence-write volume.

The corrected writer now uses:

1. one canonical JSONL journal entry appended exactly once per observation;
2. an SHA-256 predecessor chain over all journal entries;
3. a small atomically replaced runtime checkpoint without a `records` array;
4. one complete journal validation and one complete JSON-evidence
   materialization during clean close.

The accumulated write volume is therefore linear `O(n)` plus one linear final
materialization. The in-memory record list remains bounded by the existing
hard maximum of 10,000 records.

## Fail-closed persistence contract

- The journal is created with exclusive-create and append-only file-descriptor
  flags; neither an existing evidence path nor an existing journal path is
  reused.
- Every journal envelope contains its exact sequence, predecessor SHA-256,
  complete observation record, and canonical-entry SHA-256.
- Each append is flushed with `fsync` before the checkpoint advances.
- Before every observation, the writer verifies the complete checkpoint
  SHA-256 and the journal path/descriptor identity, type, inode, device, size,
  modification time, and change time.
- The checkpoint binds record count, journal byte count, running journal
  SHA-256, chain head, repository commit, source fingerprints, record bound,
  and all safety flags.
- Clean close re-reads the journal once and verifies canonical encoding,
  complete-line termination, exact count, exact sequence, predecessor chain,
  per-entry hash, exact in-memory record equality, journal SHA-256, and chain
  head before publishing schema-version-2 final evidence.
- Any detected checkpoint or journal alteration poisons the writer; the stale
  checkpoint is not advanced or converted into final evidence.
- Restart/resume is intentionally not inferred. Any preserved checkpoint or
  journal makes a new launch fail closed and requires explicit operator
  disposition.

## Compatibility and evidence identity

The configured evidence path remains a single JSON object after clean close
and still contains the complete ordered `records` array and canonical
`evidence_fingerprint`. Schema version 2 adds a `writer_contract` object that
binds the retained JSONL journal by filename, SHA-256, byte count, entry
count, chain head, algorithm, and finalized status.

While a run is active, the same evidence path contains the bounded checkpoint
with exact `record_count`, so progress can be read without loading or rewriting
the complete history.

## Verification

```text
Focused observation and safe-launch tests
18/18 passed

tests/live_l1
313/313 passed

tests/regression
170/170 passed

Unique full-suite total
483/483 passed
```

Additional assertions cover:

- constant-shape checkpoint without accumulated records;
- journal prefix preservation and exact append behavior;
- canonical SHA-256 chain continuity;
- final journal/final-evidence fingerprint binding;
- external journal append detection;
- same-size in-place journal mutation detection;
- truncated final-entry detection;
- poisoned-writer checkpoint preservation;
- idempotent clean close; and
- fail-closed restart collision for either artifact path.

`py_compile` and `git diff --check` passed. The foreign untracked file
`scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or
committed.

## Scope boundary and next gate

This change corrects only observation-evidence persistence scaling. It does not
authorize a longer observation, Workstation execution, IU4 ENFORCED, Exchange,
Live, source-state mutation, or automatic crash recovery.

The next gate is the explicit integration of the reviewed 10K baseline and
this writer-scaling branch into `main`. A materially longer SHADOW observation
requires a separate authorization after that integration.

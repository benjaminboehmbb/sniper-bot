# Pre-IU-4 SHADOW Dry-Run Harness Evidence — 2026-08-09

## Status

**IMPLEMENTED AND LOCALLY VERIFIED; ISOLATED SHADOW ONLY**

Branch: `codex/pre-iu4-shadow-dry-run-harness-2026-08-09`

IU-4 ENFORCED, Exchange, and Live remain locked. The harness is not imported by
the active L1 loop, `safe_launch.py`, or any active startup path.

## Isolation boundary

`PaperIU4ShadowDryRunHarness` accepts only a passed, read-only `SHADOW` startup
gate decision. It rejects OFF, ENFORCED/mutating, failed, or stale decisions.

For each run the harness:

1. reconciles the source atomic snapshot and WAL;
2. proves that the source state fingerprint and transaction sequence still
   equal the prior SHADOW gate decision;
3. hashes every source snapshot/WAL file by relative path, byte length, and
   SHA-256;
4. copies those validated files into a newly created temporary directory;
5. proves the copy is an exact reconciled aggregate state;
6. runs the real IU-4 adapter only against that temporary coordinator;
7. reconciles the resulting sandbox state;
8. deletes the entire temporary directory;
9. re-hashes and re-loads the source and requires byte-identical equality.

The source paths are never opened for writing. A configured work directory
inside the source coordinator root is rejected. Symlinked source snapshots,
journals, or transaction files are rejected.

## Replay contract

`IU4ShadowIntentStepV1` supplies the source intent, reason, target system state,
timestamp, tick, Decimal-compatible prices, stop, and trade identity. At each
step the harness binds a fresh content-addressed adapter request to the exact
current sandbox-state fingerprint.

This supports deterministic sequential prediction without precomputing future
state fingerprints. Duplicate source intent IDs within one run are rejected.
Invalid step boundaries fail the run and the disposable sandbox is removed.

The report contains:

- source manifest and before/after state fingerprints;
- final sandbox state fingerprint;
- source and sandbox transaction sequences;
- simulated transaction delta;
- committed, NOOP, and rejected counts;
- complete immutable adapter outcomes.

## Verified behavior

- FLAT BUY predicts one Decimal OPEN_LONG without changing the source.
- OPEN_LONG, HOLD, CLOSE_LONG produces two atomic transactions and one NOOP.
- An opposing intent closes only; there is no same-step reversal.
- Repeating the same run produces an equal report.
- HARD kill rejects a predicted entry without a sandbox transaction.
- EMERGENCY kill still allows a predicted CLOSE and preserves exit permission.
- Stale gate state, corrupt source binding, invalid steps, duplicate intents,
  unsafe work paths, and non-SHADOW gate decisions fail closed.
- Empty and non-empty runs leave no temporary artifacts behind.

## Verification

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest \
  tests.live_l1.test_paper_iu4_shadow_harness

Ran 10 tests — OK
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/live_l1 -p 'test_*.py'

Ran 219 tests — OK
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/regression -p 'test_*.py'

Ran 170 tests — OK
```

Static import search returned no active `live_l1` importer of
`live_l1.core.paper_iu4_shadow_harness`.

## Scope boundary

This unit provides an in-memory report from a temporary atomic clone. It does
not ingest live logs automatically, persist SHADOW outcomes, wire into the
active loop, enable ENFORCED, alter the accepted PEE profile, or send
exchange/live orders. A separate replay-input and evidence-export contract is
required before workstation full-history SHADOW validation.

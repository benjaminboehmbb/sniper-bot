# Pre-IU-4 Replay Evidence Export — 2026-08-09

## Status

**IMPLEMENTED AND LOCALLY VERIFIED; ISOLATED SHADOW ONLY**

Branch: `codex/pre-iu4-replay-evidence-export-2026-08-09`

IU-4 ENFORCED, Exchange, and Live remain locked. The replay loader and exporter
are not imported by the active L1 loop, `safe_launch.py`, or an active startup
path.

## Replay input contract

`load_iu4_replay_jsonl()` accepts only a regular, non-symlink UTF-8 JSONL file
with at least one step. Every line must contain exactly the versioned
`IU4ShadowIntentStepV1` fields.

The boundary rejects:

- JSON floats, NaN, and infinity; prices use canonical decimal strings or
  integers and become `Decimal` values;
- missing, unknown, malformed, blank, or non-object records;
- invalid intent, timestamp, tick, price, stop, or schema values;
- duplicate source intent IDs;
- timestamps or tick IDs that are not strictly increasing.

The loaded replay binds the exact raw input bytes by SHA-256, byte count, line
count, and logical filename.

## Evidence export contract

`export_iu4_replay_evidence()` runs the validated steps through the existing
isolated `PaperIU4ShadowDryRunHarness`. It records:

- raw input identity and replay identity;
- source manifest and before/after source state fingerprints;
- final sandbox state fingerprint and transaction sequences;
- committed, NOOP, rejected, and simulated-transaction counts;
- each content-addressed request and outcome;
- each outcome's aggregate, position, account, throttle, and S4 risk
  fingerprints, position/trade identity, KILL level, and entry/exit gates;
- a canonical evidence fingerprint and a whole-file SHA-256.

The caller supplies the replay ID and canonical generation timestamp. The
export therefore does not depend on a clock, environment variable, network,
Exchange, or Live system.

## Persistence and isolation

Evidence is encoded as canonical JSON and published in the target directory by
a durable, atomic no-clobber operation. A byte-identical repeat is idempotent
and leaves the existing inode and modification time unchanged. Different
existing evidence is a hard conflict and is never overwritten.

Input/output collisions, output inside the source coordinator root, missing or
symlinked output directories, and symlinked output files fail closed. An
injected publication interruption leaves neither a partial evidence file nor a
temporary file. The source atomic snapshot and WAL remain byte-identical.

## Verification

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest \
  tests.live_l1.test_paper_iu4_replay_evidence \
  tests.live_l1.test_paper_iu4_shadow_harness

Ran 18 tests — OK
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/live_l1 -p 'test_*.py'

Ran 227 tests — OK
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/regression -p 'test_*.py'

Ran 170 tests — OK
```

`git diff --check` and bytecode compilation passed. Static import search found
no active `live_l1` importer of either the SHADOW harness or replay exporter.

## Scope boundary

This unit validates a prepared replay file and creates immutable SHADOW
evidence from a disposable atomic clone. It does not generate intents from the
full-history market dataset, activate IU-4, alter the accepted PEE profile,
write source Paper state, or send Exchange/Live orders.

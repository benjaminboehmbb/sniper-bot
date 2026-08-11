# Pre-IU-4 Replay Pipeline Smoke Evidence — 2026-08-09

## Status

**LOCAL END-TO-END SMOKE PASSED; ISOLATED SHADOW ONLY**

Branch: `codex/pre-iu4-replay-pipeline-smoke-2026-08-09`

IU-4 ENFORCED, Exchange, and Live remain locked. The pipeline runner is not
imported by the active L1 loop, `safe_launch.py`, or an active startup path.

## Proven chain

`run_iu4_replay_pipeline_smoke()` executes the complete local chain:

1. read and hash one completed structured L1 log;
2. build strict replay JSONL plus immutable source/replay manifest;
3. create an isolated `PaperIU4ShadowDryRunHarness` from an already-passed,
   read-only SHADOW startup-gate decision;
4. replay every intent only against a disposable atomic clone;
5. export immutable per-step replay evidence;
6. re-read and validate every manifest, fingerprint, and whole-file SHA-256;
7. prove that the L1 log and atomic source snapshot/WAL remain byte-identical;
8. publish an immutable no-clobber pipeline receipt.

No clock, environment lookup, network, Exchange, or Live service is used by
the pipeline runner. Replay identity and generation time are explicit inputs.

## Real L1 smoke scenario

The integration test runs the actual active L1 paper loop over three canonical
CSV market rows with its established test-intent controls. The resulting real
structured L1 log contains:

```text
BUY → SELL → BUY
```

The builder preserves exact Decimal price text and the isolated IU-4 SHADOW
replay produces:

```text
OPEN_LONG → CLOSE_LONG → OPEN_LONG
```

Observed result:

- 3 replay steps;
- 3 committed SHADOW outcomes;
- 0 NOOP outcomes;
- 0 rejected outcomes;
- 3 simulated atomic transactions;
- source atomic transaction sequence remains `0`;
- source atomic position remains `FLAT`;
- source L1 log, atomic snapshot, and WAL remain byte-identical.

## Receipt contract

The canonical receipt binds:

- L1 source-log SHA-256 and size;
- atomic coordinator identity, state fingerprint, transaction sequence, and
  source-file-manifest fingerprint;
- replay JSONL, input manifest, and evidence SHA-256 and size;
- outcome counts and final sandbox fingerprint;
- individual Boolean checks for every source → manifest → replay → evidence
  link and all source non-interference claims;
- explicit `false` flags for IU-4 ENFORCED, Exchange, and Live;
- a canonical receipt fingerprint and whole-file SHA-256.

An identical rerun reuses all four artifacts byte-for-byte without changing
inode or modification time. Path collisions, output inside the atomic source,
symlinks, conflicting artifacts, invalid fingerprints, broken hash links, or
source mutation fail closed and never overwrite evidence.

## Verification

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest \
  tests.live_l1.test_paper_iu4_replay_pipeline \
  tests.live_l1.test_paper_iu4_replay_input \
  tests.live_l1.test_paper_iu4_replay_evidence \
  tests.live_l1.test_paper_iu4_shadow_harness \
  tests.live_l1.test_paper_economics_shadow_runtime

Ran 39 tests — OK
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/live_l1 -p 'test_*.py'

Ran 239 tests — OK
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/regression -p 'test_*.py'

Ran 170 tests — OK
```

`git diff --check` and bytecode compilation passed. Static import search found
no active importer of `paper_iu4_replay_pipeline`.

## Scope boundary

This proves the complete chain on a small local dataset. It does not validate
full history, performance, restart-scale throughput, production configuration,
or operational activation. The next gated step is a larger X1 replay dataset;
the workstation full-history run remains deferred until explicitly authorized
and available.

# Pre-IU-4 Workstation Full-History SHADOW Gate Evidence — 2026-08-13

## Status

**1,042,658-RECORD WORKSTATION SHADOW GATE DEFINED AND LOCALLY VERIFIED — RUN NOT STARTED**

The user explicitly approved
`IU4-WORKSTATION-FULL-HISTORY-SHADOW-GATE-DEFINITION FREIGEBEN` after the
passing X1 100K SHADOW retest evidence was integrated into `main`. This unit
defines the next bounded gate. It does not prepare inputs, transfer artifacts,
connect to the Workstation, or start an observation.

## Gate contract

- execution host: `WORKSTATION` only;
- requested observations: exactly `1,042,658`;
- observation mode: `SHADOW` under operational profile `PAPER`;
- IU4 adapter scope: `DISPOSABLE_SANDBOX_ONLY`;
- bound atomic source: read-only;
- source-state mutation allowed: `false`;
- approved throttle profile remains mandatory;
- evidence persistence: hash-chained append journal plus atomic checkpoint;
- final evidence: schema version 2 with bound journal identity;
- IU4 ENFORCED: disabled;
- Exchange: disabled;
- Live: disabled.

The hard implementation ceiling is raised only from `100,000` to `1,042,658`.
The exact boundary is accepted only with explicit configuration and
`requested_max_ticks <= configured_max_records`. `1,042,659` and every larger
value remain rejected fail-closed.

## Immutable input and policy authorities

The separately authorized run must bind and independently re-hash:

- immutable full-history source CSV SHA-256:
  `2896badb62e3236df301a1ccf56b878916c48b22ff57483e86b9fc32bffaf104`;
- exact valid one-minute observations: `1,042,658`;
- previously validated normalized full-history slice SHA-256:
  `902d10b1d7678777bd23140ff459b9c5eaa9ef7d968bab7ab6e09926bfbfba8a`;
- approved throttle profile ID: `PEE_RATE_OBSERVED_BOUNDARY_001`;
- approved throttle profile SHA-256:
  `b16566970a3d7db4b038085d0b8601e24721fae572fbe7d3159c071680cd91e7`;
- canonical throttle policy fingerprint:
  `ed6e55744ce76d4f2e159832a2aeebcd4dbeb0f5dc1cdbbfda6177af119d1ada`;
- 5-minute seed SHA-256:
  `6a07c0e6ca24cfd7b9e6bdea3562a7e505cf922e07a54c85dac6ff97473ef5e5`;
- economics profile SHA-256:
  `f65f00038c9420d09b7f4a0f8c28cc81a7f38998cdce52fd4f1619f89cffbc86`.

No temporary or regenerated input may be trusted without a new whole-file
hash and manifest. Source and normalized hashes must match before and after
the run.

## Resource and restart boundary

The passing 100K retest produced approximately:

- final evidence: `110 MiB`;
- records journal: `137 MiB`;
- captured stdout: `232 MiB`;
- legacy runtime directory: `233 MiB`.

Linear full-history projection is below `8 GiB` including the bound worktree
and small control artifacts. Before launch, the Workstation must demonstrate
at least `25 GiB` free on the target filesystem. The launcher must publish a
durable start timestamp, stdout, stderr, progress checkpoint, finish timestamp,
and exit-code file outside the transient process. A disconnected SSH session
must not terminate the job.

This definition does not authorize resume from a partial journal. Any future
resume mechanism requires its own explicit contract and fault-injection gate.
Without that separate authority, an interrupted run remains evidence and a
new run must use new output paths.

## Required run acceptance checks

Any separately authorized Workstation full-history SHADOW observation must
validate all of the following:

1. process exit code `0` and no runtime error, traceback, or failure markers;
2. exactly `1,042,658/1,042,658 (100.00%)` ordered records;
3. exact observation sequence and tick IDs `1..1,042,658`;
4. `1,042,658/1,042,658` unique source-intent IDs and IU4 request IDs;
5. final evidence fingerprint plus journal count, byte length, SHA-256,
   entry-chain head, and complete journal-chain validation;
6. unchanged atomic-source bytes, manifest fingerprint, state fingerprint,
   and transaction sequence;
7. unchanged market input and normalized-slice hashes before and after;
8. approved throttle, economics, seed, repository-commit, launcher, and host
   bindings;
9. position-before, action, and position-after parity true for every record;
10. every autonomous exit fully accounted as a matching committed close or
    complete state-identical guard-divergence NOOP;
11. every loss-cluster blocked entry represented as source entry intent,
    observed `HOLD`, Legacy `NOOP`, IU4 `NOOP`, and state-identical
    `FLAT -> FLAT`;
12. zero unbound autonomous-exit suppression and zero hidden divergence;
13. final Legacy position equals final IU4 sandbox position and both are
    `FLAT`; and
14. SHADOW/PAPER safety fields remain exact: source mutation `false`,
    IU4 ENFORCED `false`, Exchange `false`, and Live `false`.

Any mismatch is a fail-closed result. It must not be reclassified, suppressed,
or used to weaken parity, throttle, loss-cluster, or source-integrity gates.

## Verification

```text
Focused observation-gate tests
18/18 passed

tests/live_l1
316/316 passed

tests/regression
170/170 passed

Unique full-suite total
486/486 passed
```

Python compilation of the changed runtime and test modules passed.
`git diff --check` passed.

The foreign untracked file `scripts/build_rcc002_spec_bundle.py` remains
outside scope and must not be read, modified, staged, or committed.

## Next gate

After branch integration, the only separately authorized next action is
`IU4-WORKSTATION-FULL-HISTORY-SHADOW-OBSERVATION FREIGEBEN`. That authorization
may prepare hash-bound inputs, verify Workstation resources, transfer the exact
commit, and start only this bounded PAPER SHADOW observation. It does not
authorize IU4 ENFORCED, Exchange, Live, source-state mutation, or resume.

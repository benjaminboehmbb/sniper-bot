# Pre-IU-4 Throttle Contract Evidence — 2026-08-09

## Status

**CONTRACT AND PERSISTENCE IMPLEMENTED; NOT RUNTIME-ACTIVE**

Branch: `codex/pre-iu4-throttle-contract-2026-08-09`

This change does not authorize or activate IU-4, Exchange, or Live. It does not
select production throttle thresholds and does not change the accepted PEE V1
economics profile or fingerprint.

## Implemented scope

`live_l1/core/paper_entry_throttle.py` provides:

- a strict, versioned, profile-bound `PaperEntryThrottlePolicy`;
- canonical SHA-256 policy and state fingerprints;
- immutable accepted-entry events with monotone sequence and predecessor chain;
- persistent throttle state for UTC-day count, rolling-window events, and last
  accepted entry;
- deterministic daily-limit, rolling-window, and re-entry-cooldown evaluation;
- stable fail-closed reason codes while exits remain allowed;
- whole-second ISO-8601 UTC timestamps consistent with the binding L1 time
  standard;
- pure state transition logic without file, environment, network, or local-clock
  access.

`live_l1/state/paper_entry_throttle.py` provides:

- immutable entry-event envelopes;
- journal-before-snapshot atomic persistence;
- exact-once retry behavior;
- restart recovery after interruption between journal and snapshot writes;
- policy, event-ID, sequence, predecessor, filename, fingerprint, and resulting
  state reconciliation;
- deterministic re-evaluation of every journal transition;
- fail-closed reconciliation for missing, corrupt, mismatched, gapped,
  conflicting, or non-reproducible state.

No active loop file was changed. No policy profile with operational values was
created.

## Boundary semantics

- An accepted entry at the UTC-day limit blocks further entries until the next
  UTC midnight.
- The rolling window is `(candidate_time - window, candidate_time]`; an event
  exactly at the lower boundary has expired.
- Re-entry is allowed exactly at `last_entry_time + cooldown`.
- Candidate timestamps that move backwards fail closed.
- State and journal time use canonical UTC seconds; sub-second values are
  rejected.
- Exits remain allowed under every throttle denial and reconciliation failure.

## Verification

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest \
  tests.live_l1.test_paper_entry_throttle

Ran 24 tests — OK
```

The suite covers policy validation and fingerprinting, UTC normalization,
daily reset, exact rolling-window and cooldown boundaries, simultaneous limits,
policy mismatch, backward time, bounded retained state, atomic commit,
idempotent duplicate handling, duplicate-ID conflict, interrupted-write
recovery, restart reconciliation, corrupt JSON, unsupported schema,
state-ahead-of-journal, and non-reproducible journal transitions.

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/live_l1 -p 'test_*.py'

Ran 111 tests — OK
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/regression -t .

Ran 170 tests — OK
```

`py_compile` for both new runtime modules and the new test module passed.

## Remaining gates

1. Calibrate daily, rolling-window, and cooldown values from the IU-3
   full-history evidence on the workstation.
2. Approve a named throttle policy profile and its fingerprint.
3. Specify and test the atomic ownership boundary between throttle commit and
   the S2 entry mutation before wiring the contract into the active loop.
4. Run full-history shadow validation with the selected policy.
5. Archive `cost_guards.py` only after the new path is active, verified, and a
   final usage audit confirms no remaining consumer.

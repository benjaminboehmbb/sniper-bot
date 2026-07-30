# RCC-002 S6 Independent Review Resolution

## Document metadata

| Field | Value |
|---|---|
| Document ID | `RCC-002-S6-IRR-RES-001` |
| Date | 2026-07-30 |
| Scope | S6 independent-review findings |
| Implementation baseline | Repository `e0eecfd` plus uncommitted S6 package |
| Review package SHA-256 | `c19062b326663f347681e8cfc2f1e50ce44db2cda55558ad685157facaaa1256` |
| Claude report SHA-256 | `dfdcc47b4c40c9119005a2f2158b4a96a9ddbd3e0dbcaeea980fb4f9007fbe43` |
| Resolution status | `ALL FINDINGS CLOSED — NO CODE CHANGE REQUIRED` |

## 1. Evidence considered

The disposition uses:

- the certified RCC-002 specification bundle and manifest;
- the governing DVSEV-001 certification decision;
- the certified S5 implementation decision;
- the exact S6 source and tests in the verified review package;
- 49 S6, 524 RCC-002, and 170 regression tests;
- Claude's independent 327-case oracle with zero mismatches;
- targeted independent dominance, abort, causality, prefix, partition, schema,
  preservation, and container-identity checks.

The two Gemini ZIP responses are excluded because they attributed fabricated
classes, functions, enums, reason codes, and tests to the package. Gemini's
final source-bundle response is recorded only as a process failure, not as
technical evidence.

## 2. Finding dispositions

### 2.1 `S6-CLAUDE-001` — `GATE_INPUT_INVALID` fallback

Claude observed that the final fallback in
`rcc002/s6/compute.py::_invalid_profile_reasons` is unreachable under the
three registered baseline profiles.

**Disposition:** `CLOSED — INTENTIONAL DEFENSIVE RESERVE; NOT A DEFECT`.

Reasoning:

1. RG specification section 19.2 requires `GATE_INPUT_INVALID` to be present
   in the complete S6 registry.
2. Section 20.5 assigns it to "other row-level invalid required inputs".
3. The three baseline profiles in section 18.5 currently have no such
   additional required input: every invalid baseline input maps more
   specifically to regime or trend-strength reasons.
4. Therefore non-emission for all currently producible baseline rows is the
   correct behavior.
5. The fallback cannot alter current output because typed `S5Row/1.0.0`
   validation and the registered profile-input predicates make the branch
   unreachable.
6. Any future profile or required-input expansion requires a new registered
   profile/version and renewed review; it cannot silently activate this branch
   within the certified baseline.

Removing the branch would reduce defensive alignment with section 20.5.
Artificially emitting the code for an existing profile would violate the more
specific mapping rules. No source or test correction is required.

### 2.2 `S6-CLAUDE-002` — registered `GATE_STATE_INVALID`

Claude observed that `GATE_STATE_INVALID` is registered but no baseline trigger
is specified or implemented.

**Disposition:** `CLOSED — SPECIFICATION-REGISTERED RESERVED CODE; NOT AN
IMPLEMENTATION DEFECT`.

Reasoning:

1. RG specification section 19.2 explicitly requires
   `GATE_STATE_INVALID` at priority 80.
2. Sections 20.4–20.6 define no baseline emission condition for that code.
3. The implementation correctly registers it and does not invent an
   unspecified trigger.
4. Registry completeness and exact priorities are directly tested.
5. The generic reason-code normalizer and directional validator cover every
   registered neutral code by construction.
6. Claude found no incorrect output in 327 independent oracle cases.

Defining a new trigger would be a specification change, not an implementation
correction. The code remains reserved until a separately reviewed
specification revision defines a trigger.

## 3. Implementation disposition

| Severity | Reported | Accepted as defect | Open |
|---|---:|---:|---:|
| CRITICAL | 0 | 0 | 0 |
| MAJOR | 0 | 0 | 0 |
| MINOR | 2 | 0 | 0 |
| EDITORIAL | 0 | 0 | 0 |

No code, schema, profile, reason-code, test, or documentation correction is
required to make the S6 implementation conformant.

## 4. Decision

```text
ALL FINDINGS CLOSED
NO ACCEPTED IMPLEMENTATION DEFECT
NO CORRECTED RE-REVIEW REQUIRED
APPROVED FOR IMPLEMENTATION CERTIFICATION
```


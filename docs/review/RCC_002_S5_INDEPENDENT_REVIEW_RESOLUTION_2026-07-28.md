# RCC-002 S5 Independent Review Resolution

Date: 2026-07-28

Scope: Claude and Gemini independent reviews of the RCC-002 S5
implementation

Resolution status: corrections implemented; independent re-review required

## 1. Normative hierarchy

The adjudication uses:

1. the certified DVSEV-001 full specification bundle;
2. the certified bundle manifest and certification decision;
3. the S5 Implementation Readiness Review, which resolved implementation
   details before code was written;
4. source code and independently executable tests.

Review assertions and implementation-record assertions are evidence inputs,
not normative authority.

## 2. Claude findings

### CLD-S5-001 — Not confirmed

Claim: a segment boundary must not record a transition from a previously
valid effective regime to `UNKNOWN`.

Resolution: rejected.

Specification section 9.6 explicitly states:

```text
Der Wechsel eines zuvor gültigen effektiven Zustands nach UNKNOWN ist ein
tatsächlicher Übergang und wird mit transition_to=UNKNOWN protokolliert.
```

It then states that no transition exists at segment start when both the
previous and current states are `UNKNOWN`. This distinction would be
unnecessary if all segment boundaries unconditionally suppressed transition
metadata.

Sections 9.3 and 27.1 require the current persisted state machine to reset.
The implementation does reset the resulting current effective state,
candidate and count to `UNKNOWN`, `UNKNOWN`, and `0`. Retaining the previous
effective value solely long enough to populate `regime_transition_from`
implements section 9.6; it does not carry the previous state forward as the
current regime.

The pre-implementation readiness binding independently records:

- a valid state to `UNKNOWN` is a transition;
- `UNKNOWN` to the first confirmed valid state is a transition;
- `UNKNOWN` to `UNKNOWN` at initial dataset start is not a transition.

No code change is authorized for this finding. Regression tests now state
both segment-boundary cases explicitly:

- confirmed `SIDE` to `UNKNOWN`: transition is recorded;
- `UNKNOWN` to `UNKNOWN`: transition fields remain null.

### CLD-S5-002 — Confirmed

Claim: `REG_EFFECTIVE_UNCONFIRMED` was emitted during general warm-up even
when `regime_raw=UNKNOWN`.

Resolution: accepted and corrected.

Specification section 12.7.1 limits the code to the interval in which a
valid raw regime has not yet confirmed its first effective state. The
implementation now requires:

```text
regime_raw != UNKNOWN
AND regime_effective == UNKNOWN
```

Tests verify absence during slope warm-up and presence on the first valid
candidate row.

### CLD-S5-003 — Not confirmed

Claim: four additional State profile identity fields create an unspecified
hash interoperability risk.

Resolution: rejected.

Specification section 28 defines the snapshot fields as a minimum, not an
exact closed list. The pre-implementation readiness binding section 10.1
explicitly registers:

```text
state_profile_id=RCC002_S5_SMA200_CONTEXT_V1
state_profile_version=1.0.0
state_hash_profile_id=RCC002_S5_STATE_HASH_V1
state_hash_profile_version=1.0.0
```

Readiness section 10.4 explicitly requires SHA-256 over all snapshot fields
except `state_payload_sha256`. Independent implementations using the same
registered state and hash profiles therefore have an exact interoperable
payload contract.

No code change is authorized.

### CLD-S5-004 — Accepted editorial clarification

The numeric tolerances now carry a source comment stating that they govern
independent cross-implementation comparisons. Internal threshold decisions
remain exact and unrounded.

### CLD-S5-005 — Process note accepted

The original ZIP SHA-256 was verified on the target X1 before extraction.
Future review packages should additionally contain a per-file checksum
manifest so reviewers working only from extracted content can verify the
complete package identity.

## 3. Gemini findings

### FIND-S5-CRIT-01 — Reclassified and hardened

Claim: shared mutable `indicators` and `signals` dictionaries violate
row-preservation and constitute a critical defect.

Resolution: the critical classification and claimed normative violation are
not confirmed. The certified physical row-preservation contract requires
unchanged values, keys, order and segments; it does not define Python heap
reference identity. S3 and S4 deliberately use dictionary containers in
their established in-memory representation.

Nevertheless, shared container references present an avoidable downstream
mutation risk. The implementation now creates independent shallow dictionary
containers for S5. Their values are frozen `IndicatorField` and
`SignalField` instances, so no deep copy is required. A regression test
mutates both S5 containers and verifies that the upstream S4 containers
remain unchanged.

Final classification: `MINOR`, corrected.

### FIND-S5-MAJ-01 — Not confirmed

Claim: `REG_SEGMENT_RESET` may be suppressed by concurrent input failures.

Resolution: rejected.

The implementation adds `REG_WINDOW_CROSSES_INDICATOR_SEGMENT` and
`REG_SEGMENT_RESET` at the beginning of reason accumulation, before all
current-row input checks. Canonical normalization retains all applicable
codes. The serial/partition boundary test explicitly asserts presence of
`REG_SEGMENT_RESET` and full row equality.

No suppressing branch exists.

### FIND-S5-MIN-01 — Not confirmed

Claim: context lists should combine their field-local invalidity code with
`REG_INPUT_INVALID`.

Resolution: rejected.

Specification section 12.7.2 requires:

- `trend_strength_reason_codes` contains exclusively
  `REG_TREND_STRENGTH_INPUT_INVALID` when ADX is invalid;
- `volatility_relative_reason_codes` contains exclusively
  `REG_VOLATILITY_INPUT_INVALID` when the ATR-relative input is invalid.

Adding `REG_INPUT_INVALID` would violate both the target registry and the
explicit exclusivity rule. The schema validator correctly rejects such
cross-target mixing.

### FIND-S5-EDIT-01 — No action required

String formatting and line wrapping have no runtime or normative effect and
do not create ambiguity in registered values.

## 4. Corrected verification result

Executed after correction:

```text
python3 -m compileall -q rcc002/s5 tests/rcc002/s5
PASS

python3 -m unittest discover -s tests/rcc002/s5 -t .
Ran 69 tests
OK

python3 -m unittest discover -s tests/rcc002 -t .
Ran 475 tests
OK
```

The target X1 must additionally rerun the 170-test regression collection,
which was not present in the supplied implementation archive.

## 5. Re-review gate

No commit or publication decision is authorized by this resolution.

The corrected implementation must receive focused independent re-reviews
from Claude and Gemini. Each re-review must:

1. verify the two implemented corrections;
2. evaluate this resolution against the cited normative text;
3. state whether any unresolved `CRITICAL` or `MAJOR` finding remains;
4. issue one of `APPROVED`, `APPROVED WITH MINOR CORRECTIONS`, or `REJECTED`.


# RCC-002 S5 Implementation Readiness Review

## Document Control

| Field | Value |
|---|---|
| Document Class | Stage-Specific Implementation Readiness Review |
| Project | RCC-002 Scientific Data Processing Architecture |
| Review Date | 2026-07-28 |
| Scope | `S5_REGIMES` only |
| Explicitly Out of Scope | `S6_GATES`, reports, publication execution, legacy-regime implementation, S7/S8, strategy and execution logic |
| Certified Specification Bundle | `docs/review/RCC_002_DVSEV001_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md` |
| Certified Bundle SHA-256 | `8a6ab7d732e02727199e704313c38959161c3929441fddce34b4ee4f2586d9ee` |
| Certified Bundle Manifest | `docs/review/RCC_002_DVSEV001_CORRECTED_BUNDLE_MANIFEST_2026-07-27.md` |
| Certified Manifest SHA-256 | `176d99582ebff741d5d45b7fccc76a49b5b1d267ce350d867d4f64c17c6a8297` |
| Certification Decision | `docs/certification/RCC_002_DVSEV001_CERTIFICATION_DECISION_2026-07-27.md` |
| Certification Decision SHA-256 | `d07068f32e1741d0821fe430542e10625105f4d8ef6d87aa47ea7766be93e2e0` |
| Regime and Gate Specification | `RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md`, Version `0.5.1` |
| Repository Baseline | `main`, commit `7249bd69746a348ffc76d5232fd4a3b054f1fcd9` |
| Review Result | **IMPLEMENTATION READY — S5 ONLY** |

---

## 1. Decision

```text
IMPLEMENTATION READY — S5_REGIMES
```

No specification ambiguity blocks implementation of the canonical S5
baseline.

The normative S5 rules, field inventory, enums, state machine, reason-code
registry, validity semantics, row-preservation contract, causal slope,
context classifications and test requirements are sufficiently complete.

The parameters explicitly delegated by Regime and Gate Specification §37.1
are bound below as versioned implementation-level governance. These bindings:

- do not modify a certified specification;
- do not introduce a new regime rule;
- do not alter any certified threshold;
- do not add S6 gate logic;
- remain subordinate to the certified specification;
- require a new review if their semantic behavior changes.

This decision does not authorize S6 implementation. S6 requires its own
readiness review after S5 is implemented and validated.

---

## 2. Verified Baseline

### 2.1 Repository and S4

The supplied implementation package was checked against the S4 handover.
The following SHA-256 values match exactly:

| File | SHA-256 |
|---|---|
| `rcc002/s4/constants.py` | `918dcc041adb5d5e07f6354691b23fb15f66022a68a81f1faeaeb55798be0c95` |
| `rcc002/s4/compute.py` | `10bc615d0c0e06c7bacc877541e106a6130f821456a5885261033b0265cf1a13` |
| `tests/rcc002/s4/test_compute.py` | `f99d64617a845e3f00dd11adad2366bbb101f45283cdcb4e5a9f983f71c5c786` |

No `rcc002/s5/` implementation exists in the reviewed baseline.

### 2.2 DVSEV-001 implementation alignment

The implementation already contains:

- the complete 32-code `REASON_CODE_SEVERITY` registry;
- the certified §16.3 severity values;
- `DV_FILE_SUSPECTED_ROW_LIMIT_TRUNCATION=ERROR` as the default;
- conditional escalation of that finding to `CRITICAL`;
- `QUALITY_RULE_VERSION=RCC002_QUALITY_RULE_V1`;
- deterministic reason-code ordering;
- fail-closed blocking of all active `WARN`, `ERROR` and `CRITICAL` codes
  absent an approved non-blocking warning profile;
- corresponding unit tests.

The code therefore reflects the certified DVSEV-001 state.

### 2.3 Test execution

The reduced implementation package compiled successfully.

`unittest` executed 406 RCC-002 tests:

- 404 passed;
- two package-identity tests could not open the certified bundle and manifest
  because the reduced implementation ZIP intentionally omitted `docs/`;
- both expected hashes were independently recomputed from the separately
  supplied certified artifacts and matched the code constants exactly.

The two errors are packaging-context errors in the review copy, not failures
of the repository baseline.

---

## 3. Stage Ownership

S5 owns only:

- raw trend-regime classification;
- persisted effective regime;
- candidate state and confirmation count;
- transition metadata;
- causal SMA200 slope;
- directionless ADX trend-strength classification;
- directionless relative-volatility classification;
- S5 model/schema metadata;
- S5 validity and reason codes;
- S5 state snapshot.

S5 must not create or evaluate:

- `allow_long`;
- `allow_short`;
- `data_gate_pass`;
- `gate_state`;
- S6 gate reason codes;
- timing-score aggregation;
- MFI entry filtering;
- entry persistence;
- cooldown;
- loss-cluster gates;
- exits, TP, SL or time stops;
- position sizing;
- forward returns or labels.

---

## 4. Canonical Inputs

S5 accepts only:

```text
rcc002.stage.s4-signals/1.0.0
```

The implementation consumes `S4Row` and obtains the required values as
follows:

| Normative field | In-memory source |
|---|---|
| `close` | `S4Row.close` |
| `sma_close_200` and companions | `S4Row.indicators["sma_close_200"]` |
| `adx_wilder_14` and companions | `S4Row.indicators["adx_wilder_14"]` |
| `state_atr_relative_d` and companions | `S4Row.signals["state_atr_relative_d"]` |
| `score_atr_relative_c` and companions | `S4Row.signals["score_atr_relative_c"]` |
| `state_adx_strength_d` and companions | `S4Row.signals["state_adx_strength_d"]` |
| `score_adx_strength_c` and companions | `S4Row.signals["score_adx_strength_c"]` |
| S3 metadata | inherited `S3Row` fields |
| S4 metadata | direct `S4Row` fields |

The grouped in-memory representation does not change the normative flat
physical schema.

Before calculation, S5 must reject the batch if:

- a row is not an `S4Row`;
- S4 schema ID/version/reference is not exact;
- S4 profile ID/version is not exact;
- required S3/S4 field groups are absent or noncanonical;
- a key is duplicated;
- keys are not in canonical ascending order;
- the call contains more than one `(market_type, symbol, interval)` series;
- validity/value/reason-code combinations contradict their registered schema;
- `market_segment_id` or `indicator_segment_id` is empty;
- the interval has no registered duration;
- upstream publication eligibility is explicitly supplied as non-passing.

The canonical V1 implementation supports the already registered `1m`
interval. Any other interval is rejected until an interval-duration
compatibility rule is registered.

---

## 5. Canonical S5 Output

S5 produces:

```text
rcc002.stage.s5-regimes/1.0.0
```

All S4 fields are preserved unchanged. S5 appends exactly the 21 fields from
Regime and Gate Specification §12.2 in the specified order.

The implementation must expose immutable enums:

```text
RegimeState:
    BULL
    SIDE
    BEAR
    UNKNOWN

TrendStrength:
    WEAK
    DEVELOPING
    STRONG
    UNKNOWN

VolatilityRelative:
    BELOW_REFERENCE
    AT_REFERENCE
    ABOVE_REFERENCE
    UNKNOWN
```

The following identities are fixed:

```text
regime_model_id=RCC002_TREND_CONTEXT_REGIME_V1
regime_model_version=1.0.0
regime_schema_id=rcc002.stage.s5-regimes
regime_schema_version=1.0.0
regime_schema_ref=rcc002.stage.s5-regimes/1.0.0
component_id=RCC002_S5_REGIME_CLASSIFIER
component_version=0.4.0
regime_reason_code_registry_version=1.0.0
```

No alias or diagnostic evidence field is added to the canonical `S5Row`.

---

## 6. Mathematical Binding

### 6.1 Slope

For the canonical `1m` baseline:

```text
reference_time = open_time_t - 86_400_000 milliseconds
ratio          = sma_close_200_t / sma_close_200_reference
offset         = ratio - 1.0
result         = 100.0 * offset
```

The operations occur in exactly that order.

The implementation must not algebraically rewrite the expression into a
different operation sequence.

The reference value must:

- be exactly 1,440 one-minute intervals earlier;
- be valid;
- be strictly positive;
- belong to the same `market_segment_id`;
- belong to the same `indicator_segment_id`;
- be reachable without crossing a gap.

### 6.2 Numerical profile

```text
regime_numeric_profile_id=RCC002_FLOAT64_REGIME_NUMERICS_V1
regime_numeric_profile_version=1.0.0
```

Implementation binding:

- Python `float` is the binary64 carrier;
- no decimal rounding is applied;
- no fused multiply-add is used;
- no parallel reduction is used;
- no unordered aggregation is used;
- the operation sequence in §6.1 is mandatory;
- `bool` is rejected as numeric input;
- NaN and positive/negative infinity are invalid;
- subnormal values are retained as finite binary64 values; the application
  performs no flush-to-zero;
- a runtime that flushes subnormals incompatibly is not conformant to this
  profile;
- no third-party numerical library participates in the S5 formula.

Independent comparison tolerances remain:

```text
absolute_tolerance=1e-12
relative_tolerance=1e-10
```

Threshold decisions use unrounded values and exact comparison operators.

---

## 7. State-Machine Binding

Initial state:

```text
regime_effective=UNKNOWN
regime_candidate=UNKNOWN
regime_candidate_count=0
```

For each valid `regime_raw`:

1. Same candidate: increment count, capped at `3`.
2. Different candidate: replace candidate and set count to `1`.
3. At count `3`, if candidate differs from effective, update effective.
4. Otherwise retain the previous effective regime.

For `regime_raw=UNKNOWN`:

- effective becomes `UNKNOWN`;
- candidate becomes `UNKNOWN`;
- count becomes `0`.

Transition semantics:

- the third confirming row owns the transition;
- a valid state to `UNKNOWN` is a transition;
- `UNKNOWN` to the first confirmed valid state is a transition;
- `UNKNOWN` to `UNKNOWN` at initial dataset start is not a transition;
- no earlier row is rewritten.

`REG_EFFECTIVE_UNCONFIRMED` applies only while no first valid effective
regime has yet been confirmed. It does not invalidate an already-established
effective regime while a different valid candidate has count `1` or `2`.

---

## 8. Context Binding

Trend strength is derived directly from valid `adx_wilder_14`:

```text
ADX <= 15           -> WEAK
15 < ADX <= 25      -> DEVELOPING
ADX > 25            -> STRONG
invalid ADX         -> UNKNOWN
```

Relative volatility is derived from valid `state_atr_relative_d`:

```text
-1 -> BELOW_REFERENCE
 0 -> AT_REFERENCE
+1 -> ABOVE_REFERENCE
invalid -> UNKNOWN
```

Neither context has directional meaning. Context validity remains independent
of `regime_valid`.

---

## 9. Reason-Code Binding

The S5 registry contains exactly the ten codes and priorities from §12.7.
Lists are tuples, non-null, deduplicated and sorted by ascending registered
priority.

All safely determinable applicable codes are retained.

Implementation-level boundary rules:

- the first row of the entire input is not a segment reset;
- the first row after an actual `market_segment_id` or
  `indicator_segment_id` change receives `REG_SEGMENT_RESET`;
- a slope dependency that would require data from the preceding indicator
  segment receives `REG_WINDOW_CROSSES_INDICATOR_SEGMENT`;
- incomplete local history receives `REG_WARMUP_INCOMPLETE`;
- these codes may coexist when all conditions apply;
- `REG_INPUT_QUALITY_GATE_FAILED` is added whenever
  `quality_gate_pass=false`;
- `REG_INPUT_INVALID` is added whenever a required current-row close or SMA
  input is invalid;
- `REG_SLOPE_DENOMINATOR_INVALID` applies to a valid but nonpositive
  reference SMA;
- `REG_NONFINITE_RESULT` applies only after valid finite inputs produce a
  nonfinite result;
- context reason codes never enter `regime_reason_codes`;
- regime reason codes never enter either context-reason list.

Unknown or unregistered codes are rejected.

---

## 10. S5 State-Snapshot Contract

### 10.1 Identity

```text
state_schema_id=rcc002.state.s5-regimes
state_schema_version=1.0.0
state_schema_ref=rcc002.state.s5-regimes/1.0.0
state_profile_id=RCC002_S5_SMA200_CONTEXT_V1
state_profile_version=1.0.0
state_hash_profile_id=RCC002_S5_STATE_HASH_V1
state_hash_profile_version=1.0.0
```

The additional profile identities are implementation metadata. They do not
change the certified state-schema ID.

### 10.2 `sma200_context_state`

`sma200_context_state` is an ordered immutable tuple containing between zero
and 1,440 valid binary64 `sma_close_200` values from the current indicator
segment, oldest first.

Rules:

- only values from the current `indicator_segment_id` are retained;
- invalid SMA values are not serialized;
- at most the latest 1,440 valid values are retained;
- tuple length is the context count;
- in the `1m` profile, timestamps are reconstructed from `last_open_time`,
  tuple position and the registered 60,000-millisecond interval;
- direct state continuation plus unchanged segment IDs proves that no gap is
  crossed;
- after a segment change the tuple is reset before the current row is
  processed.

### 10.3 Snapshot fields

The immutable snapshot contains:

- the three certified state-schema identity fields;
- nonempty `parent_build_id`;
- `market_type`;
- `symbol`;
- `interval`;
- `last_open_time`;
- `market_segment_id`;
- `indicator_segment_id`;
- `sma200_context_state`;
- `regime_effective`;
- `regime_candidate`;
- `regime_candidate_count`;
- `regime_model_id`;
- `regime_model_version`;
- `state_payload_sha256`.

The canonical consolidated baseline does not add `provider` to the state
key. A future non-consolidated multi-provider profile requires a separate
reviewed key variant.

### 10.4 State hash

`state_payload_sha256` is lowercase SHA-256 over UTF-8 canonical JSON of all
snapshot fields except `state_payload_sha256`.

The implementation-owned hash profile uses:

- lexicographically sorted object keys;
- compact separators;
- enum values serialized as their registered strings;
- tuples serialized as arrays in original order;
- `allow_nan=false`;
- no platform path, memory address or wall-clock value.

### 10.5 Continuation

A prior snapshot is usable only if:

- its hash is correct;
- all schema, state-profile and model identities are exact;
- `parent_build_id` matches;
- the next row belongs to the same series;
- the next `open_time` follows directly by 60,000 milliseconds;
- both segment IDs continue unchanged;
- candidate count lies in `0...3`;
- enum values are registered.

If any check fails, the prior state is discarded and S5 begins a complete
local warm-up from the first supplied row. No partially trusted state is
used.

---

## 11. Build Entry Point

The canonical implementation entry point is:

```python
compute_regimes(
    s4_rows: Sequence[S4Row],
    *,
    parent_build_id: str,
    prior_state: RegimeStateSnapshot | None = None,
) -> S5Result
```

`parent_build_id` must be a nonempty string.

`S5Result` contains:

- immutable `rows: tuple[S5Row, ...]`;
- `final_state: RegimeStateSnapshot | None`;
- a flag stating whether a supplied prior state was accepted.

Empty input returns:

- an empty row tuple;
- the unchanged valid prior state if one was supplied and no next-row
  continuation decision was required;
- otherwise `final_state=None`.

One invocation processes exactly one canonical series. Dataset orchestration
may call the entry point separately for each series.

---

## 12. Reconciliation

The implementation must verify:

```text
S5_rows = S4_rows
```

For every output row:

- the canonical key is unchanged;
- row order is unchanged;
- `market_segment_id` is unchanged;
- `indicator_segment_id` is unchanged;
- every inherited S4 dataclass field is semantically equal;
- no S6 or S7 field exists;
- the S5 extension contains exactly the registered fields in exact order.

Reconciliation failure aborts the stage. It is not serialized as a valid S5
row.

---

## 13. Schema Compatibility

V1 accepts exactly:

```text
rcc002.stage.s4-signals/1.0.0
```

No S4 minor-version compatibility rule is registered in this baseline.
Unknown schema IDs or versions are rejected fail-closed.

S5 emits exactly:

```text
rcc002.stage.s5-regimes/1.0.0
```

No alias migration occurs inside S5.

---

## 14. Environment and Dependency Binding

S5 mathematical and state logic uses:

- Python `3.12.x`;
- Python standard library only;
- no NumPy, pandas, BLAS or platform-dependent parallel reduction.

The exact Python patch version, operating system, implementation commit,
source-tree hash and test command must be recorded in the later build
manifest. Any external serialization layer is outside the pure S5 compute
module and may not change logical values.

---

## 15. Required Implementation Files

Production:

```text
rcc002/s5/__init__.py
rcc002/s5/constants.py
rcc002/s5/formulas.py
rcc002/s5/reason_codes.py
rcc002/s5/schema.py
rcc002/s5/state.py
rcc002/s5/compute.py
```

Tests:

```text
tests/rcc002/s5/__init__.py
tests/rcc002/s5/test_formulas.py
tests/rcc002/s5/test_schema.py
tests/rcc002/s5/test_state.py
tests/rcc002/s5/test_compute.py
tests/rcc002/s5/test_golden_fixtures.py
```

Responsibilities:

- `constants.py`: identities, enums, field order, profiles and registries;
- `formulas.py`: pure slope, raw-regime and context formulas;
- `reason_codes.py`: normalization and priority ordering;
- `schema.py`: immutable S5 row and domain validation;
- `state.py`: state snapshot, hash and continuation validation;
- `compute.py`: input checks, causal orchestration, state machine,
  row-preservation reconciliation;
- tests: independent truth tables, edge cases, state and integration
  evidence.

---

## 16. Required Tests

The S5 implementation must include at least:

### 16.1 Formula and truth-table tests

- positive, negative and zero slope;
- Bull, Bear and all Side combinations;
- exact price equality;
- invalid current SMA;
- invalid reference SMA;
- zero/negative denominator;
- nonfinite rejection;
- ADX at `15`, immediately above `15`, `25`, immediately above `25`;
- ATR-relative values `-1`, `0`, `+1`;
- invalid context inputs.

### 16.2 Warm-up and segmentation

- first possible slope at local one-minute index `1639`;
- first possible effective regime at index `1641`;
- exact 1,440-minute reference;
- insufficient history;
- market-segment reset;
- indicator-segment reset;
- no state transfer across a gap;
- no false segment-reset code on the dataset’s first row.

### 16.3 State machine

- initial three-row confirmation;
- stable candidate-count saturation at `3`;
- candidate change at count `1` and `2`;
- confirmed Bull→Side, Side→Bear and Bear→Bull transitions;
- valid state→Unknown;
- Unknown reset;
- Unknown→first confirmed valid state;
- no retroactive rewriting.

### 16.4 State snapshot and partition parity

- snapshot domain validation;
- deterministic checksum;
- checksum tampering;
- parent-build mismatch;
- nonadjacent next key;
- model/schema/profile mismatch;
- segment mismatch;
- partition split during candidate count `1`;
- partition split during candidate count `2`;
- serial/partitioned exact enum equality;
- serial/partitioned slope equality within the certified tolerance.

### 16.5 Schema, validity and ownership

- exact S4 input acceptance;
- incompatible schema/profile rejection;
- exact S5 field inventory and order;
- enum domains;
- nullability;
- `regime_valid` truth;
- context validity independent of regime validity;
- reason-code order and deduplication;
- row, key and segment preservation;
- no S6/S7 fields.

### 16.6 Scientific properties

- future-row changes do not alter prior S5 output;
- repeated identical input is deterministic;
- every valid raw regime is exactly one of Bull/Side/Bear;
- candidate count always lies in `0...3`;
- Unknown always resets candidate state;
- valid slopes are finite;
- transition fields are null exactly when transition flag is false.

### 16.7 Independent golden fixtures

Golden fixtures must derive expectations independently of production
orchestration:

- slope fixture with exact rational values;
- complete 1,642-row first-regime fixture;
- multi-transition state-machine fixture;
- segment-reset fixture;
- partition-continuation fixture.

---

## 17. Acceptance Sequence

After implementation:

1. `python3 -m compileall rcc002/s5 tests/rcc002/s5`
2. S5 import test
3. S5-specific tests
4. complete RCC-002 suite
5. regression suite
6. `git diff --check`
7. staging inventory review
8. independent Claude review
9. independent Gemini review
10. findings consolidation
11. final tests
12. separate commit
13. push
14. verify `HEAD`, `origin/main` and working tree

The untracked file `scripts/build_rcc002_spec_bundle.py` must remain outside
the S5 commit unless separately reviewed and explicitly authorized.

---

## 18. Findings

### Critical

None.

### Major

None.

### Minor

None blocking implementation.

### Accepted implementation limitations

- S6 remains unimplemented and requires a separate readiness review.
- Dataset-level reports and publication execution remain separate roadmap
  work; S5 must nevertheless expose all state and reconciliation evidence
  required for their later construction.
- Legacy and GS reconstruction profiles are not part of the canonical S5
  implementation tranche.
- The repository-level deferred blockers concerning automatic
  `source_snapshot_id` derivation remain assigned to Roadmap Step 13 and do
  not affect S5.

---

## 19. Final Authorization

```text
S5_REGIMES:
IMPLEMENTATION READY

S6_GATES:
NOT REVIEWED IN THIS DECISION

Specification modification:
NOT REQUIRED

Silent fallback or invented regime semantics:
NOT PERMITTED
```

Implementation may begin with `rcc002/s5/constants.py` and its registry
tests, then proceed file by file in the order listed in Section 15.

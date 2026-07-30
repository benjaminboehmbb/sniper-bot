# RCC-002 S6 Implementation Readiness Review

## Document metadata

| Field | Value |
|---|---|
| Document ID | `RCC-002-S6-IRR-001` |
| Date | 2026-07-30 |
| Scope | `S6_GATES` only |
| Target component | `RCC002_S6_GATE_EVALUATOR/0.4.0` |
| Input schema | `rcc002.stage.s5-regimes/1.0.0` |
| Output schema | `rcc002.stage.s6-gates/1.0.0` |
| Normative bundle | `docs/review/RCC_002_DVSEV001_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md` |
| Normative bundle SHA-256 | `8a6ab7d732e02727199e704313c38959161c3929441fddce34b4ee4f2586d9ee` |
| Normative manifest | `docs/review/RCC_002_DVSEV001_CORRECTED_BUNDLE_MANIFEST_2026-07-27.md` |
| Normative manifest SHA-256 | `176d99582ebff741d5d45b7fccc76a49b5b1d267ce350d867d4f64c17c6a8297` |
| Governing certification | `docs/certification/RCC_002_DVSEV001_CERTIFICATION_DECISION_2026-07-27.md` |
| Upstream implementation certification | `docs/certification/RCC_002_S5_IMPLEMENTATION_CERTIFICATION_DECISION_2026-07-28.md` |
| Repository baseline | `e0eecfd` |
| Readiness decision | `APPROVED FOR IMPLEMENTATION` |

## 1. Scope decision

S6 is a stateless, row-preserving gate-evaluation stage. It consumes only
canonical `S5Row` inputs and adds exactly the 13 non-duplicated S6 fields
registered in Regime and Gate Specification section 18.2.

S6 does not:

- generate entries or exits;
- combine timing signals;
- apply MFI, cooldown, loss-cluster, TP, SL, or position sizing;
- calculate forward returns, barriers, labels, or S7 fields;
- alter S0-S5 values, ordering, segment identities, or row count;
- carry recursive state across partitions.

## 2. Bound profile contract

Exactly one profile is selected for each call:

1. `GATE_RESEARCH_OPEN_V1/1.0.0`;
2. `GATE_TREND_ALIGNED_V1/1.0.0`;
3. `GATE_TREND_STRENGTH_ALIGNED_V1/1.0.0`.

`GATE_RESEARCH_OPEN_V1` is the default profile because the certified
specification defines it as the canonical general-research export. Profile
selection is explicit in every emitted row through `gate_profile_id` and
`gate_profile_version`.

One API invocation processes one provider/market/symbol/interval series.
This is a physical execution constraint only; it does not modify row
semantics. Multiple series are processed through independent calls and may be
concatenated in canonical key order.

## 3. Stage-wide validation

Before any output row is created, S6 validates:

- exact Python input row type `S5Row`;
- exact S5 schema ID and version;
- exact S5 regime model ID and version;
- registered gate profile ID and exact profile version;
- non-empty provider, market, symbol, and segment identities;
- supported interval `1m`;
- one-series execution contract;
- strict timestamp ordering;
- gap-to-indicator-segment consistency;
- the full inherited S5 row contract through `S5Row.__post_init__`.

Structural failure raises an exception and produces no canonical S6 result.
It is never converted into row-level `INVALID`.

## 4. Data-gate binding

The implementation binds:

```text
data_gate_pass = quality_gate_pass
```

If `data_gate_pass=false`, evaluation ends immediately with:

```text
allow_long=false
allow_short=false
gate_valid=true
gate_state=BLOCK_BOTH
gate_reason_codes_long=(GATE_DATA_QUALITY_FAILED)
gate_reason_codes_short=(GATE_DATA_QUALITY_FAILED)
```

Regime and trend-strength validity are deliberately not inspected in that
branch.

## 5. Profile truth tables

### 5.1 Research Open

For `data_gate_pass=true`:

- both directions are allowed;
- `gate_valid=true`;
- `gate_state=ALLOW_BOTH`;
- each direction receives its registered research-open allow code.

S5 regime and trend-strength validity are not profile inputs.

### 5.2 Trend Aligned

For valid required S5 inputs:

| Effective regime | Long | Short | Gate state |
|---|:---:|:---:|---|
| `BULL` | true | false | `ALLOW_LONG_ONLY` |
| `SIDE` | false | false | `BLOCK_BOTH` |
| `BEAR` | false | true | `ALLOW_SHORT_ONLY` |

ADX and `trend_strength` are not consumed.

### 5.3 Trend Strength Aligned

For `DEVELOPING` or `STRONG`, BULL permits only Long, BEAR permits
only Short, and SIDE blocks both. `WEAK` validly blocks both directions.
All applicable direction-local regime and weak-trend block codes are retained.

Unknown or invalid required regime or trend-strength inputs produce:

```text
allow_long=false
allow_short=false
gate_valid=false
gate_state=INVALID
```

## 6. Invalid-state reason mapping

For trend-directed profiles:

- `REG_WARMUP_INCOMPLETE` or `REG_EFFECTIVE_UNCONFIRMED` maps to
  `GATE_WARMUP_INCOMPLETE`;
- `REG_SEGMENT_RESET` or
  `REG_WINDOW_CROSSES_INDICATOR_SEGMENT` maps to
  `GATE_SEGMENT_RESET`;
- invalid or unknown required regime always adds
  `GATE_REGIME_UNKNOWN`;
- invalid or unknown required strength additionally adds
  `GATE_TREND_STRENGTH_UNKNOWN`.

No downstream policy predicate is evaluated after a required profile input is
found invalid.

`GATE_INPUT_INVALID` and `GATE_STATE_INVALID` remain registered for compatible
future typed inputs and defensive classification. Canonical `S5Row/1.0.0`
validation prevents their otherwise ambiguous use for the baseline truth
tables.

## 7. Output schema and invariants

S6 adds, in exact order:

1. `allow_long`;
2. `allow_short`;
3. `data_gate_pass`;
4. `gate_state`;
5. `gate_reason_codes_long`;
6. `gate_reason_codes_short`;
7. `gate_profile_id`;
8. `gate_profile_version`;
9. `gate_schema_id`;
10. `gate_schema_version`;
11. `gate_schema_ref`;
12. `gate_valid`;
13. `gate_evaluated_at`.

The already inherited `regime_model_id` and `regime_model_version` are not
duplicated.

`S6Row` enforces:

- exact Boolean types;
- the five-value `GateState` enum;
- `gate_state` consistency with both directional Booleans and `gate_valid`;
- `INVALID` if and only if the gate is invalid;
- `BLOCK_BOTH` as a valid state;
- exact data-gate equality;
- exact metadata;
- `gate_evaluated_at=close_time`;
- canonical, deduplicated, priority-sorted reason lists;
- absence of cross-direction reason codes;
- exactly one allow code for each allowed direction;
- no allow code for a blocked direction.

The mutable `indicators` and `signals` containers are copied so S6 output
mutation cannot modify the upstream in-memory S5 row.

## 8. Determinism, causality, and partitioning

S6 reads only fields from the current S5 row and has no recursive state.
Consequently:

- future rows cannot alter an earlier result;
- identical rows and profile identity produce identical outputs;
- arbitrary row-boundary partitioning produces the same concatenated output;
- `gate_evaluated_at` is the row's `close_time`, never build wall-clock time.

## 9. Mandatory test binding

The implementation test suite must cover:

- the complete `GateState` truth rule;
- all three profile truth tables;
- quality failure before profile-input evaluation;
- SIDE versus UNKNOWN;
- WEAK versus invalid trend strength;
- all registered reason priorities;
- reason deduplication and directional separation;
- exact 13-field extension order;
- row count and inherited-value preservation;
- independent mutable containers;
- profile and schema rejection;
- canonical order and series rejection;
- point-in-time equality;
- no-lookahead prefix invariance;
- stateless partition parity;
- absence of forbidden alias, strategy, and S7 fields.

## 10. Readiness decision

No unresolved semantic decision changes S6 values, validity, reason codes,
schema, profile identity, or point-in-time behavior.

**Decision: `APPROVED FOR IMPLEMENTATION`.**


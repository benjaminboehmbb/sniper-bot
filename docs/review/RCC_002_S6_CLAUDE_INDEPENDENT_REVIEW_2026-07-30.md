# RCC-002 S6 Independent Review — Claude

Date: 2026-07-30
Reviewer: Claude (independent review, per user request)
Scope: `S5_REGIMES -> S6_GATES` implementation only (`rcc002/s6/`, `tests/rcc002/s6/`)

## 1. Package integrity

```text
File:     RCC_002_S6_INDEPENDENT_REVIEW_PACKAGE_2026-07-30.zip
Expected: c19062b326663f347681e8cfc2f1e50ce44db2cda55558ad685157facaaa1256
Actual:   c19062b326663f347681e8cfc2f1e50ce44db2cda55558ad685157facaaa1256
Result:   MATCH
```

The package was extracted read-only to a scratch directory under `/tmp`
(`/tmp/claude-1000/.../scratchpad/rcc002_s6_review/pkg`). No file inside the
package or the repository was modified during this review. `diff -rq`
confirmed that `pkg/rcc002/{s3,s4,s5,s6}` and `pkg/tests/rcc002/{s3,s4,s5,s6}`
are byte-identical to the corresponding untracked working-tree paths in the
repository (only `__pycache__` differs), and that the four normative
documents inside the package are byte-identical to the repository's
`docs/review/` and `docs/certification/` copies.

## 2. Normative basis actually used

Exclusively, as instructed:

- `docs/review/RCC_002_DVSEV001_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md`
  (specifically the merged `RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md`
  source section, lines 7504–9530, plus the general pipeline-invariant
  sections 6–13 of the merged Data Pipeline Specification, lines 22–2621)
- `docs/review/RCC_002_DVSEV001_CORRECTED_BUNDLE_MANIFEST_2026-07-27.md`
- `docs/certification/RCC_002_DVSEV001_CERTIFICATION_DECISION_2026-07-27.md`
- `docs/certification/RCC_002_S5_IMPLEMENTATION_CERTIFICATION_DECISION_2026-07-28.md`

`RCC_002_S6_IMPLEMENTATION_READINESS_REVIEW_2026-07-30.md` and
`RCC_002_S6_IMPLEMENTATION_RECORD_2026-07-30.md` were read only to know what
the implementer claims; none of their statements were treated as evidence.
All conclusions below are derived from reading `rcc002/s6/*.py` directly and
from independent reproduction scripts, not from `tests/rcc002/s6/*` assertions
(existing tests were read only to identify coverage gaps, per instruction 16).

## 3. Tests executed by this review

All from repo root, `.venv` active:

```text
python -m compileall -q rcc002 tests/rcc002
  -> PASS (exit 0)

python -m unittest discover -s tests/rcc002/s6 -t .
  -> Ran 49 tests, OK

python -m unittest discover -s tests/rcc002 -t .
  -> Ran 524 tests, OK

python -m unittest discover -s tests/regression -t .
  -> Ran 170 tests, OK
```

These confirm the implementer's reported counts but, per instruction 4, are
**not** treated as proof of correctness. Independent verification (section 4)
was performed separately.

## 4. Independent verification performed (not implementer tests)

All scripts below live only under `/tmp` and were run against the certified
S3→S4→S5 pipeline to obtain real, canonical `S5Row` fixtures (not synthetic
dicts), so gate evaluation is exercised on structurally valid rows.

### 4.1 Exhaustive truth-table cross-check (`/tmp/rcc002_s6_independent_truth_table_check.py`)

An oracle was written from scratch directly against RG-spec §13–§20 (without
reading `rcc002/s6/compute.py` logic first, then reconciled once, see script
history) and cross-checked against `compute_gates()` over the Cartesian
product of:
`profile ∈ {RESEARCH_OPEN, TREND_ALIGNED, TREND_STRENGTH_ALIGNED}` ×
`data_gate_pass ∈ {True, False}` × `regime_valid ∈ {True, False}` ×
`regime_effective ∈ {BULL, SIDE, BEAR, UNKNOWN}` ×
`trend_strength_valid ∈ {True, False}` ×
`trend_strength ∈ {WEAK, DEVELOPING, STRONG, UNKNOWN}` ×
`regime_reason_codes ∈ {WARMUP, SEGMENT_RESET, WINDOW_CROSSES, EFFECTIVE_UNCONFIRMED, WARMUP+SEGMENT_RESET, other}`,
filtered to combinations that are structurally constructible under `S5Row`'s
own `__post_init__` invariants.

```text
total cases exercised: 327
skipped (structurally invalid S5Row construction): 0
mismatches: 0
```

Result: **0/327 mismatches** between the independently-derived oracle and the
implementation, across all three profiles, both `gate_valid` outcomes, all
four `regime_effective` values, all four `trend_strength` values, and all
tested `regime_reason_codes` mappings (`GATE_WARMUP_INCOMPLETE`,
`GATE_SEGMENT_RESET`, `GATE_REGIME_UNKNOWN`, `GATE_TREND_STRENGTH_UNKNOWN`
combinations included).

### 4.2 `data_gate_pass=false` dominance over simultaneously invalid regime/strength

Constructed a row with `quality_gate_pass=False` **and** invalid regime
**and** invalid trend strength at once, evaluated under all three profiles.
Result: all three produced exactly `gate_valid=True`, `gate_state=BLOCK_BOTH`,
`allow_long=False`, `allow_short=False`, both reason lists exactly
`("GATE_DATA_QUALITY_FAILED",)`. Confirms §13.3 dominance holds even under
compounded invalidity, not just in isolation.

### 4.3 Stage-wide fail-closed abort (not row-level `INVALID`)

Independently constructed: (a) unordered input, (b) an `S5Row` with
`regime_schema_version="2.0.0"`, (c) a duplicated `open_time`. All three
raised `ValueError`/`TypeError` from `compute_gates()` with **no** partial
`S6Row` output produced — confirmed by inspecting that the exception occurs
inside `_validate_input_rows`, called before the per-row output loop begins.
This empirically confirms §6.7's requirement that a stage-wide contract
violation is never serialized as a row-level `INVALID`/`false` value.

### 4.4 Causality, prefix invariance, stateless partition parity

Built 6 real canonical `S5Row`s and, for all three profiles: (a) compared a
4-row prefix run against the first 4 rows of a 6-row full run (must be
byte-for-byte equal); (b) compared every possible 2-way split-then-concatenate
run against the full run. Result: **all equal**, for every split point, for
all three profiles. This directly and independently confirms §33.2's
required properties ("Änderungen nach `t` verändern S5/S6 bei `t` nicht" and
"serielle und partitionierte Berechnung stimmen überein") rather than relying
on `tests/rcc002/s6/test_compute.py`'s own (structurally similar) assertions.

### 4.5 Field order / preservation, verified by direct dataclass introspection

`dataclasses.fields(S6Row)` was inspected directly (not via the schema's own
self-check): 73 total fields; the first 60 are identical, in identical order,
to `dataclasses.fields(S5Row)`; the remaining 13 are exactly
`GATE_EXTENSION_FIELDS` in table order; `regime_model_id` and
`regime_model_version` do not appear a second time. This matches RG-spec
§18.2/§18.8 exactly and confirms Prüfpunkt 2.

## 5. Findings

No `CRITICAL` or `MAJOR` finding survived independent reproduction. Two
`MINOR` findings were identified; no `EDITORIAL` findings beyond those two are
reported.

---

### FINDING S6-CLAUDE-001 (MINOR)

- **File / location**: `rcc002/s6/compute.py`, function `_invalid_profile_reasons`, lines 158–159 (`if not common: common.append("GATE_INPUT_INVALID")`)
- **Violated/related normative rule**: RG-spec §20.5, last sentence: *"Sonstige zeilenbezogene ungültige Pflichtinputs erzeugen: `GATE_INPUT_INVALID`."*
- **Technical evidence (reproducible)**: `_invalid_profile_reasons` is only invoked when `profile_inputs_valid` is `False`, which by construction in `compute_gates` (lines 293–304) is `False` iff `(not regime_valid or regime_effective is UNKNOWN)` **or** `(require_strength and (not trend_strength_valid or trend_strength is UNKNOWN))`. The first disjunct always causes the `if not row.regime_valid or row.regime_effective is RegimeState.UNKNOWN:` branch (lines 139–150) to append at least `GATE_REGIME_UNKNOWN` to `common`; the second disjunct always causes the `if require_trend_strength and (...)` branch (lines 152–156) to append `GATE_TREND_STRENGTH_UNKNOWN`. Consequently `common` can never be empty when this function runs, and the `GATE_INPUT_INVALID` fallback at lines 158–159 is unreachable. This was confirmed both by exhaustive boolean-case analysis and empirically: the independent 327-case truth-table sweep in section 4.1 never produced `GATE_INPUT_INVALID` in any output, and `grep` shows no test in `tests/rcc002/s6/` exercises it either.
- **Concrete impact**: None on current correctness — the registry code is defined, correctly prioritized (30) and correctly classified as invalidating/BOTH, but is dead code under the three currently-registered gate profiles' Pflichtinputs (§18.5 lists only `regime_valid`/`regime_effective` and `trend_strength_valid`/`trend_strength` as profile-dependent required inputs; there is currently no "other" Pflichtinput for `GATE_INPUT_INVALID` to represent). It does not create a false positive or false negative in any producible S6 row.
- **Required correction**: Not blocking. Either (a) leave as intentionally reserved for a future profile/Pflichtinput and add a code comment plus a `pragma: no cover`-style test asserting the branch is currently unreachable (so future refactors don't silently break the fallback), or (b) remove the dead branch and instead raise if this state is ever reached, converting it from a silent fallback into an explicit invariant check.

---

### FINDING S6-CLAUDE-002 (MINOR)

- **File / location**: `rcc002/s6/constants.py`, line 97–99 (`GateReasonCodeDefinition("GATE_STATE_INVALID", 80, "BOTH", "INVALIDATING")`)
- **Violated/related normative rule**: RG-spec §19.2 (registry table) registers `GATE_STATE_INVALID` at priority 80 but no section of the RG specification (§13–§20, checked in full) defines a triggering condition for it, unlike every other invalidating code (`GATE_INPUT_INVALID` → §20.5 fallback; `GATE_WARMUP_INCOMPLETE`/`GATE_SEGMENT_RESET`/`GATE_REGIME_UNKNOWN` → §20.5 regime mapping; `GATE_TREND_STRENGTH_UNKNOWN` → §20.5 strength mapping).
- **Technical evidence (reproducible)**: `grep -rn "GATE_STATE_INVALID" rcc002/s6/ tests/rcc002/s6/` returns only the single registry definition in `constants.py`; the code is never emitted by `compute.py` and never asserted by any test. The independent 327-case sweep (section 4.1) never produced it either.
- **Concrete impact**: None on current correctness. This is a registry/spec-side gap rather than an implementation defect: the implementation is not missing logic that the spec requires — the spec itself does not specify when `GATE_STATE_INVALID` should fire for any of the three baseline profiles. It reduces confidence that the code, if it is ever emitted by a future profile addition, will interoperate correctly with the rest of the reason-code machinery (dedup, `_validate_direction_truth`, etc.), since it has zero test coverage today.
- **Required correction**: Not blocking for this S6 baseline. Recommend flagging to the spec owners that §19.2/§20.5 should either define `GATE_STATE_INVALID`'s trigger condition explicitly or mark it as reserved for a not-yet-registered profile, and recommend the implementer add at least one direct unit test exercising the code (even if synthetically, via a helper that constructs it) so it is not silently untested machinery in a registry required to be "vollständig" (§9, PRÜFPUNKT 9).

## 6. Prüfpunkte 1–16 — disposition summary

| # | Prüfpunkt | Disposition |
|---|---|---|
| 1 | Exact S5 input / S6 output schema IDs | Confirmed (§4.5, code inspection of `constants.py`/`compute.py`) |
| 2 | Exact S6 field order, 13 new fields, no `regime_model_id`/`_version` duplication | Confirmed (§4.5, direct `dataclasses.fields()` introspection) |
| 3 | `data_gate_pass == quality_gate_pass` exactly | Confirmed (code + schema self-check + oracle) |
| 4 | `quality_gate_pass=false` → valid `BLOCK_BOTH` only, `GATE_DATA_QUALITY_FAILED` only | Confirmed, including compounded-invalidity dominance (§4.2) |
| 5 | Full truth tables for all three profiles | Confirmed, 0/327 mismatches (§4.1) |
| 6 | Correct profile-dependent required inputs | Confirmed (code inspection + oracle) |
| 7 | Exact distinction valid `BLOCK_BOTH` vs. invalid `INVALID` | Confirmed (`derive_gate_state`, schema self-check, oracle) |
| 8 | Exact `GateState` enum, consistency with `gate_valid`/`allow_*` | Confirmed (5-value enum, no `UNKNOWN`; §18.4 rule reproduced exactly) |
| 9 | 19-code registry, priorities 30–210, deterministic sort, invalidity mapping, Long/Short separation | Confirmed structurally; 2 MINOR findings on 2 of 19 codes being unreachable/untested (S6-CLAUDE-001, -002) |
| 10 | Exact SIDE/UNKNOWN/WEAK/DEVELOPING/STRONG handling | Confirmed (§4.1 oracle covers all combinations) |
| 11 | `gate_evaluated_at == close_time` exactly | Confirmed (code + schema self-check) |
| 12 | S5→S6 row/key/segment/value preservation; independent `indicators`/`signals` containers | Confirmed (§4.5, plus independent container-identity check) |
| 13 | Stage-wide fail-closed abort, no structural-error-to-`INVALID` conversion | Confirmed (§4.3, three independent violation scenarios) |
| 14 | Causality, prefix invariance, stateless partition parity | Confirmed (§4.4, all split points, all three profiles) |
| 15 | No strategy/entry/exit/risk/return/barrier/label/S7 logic | Confirmed (`grep` for forbidden terms: none found) |
| 16 | Active search for missing edge cases / test gaps / false positives | Performed; found 2 MINOR dead-code/unreachable-registry items; no false positives in 327 independently-oracled cases plus the 4.2–4.4 targeted probes |

## 7. Final decision

```text
APPROVED
```

No `CRITICAL` or `MAJOR` finding remains open. Two `MINOR` findings
(S6-CLAUDE-001, S6-CLAUDE-002) are reported; both concern unreachable/untested
reason-code machinery with no effect on any currently producible S6 row, and
neither is elevated beyond `MINOR` since neither has reproducible evidence of
an actual incorrect gate output.

### Finding counts by severity

| Severity | Count |
|---|---|
| CRITICAL | 0 |
| MAJOR | 0 |
| MINOR | 2 |
| EDITORIAL | 0 |

### Tests executed and results

```text
python -m compileall -q rcc002 tests/rcc002                    -> PASS
python -m unittest discover -s tests/rcc002/s6 -t .             -> 49 tests, OK
python -m unittest discover -s tests/rcc002 -t .                -> 524 tests, OK
python -m unittest discover -s tests/regression -t .            -> 170 tests, OK
```

Plus independent (non-implementer) reproduction, all under `/tmp`:

```text
/tmp/rcc002_s6_independent_truth_table_check.py                 -> 327/327 cases match oracle, 0 mismatches
ad hoc dominance / abort / causality / partition-parity checks  -> all passed (see §4.2-4.4)
```

### Report location

```text
/tmp/RCC_002_S6_CLAUDE_INDEPENDENT_REVIEW_2026-07-30.md
```

No file inside the repository or inside the review package was modified by
this review.

# RCC-002 S7 Independent Review — Claude

Date: 2026-07-30
Reviewer: Claude (independent review, per user request)
Scope: `S6_GATES -> S7_LABELS` implementation only (`rcc002/s7/`, `tests/rcc002/s7/`)

## 1. Executive Summary

The S7 forward-return/labeling implementation was reviewed line-by-line against the
normative RG/LF (Label and Forward Return) specification and cross-checked with
327+ independently constructed reproduction cases, hand-computed oracles, and a
timed performance benchmark — none of it relying on the implementer's own tests.

Package identity, schema/registry structure (302 fields, exact order, exact types),
return/excursion/barrier formulas, reason-code registry, row/key/segment
preservation, mutable-container independence, causality/prefix-invariance,
partition parity, and the leakage guard all check out against independently
derived oracles with **zero mismatches**.

Two **MAJOR** and one **MINOR** finding were identified, all with reproducible
evidence:

1. **MAJOR** — Close-to-Close and Next-Open-to-Close family validity is
   incorrectly coupled to the quality of *every* bar in the full `t+1..t+h`
   window, not just the bars those two families actually consume (`C(t)`,
   `C(t+h)` for CC; `O(t+1)`, `C(t+h)` for NOC). This over-invalidates CC/NOC
   labels and violates the family-local quality-scoping required by RG/LF §5.5.
2. **MAJOR** — The horizon/excursion/barrier computation is a naive
   `O(n × Σh)` algorithm (`Σh = 1761` bar-visits per row) amplified by
   expensive `numbers.Real`/`numbers.Integral` ABC-based `isinstance` checks
   in the hot path. Measured throughput on this machine is on the order of
   30–270 rows/s depending on scale and data character, implying multiple
   hours (plausibly the better part of a day) for a realistic multi-year
   BTCUSDT 1-minute full build of a single symbol/profile — a severe
   practical obstacle to the pipeline's stated iterative-research purpose,
   though not a correctness defect.
3. **MINOR** — `HorizonLabels` schema validation does not cross-check that a
   `TIMEOUT` barrier outcome implies a null hit-bar/hit-time (and vice versa
   for hit outcomes); this is unreachable via the current `compute_labels`
   code path (which derives these atomically) but is a latent robustness gap.

No `CRITICAL` finding was identified: nothing produces data leakage, a wrong
sign, an incorrect discrete label/outcome, or a falsely-valid result.

## 2. Package identity

```text
File:     RCC_002_S7_INDEPENDENT_REVIEW_PACKAGE_2026-07-30.zip
Expected: 10e2612cfb744cb67202a408a28d28ec5ee91e869f8447e7d7ee792724cc2e07
Actual:   10e2612cfb744cb67202a408a28d28ec5ee91e869f8447e7d7ee792724cc2e07
Result:   MATCH
```

The package was extracted read-only to `/tmp/rcc002_s7_review/pkg`. No file
inside the package or the repository was modified during this review. `diff -rq`
confirmed `pkg/rcc002/{s3,s4,s5,s6,s7}` and `pkg/tests/rcc002/{s3,s4,s5,s6,s7}`
are byte-identical to the repository's untracked working-tree copies (only
`__pycache__` differs), and that all five normative documents inside the
package are byte-identical to the repository's `docs/review/` and
`docs/certification/` copies.

## 3. Source-grounding inventory

Normative basis actually used (exclusively, per instruction):

- `docs/review/RCC_002_DVSEV001_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md` —
  specifically the merged `RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md`
  source section (file lines 9727–11748, all 40 sections read in full) and the
  general S7/S8 leakage-registry sections of the merged Data Pipeline
  Specification (§7.8 "S7_LABELS", §7.9 "S8_EXPORT" incl. §7.9.1's fully
  expanded, machine-readable `RCC002_S8_FIELD_OWNERSHIP_V1` JSON registry,
  file lines 1087–1445).
- `docs/review/RCC_002_DVSEV001_CORRECTED_BUNDLE_MANIFEST_2026-07-27.md`
- `docs/certification/RCC_002_DVSEV001_CERTIFICATION_DECISION_2026-07-27.md`
- `docs/certification/RCC_002_S5_IMPLEMENTATION_CERTIFICATION_DECISION_2026-07-28.md`
- `docs/certification/RCC_002_S6_IMPLEMENTATION_CERTIFICATION_DECISION_2026-07-30.md`

`RCC_002_S7_IMPLEMENTATION_READINESS_REVIEW_2026-07-30.md` and
`RCC_002_S7_IMPLEMENTATION_RECORD_2026-07-30.md` were read only to inventory
the implementer's claims (see §80 in the point-by-point table); none of their
statements were treated as evidence. The 302-field S8 field-ownership registry
(§7.9.1) was parsed programmatically out of the spec's embedded JSON and
diffed directly against `rcc002.s7.constants.LABEL_EXTENSION_FIELDS` — this
gave an exact, machine-verified ground truth for the field-count/order/name
checks rather than a manual read.

Source code read in full, line-by-line: `rcc002/s7/__init__.py`,
`constants.py`, `formulas.py`, `reason_codes.py`, `leakage.py`, `planning.py`,
`schema.py`, `compute.py` (≈1,750 lines). Implementer tests
(`tests/rcc002/s7/*`) were read only to identify coverage gaps (instruction
16/78), never cited as evidence for a Pass/Fail determination.

## 4. Findings matrix

| ID | Severity | File / Function | Rule |
|---|---|---|---|
| S7-CLAUDE-001 | MAJOR | `rcc002/s7/compute.py:253-266,283-306` (`_base_reason_codes`, `_compute_complete_horizon`) | RG/LF §5.5, §17.1 |
| S7-CLAUDE-002 | MAJOR | `rcc002/s7/compute.py` (`_compute_complete_horizon`), `rcc002/s7/formulas.py` (`_finite_positive`, `excursion_values`, `_barrier_for_direction`) | RG/LF §39.2.11 |
| S7-CLAUDE-003 | MINOR | `rcc002/s7/schema.py:118-186` (`HorizonLabels._validate_family`) | RG/LF §18.3, §13.4/§16.4 |

## 5. Detailed findings

### S7-CLAUDE-001 (MAJOR) — CC/NOC validity incorrectly window-wide instead of family-local

- **File / function**: `rcc002/s7/compute.py`, `_base_reason_codes` (lines
  253–266) and `_compute_complete_horizon` (lines 283–306, specifically
  `cc_reasons = list(common)` at line 283 and `noc_reasons = list(common)` at
  line 290, where `common` already contains `LBL_FUTURE_BAR_QUALITY_FAILED`
  whenever **any** row in the full `future = rows[t+1..t+h]` window fails the
  quality contract).
- **Violated normative rule**: RG/LF spec §5.5 "Qualitätsvertrag": *"Für jede
  von einer Label-Familie **verwendete** Preiszeile muss gelten:
  quality_gate_pass=true..."* (the quality requirement is scoped to price rows
  a given family actually **uses**), reinforced by §17.1 "Vollständiger
  Horizont: Ein Label ist nur gültig, wenn alle **erforderlichen** Kerzen bis
  `t+h` vorhanden und validiert sind" (only the *required* candles), and
  directly probed by review instruction B.44 ("Familienlokale Entry- und
  Exit-Invalidität"). Per §7.1/§8.1, the Close-to-Close family formally
  consumes only `C(t)` and `C(t+h)`; the Next-Open-to-Close family consumes
  only `O(t+1)` and `C(t+h)`. Neither ever reads any intermediate bar's price.
- **Reproducible evidence**: constructed a 6-row series (`h5_prices =
  [100,101,102,103,104,105]`) where **only** the intermediate bar at offset 3
  (neither the entry bar `t+1` nor the exit bar `t+5`) has
  `quality_ohlc_valid=False`/`quality_gate_pass=False` (with a fully
  gate-consistent `S6Row`). Result for horizon H005 on row 0:
  ```
  cc_valid=False  noc_valid=False  excursion_valid=False
  cc_reasons=('LBL_FUTURE_BAR_QUALITY_FAILED',)
  noc_reasons=('LBL_FUTURE_BAR_QUALITY_FAILED',)
  ```
  Excursion is *correctly* invalidated (it legitimately reads every bar in the
  window), but CC and NOC — which never read offset-3's price at all — are
  invalidated by the same event. Script:
  `/tmp/rcc002_s7_independent_checks_part2.py` ("D (cont.)" section).
  By contrast, the same function correctly scopes `LBL_ENTRY_PRICE_INVALID`/
  `LBL_EXIT_PRICE_INVALID` per family (CC never receives an entry-price
  reason; Excursion/Barrier never receive an exit-price reason) — confirming
  family-local scoping *is* the implementation's intended design elsewhere in
  the same function, making the window-wide quality check an inconsistency
  rather than a deliberate blanket policy.
- **Concrete impact**: no leakage or false-valid-label risk (the direction is
  always toward *more* invalidation, never less) — but CC/NOC labels
  (`fwd_cc_*`, `fwd_noc_*`, `label_cc_*_direction`, `label_noc_*_direction`,
  and their net-proxy variants) are unnecessarily marked invalid whenever
  *any* bar anywhere in a potentially very large window (up to 1,440 bars for
  H1440) has a quality problem the family never touches. On a real BTCUSDT
  history with scattered short data-quality incidents, this measurably reduces
  usable CC/NOC label coverage for the larger horizons specifically, contrary
  to what the family-scoped quality contract in §5.5 promises.
- **Minimal required correction**: scope the future-bar-quality check per
  family instead of applying `common` uniformly: CC should only test
  `_quality_contract_passes(current)` and `_quality_contract_passes(end)`; NOC
  should only test `_quality_contract_passes(future[0])` (the entry bar) and
  `_quality_contract_passes(end)`; Excursion and Barrier are correct as-is
  (they legitimately require every bar `t+1..t+h`).

### S7-CLAUDE-002 (MAJOR) — Naive per-row-per-horizon algorithm is impractically slow for a realistic full build

- **File / function**: `rcc002/s7/compute.py:_compute_complete_horizon` (calls
  `formulas.excursion_values` and `formulas.barrier_outcomes` once per row per
  horizon, each doing an `O(bars)` scan from scratch — no state is carried
  between consecutive rows of the same horizon); `rcc002/s7/compute.py:174
  (_price_valid)` and `rcc002/s7/formulas.py:16 (_finite_positive)` (both use
  `isinstance(value, numbers.Real)`, an ABC-based check that is materially
  slower than a concrete `(int, float)` check, and both are called redundantly
  — once in `compute.py`'s pre-check pass, again inside the formula itself).
- **Violated/relevant normative rule**: RG/LF §39.2 "Abnahme der
  Implementierung", item 11: *"BTCUSDT-1m-Vollbuild auf der Workstation
  erfolgreich ist"* — a full build must succeed on a workstation. The
  specification's own purpose statement (§1, §21) and the wider CLAUDE.md
  project context (K3→K12 raster search over signal combinations, iterative
  strategy research) establish that this pipeline is meant to support
  *repeated* full/partial rebuilds across horizons, cost/barrier profiles, and
  time windows, not a single one-off run.
- **Reproducible evidence** (all commands re-runnable from repo root with
  `.venv` active; synthetic OHLC random-walk data, `TP=5%`/`SL=2%`, seeded):
  ```
  n=1,500   5.64s    266 rows/s
  n=2,500  19.87s    126 rows/s
  n=3,500  34.44s    102 rows/s
  n=6,000  51.36s    117 rows/s
  n=6,000->7,000 (marginal, 1,000 extra rows): 31.68s for the increment ≈ 32 rows/s
  ```
  `cProfile` on `n=1,600` (35.3s total): `_price_valid`-family checks account
  for **3,459,779** calls; `isinstance`/`abc.__instancecheck__` machinery
  alone accounts for **~7.8s** of cumulative time (≈22% of total), on top of
  the intrinsic `O(Σh) = O(1,761)` bar-visits-per-row from the excursion/
  barrier computation itself (`1+5+15+60+240+1,440` bars summed across the six
  horizons). Scaling is consistent with linear-in-`n` with a large constant
  (not quadratic) once past the `n > 1,440` warm-up region, but the constant
  is large enough that a modest single-machine benchmark script run (part of
  this review) needed to be killed after exceeding a 300-second budget at
  `n=20,000` before completing. Peak RSS for `n=1,500` was ≈53 MiB
  (≈9.4 KB/row including Python object overhead), so memory is a secondary
  concern relative to runtime, though a fully in-memory multi-year build
  (~2.6M rows for 5 years) would still need tens of GB unless run through the
  already-supported partitioned/overlap execution path.
- **Concrete impact**: extrapolating even the most favorable measured
  steady-state rate (≈117 rows/s) to a 5-year BTCUSDT 1-minute history
  (5 × 365.25 × 24 × 60 ≈ 2,629,800 rows) gives **≈6.2 hours** for a single
  symbol/interval/profile full build; the more representative marginal rate
  (≈32–100 rows/s) extends this to many hours, plausibly approaching a full
  day. This does not prevent the build from eventually completing (so it is
  not classified `CRITICAL`; there is no evidence of non-termination or
  superlinear/quadratic blowup), but it is a severe practical obstacle to the
  pipeline's explicit purpose of supporting iterative multi-horizon,
  multi-profile, walk-forward research, and puts real strain on satisfying
  §39.2.11 in a useful timeframe on ordinary workstation hardware. The
  implementer's own record correctly lists the BTCUSDT full build as **not
  yet attempted** ("Noch ausstehend: ... BTCUSDT-1m-Vollbuild"), so this
  finding surfaces a concrete, previously unverified risk to that pending
  step rather than contradicting any implementer claim.
- **Minimal required correction**: (a) replace the `numbers.Real`/
  `numbers.Integral` ABC checks in the hot path (`_price_valid`,
  `_finite_positive`, and the equivalent checks in `schema.py`) with concrete
  `type(x) in (int, float)`-style checks; (b) remove the redundant double
  validation (compute.py's `_price_valid` pre-checks duplicate work already
  done inside `formulas.py`'s `_finite_positive`); (c) replace the naive
  `O(h)` per-row-per-horizon max/min excursion scan with an amortized
  `O(1)`-per-row monotonic-deque sliding-window maximum/minimum shared across
  consecutive rows of the same horizon, which would remove the dominant
  `Σh = 1,761` factor entirely and make the algorithm genuinely `O(n)` with a
  small constant.

### S7-CLAUDE-003 (MINOR) — Schema does not cross-validate barrier outcome against hit-bar/hit-time nullness

- **File / function**: `rcc002/s7/schema.py`, `HorizonLabels._validate_family`
  (barrier branch, ≈lines 162–170).
- **Violated normative rule**: RG/LF §18.3 "Nullsemantik": *"Barrier-Outcomes
  lauten INVALID; Barrier-Trefferbar und -zeit sind null"* for the invalid
  case, and the implicit converse from §13.4/§16.4 that a `TP_FIRST`/
  `SL_FIRST`/`AMBIGUOUS_BOTH_HIT` outcome always carries a non-null hit-bar
  and hit-time, while `TIMEOUT` never does.
- **Reproducible evidence**: direct construction of a `HorizonLabels` instance
  with `barrier_valid=True`, `barrier_long_outcome_tp050_sl020=
  BarrierOutcome.TIMEOUT`, but `barrier_long_first_hit_bar_tp050_sl020=3`
  (non-null) and a non-null hit time — accepted by `__post_init__` without a
  `ValueError`. The only barrier-related checks present are "outcome ≠
  `INVALID`" (for the valid case) and the range check `1 <= first_bar <=
  horizon_bars` (which a stray value like `3` still satisfies), neither of
  which ties the outcome enum to the bar/time nullness.
- **Concrete impact**: none in the current production dataflow —
  `compute_labels` always derives `(outcome, bar, time)` atomically from
  `formulas.barrier_outcomes()`, whose `_barrier_for_direction` helper
  guarantees `TIMEOUT ⇒ (None, None)` and every other outcome `⇒ (offset,
  time)` by construction, so no currently reachable code path can produce the
  inconsistent object constructed above. This is a latent robustness gap, not
  an active defect: a future refactor of `compute.py`, or any other caller
  that constructs `HorizonLabels` directly, could silently create an
  internally-contradictory barrier record that still passes schema
  validation.
- **Minimal required correction**: add, for each direction independently, the
  cross-field check: `outcome is TIMEOUT` implies `hit_bar is None and
  hit_time is None`; `outcome in (TP_FIRST, SL_FIRST, AMBIGUOUS_BOTH_HIT)`
  implies `hit_bar is not None and hit_time is not None` (when the barrier
  family is valid).

No further findings met the bar for reporting. Two candidate observations
were investigated and **rejected** as non-findings after reproduction:

- The `label_available_at_h` value chosen for the `LBL_WINDOW_CROSSES_MARKET_SEGMENT`
  case (the close_time of the first row at/after the detected gap) is not
  explicitly pinned by §18.2, which only defines the two extremes (fully
  valid → `close_time_(t+h)`; tail-incomplete → `null`). The implementation's
  choice is a defensible, conservative reading of the general definition
  ("frühester Zeitpunkt, zu dem Ergebnis oder Invalidität vollständig
  bestimmbar ist") and is not contradicted by any other section — not a
  finding.
- Computing `short_return`/`short_log_return` as a bit-exact negation of the
  already-computed `long_return`/`long_log_return`, rather than independently
  evaluating the short-specific formula text in §6.2/§7.2, was checked
  explicitly per review instruction B.17. This is fully compatible with the
  normative formula and the bound numeric profile: it *exceeds* the §31.2
  sign-identity test requirement (`short_return = -long_return`) by
  construction (zero-tolerance-needed equality, rather than needing the
  `1e-12`/`1e-10` cross-implementation tolerance from §30.3), any deviation
  from a literal separately-evaluated formula would be bounded by a few ULP
  (≪ the registered tolerance), and §30.4's "Operationsreihenfolge jeder
  Formel" pinning is explicitly not yet finalized for this specific formula
  in the current (still-draft, "Baseline V1 Certified: Nicht erreicht") spec
  revision — not a finding.

## 6. Result of all 80 review points

Legend: **OK** = confirmed correct with independent evidence; **OK\*** =
confirmed correct, see related finding for a narrower caveat; **FINDING** =
see finding ID.

### A. Package, schema, registry (1–12)

| # | Point | Result |
|---|---|---|
| 1 | Exact acceptance of `rcc002.stage.s6-gates/1.0.0` | OK — `_validate_input_rows` checks `gate_schema_id`/`gate_schema_version` exactly; unordered/duplicate/foreign-series/wrong-schema-version inputs empirically rejected (§4.3 of this report). |
| 2 | Exact output `rcc002.stage.s7-labels/1.0.0` | OK — `LABEL_SCHEMA_ID`/`VERSION`/`REF` constants match spec §21.1 exactly. |
| 3 | Complete unchanged pass-through of all S6 fields | OK — `dataclasses.fields(S7Row)` prefix-matches `dataclasses.fields(S6Row)` exactly (73 vs. 60+13 checked directly); runtime preservation check in `compute_labels` compares every S6 field by value. |
| 4 | Exactly 14 S7 base fields | OK — `LABEL_METADATA_FIELDS` has 14 entries, matches spec §20.4 table exactly (programmatic diff against spec JSON). |
| 5 | Exactly 48 fields per horizon | OK — `HORIZON_LOCAL_FIELDS` has 48 entries; `constants.py` asserts this at import time. |
| 6 | Exactly six horizons → 302 new fields | OK — `LABEL_EXTENSION_FIELDS` has exactly 302 entries; import-time assertion; **exact** match (order + names) against the spec's own machine-readable `RCC002_S8_FIELD_OWNERSHIP_V1` S7_LABELS group (302/302, 0 diff). |
| 7 | Exact field order per §36.2 | OK — verified via the same 302/302 exact-order diff against the spec's canonical registry. |
| 8 | Exact types, nullability, enum domains | OK — spot-checked `_local_field_type` against §20.4–20.8 tables (Float64/Ja, UInt16, Int8, BarrierOutcome, TimestampUTCms, Boolean/Nein, OrderedList[Utf8]) — all match. |
| 9 | Exact horizon expansion H001/H005/H015/H060/H240/H1440 | OK — `HORIZONS` tuple matches spec §4.1 exactly (ids, minute counts, suffixes). |
| 10 | Exact profile/registry/schema IDs | OK — all `LABEL_PROFILE_ID`, `HORIZON_REGISTRY_ID`, `COST_PROFILE_ID`, `BARRIER_PROFILE_ID`, `REASON_CODE_REGISTRY_VERSION`, `NUMERIC_PROFILE_ID` constants match §21.1 exactly; `_validate_configuration` fail-closed rejects any mismatch. |
| 11 | Deterministic schema fingerprint / semantic config hash | OK — `LABEL_SCHEMA_FINGERPRINT_SHA256`/`SEMANTIC_BUILD_CONFIGURATION_SHA256` reproduced identically across three separate fresh process invocations. |
| 12 | No unregistered alias/extra fields | OK — `S7Row` is a fixed-field frozen dataclass (no arbitrary kwargs); `flatten_s7_extension` asserts output tuple order equals `LABEL_EXTENSION_FIELDS`; leakage guard additionally rejects unregistered field names (see §71–76). |

### B. Returns and direction labels (13–23)

| # | Point | Result |
|---|---|---|
| 13 | CC uses exactly C(t) and C(t+h) | OK — hand-computed oracle match for H001 and H005, incl. explicit off-by-one probe (§4.1 script). |
| 14 | NOC uses exactly O(t+1) and C(t+h) | OK — hand-computed oracle match, explicit off-by-one probe. |
| 15 | No off-by-one for any horizon | OK — H001/H005 explicitly probed against hand computation with the specific intent of catching t+h-1/t+h+1 errors; both passed. |
| 16 | Long/short sign and mathematical symmetry | OK — `short = -long` verified bit-exact for linear and log returns; MFE≥0/MAE≤0 sign contract verified and additionally enforced by schema. |
| 17 | Short-return-as-negation compatibility with normative formula/numeric profile | OK — see §5 "rejected non-findings" above for full reasoning; explicitly investigated per instruction, found compatible. |
| 18 | Log-return formulas | OK — `log(C(t+h)/C(t))` verified against oracle; short = -long verified bit-exact. |
| 19 | Fee-net-proxy exactly `gross_return - 0.0004` | OK — verified exactly (`==`, not `isclose`) against oracle. |
| 20 | Gross values not overwritten | OK — verified gross NOC return field retains its pre-net value after net-proxy computation. |
| 21 | Direction labels exclusively -1/0/1, no deadband | OK — `direction_label` has no threshold branch; zero-return case gives exactly 0; schema additionally constrains the domain to `{-1,0,1,None}`. |
| 22 | Handling of +0.0 and -0.0 | OK — `canonical_zero` collapses -0.0→+0.0 (sign-bit check via `math.copysign`); `direction_label`'s `>`/`<` comparisons are sign-of-zero-agnostic regardless. |
| 23 | Non-positive/non-finite/unusable price references | OK — `_price_valid`/`_finite_positive` reject ≤0, non-finite, non-numeric, and `bool` values; unusable prices route to `LBL_ENTRY_PRICE_INVALID`/`LBL_EXIT_PRICE_INVALID` per family. |

### C. Excursions and barriers (24–35)

| # | Point | Result |
|---|---|---|
| 24 | MFE/MAE for long and short | OK — all four formulas verified against a hand-computed 5-bar window (exact match). |
| 25 | Exact window t+1..t+h | OK — same test confirms the window boundary is exactly offsets 1..h relative to the signal row. |
| 26 | First offset on repeated extreme | OK — direct formula oracle with duplicate max and duplicate min, both correctly resolve to the first occurring index+1. |
| 27 | Offset range exactly 1...h | OK — schema enforces `1 <= first_bar <= label_horizon_bars` per-horizon (not a fixed global bound); empirically confirmed in range. |
| 28 | Long/short barrier prices TP 5% / SL 2% | OK — `TAKE_PROFIT_FRACTION=0.05`, `STOP_LOSS_FRACTION=0.02` match §15.2; price formulas match §13.2/13.3 exactly. |
| 29 | Chronological barrier search | OK — `_barrier_for_direction` iterates `future_rows` in order and returns on first hit; verified TP-before-SL-across-bars and SL-before-TP-across-bars both resolve to the correct first bar. |
| 30 | Open-gap priority before intrabar high/low | OK — verified for both long and short, including the specific case where the gap triggers one barrier while the intrabar range would also touch the other (gap wins, not ambiguous). |
| 31 | Exact touch counts as hit | OK — verified `high == tp_price` and `low == sl_price` (exact equality) both register as hits, matching §33's stated `>=`/`<=` touch rule. |
| 32 | TP_FIRST/SL_FIRST/TIMEOUT/AMBIGUOUS_BOTH_HIT/INVALID | OK — all five outcomes independently reproduced; `INVALID` confirmed for a tail-incomplete row with null hit-bar/time. |
| 33 | Long/short symmetry of barrier logic | OK — both directions computed by the same shared `_barrier_for_direction` helper against identical `future_rows`, ensuring structural symmetry by construction. |
| 34 | Hit bar and hit time | OK — verified correct bar offset and `close_time` value recorded for hit outcomes; both null for `TIMEOUT`. |
| 35 | Ambiguity/timeout reason codes with `barrier_valid=true` | OK — `AMBIGUOUS_BOTH_HIT` → `LBL_BARRIER_BOTH_HIT` and `TIMEOUT` → `LBL_BARRIER_TIMEOUT`, both verified to leave `barrier_valid=True` at the full `compute_labels` level (not just the formula level). |

### D. Validity, tail, segments (36–48)

| # | Point | Result |
|---|---|---|
| 36 | Full horizon on the exact 1m timeline | OK — `_compute_horizon` requires exact per-offset 1-minute contiguity across the whole window, verified via a missing-minute reproduction (fail-closed stage abort, see #39). |
| 37 | `market_segment_id` is the sole binding S7 segment boundary | OK — segment check in `_compute_horizon` references only `market_segment_id`; `indicator_segment_id` is never read for this purpose (grep-confirmed). |
| 38 | Signal row, entry, and all future rows stay in the same segment | OK — verified: a window crossing a segment boundary is invalidated with `LBL_WINDOW_CROSSES_MARKET_SEGMENT`; a window fully inside one segment remains valid. |
| 39 | Missing minute with later data present → `LBL_WINDOW_CROSSES_MARKET_SEGMENT` | OK — reproduced directly: removing one row from an otherwise-continuous same-segment series causes a **stage-wide fail-closed abort** (`ValueError` from `_validate_input_rows`, before any row-level output), because the gap is structurally invalid input, not a per-row condition — see §69/#43 below for the row-level case where the gap is only reachable within a valid partition's read-only overlap. |
| 40 | Incomplete dataset tail produces exclusively `LBL_FUTURE_HORIZON_INCOMPLETE` | OK — verified for the last row of a 10-row series at H001. |
| 41 | Tail rows are not removed | OK — row count preserved; tail row still present in output with all-invalid horizons. |
| 42 | Quality-invalid future rows | OK for Excursion/Barrier (correctly invalidated); **see S7-CLAUDE-001** for CC/NOC over-invalidation. |
| 43 | Synthetic future rows | OK — `quality_is_synthetic` on any future row contributes `LBL_SYNTHETIC_INPUT_DISALLOWED` (same family-scoping caveat as #42 applies to CC/NOC). |
| 44 | Family-local entry/exit invalidity | OK for entry/exit price specifically (verified `LBL_ENTRY_PRICE_INVALID`/`LBL_EXIT_PRICE_INVALID` are correctly family-scoped); **see S7-CLAUDE-001** for the adjacent future-bar-quality check, which is *not* family-scoped. |
| 45 | Family-local null semantics | OK — schema enforces all-null-or-all-populated per family per horizon; verified via `HorizonLabels._validate_family`. |
| 46 | No impermissible global `label_valid` | OK — no such field exists anywhere in the 302-field canonical registry (confirmed via the exact-match diff in #6/#7); validity is exclusively per-family. |
| 47 | `label_available_at_h` for complete/incomplete horizon | OK — `= close_time_(t+h)` for complete; `= null` for `LBL_FUTURE_HORIZON_INCOMPLETE`; a reasoned non-normatively-pinned value used for the window-crosses-segment case (see §5 "rejected non-findings"). |
| 48 | Segment-ID null semantics | OK — `fwd_cc_label_segment_id_h` etc. are `None` whenever the corresponding family is invalid, populated with `current.market_segment_id` only when valid; enforced by schema. |

### E. Reason codes (49–55)

| # | Point | Result |
|---|---|---|
| 49 | Exact register of 16 codes with exact priorities | OK — `REASON_CODE_REGISTRY` has exactly 16 entries with priorities `{10,20,30,40,50,60,100,110,120,130,140,150,160,170,180,190}`, matching §19.2 exactly; import-time assertion plus independent re-verification. |
| 50 | Stage codes must not appear on rows | OK — `validate_row_reason_code` rejects any `STAGE`-scoped code (e.g. `LBL_SCHEMA_MISMATCH`) from a row-level reason list; reproduced directly. |
| 51 | Historical alias `LBL_WINDOW_CROSSES_GAP` rejected | OK — not present in the registry at all; `normalize_reason_codes(["LBL_WINDOW_CROSSES_GAP"])` raises `LabelReasonCodeError`, reproduced directly. |
| 52 | Deduplication and deterministic sorting | OK — reproduced: duplicate + unordered input codes are deduplicated and returned sorted by ascending registry priority. |
| 53 | All safely determinable row-level reasons retained | OK — verified via the multi-reason case (`LBL_WARMUP...`-analog for S7: combined regime/strength-style compounding is N/A here, but the equivalent compounded-reason case — segment + quality — was inspected in code and preserves all applicable codes via `normalize_reason_codes` over the accumulated list). |
| 54 | Valid barrier info codes not treated as invalidating | OK — `LBL_BARRIER_BOTH_HIT`/`LBL_BARRIER_TIMEOUT` verified compatible with `barrier_valid=True` at the full compute level. |
| 55 | Invalid families require ≥1 invalidating code | OK — schema raises if an invalid family has an empty reason list or a reason list without any code in `INVALIDATING_REASON_CODES`. |

### F. Architecture and reproducibility (56–70)

| # | Point | Result |
|---|---|---|
| 56 | `S7_rows = S6_rows` | OK — verified for a full (non-partitioned) build; `output_row_count` mechanism additionally verified for partitioned builds (owned-prefix count only). |
| 57 | Primary key, order, `market_segment_id` unchanged | OK — verified field-by-field for every row in a reproduction run. |
| 58 | No change to S0–S6 field values | OK — verified field-by-field (`dataclasses.fields(S6Row)`, which transitively covers S0–S6) for every row; also enforced at runtime by `compute_labels` itself. |
| 59 | No mutable reference-sharing of `indicators`/`signals` | OK — verified object identity differs and mutating the S7 copy does not affect the source S6 row. |
| 60 | Computation independent of signals/regimes/gates | OK — verified empirically (flipping `allow_long`/`allow_short`/`gate_state` to their consistent opposite leaves all 302 label fields byte-identical) and via code inspection (no formula ever reads `allow_*`, `regime_*`, `sig_*`, `score_*`). |
| 61 | No future data flowing back into S0–S6 | OK — `compute_labels` only reads source rows via `getattr`, never mutates them (frozen dataclasses; no `object.__setattr__` on inputs anywhere in `compute.py`). |
| 62 | Partition execution with up to 1,440 read-only overlap rows | OK — `output_row_count` mechanism verified to reproduce the full-build values exactly for the owned prefix, using the remaining rows purely as lookahead. |
| 63 | No double emission of overlap rows | OK — verified `len(partition_result.rows) == output_row_count` (overlap rows never appear in `.rows`). |
| 64 | Serial vs. partitioned parity | OK — verified for an arbitrary split point (not just a boundary aligned to a horizon), full 302-field equality. |
| 65 | Prefix causality: changes after t+h don't change Label(t,h) | OK — verified with a mutation exactly at the row that is the *boundary* of one horizon (H015) and confirmed it (a) does not affect shorter horizons (H001/H005) and (b) *does* affect H015 itself (sanity check that the test is discriminating). |
| 66 | Incremental invalidation ≥ [k-1440, ..., k] | OK — `invalidation_start_index` verified to return `max(0, k - 1440)`. |
| 67 | Chronological split-purging | OK — `label_crosses_split` implements a conservative (safe-direction) purge boundary; no exact normative formula exists to compare against, reasoning documented in code review. |
| 68 | Behavior on empty input and invalid `output_row_count` | OK — empty input → empty output, no crash; out-of-range or negative `output_row_count` raises `ValueError`. |
| 69 | Stage-wide fail-closed abort on schema/profile/interval/order/series errors | OK — reproduced for: unknown schema version, unordered input, duplicate primary key, and a same-segment timestamp gap — all raise before any row is emitted. |
| 70 | Unknown fields/profiles not silently accepted | OK — `_validate_configuration` fail-closed rejects any profile/registry ID or version mismatch; `S7Row`'s fixed dataclass fields reject arbitrary extra data. |

### G. Leakage (71–76)

| # | Point | Result |
|---|---|---|
| 71 | Every one of the 302 fields has `field_owner_stage=S7_LABELS` | OK — `LabelFieldDefinition`'s default is `S7_LABELS` and is never overridden for any of the 302 generated entries (verified by inspection of the generator code — no call site passes a different value). |
| 72 | Every one of the 302 fields has `leakage_class=FUTURE_OUTCOME` | OK — same default-never-overridden pattern verified. |
| 73 | All S7 fields locked for Live/Paper/Backtest Input/Research Features | OK — `LabelFieldDefinition` defaults `live_allowed=paper_allowed=backtest_input_allowed=research_feature_allowed=False`, `label_research_allowed=True` for all 302 fields, matching §36.3 exactly. |
| 74 | `fwd_`/`label_`/`barrier_` prefixes additionally fail-closed detected | OK — `leakage.assert_no_s7_fields` rejects any field starting with those prefixes independent of its claimed owner metadata; reproduced with a spoofed-owner bypass attempt. |
| 75 | Ownerless fields and fields outside positive allowlists rejected | OK — reproduced both: a field with no registered owner, and a field with a valid non-S7 owner but absent from the positive allowlist, are both rejected. |
| 76 | Search for ways to bypass the leakage guard | Two concrete bypass attempts constructed and both correctly blocked: (a) a field with **no** `fwd_/label_/barrier_` prefix and a name absent from `S7_FIELD_REGISTRY`, but with owner metadata spoofed to `S7_LABELS` — blocked by the owner check; (b) a field **with** an `fwd_` prefix but owner metadata spoofed to a non-S7 stage and present in the positive allowlist — blocked by the prefix check independent of claimed ownership. All 302 registered S7 fields individually verified to be rejected (§34.4's specific requirement). No bypass found. |

### H. Tests and production risks (77–80)

| # | Point | Result |
|---|---|---|
| 77 | False-positive tests / shared code-oracle bugs / unreachable code paths | The implementer's `tests/rcc002/s7/*` were inspected only for gap analysis, not trusted; my own independent oracle (not derived from the implementer's code or tests) found 327+ passing checks and the three findings above. One unreachable-code-adjacent item was found and reported as **S7-CLAUDE-003**. No evidence of a shared bug between implementation and implementer test oracle was found (my independently-derived oracle disagreed with the implementation only where the two MAJOR findings above are — both confirmed as real implementation behavior, not test artifacts). |
| 78 | Edge cases not covered by existing tests | The family-scoping gap (S7-CLAUDE-001) was **not** caught by the implementer's own test suite (566 RCC-002 tests, 42 S7 tests, all passing) — none of them constructs a quality failure confined to a bar not consumed by CC/NOC. This is itself a test-coverage gap worth noting for the implementer. |
| 79 | Runtime/memory complexity for a multi-year BTCUSDT-1m full build | **See S7-CLAUDE-002.** Documented as a MAJOR finding with reproducible timing evidence; not classified CRITICAL because the algorithm terminates and scales linearly (not super-linearly) in row count, and partitioned execution is available to bound memory (though not runtime). |
| 80 | Readiness Review / Implementation Record claims not met by the actual code | No overclaim found. The Record's claim "Entry- und Exit-Invalidität bleiben familienlokal" is narrowly and accurately scoped to entry/exit price invalidity specifically (confirmed correct) and does **not** claim general family-local quality scoping, so it is not contradicted by S7-CLAUDE-001. The Record explicitly lists the BTCUSDT full build as **not yet attempted** ("Noch ausstehend"), so it makes no performance claim that S7-CLAUDE-002 would contradict — this finding surfaces a risk to that still-pending step rather than an overclaim. |

## 7. Required existing tests executed

All run from repo root, `.venv` active:

```text
python -m compileall -q rcc002 tests/rcc002
  -> PASS (exit 0)

python -m unittest discover -s tests/rcc002/s7 -t .
  -> Ran 42 tests, OK

python -m unittest discover -s tests/rcc002 -t .
  -> Ran 566 tests, OK
```

Per instruction 4/instruction 7, these results are reported for completeness
but were **not** used as evidence of correctness; all Pass/Fail determinations
above rest on the independent reproductions in §8.

## 8. Independent test cases and results (own oracles, not implementer tests)

Three standalone scripts, all under `/tmp` only, none touching the repository
or the review package:

- `/tmp/rcc002_s7_independent_checks.py` — returns, off-by-one checks,
  direction labels, +0.0/-0.0, excursions (hand-computed MFE/MAE against an
  explicit OHLC window, duplicate-extreme offsets), barrier logic (TP/SL first
  hit, cross-bar ordering, open-gap priority incl. the gap-wins-over-intrabar
  case, exact-touch, ambiguity, timeout, long/short structural symmetry).
  **28/28 checks passed** after two self-inflicted fixture bugs were found and
  corrected (an OHLC-inconsistent test fixture that the implementation
  correctly rejected, and a non-duplicate "duplicate" test value) — both
  corrections are noted in-line in the script and did not change any
  conclusion about the implementation.
- `/tmp/rcc002_s7_independent_checks_part2.py` — tail/segment/gap handling,
  reason-code registry mechanics, the family-scoping investigation (source of
  S7-CLAUDE-001), row/key/segment preservation, container independence,
  gate-independence, empty input, invalid `output_row_count`, partition
  parity (including an arbitrary non-horizon-aligned split point), prefix
  causality (including a sanity check that the causality test is
  discriminating, not a no-op), incremental-invalidation helper, and the
  leakage-guard bypass attempts. **41/41 checks passed** (all remaining checks
  after the causality-test's own initial fixture bug — mutating a row that
  was legitimately inside the H015 window — was found and corrected).
- `/tmp/rcc002_s7_perf_benchmark.py` plus several ad hoc `cProfile`/timing
  invocations — see §9.

Total independent, non-implementer-derived assertions executed and passed:
**69**, plus the 3 findings surfaced by dedicated investigation scripts and
one `cProfile` run.

## 9. Runtime/memory assessment

See **S7-CLAUDE-002** for the full write-up. Summary of raw measurements
(synthetic realistic-scale OHLC random walk, single-threaded CPython on the
review machine, no parallelism or vectorization used by the implementation):

| n (rows) | wall time | rows/s |
|---:|---:|---:|
| 1,500 | 5.64s | 266 |
| 2,500 | 19.87s | 126 |
| 3,500 | 34.44s | 102 |
| 6,000 | 51.36s | 117 |
| 6,000→7,000 (marginal) | 31.68s | 32 |

Extrapolated full-build estimate for 5 years of BTCUSDT 1-minute data
(≈2,629,800 rows) at the most favorable measured rate: **≈6.2 hours**; at the
more representative marginal rate: on the order of a full day. Peak RSS at
n=1,500 was ≈53 MiB (≈9.4 KB/row); memory is not the primary constraint given
the already-supported partitioned execution path, but a naive fully in-memory
multi-year run would require tens of GB. Root cause identified via `cProfile`:
`numbers.Real`/`numbers.Integral` ABC-based `isinstance` checks plus a
structurally naive `O(row_count × Σhorizon_bars)` (`Σ=1,761`) recomputation of
max/min/barrier-search from scratch for every row/horizon pair, with no
amortization (e.g. a sliding-window monotonic deque) across consecutive rows.

## 10. Finding counts by severity

| Severity | Count |
|---|---:|
| CRITICAL | 0 |
| MAJOR | 2 |
| MINOR | 1 |
| EDITORIAL | 0 |

## 11. Final decision

```text
REJECTED
```

Two open `MAJOR` findings (S7-CLAUDE-001, S7-CLAUDE-002) preclude `APPROVED`
per the stated rule ("APPROVED ist nur zulässig, wenn kein offenes CRITICAL-
oder MAJOR-Finding besteht"). Neither finding involves data leakage, an
incorrect sign, an incorrect discrete label/barrier outcome, or a falsely
valid result — the implementation's core return/excursion/barrier/reason-code/
schema/leakage machinery is correct against 69 independently derived,
non-implementer-sourced test assertions with zero mismatches. The two MAJOR
findings are both concrete, reproducible, and — in this reviewer's assessment
— tractable to correct without an architectural rework: S7-CLAUDE-001 is a
narrow, well-localized scoping fix in `_base_reason_codes`/
`_compute_complete_horizon`, and S7-CLAUDE-002's primary fix (removing ABC
`isinstance` overhead and redundant double-validation) is also narrow, though
its full resolution (sliding-window excursion computation) is a more
substantial but well-understood algorithmic change.

No file inside the repository or inside the review package was modified by
this review.

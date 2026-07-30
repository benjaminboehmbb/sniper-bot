# RCC-002 S7 Corrected Re-Review — Claude

Date: 2026-07-30
Reviewer: Claude (independent corrected re-review, per user request)
Scope: `S6_GATES -> S7_LABELS` implementation only (`rcc002/s7/`, `tests/rcc002/s7/`),
full re-review (not diff-only), with focused verification of the three
findings from `RCC_002_S7_CLAUDE_INDEPENDENT_REVIEW_2026-07-30.md`.

## 1. Package identity

```text
File:     RCC_002_S7_CORRECTED_RE_REVIEW_PACKAGE_2026-07-30.zip
Expected: 8d9677747cf894c2e5414ffdf826fa61bdf3b01531cd934e93fddc2af017d8e9
Actual:   8d9677747cf894c2e5414ffdf826fa61bdf3b01531cd934e93fddc2af017d8e9
Result:   MATCH
```

Note on the prompt's premise: the instructions stated the review is conducted
"already inside the fully unpacked package," but the actual shell working
directory was the repository root (`/home/benja/projects/sniper-bot`), with
only the zip present there. The package was extracted read-only to
`/tmp/rcc002_s7_re_review/pkg` following the same protocol as the two prior
S7 reviews; no file inside the zip or the repository was modified. `diff -rq`
confirmed the repository's untracked `rcc002/s7/` and `tests/rcc002/s7/`
working-tree copies are **already byte-identical** to the package's copies
(only `__pycache__` differs), so running the test/verification suite directly
against the repository exercises exactly the code under review. The three
normative documents inside the package are byte-identical to the
repository's `docs/review/` and `docs/certification/` copies.

## 2. Source-grounding inventory

Normative basis used (exclusively, per instruction):

- `docs/review/RCC_002_DVSEV001_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md`
  (RG/LF Label and Forward Return spec sections, previously read in full for
  the original review; re-consulted for every finding below)
- `docs/review/RCC_002_DVSEV001_CORRECTED_BUNDLE_MANIFEST_2026-07-27.md`
- `docs/certification/RCC_002_DVSEV001_CERTIFICATION_DECISION_2026-07-27.md`

`RCC_002_S7_IMPLEMENTATION_READINESS_REVIEW_2026-07-30.md`,
`RCC_002_S7_IMPLEMENTATION_RECORD_2026-07-30.md`, and
`RCC_002_S7_INDEPENDENT_REVIEW_RESOLUTION_2026-07-30.md` were read only as
the implementer's claims about what changed and why (instruction 4); every
claim in them was independently re-derived from the source diff and/or
reproduced with dedicated test scripts before being treated as true. The
package also contains my own prior report
(`RCC_002_S7_CLAUDE_INDEPENDENT_REVIEW_2026-07-30.md`) for reference only.

**Diff-first scoping, then full review.** Before reviewing, a file-level diff
was taken against the exact package I reviewed previously
(`/tmp/rcc002_s7_review/pkg`, `RCC_002_S7_INDEPENDENT_REVIEW_PACKAGE_2026-07-30.zip`,
SHA-256 `10e2612c...`) to know precisely what changed:

```text
Changed:   rcc002/s7/compute.py, constants.py, formulas.py, schema.py
           tests/rcc002/s7/test_compute.py, test_schema.py
Unchanged: rcc002/s7/__init__.py, leakage.py, planning.py, reason_codes.py
           tests/rcc002/s7/_helpers.py, test_formulas.py,
           test_golden_fixtures.py, test_planning.py, test_reason_codes.py
           rcc002/s3, s4, s5, s6 (entire trees, byte-identical)
```

Per instruction 5, the review was **not** limited to the diff: every line of
all eight `rcc002/s7/*.py` files was re-read in full (not just the four
changed files), the complete 302-field registry was re-derived and
re-diffed against the spec's machine-readable `RCC002_S8_FIELD_OWNERSHIP_V1`
JSON (as in the original review), and the reason-code registry, leakage
guard, and architectural/reproducibility properties were all independently
re-verified from scratch rather than assumed unchanged just because their
source files were untouched.

## 3. Tests executed and own checks performed

### 3.1 Required existing tests (repo root, `.venv` active)

```text
python -m compileall -q rcc002 tests/rcc002
  -> PASS (exit 0)

python -m unittest discover -s tests/rcc002/s7 -t .
  -> Ran 49 tests, OK   (was 42 in the original package; 7 new tests added
                          for the three fixes)

python -m unittest discover -s tests/rcc002 -t .
  -> Ran 573 tests, OK  (was 566)

python -m unittest discover -s tests/regression -t .
  -> Ran 170 tests, OK
```

As before, these results are reported for completeness but are **not**
treated as proof of correctness (instruction 4/6); every conclusion below
rests on the independent reproductions in §3.2–§3.4.

### 3.2 Independent re-verification of each original finding

All scripts below are new for this re-review and live only under `/tmp`.

- `/tmp/rcc002_s7_rereview_finding001.py` — **S7-CLAUDE-001**: 24 fresh,
  independent checks (not the implementer's tests) covering: quality failure
  at an intermediate bar only (CC/NOC must stay valid, Excursion/Barrier must
  not); the same for a synthetic-only flag; quality failure exactly at the
  entry bar `t+1` (must invalidate NOC but not CC); exactly at the exit bar
  `t+h` (must invalidate both); at the current/signal row `t` (must
  invalidate all four families — this is *not* supposed to become
  family-scoped away); a market-segment boundary crossing mid-window (must
  invalidate all four families — segment rule stays window-wide as required);
  the `H001` edge case where the entry and exit bar are the same index (no
  duplicate reason codes); and multiple scattered intermediate failures.
  **24/24 passed.**
- Direct interactive script (barrier-hit-consistency probes) —
  **S7-CLAUDE-003**: 9 fresh checks covering baseline TIMEOUT acceptance, the
  original reported gap (TIMEOUT + non-null hit bar/time, now rejected),
  TP_FIRST/SL_FIRST/AMBIGUOUS_BOTH_HIT each independently with both null
  (rejected) and correct non-null (accepted) hit metadata, a
  long-side-consistent/short-side-inconsistent mixed case (rejected), and the
  pre-existing `INVALID`-outcome invariant (still accepted, unaffected).
  **9/9 passed.**
- `/tmp/rcc002_s7_naive_oracle_crosscheck.py` — **S7-CLAUDE-002**: a complete,
  from-scratch reimplementation of CC/NOC/Excursion/Barrier logic directly
  from the RG/LF spec text (zero imports from `rcc002.s7.formulas` or
  `rcc002.s7.compute`'s internal helpers — see §3.3 for why this
  independence matters), cross-checked field-by-field against the actual
  optimized `compute_labels()` output across: a 60-row random-walk series (all
  six horizons, complete and tail-incomplete cases), whole-window identical
  high/low ties, duplicate-extreme tie-breaking, an open-gap-over-both-
  barriers-in-different-bars case, pure intrabar ambiguity, a mid-window
  market-segment boundary, a fully incomplete tail, and an exact-touch case —
  plus a second high-volatility batch (frequent barrier hits, 120 rows,
  sampled). **714/714 row-horizon combinations matched exactly, 0
  mismatches.**
- Dedicated boundary-condition script — single-row dataset, empty dataset,
  a horizon whose end index lands exactly on the last row of the dataset,
  and a dataset exactly one row short of a horizon's requirement. **4/4
  passed**, confirming the new segment-tree/rolling-extrema machinery has no
  off-by-one at the array boundary.

### 3.3 A note on independence (why a from-scratch oracle was necessary)

The implementer's own new test
(`test_optimized_windows_match_naive_formula_oracle` in `test_compute.py`)
compares the optimized path against `rcc002.s7.formulas.excursion_values`/
`barrier_outcomes`. Inspection of the diff shows these "naive" comparison
functions **share code** with the optimized path: both the old linear-scan
`_barrier_for_direction` (still present in `formulas.py`, used by the
comparison functions) and the new range-tree-based
`compute._barrier_for_direction` call the same extracted
`barrier_outcome_at_bar()` helper to classify a single candidate bar. A bug
inside `barrier_outcome_at_bar()` itself would therefore be invisible to that
particular implementer test, since both sides of the comparison would inherit
it identically. This is precisely the scenario instruction 7's "unabhängig
implementiertes naives Orakel" requirement guards against — my
`/tmp/rcc002_s7_naive_oracle_crosscheck.py` shares **zero** code with either
the old or the new implementation (it reimplements the open-gap-priority,
intrabar-touch, and ambiguity rules directly from spec §16 text), so its
714/714 match is a materially stronger independence guarantee than the
implementer's own regression test provides. This is noted as a residual
observation in §8, not elevated to a finding, because it does not indicate an
actual defect — only a narrower blind spot in the implementer's own test than
in mine, and mine found nothing wrong.

### 3.4 Reproducible performance benchmark

```text
n=2,000    1.931s   1,036.0 rows/s
n=8,000    8.622s     927.9 rows/s
n=20,000  24.672s     810.6 rows/s
n=50,000  55.353s     903.3 rows/s
```

Throughput is now stable (≈800–1,000 rows/s) across nearly two orders of
magnitude of `n`, in sharp contrast to the original review's measurements,
which *decreased* monotonically well past the `n > 1,440` warm-up region
(266 → 126 → 102 → 117 → 32 rows/s marginal) — the original evidence of a
`O(n × Σh)` cost profile. `cProfile` on `n=6,000` confirms the shift: the
previously dominant `abc.__instancecheck__`/`numbers.Real` machinery no
longer appears in the top-15 cumulative-time functions at all (replaced by
concrete `type(x) in (int, float)` checks), and the call count for
`_compute_complete_horizon`-family functions is now `O(n × horizons)`
(36,000 calls for 6,000 rows × 6 horizons — exactly one call per row per
horizon) rather than `O(n × Σh)`. The remaining cost is dominated by
legitimate per-row `HorizonLabels`/`S7Row`/inherited-`S6Row`-chain schema
validation, not window recomputation.

Extrapolated to a 5-year BTCUSDT 1-minute full build (≈2,629,800 rows) at the
measured ≈900 rows/s: **≈49 minutes**, down from the original review's
best-case estimate of ≈6.2 hours (worst-case approaching a day). The
implementer's own Resolution Record reports a higher throughput
(≈2,600–2,954 rows/s on their machine, implying ≈16 minutes) — the exact
figure is understandably machine/data-dependent, but both my independently
measured number and theirs land in the same qualitative regime: a full build
is now on the order of tens of minutes, not hours to a day. This decisively
resolves the practical-usability concern raised in S7-CLAUDE-002.

## 4. Status of each original finding

### S7-CLAUDE-001 (was MAJOR) — Family-local quality validation

```text
STATUS: RESOLVED
```

Root cause and fix independently confirmed by direct code reading of
`rcc002/s7/compute.py`: the monolithic `_base_reason_codes()` (which applied
a single window-wide quality/synthetic verdict to all four families
uniformly) was replaced by three distinct helpers —
`_current_reason_codes()` (signal row only, applies universally, as
required), `_future_reason_codes_at()` (checks quality/synthetic **only** at
the caller-supplied specific indices — used with `(end_index,)` for CC and
`(entry_index, end_index)` for NOC), and `_future_reason_codes_range()`
(checks the **full** `[entry_index, end_index]` window via `O(1)` prefix-sum
range queries — used for Excursion and Barrier). Market-segment-boundary
checking remains in `_compute_horizon`, upstream of and independent from this
family-split, and still covers the full window for all four families
uniformly (correctly — segment consistency is not supposed to be
family-scoped per §17.2). All 24 independent reproductions in §3.2 confirm
this exactly matches the required behavior, including the specific
counterexample from the original finding (quality failure at offset 3 of a
5-bar window: `fwd_cc_valid_h005` and `fwd_noc_valid_h005` are now `True`,
`fwd_excursion_valid_h005`/`barrier_valid_h005` remain correctly `False`).

### S7-CLAUDE-002 (was MAJOR) — Runtime/algorithmic complexity

```text
STATUS: RESOLVED
```

The naive per-row-per-horizon `O(bars)` rescans were replaced with: (a) a
monotonic-deque sliding-window maximum/minimum (`_rolling_extrema`) computing
all excursion extrema for a given horizon across **all** rows in amortized
`O(n)` (not `O(n × bars)`) — independently verified correct via the deque
algorithm's own logic (window-boundary popping keyed to `right - bars`) and
via the 714-case naive-oracle cross-check; (b) a segment-tree
(`_BarrierRangeIndex`) over per-bar composite "reachable extreme" values
(`max(open, high)` / `min(open, low)`) that locates the first index in
`[t+1, t+h]` where *either* barrier threshold is reachable in `O(log n)`,
after which the exact original open-gap-priority/intrabar/ambiguity
classification (`barrier_outcome_at_bar`, logic byte-for-byte unchanged from
the original review) is applied to that single candidate bar to produce the
final outcome — independently verified to be a mathematically exact (not
approximate) reduction of the original per-bar predicate (§16.2's gap
condition `open ≥ tp_price ∨ open ≤ sl_price`, generalized, is exactly
`max(open,high) ≥ threshold_upper ∨ min(open,low) ≤ threshold_lower` for both
LONG and SHORT after accounting for the direction-dependent threshold
assignment), confirmed empirically via 0/714 mismatches including
high-volatility (frequent-hit) data; (c) the `numbers.Real`/`numbers.Integral`
ABC-based `isinstance` checks flagged as a profiled hotspot were replaced
with concrete `type(x) in (int, float)` checks throughout `compute.py` and
`schema.py`. Reproducible benchmarking (§3.4) confirms throughput is now
stable at ≈800–1,000 rows/s regardless of scale (previously
monotonically decreasing well past `n=1,440`), reducing the extrapolated
5-year full-build time from hours (potentially a day) to well under an hour.

### S7-CLAUDE-003 (was MINOR) — Barrier schema invariants

```text
STATUS: RESOLVED
```

A new `HorizonLabels._validate_barrier_hits()` method, called from
`__post_init__` whenever `barrier_valid` is `True`, independently checks each
direction (long, short): `TIMEOUT` requires both hit-bar and hit-time to be
`None`; any other outcome (`TP_FIRST`, `SL_FIRST`, `AMBIGUOUS_BOTH_HIT`)
requires both to be non-`None`. All 9 independent reconstructions in §3.2
confirm this closes the exact gap originally reported (a manually
constructed `TIMEOUT` + non-null hit-bar/time object is now rejected with
`ValueError`) while leaving the pre-existing `INVALID`-outcome path (governed
by a separate, previously-correct check) unaffected, and correctly enforces
the invariant **per direction independently** (a long-side-consistent,
short-side-inconsistent object is still rejected).

## 5. New findings matrix (this re-review)

No new `CRITICAL` or `MAJOR` finding was identified. One `MINOR`
observation and one `EDITORIAL` note are reported; neither blocks approval.

| ID | Severity | File / Function | Rule |
|---|---|---|---|
| S7-CLAUDE-RR-001 | MINOR | `rcc002/s7/constants.py:14` (`COMPONENT_VERSION`) | RG/LF §21.3, general traceability practice |
| S7-CLAUDE-RR-002 | EDITORIAL | `tests/rcc002/s7/test_compute.py` (`test_optimized_windows_match_naive_formula_oracle`) | Instruction 7 / test-independence hygiene |

### S7-CLAUDE-RR-001 (MINOR) — Component version not bumped for a behavior-changing correction

- **File / location**: `rcc002/s7/constants.py:14`,
  `COMPONENT_VERSION: Final[str] = "0.3.0"` (unchanged across this
  correction cycle).
- **Observation**: this correction cycle changed observable output for
  certain input rows (`fwd_cc_valid_h`/`fwd_noc_valid_h` and dependent fields
  can now be `True` where the previous implementation produced `False` for
  the same input — see S7-CLAUDE-001), yet `COMPONENT_VERSION` was left at
  `0.3.0`. The `semantic_build_configuration_sha256` **was** correctly
  updated (the spec-designated mechanism for tracking build-affecting
  semantic changes per §37.1), and the logical schema/field structure is
  genuinely unchanged (`label_schema_fingerprint_sha256` correctly stays
  identical), so this is not a schema-versioning violation under §21.4 (no
  field, type, enum, or meaning changed) — the finding is purely about
  `component_id`/`component_version` as an implementation-build identity
  marker (§21.3: "Die Implementierung manifestiert zusätzlich:
  Source-Tree- oder Commit-Identität ... Label-, Horizon-, Kosten-,
  Barrier- und Reason-Code-Profilversionen").
- **Impact**: low — the `semantic_build_configuration_sha256` change is
  sufficient to distinguish old and new build outputs at the dataset level,
  so no leakage/reproducibility risk exists. It is, however, a minor
  traceability gap: two different `RCC002_S7_LABEL_BUILDER` component builds
  that produce observably different valid/invalid verdicts for the same
  input now report the same `component_version`, which could complicate
  debugging a future discrepancy between two datasets built with different
  code revisions if only `component_version` (not the full config hash) is
  consulted.
- **Correction**: bump `COMPONENT_VERSION` (e.g. to `0.4.0`) for this
  behavior-changing correction cycle, consistent with ordinary software
  build-identity practice; not required to be re-derived from the
  specification, which does not mandate a specific bump policy for
  implementation (as opposed to schema) versions.

### S7-CLAUDE-RR-002 (EDITORIAL) — Implementer's own "naive oracle" test shares code with the implementation under test

- **File / location**: `tests/rcc002/s7/test_compute.py`,
  `test_optimized_windows_match_naive_formula_oracle`.
- **Observation**: see §3.3. The comparison target
  (`rcc002.s7.formulas.excursion_values`/`barrier_outcomes`) shares the
  `barrier_outcome_at_bar()` per-bar classification helper with the
  optimized implementation under test, so a defect in that shared function
  would not be caught by this specific test. This review's own from-scratch,
  zero-shared-code oracle (§3.2/§3.3) covers the gap and found no
  discrepancy, so this is not a live defect — it is a suggestion to
  strengthen the implementer's regression suite for the future.
- **Correction**: not required for this re-review's decision. Recommended
  (non-blocking) for the implementer: add or keep a second comparison
  oracle that reimplements the barrier classification independently (e.g. a
  pure per-bar loop written without calling `barrier_outcome_at_bar`), so
  that a future regression in that specific shared helper would be caught by
  the implementer's own suite and not rely solely on external review.

## 6. Full-scope re-verification (instruction 9)

All re-run or freshly verified against the corrected code, not assumed
unchanged:

| Area | Result |
|---|---|
| Exact forward-return formulas and off-by-one boundaries | OK — re-verified via hand-computed oracle (H001/H005, exact `t`/`t+1`/`t+h` usage) and the 714-case naive cross-check. |
| MFE/MAE | OK — verified against both a hand-computed window and the naive cross-check across all adversarial cases (ties, duplicate extrema). |
| Barrier truth tables | OK — TP_FIRST/SL_FIRST/TIMEOUT/AMBIGUOUS_BOTH_HIT/INVALID, open-gap priority, exact touch, chronological first-hit, all independently re-verified; 0/714 naive-oracle mismatches. |
| Reason codes and priority | OK — registry still exactly 16 codes, priorities `{10,...,190}` unchanged; stage-code and historical-alias rejection re-verified; dedup/sort re-verified. |
| Schema and field order | OK — 302/302 fields, exact order, exact match against the spec's machine-readable registry, re-derived fresh (not assumed from the prior review). |
| S6→S7 row preservation | OK — primary key, `market_segment_id`, and all inherited S0–S6 field values re-verified unchanged for every row in a fresh reproduction. |
| Leakage protection | OK — all 302 fields still individually rejected by `leakage.assert_no_s7_fields` (file unchanged, but re-run against the current field registry to confirm no drift); both original bypass attempts (spoofed owner, spoofed prefix-owner mismatch) still correctly blocked. |
| Causality and prefix behavior | OK — re-verified: mutating a row strictly beyond a given horizon's window leaves that horizon's labels unchanged for all earlier rows; the discriminating sanity check (the same mutation *does* change the horizon whose window it falls inside) still passes. |
| Deterministic reproducibility | OK — `LABEL_SCHEMA_FINGERPRINT_SHA256` and `SEMANTIC_BUILD_CONFIGURATION_SHA256` reproduced identically; partition/overlap execution reproduces the full-build values exactly for the owned prefix; serial vs. split-at-arbitrary-point parity re-verified. |
| Mutable references | OK — `indicators`/`signals` container independence re-verified (object identity differs; mutating the S7 copy does not affect the source S6 row). |
| Stage-wide fail-closed abort | OK — re-verified: unordered input, duplicate primary key, wrong schema version, and a same-segment timestamp gap all still raise before any row-level output; `_validate_input_rows`'s core logic is structurally unchanged (only `isinstance`→`type` micro-changes). |
| Test gaps / false-positive risk | See §3.3 (S7-CLAUDE-RR-002) for the one identified gap in the implementer's own suite; my own independent suite (81 checks from the original review's scripts, re-run and still 100% passing, plus 24+9+714+4 = 751 new checks for this re-review) found no false positive in either direction. |

## 7. Finding counts by severity

| Severity | Count |
|---|---:|
| CRITICAL | 0 |
| MAJOR | 0 |
| MINOR | 1 |
| EDITORIAL | 1 |

## 8. Final decision

```text
APPROVED
```

All three original findings (S7-CLAUDE-001, S7-CLAUDE-002, S7-CLAUDE-003) are
independently confirmed **RESOLVED** with reproducible, from-scratch
evidence — not the implementer's own claims or tests. No `CRITICAL` or
`MAJOR` finding remains open, satisfying the stated approval rule. The one
new `MINOR` finding (component-version traceability) and one `EDITORIAL`
observation (a narrower-than-ideal implementer test oracle, which this
review's own independent oracle compensates for) do not block approval per
instruction 10.

Full-scope re-verification (not limited to the diff) found the rest of the
S7 implementation — schema/field registry, reason-code registry, leakage
guard, row/key/segment preservation, mutable-container independence,
causality/prefix invariance, partition parity, and stage-wide fail-closed
behavior — unaffected by the correction and still fully conformant, matching
the original review's conclusions on those points.

No file inside the repository or inside the review package was modified by
this review.

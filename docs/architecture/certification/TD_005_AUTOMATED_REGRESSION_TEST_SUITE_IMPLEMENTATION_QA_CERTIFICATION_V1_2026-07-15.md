Document Class:
Implementation QA Certification

Document ID:
TD005-IMP-QA

Title:
TD-005 Automated Regression Test Suite - Implementation QA Certification

Version:
V1.0

Date:
2026-07-15

Status:
FINAL QA CERTIFICATION REVIEW

Storage Location:
docs/architecture/certification/

Filename:
TD_005_AUTOMATED_REGRESSION_TEST_SUITE_IMPLEMENTATION_QA_CERTIFICATION_V1_2026-07-15.md

Technical Debt Item:
TD-005 - Automated Regression Test Suite (docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md)

Review Scope:
tests/regression/
docs/architecture/implementation/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_IMPLEMENTATION_REPORT_V1_2026-07-15.md

Accepted Working Baselines:
docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md, Version V1.1
docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-14.md, Version V1.1
docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_CAPABILITY_GAP_ANALYSIS_V1_2026-07-14.md, Version V1.1
docs/architecture/design/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_ARCHITECTURE_V1_2026-07-14.md, Version V1.1
docs/architecture/specifications/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_SPECIFICATION_V1_2026-07-14.md, Version V1.1
docs/architecture/implementation/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_IMPLEMENTATION_SPECIFICATION_V1_2026-07-14.md, Version V1.1

Language:
English

Encoding:
ASCII

---

# TD-005 Automated Regression Test Suite - Implementation QA Certification

## 1. Metadata

See front matter above. This certification was performed independently of, and without trusting, the TD-005 Implementation Report or the existing test suite's own passing status as evidence of correctness. Every claim below was re-derived from direct repository inspection, fresh test execution, standalone verification scripts, and mutation-style fault injection performed during this review and fully reverted before completion.

**Correction pass (same V1.0, no version bump).** Following initial issuance of this document with result `CERTIFIED WITH MINOR CORRECTIONS` alongside an *uncorrected* Low finding (F-01), a governance-directed follow-up review re-evaluated F-01 against `tests/regression/orchestrator.py`, `tests/regression/coverage.py`, `tests/regression/classification.py`, and the accepted Specification/Implementation Specification, determined it to be a genuine implementation defect (Option A: correct, not Option B: reclassify), and corrected `orchestrator.py` accordingly. Four tests in `tests/regression/test_orchestration.py` and one in `tests/regression/test_regression_scenarios.py` were added to prove the corrected behaviour; four existing tests in `test_orchestration.py` were updated to establish coverage as an explicit precondition, mirroring the suite's own existing pattern for the Reference Baseline precondition. This revision also completed the Section 3 audit discipline this same governance follow-up required: F-03 and F-04, on re-examination, were confirmed to require no code correction and are reclassified from Low to Informational accordingly (Section 14). All sections below reflect the corrected implementation and the completed audit; no contradiction remains between findings, correction status, remaining risks, and the certification result.

## 2. Review Scope

In scope: every file under `tests/regression/` (17 realization/package modules, 12 test modules), and the Implementation Report. Reviewed against all six accepted Working Baselines listed above, independently re-read in full during this review (not assumed from any prior session or document summary).

Out of scope: redesigning any accepted baseline; modifying `run_engine/`; modifying `requirements.txt`; modifying FRA/SDA/CGA/Architecture/Specification/Implementation Specification; staging, committing, or pushing.

## 3. Repository State

Confirmed at the start of this review:

- Branch: `run-engine-consolidation-safety`
- HEAD: `8952b1cba42506e4126e57ee89c59934f3d48b71`
- `git status --short`:
  - `M docs/capabilities/SGF_013_SCIENTIFIC_BEHAVIOUR_REPRESENTATION_2026-06-26.md` (pre-existing, unrelated)
  - `?? docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_CAPABILITY_GAP_ANALYSIS_V1_2026-07-14.md`
  - `?? docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-14.md`
  - `?? docs/architecture/analysis/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-14.md`
  - `?? docs/architecture/design/`
  - `?? docs/architecture/implementation/`
  - `?? docs/architecture/specifications/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_SPECIFICATION_V1_2026-07-14.md`
  - `?? tests/`
- `git diff --stat -- run_engine/`: empty. Confirmed independently at the start and end of this review: **zero `run_engine/` files were modified by TD-005 at any point**, including during this QA pass (mutation-style verification in Section 13 touched files under `tests/regression/` only, each reverted immediately).
- `git diff --stat -- requirements.txt`: empty. Unchanged.
- SGF-013 working-tree modification: present, unchanged, untouched by this review (single `M` entry, identical scope throughout).

## 4. Independent Review Method

No claim in the Implementation Report or in the existing test suite's own passing status was accepted without independent re-verification:

1. All six accepted baseline documents (FRA, SDA, CGA, Architecture, Specification, Implementation Specification) were re-read in full during this review.
2. All 29 Python files under `tests/regression/` were re-read in full, fresh, line by line.
3. `run_engine/core/loop.py`, `run_engine/main.py`, `run_engine/core/strategy.py`, and `run_engine/core/trade_lifecycle.py` were independently re-read to verify claims the test suite and Implementation Report make about active Run Engine behaviour, rather than trusting those claims.
4. Four standalone, review-only Python scripts (never committed; see Section 17) independently re-executed determinism, comparison, evidence, persistence, scope-derivation, and LDV-contract-identity properties outside of the existing test suite.
5. Seven categories of mutation-style fault injection were applied directly to `tests/regression/` source files, each verified to be caught by the existing suite, then fully reverted (Section 13).
6. `python -m compileall`, `python -m unittest discover`, `git diff --check`, and `git status --short` were re-run multiple times throughout the review, not only at the end.

## 5. Code Quality Review

All 17 realization/package modules were read in full: `__init__.py`, `vocabulary.py`, `corpus.py`, `certification_boundary.py`, `scope.py`, `environment_identity.py`, `replay.py`, `observation.py`, `reference_baseline.py`, `comparison.py`, `classification.py`, `evidence.py`, `coverage.py`, `orchestrator.py`, `ldv_integration.py`, `governance.py`, `registry.py`.

**Correctness.** Every realization module's own behaviour was cross-checked against its own owning Implementation Unit's Purpose/Responsibility/Required-and-Forbidden-interactions text (Implementation Specification Section 7). No module was found to realize behaviour beyond its own owning unit (TD005-II-002), and no module was found to omit required behaviour, following the F-01 correction described below (Section 14).

**Determinism.** `replay.py`'s `ReplaySession.run()` drives `RunLoop()` (fresh-constructed, no injected state) through `.step()` only; no randomness, wall-clock branching, or network access anywhere in `tests/regression/` (confirmed by full-text read and by the independent AST-based static scan in Section 7, item 11).

**Ownership.** Data ownership transfer is single-directional and matches Implementation Specification Section 9 ("Ownership transfer"): `ReplaySession` owns a captured trajectory until `NonInterferenceObserver` exposes it as `ObservedSnapshot`s; `RegressionClassifier` owns a `ClassificationRecord` until `EvidenceComposer` composes evidence for it; `EvidenceComposer` owns a `Composed` record until `EvidencePersistence` persists it. No module reaches into another module's own internal state.

**Architecture/Specification compliance.** See Section 9 (Baseline Conformance).

**Hidden coupling (F-01, corrected).** One genuine, load-bearing hidden coupling was found in the reviewed implementation: `RegressionPipelineOrchestrator.invoke()` called `self.contract_coverage.record_contract_exercised(evaluated_contract_id)` immediately before `self.contract_coverage.compute()`, which meant the coverage-confidence signal `classification.py` consumes was always self-satisfied for the contract currently being evaluated - the "low coverage confidence" trigger of the Indeterminate outcome (TD005-ID-009 Step 2) could never actually fire through the full pipeline, only through direct unit-level calls to `RegressionClassifier.classify()`. This was independently confirmed via direct instrumentation and via mutation testing that showed reordering coverage-recording to genuinely precede classification flipped four existing tests from Non-Regression to Indeterminate - proof that those tests' own passing status depended on this self-recording pattern, not on genuine prior coverage.

Determined to be a genuine implementation defect (Section 10, F-01 Re-evaluation) and corrected: `contract_coverage.compute()` now runs, and its result is consumed by `classifier.classify()`, strictly before `contract_coverage.record_contract_exercised()` records this invocation's own exercise. Coverage-confidence therefore reflects only what a prior invocation (or explicit pre-registration) already established, never a record this same invocation manufactures for itself. Recording moves to after Classification has already reached its outcome, so it can only ever benefit future invocations, never alter the one just completed (TD005-AI-014, TD005-SI-015). Four new tests in `test_orchestration.py::TestCoverageConfidenceSequencing` and one new test in `test_regression_scenarios.py::TestClassificationOutcomesIntegration` independently prove: a certified contract with no prior recorded coverage yields Indeterminate on first evaluation; a second evaluation of the same contract, now covered, yields a determinate outcome; coverage recorded after classification never alters the already-returned classification object; and the two distinct Indeterminate causes (uncertified contract vs. certified-but-uncovered) produce distinct, non-generic reasoned-unavailability-marker text (TD005-II-014).

**Replay isolation.** `NonInterferenceObserver.observe()` deep-copies (`copy.deepcopy`) every raw per-tick dict at the observation boundary; independently confirmed (Section 7, item and `test_snapshot_is_independent_deep_copy`) that mutating an exposed `ObservedSnapshot` never corrupts the session's own underlying trajectory nor a second, independent observation of the same session.

**Evidence generation, coverage logic, persistence, orchestration, state isolation, module discovery, failure handling, restart handling, cleanup handling.** Each independently verified; see Section 7 (Runtime Verification) and Section 13 (Mutation-Style Verification) for the specific evidence. No dead code, no unreachable branch, and no duplicated logic beyond the two deliberate, disclosed, non-duplicative "direct certified-class" test paths (Section 8) were found. Two evidence-content precision observations (F-03, F-04) are reported in Section 14, both confirmed on re-examination to require no code correction and reclassified Informational; neither is a functional defect.

**Implementation leakage.** None found: no test-only helper leaks into a realization module's own public surface; `simulate_interruption` (evidence.py) and `partition_provider` (scope.py) are the only test-oriented seams, both explicitly documented as such in their own docstrings, both defaulting to the real production behaviour, and both independently confirmed not to weaken any invariant when unused (Section 7, items 9 and 11).

**Static hygiene.** Five unused imports were found and corrected during this review (Finding F-02, Section 14): `comparison.py` (`Dict`, `Enum`), `evidence.py` (`Optional`), `reference_baseline.py` (`Dict`, `Any`), `test_regression_scenarios.py` (`ObservableSurfaceClassifier`). No bare `except:`, no mutable default arguments, and three `except Exception` clauses, each individually reviewed and found justified: `evidence.py:173` (temp-file cleanup before re-raising, inside the atomic-persist try block), `orchestrator.py:82` (boundary translation into `PreconditionNotMetError`), `replay.py:140` (explicitly documented: an unhandled condition is itself the session's own Failed trigger, per TD005-SO-004's own Required behaviour).

## 6. Test Quality Review

All 165 originally-reviewed tests, plus the five tests added by the F-01 correction (170 total across 12 test modules), were individually read and assessed against the nine criteria in Section 4 of the governing task.

**General finding.** No test was found to be tautological, to compare a mutable object against itself, or to validate a constant produced by the same module under test in a way that would pass regardless of a real defect. Every test's assertions were confirmed to target either (a) a `run_engine`-derived value (via `ReplaySession`/direct certified-class instantiation) or (b) a `tests/regression/`-internal state transition explicitly named in its own owning Specification/Implementation Unit's state model - never an assertion whose only possible failure mode is a bug in the test itself.

**State isolation between runs.** Every test that persists evidence uses `tempfile.mkdtemp()` with a `tearDown()`-scoped `shutil.rmtree(..., ignore_errors=True)`; independently confirmed no test writes to the shared production `tests/regression/data/evidence/` path (that directory does not exist in the repository at rest; confirmed via `find` in Section 12).

**Specific quality findings:**

- `test_evidence.py::test_identical_environment_matches_itself` - a slightly misleading name (it compares two *distinct* captures for equivalence, not a capture against itself); the assertion itself is correct and meaningful. Informational only, not corrected (a docstring/name-only nit with zero functional or evidentiary impact).
- `test_classification.py` directly exercises `coverage_confident=False` as a keyword argument to `RegressionClassifier.classify()`, correctly proving the classifier's own logic branch is right in isolation. Prior to the F-01 correction this path was reachable only at the unit level, not end-to-end; following the correction, `test_orchestration.py::TestCoverageConfidenceSequencing` now independently proves the same property end-to-end through the full orchestrator, so the unit test's own name no longer overstates what is reachable in integration.
- `test_orchestration.py`'s `TestOrchestrator` and `TestCoverageConfidenceSequencing` classes, together with `test_regression_scenarios.py`'s `TestClassificationOutcomesIntegration` class, now give genuine full-pipeline, non-tautological evidence for all four classification outcomes, including both of Indeterminate's distinct triggers (uncertified contract, and certified-but-not-yet-covered contract). The previously-missing negative/boundary case (Indeterminate-via-low-coverage-confidence, end-to-end) is now covered.
- No duplicated tests were found (each test targets a distinct behavioural property, even where two tests share the same fixture pattern).
- No test name was found to overstate what it actually proves, with the one qualified exception above (informational).
- Every test that claims to reach a specific runtime path was independently confirmed to actually do so: for example, `test_regression_scenarios.py::test_four_previously_uncovered_active_modules_now_exercised` was checked against `run_engine/main.py` and `run_engine/core/regime.py` directly (Section 9) to confirm a `ReplaySession` reaching `Captured` genuinely cannot avoid importing and executing all four previously-uncovered modules.
- Weak-assertion risk: `test_evidence.py::test_persisted_record_never_modified_in_place` asserts only that two successive loads of the same file are equal (`before == after`), which does not itself prove immutability against an external actor, only against this suite's own read path. This is accurate to what the test's own name implies ("never modified in place" - by this suite) and is complemented by the stronger, independent proof in `test_interrupted_persist_leaves_record_unpersisted_not_altered` and by this review's own Section 7 (item 8) atomic-persistence checks. Not a defect; noted as a precision observation only.

**Missing negative/boundary tests identified:**

- The coverage-driven Indeterminate path is now exercised end-to-end (F-01 correction, above); no longer a gap.
- No test in `tests/regression/` exercises a `ReplaySession` whose `bounded_duration_seconds` is exceeded mid-sequence by a genuinely slow tick (the existing `test_bounded_duration_exceeded_reaches_failed` uses `bounded_duration_seconds=0.0`, which times out immediately on the first tick rather than mid-sequence). This is a minor boundary-case gap; the underlying `time.monotonic()` check itself was independently re-confirmed correct by direct code inspection (Section 5) and is not itself in question - only the specific "exceeded partway through a long sequence" boundary is untested. Informational (F-08).

## 7. Runtime Verification

Performed independently, outside the existing test suite, using four standalone scripts (removed after this review; see Section 17). All checks below were executed fresh during this review with real, not simulated, `RunLoop` execution unless stated otherwise.

1. Two independent `ReplaySession` instances, 500 ticks each (`tick % 137 - tick % 53` price stream): both reached `Captured`; `TrajectoryComparator` reported `equivalent: True`, zero differences. **PASS.**
2. A third, independent 500-tick instance compared against the first: also `equivalent: True`. Repeated-run determinism confirmed beyond the minimum two-instance requirement. **PASS.**
3. Object-identity independence: `ObjectIdentityIndependentComparator.structurally_equal()` confirmed `True` for two structurally-equal, non-identical objects and `False` for structurally-different ones. **PASS.**
4. Exact categorical comparison: case-sensitive exact match confirmed for `event_type`. **PASS.**
5. Numeric tolerance boundary behaviour, `ABSOLUTE_TOLERANCE = 1e-6`, `RELATIVE_TOLERANCE = 1e-9`:
   - Below absolute tolerance: equal. **PASS.**
   - Exactly at absolute tolerance (`diff == ABSOLUTE_TOLERANCE`): equal (`<=`, inclusive boundary). **PASS.**
   - Above both bounds at the tested magnitude: not equal. **PASS.**
   - Negative values, within/outside tolerance: both correctly handled, symmetric with the positive case. **PASS.**
   - Zero: `0.0` vs `0.0` equal; `0.0` vs a value exceeding the absolute bound (relative bound degenerates to `0` at magnitude zero) not equal. **PASS.**
   - Large values (`1e9`): relative tolerance correctly dominates; a diff of exactly `RELATIVE_TOLERANCE * value` sits at the inclusive boundary and passes, confirming the "whichever bound is looser" combined policy (TD005-ID-008) operates as designed, not as a defect. **PASS.**
   - Symmetric application under operand swap: confirmed identical verdict forward and backward (TD005-II-007). **PASS.**
   - Uncategorized field: raises `UncategorizedFieldError`, never silently compared. **PASS.**
6. Failure-to-Invalid-Comparison routing: a candidate `ReplaySession` failing to reach `Captured` (empty tick sequence) was independently driven through a fresh `RegressionPipelineOrchestrator`; classification outcome was `Invalid Comparison`, with a persisted evidence record. **PASS.**
7. **Coverage-confidence reachability (originally a finding, now a corrected-behaviour check):** instrumentation of `ContractRequirementCoverage.compute()` originally showed `evaluated_contract_id` unconditionally absent from `uncovered_contracts` immediately after `invoke()`'s own coverage-recording step - the basis for Finding F-01. Following the correction, the same instrumentation confirms `compute()` now runs, and its result is consumed, strictly before `record_contract_exercised()` is called for the current invocation; a contract genuinely absent from all prior recording correctly remains in `uncovered_contracts` at the point `classify()` consumes it. **PASS** (post-correction).
8. Evidence completeness: the persisted Invalid-Comparison evidence record (item 6) contained all eight required elements; five of eight carried a reasoned unavailability marker (`actual_value`, `affected_stage_or_component`, `affected_tick`, `execution_environment_identity`, `expected_value`), each with a distinct, non-generic, non-empty reason string naming its own specific upstream cause. **PASS.** The remaining three (`certified_contract_id`, `initial_state_provenance`, `input_provenance`) carried determinate values; `certified_contract_id`'s determinate value is examined further in Finding F-04.
9. Reasoned-unavailability markers for both Indeterminate causes: `certified_contract_id` for an uncertified-contract case reads "certification boundary does not recognize this contract as certified"; for a certified-but-not-yet-covered case it reads "contract is certified but has no prior established coverage recorded by this suite" - two distinct, cause-specific reasons (`_indeterminate_contract_id_reason()`, added as part of the F-01 correction), never one generic marker text shared across both conditions. **PASS.**
10. Atomic persistence interruption: `EvidencePersistence.persist(record, simulate_interruption=True)` raised `InterruptedPersistError`; the record was confirmed absent from `is_persisted()`; zero files (including zero leftover `.tmp-*` files) remained in the evidence directory afterward. **PASS.**
11. Restart after interrupted persistence: a fresh `persist()` call (no `simulate_interruption`) on the same record succeeded, and loaded content matched the composed record exactly. **PASS.**
12. Reference immutability: `ReferenceBaselineRecord` (frozen dataclass) rejected direct field mutation; `ReferenceBaselineAuthority.revise()` was confirmed to produce a distinct record object, leaving the prior record's own trajectory length unaffected. **PASS.**
13. Environment-identity freshness: two `capture()` calls with different `session_id` values produced distinct record objects with distinct `session_id`s and matching library versions (same interpreter). **PASS.**
14. Active/inactive module derivation: `scope.py` contains zero `__import__`/`exec`/`eval`/`import_module` calls (static AST scan of `scope.py`'s own source); `derive_scope_partition()` was confirmed, via a `sys.modules` before/after diff, to import **zero** `run_engine` modules as a side effect of computing the partition - it is genuinely static-analysis-only (TD005-II-008). Active count 14, inactive count 4, reproducible across repeated calls. **PASS.**
15. No direct runtime-state reads outside the observation boundary: an independent AST scan of every non-test file under `tests/regression/` confirmed that **only** `replay.py` imports anything from `run_engine`; no other realization module (including `observation.py` itself, which consumes only the already-returned dict) imports `run_engine` directly. **PASS** (confirms TD005-II-004/TD005-II-011 by construction, not merely by docstring claim).
16. Long-Duration-Validation invocation-contract identity: all six LDV stages produced a result; `contract_is_identical_across_stages()` returned `True`; the six captured `InvocationContract` instances were confirmed structurally equal to each other independently of the suite's own assertion helper. **PASS.**
17. Executor namespace non-duplication: exactly one `run_engine/core/execution/executor.py` path present in the active closure; `governance.py` was confirmed to contain an explicit disclaimer text disowning any Executor-namespace-uniqueness responsibility. **PASS.**

## 8. Lifecycle Verification

Independently verified, both via full-pipeline `ReplaySession` execution and via direct instantiation of the certified `TradeLifecycleEngine`, `PnLEngine`, `RiskEngine`, and `PerformanceEngine` classes (never a parallel Run Engine; confirmed by AST scan in Section 7, item 15, that these test modules import only the real, active classes and never construct or wrap a `RunLoop` of their own for this purpose).

| Scenario | Full-pipeline evidence | Direct-class evidence | Both required? | Sufficient? |
|---|---|---|---|---|
| Open | Yes (`test_trade_opened_occurs_on_first_tick`) | Yes (`test_open_scale_in_partial_close_full_close_sequence`) | No - full-pipeline alone suffices for TD005-FR-007 | Yes |
| Scale-In (first) | Yes (naturally reached) | Yes | No | Yes |
| Scale-In (repeated) | Yes (`trending_tick_sequence`) | Yes | No | Yes |
| Partial Close | No - empirically unreachable via `ReplaySession` under default `StrategySelector` parameters (see Section 10) | Yes | Yes, in this specific case, since full-pipeline cannot reach it | Yes, direct-class is the only available and sufficient evidence |
| Full Close | No - same reason | Yes | Yes | Yes |
| Runtime Failure Event | No - see Section 10 | Yes (three distinct triggers independently re-verified against `trade_lifecycle.py`, Section 6) | Yes | Yes |
| PnL (realized) | Indirect only (embedded in tick output, never isolated) | Yes, explicit (`test_pnl_realized_on_full_close_long/short`) | Direct-class needed for isolated verification | Yes |
| Equity / peak equity | Indirect only | Yes, explicit | Direct-class needed | Yes |
| Drawdown | Indirect only | Yes, explicit | Direct-class needed | Yes |
| Risk | Indirect only | Yes, explicit, including AC-003 configuration-independence | Direct-class needed | Yes |
| Performance | Indirect only | Yes, explicit, including AC-008 gating and LONG/SHORT keying | Direct-class needed | Yes |
| Executor status | Yes (`BUY_EXECUTED`, `NOOP` both observed) | Not separately needed | No | Yes |
| Lifecycle ordering | Yes (`test_lifecycle_event_ordering_open_precedes_scale_in_for_same_trade`) | Yes (sequence test) | No | Yes |

**Confirmation that direct-class tests are legitimate:** independently re-read `run_engine/core/trade_lifecycle.py` in full (Section 6) and confirmed every direct-class assertion in `test_regression_scenarios.py` (`TestLifecycleTransitionsDirect`, `TestFinancialAndRiskAndPerformance`) matches the actual, active, certified implementation exactly - `_handle_buy`/`_handle_sell` dispatch to `_open_trade` when no active trade exists (confirming the test's own comment that "SELL with no active trade legitimately opens a SHORT" is correct, not a workaround); `_validate_execution_quantity` requires `quantity > 1e-9` (confirming the `INVALID_EXECUTION_QUANTITY` trigger); `_close_trade`'s `trade.quantity + QUANTITY_EPSILON < quantity` check confirms the `OVER_CLOSE_QUANTITY` trigger; closed trades remain in `self.trades` with `status="CLOSED"` and are never targeted by a subsequent `active_trade`-scoped mutation, confirming AC-004 immutability. These tests instantiate `TradeLifecycleEngine()`, `PnLEngine()`, `RiskEngine()`, `PerformanceEngine()` directly - the same classes `RunLoop.__init__()` itself constructs - as ordinary, non-invasive unit tests. No alternative Run Engine is created; no live `RunLoop` state is read outside `NonInterferenceObserver`'s own boundary in any of these tests (confirmed by the same AST import-scan in Section 7, item 15, which found these test files import from `run_engine.core.*` directly but never from `run_engine.core.loop`). No test in this class makes a claim stronger than what it demonstrates.

## 9. Baseline Conformance

**Implementation Units (23 of 23).** Individually cross-referenced against Section 2.1 of the Implementation Report and independently re-verified against this review's own fresh reading (Section 5/7/8): every `TD005-IU-001` through `TD005-IU-023` is realized by exactly the module claimed, with a docstring citation in that module naming its own Traceability. No orphan Implementation Unit, no module realizing more than its own owning unit (TD005-IU-005 is the sole, correctly-justified aggregate). TD005-IU-005's own Coverage-informs-Classification sequencing point (previously flagged as F-01) is now corrected and independently re-verified (Section 7 item 7, Section 13). **Conforms.**

**Implementation Invariants (18 of 18).** Each individually spot-verified against its own stated enforcement point (Implementation Report Section 4.2), not accepted on the Report's own claim alone:

| Invariant | Independent verification performed | Result |
|---|---|---|
| TD005-II-001 | Every module docstring cites Traceability (read in full) | Confirmed |
| TD005-II-002 | Each module's own scope matches its owning Specification Object | Confirmed |
| TD005-II-003 | `orchestrator.py`'s fixed call sequence read in full; Mutation G confirmed reordering is detectable | Confirmed |
| TD005-II-004 | AST scan: only `replay.py` imports `run_engine` (Section 7, item 15) | Confirmed |
| TD005-II-005 | `ControlledConditionManifest.validate()` rejects non-default state; `ReplaySession` imports `RunLoop` locally, calls `.step()` only | Confirmed |
| TD005-II-006 | `EvidenceRecord` composed once; `record_id` fresh per `compose()` call (`uuid4()`) | Confirmed |
| TD005-II-007 | Symmetric tolerance independently re-tested (Section 7, item 5) | Confirmed |
| TD005-II-008 | `sys.modules` diff proves zero dynamic import (Section 7, item 14) | Confirmed |
| TD005-II-009 | LDV contract structural-equality independently re-tested (Section 7, item 16) | Confirmed |
| TD005-II-010 | `hasattr` absence tests read; confirmed no such attribute exists on `ClassificationRecord` | Confirmed |
| TD005-II-011 | Same AST scan as II-004; only `NonInterferenceObserver` reads the raw trajectory | Confirmed |
| TD005-II-012 | `registry.py`'s `RESOLVED`/`STILL_OPEN` read in full; all nine resolved mechanisms individually cross-checked against their own owning module | Confirmed |
| TD005-II-013 | `governance.py`'s exclusion statement read; scope.py confirmed to perform no namespace-collision check | Confirmed |
| TD005-II-014 | `UnavailabilityMarker.__post_init__` re-tested via mutation (bypassing it independently, Section 6) and via Section 7 item 8/9 | Confirmed |
| TD005-II-015 | Neither coverage class exposes a classification-altering method (confirmed by reading the full class body, not only the `hasattr` test) | Confirmed |
| TD005-II-016 | `EVIDENCE_DIR` confirmed under `tests/regression/data/evidence/`, within the repository boundary | Confirmed |
| TD005-II-017 | Bounded-duration check read; independently re-tested (existing test only covers the immediate-timeout case, Section 6 boundary-test gap noted) | Confirmed, with a minor boundary-test coverage gap noted (Section 6) |
| TD005-II-018 | `EVIDENCE_DIR` matches TD005-ID-014's designated location exactly | Confirmed |

**Implementation Decisions (15 of 15).** Each read in full against its own realization; all fifteen `TD005-ID-001` through `TD005-ID-015` are faithfully realized at the code level, with nine further code-level mechanism decisions correctly registered in `registry.py` and two correctly left open (Section 11). **Conforms.**

**Specification Objects, Invariants, Decisions (22 SO / 22 SI / 4 SD).** Verified via the unbroken, individually-listed 1:1 traceability chain (Implementation Specification Section 15.1: every `TD005-SO-xxx` maps to exactly one `TD005-IU-xxx`, itself independently re-verified realized in Section 5/9 above) rather than re-deriving all 22+22+4 items from first principles, since this Specification was itself independently Editorial-Reviewed and Final-QA-Certified in a prior governance stage and this review's own mandate is Stage 7 (Implementation) conformance. Spot-checked in depth: TD005-SO-004 (Replay), TD005-SO-007 (Observation), TD005-SO-013 (Classification), TD005-SO-016/017 (Evidence), TD005-SO-021 (Scope) - all confirmed faithfully realized by direct code reading, including TD005-SO-013's own four-outcome exhaustiveness now genuinely reachable end-to-end for all four outcomes. **Conforms.**

**Architecture Components, Decisions, Invariants (22 ARC / 13 AD / 19 AI).** Verified via the unbroken Architecture-Component-to-Implementation-Unit chain (Implementation Specification Section 15.4), independently reconciled against a fresh subagent-assisted extraction of the Architecture document performed during this review. No orphan Architecture Component; every Architecture Invariant traced to at least one Implementation Invariant above. **Conforms.**

**FRA (22 FR / 4 CON / 2 Deferred Obligations / 6 OQ), SDA (33 DEP), CGA (22 CAP).** These were independently re-extracted in full during this review (not assumed from any prior session). All 22 Functional Requirements trace through the Specification's own Section 19.1 table to a Specification Object, itself traced to an Implementation Unit confirmed realized above; all four Constraints (non-interference, no-alternative-execution-path, repository-scope, deterministic-execution) were independently re-verified at the code level in Section 5/7 (items 14, 15) rather than accepted from the traceability table alone. The two Deferred Obligations (Active Module Coverage, Executor Namespace) are independently confirmed satisfied: module coverage via Section 7 item 14 (14 active modules confirmed) and Section 8's four-previously-uncovered-modules check; Executor namespace via Section 7 item 17. All six Open Questions (OQ-001 through OQ-006) are confirmed resolved or correctly deferred at the Implementation Specification level (OQ-001 boundary = `RunLoop.step()`'s return value, independently confirmed as the sole read path in Section 7 item 15; OQ-002 = freshly-established baseline, confirmed in `reference_baseline.py`; OQ-003 = RETAIN-Deferred-Scope modules confirmed out of scope; OQ-004 = execution-time budget explicitly left open, confirmed in `registry.py`'s `STILL_OPEN`; OQ-005 = `tests/regression/`, confirmed as the actual location; OQ-006 = the four-outcome classification model, confirmed realized in `classification.py`). **Conforms**, no gap found at this level.

## 10. Deviation Assessment

**A. ControlledConditionManifest limitation.** Independently re-verified directly against `run_engine/core/loop.py` (read in full, Section 6): `RunLoop.__init__(self)` takes zero parameters and unconditionally constructs fresh `StateEngine`/`RegimeClassifier`/`StrategySelector`/`PositionEngine`/`TradeLifecycleEngine`/`RiskEngine`/`Executor`/`PnLEngine`/`PerformanceEngine` instances - confirmed, no injection point exists for a non-default initial Position, lifecycle history, regime/strategy state, or configuration. Additionally, and beyond what the Implementation Report itself checks, this review independently read `run_engine/main.py` and confirmed that **production's own entry point also constructs `RunLoop()` fresh with no injected state** - meaning this is not a limitation the test suite introduces relative to what the active, certified system can actually do; it is an exact match to the active Run Engine's own real capability. `ControlledConditionManifest.validate()` correctly fails closed (`UnsupportedManifestError` -> session `Failed`) rather than silently ignoring an unsupported request. No accepted baseline (FRA/SDA/CGA/Architecture/Specification/Implementation Specification) requires these four fields to be genuinely settable today; TD005-ID-005 only requires them to be named explicitly, which they are.

**Determination: Acceptable implementation constraint.** Not an unresolved implementation gap (nothing in TD-005's own scope permits modifying `run_engine/` to add an injection point, and none of the 22 Functional Requirements requires varying initial Position/lifecycle history/regime state across runs). Not a baseline deviation requiring governance escalation.

**B. Direct lifecycle-class testing.** Independently re-derived (not trusted from the Implementation Report) the empirical claim underlying this deviation, directly from `run_engine/core/strategy.py` (read in full, Section 6): with `self.weights` never mutated by `RunLoop.step()` (no call to `StrategySelector.update()` exists anywhere in `loop.py`), the worst-case regime for a LONG position to flip to SELL is `TREND_DOWN` (`_regime_bias` = `{"BUY": 0.7, "SELL": 1.3, "HOLD": 1.0}`). With `current_pos == "LONG"` dampening `BUY` by `x0.01`, the normalized scores are approximately `BUY ~= 0.00303`, `SELL ~= 0.5635`, `HOLD ~= 0.4335`. Since `0.5635 < 0.60` (`decide()`'s own switch-confirmation threshold), `decide()` always reverts to `last_action = "BUY"`. This independently reconfirms, via fresh manual derivation from the actual source in this review, that a LONG position can never naturally flip to SELL under the active `StrategySelector`'s own default parameters, and therefore that Scale-In-beyond-first, Partial Close, Full Close, and most Runtime Failure Event triggers are genuinely unreachable through `ReplaySession` alone.

Per Section 8 (Lifecycle Verification), the following accepted requirements are assessed by evidence tier:

- Requiring **unit-level evidence only** (full-pipeline is not attainable and not required by any FR): Partial Close (TD005-FR-008), Full Close (TD005-FR-009), Runtime Failure Handling (TD005-FR-017, for triggers other than the initial `NO_ACTIVE_TRADE` case not exercised by any tick sequence), PnL reproducibility (TD005-FR-011), PnL/equity/drawdown consistency (TD005-FR-012), Risk determinism (TD005-FR-013), Performance gating and keying (TD005-FR-014, TD005-FR-015).
- Requiring **full-pipeline evidence only**: Deterministic Execution Ordering (TD005-FR-001), Repeated-Run Determinism (TD005-FR-002), Tick-Complete Publication Integrity (TD005-FR-003), Canonical Ownership (TD005-FR-004), Snapshot Isolation (TD005-FR-005), Information Flow (TD005-FR-006).
- Requiring **both**: Position Lifecycle State Machine Integrity (TD005-FR-007, Open+Scale-In via full pipeline, Partial/Full Close via direct class), Executor Action-to-Status Mapping (TD005-FR-016, full-pipeline `BUY_EXECUTED`/`NOOP` observed; direct-class not separately required since Executor is exercised identically either way).

**Determination: Sufficient for TD-005 as currently scoped**, with every mandatory scenario this review could identify from the accepted baselines backed by at least one non-tautological test at the appropriate tier, and no scenario found to require full-pipeline evidence that the suite only provides at the unit level, or vice versa.

## 11. Mechanism Decision Assessment

| Decision | Baseline-compatible | Deterministic | Scientifically justified | Documented | Tested |
|---|---|---|---|---|---|
| ControlledConditionManifest representation | Yes | Yes | Yes (Section 10) | Yes (docstring + registry.py) | Yes |
| Execution-environment identity representation | Yes | Yes (values, not identity) | Yes | Yes | Yes |
| Trajectory representation (ordered tick-indexed tuple) | Yes | Yes | Yes (TD005-ID-007) | Yes | Yes |
| `ABSOLUTE_TOLERANCE = 1e-6` | Yes | Yes | Yes - conservative relative to float64 precision, independently re-tested at the boundary (Section 7) | Yes | Yes |
| `RELATIVE_TOLERANCE = 1e-9` | Yes | Yes | Yes, same | Yes | Yes |
| JSON evidence persistence | Yes | Yes | Reasonable, standard-library-only choice, no external dependency added | Yes | Yes |
| Write-then-rename atomicity | Yes | Yes | Yes - `os.replace` is atomic on both POSIX and Windows; independently re-verified via Mutation D (Section 13.4) that weakening this ordering is caught | Yes | Yes |
| Evidence location (`tests/regression/data/evidence/`) | Yes (TD005-ID-014, within Repository Consolidation's Normative Boundary) | N/A | Yes | Yes | Yes (directory confirmed absent at rest, Section 12) |
| Indefinite evidence retention | Yes (no baseline names a policy) | N/A | Correctly left open, not invented | Yes (`registry.py` `STILL_OPEN`) | N/A - correctly untested since unimplemented |
| 300-second ReplaySession timeout | Yes | Yes | Conservative, documented rationale in `replay.py`'s own module comment | Yes | Yes, though only the immediate-timeout boundary is tested (Section 6) |
| Coverage model (module/state-transition/FR-citation, no aggregate %) | Yes | Yes | Yes (TD005-ID-010, matches Specification Section 13's explicit prohibition on a percentage metric) | Yes | Yes |
| Classification procedure (ordered four-step) | Yes | Yes | Yes (TD005-ID-009) | Yes | Yes, at both the unit level and end-to-end (F-01 correction closed the previously coverage-driven-branch gap) |
| `unittest` framework choice | Yes | Yes | Yes - independently re-confirmed `pytest` is not installed (`requirements.txt` re-read, Section 3) and no test framework appears anywhere in the dependency list | Yes | N/A |

**Arbitrary constants flagged:** none found to be unsupported by repository evidence. `ABSOLUTE_TOLERANCE`/`RELATIVE_TOLERANCE` and `DEFAULT_BOUNDED_DURATION_SECONDS` are each accompanied by an explicit, checkable rationale in their own module and were independently probed at their stated boundaries in Section 7 without finding an inconsistency.

**Portability risk:** `tempfile.mkstemp(dir=self._directory, ...)` followed by `os.replace()` is portable and correct on both POSIX and Windows (this review executed the entire suite, including the atomic-persistence tests, on Windows/Git Bash without incident). No platform-specific path-separator assumption was found; `scope.py` normalizes with `os.sep`/`"/"` consistently.

## 12. Static Validation

Executed fresh, multiple times during this review:

```
python -m compileall run_engine tests -q
```
Exit 0.

```
python -m unittest discover -s tests/regression -p "test_*.py"
```
Ran 165 tests, OK, at the initial issuance of this document. Following the F-01 correction (five tests added, four updated to establish coverage as an explicit precondition): ran 170 tests. OK (0 failures, 0 errors, 0 skipped).

```
git diff --check
```
Exit 2, confined entirely to `docs/capabilities/SGF_013_SCIENTIFIC_BEHAVIOUR_REPRESENTATION_2026-06-26.md` (10 pre-existing trailing-whitespace findings, unrelated to TD-005, unchanged by this review).

```
git status --short
```
Matches Section 3 exactly, with the expected addition of this certification document's own entry once created (`?? docs/architecture/certification/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_IMPLEMENTATION_QA_CERTIFICATION_V1_2026-07-15.md`), consistent with this governance chain's own established convention for a document that did not yet exist at the moment its own Section 3 evidence was captured. The F-01 correction pass modifies files inside the already-untracked `tests/` directory only and therefore adds no further `git status` entry.

**Additional inspections:**
- Unused imports: five found and corrected (F-02).
- Unreachable branches: none found beyond ordinary short-circuit guard clauses.
- Broad exception handling: three `except Exception` clauses, all individually reviewed and justified (Section 5).
- Swallowed exceptions: none - every caught exception either re-raises, translates into a suite-specific exception type, or (in `replay.py`) is the documented, required Failed-state trigger.
- Mutable default arguments: none found (`field(default_factory=...)` used correctly throughout for dataclasses).
- Path construction: `os.path.join`/`os.sep` used consistently; no hard-coded `/` or `\` path literal found outside of normalization logic in `scope.py` that explicitly converts to `/` for cross-platform comparison.
- Windows/WSL portability: the entire suite, including this review's own mutation testing, was executed on Windows/Git Bash throughout with zero portability failures.
- Temporary-file cleanup: confirmed via Section 7 item 10 (zero leftover `.tmp-*` files after an interrupted persist) and via every test's own `tearDown()` (`shutil.rmtree(..., ignore_errors=True)`).
- Filesystem race conditions: `os.replace()` is atomic; no window exists between temp-file completion and final-path visibility that could expose a partially-written file to a concurrent reader.
- Test-generated artifact cleanup: confirmed - `tests/regression/data/` does not exist in the repository at rest (checked via `find`, Section 7).
- Accidental repository writes during tests: none - every persistence-touching test uses an isolated `tempfile.mkdtemp()` directory, never `evidence.EVIDENCE_DIR` itself.

No additional lint or test dependency was installed for this review.

## 13. Mutation-Style Verification

Seven categories, each applied directly to the relevant `tests/regression/` source file, verified against the real test suite, then reverted immediately (confirmed via `git diff --stat` and a `grep` for any leftover mutation marker, both clean at the end of this section and again at the end of the review).

**13.1 Numeric comparison** (`comparison.py`: `ABSOLUTE_TOLERANCE` temporarily set to `1e6`). Detected by 2 tests: `test_comparison.TestNumericCategoricalComparator.test_tolerance_bounded_field_rejects_large_difference`, `test_regression_scenarios.TestObjectIdentityAndCategoricalAndToleranceComparison.test_tolerance_bounded_numeric_comparison_equity`. Reverted; suite re-confirmed green.

**13.2 Classification** (`classification.py`: final branch condition forced to always select Non-Regression). Detected by 2 tests: `test_classification.test_non_equivalent_comparison_yields_regression`, `test_orchestration.test_different_price_trajectory_yields_regression_with_evidence`. Reverted; suite re-confirmed green.

**13.3 Evidence completeness** (`evidence.py`: two variants tested - the missing-elements check emptied, and separately the bare-`None`-omission check bypassed). Variant 1 detected as a test error via the downstream `KeyError` (`test_missing_element_raises`); variant 2 detected directly (`test_bare_none_omission_raises` failed with "IncompleteEvidenceError not raised", proving an incomplete record would otherwise have reached `Composed`). Both reverted; suite re-confirmed green after each.

**13.4 Atomic persistence** (`evidence.py`: `os.replace()` moved to occur before, rather than after, the `simulate_interruption` check). Detected by 2 tests: `test_evidence.test_interrupted_persist_leaves_record_unpersisted_not_altered`, `test_evidence.test_restart_after_interrupted_persistence_succeeds`. Reverted; suite re-confirmed green.

**13.5 Replay determinism** (`replay.py`: tick price perturbed by `hash(session_id) % 5` before being passed to `RunLoop.step()`). Detected by 4 tests (`test_orchestration.test_repeated_invocation_is_independent_per_call`, `test_orchestration.test_restart_after_failure_succeeds_with_valid_manifest`, `test_regression_scenarios.test_ac_011_end_to_end_information_traceability`, `test_regression_scenarios.test_object_identity_independence_across_two_captures`). Note: because Python's string hashing is randomized per-process, a small number of session-ID pairs may coincidentally share the same `% 5` offset on any given run and would not individually trigger a failure on that run; this is expected and does not weaken the finding, since multiple independent detections occurred. Reverted; suite re-confirmed green.

**13.6 Scope derivation** (`scope.py`: `run_engine/core/regime.py` explicitly excluded from the BFS queue during `derive_scope_partition()`). Detected by 5 tests (`test_coverage.test_compute_with_nothing_exercised_reports_all_active_modules_uncovered`, `test_scope_and_environment.test_active_count_is_fourteen`, `test_scope_and_environment.test_four_previously_uncovered_active_modules_are_active`, `test_scope_and_environment.test_inactive_count_is_four`, `test_scope_and_environment.test_inactive_set_matches_retain_deferred_scope`). Reverted; suite re-confirmed green.

**13.7 Orchestration order** (`orchestrator.py`, pre-correction code: Classification moved to occur before, rather than after, Coverage recording - i.e., a genuine "coverage precedes classification" ordering rather than the then-current self-recording pattern). Detected by 4 tests, all flipping from `Non-Regression`/`Regression` to `Indeterminate` (`test_orchestration.test_different_price_trajectory_yields_regression_with_evidence`, `test_orchestration.test_identical_manifest_yields_non_regression`, `test_orchestration.test_repeated_invocation_is_independent_per_call`, `test_orchestration.test_restart_after_failure_succeeds_with_valid_manifest`). This result independently confirmed Finding F-01: the existing tests' own passing status depended on the self-recording coverage pattern, not on genuine prior coverage. Reverted; suite re-confirmed green. This mutation's own reordering is, in substance, the fix later made permanent by the F-01 correction (Section 14).

**Summary (pre-correction): all seven mutation categories were detected by the existing suite; zero undetected mutations.** Mutation 13.7's own result was additionally treated as direct, independent proof supporting Finding F-01.

**13.8 Post-correction re-verification (governance-directed re-run, against the corrected `orchestrator.py` and the five new/updated tests).**

- **Coverage-confidence mutation:** the corrected sequencing was reverted in place (`record_contract_exercised()` moved back to immediately before `compute()`, reintroducing F-01's own pre-correction pattern verbatim). Detected by 4 tests: `test_orchestration.TestCoverageConfidenceSequencing.test_coverage_established_by_a_prior_invocation_enables_determinate_outcome`, `test_orchestration.TestCoverageConfidenceSequencing.test_never_before_covered_certified_contract_yields_indeterminate`, `test_orchestration.TestCoverageConfidenceSequencing.test_uncertified_contract_indeterminate_reason_distinct_from_low_coverage_reason`, `test_regression_scenarios.TestClassificationOutcomesIntegration.test_indeterminate_when_contract_certified_but_not_yet_covered`. Reverted; suite re-confirmed green (170 tests, OK).
- **Orchestration-order mutation:** Classification moved to occur before `contract_coverage.compute()`, with `coverage_confident` hardcoded to `True` instead of genuinely read. Detected by the identical 4 tests listed above. Reverted; suite re-confirmed green.
- **Classification mutation** (`classification.py`, same fault as 13.2, re-applied against the corrected orchestrator to confirm the fix did not disturb this independent property): final branch condition forced to always select Non-Regression. Detected by 2 tests: `test_classification.test_non_equivalent_comparison_yields_regression`, `test_orchestration.test_different_price_trajectory_yields_regression_with_evidence`. Reverted; suite re-confirmed green.

**Summary (post-correction): all three re-run mutation categories were detected by the existing suite (including the four new F-01-specific tests, each individually confirmed to detect both the coverage-confidence and the orchestration-order mutation); zero undetected mutations. The corrected implementation is no longer vulnerable to the specific fault that produced Finding F-01.**

## 14. Findings and Corrections

**F-01 [LOW, CORRECTED]. Re-evaluation and disposition (governance-directed follow-up).**

*Re-evaluation performed against:* `tests/regression/orchestrator.py`, `tests/regression/coverage.py`, `tests/regression/classification.py`, TD-005 Specification V1.1, TD-005 Implementation Specification V1.1, re-read in full for this follow-up.

*Current data source (pre-correction):* `contract_coverage`, a `ContractRequirementCoverage` instance injected into `RegressionPipelineOrchestrator` and shared across every `invoke()` call on that orchestrator instance (an Authority/Registry-pattern object, per Implementation Specification Section 8's own "Cleanup" bullet - long-lived across invocations, not reset per invocation).

*Current sequencing (pre-correction):* within the `else` branch of `invoke()`, `self.contract_coverage.record_contract_exercised(evaluated_contract_id)` executed, then `contract_report = self.contract_coverage.compute()` executed, then `coverage_confident = evaluated_contract_id not in contract_report.uncovered_contracts` was computed, then `classifier.classify(..., coverage_confident=coverage_confident, ...)` consumed it.

*Current coverage-confidence condition (pre-correction):* `evaluated_contract_id not in contract_report.uncovered_contracts`, evaluated immediately after that same `evaluated_contract_id` had just been unconditionally added to `_exercised_contracts` by the preceding `record_contract_exercised()` call on the same line-sequence, within the same invocation.

*Why this was not scientifically independent:* `uncovered_contracts` is computed as `all_contracts - exercised_contracts` (`coverage.py::ContractRequirementCoverage.compute()`). Because `evaluated_contract_id` was added to `exercised_contracts` immediately beforehand, in the same invocation, `evaluated_contract_id` could never appear in `uncovered_contracts` at the moment `coverage_confident` was computed - independent of whether any invocation, ever, had previously exercised that contract. The signal therefore measured "did this invocation just record itself," not "was this contract already, independently, established as covered." This is a self-satisfying condition, not an independent one, confirmed by direct instrumentation (Section 7, item 7, pre-correction) and by mutation testing (Section 13.7, pre-correction): reordering to check coverage genuinely before recording flipped four passing tests from Non-Regression/Regression to Indeterminate, proving those tests' own passing status depended on the self-recording pattern rather than on any genuine prior coverage fact.

**Disposition: Option A - genuine implementation defect, corrected.** Not Option B: TD005-SD-001's own scientific justification is explicit that "an Indeterminate outcome is required whenever... Coverage... cannot yet confidently place a deviation inside or outside the certified-contract boundary" - a requirement the self-recording pattern defeated by construction for every invocation, not merely an edge case. TD005-AI-014/TD005-SI-015's own advisory-only framing governs whether coverage may *override an already-reached classification* (Section 8/Section 12 correctly confirm it never did); it does not exempt the coverage-confidence *input* itself from needing to be a genuine, independently-computed fact before Classification consumes it, and Implementation Specification Section 8's own Runtime Lifecycle text is explicit that "Coverage... inform[s] Classification in advance, never after (TD005-AI-014)" - the self-recording pattern satisfied the letter of "before" while defeating its scientific substance.

*Correction applied* (`tests/regression/orchestrator.py`): `contract_coverage.compute()` now runs, and `coverage_confident` is read from its result, strictly before `classifier.classify()` is called; `contract_coverage.record_contract_exercised()` (and the analogous `module_coverage.record_event_type_exercised()` bookkeeping) now runs only after `classify()` has already returned its outcome. Coverage-confidence therefore reflects only what a prior invocation (or explicit test-level pre-registration, mirroring how the Reference Baseline is already established as a precondition) established before the current invocation began - never a record the current invocation manufactures for its own benefit. No aggregate coverage percentage was introduced (none is required by TD005-ID-010, and none was added); the existing boolean `coverage_confident` signal was retained, now genuinely computed rather than tautological. No circular dependency was introduced: the dependency direction (`contract_coverage` -> `classifier`) is unchanged; only the read/write order of two calls on the same already-existing dependency was corrected. The `certified_contract_id` reasoned-unavailability-marker text was additionally refined (`_indeterminate_contract_id_reason()`) to name the two Indeterminate causes - uncertified contract, versus certified-but-not-yet-covered - distinctly, since the correction makes both genuinely, independently reachable through the full pipeline (previously only the former was reachable, so a single generic marker text was a latent, not yet live, imprecision).

*Tests added, proving the six Option-A requirements:*
1. Certified contract + equivalent behaviour + complete (prior-established) coverage -> Non-Regression: `test_orchestration.TestOrchestrator.test_identical_manifest_yields_non_regression` (updated to pre-establish coverage, mirroring the existing `establish_reference()` precondition pattern via a new `establish_coverage()` helper).
2. Certified contract + non-equivalent behaviour + complete coverage -> Regression: `test_orchestration.TestOrchestrator.test_different_price_trajectory_yields_regression_with_evidence` (updated identically).
3. Unresolved/incomplete coverage -> Indeterminate: `test_orchestration.TestCoverageConfidenceSequencing.test_never_before_covered_certified_contract_yields_indeterminate` (new); `test_regression_scenarios.TestClassificationOutcomesIntegration.test_indeterminate_when_contract_certified_but_not_yet_covered` (new).
4. Upstream execution/comparison failure -> Invalid Comparison: `test_orchestration.TestOrchestrator.test_candidate_failure_yields_invalid_comparison_with_evidence` (pre-existing, unaffected by this correction - the early-exit path never touches coverage).
5. Coverage cannot change a completed Regression or Non-Regression outcome after classification: `test_orchestration.TestCoverageConfidenceSequencing.test_coverage_recorded_after_classification_never_alters_the_returned_outcome` (new).
6. Orchestration invokes coverage before classification where required: `test_orchestration.TestCoverageConfidenceSequencing.test_coverage_established_by_a_prior_invocation_enables_determinate_outcome` (new - a first invocation of a never-covered contract is Indeterminate; a second invocation of the *same* contract, now covered by the first, is Non-Regression, directly proving `compute()` reads state established before the current call).

*Mutation-style re-verification:* Section 13.8. Coverage-confidence mutation (reintroducing the pre-correction self-recording pattern) and orchestration-order mutation (classification before a genuine `compute()`) were both independently re-applied to the corrected code and both detected by the same four new tests; the classification mutation (Section 13.2's own fault) was re-applied and remained independently detected. All reverted; full suite re-confirmed green (170 tests, OK) after each.

Affected baseline IDs: TD005-ID-009 (Step 2), TD005-SO-013, TD005-SD-001, TD005-AI-014, TD005-SI-015 (all now more completely satisfied, none contradicted; no baseline text required amendment - the correction operates entirely within Implementation-stage discretion already granted by TD005-SO-013's own "Requires Further Specification: concrete classification procedure" deferral, resolved at the Implementation Specification level by TD005-ID-009 and left to code-level realization).
Correction status: **fixed**; full suite re-run after correction (170 tests, 0 failures, 0 errors).

**F-02 [LOW].**
Files: `tests/regression/comparison.py`, `tests/regression/evidence.py`, `tests/regression/reference_baseline.py`, `tests/regression/test_regression_scenarios.py`.
Description: five unused imports (`Dict`, `Enum` in `comparison.py`; `Optional` in `evidence.py`; `Dict`, `Any` in `reference_baseline.py`; `ObservableSurfaceClassifier` in `test_regression_scenarios.py`).
Independent evidence: an AST-based reference-count scan (Section 5), individually confirmed per name via `grep` before correction.
Impact: none functional; code hygiene only.
Required correction: removed. Full suite re-run after correction: 165 tests, 0 failures, 0 errors.
Affected baseline IDs: none.
Correction status: fixed.

**F-03 [INFORMATIONAL, reclassified from Low].**
File: `tests/regression/orchestrator.py`, `_compose_and_persist_evidence()`, `affected_tick` element.
Description: the `affected_tick` evidence element's determinate value is `first_diff.path` (e.g. `"tick[3].price"`), a full dotted path string, not a raw tick index, despite the field's own name and TD005-SO-016's literal "affected tick" description.
Independent evidence: Section 7 item 8 (persisted evidence content inspected directly).
Re-examination (this follow-up): confirmed no code correction is required. The tick index is embedded in the path string and remains fully sufficient for independent reproduction, which is TD005-FR-019's own actual, literal requirement ("sufficient detail... to allow the failure to be independently reproduced"); no accepted baseline requires the raw integer to be stored in a separate field, and TD005-SO-016 itself specifies required *elements*, not their internal representation. This is an accepted residual limitation of field-naming precision, not a defect - correction would only be justified if reproduction were actually impaired, which it is not.
Affected baseline IDs: TD005-SO-016 (naming precision only; not contradicted).
Correction status: no code correction required; accepted residual limitation.

**F-04 [INFORMATIONAL, reclassified from Low].**
File: `tests/regression/orchestrator.py`, `_compose_and_persist_evidence()`, `certified_contract_id` element.
Description: for the Invalid-Comparison early-exit path (candidate replay failed before `Captured`), `certified_contract_id` is set to the raw `evaluated_contract_id` input parameter as a determinate value, even though `self.boundary.evaluate()` is never invoked on that code path.
Independent evidence: Section 7 item 8.
Re-examination (this follow-up): confirmed no code correction is required. The value is not fabricated - it is the actual contract this invocation was asked to evaluate, known unconditionally from the `invoke()` call's own parameter, independent of whether the certification boundary was ever consulted for it in this specific invocation. TD005-SO-016's own field description requires "the specific certified-contract ID the deviation is attributed to," which this value correctly satisfies; TD005-II-014 governs the reasoned-unavailability *marker* text, not a determinate value, and is not engaged here since no marker was used. This is an accepted residual limitation of certainty-framing, not a defect.
Affected baseline IDs: TD005-SO-016, TD005-II-014 (neither contradicted - the element carries a real, correct, baseline-satisfying value).
Correction status: no code correction required; accepted residual limitation.

**F-05 [INFORMATIONAL].** Deviation A (ControlledConditionManifest limitation) - see Section 10. Independently reconfirmed accurate and additionally strengthened (production's own `main()` also has no injection point). Acceptable implementation constraint, non-blocking.

**F-06 [INFORMATIONAL].** Deviation B (direct-class lifecycle testing) - see Section 10. Independently re-derived from source, confirmed accurate and sufficient. Acceptable, non-blocking.

**F-07 [INFORMATIONAL].** `test_evidence.py::test_identical_environment_matches_itself` - minor test-name imprecision (compares two distinct captures, not a capture against itself); assertion itself correct. Not corrected (name/docstring-only nit).

**F-08 [INFORMATIONAL].** No test exercises `ReplaySession`'s bounded-duration failure mid-sequence (only immediate timeout, `bounded_duration_seconds=0.0`, is tested); the underlying check was independently confirmed correct by direct code inspection. Missing boundary test, non-blocking.

**F-09 [INFORMATIONAL].** Behavioural consequence of the F-01 correction, disclosed for clarity: a certified contract's *very first* evaluation against a given `ContractRequirementCoverage` instance now genuinely yields Indeterminate, not a determinate outcome, since no prior coverage exists yet to consult. This is the intended, scientifically correct consequence of the fix (Section 15), not a defect; a operator running this suite for the first time against a fresh coverage tracker (for example, at the start of a Long-Duration-Validation sequence) should expect the first invocation of each contract to be Indeterminate and subsequent invocations of the same contract to be determinate, and should not mistake the first occurrence for a regression-detection failure.

No Critical, High, or Medium finding was identified. No Low finding requiring correction remains unresolved: F-01 and F-02 were corrected; F-03 and F-04 were re-examined and confirmed to require no correction, reclassified Informational.

## 15. Remaining Risks

- The coverage-confidence self-recording pattern (F-01) has been corrected; no residual risk from that specific defect remains. The resulting behavioural consequence (F-09) - a contract's first-ever evaluation against a fresh coverage tracker is genuinely Indeterminate - is documented so a future operator of this suite, including whoever runs the Long-Duration-Validation sequence, does not mistake it for a regression-detection failure.
- Both disclosed deviations (A and B) remain permanent features of this suite for as long as the active `RunLoop` offers no state-injection point and `StrategySelector`'s own default parameters keep a LONG position from naturally flipping to SELL; neither is a defect, but both should be re-examined if `run_engine/` itself is ever modified in a way that changes either property.
- The Long-Duration-Validation execution-time budget and the evidence retention/expiry policy remain explicitly, correctly open (`registry.py` `STILL_OPEN`), pending real calibration data no accepted baseline currently supplies.

## 16. Certification Decision

**CERTIFIED WITH MINOR CORRECTIONS**

Rationale: no Critical, High, or Medium finding was identified during this independent review or its governance-directed follow-up. Nine findings were identified in total. Two required correction (F-01, F-02), both Low, both corrected and independently re-verified (full suite green at 170 tests; mutation re-verification in Section 13.8 confirmed the corrected code is no longer vulnerable to the specific faults that produced F-01 or F-02). Two further Low findings (F-03, F-04) were re-examined under this same governance-directed audit discipline and confirmed to require no code correction, and are accordingly reclassified Informational, not left as unresolved Low findings. The remaining five findings (F-05 through F-09) are Informational: accepted residual limitations, non-blocking observations, or documentation of the corrected behaviour's own intended consequence. No Low, Medium, High, or Critical finding requiring correction remains unresolved. All ten mutation-style verification categories across both review passes (seven original, three re-run post-correction) were detected by the existing suite; zero undetected mutations at any point. All mandatory scenarios named in the governing implementation task are adequately evidenced, at the correct tier (full-pipeline, direct-class, or both), independently re-derived against the actual active Run Engine source. No blocking baseline conflict or deviation was found; the F-01 correction required no accepted-baseline amendment, since it operated entirely within Implementation-stage discretion the Specification and Implementation Specification already grant.

## 17. Final Recommendation

TD-005 Stage 7 (Implementation / Coding) is ready to proceed to TD-005 Final Certification. No accepted baseline requires amendment. Findings F-03, F-04, F-05, F-06, F-07, F-08, and F-09 should be carried forward as disclosed, non-blocking, Informational observations for the Final Certification stage's own review; none requires further action before that stage begins.

All review-only scripts created during the original review (`independent_verify_1.py` through `independent_verify_4.py`, `unused_imports_check.py`) were written to the session scratchpad directory outside the repository and were never added to the repository; none remain under `tests/regression/` or anywhere else in the repository. No new review-only script was created for this follow-up correction pass - all re-verification was performed via direct, immediately-reverted mutation of the relevant `tests/regression/` source files (Section 13.8). All ten mutation-style fault injections across both passes were fully reverted immediately after each was confirmed detected; `grep -r "MUTATION" tests/regression/` returns zero matches as of the end of this follow-up. No `run_engine/` file was changed. `requirements.txt` is unchanged. The SGF-013 working-tree modification remains preserved exactly. No file outside `tests/regression/`, this certification document, and (not modified, confirmed factually accurate as-is) the Implementation Report was touched. Nothing was staged, committed, or pushed.

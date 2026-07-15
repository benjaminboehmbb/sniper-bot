# Document Metadata

Document Class: Scientific Dependency Analysis
Document ID: P1-04-SDA
Version: V1.0
Status: Draft
Date: 2026-07-09
Project: Trading-Bot Scientific Runtime
Subsystem: Run Engine
Storage Location: docs/architecture/analysis/
Filename: P1_04_SCIENTIFIC_DEPENDENCY_ANALYSIS_V1_2026-07-09.md

Depends On:
- docs/architecture/RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md
- docs/architecture/RUN_ENGINE_IMPLEMENTATION_BASELINE_V1_2026-07-07.md
- docs/architecture/analysis/P1_04_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-09.md (sole functional input)

Referenced By:
- P1_04_CAPABILITY_GAP_ANALYSIS
- P1_04_ARCHITECTURE
- P1_04_SPECIFICATION

---

# P1-04 Scientific Dependency Analysis

## 1. Metadata

See Document Metadata block above.

---

## 2. Objective

The P1-04 Functional Requirement Analysis derived six functional requirements (P1-04-FR-001 through P1-04-FR-006) implementing ADR-011 ("Runtime Failure Handling"). Before architecture or specification work begins, the dependency structure underlying these six requirements must be derived.

The objective of this document is to:

1. Decompose each functional requirement into its atomic scientific/technical capabilities.
2. Determine, for each atomic capability, whether it already exists as a verified output of P1-01 through P1-03.1, or whether it must be newly established.
3. Apply the Removal Test (as used in the P1-03 Scientific Dependency Analysis) to classify each candidate dependency.
4. Certify whether P1-04 may proceed directly to Capability Gap Analysis, or whether a missing prerequisite capability must first be built.

This document proposes no interfaces, no implementation, and no architecture. It uses `P1_04_FUNCTIONAL_REQUIREMENT_ANALYSIS_V1_2026-07-09.md` as the sole functional input.

---

## 3. Functional Capability Decomposition

Each functional requirement is decomposed into the atomic capabilities it requires.

**P1-04-FR-001 (Explicit Runtime-Failure Gate in RunLoop)** requires:
- A distinguishable rejection signal on the lifecycle event returned to `RunLoop`.
- A branch point in `RunLoop.step()` capable of consuming that signal.

**P1-04-FR-002 (Performance Non-Mutation on Rejection)** requires:
- The same distinguishable rejection signal.
- A data path carrying that signal (or an equivalent skip decision) to `PerformanceEngine`.

**P1-04-FR-003 (Position Mark-Price Update Policy on Rejection)** requires:
- The same distinguishable rejection signal.
- An explicit, adjudicated policy decision on whether `last_price` may update on rejection.
- A data path carrying the rejection signal (or the resulting policy outcome) to `PositionEngine`.

**P1-04-FR-004 (Runtime Failure Event Traceability Verification)** requires:
- Generation of an immutable Runtime Failure Event on every rejected transition.
- Permanent, queryable retention of that event.

**P1-04-FR-005 (Deterministic Rejection Replay)** requires:
- A rejection-event generation mechanism (as above).
- Deterministic behavior of the full active execution path, with no hidden nondeterminism between identical inputs.

**P1-04-FR-006 (Financial State Non-Mutation Contract)** requires:
- The same distinguishable rejection signal.
- An explicit, testable contract (not an incidental side effect) guaranteeing `PnLEngine`/`CanonicalState` financial fields do not change on rejection.

Collapsing duplicates across the six requirements yields five distinct candidate capabilities, analyzed in Section 5.

---

## 4. Scientific Dependency Graph

```text
D-001  Rejection Signal Existence
   │
   ├──> D-002  Rejection Immutability & Retrievability
   │
   ├──> D-004  Consumer-Side Rejection Awareness (interface wiring)
   │        │
   │        └──> satisfies FR-001, FR-002, FR-003, FR-006
   │
   └──> D-005  Explicit Mark-Price Policy Decision
            │
            └──> required specifically by FR-003 (in addition to D-004)

D-003  Deterministic Runtime Execution (independent primitive)
   │
   └──> required by FR-005, and implicitly by FR-004/FR-006's reproducibility
```

D-001 is the root dependency. D-002, D-004, and D-005 each build on D-001. D-003 is an independent primitive (it does not derive from D-001 and does not feed into it) required specifically for replay-determinism claims. No circular dependency exists. No dependency inversion was identified.

---

## 5. Capability Prerequisites

**D-001 — Rejection Signal Existence**

Definition: The runtime must be able to represent "this proposed transition was rejected" as one explicit, distinguishable value, generated deterministically whenever a proposed transition violates the Lifecycle Transition Table.

Status: **Exists.** `TradeLifecycleEngine._failure_event()` produces a `LifecycleEvent` with `event_type="RUNTIME_FAILURE_EVENT"` and a `reason` field, for all four currently defined rejection classes (`INVALID_EXECUTION_QUANTITY`, `NO_ACTIVE_TRADE`, `OVER_CLOSE_QUANTITY`, `UNSUPPORTED_EXECUTION_ACTION`). Established in P1-03, hardened for non-finite/non-numeric input in P1-03.1.

Removal Test: If removed, `RunLoop` and every downstream component would have no way to distinguish an accepted tick from a rejected one at all — none of FR-001 through FR-006 could be defined.

Classification: Mandatory Primary Dependency. **Already satisfied.**

---

**D-002 — Rejection Immutability & Retrievability**

Definition: Once created, a Runtime Failure Event must be permanent and queryable — not merely a transient return value.

Status: **Exists.** `LifecycleEvent` is a frozen (`frozen=True`) dataclass; instances are appended to `TradeLifecycleEngine.failure_events` (an append-only list) and, when applicable, to the active trade's `events` history. `get_failure_events()` provides retrieval.

Removal Test: If removed, Runtime Failure Events could be silently lost or mutated after creation, violating ADR-011's "permanently preserved" requirement and AC-015.

Classification: Mandatory Dependency. **Already satisfied.**

---

**D-003 — Deterministic Runtime Execution**

Definition: Identical inputs to the active execution path (`StateEngine → RegimeClassifier → StrategySelector → Executor → TradeLifecycleEngine → PositionEngine → PnLEngine → RiskEngine → PerformanceEngine`) must produce identical outputs, with no hidden nondeterminism.

Status: **Exists on the active execution path.** `run_engine/core/regime.py`'s previous random-fallback behavior was removed (commit `6422438`, "Remove random regime fallbacks"). A repository-wide search for `random`/`Random` usage inside `run_engine/core` found exactly one remaining occurrence, in `run_engine/core/state_modulation.py` (`random.random()` calls). That module is **not imported by any file in `run_engine/core`** — it is dead code outside the Verified Active Execution Path defined by the Architecture Baseline, and does not affect determinism of the path P1-04 operates on. This is recorded as a non-blocking observation in Section 9, not treated as a defect in this capability.

Removal Test: If removed, P1-04-FR-005's acceptance criterion (identical replay produces identical Runtime Failure Event values) would be untestable and potentially false.

Classification: Mandatory Dependency. **Already satisfied for the active path.**

---

**D-004 — Consumer-Side Rejection Awareness (interface wiring)**

Definition: Each downstream consumer that must suppress a side effect on rejection needs a data path carrying the rejection signal (or an equivalent decision derived from it).

Status: **Partially wired, not missing as a capability.** The signal itself (D-001) already exists and is already available as `trade_event` inside `RunLoop.step()`, and is already passed explicitly into `PnLEngine.update()`. It is **not currently passed** into `PerformanceEngine.update(decision, pnl, regime)`, whose signature has no rejection-aware parameter. Precedent for this kind of explicit consumer-side context-passing already exists in the codebase (e.g., `RiskEngine.check(canonical_state, position, regime)` already receives explicit context parameters rather than inferring state implicitly) — so satisfying D-004 requires only an interface extension using an already-existing value, not a new data model or new domain concept.

Removal Test: If this wiring is never added, FR-002, FR-003, and FR-006 cannot be implemented, since there is currently no path carrying the rejection signal to `PerformanceEngine`, and no explicit path (only an incidental one, via `PnLEngine`'s event-type filter) enforcing the financial-state contract.

Classification: **This is the one true prerequisite gap identified by this analysis.** It is classified as **P1-04's own implementation scope**, not a missing capability inherited from an earlier phase — it consumes only data (`trade_event.event_type`) that P1-01 through P1-03.1 already produce. This distinction is the determining factor for the certification in Section 10.

---

**D-005 — Explicit Mark-Price Policy Decision**

Definition: A single, documented decision on whether `Position.last_price` may update on a rejected transition.

Status: **Not yet decided** (open question RQ-001 in the Functional Requirement Analysis). This is not a technical or scientific capability gap: the runtime already has full technical capacity to implement either policy (it currently implements "always update"). What is missing is the decision itself.

Removal Test: Without this decision, FR-003/AC-002 cannot be finalized in the Architecture document — but Capability Gap Analysis does not require the decision to already be made; it requires only that no capability is missing to reach a decision and implement it, which is true.

Classification: **Specification Decision, not a capability dependency.** Deferred to the P1-04 Architecture document, consistent with RQ-001.

---

## 6. Dependency Ordering

D-001, D-002, and D-003 require no ordering relative to P1-04 — they are already satisfied, inherited unchanged from P1-01 through P1-03.1.

Within P1-04's own scope, the ordering is:

1. D-005 (mark-price policy decision) should be resolved in the Architecture document before D-004's `PositionEngine`-specific wiring is specified for FR-003, since the wiring's behavior depends on which policy is chosen.
2. D-004's wiring for FR-001 (RunLoop gate), FR-002 (`PerformanceEngine`), and FR-006 (financial contract) does not depend on D-005 and may proceed independently and in parallel.
3. FR-004 (traceability verification) and FR-005 (deterministic replay) depend only on D-001, D-002, and D-003, all already satisfied — they may be verified immediately and do not block, or wait on, D-004/D-005.

No circular ordering constraint exists.

---

## 7. Minimal Capability Set

The minimal set of capabilities that must exist before P1-04 can be specified and implemented is:

- D-001 — Rejection Signal Existence
- D-002 — Rejection Immutability & Retrievability
- D-003 — Deterministic Runtime Execution

All three are **already present** in the runtime as of commit `57e24e6` (P1-03.1). No capability outside this minimal set was found to be required. D-004 (interface wiring) and D-005 (policy decision) are not prerequisite capabilities in the P1-03-SDA sense — they are the work product P1-04 itself is scoped to produce, using the minimal set as its foundation.

---

## 8. Scientific Justification

This conclusion is consistent with the Implementation Baseline's own diagnosis of Phase 1 as a whole: Scientific Finding SF-002 states that "the principal architectural problem is incomplete integration rather than missing functionality." P1-04 is a direct instance of this pattern — the Runtime Failure Event concept required by ADR-011 was already built (as a necessary consequence of implementing the Lifecycle Transition Table's invalid-transition handling in P1-03, per ADR-009), and P1-03.1 already hardened its input validation. What ADR-011 additionally requires — that rejection is explicitly honored by every downstream consumer — is integration work, not new capability.

This is also consistent with ADR-002 (Event-Driven Runtime Evolution): the Runtime Failure Event is already a first-class Runtime Event in the approved event hierarchy ("Trade Lifecycle Events... Runtime Failure Event"). P1-04 does not need to invent a new event category; it needs to ensure existing consumers respect an event category that already exists.

No Architecture Decision Record is contradicted by this conclusion, and no new Authoritative Owner, Computational Authority, or canonical runtime information object is introduced by any of the five candidate dependencies — satisfying Principle IP-001 (Architecture First: implementation shall never redefine architectural responsibilities).

---

## 9. Risks

**R-001** — D-004's implementation strategy (RunLoop-level gate vs. per-consumer guard, RQ-002 in the Functional Requirement Analysis) is an open design choice, not a capability risk. It must be resolved in the Architecture document before Specification.

**R-002** — D-005's mark-price policy decision (RQ-001) is unresolved. Until decided, FR-003/AC-002 cannot be finalized. This does not block Capability Gap Analysis, which does not depend on the decision being made yet.

**R-003** — `run_engine/core/state_modulation.py` contains `random.random()` calls and is currently dead code (not imported anywhere in `run_engine/core`). It does not affect D-003 today, but its presence is a latent risk if a future change wires it into the active path without revisiting this determinism claim. Recommended for Phase 6 Repository Consolidation classification (Retain / Integrate / Archive / Remove), not P1-04 scope.

**R-004** — FR-004 and FR-005's verification activities (Section 3) will be performed manually, as no automated regression test suite exists for `run_engine/core` (TD-005, Technical Debt Register). This is a methodology risk carried forward from P1-03.1, not a new one introduced here.

---

## 10. Conclusion

Every P1-04 functional requirement (P1-04-FR-001 through P1-04-FR-006) was decomposed into its atomic capabilities. Of the five distinct candidate dependencies identified, three (D-001 Rejection Signal Existence, D-002 Rejection Immutability & Retrievability, D-003 Deterministic Runtime Execution) are the minimal capability set required as input, and all three are already implemented and verified as of P1-01 through P1-03.1. The remaining two items (D-004 interface wiring, D-005 policy decision) are P1-04's own implementation and specification scope — built from, not blocked by, the existing capability set.

**No missing prerequisite capability was identified.**

**P1-04 may proceed directly to Capability Gap Analysis.**

---

## 11. Next Document

The next document is `P1_04_CAPABILITY_GAP_ANALYSIS_V1_2026-07-09.md`.

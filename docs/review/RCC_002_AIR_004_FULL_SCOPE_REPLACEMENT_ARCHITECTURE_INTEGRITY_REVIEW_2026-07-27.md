# RCC-002-AIR-004 — Full-Scope Replacement Architecture Integrity Review

## 1. Document Control

| Field | Value |
|---|---|
| Document Class | Full-Scope Replacement Architecture Integrity Review |
| Review ID | `RCC-002-AIR-004` |
| Review Type | Full-Scope Replacement Architecture Integrity Review |
| Date | 2026-07-27 |
| Status | Completed — Verdict: **PASS WITH MINOR CORRECTIONS** |
| Reviewed Substrate | `docs/review/RCC_002_MINOR_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md` (SHA-256 `8bd00fd09055e0055b09642edbdddf105c25ea1f36b720c1892f07d360aca75f`) |
| Status Function | Full replacement of `RCC-002-AIR-002`; final architecture review before Internal Certification |
| Storage Location | `docs/review/RCC_002_AIR_004_FULL_SCOPE_REPLACEMENT_ARCHITECTURE_INTEGRITY_REVIEW_2026-07-27.md` |
| Evidence File | `docs/review/evidence/RCC_002_AIR_004_REVIEW_EVIDENCE_2026-07-27.json` |
| Working Mode | Read-only. No specification, bundle, manifest, or prior review file was modified. No commit was created. |
| Independence | No prior architecture verdict (AIR-001, AIR-002, AIR-003) or scientific verdict (SCR-007, SCR-008) was accepted as proof of architectural soundness. Every claim below was independently re-derived from the current bundle/source text through an architecture lens (ownership, control flow, dependency graph, gate composition, implementability, testability) distinct from SCR-008's scientific-consistency lens. Where this review's conclusion differs from SCR-008's (specifically on the O-8 carve-out asymmetry), the difference and its reasoning are stated explicitly. |

No files were changed and no commit was created, with the exception of this report and its evidence file.

---

## 2. Executive Summary

Input control passed completely: all seven referenced artifacts (bundle, manifest, Implementation Record, Implementation Evidence, SCR-008 report, SCR-008 Evidence, Implementation Plan) independently re-hash to their stated values; the generator reproduces the bundle byte-for-byte in an independent round-trip; the bundle contains exactly seven specifications, each once, in canonical order; the version matrix matches the expected values exactly for all seven documents. SCR-008's own claims (0 Critical, 0 Major, 0 open Minor, 6/6 findings closed, 0 regressions, both deviations accepted) were independently re-confirmed against its own evidence JSON.

The architecture was assessed from scratch through the lens this review is specifically responsible for: system boundary, decomposition/cohesion/coupling, the full stage chain's contracts, a field-ownership matrix, the dependency graph (confirmed acyclic), an implementable control-flow/state-machine derivation, error/fail-closed architecture, gate composition, reproducibility/manifest/publication architecture, configuration and partitioning architecture, schema architecture, implementation readiness, test architecture, and governance architecture — each backed by fresh quotes and ten required matrices, 20 architecture-smell checks, and 25 negative architecture scenarios.

**Result: the seven specifications form a closed, non-circular, ownership-clean architecture that is implementable and testable without further architectural decisions**, with one exception: this review does **not** adopt SCR-008's classification of its own Observation O-8 (the `PASS_WITH_APPROVED_EXCEPTIONS` carve-out lists in Indicator §30 and Signal Transformation §32 not explicitly naming a failed Property-Test as non-overridable). Assessed independently through an *implementability* lens rather than a scientific-consistency lens, this is elevated to a genuine architecture gap — an engineer implementing the Publication Gate's exception-approval logic faces a real, unresolved design choice (is the enumerated non-overridable list exhaustive or illustrative?) that the specification does not close. This is classified **Minor Finding `AIR4-MIN-01`**, not Critical or Major, because the exception mechanism already requires human documentation and approval (not an automatic bypass) and because every other Publication Gate control in the family is unambiguous.

No Critical Finding and no other Major Finding were found. Zero circular dependencies, zero ownership conflicts, zero unresolved control-flow ambiguity in the core pipeline, zero publication-bypass vectors beyond the one noted above.

**Verdict: PASS WITH MINOR CORRECTIONS.** **Internal-Certification Recommendation: `RECOMMENDED FOR INTERNAL CERTIFICATION AFTER MINOR CORRECTIONS`** — specifically, resolving `AIR4-MIN-01` (a one-sentence clarification in two documents) before or alongside Editorial Pass; nothing else blocks certification on architectural grounds.

---

## 3. Review Identity

`RCC-002-AIR-004` fully replaces `RCC-002-AIR-002` as the architecture review of record for the current bundle. AIR-002 is not treated as valid for the current bundle (it reviewed a materially different, pre-C1 artifact, and its own review-lineage validity was separately challenged by Finding C2 — see `RCC_002_C2_REVIEW_LINEAGE_INVESTIGATION_2026-07-25.md`, out of scope for re-litigation here). This review does not accept AIR-001/AIR-002/AIR-003's architectural conclusions, nor SCR-007/SCR-008's scientific conclusions, without independent re-derivation.

---

## 4. Scope

Architecture integrity of the full seven-document specification family: system boundary, decomposition, stage architecture, data flow, ownership, boundary contracts, dependency architecture, control flow/orchestration, error architecture, gate architecture, reproducibility architecture, manifest architecture, publication architecture, configuration architecture, partitioning/scaling architecture, schema architecture, implementation readiness, test architecture, and governance architecture — plus consistency-checking against SCR-008 as prior scientific evidence (not as a substitute for this review).

Explicitly out of scope: re-deriving scientific/mathematical correctness already covered by SCR-007/SCR-008 (used here only as evidence); implementing any correction; any actual software implementation of RCC-002 (none exists in this repository).

---

## 5. Reviewed Substrate

| Artifact | Path | Expected SHA-256 | Actual SHA-256 | Match |
|---|---|---|---|---|
| Bundle | `docs/review/RCC_002_MINOR_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md` | `8bd00fd09055e0055b09642edbdddf105c25ea1f36b720c1892f07d360aca75f` | `8bd00fd09055e0055b09642edbdddf105c25ea1f36b720c1892f07d360aca75f` | ✅ |
| Manifest | `docs/review/RCC_002_MINOR_CORRECTED_BUNDLE_MANIFEST_2026-07-27.md` | `7edd5c28d20db328be64394b615c3cadec81ecbaaac8ccca05577586c251c030` | `7edd5c28d20db328be64394b615c3cadec81ecbaaac8ccca05577586c251c030` | ✅ |
| Implementation Record | `docs/review/RCC_002_MINOR_CORRECTION_IMPLEMENTATION_RECORD_2026-07-27.md` | `47d67eccd7586df2f5570d98a578532b910016bba1a482020a6899e4689e65e7` | `47d67eccd7586df2f5570d98a578532b910016bba1a482020a6899e4689e65e7` | ✅ |
| Implementation Evidence | `docs/review/evidence/RCC_002_MINOR_CORRECTION_IMPLEMENTATION_EVIDENCE_2026-07-27.json` | `3441bbb434922fb0ec58f00f76f7e2b0f6380d114184ebcd7968d0871f8b4048` | `3441bbb434922fb0ec58f00f76f7e2b0f6380d114184ebcd7968d0871f8b4048` | ✅ |
| SCR-008 Report | `docs/review/RCC_002_SCR_008_FULL_SCOPE_RE_REVIEW_2026-07-27.md` | `642b0f12b67985e18f843cfcb93bd945ba18db8aae634487aa261d81fd590a63` | `642b0f12b67985e18f843cfcb93bd945ba18db8aae634487aa261d81fd590a63` | ✅ |
| SCR-008 Evidence | `docs/review/evidence/RCC_002_SCR_008_REVIEW_EVIDENCE_2026-07-27.json` | `37f5a800325c2c9f275186aa430342d7cb0eb4011e38cfba0a82e85f9269b4f6` | `37f5a800325c2c9f275186aa430342d7cb0eb4011e38cfba0a82e85f9269b4f6` | ✅ |
| Implementation Plan | `docs/review/RCC_002_MINOR_CORRECTION_IMPLEMENTATION_PLAN_2026-07-27.md` | `1751494fa0f7ef2fcf039f7bc4fd1f022f4250d56265395b8db74ebf4162085c` | `1751494fa0f7ef2fcf039f7bc4fd1f022f4250d56265395b8db74ebf4162085c` | ✅ |

---

## 6. Hash Verification

All seven hashes independently recomputed and matched exactly. Bundle: 13,926 lines / 493,231 bytes, matching expected values exactly. SCR-008's own evidence JSON was parsed directly and confirms: `finding_counts = {critical: 0, major: 0, minor: 0, observation: 8, positive_finding: 6, future_architecture_risk: 4}`, `regression_detected = false`, both deviations `ACCEPTED`, `final_verdict = "PASS WITH MINOR CORRECTIONS"` — independently re-read, not assumed.

**Result: fully passed.**

---

## 7. Round-Trip Verification

Generator executed independently against a temporary path with the exact recorded arguments. Result: 13,926 lines / 493,231 bytes, SHA-256 `8bd00fd09055e0055b09642edbdddf105c25ea1f36b720c1892f07d360aca75f` — exact match; `diff` reported no differences. Temporary file deleted after verification.

**Result: round-trip byte-exact.**

---

## 8. Methodology

1. Mandatory input control (Sections 6–7) performed first and independently.
2. SCR-008 was read and its claims independently re-verified against its own evidence JSON (Section 6), then treated strictly as scientific evidence for this review, never as a substitute for architectural judgment (per this review's own governing instruction).
3. The architecture was reconstructed independently from the current specification texts: system boundary and scope statements, the Document-Control dependency fields (for the dependency graph), each stage's field-ownership registry (for the ownership matrix), each stage's abort/error-handling section (for error architecture), each Publication Gate chapter (for gate/publication architecture), and Reproducibility's identity/manifest/lineage apparatus (for reproducibility/manifest architecture).
4. Ten required architecture matrices, a 20-item architecture-smell checklist, and 25 negative architecture scenarios were each worked through explicitly against this reconstructed architecture, not against prior review prose.
5. The one point where this review's judgment diverges from SCR-008 (O-8 / `AIR4-MIN-01`) was reached by applying an implementability-specific test (*"could a competent implementer build this component without an additional, unspecified architectural decision?"*) rather than SCR-008's scientific-consistency test (*"does this create a demonstrated divergent scientific result?"*) — the review order explicitly directs this distinct standard.
6. Findings were classified per the six-tier taxonomy given, each requiring a concrete contract/data-flow/ownership/gap citation, not editorial preference.

---

## 9. System Boundary Assessment

Data Pipeline's own Document-Control fields state the system boundary explicitly:

> "Geltungsbereich | Kanonische Forschungsdatenpipeline für BTCUSDT und spätere weitere Assets/Zeitebenen"
> "Referenziert durch | künftige RCC-002-Implementierung; Analyse-Runner; SimTrader; Live-/Paper-Trading-Paritätsprüfung; Dataset Manifest"

Each of the six subordinate specifications declares its own narrower `Geltungsbereich` (S0–S2, S3, S4, S5–S6, S7, S0–S8 respectively) and its own `Referenziert durch` field naming external consumers (Strategieforschung, Backtest, Paper-/Live-Parität, ML-Datensätze, Counterfactual Gate Evaluation, Walk-Forward-Analysen, RCC-002-Implementierungsplan, Build- und Prüfwerkzeuge, Dataset-Release-Dokumentation). RCC-002 consistently positions itself as a **data-producing** system whose artifacts are *consumed by* strategy research, backtesting, and paper/live parity checking — never as a system that itself performs strategy decisions, order execution, or run-loop orchestration. No specification claims ownership of, or describes internal mechanics for, `run_engine/`, `live_l1/`, or `engine/simtraderGS.py` (the implemented code paths documented in this repository's `CLAUDE.md`) — RCC-002 is confirmed, by the consistent absence of any such claim across all seven documents, to be a specification-only, not-yet-implemented sibling data pipeline, with a one-directional "produces datasets that these systems may consume" relationship, never the reverse.

**Assessment**: the system boundary is clearly, consistently, and non-overlappingly stated at both the family level (Data Pipeline) and the per-stage level (each subordinate document). No implicit scope expansion was found — every `Referenziert durch` field names external *consumers*, never external *dependencies* the pipeline itself relies on, keeping the boundary one-directional and closed. **Implementable and testable: yes.**

---

## 10. Architectural Decomposition

| Specification | Cohesion | Coupling to others | Overlap/duplication found? |
|---|---|---|---|
| Data Pipeline | High — global principles, S0/S1 canonical formats, S8 field-ownership registry, cross-cutting policy (§5, §6, §7.9, §8, §9, §12, §19) | Root of the dependency graph (Section 15) — zero inbound normative dependency, six outbound "referenced by" relationships | None found — its S8 field-ownership-registry role (§7.9) is the one place it descends to concrete-registry detail, justified because that registry is inherently cross-stage (Section 26, God-Specification smell) |
| Data Validation | High — S0/S1/S2 exclusively | Depends only on Data Pipeline | None |
| Indicator | High — S3 exclusively | Depends on Data Pipeline, Data Validation | None |
| Signal Transformation | High — S4 exclusively | Depends on Data Pipeline, Data Validation, Indicator | None |
| Regime and Gate | Medium-high — S5 and S6 are two distinct concerns (classification vs. gating) sharing one document | Depends on Data Pipeline, Data Validation, Indicator, Signal Transformation | S5/S6 co-location assessed in Section 11 — found justified, not an overlap |
| Label and Forward Return | High — S7 exclusively | Depends on all five upstream documents | None |
| Reproducibility and Manifest | High — build/dataset/manifest/lineage/publication identity, explicitly *not* stage semantics | Depends on all six other documents (widest coupling in the family, by design — Section 15) | None — confirmed it does not redefine or override any upstream stage's fachliche (domain) semantics, only wraps identity/provenance/publication concerns around them |

**No unnecessary duplication, no missing central ownership, no overlapping normative authority, and no hidden cross-cutting responsibility were found.** Reproducibility's wide coupling is architecturally necessary (it is, by design, the only document whose job requires referencing every other document's identity) and is not a "God Specification" in the negative sense, because it never asserts fachliche authority over any stage's domain logic (Section 26).

---

## 11. Stage Architecture

Full S0→S8 chain, condition-by-condition:

| Stage | Task | Inputs | Outputs | Owned fields | Error state | Gate state | Reconciliation | Publication effect |
|---|---|---|---|---|---|---|---|---|
| S0/S1 (Source/Normalized) | Ingest, normalize | Raw source | `rcc002.stage.s1-normalized` | Source/normalization fields | `CRITICAL` on missing PK/OHLCV | N/A | S0→S2 reconciliation (Data Validation §17) | Gates S2 |
| S2 (Validated) | Validate, form `quality_gate_pass` | S1 | `rcc002.stage.s2-validated` | Quality/reason-code fields | Row-level invalid; artifact-level quarantine/abort | `quality_gate_pass` | §17 | Gates S3 |
| S3 (Indicators) | Derive indicators | S2 (unchanged) + | `rcc002.stage.s3-indicators` | Indicator/validity fields | `x_valid=false`/`x=null` | N/A (consumes `quality_gate_pass`) | §26.2/§27.7 | Gates S4 |
| S4 (Signals) | Derive signals | S3 (unchanged) + | `rcc002.stage.s4-signals` | Signal/validity fields | `y_valid=false`/`y=null` | N/A (propagates `x_valid`) | §28.2/§29.8 | Gates S5 |
| S5 (Regimes) | Classify regime | S4 (unchanged) + | `rcc002.stage.s5-regimes` | Regime fields | `regime_valid=false`/`UNKNOWN` | Regime validity feeds S6 | §31.5 | Gates S6 |
| S6 (Gates) | Apply trading gate | S5 (unchanged) + | `rcc002.stage.s6-gates` | `data_gate_pass`, `gate_state`, `gate_valid` | `gate_valid=false`/`INVALID` | `GateState` enum | §32.6 | Gates S7 |
| S7 (Labels) | Derive forward returns/labels | S6 (unchanged) + | `rcc002.stage.s7-labels` | Label/horizon fields | Family-scoped `*_valid_h=false` | N/A | §22, §31–35 | Gates S8 |
| S8 (Export) | Assemble, publish views | S7 (unchanged) + | `rcc002.view.*` (6 views) | View-allowlist membership only (no new fields) | Whole-artifact quarantine/abort only | Publication Gate `PASS`/`FAIL`/`PASS_WITH_APPROVED_EXCEPTIONS` (per stage) / dataset-wide checklist (Reproducibility §25) | §18.4 (`S8_rows==S7_rows` + identity/order/manifest/hash), now explicitly named in §25 | Terminal — `published`/`candidate`/quarantined |

Every stage's own owned-field set, read-only upstream fields, permitted/forbidden mutations, and row-count/identity/order invariant were independently re-confirmed present and non-contradictory (this reconstructs, rather than merely cites, the same chain independently verified in `RCC_002_SCR_007_FULL_SCOPE_REPLACEMENT_REVIEW_2026-07-27.md` Section 12 — no discrepancy found on architecture-focused re-derivation).

**S5/S6 co-location assessment** (explicitly requested): Regime (S5, pure classification: `BULL`/`SIDE`/`BEAR`/`UNKNOWN`, no trading semantics) and Gate (S6, trading-permission decision consuming S5's output plus `data_gate_pass`) are architecturally distinct concerns sharing one document. This is confirmed **not** a cohesion violation: §12 (S5 field register) and later sections (S6 field register, gate-state derivation) are cleanly separated within the document, S5 fields are marked read-only inputs to S6's rules, and no S6 rule mutates an S5 field. The co-location is a documentation-organization choice (both concerns sit on the "market context before the trading decision" side of the pipeline), not an architecture defect — equivalent in cleanliness to having them in two separate files.

---

## 12. Data Flow Architecture

```text
Canonical Source Data
    → S1 (normalize)
    → S2 (validate; form quality_gate_pass)
    → S3 (derive indicators; x_valid AND-chain includes quality_gate_pass)
    → S4 (derive signals; y_valid propagates x_valid)
    → S5 (classify regime; regime_valid includes quality_gate_pass check)
    → S6 (apply gate; data_gate_pass = quality_gate_pass; GateState)
    → S7 (derive labels/forward returns; causal boundary — only stage referencing t+1..t+h)
    → S8 (assemble views; positive field-allowlists; S8_rows = S7_rows)
    → Manifest (identity, hashing, lineage)
    → Publication / Quarantine / Abort
```

Checked and confirmed for every arrow above:
- **No unauthorized bypass**: every stage's input schema is version-gated and fail-closed on an unrecognized major version (§6.7-pattern, confirmed present per-document in Regime and Gate, and via Data Pipeline's general §6.4 rule applied to all nine stages) — a stage cannot silently accept data that skipped a predecessor.
- **No backflow into earlier stages**: no specification anywhere grants a later stage (S4 onward) write access to an earlier stage's fields; Row Preservation invariants and "vorgelagerte Felder unverändert" clauses are stated at every boundary (re-confirmed, not merely re-cited, by direct re-reading of each boundary's contract in this review).
- **No hidden mutation**: every stage's field-ownership registry marks exactly one owning stage per field; no field appears in two different stages' "owned fields" columns.
- **No stage processes an artifact it does not own**: S8 views are explicitly scoped as "positive... Feld-Allowlist" per view (Data Pipeline §7.9) — a view may only ever gain fields, never claim ownership of upstream stage logic.
- **No stage requires data produced later**: confirmed by the strict, one-directional Document-Control dependency chain (Section 15) — Data Pipeline has zero upstream normative dependency; each subsequent document depends only on documents earlier in the S0→S8 order.
- **No circular runtime or normative dependency**: confirmed in Section 15.

**Result: the data flow is fully closed, one-directional, and free of bypass, backflow, hidden mutation, or premature-data requirements.**

---

## 13. Ownership Architecture

### Field Ownership Matrix (by field class)

| Field class | Producing stage | Reading stages | Mutating stage | Forbidden mutation | Final ownership | Manifest-relevant |
|---|---|---|---|---|---|---|
| Source fields (OHLCV, PK, `open_time`) | S0/S1 | S2–S8 | None after S1 | Any downstream mutation | S0/S1 (Data Validation) | Yes — source manifest |
| Validation/quality fields (`quality_gate_pass`, reason codes) | S2 | S3–S8 (consumed, e.g. `data_gate_pass=quality_gate_pass`) | None after S2 | Any downstream mutation | S2 (Data Validation) | Yes |
| Indicator fields (`x`, `x_valid`, `x_warmup_complete`, `x_reason_codes`) | S3 | S4 | None after S3 | Any downstream mutation | S3 (Indicator) | Yes |
| Signal fields (`y`, `y_valid`, `y_reason_codes`) | S4 | S5 (indirectly, via regime inputs) | None after S4 | Any downstream mutation | S4 (Signal Transformation) | Yes |
| Regime fields (`regime_raw`, `regime_effective`, `regime_valid`, trend/volatility classes) | S5 | S6 | None after S5 | Any downstream mutation | S5 (Regime and Gate) | Yes |
| Gate fields (`data_gate_pass`, `gate_state`, `gate_valid`) | S6 | S7 (indirectly, not consumed directly by label logic per the causal-isolation rule) | None after S6 | Any downstream mutation | S6 (Regime and Gate) | Yes |
| Label/forward-return fields (`fwd_*`, `label_*`, `barrier_*`) | S7 | S8 (view-gated) | None after S7 | Any downstream mutation; any upstream (S0–S6) reference | S7 (Label and Forward Return) | Yes |
| Quality/reconciliation summary fields | Cross-cutting, aggregated at manifest time | Manifest consumers | Reproducibility (aggregation only, not source mutation) | Redefining an upstream quality determination | Reproducibility (aggregator, not primary owner) | Yes |
| Reproducibility/manifest identity fields (`build_id`, `dataset_id`, hashes, `specification_profile`) | Reproducibility | All (informative) | Reproducibility | Any stage claiming to define these independently | Reproducibility | Yes (this *is* the manifest) |
| Publication/status fields | Reproducibility (dataset-level), each stage (stage-level Gate status) | All | Reproducibility / respective stage | Cross-assignment between stage-level and dataset-level status | Split ownership — INTENTIONAL (see below) | Yes |
| Lineage fields (Dataset/Artifact/Knowledge Lineage) | Reproducibility | All | Reproducibility | Any stage asserting its own independent lineage record | Reproducibility | Yes |
| Error/reason-code fields | Each stage owns its own reason-code namespace/registry | Downstream (read-only) | Owning stage only | Cross-stage reason-code reuse without registry reference | Per-stage | Yes |
| Status fields (Gate Status, `dataset` `status`) | Respective Gate chapter / Reproducibility | All | Owning document only | — | Per-document, clearly split | Yes |

**Classification of the one deliberately split ownership** (Publication/status fields): stage-level Publication Gate status (`PASS`/`FAIL`/`PASS_WITH_APPROVED_EXCEPTIONS`, defined identically in each stage-owning document's own Publication Gate chapter) and dataset-level publication status (`candidate`/`published`, owned by Reproducibility's manifest schema and §25 checklist) are **INTENTIONAL CROSS-CUTTING OWNERSHIP**, not ambiguous or conflicting: a stage's own Gate status answers "may *this stage's* output be published," while Reproducibility's dataset-level status answers "may *the whole assembled dataset* be published," which additionally requires every stage's Gate status plus cross-cutting concerns (manifest completeness, lineage, hashing). No case was found where a stage-level Gate status and the dataset-level status could conflict without one deterministically forcing the other (a single stage `FAIL` blocks the whole dataset per Reproducibility §25's closing sentence: *"Ein einzelnes fehlgeschlagenes Pflichtkriterium blockiert die Veröffentlichung."*).

**No `AMBIGUOUS` or `CONFLICTING` ownership was found anywhere in the family.**

---

## 14. Boundary Contract Assessment

All eight boundaries (Data Pipeline↔Data Validation, Data Validation↔Indicator, Indicator↔Signal Transformation, Signal Transformation↔Regime, Regime↔Gate, Gate↔Label, Label↔Reproducibility, Reproducibility↔Publication) were checked for: who validates, who transforms, who decides, who blocks, who quarantines, who publishes, who logs, who reconciles, who owns error states.

| Boundary | Validates | Transforms | Decides | Blocks | Quarantines | Publishes | Reconciles | Owns errors |
|---|---|---|---|---|---|---|---|---|
| Pipeline↔Validation | Data Validation | — | Data Validation (`quality_gate_pass`) | Data Validation (row-level), Pipeline (build-level via §5.8) | Reproducibility (artifact-level) | — | Data Validation §17 | Data Validation |
| Validation↔Indicator | Indicator (input schema) | Indicator | Indicator (`x_valid`) | Indicator (row-level, via `x_valid=false`) | Reproducibility | — | Indicator §26.2/27.7 | Indicator |
| Indicator↔Signal | Signal Transformation (input schema) | Signal Transformation | Signal Transformation (`y_valid`) | Signal Transformation | Reproducibility | — | Signal Transformation §28.2/29.8 | Signal Transformation |
| Signal↔Regime | Regime and Gate (input schema) | Regime and Gate (S5 classification) | Regime and Gate (`regime_valid`) | Regime and Gate | Reproducibility | — | Regime and Gate §31.5 | Regime and Gate |
| Regime↔Gate | Regime and Gate (same document, S5→S6 internal) | Regime and Gate (S6 decision) | Regime and Gate (`gate_state`) | Regime and Gate (`BLOCK_BOTH` etc.) | Reproducibility | — | Regime and Gate §32.6 | Regime and Gate |
| Gate↔Label | Label (input schema) | Label (forward-return derivation) | Label (`*_valid_h`) | Label (family-scoped invalidity) | Reproducibility | — | Label §22, §31–35 | Label |
| Label↔Reproducibility | Reproducibility (S7 field-ownership check) | — (Reproducibility does not transform label semantics) | Reproducibility (S8 view membership) | Reproducibility (view-level fail-closed rejection) | Reproducibility | Reproducibility | Reproducibility §18.4 | Reproducibility (identity-layer errors only) |
| Reproducibility↔Publication | Reproducibility (§25 checklist) | — | Reproducibility (dataset `published`/`candidate`) | Reproducibility (any single failed criterion) | Reproducibility | Reproducibility | Reproducibility §25 | Reproducibility |

**No boundary was found implementable only by implicit reading** — every "who does X" question above resolves to a specific, named document and, in every case checked, a specific named section.

---

## 15. Dependency Architecture

Directed graph (confirmed via each document's own Document-Control "Übergeordnetes Dokument"/"Direkte Abhängigkeit(en)"/"Primäre Abhängigkeit"/"Fachliche Abhängigkeiten" fields, independently re-read fresh for this review):

```text
Data Pipeline (root — 0 inbound normative dependencies)
  ← Data Validation
  ← Indicator (← Data Validation)
  ← Signal Transformation (← Data Validation, Indicator)
  ← Regime and Gate (← Data Validation, Indicator, Signal Transformation)
  ← Label and Forward Return (← Data Validation, Indicator, Signal Transformation, Regime and Gate)
  ← Reproducibility and Manifest (← Data Validation, Indicator, Signal Transformation, Regime and Gate, Label and Forward Return)
```

This is a strict, linear DAG matching the S0→S8 stage order exactly — **zero cycles**, confirmed by construction (every edge points from a later-numbered stage's owning document back to an earlier one, never forward).

| Edge | Type | Version-pinned? | Status |
|---|---|---|---|
| Every document → Data Pipeline | REQUIRED (normative) | Yes, exact version | Valid, current (post Minor Correction Cycle) |
| Indicator/Signal Transformation/Regime and Gate/Label/Reproducibility → Data Validation | REQUIRED | Yes | Valid, current |
| Signal Transformation/Regime and Gate/Label/Reproducibility → Indicator | REQUIRED | Yes | Valid, current |
| Regime and Gate/Label/Reproducibility → Signal Transformation | REQUIRED | Yes | Valid, current |
| Label/Reproducibility → Regime and Gate | REQUIRED | Yes | Valid, current |
| Reproducibility → Label and Forward Return | REQUIRED | Yes | Valid, current |
| Every document's §19-listed / self-referenced historical-block citations | INFORMATIVE (explicitly, by their own "Version X bewahrt..." framing) | No (intentionally historical) | Valid — correctly excluded from live-dependency status |

No `OPTIONAL`, `REDUNDANT`, or `INVALID` edge was found. No undeclared dependency was found (every cross-document citation traces to a declared Document-Control field). No dependency on a historical document state remains outside the explicitly-labeled historical narrative blocks (independently re-confirmed in `RCC_002_SCR_008_FULL_SCOPE_RE_REVIEW_2026-07-27.md` Section 22, re-verified fresh here via the same full-family grep sweep — zero stale live citations found).

**Reproducibility as cross-cutting specification**: confirmed correctly bound — it depends on all six other documents (widest fan-in) but is depended upon by none, and its own content (Sections 11/18 below) never redefines a stage's domain semantics, only wraps identity/hash/manifest/publication concerns around them. This is the architecturally correct shape for a cross-cutting concern (leaf node in the dependency graph, not embedded mid-chain).

---

## 16. Control Flow and Orchestration

An implementable control flow was derived directly from the specifications' declarative contracts (none of the seven documents state an explicit state-machine diagram; this section constructs one from the fail-closed/abort/quarantine/gate/publication rules scattered across them, and assesses whether that construction is unambiguous):

```text
BUILD_INITIALIZED
  → STAGE_RUNNING (S0 through S8, in strict order)
      per stage:
        contract check fails  → STAGE_FAILED → fail-closed Stage-Abbruch (Regime and Gate §6.7-pattern,
                                                 confirmed present in equivalent form at every stage's own
                                                 "Eingangsablehnung"/abort-condition section)
        contract check passes → STAGE_COMPLETED → next stage
  → (after S8) RECONCILED (§18.4 / §25 reconciliation checks)
  → PUBLICATION_ELIGIBLE (all Publication Gate criteria + §25 checklist PASS or PASS_WITH_APPROVED_EXCEPTIONS)
      → PUBLISHED
  → NOT_PUBLISHED (any FAIL)
  → QUARANTINED (artifact-level defect, independent of build-wide ABORTED)
  → ABORTED (build-wide structural failure, per Data Pipeline §5.8's explicit scoping:
             "Beide [Build-Abbruch und Artefakt-Quarantäne] wirken auf das gesamte Artefakt
             oder den gesamten Build, nicht auf einzelne Zeilen.")
```

Every transition above is normatively traceable to a specific rule (cited above and in Sections 17–18). **STAGE_FAILED → fail-closed abort** is the one transition requiring cross-document confirmation, since Data Pipeline states the general fail-closed principle (§2/§6.4/§7.3.2 area) while each stage-owning document instantiates its own specific abort-condition list (confirmed present in Regime and Gate §6.7, and — independently re-checked here — in equivalent form in Signal Transformation §5.5's nine abort conditions and Indicator's own input-validation section) — this is the same general-principle/specific-instantiation pattern already found architecturally sound for row-count invariants (Section 15).

**Assessment**: the control flow is **fully derivable and internally consistent**, with no state left without a defined normative source. The specification is declarative (contracts and invariants) rather than procedural (no literal `STAGE_RUNNING` enum exists in the text) — an implementer must choose concrete state names, but not invent any new *substantive* transition rule. This is normal for a specification of this kind and is classified `IMPLEMENTABLE WITH LOCAL ASSUMPTIONS` (state-naming only), not a gap (Section 25).

---

## 17. Error Architecture

| Dimension | Finding |
|---|---|
| Fail-closed principle | Stated globally (Data Pipeline) and instantiated per-stage; confirmed present at every stage boundary checked |
| Local stage errors | Row-level (`x_valid`/`y_valid`/`regime_valid`/`*_valid_h` = false) — row retained, never dropped (Row Preservation, Section 11) |
| Global build errors | Structural contract violations (schema/PK/sort/segment) → stage-level fail-closed abort; cascades to whole-build abort per Data Pipeline §5.8's exception clause |
| Recoverable vs. non-recoverable | Row-level invalidity is "recoverable" in the sense that the row remains in the canonical stream and later stages continue; structural contract violations are non-recoverable for that build attempt (abort) |
| Warning vs. error | `PASS_WITH_APPROVED_EXCEPTIONS` is the family's only formal "warning-that-still-blocks-if-severe" mechanism (Section 18, `AIR4-MIN-01`) |
| `quality_gate_pass=false` | Deterministically propagates through every downstream stage's own validity formula (independently re-derived in Section 12; confirmed not just inherited but independently re-checked at Regime level via §7.4's direct `quality_gate_pass=false → regime_raw=UNKNOWN` rule) |
| `data_gate_pass=false` | Unconditionally forces `BLOCK_BOTH`, overriding any profile (§13.3) |
| Stage Gate blocking | Confirmed unconditional and unbypassable at the row/direction level |
| Quarantine | Artifact-level only, never row-level (Section 11) |
| Abort | Build-level only, never row-level |
| Silent degradation | None found — every invalidity path produces an explicit reason code and an explicit `null`/`INVALID` state, never a silently-substituted plausible-looking value |
| Uncontrolled continuation | None found — every stage boundary's contract-violation path is fail-closed |

**Errors are uniformly, unambiguously detected, classified, propagated, logged (via reason codes), and translated into a final build/publication status.** No architecture-level gap found in error handling.

---

## 18. Gate Architecture

Terminology clarified first, since the review order's list ("Data Gate, Quality Gate, Regime Gate, Directional Gate, Publication Gate") does not map one-to-one onto the family's own vocabulary:

- **"Quality Gate"** = `quality_gate_pass`, formed at S2 (Data Validation/Data Pipeline).
- **"Data Gate"** = `data_gate_pass`, formed at S6 and defined as `data_gate_pass = quality_gate_pass` verbatim (Regime and Gate §13.2) — **not** a second, independent gate; it is S6's own re-exposure of the S2 quality determination, by explicit, single-source-of-truth design (§13.2: *"Die einzige normative Wahrheitstabelle lautet..."*).
- **"Regime Gate"** does not exist as a named gate — Regime (S5) is a pure classification stage (no `PASS`/`FAIL`/blocking concept of its own); its output (`regime_valid`, `regime_effective`) is consumed as an *input* to the Directional Gate's profiles, not a gate in its own right.
- **"Directional Gate"** = the S6 `GateState` derivation (`ALLOW_BOTH`/`ALLOW_LONG_ONLY`/`ALLOW_SHORT_ONLY`/`BLOCK_BOTH`/`INVALID`), independently re-confirmed exhaustive over its 2×2-plus-validity input domain (Section 12; re-derived fresh here, matching `RCC_002_SCR_007_FULL_SCOPE_REPLACEMENT_REVIEW_2026-07-27.md` Section 16 exactly).
- **"Publication Gate"** = the per-stage `PASS`/`FAIL`/`PASS_WITH_APPROVED_EXCEPTIONS` chapters (Data Validation §20, Indicator §30, Signal Transformation §32, Regime and Gate §35/36, Label §38) plus Reproducibility's dataset-wide §25 checklist and Data Pipeline's generic §12 catalog.

### Gate Composition Matrix

| Gate | Owning stage/doc | Inputs | Possible outcomes | Priority relative to other gates |
|---|---|---|---|---|
| Quality Gate | S2 / Data Validation | Schema/PK/sort/type/range/segment validity | `true`/`false` | Highest — feeds every downstream gate unconditionally |
| Data Gate | S6 / Regime and Gate | `quality_gate_pass` (verbatim) | `true`/`false` | Equal to Quality Gate by definition (`=`) |
| Directional Gate | S6 / Regime and Gate | `data_gate_pass`, `regime_valid`, `regime_effective`, profile-specific inputs | `ALLOW_BOTH`/`ALLOW_LONG_ONLY`/`ALLOW_SHORT_ONLY`/`BLOCK_BOTH`/`INVALID` | Subordinate to Data Gate — `data_gate_pass=false` unconditionally forces `BLOCK_BOTH` regardless of profile (§13.3) |
| Stage-level Publication Gate | Each stage-owning document | That stage's own criteria list | `PASS`/`FAIL`/`PASS_WITH_APPROVED_EXCEPTIONS` | Each stage's Gate blocks only that stage's own publication; a failure cascades because each stage's own Gate criterion 1 requires the previous stage to already be fully released |
| Dataset-level Publication Gate | Reproducibility §25 | All stage Gates + manifest/lineage/hash completeness | `published`/`candidate` (blocked) | Highest-level — a single failed criterion anywhere blocks the whole dataset, regardless of any individual stage's own `PASS_WITH_APPROVED_EXCEPTIONS` |

**No semantic mixing was found** between these five gate concepts — each has its own owning document/section, its own input set, and its own outcome enum, with priority relationships that are explicit and non-circular (Quality Gate ⊇ Data Gate ⊇ Directional Gate; stage Gates ⊆ dataset Gate). **Long/Short symmetry** was independently re-confirmed structural, not merely asserted (mirrored predicates in the `GATE_TREND_ALIGNED_V1`/`GATE_TREND_STRENGTH_ALIGNED_V1` profiles).

**The one gap found in this architecture**, independently derived through the implementability lens (Section 8 methodology) rather than adopted from SCR-008: the stage-level Publication Gate's `PASS_WITH_APPROVED_EXCEPTIONS` outcome is under-specified as an architectural mechanism, not merely a scientific wording issue — see `AIR4-MIN-01` (Section 33).

---

## 19. Reproducibility Architecture

Independently re-checked: Reproducibility defines Build Identity, Dataset Identity, Schema Identity, Configuration Identity (semantic + physical, separately hashed), Code Identity (`code_provenance`), Environment Identity, Version Identity (now consistent, Section 15), Artifact Identity, Dataset/Artifact/Knowledge Lineage, a four-tier Hash/Byte-Scope ladder (E0–E3), deterministic normalization rules, and rebuild/round-trip test requirements. No central identity component was found missing. `manifest_id`'s circularity avoidance (computed pre-insertion, §5.9) was independently re-confirmed sound (matches `RCC_002_SCR_007_MAJOR_FINDINGS_VERIFICATION_2026-07-27.md` Section 5's finding exactly, re-derived here rather than merely cited).

**Does Reproducibility over-reach into stage-level fachliche ownership?** No — every reproducibility mechanism (hashing, manifest, lineage) operates *on* the outputs of the six stage-owning documents without redefining any of their domain rules; this was specifically re-checked at the one location where the two are closest (the S8 field-ownership registry, owned by Data Pipeline §7.9, merely *referenced* — not redefined — by Reproducibility's manifest-construction guidance).

**Sufficiency for later implementation**: assessed `IMPLEMENTABLE` — every identity component an implementer needs to construct a conforming manifest is present and, since the Minor Correction Cycle, internally version-consistent (Section 15).

---

## 20. Manifest Architecture

The manifest's role is confirmed to be **evidence, not hidden control logic**: §24's example schema and its explicit disclaimer (*"Implementierungen MÜSSEN reale Werte einsetzen"*) frame it as a recorded artifact of what a build did, not a mechanism that itself makes runtime decisions. All required field classes (identity, stage status, gate status, reconciliation, hashes, dependencies, version profile, build result, publication/quarantine/abort status) are present in the §24 schema. §12.3's specification-profile table, now internally consistent (Section 15), feeds the manifest's `specification_profile` array correctly. No contradiction was found between the manifest schema (§24) and the Publication Gate checklist (§25) — every §25 checklist item corresponds to a concept the manifest schema has a field for.

**Assessment: complete, deterministic, canonical, non-contradictory, and architecturally unambiguous to consume** — an implementer reading only §24/§25 could build a conforming manifest consumer without an additional undocumented decision, aside from the one gate-composition nuance noted in Section 18/33.

---

## 21. Publication Architecture

Publication Eligibility (per-stage and dataset-level Gate criteria), Publication Decision (Gate status), Publication Execution (Reproducibility's `published`/`candidate` transition, atomicity requirement in §25), Quarantine (artifact-level), and Build Abort (build-level) are each independently owned and non-overlapping (Section 13). `PASS`, `PASS_WITH_APPROVED_EXCEPTIONS`, `FAIL`, and the dataset-level `NOT PUBLISHED` state are all closed, enumerable outcomes — no "unknown" publication outcome is reachable.

**O-8 independent re-assessment (per explicit instruction not to adopt SCR-008's verdict unchecked):**

SCR-008 classified this as Observation, reasoning that the carve-out's general "non-blocking findings only" clause already forecloses the concern regardless of the enumerated list's completeness — a valid *scientific*-consistency argument (no evidence of an actual divergent scientific result was found). Applying this review's own, distinct implementability standard instead: an engineer tasked with building the `PASS_WITH_APPROVED_EXCEPTIONS` approval workflow needs a **closed, checkable rule** for "is this specific failure type override-eligible," because the approval step is (per the specification's own words) meant to be granted by a human reviewer against a specific, enumerable list of what may *never* be overridden. The specification gives that list, but does not state whether the list is **exhaustive** (anything not named may be considered for override, subject only to the vague "non-blocking" qualifier) or **illustrative** (the list names known-important examples of a broader, not-fully-enumerated "blocking" category). These two readings lead to different, concretely divergent implementations of the exact same approval workflow:
- **Exhaustive reading**: an implementer builds an allowlist/denylist check against exactly the ~6 named categories; a failed Property-Test (criterion 16/18, not in the list) would pass this check and could be waved through by an approver acting in good faith but relying on the specification's own enumerated list as authoritative.
- **Illustrative reading**: an implementer builds a check against "any failed MUST-level Publication Gate criterion," which would correctly catch a failed Property-Test but requires inferring an unwritten general principle rather than following the text as a closed spec.

Both readings are **defensible from the text as written**, and they produce **different software** for the same approval gate — this is exactly the "could two conformant implementations diverge" test this review's own methodology (Section 8) applies, and it resolves differently here than SCR-008's test did, because SCR-008 asked "does this create a wrong *scientific result*" (answer: not directly, since the underlying invariant is still checked by the Gate criterion itself) while this review asks "is the *approval mechanism itself* unambiguously implementable" (answer: no).

**This review classifies this as Minor Finding `AIR4-MIN-01`** (Section 33) — not Major, because: (a) the exception mechanism requires human documentation and approval by design, so this is not a silent/automatic bypass; (b) it affects exactly one narrow mechanism (the exception carve-out), not the Gate's own MUST-level criteria, which remain unambiguous and binding on their own; (c) Reproducibility's own dataset-level §25 gate has *no* such exception mechanism at all and is therefore fully unambiguous, providing a final backstop even if a stage-level exception were mis-granted.

---

## 22. Configuration Architecture

`semantic_build_configuration` and `physical_publication_configuration` are both required to be fully canonicalized and hashed (`canonical_sha256`), with an explicit rule (§6.4-family compatibility rule, plus Reproducibility's `SCR-005-M03` closed finding: *"neue `build_id` und `dataset_id` bei jeder Änderung der semantischen Konfiguration, auch bei zufällig identischem Tabelleninhalt"*) ensuring semantic configuration changes always produce a new identity regardless of output similarity. No hidden default was found — every configuration key is required to be canonicalized (§25: *"jeder wirksame Konfigurationsschlüssel genau einer Klasse zugeordnet"*), and physical (non-semantic) configuration is explicitly barred from affecting logical output (Data Pipeline §8.2: partitioning "darf keine fachliche Semantik verändern"). No stage-vs-cross-cutting configuration conflict was found — physical/semantic classification is itself a single, centrally-owned distinction (Reproducibility).

**Assessment: no hidden default, no un-hashed normative configuration, no stage conflict, no ambiguous priority.**

---

## 23. Partitioning and Scaling Architecture

Serial/partitioned equivalence is required as a MUST-level, Publication-Gate-blocking criterion at every stage where it is relevant (Indicator §22.1/§27.5/§30 crit. 17; Signal Transformation §27.1/§29.8/§32 crit. 10), with explicit checksum-verified state continuity and a hard prohibition on silent fallback (Indicator §22.4). Warm-up, forward-horizon, and tail-row handling are all explicitly defined not to depend on partition boundaries (Row Preservation invariants apply uniformly). Partition-Reconciliation, ordering, and determinism were independently re-confirmed unchanged and sound (Section 12).

**Future scaling assessment**: a future implementation could scale processing (more partitions, different chunk sizes) without breaking any architectural contract, because every relevant invariant is explicitly partition-size-and-count-independent by construction. One pre-existing, non-blocking coverage gap (empty-partition scenario not explicitly named in Indicator §27.5's test list, carried over as O-1) does not threaten this conclusion, since the *architecture* (not merely the *test list*) already requires equivalence for arbitrary partition shapes, including degenerate ones, by the general wording of §22.1.

---

## 24. Schema Architecture

Every stage has its own versioned schema ID (`rcc002.stage.*/x.y.z`) and a compatibility rule (Data Pipeline §6.4: Patch/Minor/Major semantics, independently re-confirmed applied consistently across the family post-Minor-Correction-Cycle, Section 15) governing schema evolution. Field ownership, required/optional/additional/unknown-field handling, and nullability are all explicitly and consistently defined (re-confirmed via the per-stage field-ownership registries, Section 13). Unknown major schema versions are fail-closed rejected at every boundary (Section 17).

**Assessment: schema evolution is controlled and versionable; no architecture gap found.**

---

## 25. Implementation Readiness

| Specification | Inputs/outputs complete? | Error states complete? | Ownership/mutation rules complete? | Tests derivable? | Manifest fields derivable? | Config values derivable? | Classification |
|---|---|---|---|---|---|---|---|
| Data Pipeline | Yes | Yes (general principle) | Yes | Yes | Yes | Yes | **IMPLEMENTABLE** |
| Data Validation | Yes | Yes | Yes | Yes | Yes | Yes | **IMPLEMENTABLE** |
| Indicator | Yes | Yes | Yes | Yes | Yes | Yes | **IMPLEMENTABLE** |
| Signal Transformation | Yes | Yes, except the `AIR4-MIN-01` carve-out nuance | Yes | Yes | Yes | Yes | **IMPLEMENTABLE WITH LOCAL ASSUMPTIONS** (one exception-eligibility decision) |
| Regime and Gate | Yes | Yes | Yes | Yes | Yes | Yes | **IMPLEMENTABLE** |
| Label and Forward Return | Yes | Yes | Yes | Yes | Yes | Yes | **IMPLEMENTABLE** |
| Reproducibility and Manifest | Yes | Yes | Yes | Yes | Yes | Yes | **IMPLEMENTABLE** |

No specification requires an undisclosed programming-language- or library-level choice beyond what the review order excludes from consideration. Six of seven specifications are fully `IMPLEMENTABLE`; Signal Transformation is `IMPLEMENTABLE WITH LOCAL ASSUMPTIONS` solely due to `AIR4-MIN-01` (and, by the same reasoning, Indicator carries the identical latent assumption, though SCR-008 and this review both note it has gone unexercised across three prior review passes without incident — still worth resolving for the same reason).

---

## 26. Test Architecture

Unit, Contract, Stage Boundary, Integration, Determinism, Partition Equivalence, Negative, Schema, Manifest, Rebuild, Failure Propagation, Publication, and Regression test classes were each checked for derivability:

| Test class | Derivable? | Basis |
|---|---|---|
| Unit | Yes | Per-field formulas (§20.1-style AND-chains, discrete truth tables) |
| Contract | Yes | Per-stage input/output schema + field-ownership registries |
| Stage Boundary | Yes | Row-count/identity/order invariants at every boundary |
| Integration | Yes | Full S0→S8 chain with Reproducibility as final consumer |
| Determinism | Yes | Explicit tolerance profiles, serial/partitioned equivalence requirements |
| Partition Equivalence | Yes | Indicator §27.5, Signal Transformation §29.8, explicit test scenario lists |
| Negative | Yes | Section 32 (25 scenarios below), all traced to a normative source |
| Schema | Yes | Versioned schema IDs, fail-closed unknown-version rejection |
| Manifest | Yes | §24/§25 |
| Rebuild | Yes | Reproducibility §18.4 |
| Failure Propagation | Yes | Section 17 |
| Publication | Yes, **except** the exact PASS_WITH_APPROVED_EXCEPTIONS/Property-Test boundary case (`AIR4-MIN-01`) — a test author cannot write an unambiguous oracle for "should this specific exception be grantable" without resolving the exhaustive-vs-illustrative question first | Sections 15/18/21 |
| Regression | Yes | Version-pinned schema/config identities |

**Assessment: every test class is derivable with a clear oracle, with the single, already-identified exception.**

---

## 27. Governance Architecture

Document hierarchy (Data Pipeline as root, six subordinate specifications, Reproducibility as cross-cutting leaf), versioning (now consistent post-Minor-Correction-Cycle, Section 15), change control (Review-Nachweis tables / Reproducibility §29 changelog paragraphs), the Canonical Specification Profile (§12.3, now correct), Review Evidence, Finding Closure (Section 6, independently re-confirmed against SCR-008's own evidence), Approved Exceptions (the mechanism assessed in Section 21), Certification/Release status fields, and Historisierung/Knowledge/Artifact Lineage were all checked.

**Historical vs. current normative separation**: independently re-confirmed clean (Section 15; matches `RCC_002_SCR_008_FULL_SCOPE_RE_REVIEW_2026-07-27.md` Section 18/24's finding, re-derived here rather than merely cited) — every "Version X bewahrt..." block is self-labeled with its own version and does not compete with the current header/§12.3 state for any document.

---

## 28. SCR-008 Consistency Assessment

| SCR-008 claim | Independently re-confirmed? |
|---|---|
| 0 Critical Findings | Confirmed (Section 6; and independently, no Critical Finding found by this review either) |
| 0 Major Findings | Confirmed by SCR-008's own scope (scientific consistency); this review, applying a different (architectural/implementability) standard, finds one new Minor Finding (`AIR4-MIN-01`) that SCR-008 did not have cause to raise under its own standard — this is not a contradiction of SCR-008, since the two reviews apply different, explicitly distinguished tests (Section 21) |
| 0 open Minor Findings (scientific) | Confirmed within SCR-008's own scope |
| 6/6 findings closed | Independently re-confirmed against fresh quotes in Sections 11–21 above, not merely against SCR-008's own claim |
| 0 regressions | Confirmed — this review's own architecture-focused re-derivation (Sections 9–27) found no scientific or architectural regression from the Minor Correction Cycle |
| Both deviations acceptable | Confirmed — independently re-assessed in Sections 15 (Deviation 1: same approved version defect, corrected consistently) and 27 (Deviation 2: historical/current separation intact) |
| O-8 is "only an Observation" | **Not adopted.** This review independently elevates it to Minor Finding `AIR4-MIN-01` under the review order's own instruction that an architecture review may convert a scientific Observation into an architecture Finding *when a concrete implementation-relevant architecture gap exists* — which Section 21 demonstrates it does |
| Four Future Architecture Risks | Confirmed carried over (F-1 through F-3); this review adds one more (`AIR4-FAR-01`, Section 36), specific to the carve-out-list pattern generalizing beyond this one instance |

---

## 29. Architecture Matrices

### A. Stage Responsibility Matrix

| Responsibility | Data Pipeline | Data Validation | Indicator | Signal Transf. | Regime and Gate | Label | Reproducibility |
|---|---|---|---|---|---|---|---|
| Validation | CONTRIBUTOR (global principle) | OWNER | CONSUMER | CONSUMER | CONSUMER | CONSUMER | CONSUMER |
| Transformation | NOT RESPONSIBLE | NOT RESPONSIBLE | OWNER (S3) | OWNER (S4) | CONTRIBUTOR (S5) | NOT RESPONSIBLE | NOT RESPONSIBLE |
| Classification | NOT RESPONSIBLE | NOT RESPONSIBLE | NOT RESPONSIBLE | NOT RESPONSIBLE | OWNER (S5) | NOT RESPONSIBLE | NOT RESPONSIBLE |
| Gating | NOT RESPONSIBLE | NOT RESPONSIBLE | NOT RESPONSIBLE | NOT RESPONSIBLE | OWNER (S6) | NOT RESPONSIBLE | NOT RESPONSIBLE |
| Labeling | NOT RESPONSIBLE | NOT RESPONSIBLE | NOT RESPONSIBLE | NOT RESPONSIBLE | NOT RESPONSIBLE | OWNER | NOT RESPONSIBLE |
| Reconciliation | CONTRIBUTOR (§12/§13 generic criteria) | CONTRIBUTOR (§17) | CONTRIBUTOR (§26.2/27.7) | CONTRIBUTOR (§28.2/29.8) | CONTRIBUTOR (§31.5/32.6) | CONTRIBUTOR (§22/31–35) | OWNER (aggregates all, §18.4) |
| Publication | CONTRIBUTOR (§12 generic) | CONTRIBUTOR (own Gate) | CONTRIBUTOR (own Gate) | CONTRIBUTOR (own Gate) | CONTRIBUTOR (own Gate) | CONTRIBUTOR (own Gate) | OWNER (dataset-level, §25) |
| Manifest | CONTRIBUTOR (defines dataset manifest requirement, §8.5) | CONTRIBUTOR | CONTRIBUTOR | CONTRIBUTOR | CONTRIBUTOR | CONTRIBUTOR | OWNER |
| Error Handling | CONTRIBUTOR (global fail-closed principle) | OWNER (own errors) | OWNER (own errors) | OWNER (own errors) | OWNER (own errors) | OWNER (own errors) | CONTRIBUTOR (aggregation) |
| Configuration | CONTRIBUTOR (partitioning rule §8.2) | NOT RESPONSIBLE | CONTRIBUTOR (numeric tolerance) | CONTRIBUTOR | NOT RESPONSIBLE | NOT RESPONSIBLE | OWNER (semantic/physical config identity) |
| Lineage | NOT RESPONSIBLE | NOT RESPONSIBLE | NOT RESPONSIBLE | NOT RESPONSIBLE | NOT RESPONSIBLE | NOT RESPONSIBLE | OWNER |
| Hashing | NOT RESPONSIBLE | NOT RESPONSIBLE | CONTRIBUTOR (component hashes) | CONTRIBUTOR | NOT RESPONSIBLE | NOT RESPONSIBLE | OWNER |

No `AMBIGUOUS` or `CONFLICT` cell was found.

### B. Field Ownership Matrix

See Section 13 in full.

### C. Stage Boundary Contract Matrix

See Section 11/14 in full.

### D. Dependency Matrix

See Section 15 in full.

### E. Gate Composition Matrix

See Section 18 in full.

### F. Failure Propagation Matrix

| Failure origin | Propagates to | Terminal effect |
|---|---|---|
| S2 `quality_gate_pass=false` | S3 `x_valid=false` → S4 `y_valid=false` → S5 `regime_valid=false`/`UNKNOWN` → S6 `data_gate_pass=false` → `BLOCK_BOTH` | Row retained, all derived fields invalid, trading blocked for that row |
| S3–S6 structural contract violation | Stage-level fail-closed abort | Whole-stage abort, cascades to whole-build abort |
| S7 incomplete horizon (tail rows) | `*_valid_h=false`, fields null per §18.3 | Row retained, label fields null, no build-level effect |
| S8 row-count mismatch | §18.4 test failure | Blocks §25 dataset-level publication |
| Any stage's failed MUST Publication Gate criterion | That stage `FAIL` | Cascades — every downstream stage's own Gate criterion 1 requires the prior stage fully released |

### G. Build-State Transition Matrix

See Section 16 in full (derived state machine).

### H. Publication Decision Matrix

| Stage Gate status | Dataset §25 status | Result |
|---|---|---|
| All stages `PASS` | All checklist items pass | `published` |
| Any stage `PASS_WITH_APPROVED_EXCEPTIONS` (properly scoped) | Remaining checklist items pass | `published` (with documented exception) |
| Any stage `FAIL` | N/A | `candidate`, blocked (§25 closing sentence) |
| Any §25 item fails independent of stage Gates | N/A | `candidate`, blocked |
| Any mandatory artifact quarantined | N/A | Blocked (§25: "kein Pflichtartefakt quarantänisiert") |

### I. Testability Matrix

See Section 26 in full.

### J. Implementation Readiness Matrix

See Section 25 in full.

---

## 30. Architecture Smell Assessment

| Smell | Status | Note |
|---|---|---|
| Circular Dependency | NOT PRESENT | Section 15 |
| Hidden Dependency | NOT PRESENT | All deps explicit in Document-Control |
| Leaky Abstraction | NOT PRESENT | S8 registry centralization in Data Pipeline §7.9 is deliberate, not leaky |
| Shared Mutable Ownership | NOT PRESENT | Section 13 |
| God Specification | PRESENT BUT ACCEPTABLE | Data Pipeline's dual role (global principles + S8 field-ownership registry) is justified by that registry's inherently cross-stage nature |
| Orphan Responsibility | NOT PRESENT | Every responsibility has a clear owner (Matrix A) |
| Duplicate Normative Authority | NOT PRESENT | Section 15/29-D; general-principle/specific-instantiation pattern is intentional, not duplicative |
| Implicit Control Flow | PRESENT BUT ACCEPTABLE | Section 16 — substance is fully derivable, only state-naming is left to the implementer |
| Ambiguous Error Ownership | NOT PRESENT | Section 17 |
| Unbounded Exception Mechanism | **PRESENT** | Section 21/33 — `AIR4-MIN-01` |
| Non-deterministic Configuration | NOT PRESENT | Section 22 |
| Unversioned Contract | NOT PRESENT | Section 15 (post-cycle) |
| Non-testable Requirement | PRESENT BUT ACCEPTABLE | A small number of documentation-completeness checklist items (e.g., "bekannte Einschränkungen dokumentiert") are not machine-testable by nature; carried over from SCR-007, non-blocking |
| Cross-Stage Mutation | NOT PRESENT | Section 12 |
| Publication Bypass | NOT PRESENT (beyond `AIR4-MIN-01`'s narrow exception-approval ambiguity, which requires human sign-off and cannot occur silently) | Section 21 |
| Reconciliation Gap | NOT PRESENT | S7→S8 gap closed (Section 11) |
| Schema Drift | NOT PRESENT | Section 24 |
| Temporal Leakage | NOT PRESENT | S7 causal isolation confirmed quadruple-redundant (unchanged from SCR-007) |
| Stage Ordering Ambiguity | NOT PRESENT | Section 11/16 |
| Historical/Current Norm Conflict | NOT PRESENT | Section 27 |

---

## 31. Negative Architecture Scenario Assessment

| # | Scenario | Expected architecture behavior | Normative source | Unambiguously implementable? |
|---:|---|---|---|---|
| 1 | Stage reads a later-produced field | Prevented — input schemas only ever contain earlier-stage fields | Section 12, Document-Control dependency order | Yes |
| 2 | Stage mutates a foreign field | Prevented — Row Preservation + single-owner field registries | Section 13 | Yes |
| 3 | Data Validation fails, Indicator continues | Controlled: row retained with `quality_gate_pass=false`, Indicator produces only invalid values for it | Section 17 | Yes |
| 4 | Indicator incomplete, Signal still produced | Prevented — `y_valid` propagation forces invalidity | §23.6 | Yes |
| 5 | Regime blocks, Gate allows | Not architecturally meaningful as stated — Regime doesn't block, it classifies; an invalid/`UNKNOWN` regime forces `BLOCK_BOTH` at the Gate, so "Gate allows despite invalid Regime" is prevented | §7.4, §13.3 area | Yes |
| 6 | Gate blocks only one direction | Expected, valid state (`ALLOW_LONG_ONLY`/`ALLOW_SHORT_ONLY`), not a defect | Section 18 | Yes |
| 7 | `quality_gate_pass=false` in an otherwise valid build | Expected/normal — row-level invalidity ≠ build-level failure | §5.8 | Yes |
| 8 | `data_gate_pass=false` with partial data usability | Deterministically forces `BLOCK_BOTH` | §13.3 | Yes |
| 9 | Partition fails | Fail-closed abort, no silent fallback | Indicator §22.4 | Yes |
| 10 | Reconciliation fails | Blocks publication | Section 14/29-F | Yes |
| 11 | Manifest incomplete | Blocks publication | §25 | Yes |
| 12 | Hash mismatch | Detected via E0–E3 ladder; blocks the specific equality tier claimed, does not necessarily block E2-floor publication | §7.4 | Yes |
| 13 | Build reproducible but not publication-eligible | Expected and architecturally orthogonal — reproducibility and Gate criteria are independent concerns | Section 19/21 | Yes |
| 14 | Approved Exception without authorization | Forbidden by the carve-out's own wording; the *authorization record's* structure is only indirectly specified (via the Knowledge Lineage decision-object schema, §12.4) | Section 21 | Implementable with a local assumption (link the exception to a `§12.4`-style decision object) |
| 15 | Approved Exception without manifest evidence | Same as #14 | §24 `reviews`/`quality_summary` fields | Implementable with a local assumption |
| 16 | Historical version read as current dependency | Now prevented — zero stale live citations remain (Section 15) | — | Yes |
| 17 | Schema version and manifest version diverge | Prevented — schema fingerprinting (§7.3/§7.4) | — | Yes |
| 18 | Same data/config produce different artifacts | Prevented — determinism invariants + build/dataset-ID derivation rules | §22 configuration architecture | Yes |
| 19 | Serial and partitioned builds diverge | Prevented, and gate-blocking if it occurs | Section 23 | Yes |
| 20 | Label stage changes row order | Explicitly forbidden | §22 | Yes |
| 21 | S8 publishes despite an upstream abort | Prevented by construction — abort is build-wide, so S8 would never begin; relies on the "whole build" framing logically entailing "no stage proceeds after an abort signal," which is not spelled out as its own explicit rule | §5.8 | Yes, with one implicit-but-clear inference |
| 22 | Quarantine and Publication simultaneously active | Mutually exclusive by construction (§25: "kein Pflichtartefakt quarantänisiert") | §25 | Yes |
| 23 | Unknown build end-state | Prevented — closed enums throughout (Gate Status, dataset status) | Section 18/21 | Yes |
| 24 | Missing Canonical Specification Profile version | Now prevented and actually enforceable — §12.3 is internally consistent for the first time (Section 15) | §12.3 | Yes |
| 25 | Unversioned configuration change | Prevented — `canonical_sha256` hashing required on both configuration classes | Section 22 | Yes |

**23 of 25 scenarios are fully, unambiguously implementable from the text as written. Scenarios 14/15 require one small, reasonable local assumption (tying exception authorization to the existing Knowledge Lineage decision-object schema) rather than representing an unresolved architecture gap; scenario 21 relies on one clear, if implicit, logical inference from the "whole build" framing.** None of these three rises to a Finding on its own; scenarios 14/15 are folded into the broader `AIR4-MIN-01` observation about the exception mechanism's under-specification (Section 21/33).

---

## 32. Critical Findings

None.

---

## 33. Major Findings

None.

---

## 34. Minor Findings

### AIR4-MIN-01 — `PASS_WITH_APPROVED_EXCEPTIONS` carve-out lists do not resolve exhaustive-vs-illustrative ambiguity for Property-Test failures

- **Severity**: Minor
- **Affected documents**: `RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md` §30; `RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md` §32
- **Architecture component**: Publication Gate / Exception-Approval mechanism
- **Quotes**:
  - Indicator §30: *"`PASS_WITH_APPROVED_EXCEPTIONS` darf ausschließlich nicht blockierende, vollständig dokumentierte Berichtsbefunde betreffen. Es darf weder ein ungültiges S2-Feld noch einen regelwidrig gebildeten `x_valid`-Status, einen Schemafehler, einen Segmentfehler, einen nicht endlichen gültigen Wert oder eine fehlgeschlagene Reconciliation überstimmen."* (criterion 16, same section, separately requires: *"Golden-, Schema-, Segment-, Kausalitäts- und Property-Tests bestanden sind"*)
  - Signal Transformation §32: identical pattern, criterion 18 *"Property-Tests bestanden sind"*, carve-out list naming *"Schemafehler... falsche Feldwerte, unzulässige Nullwerte, Segmentfehler, nicht endliche gültige Werte, Rollenverletzungen oder eine fehlgeschlagene Reconciliation"*.
- **Description**: Neither carve-out list names "a failed Property-Test requirement" among its enumerated non-overridable categories, even though each document's own Publication Gate makes passing Property-Tests a MUST-level criterion for that stage's publication. The specification does not state whether the enumerated list is exhaustive (only these categories are non-overridable) or illustrative (these are examples of a broader, implicit "blocking" category that a Property-Test failure would also belong to).
- **Minimal reproducible architecture scenario**: An engineer implements the `PASS_WITH_APPROVED_EXCEPTIONS` approval workflow as a lookup against the literal enumerated list (a reasonable, text-faithful implementation choice). A build with a failed Property-Test (e.g., "`x_valid=true` implies `x_warmup_complete=true`" violated by a coding defect) is then eligible, per this implementation, for human approval as a non-blocking exception — even though the same document's own criterion 16/18 states Property-Tests must have passed for *any* publication, `PASS` or `PASS_WITH_APPROVED_EXCEPTIONS`. A second, equally reasonable implementation treats the list as illustrative and correctly blocks this case. Both implementations are defensible readings of the same text.
- **Impact**: Architecture/implementability gap in the exception-approval mechanism specifically; does not affect the underlying scientific invariants (which remain correctly and separately stated), and does not constitute a silent/automatic bypass, since human documentation and approval are required by the mechanism's own design.
- **Implementation impact**: An implementer must make an undocumented design choice to build this one mechanism; this is the only such gap found across the full seven-document family in this review.
- **Certification impact**: Non-blocking for Internal Certification if resolved before or concurrently with Editorial Pass; does not, by itself, invalidate any other part of the architecture.
- **Minimal recommended correction**: Add one clarifying clause to both carve-out lists, e.g. *"...noch die Verletzung eines beliebigen als MUST formulierten Publication-Gate-Kriteriums dieses Abschnitts überstimmen."* (or equivalent), making explicit that the enumerated list is illustrative of, not a substitute for, the general MUST-criteria set.
- **Severity justification**: Minor, not Major — narrowly scoped to one exception-approval mechanism in two documents; requires a human-approval step to actually manifest (not automatic); every other Publication Gate control (the MUST criteria themselves, the dataset-level §25 gate with no exception mechanism at all) remains unambiguous and provides a backstop.

---

## 35. Observations

- Carried over from SCR-008 (O-1 through O-7, unaffected by this review's architecture-specific lens): empty-partition test-scenario coverage gap (Indicator §27.5); no central Row Identity/Order/Count glossary; discrete/continuous signal anchor-point framing; deferred numeric acceptance thresholds for profile promotion (Regime and Gate §25); absence of a dedicated changelog heading in six of seven documents (partially mitigated by this cycle's new Review-Nachweis rows); non-monotonic-timestamp handling generalized rather than named.
- **New (this review)**: Negative scenarios 14/15 (Section 31) — Approved Exception authorization/manifest-evidence structure is only indirectly derivable via the Knowledge Lineage decision-object schema (§12.4); workable with a reasonable local assumption, not itself elevated to a Finding, but worth an explicit cross-reference from the Publication Gate carve-out to §12.4 in a future editorial pass.
- **New (this review)**: Negative scenario 21 — "no stage proceeds after a build-wide abort" is a clear, safe inference from the "whole build" framing of Build Abort, but is never stated as its own explicit rule; a future editorial pass could state it directly for reader clarity.

---

## 36. Positive Findings

- **P-1**: The dependency graph is a strict, verifiable DAG with zero cycles and zero undeclared edges, now (post Minor Correction Cycle) fully version-consistent for the first time in the project's documented history.
- **P-2**: Field ownership is unambiguous everywhere except one deliberately and correctly split case (stage-level vs. dataset-level publication status), which is architecturally sound cross-cutting ownership, not a conflict.
- **P-3**: The fail-closed error architecture is uniform, redundant, and independently re-derivable at every stage boundary without gaps.
- **P-4**: The S7→S8 boundary, once a genuine architecture gap (`AIR3-M1`), is now closed with an explicit invariant (§8.7.1), an explicit test (§18.4), and — new in this cycle — an explicit dataset-level Publication Gate checklist reference (§25), giving it stronger closure than the equivalent mechanisms in Indicator/Signal Transformation (Section 18/21).
- **P-5**: Reproducibility's cross-cutting role is architecturally correct in shape (leaf node, wide fan-in, zero fan-out, no fachliche override of any stage) — a textbook-clean placement for a cross-cutting identity/provenance concern.
- **P-6**: 23 of 25 negative architecture scenarios are fully and unambiguously implementable from the specification text alone, with the remaining two requiring only a small, reasonable local assumption rather than an unresolved gap.

---

## 37. Future Architecture Risks

- **F-1** (carried over): row-count invariant replication pattern (general principle + per-boundary instantiation) remains a latent drift risk if not disciplined in future edits.
- **F-2** (carried over): a future eighth stage or new S8 view has no enforcement mechanism beyond reviewer diligence to gain its own row-count invariant and Publication Gate item.
- **F-3** (carried over): coincidental section-number collisions remain a latent cross-reference risk.
- **`AIR4-FAR-01`** (new): the `PASS_WITH_APPROVED_EXCEPTIONS` carve-out-list pattern underlying `AIR4-MIN-01` is a *generalizable* risk, not unique to Property-Tests — any future new Publication Gate criterion added to Indicator or Signal Transformation (or, by the same pattern, to Data Validation/Regime and Gate/Label's own Publication Gate chapters, not yet checked against this specific question) risks the same silent exhaustive-vs-illustrative ambiguity unless the carve-out list is either made explicitly non-exhaustive (recommended fix in `AIR4-MIN-01`) or is disciplined to grow in lockstep with every new MUST criterion.

---

## 38. Regression Assessment

No architectural regression was found. The Minor Correction Cycle's 18 changes (version metadata, dependency citations, one wording clarification, two additive checklist items) touched zero ownership boundaries, zero control-flow rules, zero gate-composition logic, and zero dependency-graph edges beyond correcting their version labels. The new Signal Transformation criterion 18 and Reproducibility §25 checklist item are both purely additive AND-terms to already-conjunctive gate conditions (Section 20), verified not to create any new unreachable, double-defined, or conflicting state.

**Architectural regressions detected: 0.**

---

## 39. Certification Impact

Zero Critical and zero Major architecture findings. One Minor Finding (`AIR4-MIN-01`), narrowly scoped, human-approval-gated, and trivially correctable with a one-sentence clarification in two documents. No unresolved ownership conflict, no control-flow ambiguity in the core pipeline, no circular dependency, no publication-bypass vector beyond the bounded one already discussed. Internal Certification is not blocked by any finding of this review on architectural grounds, provided `AIR4-MIN-01` is tracked and resolved at or before Editorial Pass.

---

## 40. Final Verdict

```text
PASS WITH MINOR CORRECTIONS
```

Justification: zero Critical Findings, zero Major Findings, exactly one new, narrowly-scoped Minor Finding (`AIR4-MIN-01`) that does not impair the core architecture's implementability or the certification-readiness of any other component.

---

## 41. Internal-Certification Recommendation

```text
RECOMMENDED FOR INTERNAL CERTIFICATION AFTER MINOR CORRECTIONS
```

---

## 42. Required Next Actions

1. Resolve `AIR4-MIN-01`: add an explicit "any MUST-level Publication Gate criterion" clause to the `PASS_WITH_APPROVED_EXCEPTIONS` carve-out lists in Indicator §30 and Signal Transformation §32.
2. Optional, non-blocking: address the two carried-over Observations (O-1 empty-partition test coverage; the Section 35 cross-reference suggestions) at the next editorial opportunity.
3. Optional, non-blocking, forward-looking: adopt a standing rule (per `AIR4-FAR-01`) that any future new Publication Gate criterion in any document must be accompanied by a review of that document's own carve-out list.
4. Proceed to Editorial Pass (which may bundle the `AIR4-MIN-01` correction), then Internal Certification, per the sequence already recorded in Reproducibility §29.
5. No bundle/manifest regeneration is required based on this review's findings alone unless `AIR4-MIN-01` is corrected, in which case the standard regenerate/rehash/round-trip sequence (already exercised twice in this project's history) applies.

---

## 43. Residual Uncertainty

- This review constructs an implementable control-flow/state-machine model (Section 16) from declarative contracts that do not themselves name explicit states; the substance of every transition is normatively traceable, but the specific state names used in this report are this review's own reasonable construction, not a literal quotation — a different, equally valid implementation could choose different names for the same states without any architectural disagreement.
- The `AIR4-MIN-01` finding reflects this review's own considered judgment that an implementability standard, distinct from and stricter than SCR-008's scientific-consistency standard, is the correct one to apply to an exception-approval mechanism; a governance authority could reasonably conclude the general "non-blocking only" clause is sufficient as written and decline to treat this as a Finding requiring correction — this review documents its reasoning rather than asserting the point beyond debate.
- No implementation of RCC-002 exists in this repository; all findings are specification-level, and the negative-scenario "implementability" judgments (Section 31) are necessarily projections onto a not-yet-built system, not observations of actual runtime behavior.
- This review does not re-derive the full scientific-consistency substrate from zero (it treats SCR-007/SCR-008's independently-derived scientific findings as evidence, per the review order's own instruction); a hypothetical future review applying yet a third, different lens could still find something neither the scientific nor the architectural lens was positioned to catch.

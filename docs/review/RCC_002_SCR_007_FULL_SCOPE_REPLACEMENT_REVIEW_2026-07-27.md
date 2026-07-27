# RCC-002-SCR-007 — Full-Scope Replacement Scientific Consistency Review

## 1. Document Control

| Field | Value |
|---|---|
| Document Class | Full-Scope Replacement Scientific Consistency Review |
| Review ID | `RCC-002-SCR-007` |
| Review Type | Full-Scope Replacement Scientific Consistency Review |
| Title | Full-Scope Replacement Scientific Consistency Review — RCC-002 Specification Family |
| Date | 2026-07-27 |
| Status | Completed — Verdict: **FAIL** |
| Reviewed Substrate | `docs/review/RCC_002_C1_CORRECTED_FULL_SPEC_BUNDLE_2026-07-25.md` (SHA-256 `18faca1d09411eb7c5b440833c8cc7fcac2a6f1870669f961653412163435198`) |
| Replaces (scientific trust function of) | `docs/review/RCC_002_SCR_006_FINDINGS_2026-07-24.md` |
| Storage Location | `docs/review/RCC_002_SCR_007_FULL_SCOPE_REPLACEMENT_REVIEW_2026-07-27.md` |
| Evidence File | `docs/review/evidence/RCC_002_SCR_007_REVIEW_EVIDENCE_2026-07-27.json` |
| Working Mode | Read-only review. No specification file, bundle, manifest, or generator was modified. No commit was created. |
| Independence | Findings in this review are derived directly from the current, hash-verified bundle text and from the seven canonical source files under `docs/specifications/`, which were independently confirmed byte-identical to the bundle's embedded copies via hash comparison and a live generator round-trip. Prior SCR/AIR/C1/C2/Gemini documents were used only to identify candidate risk areas (per the review's own mandatory methodology); no prior verdict was accepted without independent re-derivation from the current text. |

No files were changed and no commit was created, with the exception of this report and its evidence file.

---

## 2. Executive Summary

Input control fully passed: the bundle, manifest, pre-certification status document, and file inventory all independently re-hash to their stated SHA-256 values, with matching line/byte counts, and the bundle generator (`scripts/build_rcc002_spec_bundle.py`) reproduces the bundle byte-for-byte in a temporary round-trip test. The bundle contains all seven expected specifications, exactly once each, in the order and with the versions stated in the manifest.

The scientific and architectural core of the RCC-002 specification family is sound. Under adversarial, quote-anchored re-derivation across all seven documents, the Canonical Row Preservation Principle (Data Pipeline §5.8) and its per-boundary realizations (`Sn_rows = Sn-1_rows` at every stage from S2→S3 through S7→S8) hold consistently, with zero contradictions found. The `quality_gate_pass`/`data_gate_pass`/gate-state chain is deterministic, exhaustively defined, and fail-closed. Look-ahead/leakage protection at S7 is unusually strong (quadruple-redundant). Gemini MAJOR-001 is independently re-confirmed as correctly rejected.

However, this review finds **three confirmed Major Findings**, all in the reproducibility/versioning domain rather than the core row-preservation/signal architecture: (1) the S7→S8 row-preservation invariant that Architecture Integrity Review AIR-003 required to be added to *both* Data Pipeline §7.9 and the Reproducibility specification was in fact added only to the latter — Data Pipeline's own stage-contract catalog (§6.1), which itself mandates a "Zeilenzahl-Invariante" for every one of its nine explicitly listed stages including S8_EXPORT, still lacks one for S8; (2) the Reproducibility specification's own "kanonisches Spezifikationsprofil" table (§12.3) is stale by one to two generations and self-contradicts the same document's own version field; and (3) the current correction cycle added new normative content (a new invariant, a new mandatory test, five new cross-references) across six of the seven documents without incrementing a single version number anywhere in the family, and left all six dependent documents' own metadata still citing the pre-C1 versions of their upstream dependencies — reproducing, inside the very cycle that fixed C1, the same unversioned/under-tracked-change failure pattern that produced C1 and contributed to the ambiguity underlying C2.

Per the review's mandatory verdict rules, the presence of confirmed Major Findings requires **FAIL**. This is consistent with, and independently confirms from a different methodology, the RCC-002 Pre-Certification Status document's own conclusion that Editorial Pass and Internal Certification remain blocked pending a full-scope replacement review.

---

## 3. Review Identity and Replacement Function

This review (`RCC-002-SCR-007`) replaces the scientific trust function of `RCC_002_SCR_006_FINDINGS_2026-07-24.md`. SCR-006 remains as a historical document but, per the C2 lineage investigation, cannot be treated as a byte-verified review of the bundle currently present in the repository (its stated package hash, `33aac77f...`, does not match any bundle reachable in Git history — see Section 31).

SCR-007 independently and completely re-examines the entire current RCC-002 specification family against the exact hash-secured bundle named above. No prior SCR, AIR, C1, C2, or Gemini result was accepted as proof of correctness; each was used, at most, to identify a candidate risk area, and every such candidate was independently re-derived from the current bundle/source text before being confirmed, narrowed, or rejected in this review.

---

## 4. Scope

Full specification family (seven documents), embedded in the bundle in this order:

1. Data Pipeline Specification (`RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`, v0.7.1)
2. Data Validation Specification (`RCC_002_DATA_VALIDATION_2026-07-23.md`, v0.4.1)
3. Indicator Specification (`RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md`, v0.4.1)
4. Signal Transformation Specification (`RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md`, v0.4.0)
5. Regime and Gate Specification (`RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md`, v0.5.0)
6. Label and Forward Return Specification (`RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md`, v0.4.0)
7. Reproducibility and Manifest Specification (`RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md`, v0.6.0)

All seven were read in full (not excerpted) directly from `docs/specifications/`, which were independently confirmed byte-identical to their bundle-embedded counterparts (Section 6/7). The individual documents were used as the normative evaluation basis, as permitted by the review order (they are byte-identical to the bundle); the bundle itself remains the authoritative hash-anchored substrate.

Out of scope: implementing any fix, modifying any specification, modifying the bundle/manifest/generator, and any Architecture Integrity Review content (a separate, not-yet-conducted full-scope replacement AIR is required per the Pre-Certification Status document).

---

## 5. Reviewed Substrate

| Artifact | Path | Lines | Bytes | SHA-256 |
|---|---|---:|---:|---|
| Bundle | `docs/review/RCC_002_C1_CORRECTED_FULL_SPEC_BUNDLE_2026-07-25.md` | 13,876 | 489,881 | `18faca1d09411eb7c5b440833c8cc7fcac2a6f1870669f961653412163435198` |
| Manifest | `docs/review/RCC_002_C1_CORRECTED_BUNDLE_MANIFEST_2026-07-25.md` | — | — | `3d37c7cb0f87ef93900c6456d8c5c38bbad6f895d9381c2da6eddb9029de64e0` |
| Pre-Certification Status | `docs/review/RCC_002_PRE_CERTIFICATION_STATUS_2026-07-27.md` | — | — | `ec88d121b64b896558326b7ef46c3513f837bad3ee771c74e08c5ba14d4ae0aa` |
| Pre-Certification Inventory | `docs/review/evidence/RCC_002_PRE_CERTIFICATION_FILE_INVENTORY_2026-07-27.json` | — | — | `380bfcd520d2fcaf8e0822dc88bc370cd3b4acf204d399a68e003994d95be9e9` |
| Generator | `scripts/build_rcc002_spec_bundle.py` | — | — | (not separately hash-pinned by the review order; content independently read and analyzed, see Section 7 and Section 18) |

---

## 6. Independent Hash Verification

All four mandatory hashes, plus the bundle's line and byte counts, were independently recomputed with `sha256sum`/`wc` against the working tree (not copied from any prior document) and compared to the review order's stated values:

| Artifact | Expected SHA-256 | Actual SHA-256 | Match |
|---|---|---|---|
| Bundle | `18faca1d09411eb7c5b440833c8cc7fcac2a6f1870669f961653412163435198` | `18faca1d09411eb7c5b440833c8cc7fcac2a6f1870669f961653412163435198` | ✅ |
| Manifest | `3d37c7cb0f87ef93900c6456d8c5c38bbad6f895d9381c2da6eddb9029de64e0` | `3d37c7cb0f87ef93900c6456d8c5c38bbad6f895d9381c2da6eddb9029de64e0` | ✅ |
| Status document | `ec88d121b64b896558326b7ef46c3513f837bad3ee771c74e08c5ba14d4ae0aa` | `ec88d121b64b896558326b7ef46c3513f837bad3ee771c74e08c5ba14d4ae0aa` | ✅ |
| Inventory | `380bfcd520d2fcaf8e0822dc88bc370cd3b4acf204d399a68e003994d95be9e9` | `380bfcd520d2fcaf8e0822dc88bc370cd3b4acf204d399a68e003994d95be9e9` | ✅ |

| Metric | Expected | Actual | Match |
|---|---:|---:|---|
| Bundle lines | 13,876 | 13,876 | ✅ |
| Bundle bytes | 489,881 | 489,881 | ✅ |

Both hash string lengths were independently confirmed to be valid 64-character hexadecimal SHA-256 digests (not truncated or malformed).

Additionally, each of the seven canonical source files under `docs/specifications/` was independently re-hashed and its line/byte count recomputed; all seven match the manifest's per-file table (§1) exactly, including versions, and the bundle's seven `## Quelldatei:` embedding markers appear in the manifest's stated order with no duplicates and no omissions (verified via `grep -n "^# Eingebettetes Dokument"` / `"^## Quelldatei:"`, seven matched pairs, sequential "N von 7" labels 1 through 7).

**Result: input control items 1–7 fully passed. No discrepancy found.**

---

## 7. Round-Trip Verification

The generator was executed against a temporary output path with the exact command recorded in the manifest (§5):

```bash
python3 scripts/build_rcc002_spec_bundle.py \
  --title "RCC-002 C1 Corrected Full Specification Bundle" \
  --korrekturstand "C1-Corrected Draft – full re-review pending (Row Preservation harmonization S2-S7 [C1] + S7-S8 explicit invariant and cross-references [post-AIR-003]; patch versions 0.7.1/0.4.1/0.4.1 unchanged)" \
  --output <temp-file>
```

Result: the temporary output was **13,876 lines / 489,881 bytes**, SHA-256 `18faca1d09411eb7c5b440833c8cc7fcac2a6f1870669f961653412163435198` — an exact match to the reviewed bundle. `diff` between the temporary file and the reviewed bundle reported **no differences** ("IDENTICAL"). The temporary file was deleted after verification; no artifact of this test remains in the repository.

**Result: input control items 8–10 fully passed — the round-trip is byte-exact.**

---

## 8. Methodology

1. Mandatory input control (Sections 6–7) performed first and independently, before any scientific judgment was formed.
2. Prior SCR/AIR/C1/C2/Gemini documents (`RCC_002_C1_SCIENTIFIC_CONSISTENCY_REVIEW_2026-07-25.md`, `RCC_002_AIR_003_C1_ARCHITECTURE_REVIEW_2026-07-25.md`, `RCC_002_GEMINI_MAJOR_001_VERIFICATION_2026-07-25.md`, `RCC_002_PRE_CERTIFICATION_STATUS_2026-07-27.md`) were read once, solely to extract a candidate risk-area list (per the review order's explicit instruction that these may only be used to identify risk areas, never as proof).
3. The seven canonical specifications were partitioned into four independent, quote-anchored deep-dive analyses (Data Pipeline+Data Validation; Indicator+Signal Transformation; Regime and Gate+Label and Forward Return; Reproducibility and Manifest+cross-document versioning), each performed as a full read of the assigned documents with adversarial, falsification-oriented instructions and an explicit mandate to re-derive every candidate risk area from the current text rather than trust the prior verdict.
4. The coordinating reviewer (this document's author) independently re-verified, by direct `grep`/`sed` inspection of the actual source files, every claim underlying a proposed Major Finding, before accepting it into this report. Quotes below are the actual verbatim text found in the current, hash-verified specification files, not text carried over from prior review documents.
5. Findings were classified using exactly the five-tier taxonomy mandated by the review order (Critical / Major / Minor / Observation / Positive Finding / Future Architecture Risk), each requiring a concrete quote, a minimal reproducible counterexample or scenario, and a certification-impact statement.
6. The final verdict follows mechanically from the confirmed finding counts per the review order's mandatory rule.

---

## 9. Specification-Family Overview

| # | Document | Version | Lines | Bytes | Primary Concern |
|---:|---|---|---:|---:|---|
| 1 | Data Pipeline | 0.7.1 | 2,592 | 134,284 | Global principles, all nine stage contracts (S0–S8), Publication Gate catalog |
| 2 | Data Validation | 0.4.1 | 1,381 | 46,721 | Source→S2 validity, `quality_gate_pass` formation, quarantine/abort semantics |
| 3 | Indicator | 0.4.1 | 1,741 | 50,753 | S2→S3, warm-up/recursion/partition equivalence, `x_valid` |
| 4 | Signal Transformation | 0.4.0 | 1,663 | 52,988 | S3→S4, discrete/continuous signal derivation, truth tables |
| 5 | Regime and Gate | 0.5.0 | 2,215 | 68,119 | S4→S5, S5→S6, gate-state truth table, priority rules |
| 6 | Label and Forward Return | 0.4.0 | 2,015 | 59,993 | S6→S7, forward returns, leakage isolation |
| 7 | Reproducibility and Manifest | 0.6.0 | 2,202 | 74,822 | S7→S8, manifest/hash identity, publication gate, versioning |

The nine canonical pipeline stages (S0 through S8) are defined once, centrally, in Data Pipeline §6 ("Kanonische Stufenliste") and consumed consistently by name in every downstream document; no stage-naming drift was found by any of the four deep-dive analyses.

---

## 10. Ontology and Terminology Review

- **Row Identity / Row Order / Row Count** are used consistently across all seven documents but are never given one central glossary definition; each document operationalizes them via its own primary-key/sort-contract/row-count-equation language rather than referencing a single canonical definition anchor in Data Pipeline §2 (which defines only the RFC-2119 keyword set). This is a cross-document ontology gap — not a contradiction, since usage is consistent, but a latent maintainability risk (Observation, Section 26 O-1).
- **`quality_gate_pass`** (formed at S2) and **`data_gate_pass`** (S6) are cleanly and consistently distinguished throughout; Regime and Gate §13.2 states explicitly: *"Die einzige normative Wahrheitstabelle lautet"* for the `data_gate_pass` derivation, and confirms `data_gate_pass = quality_gate_pass` for every schema/key/sort/segment-valid row — verified as the single source of truth, with no duplicate or conflicting table found elsewhere.
- **"Kanonisch" vs. "gültig" (valid)** are explicitly and repeatedly separated: Data Pipeline §5.8 states *"`quality_gate_pass` bestimmt die semantische Verwendbarkeit einer Zeile, nicht ihre kanonische Existenz."* This distinction is never conflated in any of the four deep-dive analyses.
- **RFC-2119 keyword framework** (Data Pipeline §2) formally defines `MUST/MUST NOT/SHOULD/SHOULD NOT/MAY`, but the document's own body uses these exact keywords only twice each; normative force in Data Pipeline is instead carried almost entirely by German modal verbs ("muss", "darf nicht", "dürfen") with no explicit equivalence statement between the two systems. Data Validation, by contrast, uses `MUST` 31 times. This is a genuine, quotable terminology-consistency gap (Minor, Section 25 m-05).
- **`impute_flag`**: this term, named explicitly in the review order's edge-case list (items 12–13), does not exist anywhere in the Indicator or Signal Transformation specifications (`grep -i impute` → zero hits in both). The functional equivalent is the `x_valid`/`x_warmup_complete`/`x_reason_codes` triple together with `quality_gate_pass`. This is not a defect — the family simply does not use this vocabulary — but is recorded here so the edge-case section below is read correctly against the actual terminology in use.
- **Label validity**: Label and Forward Return §18.3 explicitly and deliberately rejects a single global `label_valid`: *"Ein globales `label_valid` oder `label_valid_h` ist unzulässig, weil es unterschiedliche Familienvoraussetzungen verdecken würde."* — a well-justified, intentional ontological choice, not an omission.

---

## 11. Global Invariant Review

The Canonical Row Preservation Principle, Data Pipeline §5.8, quoted in full:

> "Jede Zeile, die in die kanonische Pipeline aufgenommen wurde, muss ihre kanonische Row Identity über alle nachgelagerten Stufen hinweg bewahren. Pipeline-Stufen dürfen kanonische Zeilen aufgrund von `quality_gate_pass=false` weder stillschweigend entfernen noch unterdrücken, duplizieren, zusammenführen oder umordnen. `quality_gate_pass` bestimmt die semantische Verwendbarkeit einer Zeile, nicht ihre kanonische Existenz. Zeilen mit `quality_gate_pass=false` müssen im kanonischen Artefakt verbleiben und werden durch deterministische fail-closed Zustände repräsentiert. Zulässige Reaktionen sind insbesondere: ungültige oder Null-Indikatorwerte; ungültige Signalwerte; nachgelagerte Gate-Zustände wie `BLOCK_BOTH`. Eine Abweichung von der Row Preservation ist ausschließlich durch einen ausdrücklich normierten vollständigen Build-Abbruch oder eine Artefakt-Quarantäne zulässig. Beide wirken auf das gesamte Artefakt oder den gesamten Build, nicht auf einzelne Zeilen. Publication Gates regeln die Veröffentlichbarkeit und semantische Gültigkeit abgeleiteter Werte. Sie dürfen nicht implizit als Row-Deletion-Regeln ausgelegt werden."

This principle is realized as an explicit row-count equation at every stage boundary except one:

| Boundary | Invariant | Location |
|---|---|---|
| S2→S3 | `S3_rows = S2_rows` | Indicator §4.5, §26.2, §27.7, §30 crit. 8 |
| S3→S4 | `S4_rows = S3_rows` | Signal Transformation §28.2, §29.8, §32 crit. 8 |
| S4→S5 | `S5_rows = S4_rows` | Regime and Gate §30 |
| S5→S6 | `S6_rows = S5_rows` | Regime and Gate §30 |
| S6→S7 | `S7_rows = S6_rows` (+ PK, PK order, segment ID) | Label §22 |
| **S7→S8** | `S8_rows = S7_rows` (per view) | **Reproducibility §8.7.1 only** — absent from Data Pipeline §7.9/§12 |

Build Abort and Artifact Quarantine are consistently scoped to the whole artifact/build, never to individual rows, at every location checked (Data Pipeline §5.8; Reproducibility §8.7.1's own exception clause; no row-level quarantine mechanism found in Regime and Gate or Label). No case was found, across any of the four deep-dive analyses, in which an invalid row is silently dropped rather than retained-and-flagged, and no case was found in which a row is simultaneously "valid" and "blocked" in a way that lacks a defined successor state.

**Confirmed gap**: Data Pipeline §6.1 ("Verbindliche Stufenverträge") states, for all nine explicitly listed stages including `S8_EXPORT`, that *"Jede Stufe muss definieren: ... Zeilenzahl-Invariante; ..."*. Data Pipeline's own §7.9 (the S8_EXPORT stage contract) contains **zero** occurrences of "Zeilenzahl", "S8_rows", or "S7_rows" (independently re-verified via `grep` against the current file — see Section 22 / Finding SCR7-MAJ-01). The invariant exists, but only in a different document (Reproducibility §8.7.1), not in the document whose own rule requires every stage — including S8 — to carry one.

Determinism, build-reproducibility, and manifest-reproducibility invariants are stated with matching numeric tolerance profiles (`1e-12` absolute / `1e-10` relative) in both Indicator and Signal Transformation, and are gated as non-overridable Publication Gate criteria in every stage-level Publication Gate chapter found (Data Validation §20, Indicator §30, Signal Transformation §32, Regime and Gate §35/36, Label §38).

---

## 12. Stage-by-Stage Review

**Source/Input → S2** (Data Pipeline §7.1–§7.3; Data Validation §5–§15): the S0 source-manifest field table and the `quality_gate_pass` truth-condition bullet list are stated **byte-identically** in both documents (verified by direct text comparison, not merely absence of contradiction). Duplicate primary keys are fully disposed of: identical duplicates may be deterministically collapsed with lineage retention (`DV_DUPLICATE_IDENTICAL_COLLAPSED`); conflicting duplicates are `CRITICAL` and abort the build absent an approved deterministic priority rule (Data Validation §10, lines 460–505). Non-monotonic timestamps are handled via a deterministic re-sort with `source_row_id` preserving original arrival order (§8.5) rather than named as their own anomaly class — assessed as benign (Observation O-6), since sorting is lossless and idempotent and conflicting-duplicate timestamps are separately and explicitly covered.

**S2→S3** (Indicator): input state `rcc002.stage.s2-validated/1.0.0`, all S2 fields carried unchanged. `quality_gate_pass=false` rows remain canonical; §4.3 states explicitly: *"Zeilen mit `quality_gate_pass=false` bleiben Teil des kanonischen Datenstroms und des kanonischen S3-Artefakts; für sie werden keine gültigen Indikatorwerte erzeugt und keine Indikatorwerte als gültig veröffentlicht. Row Identity, Zeilenreihenfolge und `S3_rows = S2_rows` bleiben davon unberührt."* The `x_valid` formula (§20.1) mechanistically enforces this by ANDing `quality_gate_pass` into validity: *"Für eine Zeile mit `quality_gate_pass=false` gilt für jedes Indikatorfeld `x_warmup_complete=false`, `x_valid=false` und `x=null`."* Recursive indicators re-seed fully at every segment boundary (§21.4); partitioned computation is bound by a hard serial-equivalence requirement (§22.1) plus checksum-verified, fail-closed-on-mismatch state continuity (§22.4: *"Bei einem kanonischen Fortsetzungsbuild wird andernfalls abgebrochen... Ein stiller Fallback ist unzulässig."*).

**S3→S4** (Signal Transformation): input schema validated with 9 explicit fail-closed abort conditions (§5.5) before any transformation runs. The discrete rule matrix (§20) is exhaustive over its entire domain, with threshold equality uniformly resolved to the neutral/lower-severity branch (RSI 30/70→0, Bollinger touch→0, Stochastic 20/80→0, CCI ±100→0, MFI 20/80→0, MACD hist=0→0, ROC=0→0, ADX=25→0). Validity propagation (§23.6) is explicit: *"Ist ein erforderlicher S3-Indikator ungültig, ist die abhängige S4-Transformation ebenfalls ungültig... Ein nachgelagerter gültiger numerischer Ausdruck darf einen ungültigen Inputstatus nicht verdecken."*

**S4→S5 / S5→S6** (Regime and Gate): both row-count boundaries are stated **separately**, not conflated into one invariant (§30). The `GateState` enum (`ALLOW_BOTH, ALLOW_LONG_ONLY, ALLOW_SHORT_ONLY, BLOCK_BOTH, INVALID`) is derived by a fixed, exhaustive rule (§18.4) with an explicit, absolute-priority `data_gate_pass` override (§13.3: *"Dies gilt unabhängig vom gewählten Richtungs-Gate."*). Structural-contract failures are explicitly barred from being serialized as a row value (§6.7: *"Ein stageweiter Vertragsfehler wird nicht als zeilenweises `UNKNOWN` oder `INVALID` weitergeführt, sondern führt zum fail-closed Abbruch der Stufe."*).

**S6→S7** (Label and Forward Return): §22 states the S7 row/PK/PK-order/segment-ID invariant together with an explicit, correctly-targeted back-reference to Data Pipeline §5.8. Causal isolation is unusually strong: S7 is the only stage permitted to reference `t+1..t+h` (§2.1), enforced redundantly via naming convention, field-ownership/leakage-class metadata (§36.3), a per-field SHA-256'd allowlist per view (§26.1), and mandatory negative-injection tests for every registered field (§26.4/§34.4) — a quadruple-redundant falsifiable control (Positive Finding P-3).

**S7→S8** (Reproducibility §8.7.1, quoted in full):

> "Für jedes erfolgreich erzeugte kanonische S8-View-Artefakt MUSS gelten: S8_rows = S7_rows — je View, bezogen auf den vollständigen kanonischen Primärschlüssel (market_type, symbol, interval, open_time) und, bei unkonsolidierten Multi-Provider-Daten, zusätzlich provider. Row Identity MUSS vollständig erhalten bleiben. Row Order MUSS vollständig erhalten bleiben. Export-, Manifest-, Hash- und Reproduzierbarkeitsprozesse DÜRFEN keine kanonischen Zeilen: entfernen, zusammenführen, duplizieren, umordnen. Dies konkretisiert für S8 das kanonische Row-Preservation-Prinzip aus RCC_002_DATA_PIPELINE_SPECIFICATION §5.8 ... Die einzige zulässige Ausnahme von dieser Zeilenerhaltung ist ein ausdrücklich normierter vollständiger Build-Abbruch oder eine Artefakt-Quarantäne. Beide wirken auf das gesamte Artefakt oder den gesamten Build, nicht auf einzelne Zeilen."

This is a well-formed, falsifiable invariant with a matching reconciliation test (Reproducibility §18.4, five concrete PASS/FAIL predicates: `S8_rows == S7_rows`; full Row Identity Preservation; full Row Order Preservation; Manifest consistency; Hash consistency). As documented in Section 11, this invariant's *only* home is the Reproducibility specification — it is absent from Data Pipeline's own §7.9/§12, where its own §6.1 rule requires it (Finding SCR7-MAJ-01).

No contradiction between any two adjacent stage contracts was found across the full chain by any of the four independent deep-dive analyses.

---

## 13. Data Validation Review

- **Validity vs. publication-eligibility**: cleanly separated. §20 Criterion 16 states: *"Zeilen mit `quality_gate_pass=false` bleiben Bestandteil des kanonischen S2-Artefakts, werden nicht stillschweigend entfernt und werden von nachgelagerten Stufen gemäß deren Stage Contracts fail-closed verarbeitet ... Kriterium 16 konkretisiert für S2 das kanonische Row-Preservation-Prinzip aus `RCC_002_DATA_PIPELINE_SPECIFICATION` §5.8."* An artifact can be published (Gate Status `PASS`) while individual rows remain `quality_gate_pass=false` — publication-eligibility is an artifact-level property; validity is a row-level property. This is a genuine, correctly-targeted §5.8 back-reference (confirmed via full-file search: exactly two "5.8" occurrences in this document, both meaningful).
- **Error classes / blocking conditions**: missing PK/time/OHLCV fields are `CRITICAL` (§14.1); unregistered extra fields are permitted only if they surface in the schema report, never silently promoted to canonical (§7.3).
- **Duplicate/timestamp handling**: see Section 12.
- **No path found** in which a structurally valid row with `quality_gate_pass=false` becomes simultaneously "usable" and "blocked" in an undefined way — the same §15.3/§7.3.2 truth table governs both documents identically.

---

## 14. Indicator Review

- **Warm-up/lookback**: exhaustive per-indicator formulas (§7–§18) plus a consolidated Warm-up-Matrix (§19) — cross-checked with no discrepancy.
- **Null/missing/imputation**: `x_valid=false ⇒ x=null` unconditionally (§20.1); no imputation mechanism exists anywhere in this document — missing/invalid values remain `null`, never filled. Warm-up rows are preserved with `x=null`, never dropped (`impute_flag` as a named field does not exist here; see Section 10).
- **Recursive indicators / partitioning**: see Section 12 (S2→S3). Independent re-derivation of Gemini MAJOR-001 (Section 30) is anchored in this document.
- **`§4.3` and `§30` criterion 2 vs. `§20.1`**: mutually consistent by construction — `quality_gate_pass` is one of the ANDed terms in the `x_valid` formula, so `quality_gate_pass=false` mechanically forces `x_valid=false`; no gap between the declarative rule (§4.3/§30) and the mechanistic formula (§20.1).
- **MUST/SHALL/SHOULD/MAY**: `SHALL` is used zero times in this document; `MUST`≈11, `SHOULD`=2, `MAY`=5. Every `SHOULD`/`MAY` instance traces to an optional technique (alternative gap policy, rolling overlap read, incremental append, external library use) that does not weaken a `MUST`-level invariant, with one partial exception: property-based tests re-stating `MUST`-level invariants are themselves pinned at `SHOULD` (§27.8) — Finding SCR7-MIN-03.

---

## 15. Signal Transformation Review

- **§28.2** `S4_rows = S3_rows`, correctly cross-referenced to Data Pipeline §5.8; a stronger per-field reconciliation requirement is added beyond the row-count equation: *"Zusätzlich muss die zeilenweise Reconciliation für jedes durchgereichte S3-Feld semantische Gleichheit bestätigen."*
- **§20 discrete rule matrix**: exhaustive, threshold equality resolved uniformly to the neutral branch in all cases checked (see Section 12).
- **Neutral/invalid/null are kept distinct**: §3.3 explicitly separates `DIRECTION_DISCRETE`/`DIRECTION_SCORE`/`TREND_STATE`/`VOLATILITY_STATE`/`TREND_STRENGTH`/`VALIDITY` and explicitly guards against silently summing non-directional roles as long/short votes: *"`VOLATILITY_STATE` und `TREND_STRENGTH` dürfen nicht ohne eine separat spezifizierte Regel als Long- oder Short-Stimme summiert werden."*
- **§4.5 "parallele Repräsentationen"**: discrete and continuous signal families are explicitly disclosed as not fully order-consistent at exact threshold anchors (e.g., RSI=30 exactly: discrete=neutral, continuous=maximum long anchor) — self-disclosed and deferred to a future strategy-layer combination rule, not a hidden contradiction (Observation O-3).
- **Stale dependency-version metadata**: this document's own Document-Control table (lines 15–16) and §35 still state its parent (Data Pipeline) as "Version 0.7.0" and its dependencies (Data Validation, Indicator) as "Version 0.4.0" — all three are stale relative to the actual current versions (0.7.1/0.4.1/0.4.1). See Finding SCR7-MAJ-03.

---

## 16. Regime and Gate Review

Full `GateState` derivation (§18.4), quoted in structure:

```
if gate_valid = false:        INVALID (both directions false)
elif long=true and short=true: ALLOW_BOTH
elif long=true and short=false: ALLOW_LONG_ONLY
elif long=false and short=true: ALLOW_SHORT_ONLY
else:                           BLOCK_BOTH
```

This is exhaustive over the full 2×2 boolean space plus the validity override; no combination is left undefined, doubly defined, or unreachable in a way that breaks determinism. Evaluation order is fixed (§20.4): structural check → data-gate check (absolute priority) → profile-input validity → policy predicates. Long/Short symmetry is structural (mirrored predicates in `GATE_TREND_ALIGNED_V1`/`GATE_TREND_STRENGTH_ALIGNED_V1`, §15/§16), not merely asserted — no unjustified asymmetry found.

Regime and Gate's own local **§5.8**, titled "Profilversionen", is a version-number/profile-ID table unrelated in content to Data Pipeline's Row-Preservation §5.8 — confirmed, via full quotation and re-reading, to be a coincidental section-number collision, not a genuine cross-reference (Finding SCR7-MIN-06 / confirms prior AIR3-m1's own characterization independently).

`data_gate_pass=false` unconditionally forces `BLOCK_BOTH` with `gate_valid=true`, and no profile can override this (§13.3/§14.2) — verified directly, no counterexample found.

Falsifiability is strong throughout: every truth table maps 1:1 to an enumerated test-requirement section (§31–34), with identical numeric tolerance constants to the Indicator/Signal Transformation documents. One honestly-disclosed exception: §25's falsification criteria for *profile promotion to production* explicitly defer concrete numeric acceptance thresholds to a not-yet-existing separate test plan (Observation O-4) — this gates only a future activation decision, not current pipeline consistency.

---

## 17. Label and Forward Return Review

S7 causal isolation (Section 12) is the strongest control found in the family. The row-preservation invariant (§22) explicitly covers row count, PK identity, PK order, and market-segment-ID equality in one place.

**Confirmed Minor finding** — apparent wording conflict on tail-row field nullness:

- §17.4: *"Für die letzten `h` Zeilen ... fehlen regulär vollständige Zukunftsdaten. Diese Werte sind ungültig mit: `LBL_FUTURE_HORIZON_INCOMPLETE`. Sie werden nicht mit null aufgefüllt und nicht entfernt."*
- §18.3: *"Wenn ein familienbezogenes `*_valid_h=false` ist: alle numerischen Felder dieser Familie und dieses Horizonts sind `null`..."*

Read literally, §17.4 says tail-row values are "not padded with null" while §18.3 says family-invalid numeric fields (which necessarily includes tail rows once `*_valid_h=false`) *are* null for the same scenario. The more specific and repeated rule (§18.3) controls the actual normative outcome — rows are retained, and their numeric fields for the incomplete horizon are `null` — but the literal text of §17.4 states the opposite for the same case (Finding SCR7-MIN-02). This does not affect row preservation itself (both readings agree rows are kept, never deleted or backfilled with synthetic non-null rows).

No look-ahead/leakage violation was found; the causality boundary (§2, §3.1) is exceptionally explicit and independently cross-checked against Regime and Gate §26, which separately and explicitly forbids referencing forward returns as a regime input (line ~1621: *"Forward Returns als Regimeinput"* explicitly excluded) — a direct textual firewall against S7→S5/S6 feedback leakage.

---

## 18. Reproducibility and Manifest Review

- **§7.4** four-tier equality ladder (E0 "keine Gleichheitsaussage" through E3 "Bytehash gleich"), with E2 (semantic fingerprint equality) as the mandatory publication floor (*"Veröffentlichte RCC-002-Daten MÜSSEN mindestens E2 erreichen."*) — well-formed and falsifiable.
- **§7.3 semantic fingerprint**: includes row count as one input among several (column order, logical types, null representation, canonical PK, canonical row order, schema version). This is a **detection** mechanism for drift, not itself the row-preservation **requirement** — that requirement is stated separately and explicitly in §8.7.1. No circularity found between the two; they are complementary.
- **§5.9 `manifest_id`**: explicitly designed to avoid self-reference — computed from the canonicalized manifest *minus* the `manifest_id` field itself, then inserted; the stored file's byte-hash is logged separately and explicitly permitted to differ (*"Der `manifest_id` und der Byte-Hash der finalen Datei dürfen verschieden sein, weil das Feld `manifest_id` selbst erst nach der Vorabbildung ergänzt wird."*) — a clean, circularity-free design (Positive Finding P-4).
- **§8.7.1 / §18.4**: see Section 12 (S7→S8) — confirmed present, explicit, and falsifiable; independently re-verified by direct file inspection (`grep -n "8.7.1"` → line 886; the surrounding text matches the quote given above verbatim).
- **§25 Publication Gate**: a single, dataset-wide checklist of roughly 30 items (source manifest validity, code provenance, config/schema hashing, lineage completeness, per-stage contract proofs, S7 leakage tests, etc.). No dedicated, view-specific S8 publication-gate chapter exists — S8 criteria remain distributed across this section and Data Pipeline §12. This confirms AIR3-m2's prior characterization; assessed here as Minor (organizational gap; underlying substance is covered elsewhere), Finding SCR7-MIN-08.
- **Generator read/hash asymmetry** (new finding, not previously reported by any prior review): `build_bundle()` in `scripts/build_rcc002_spec_bundle.py` reads each source file twice — `path.read_text(encoding="utf-8")` (subject to Python's universal-newline translation) for the embedded content, and `path.read_bytes()` (untranslated) for the SHA-256 shown in the bundle's own per-file table. On the current, LF-only Linux checkout the two reads coincide (confirmed by the byte-exact round-trip, Section 7), so the defect is currently dormant. But if any source file under `docs/specifications/` were ever saved with CRLF line endings — plausible given §16.1's own named multi-device reproducibility targets, which include Windows-class devices — the table's claimed per-file hash would be computed from the CRLF raw bytes while the embedded document body would have those same bytes silently LF-normalized by `read_text()`, so the table's hash would no longer match the hash of the text actually embedded beneath it. This is distinct from, and not fixed by, the already-closed newline-portability finding `m2` (which pinned only the *output* file's newline via `newline="\n"` on write) — this is a *read-side* asymmetry (Finding SCR7-MIN-04).
- **§12.3 "Kanonisches Spezifikationsprofil"**: see Section 22 (Finding SCR7-MAJ-02) — confirmed stale and self-contradictory by direct inspection.
- **Document-Control staleness**: the document's own `Status` field and §29 ("Der aktuelle Status lautet" / "Nächste vorgeschriebene Schritte") still describe the document as `SCR-005-Corrected Draft – Scientific Consistency Re-Review 006 Pending`, and list SCR-006 as a still-pending next step, even though the same file's normative body already contains post-C1/post-AIR-003 content (§8.7.1, §18.4, the §5.8 cross-reference) (Finding SCR7-MIN-07).

---

## 19. Negative and Edge-Case Review

| # | Case | Result | Basis | Contradiction? |
|---:|---|---|---|---|
| 1 | Empty dataset | No row-count equation triggers (0=0 trivially); Publication Gate criteria still apply | Data Validation §20; Data Pipeline §12 | None found; not explicitly discussed anywhere (Observation O-2) |
| 2 | Single row | `market_segment_id` formed trivially | Data Pipeline §7.3.1 | None |
| 3 | Fully invalid dataset | Every row `quality_gate_pass=false`, all preserved, Gate Status likely FAIL | §5.8, §20 | None |
| 4 | Partially invalid dataset | Mixed `quality_gate_pass` per row, all preserved | §5.8, §15.1 | None |
| 5 | Duplicate PK (identical) | Deterministic collapse permitted, full lineage retained | Data Validation §10.1 | None |
| 6 | Duplicate PK (conflicting) | `CRITICAL`, build aborts absent approved priority rule | Data Validation §10.2 | None |
| 7 | Non-monotonic timestamps | Deterministic re-sort, `source_row_id` preserves original order | Data Validation §8.5 | None (Observation O-6) |
| 8 | Identical timestamps | Covered under conflicting-duplicate handling | Data Validation §10.2 | None |
| 9 | Missing required fields | `CRITICAL` | Data Validation §14.1 | None |
| 10 | Unknown extra fields | Allowed only if registered; else surfaced in schema report, never silently canonicalized | Data Pipeline §7.3 | None |
| 11 | Fully missing indicator values | Row kept; `x=null`, `x_valid=false`, `x_warmup_complete=false`, reason code | Indicator §20.1–§20.2 | None |
| 12 | Single missing indicator value | Invalidation scoped only to the dependent field(s) (*"ungültiger MFI invalidiert keine RSI-Transformation"*) | Signal Transformation §23.7 | None |
| 13 | `impute_flag=false`/`true` | N/A — field does not exist in this family (Section 10); equivalent semantics fully covered via `x_valid`/`x_warmup_complete` | — | N/A |
| 14 | Insufficient warm-up history | Same as case 11 — never a row-count effect | Indicator §19, §20.1 | None |
| 15 | Unvollständiger Forward-Return-Horizont | Row kept; numeric fields for that horizon null; reason code `LBL_FUTURE_HORIZON_INCOMPLETE` | Label §17.4/§18.3 | See Finding SCR7-MIN-02 (wording conflict, not a row-preservation defect) |
| 16 | Last rows with no computable label | Same as case 15 | Label §17.4/§18.3 | See Finding SCR7-MIN-02 |
| 17 | `quality_gate_pass=false` | Row preserved, downstream fail-closed states (e.g. `BLOCK_BOTH`) | §5.8, §15.3 | None |
| 18 | `data_gate_pass=false` | Same row-preservation guarantee; unconditionally forces `BLOCK_BOTH` | Regime and Gate §13.2/§13.3 | None |
| 19 | `BLOCK_LONG`-equivalent (`ALLOW_SHORT_ONLY`) | Reachable, tested | Regime and Gate §18.4, §32 | None |
| 20 | `BLOCK_SHORT`-equivalent (`ALLOW_LONG_ONLY`) | Reachable, tested | Regime and Gate §18.4, §31 | None |
| 21 | `BLOCK_BOTH` | Reachable via data-gate failure or unfavorable-but-valid regime | Regime and Gate §13.3, §31–32 | None |
| 22 | Artifact quarantine | Whole-artifact only, never row-level | §5.8, §8.7.1 exception clause | None |
| 23 | Build abort | Whole-build only, never row-level | §5.8, §8.7.1 exception clause | None |
| 24 | Failed partition | State-continuity precondition failure aborts fail-closed, no silent fallback | Indicator §22.4 | None |
| 25 | Unequal-size partitions | Explicitly tested | Indicator §27.5 | None |
| 26 | Empty partition | Not explicitly named in Indicator §27.5's test-scenario list (though §22.4's abort-on-mismatch preconditions would likely catch most resulting inconsistencies indirectly) | Indicator §27.5 | Coverage gap, not a normative contradiction (Observation O-7) |
| 27 | Different chunk size | Covered generally under partition-parity requirement; chunk size explicitly barred from affecting logical output | Indicator §31.2/§33.2 | None |
| 28 | Serial vs. partitioned build | Mandatory, gate-blocking equivalence | Indicator §22.1/§27.5/§30 crit. 17; Signal Transformation §27.1/§29.8/§32 crit. 10 | None |
| 29 | Repeated identical build | Identical deterministic IDs required when only `run_id`/run-time changes | Reproducibility §6.7, §18.4 | None |
| 30 | Same semantics across different line endings | Covered on write side (generator `m2` fix, closed); read-side asymmetry remains (Finding SCR7-MIN-04) | `scripts/build_rcc002_spec_bundle.py` | Latent, currently dormant |

---

## 20. Mathematical and Logical Consistency

- The `GateState` truth table (Section 16) is exhaustive over its full input domain, with a fixed evaluation priority and no unreachable-but-undocumented or doubly-defined state found.
- The discrete signal rule matrix (Section 15) is exhaustive with threshold equality uniformly resolved to the neutral/lower-severity branch in every row checked — no ambiguity at boundary values.
- The `x_valid`/`y_valid` boolean formulas (Sections 14/15) are conjunctive (AND) chains over named sub-conditions; every sub-condition traces to an independently defined boolean, and `quality_gate_pass=false` propagates deterministically through both.
- Zero-denominator handling across ATR/OBV/ROC/MA200/EMA50/MACD-ratio transformations follows one consistent pattern throughout Indicator: numerator-also-zero → defined `0`; otherwise → `INVALID` with a dedicated reason code — no divergent handling found between indicators.
- No unreachable state, no double-assignment of one input combination to two different outcomes, and no non-deterministic rule-resolution order were found in the two truth tables examined most closely (gate-state, discrete-signal).

---

## 21. Cross-Document Consistency Matrix

| Topic | Consistency across the 7 documents | Notes |
|---|---|---|
| Stage names/numbers (S0–S8) | Identical | Defined once (Data Pipeline §6), consumed by name everywhere |
| Primary key `(market_type, symbol, interval, open_time[, provider])` | Identical | Confirmed at S2 (Data Validation), S7 (Label §22), S8 (Reproducibility §8.7.1) |
| Row Count invariant | Present & compatible S2→S8, **but Data Pipeline's own S8 stage contract (§7.9) and Publication Gate catalog (§12) do not state it** | See Finding SCR7-MAJ-01 |
| Row Identity / Row Order | Consistent at every boundary | Phrased compatibly throughout |
| `quality_gate_pass` | Single source of truth (Data Validation/Data Pipeline §7.3.2/§15.1) | No duplicate/conflicting definition found |
| `data_gate_pass` | Single source of truth (Regime and Gate §13.2, explicitly self-declared) | `data_gate_pass = quality_gate_pass` verified |
| Build Abort / Quarantine | Consistent — artifact/build-level only, never row-level | Verified across Data Pipeline, Reproducibility, Regime and Gate, Label |
| Publication | Every stage has a dedicated Publication Gate chapter **except S8** | S8 criteria remain distributed (Data Pipeline §12 + Reproducibility §25) — Finding SCR7-MIN-08 |
| Configuration Identity | Consistent `component_id`/`component_version` + hash-fingerprint pattern | Indicator §28.5, Signal Transformation §28.5-equivalent, Reproducibility §7.3/§7.4 |
| Schema Identity | Consistent versioned-schema-URI pattern (`rcc002.stage.*/x.y.z`) with fail-closed unknown-major-version rejection | Verified at every stage boundary examined |
| **Version Identity** | **Inconsistent / stale** | See Findings SCR7-MAJ-02, SCR7-MAJ-03 — this is the standout row of the matrix |
| Determinism | Consistent — serial/partitioned equivalence required uniformly | Matching tolerance constants across Indicator and Signal Transformation |
| Partitioning | Consistent, with one minor coverage gap (empty partition not explicitly named as a scenario in Indicator §27.5) | Observation O-7 |
| Reconciliation | Present and falsifiable at every boundary, including S7→S8 (Reproducibility §18.4) | No gap found |

---

## 22. Versioning Assessment

Item 14 of the review order requires this assessment to be independently re-derived, not deferred to any prior instruction against changing version numbers.

**Actual current versions** (independently re-confirmed by direct grep against `docs/specifications/*.md`):

| Document | Version |
|---|---|
| Data Pipeline | `0.7.1` |
| Data Validation | `0.4.1` |
| Indicator | `0.4.1` |
| Signal Transformation | `0.4.0` |
| Regime and Gate | `0.5.0` |
| Label and Forward Return | `0.4.0` |
| Reproducibility and Manifest | `0.6.0` |

None of the seven specification files contains an internal changelog/version-history section (`grep` for "Änderungshistorie"/"Changelog"/"Version History"/"Änderungsvermerk" across all seven returns zero hits); all version provenance lives in external `docs/review/` documents (Observation O-5).

**Round 1 (original C1 fix)**: Data Pipeline, Data Validation, and Indicator each received a patch bump (0.7.0→0.7.1, 0.4.0→0.4.1, 0.4.0→0.4.1) for the original Row Preservation wording correction — appropriately versioned.

**Round 2 (this cycle — the subject of this reassessment)**: five documents (Data Validation, Indicator, Signal Transformation, Regime and Gate, Label and Forward Return) gained a new `§5.8` cross-reference to Data Pipeline, and the Reproducibility specification gained an entirely new normative invariant (§8.7.1) plus a new mandatory reconciliation test (§18.4). **Independently confirmed: zero version number changed anywhere in the family for this round** — Reproducibility's own header still reads `| Version | \`0.6.0\` |`, unchanged.

Data Pipeline's own compatibility rule (§6.4), which this document family itself establishes and which therefore is the correct internal yardstick for this question, reads in full:

> "Für logische Stufenschemas gilt semantische Versionierung: Patch: redaktionelle oder nichtsemantische Metadatenkorrektur; Minor: additive optionale Felder ohne Änderung bestehender Semantik; Major: Entfernung, Umbenennung, Typänderung, neue Nullsemantik, Schlüsseländerung oder fachliche Bedeutungsänderung."

Applying this rule to Round 2's own changes: adding a new `MUST`-level row-preservation invariant and a new mandatory reconciliation test to Reproducibility is not "redaktionelle oder nichtsemantische Metadatenkorrektur" — it is, at minimum, an additive normative change (Minor-class under §6.4), arguably stronger since it imposes a new binding constraint on existing S8 export behavior that did not exist in text form before. Under the family's own internal rule, this does not qualify for zero version change.

The manifest itself (§1, "Änderung gegenüber 1.1.0") states plainly: *"keine Versionserhöhung vorgenommen (explizite Weisung für diesen Korrekturzyklus; fachliche Neubewertung der Versionierungsfrage nicht Gegenstand dieses Zyklus)"* — this is an explicit acknowledgment that the versioning question was deliberately deferred, not resolved. Per the review order's own instruction, a prior instruction not to change version numbers is a process fact, not a scientific justification, and this review is required to re-litigate the question independently — which it has done, concluding that the family's own compatibility rule is not satisfied by a zero-version-change outcome for Round 2 (**Finding SCR7-MAJ-03**).

Independently and separately, Reproducibility's own §12.3 "Kanonisches Spezifikationsprofil" table — a section explicitly declared `MUST`-binding (*"Das kanonische RCC-002-Profil MUSS mindestens folgende Dokumente referenzieren"*) — was directly re-inspected and found to read:

```
| RCC_002_DATA_PIPELINE_SPECIFICATION | 0.6.0 |
| RCC-002-DV                          | 0.3.0 |
| RCC-002-IS                          | 0.3.0 |
| RCC-002-ST                          | 0.3.0 |
| RCC-002-RG                          | 0.4.0 |
| RCC-002-LF                          | 0.3.0 |
| RCC-002-RM                          | 0.5.0 |
```

This table (a) lags the actual current versions of all seven documents by one to two generations (e.g. Data Pipeline shown as 0.6.0 against an actual current 0.7.1), and (b) self-contradicts the very same file's own header (`| Version | \`0.6.0\` |`) and §29 closing section (both state `0.6.0`), since the table lists `RCC-002-RM` (this document itself) as `0.5.0` (**Finding SCR7-MAJ-02**).

Additionally and convergently, all six documents dependent on Data Pipeline/Data Validation/Indicator were independently re-checked and found to still cite those three documents' **pre-C1** versions (0.7.0 / 0.4.0 / 0.4.0) in their own Document-Control metadata tables and closing "Abhängigkeiten"/"dependencies" sections — none were updated when the C1 patch bump occurred:

```
RCC_002_DATA_VALIDATION...:15:            ...DATA_PIPELINE...md, Version 0.7.0
RCC_002_INDICATOR_SPECIFICATION...:15-16: ...DATA_PIPELINE... 0.7.0; ...DATA_VALIDATION... 0.4.0
RCC_002_SIGNAL_TRANSFORMATION...:15-16:   ...DATA_PIPELINE... 0.7.0; ...DATA_VALIDATION... 0.4.0; ...INDICATOR... 0.4.0
RCC_002_REGIME_AND_GATE...:15-16:         ...DATA_PIPELINE... 0.7.0; ...DATA_VALIDATION/INDICATOR/SIGNAL_TRANSFORMATION... 0.4.0
RCC_002_LABEL_AND_FORWARD_RETURN...:      (same pattern, independently confirmed by deep-dive fork)
RCC_002_REPRODUCIBILITY_AND_MANIFEST...:16: ...DATA_PIPELINE... Version 0.7.0
```

This reproduces, inside the live, currently-canonical bundle, the identical failure category — a document's stated dependency-version metadata silently diverging from the dependency's actual current version — that this project's own history (Findings C1 and C2) has already treated as certification-relevant. This is folded into **Finding SCR7-MAJ-03** as supporting, convergent evidence from six independent locations rather than a separate finding.

**Independent conclusion**: "no version change" for Round 2 is not scientifically or governance-defensible under the document family's own internal rule, irrespective of the explicit instruction to leave versions unchanged for this cycle; that instruction is a valid record of what happened, not a justification for why it was correct.

---

## 23. Critical Findings

None. No defect was found in this review that produces scientifically incorrect results, non-deterministic or non-reproducible outputs, data loss, undetected leakage, publication of invalid artifacts, a fundamental architecture contradiction, or certification of the wrong review substrate. Input control (Sections 6–7) confirms the substrate itself is correct and reproducible.

---

## 24. Major Findings

### SCR7-MAJ-01 — S7→S8 Row Preservation invariant absent from Data Pipeline's own stage-contract and Publication Gate catalog

- **Severity**: Major
- **Affected documents**: `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md` §6.1, §7.9, §12
- **Quotes**:
  - §6.1: *"Jede Stufe muss definieren: ... Zeilenzahl-Invariante; ..."* (stated for all nine stages listed in §6, including `9. S8_EXPORT: konsumfertige, manifestgebundene Datensätze.`)
  - §7.9 (opening): *"S8 verwendet ausschließlich die nachfolgende versionsgebundene Registry. Jede View ist eine positive, fail-closed Feld-Allowlist."* — no row-count statement anywhere in §7.9 (independently confirmed: zero matches for "Zeilenzahl"/"S8_rows"/"S7_rows" in the full §7.9 text).
  - §12 criterion 3: *"Zeilenzahlveränderungen vollständig erklärt sind"* — generic, dataset-build-wide, not S8-view-specific.
- **Description**: Architecture Integrity Review AIR-003 (2026-07-25) identified this exact gap as its Major Finding AIR3-M1 and recommended adding the invariant to *both* `RCC_002_DATA_PIPELINE_SPECIFICATION` §7.9 *and* a reconciliation test requirement to `RCC_002_REPRODUCIBILITY_AND_MANIFEST`. Only the latter half of that recommendation was implemented (Reproducibility §8.7.1 + §18.4, independently confirmed correct and falsifiable in Section 18). Data Pipeline §7.9 was not touched in this correction round (confirmed via the manifest's own change table: Data Pipeline is marked "in diesem Zyklus unverändert" for the round that added the cross-references and the S8 invariant). Data Pipeline's own §6.1 rule — which governs Data Pipeline's own stage-contract catalog and explicitly names `S8_EXPORT` as one of the nine stages subject to it — is therefore currently unsatisfied by Data Pipeline's own text.
- **Minimal reproducible counterexample**: A reader consulting only `RCC_002_DATA_PIPELINE_SPECIFICATION` §7.9 (the document that owns the stage-contract catalog and the S8 stage definition) to determine whether S8 views must preserve row count would find no such statement; they would have to already know to cross-check a different document (Reproducibility) to discover the actual, correctly-stated invariant.
- **Scientific/technical impact**: The invariant is fully enforced in the specification family (via Reproducibility), so no live scientific defect exists; the impact is a self-consistency failure of Data Pipeline's own §6.1 completeness rule against its own §7.9 section, and a repeat of exactly the "implicit-only, single-document" gap pattern that produced the original C1 finding.
- **Certification impact**: Blocks confident sign-off on Data Pipeline's internal completeness under its own §6.1 rule; does not by itself invalidate the S7→S8 architecture, which is soundly specified elsewhere.
- **Minimal recommended correction**: Add an explicit `S8_rows = S7_rows` (per view) statement directly to Data Pipeline §7.9, and add an S8-view-specific row-reconciliation criterion to §12's Publication Gate catalog (distinct from the generic criterion 3), per AIR-003's original recommendation in full.
- **Severity justification**: Major, not Critical, because the invariant is in fact present, explicit, and enforced elsewhere in the family (Reproducibility), so no undetected row-loss risk currently exists; Major, not Minor, because it is a confirmed incompleteness of a named `MUST`-level requirement (§6.1) applied to the document's own explicitly-listed stage, in the exact defect category (implicit/single-location invariant at a Publication-relevant boundary) this review family has already once certified as Major (AIR3-M1) and has not fully closed.

### SCR7-MAJ-02 — Reproducibility §12.3 canonical specification-profile table is stale and self-contradictory

- **Severity**: Major
- **Affected document**: `RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md` §12.3
- **Quotes**: table reproduced in full in Section 22; header (line 11): `| Version | \`0.6.0\` |`; §12.3 lists `RCC-002-RM` (this same document) as `0.5.0`.
- **Description**: §12.3 is explicitly normative (*"Das kanonische RCC-002-Profil MUSS mindestens folgende Dokumente referenzieren"*) and is the document's own mechanism for constructing `specification_profile` entries in dataset manifests (per this document's stated purpose, §1: *"welche Spezifikationsstände verbindlich waren"*). The table is stale by one to two generations for six of seven listed documents relative to their actual current versions, and directly self-contradicts this same document's own header and §29 closing section regarding its own version number.
- **Minimal reproducible counterexample**: An implementation that follows §12.3 literally when constructing a dataset manifest's `specification_profile` field would stamp `RCC_002_DATA_PIPELINE_SPECIFICATION: 0.6.0` into every manifest it produces, even though the actual specification in force is `0.7.1` — making the manifest's own lineage claim about "which specification versions were binding" false on its face.
- **Scientific/technical impact**: Directly undermines the Reproducibility specification's own stated purpose (traceable knowledge lineage) if implemented literally; this is exactly the class of defect the review taxonomy's Major tier describes as "eine Implementierung zu inkompatiblen Ergebnissen führen kann."
- **Certification impact**: Blocks certification of the Reproducibility specification's internal consistency; must be resolved before Editorial Pass.
- **Minimal recommended correction**: Update §12.3 to the seven actual current versions and reconcile it with the header/§29 version field, or replace the static table with an explicit rule to resolve versions from the actual current `docs/specifications/` contents at build time.
- **Severity justification**: Major — a direct, quotable self-contradiction inside a `MUST`-level, lineage-relevant table in a single document, with a concrete failure scenario for any implementation that follows it as written; not Critical because no artifact has yet been built against this table (the RCC-002 specification family has no implementation in this repository at the time of this review).

### SCR7-MAJ-03 — Systemic zero version-increment for substantive normative additions, contrary to the family's own compatibility rule, with stale cross-document dependency-version references in all six dependent documents

- **Severity**: Major
- **Affected documents**: all seven specifications (Reproducibility for the new content; Data Validation, Indicator, Signal Transformation, Regime and Gate, Label and Forward Return, and Reproducibility for the stale dependency references)
- **Quotes**: Data Pipeline §6.4 (compatibility rule, quoted in full in Section 22); manifest §1 ("keine Versionserhöhung vorgenommen... explizite Weisung"); six documents' Document-Control tables citing Data Pipeline "Version 0.7.0" / Data Validation and Indicator "Version 0.4.0" (all quoted in Section 22).
- **Description**: see full derivation in Section 22. In summary: (a) Round 2 of the correction cycle added a new `MUST`-level invariant and a new mandatory test to Reproducibility, plus new cross-reference content to five other documents, with zero version increment anywhere; (b) applying the family's own §6.4 compatibility rule to this change classifies it as at least Minor-worthy, not zero-change; (c) all six documents dependent on Data Pipeline/Data Validation/Indicator still declare those documents' pre-C1 versions in their own metadata, never updated when the C1 patch bump occurred.
- **Minimal reproducible counterexample**: A future reader or an automated dependency-consistency check trusting Signal Transformation's own metadata table (*"Übergeordnetes Dokument | ... Version 0.7.0"*) would believe it depends on Data Pipeline v0.7.0 — a version already superseded by the very correction cycle this bundle represents — and could consult the wrong historical text when investigating a discrepancy. This is the same byte/version-confusion pattern that produced Findings C1 and C2 in this project's own history, now reproduced live in six locations simultaneously.
- **Scientific/technical impact**: Undermines confident cross-document version reconciliation (review item 13) and repeats, inside the very correction cycle that fixed C1, the failure category that produced C1 in the first place.
- **Certification impact**: Blocks confident certification of cross-document version consistency; must be resolved (or explicitly, scientifically re-justified — not merely re-asserted as a process instruction) before Editorial Pass.
- **Minimal recommended correction**: Apply a governance-approved version increment to Reproducibility (at least Minor, per §6.4) and to the five cross-reference-only documents (at least Patch, per §6.4), and update all six documents' stale dependency-version references to the current actual versions (0.7.1/0.4.1/0.4.1).
- **Severity justification**: Major — a normative defect (unversioned substantive change; six convergent stale cross-references) that makes cross-document version identity unreliable family-wide, in a category this project's own governance history has already twice treated as certification-relevant; not Critical since no scientifically wrong *result* is produced by the current text — the row-preservation/signal architecture itself remains correct regardless of which version label attaches to it.

---

## 25. Minor Findings

### SCR7-MIN-01 — Data Pipeline §5.8 states permitted responses only illustratively, not as an explicit prohibition
- **Document/§**: Data Pipeline §5.8. **Quote**: *"Zulässige Reaktionen sind insbesondere: ungültige oder Null-Indikatorwerte; ..."* ("insbesondere" = "in particular" — an illustrative, non-exhaustive list, not a `MUST NOT`-strength clause against valid derived values for `quality_gate_pass=false` rows).
- **Failure scenario**: A reader of §5.8 alone could not point to an explicit sentence banning valid derived values for invalid rows; they would need to also know Indicator §4.3/§20.1 states the mechanistic enforcement.
- **Impact**: No functional gap — the prohibition is fully enforced mechanistically in Indicator via the `x_valid` AND-formula (Section 14) — but the abstract global principle itself is textually permissive-by-omission at this exact location.
- **Certification impact**: Non-blocking.
- **Minimal fix**: Add one explicit sentence to §5.8, e.g. "Zeilen mit `quality_gate_pass=false` DÜRFEN NICHT gültige abgeleitete Werte tragen."
- **Severity justification**: Minor — localized wording gap, no normative inconsistency, independently confirms the prior C1-SCR "m3" characterization.

### SCR7-MIN-02 — Label and Forward Return §17.4 vs. §18.3 apparent wording conflict on tail-row nullness
- Quoted and analyzed in full in Section 17. **Minimal fix**: reword §17.4 to clarify that "these values are not backfilled" refers to row retention, not field-level nullness, explicitly deferring field nullness to §18.3.
- **Severity justification**: Minor — the more specific, repeated rule (§18.3) controls the actual outcome and rows are never dropped under either reading, but the literal text of §17.4 states the opposite of §18.3 for the same scenario.

### SCR7-MIN-03 — Property-based tests re-stating MUST-level invariants are pinned at SHOULD
- **Document/§**: Indicator §27.8, Signal Transformation §29.10. **Quote (Indicator §27.8)**: *"SHOULD geprüft werden: ... `x_valid=true` impliziert `x_warmup_complete=true`; kein Feld mit einem invalidierenden Reason Code besitzt `x_valid=true`..."*
- **Failure scenario**: A coding defect that occasionally sets `x_valid=true` while `x_warmup_complete=false` would only be systematically caught by a test class that is optional (`SHOULD`), not mandatory.
- **Minimal fix**: Elevate the specific bullets that directly re-state a `MUST` invariant (validity implication, segment-ID determinism, no-invalidating-code-when-valid) to `MUST`; leave genuinely exploratory property tests at `SHOULD`.
- **Severity justification**: Minor — normative content unaffected; a testability/operationalization gap for otherwise-correct invariants.

### SCR7-MIN-04 — Generator hashes raw source bytes but embeds newline-translated content
- Full analysis in Section 18. **Minimal fix**: hash `content.encode("utf-8")` instead of `raw_bytes`, or enforce LF-only source files via `.gitattributes`.
- **Severity justification**: Minor — currently dormant (all current sources are LF-only, independently confirmed via the byte-exact round-trip), but latent given the spec's own stated multi-OS reproducibility targets.

### SCR7-MIN-05 — RFC-2119 keyword framework underused relative to German modal-verb normative prose
- Full analysis in Section 10. **Minimal fix**: add one sentence to Data Pipeline §2 stating that "muss"/"darf nicht" are used as MUST/MUST NOT-equivalent throughout the document, or increase literal keyword usage.
- **Severity justification**: Minor — a latent normative-force ambiguity, not a confirmed contradiction (no case was found where a German modal verb was read at a weaker strength than intended).

### SCR7-MIN-06 — Regime and Gate §5.8 is a coincidental section-number collision with Data Pipeline's Row-Preservation §5.8
- Full analysis in Section 16. **Minimal fix**: renumber Regime and Gate's "Profilversionen" section at the next editorial opportunity to avoid reader/tooling confusion.
- **Severity justification**: Minor/Future Risk boundary — no content relation and no current misreading found, but a latent cross-reference-tooling risk in a family that already relies heavily on section-number cross-references.

### SCR7-MIN-07 — Reproducibility's own Document-Control metadata is stale relative to its own normative body
- Full analysis in Section 18 (Status field, §29 still describing "SCR-006 pending" despite already containing post-AIR-003 content).
- **Minimal fix**: refresh the Status field and §29 alongside any future version bump (see SCR7-MAJ-03).
- **Severity justification**: Minor — editorial/traceability inconsistency, not a scientific defect, but feeds the same "which version does this text represent" ambiguity pattern underlying the Major versioning findings.

### SCR7-MIN-08 — No dedicated, view-specific S8 Publication Gate chapter
- Full analysis in Section 18/21 (confirms prior AIR3-m2 independently).
- **Minimal fix**: add a dedicated S8 Publication Gate chapter (analogous to Data Validation §20 / Indicator §30 / Signal Transformation §32 / Regime and Gate §35–36 / Label §38), consolidating the currently-distributed Data Pipeline §12 + Reproducibility §25 criteria.
- **Severity justification**: Minor — underlying substance (row preservation, allowlist, leakage) is fully covered elsewhere; the gap is organizational, not normative.

---

## 26. Observations

- **O-1**: No central glossary defines Row Identity/Row Order/Row Count as first-class terms across the family; usage is consistent but only operational (Section 10).
- **O-2**: Empty-dataset and single-row scenarios are not explicitly discussed anywhere in the reviewed text; behavior generalizes consistently (0=0 trivially) but is genuinely untested/undiscussed as a named case.
- **O-3**: Signal Transformation's "parallel representations" framing (§4.5) is disclosed and deferred but can read as implying closer ordering-consistency between discrete and continuous signal families than actually holds at exact threshold anchors.
- **O-4**: Regime and Gate §25's falsification criteria for profile promotion defer concrete numeric acceptance thresholds to a not-yet-existing separate test plan — honestly disclosed, gates only a future activation decision.
- **O-5**: None of the seven canonical specification files carries an internal changelog/version-history section; all version provenance lives in external `docs/review/` documents.
- **O-6**: Non-monotonic (as opposed to missing) timestamps are handled via the general deterministic re-sort mechanism rather than named as their own anomaly class; appears benign (sorting is lossless/idempotent) but not explicitly discussed as a distinct edge case.
- **O-7**: Indicator §27.5's partition-parity test-scenario list does not explicitly name an empty-partition case.

---

## 27. Positive Findings

- **P-1**: Row Preservation is stated as an explicit row-count equation at every stage boundary from S2→S3 through S7→S8 (six consecutive invariants), each correctly cross-referencing Data Pipeline §5.8, with zero contradictions found under adversarial search across four independent deep-dive analyses.
- **P-2**: The `quality_gate_pass`/`data_gate_pass`/gate-state chain is deterministic and exhaustively defined, with a fixed evaluation priority and an unconditional, non-overridable `data_gate_pass=false → BLOCK_BOTH` rule.
- **P-3**: S7 (Label) leakage protection is quadruple-redundant: naming-prefix convention, explicit field-ownership/leakage-class metadata, a per-field SHA-256'd allowlist per view, and mandatory negative-injection tests for every registered field — among the most falsifiable architecture elements found in the family.
- **P-4**: `manifest_id` computation (Reproducibility §5.9) and the semantic-fingerprint/row-count relationship (§7.3 vs. §8.7.1) are both circularity-free by explicit design, not by omission.
- **P-5**: The Source→S2 boundary is specified byte-identically in both Data Pipeline and Data Validation (verified by direct text comparison), despite being independently authored prose in two separate documents — zero drift found.
- **P-6**: Numerical tolerance regime (`1e-12` absolute / `1e-10` relative) and serial-vs-partitioned build equivalence are stated in matching form across Indicator and Signal Transformation, each gated as a mandatory, non-overridable Publication Gate criterion.
- **P-7**: The bundle generator's deterministic ordering, missing/duplicate/extra-file validation, and byte-exact round-trip property were independently re-verified in this review (not merely re-asserted from a prior document) and hold.

---

## 28. Future Architecture Risks

- **F-1**: The "principle stated once, replicated locally across N documents without a single machine-checked source" pattern that produced the original C1 drift remains structurally present — each stage's `Sn_rows = Sn-1_rows` equation is independently authored prose rather than derived from one canonical source, so a future edit to any one boundary's wording could silently re-diverge from its siblings.
- **F-2**: A future eighth pipeline stage or new S8 view would need to remember, unprompted, to add its own explicit row-count invariant to both Data Pipeline's stage-contract catalog (§6.1) and the Reproducibility specification — there is currently no enforcement mechanism beyond manual reviewer diligence ensuring this, which is exactly the gap class underlying SCR7-MAJ-01.
- **F-3**: Coincidental section-number collisions across documents (e.g. Regime and Gate's own local §5.8) could compound into genuine cross-reference errors as the family gains more documents/sections; a document-level heading-numbering or glossary convention would reduce this risk.

---

## 29. C1 Assessment

The original C1 Row Preservation correction (Data Pipeline §5.8 plus the associated Data Validation/Indicator wording fixes) is confirmed, under independent adversarial re-derivation across all four deep-dive analyses, to be structurally sound and internally consistent for the S2 through S7 portion of the pipeline — no counterexample was found. C1 is correctly described as technically closed with respect to the row-preservation *content* it addressed.

However, this review finds that the *process pattern* that produced C1 — a normative, testable change made without adequate version tracking, discovered only via close reading rather than an enforced identity check — has recurred within the very correction cycle that fixed C1 (SCR7-MAJ-02, SCR7-MAJ-03), and that C1's own downstream architectural consequence at the S7→S8 boundary (identified separately as AIR3-M1) was only partially remediated (SCR7-MAJ-01: the invariant landed in Reproducibility but not, as originally recommended, also in Data Pipeline itself). C1 is therefore assessed as **technically closed for its original scope, but its associated remediation cycle is not yet fully closed**, given these three confirmed Major findings.

---

## 30. Gemini MAJOR-001 Assessment

Independently re-derived from the current Indicator specification's text alone (not deferred to the prior REJECTED verdict): the claimed gap — lack of an explicit deterministic reconstruction mechanism (sequence barrier, mandatory sort) for the S2→S3 transition under parallel execution — does not hold against the current text. The combination of (a) a hard serial/partitioned-build equivalence requirement (§22.1: *"Ein partitionierter Vollbuild MUST nach feldspezifischer Toleranz dieselben Werte erzeugen wie ein serieller Build"*), (b) mandatory checksum-verified sequential state chaining with fail-closed abort on any mismatch and an explicit ban on silent fallback (§22.4), (c) a fully deterministic, non-random segment-ID derivation formula (§21.2: *"Zufällige UUIDs sind unzulässig."*), and (d) row order fixed externally by the unchanged S2 canonical key (not by processing or merge order), jointly over-determine a unique deterministic result regardless of execution order or parallelism. No implementation technique is mandated — correctly, since the specification defines the required *outcome*, not a *mechanism* — but none is architecturally missing either.

**Independent conclusion: REJECTED is confirmed correct**, re-derived from the specification text itself rather than accepted on the strength of the prior verification document.

---

## 31. C2 Scientific-Impact Assessment

C2 concerns a historical hash mismatch between the bundle actually present in Git as `RCC_002_SCR_005_CORRECTED_FULL_SPEC_BUNDLE_2026-07-24.md` (SHA-256 `5aae1bd7...`) and the package hash referenced by `RCC-002-SCR-006`/`RCC-002-AIR-002` (`33aac77f...`). It does not concern, and cannot by its nature concern, the bytes of the bundle reviewed here — this review's own independent input control (Sections 6–7) re-hashed the *current* bundle, manifest, status document, and inventory from scratch, found exact matches to their stated values, and independently reproduced the bundle byte-for-byte via a live generator round-trip. **C2 does not undermine the validity of this review's substrate.**

However, C2's root cause classification — "D. Governance Process Problem": a review document stated a bundle hash without a repository-enforced verification step confirming the reviewed bytes matched what was later committed — describes exactly the *category* of defect this review independently re-discovers, in a different location, as SCR7-MAJ-02 and SCR7-MAJ-03: version/dependency-identity fields stated in specification metadata without any enforced consistency check against the documents' actual current state. This review therefore treats C2 as historically bounded and non-blocking for *this review's substrate validity*, while assessing its underlying failure *category* as still active and currently recurring in the specification family's version metadata, not merely historical.

---

## 32. Certification Impact

Three confirmed Major Findings (SCR7-MAJ-01, SCR7-MAJ-02, SCR7-MAJ-03) block Editorial Pass and Internal Certification per the review order's mandatory verdict rules. This conclusion is reached independently in this review, via a different methodology (direct quote-anchored adversarial re-derivation across four parallel deep-dive analyses plus coordinator-level independent spot-verification of every Major claim), and happens to agree with the RCC-002 Pre-Certification Status document's own conclusion that a full-scope replacement Scientific Consistency Review would be required before certification could proceed — this review is that required review, and its outcome is that certification remains blocked until the three Major Findings above are resolved.

No Critical Finding was found; the core row-preservation, gate, signal-derivation, and leakage-isolation architecture is scientifically sound. The blocking findings are entirely in the reproducibility/versioning-identity domain.

---

## 33. Final Verdict

```text
FAIL
```

Justification: at least one confirmed Major Finding exists (in fact, three: SCR7-MAJ-01, SCR7-MAJ-02, SCR7-MAJ-03), which mandates FAIL per the review order's verdict rules, irrespective of the absence of any Critical Finding and irrespective of the otherwise-sound core scientific architecture.

---

## 34. Required Next Actions

1. Resolve **SCR7-MAJ-01**: add an explicit `S8_rows = S7_rows` (per view) statement to Data Pipeline §7.9, and an S8-specific row-reconciliation criterion to Data Pipeline §12, completing AIR-003's original recommendation in full.
2. Resolve **SCR7-MAJ-02**: correct Reproducibility §12.3's stale/self-contradictory specification-profile table and reconcile it with the document's own header/§29 version field.
3. Resolve **SCR7-MAJ-03**: obtain a governance decision to either (a) apply a version increment to Reproducibility (at least Minor) and to the five cross-reference-only documents (at least Patch), per the family's own §6.4 compatibility rule, and correct all six documents' stale dependency-version references, or (b) issue an explicit, scientifically-reasoned waiver — not merely a restated process instruction — if no bump is chosen.
4. Address the eight Minor Findings (SCR7-MIN-01 through SCR7-MIN-08) at the next editorial opportunity; none are individually certification-blocking, but SCR7-MIN-02 (Label tail-row wording) and SCR7-MIN-04 (generator read/hash asymmetry) should be prioritized given their proximity to row-preservation and reproducibility correctness respectively.
5. After steps 1–3, regenerate the bundle and manifest, repeat independent hash verification and byte-exact round-trip validation, and conduct a new full-scope replacement Scientific Consistency Review (and the still-outstanding full-scope replacement Architecture Integrity Review) against the corrected bundle before any Editorial Pass or Internal Certification step.
6. This review does not itself resolve C2; C2's own required next steps (per `RCC_002_C2_REVIEW_LINEAGE_INVESTIGATION_2026-07-25.md` §10 and the Pre-Certification Status document) remain independently applicable and are not superseded by this review.

---

## 35. Residual Uncertainty

- This review analyzed the seven canonical source files under `docs/specifications/` (independently confirmed byte-identical to the bundle's embedded copies via hash comparison and full-bundle embedding-marker verification) via four independent, full, adversarially-instructed reads, with the coordinating reviewer independently re-verifying every claim underlying a Major Finding by direct file inspection. It did not consist of one reviewer reading all 13,876 bundle lines end-to-end in a single continuous pass; this is a deliberate scope/depth trade-off between full-family coverage and per-line reviewer attention, disclosed here per the review's own falsifiability principle.
- No implementation of the RCC-002 pipeline exists in this repository at the time of this review (RCC-002 is a specification-only artifact family under `docs/specifications/` and `docs/review/`, distinct from the implemented `engine/`, `live_l1/`, and `run_engine/` code paths documented in this repository's `CLAUDE.md`). All findings in this review are specification-level; their real-world consequence is conditional on a future implementation being built literally against this specification family.
- The versioning findings (SCR7-MAJ-02, SCR7-MAJ-03) reflect this review's own independent normative judgment, as item 14 of the review order explicitly requires; a governance authority may reasonably weigh the tension between "explicit instruction to freeze versions this cycle" and "the family's own compatibility rule" differently. This review documents why the instruction alone is not a sufficient scientific justification, without claiming sole authority over the eventual governance decision.
- This review did not conduct a full-scope replacement Architecture Integrity Review (a distinct, still-outstanding requirement per the Pre-Certification Status document); some architecture-adjacent observations are included here where they bear directly on scientific consistency (e.g. SCR7-MAJ-01), but a dedicated AIR-scope review may surface additional architecture-specific findings outside this review's scientific-consistency mandate.

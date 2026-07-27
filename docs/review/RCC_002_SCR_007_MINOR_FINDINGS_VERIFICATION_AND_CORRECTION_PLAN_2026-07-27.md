# RCC-002 SCR-007 Minor Findings — Independent Verification and Correction Plan

## 1. Document Control

| Field | Value |
|---|---|
| Document Class | Independent Verification of Minor Findings + Consolidated Correction Plan |
| Verification ID | `RCC-002-SCR-007-MinFV` |
| Scope | Ten correction candidates: `SCR7-MIN-01` through `SCR7-MIN-08`, plus `SCR7-MAJ-02` and `SCR7-MAJ-03` (both already reclassified to Minor by `RCC_002_SCR_007_MAJOR_FINDINGS_VERIFICATION_2026-07-27.md`) |
| Date | 2026-07-27 |
| Status | Completed — planning only, no correction implemented |
| Reviewed Substrate | `docs/review/RCC_002_C1_CORRECTED_FULL_SPEC_BUNDLE_2026-07-25.md` (SHA-256 `18faca1d09411eb7c5b440833c8cc7fcac2a6f1870669f961653412163435198`) and the seven canonical files under `docs/specifications/` |
| Inputs | `docs/review/RCC_002_SCR_007_FULL_SCOPE_REPLACEMENT_REVIEW_2026-07-27.md` (SHA-256 `175d489133f833a6aca6ca0aa80e1658cb54ff3672e224a51d778cb6e422cf39`); `docs/review/RCC_002_SCR_007_MAJOR_FINDINGS_VERIFICATION_2026-07-27.md` (SHA-256 `7aef0a8e92aded7945724cfc037896bbe1d6811be1b54e4fc99fd6025e63e287`) |
| Storage Location | `docs/review/RCC_002_SCR_007_MINOR_FINDINGS_VERIFICATION_AND_CORRECTION_PLAN_2026-07-27.md` |
| Working Mode | Read-only planning document. No specification, bundle, manifest, generator, or prior review file was modified. No commit was created. |
| Independence Note | No prior classification (SCR-007's own, or this project's general precedent) was accepted without re-derivation from the current, actual specification text. Where this verification's conclusion narrows, rejects, or splits a prior finding, the reasoning is stated explicitly. |

No files were changed and no commit was created, with the exception of this report.

---

## 2. Executive Summary

Ten correction candidates were independently re-verified directly against the current canonical specification texts. Outcomes:

| Candidate | Verdict | Reassessed Severity |
|---|---|---|
| SCR7-MIN-01 | REJECTED | Observation |
| SCR7-MIN-02 | CONFIRMED | Minor |
| SCR7-MIN-03 | PARTIALLY CONFIRMED (Indicator: rejected; Signal Transformation: confirmed) | Observation (Indicator) / Minor (Signal Transformation) |
| SCR7-MIN-04 | CONFIRMED as a latent code characteristic, but not a *current* defect (already excluded by the passing round-trip test) | Future Architecture Risk / Observation |
| SCR7-MIN-05 | REJECTED | Observation |
| SCR7-MIN-06 | REJECTED (as requiring correction) | Observation / Future Architecture Risk |
| SCR7-MIN-07 | CONFIRMED | Minor |
| SCR7-MIN-08 | PARTIALLY CONFIRMED (narrower than originally stated) | Minor |
| SCR7-MAJ-02 (Minor candidate) | CONFIRMED | Minor |
| SCR7-MAJ-03 (Minor candidate) | CONFIRMED | Minor |

**Net result**: zero Critical, zero Major findings survive across all ten candidates. Six confirmed, correctable Minor findings remain (MIN-02, MIN-03/Signal-Transformation-only, MIN-07, MIN-08-narrow, MAJ-02, MAJ-03); none is certification-blocking on its own or in combination — all are local, unambiguously correctable, and none touches scientific correctness, determinism, reproducibility, or stage behavior. Four candidates (MIN-01, MIN-05, MIN-06, and half of MIN-03) are rejected as requiring any correction at all upon closer reading, because the underlying property is already redundantly and mechanistically enforced elsewhere in the specification family, or because no actual normative ambiguity or risk was demonstrated.

Given this, the technically correct intermediate verdict for RCC-002-SCR-007, reassessed after both the Major-Findings and Minor-Findings verification passes, is **PASS WITH MINOR CORRECTIONS** (Section 18).

---

## 3. Reviewed Substrate

| Artifact | Path | SHA-256 | Independently re-verified |
|---|---|---|---|
| Bundle | `docs/review/RCC_002_C1_CORRECTED_FULL_SPEC_BUNDLE_2026-07-25.md` | `18faca1d09411eb7c5b440833c8cc7fcac2a6f1870669f961653412163435198` | ✅ |
| SCR-007 report | `docs/review/RCC_002_SCR_007_FULL_SCOPE_REPLACEMENT_REVIEW_2026-07-27.md` | `175d489133f833a6aca6ca0aa80e1658cb54ff3672e224a51d778cb6e422cf39` | ✅ |
| Major Findings Verification | `docs/review/RCC_002_SCR_007_MAJOR_FINDINGS_VERIFICATION_2026-07-27.md` | `7aef0a8e92aded7945724cfc037896bbe1d6811be1b54e4fc99fd6025e63e287` | ✅ |

---

## 4. Finding Inventory

| ID | Title | Document(s) | Paragraph(s) | Claimed Defect | Original Recommended Fix |
|---|---|---|---|---|---|
| SCR7-MIN-01 | Illustrative-only prohibition | Data Pipeline | §5.8 | "insbesondere" list is illustrative, not an explicit `MUST NOT` against valid derived values for `quality_gate_pass=false` rows | Add explicit sentence to §5.8 |
| SCR7-MIN-02 | Tail-row nullness wording conflict | Label and Forward Return | §17.4 vs §18.3 | Apparent contradiction on whether tail-row values are null-padded | Reword §17.4 |
| SCR7-MIN-03 | Property tests pinned at SHOULD | Indicator; Signal Transformation | Indicator §27.8; Signal Transformation §29.10 | MUST-level invariants tested only at SHOULD strength | Elevate specific bullets to MUST |
| SCR7-MIN-04 | Generator read/hash asymmetry | `scripts/build_rcc002_spec_bundle.py` | `build_bundle()` | `read_text()` vs `read_bytes()` could diverge on non-LF sources | Hash `content.encode("utf-8")` or enforce LF via `.gitattributes` |
| SCR7-MIN-05 | RFC-2119 keyword underuse | Data Pipeline | §2 | Formal MUST/SHOULD/MAY framework rarely used in body text | Add equivalence statement or increase keyword usage |
| SCR7-MIN-06 | Coincidental §5.8 numbering collision | Regime and Gate | §5.8 ("Profilversionen") | Collides with Data Pipeline's Row-Preservation §5.8 | Renumber at next editorial opportunity |
| SCR7-MIN-07 | Stale Document-Control metadata | Reproducibility | Status field; §29 | Still describes itself as pre-C1/pre-AIR-003, "SCR-006 pending" | Refresh Status/§29 alongside a future version bump |
| SCR7-MIN-08 | No dedicated S8 Publication Gate chapter | Data Pipeline; Reproducibility | Data Pipeline §12; Reproducibility §25 | S8 lacks a chapter analogous to every other stage's Publication Gate | Add dedicated S8 Publication Gate chapter |
| SCR7-MAJ-02 (Minor candidate) | Stale/self-contradictory §12.3 | Reproducibility | §12.3 | Table lags actual versions by 1–2 generations; self-contradicts own header | Update table; reconcile with header/§29 |
| SCR7-MAJ-03 (Minor candidate) | Zero version increment + stale citations | Reproducibility + 5 others | Various Document-Control tables | Substantive Round-2 content added with no version bump; six documents cite pre-C1 upstream versions | Apply version increment; correct citations |

---

## 5. Verification Method

Each candidate was checked directly against the current canonical specification text (`docs/specifications/*.md`), using `grep -n`/`sed` to locate and quote the exact current wording — not the wording as paraphrased by SCR-007 or any other prior document. For each candidate the nine questions in the task's Teil B checklist were applied: (1) does the claimed wording actually exist, (2) is it normative or informative, (3) is there a real contradiction, (4) is it merely an editorial ambiguity, (5) is the matter already unambiguously normed elsewhere, (6) could two conformant implementations diverge in scientific result because of it, (7) which of scientific correctness / determinism / reproducibility / stage behavior / publication capability / pure documentation-or-version-metadata is affected, (8) is a change actually required, and (9) what is the smallest correct change. Severity was assigned strictly per the Major/Minor/Observation standard given in the task, independent of any prior label.

---

## 6. Individual Finding Verifications

### SCR7-MIN-01 — Data Pipeline §5.8 illustrative-only prohibition

Quote re-confirmed (§5.8): *"Zulässige Reaktionen sind insbesondere: ungültige oder Null-Indikatorwerte; ungültige Signalwerte; nachgelagerte Gate-Zustände wie `BLOCK_BOTH`."* — an illustrative ("insbesondere"), not exhaustive, list; no explicit `MUST NOT` clause against valid derived values sits at this exact location.

Independent cross-check of whether this is *actually* enforced elsewhere, at every subsequent stage (not just Indicator, as SCR-007 checked):

- **Indicator** §20.1: `x_valid` is an AND-chain that includes `quality_gate_pass=true` as one of its conjuncts; `quality_gate_pass=false` rows get `x_warmup_complete=false`, `x_valid=false`, `x=null` unconditionally.
- **Signal Transformation** §23.6: *"Ist ein erforderlicher S3-Indikator ungültig, ist die abhängige S4-Transformation ebenfalls ungültig ... Ein nachgelagerter gültiger numerischer Ausdruck darf einen ungültigen Inputstatus nicht verdecken."* — propagation is explicit and mandatory.
- **Regime and Gate** §7.4: *"`regime_raw = UNKNOWN`, wenn: `quality_gate_pass=false` ist, ..."* — `quality_gate_pass=false` is listed as a **direct, explicit** condition forcing `regime_raw=UNKNOWN` (and therefore `regime_valid=false`, per §12.5's own rule that `regime_valid=false` implies `regime_raw=UNKNOWN` or `regime_effective=UNKNOWN`). §12.7.1 additionally names a dedicated reason code, `REG_INPUT_QUALITY_GATE_FAILED bei quality_gate_pass=false`, confirming this is a first-class, independently-implemented rule at the regime stage, not merely inherited transitively through upstream fields.
- **Regime and Gate** §13.2: `data_gate_pass = quality_gate_pass` verbatim, and §13.3 makes `data_gate_pass=false` force `BLOCK_BOTH` unconditionally, overriding any profile.

**Answer to question 6 (could two conformant implementations diverge?)**: No — every stage independently and explicitly re-derives invalidity from `quality_gate_pass=false` via its own MUST-level formula; there is no stage in the chain where a conforming implementation could produce a valid derived value for such a row without separately violating an explicit, MUST-strength rule specific to that stage. The "insbesondere" wording at the abstract §5.8 principle level is a style choice consistent with how Data Pipeline states every other global principle (in general terms, delegating concrete, testable enforcement to the owning stage specification — the same pattern independently confirmed for row-count invariants in `RCC_002_SCR_007_MAJOR_FINDINGS_VERIFICATION_2026-07-27.md` Section 5).

**Urteil: `REJECTED`** (no functional gap exists; enforcement is redundant and explicit at every single stage, not merely implicit).

**Independent severity: `Observation`** — a cosmetic tightening of §5.8's wording is possible but not required; not included in the confirmed correction set.

---

### SCR7-MIN-02 — Label and Forward Return §17.4 vs. §18.3

Full quotes re-confirmed:

> §17.4 "Tail": *"Für die letzten `h` Zeilen eines Datensatzes fehlen regulär vollständige Zukunftsdaten. Diese Werte sind ungültig mit: `LBL_FUTURE_HORIZON_INCOMPLETE`. Sie werden nicht mit null aufgefüllt und nicht entfernt."*

> §18.3 "Nullsemantik": *"Wenn ein familienbezogenes `*_valid_h=false` ist: alle numerischen Felder dieser Familie und dieses Horizonts sind `null`; ..."*

**Question 3/4 (real contradiction, or editorial ambiguity?)**: A genuine textual ambiguity exists. Read in isolation, §17.4's "Sie werden nicht mit null aufgefüllt" ("they are not padded with null") could be read either as (a) a statement about the *row* not being backfilled/deleted (a row-retention statement, consistent with §18.3), or (b) a statement about the *field value itself* not being represented as null (which would directly contradict §18.3's explicit "sind `null`" for the same scenario, since tail rows necessarily have `*_valid_h=false`). Both readings are grammatically plausible from §17.4 alone.

**Question 5 (already unambiguously normed elsewhere?)**: Yes — §18.3 is titled "Nullsemantik" and is structurally the document's dedicated, authoritative null-representation section; §17.4 sits under §17 ("Vollständiger Horizont" / gap / tail handling), a chapter about horizon completeness and row retention, not field-level null representation. By document structure, §18.3 governs the actual field representation question.

**Question 6 (could two conformant implementations diverge)**: Yes, plausibly — an implementer reading only §17.4 could leave tail-row numeric fields un-nulled or otherwise represented, producing output that fails §18.3's explicit requirement, which is the actually-controlling rule.

**Urteil: `CONFIRMED`**

**Independent severity: `Minor`** — resolvable by reading the document as a whole (§18.3 controls), but the literal text of §17.4 states the opposite of §18.3 for the same case; a wording fix removes the ambiguity at its source rather than relying on cross-section reconciliation. Minimal fix: reword §17.4's last sentence to something like *"Diese Zeilen werden nicht entfernt und nicht durch synthetische Ersatzzeilen ersetzt; die betroffenen Feldwerte folgen der Nullsemantik aus §18.3."*

---

### SCR7-MIN-03 — Property-based tests pinned at SHOULD

Quotes re-confirmed:

> Indicator §27.8: *"SHOULD geprüft werden: ... `x_valid=true` impliziert `x_warmup_complete=true`; kein Feld mit einem invalidierenden Reason Code besitzt `x_valid=true`; ..."*

> Signal Transformation §29.10: *"SHOULD geprüft werden: ... kein invalidierender Reason Code tritt bei `y_valid=true` auf; kein Basisfeld besitzt ein nullbares `y_valid` oder `y_reason_codes`; ..."*

**Question 5 (already unambiguously normed elsewhere?) — checked independently for each document, which SCR-007 did not do:**

- **Indicator**: §30 Publication Gate criterion 16 states, as a MUST-level (Publication-blocking) requirement: *"Golden-, Schema-, Segment-, Kausalitäts- und Property-Tests bestanden sind"* — i.e., passing the property tests (the same test category §27.8 labels SHOULD) is itself a **mandatory precondition for S3 publication**. The "SHOULD" in §27.8 therefore describes the recommended *content* of the property-test suite; the *obligation to run and pass it before publication* is enforced at MUST-strength by the Publication Gate. No functional gap exists for Indicator.
- **Signal Transformation**: §32 Publication Gate (criteria 1–17) was checked line by line; it names "Grenzwert-, Ankerwert-, Monotonie- und Kausalitätstests" (criterion 9) explicitly, but contains **no criterion naming property-based tests** as a publication precondition, unlike Indicator's criterion 16. This is a genuine asymmetry between the two sibling documents: the same invariant class (validity-implication properties) is publication-gated at MUST-strength in Indicator but not in Signal Transformation.

**Urteil: `PARTIALLY CONFIRMED`** — REJECTED for Indicator (already enforced at MUST-strength via §30 criterion 16); CONFIRMED for Signal Transformation (no equivalent MUST-strength backstop in §32).

**Independent severity**: `Observation` for Indicator (no correction needed); `Minor` for Signal Transformation. Minimal fix: add one criterion to Signal Transformation §32, mirroring Indicator's own pattern, e.g. *"18. Property-Tests bestanden sind"* — a one-line, non-architectural addition that brings Signal Transformation into line with Indicator's already-correct pattern. Do not elevate §29.10 itself from SHOULD to MUST (that would be a larger, less consistent change than adding the missing Gate criterion, and would depart from the pattern actually used elsewhere).

---

### SCR7-MIN-04 — Generator read/hash asymmetry

Re-confirmed directly in `scripts/build_rcc002_spec_bundle.py::build_bundle()`: `content = path.read_text(encoding="utf-8")` (subject to universal-newline translation) is used for embedded text, while `raw_bytes = path.read_bytes()` (untranslated) is used for the per-file SHA-256 shown in the bundle table.

**Question 6/7**: On the current repository, all seven source files are confirmed LF-only (the round-trip test performed for both `RCC-002-SCR-007` and this verification's own input-control context reproduces the bundle byte-for-byte), so `content` and `raw_bytes.decode()` currently coincide exactly — **the deviation this finding describes cannot currently manifest**, because there is no CRLF source file in the repository for it to act on.

Per this task's own explicit instruction — *"Eine bereits durch Tests ausgeschlossene Abweichung darf nicht als aktueller Minor Defect bestehen bleiben"* — a deviation that the passing round-trip test has already excluded from actually occurring must not remain classified as a **current** Minor defect.

**Urteil: `CONFIRMED`** as an accurate description of the code's structure and its latent (not currently manifesting) risk under a hypothetical future CRLF source file.

**Independent severity: `Future Architecture Risk` / `Observation`**, downgraded from Minor. Not included in the confirmed correction set for this cycle; recorded as a defensive-hardening suggestion only (hash `content.encode("utf-8")` instead of `raw_bytes`, or add a `.gitattributes` rule enforcing LF for `docs/specifications/*.md`), to be picked up opportunistically, not as a required correction now.

---

### SCR7-MIN-05 — RFC-2119 keyword underuse

Re-confirmed: Data Pipeline §2 formally defines `MUST/MUST NOT/SHOULD/SHOULD NOT/MAY`; the document body uses the literal keywords sparingly, carrying most normative force via German modal verbs ("muss", "darf nicht").

**Question 3/6**: No instance was found, across any of the specification family's documents examined in this or the prior two verification passes, where a German modal verb was demonstrably read at a weaker-than-intended strength, or where this caused two readings to diverge on an actual requirement. This repository's own project-level documentation (`CLAUDE.md`) records that a German/English mix is the established, expected convention across this repository's documents, not an anomaly requiring a fix. "Muss"/"darf nicht" read unambiguously as MUST/MUST NOT-equivalent throughout ordinary German normative/technical usage, and every specific requirement checked in three successive verification passes resolved without needing to invoke the RFC-2119 keyword definitions to disambiguate.

**Urteil: `REJECTED`** (no demonstrated ambiguity or divergence risk).

**Independent severity: `Observation`** — not included in the confirmed correction set.

---

### SCR7-MIN-06 — Regime and Gate §5.8 coincidental numbering collision

Re-confirmed: Regime and Gate's own local §5.8, titled "Profilversionen", is a profile-ID/version table, unrelated in content to Data Pipeline's Row-Preservation §5.8.

**Question 8 (is a change actually required)**: No functional defect exists — no cross-document citation was found (in any of the seven documents, across three verification passes) that references "§5.8" ambiguously between the two meanings; each document's own §5.8 is unambiguous in its own local context, and all genuine cross-references to Data Pipeline's Row-Preservation principle spell out the target document explicitly (*"...aus `RCC_002_DATA_PIPELINE_SPECIFICATION` §5.8"*), never a bare "§5.8". Renumbering Regime and Gate's own section would itself carry a non-trivial risk: it is a live, heavily cross-referenced document, and renumbering could disturb internal cross-references within Regime and Gate itself that were not audited as part of this narrow check — this would trade a purely cosmetic, non-manifesting risk for a concrete editing risk, which the task's own working rules caution against ("keine unnötige doppelte Normierung", implicitly extending to "no correction whose cost exceeds its benefit").

**Urteil: `REJECTED`** (as requiring correction in this cycle).

**Independent severity: `Observation` / `Future Architecture Risk`** — worth keeping in mind for a future numbering-convention pass across the whole family, but not a confirmed correction now.

---

### SCR7-MIN-07 — Reproducibility Document-Control staleness

Re-confirmed verbatim:

> Header, line 13: *"Status | SCR-005-Corrected Draft – Scientific Consistency Re-Review 006 Pending"*

> §29: *"Der aktuelle Status lautet: SCR-005-Corrected Draft – Scientific Consistency Re-Review 006 Pending"*, followed by "Nächste vorgeschriebene Schritte" that lists SCR-006 as still pending (step 3), even though SCR-006's scientific trust function has since been formally replaced by `RCC-002-SCR-007` (per that report's own Section 3), and the same Reproducibility document's own normative body already contains post-C1/post-AIR-003 content (§8.7.1, §18.4, the §5.8 cross-reference).

**Question 7**: Exclusively documentation/governance-metadata; no effect on scientific results or stage behavior.

**Urteil: `CONFIRMED`**.

**Independent severity: `Minor`** — trivially correctable; naturally bundled with the version-bump correction for this document (Section 14), since both touch the same Document-Control block.

---

### SCR7-MIN-08 — No dedicated S8 Publication Gate chapter

SCR-007's original framing ("S8 lacks a chapter analogous to every other stage's Publication Gate") was re-examined against the same delegation-pattern evidence established in `RCC_002_SCR_007_MAJOR_FINDINGS_VERIFICATION_2026-07-27.md` (Section 5): Reproducibility's own declared scope explicitly covers S8, and its §25 "Veröffentlichungs-Gate" **does** function as the S8/dataset-level publication gate — so "no chapter exists at all" is not accurate; Reproducibility does have one.

However, direct re-reading of §25's full checklist (all ~29 items) finds it explicitly names contract-verification items for other stage boundaries by number — *"S2-Qualitäts- und Segmentvertrag eindeutig nachgewiesen"*, *"S5-/S6-Verträge eindeutig nachgewiesen"*, *"S7-Horizon- und Feldnamensraum eindeutig nachgewiesen"*, *"stufenbasierte und präfixbasierte S7-Leakage-Tests bestanden"* — but contains **no equivalent, explicitly-named item for the S7→S8 boundary**, even though the very same document defines a concrete, falsifiable test for exactly that boundary in §18.4 (*"S8_rows == S7_rows; vollständige Row Identity Preservation; vollständige Row Order Preservation; Manifest-Konsistenz; Hash-Konsistenz"*). Generic items in §25 ("alle Bytehashes gültig", "alle semantischen Fingerprints gültig") could incidentally catch some failure modes but do not explicitly require §18.4's reconciliation test to have passed as a **named** publication precondition, unlike the explicit treatment given to S2/S5-S6/S7.

**Urteil: `PARTIALLY CONFIRMED`** — narrower than SCR-007's original framing (no dedicated *chapter* is missing; Reproducibility's §25 already is the S8 publication gate), but a real, confirmed asymmetry exists: §25's checklist lacks an explicit item mirroring the document's own §18.4 S7→S8 reconciliation test, unlike its explicit treatment of every other named stage boundary.

**Independent severity: `Minor`** — minimal fix: add one checklist item to §25, e.g. *"S7→S8-Row-Preservation-Reconciliation (§18.4) bestanden"*, immediately after the existing S7 item. This is a one-line addition, not a new chapter and not an architecture change.

---

### SCR7-MAJ-02 (Minor candidate) — Reproducibility §12.3

Already fully verified in `RCC_002_SCR_007_MAJOR_FINDINGS_VERIFICATION_2026-07-27.md` Section 6: **CONFIRMED** as fact (table stale by 1–2 generations for six of seven entries; self-contradicts the host document's own version), **Minor** severity (confined to the "Knowledge Lineage" decision-log chapter, distinct from the technical manifest schema in §24, which carries its own explicit "use real values" safeguard; no build-execution consumption path found). No new evidence in this pass changes that conclusion; see Section 7 below for the exact target state.

---

### SCR7-MAJ-03 (Minor candidate) — Zero version increment + stale dependency citations

Already fully verified in `RCC_002_SCR_007_MAJOR_FINDINGS_VERIFICATION_2026-07-27.md` Section 7: **CONFIRMED** as fact on both sub-parts, **Minor** severity (exclusively versioning/documentation in character; no divergent-implementation risk since each specification exists as a single current file, not multiple coexisting versioned copies). This verification adds the document-by-document version-increment justification required by this task's Teil C.2 in Section 8 below.

---

## 7. Reproducibility §12.3 Assessment

**Fully correct current version values for all seven specifications** (ground truth: each document's own header field, independently re-confirmed by direct `grep`):

| Document ID (as used in §12.3) | Actual current version |
|---|---|
| `RCC_002_DATA_PIPELINE_SPECIFICATION` | `0.7.1` |
| `RCC-002-DV` | `0.4.1` |
| `RCC-002-IS` | `0.4.1` |
| `RCC-002-ST` | `0.4.0` |
| `RCC-002-RG` | `0.5.0` |
| `RCC-002-LF` | `0.4.0` |
| `RCC-002-RM` | `0.6.0` |

These are the versions **as they stand before** the corrections in this plan are applied. Section 8 below determines which of these seven values must additionally change as part of this correction cycle; Section 9 (Dependency Matrix) and Section 15 give the **final target state** that §12.3 (and every citing document) must reflect once all corrections in this plan are applied together, so that the table is only edited once rather than twice.

Exact defined target state for §12.3 after applying Section 8's version plan: see Section 15 ("Final §12.3 Target Table").

---

## 8. Version Assessment

Version increments are **not applied uniformly**; each is justified individually against Data Pipeline's own compatibility rule (§6.4: *"Patch: redaktionelle oder nichtsemantische Metadatenkorrektur; Minor: additive optionale Felder ohne Änderung bestehender Semantik; Major: Entfernung, Umbenennung, Typänderung, neue Nullsemantik, Schlüsseländerung oder fachliche Bedeutungsänderung."*) and against what actually changed in each document's own text since its current version was set.

| Document | Current version | Normative changes since current version | Purely editorial changes since current version | Required new version | Classification and justification |
|---|---|---|---|---|---|
| Data Pipeline | `0.7.1` | None — confirmed via the bundle manifest's own change table ("in diesem Zyklus unverändert") and independently by full-document re-reading; no `_rows =` equation or other content was added in Round 2 | None | **`0.7.1` (unchanged)** | No change occurred in this document since its last (correctly-applied) patch bump; no version action needed |
| Data Validation | `0.4.1` | None beyond the already-versioned C1 wording fix | One new sentence: `§5.8`-Rückverweis (a pure cross-reference pointer to Data Pipeline §5.8, adding no new obligation — the substantive content it points to, §20 Kriterium 16, was already present and already correctly reflected in the `0.4.1` version) | **`0.4.2`** | Patch — matches Data Pipeline §6.4's own "redaktionelle... Metadatenkorrektur" category exactly; a pure cross-reference addition is the paradigm case for Patch |
| Indicator | `0.4.1` | None beyond the already-versioned C1 wording fix | One new sentence: `§5.8`-Rückverweis (same pattern as Data Validation) | **`0.4.2`** | Patch — same reasoning as Data Validation |
| Signal Transformation | `0.4.0` | None | One new sentence: `§5.8`-Rückverweis | **`0.4.1`** | Patch — same reasoning; this document never received a version step for any part of the correction cycle until now |
| Regime and Gate | `0.5.0` | None | One new sentence: `§5.8`-Rückverweis | **`0.5.1`** | Patch — same reasoning |
| Label and Forward Return | `0.4.0` | None from the version-increment perspective; separately, this plan's Section 14 also corrects the §17.4/§18.3 wording ambiguity (SCR7-MIN-02) in the same document | One new sentence: `§5.8`-Rückverweis, plus the SCR7-MIN-02 wording correction (itself a clarification of already-intended semantics, not a change in required behavior — §18.3 already controlled the actual outcome) | **`0.4.1`** | Patch — the §5.8 cross-reference is Patch-class on its own; the §17.4 wording clarification is likewise Patch-class per Data Pipeline §6.4 ("redaktionelle... Metadatenkorrektur", since it does not change the actual required behavior, only removes an ambiguous sentence), so both changes together still classify as Patch, not Minor |
| Reproducibility | `0.6.0` | New `MUST`-level invariant (§8.7.1, `S8_rows = S7_rows`) and a new mandatory reconciliation test (§18.4) — genuinely new normative text, not merely a rewording of an existing criterion; additionally, this plan's Section 14 corrects §12.3 (stale table), the Status field/§29 (stale governance narrative, SCR7-MIN-07), and adds one Publication Gate checklist item to §25 (SCR7-MIN-08) | `§5.8`-Rückverweis | **`0.7.0`** | Minor — per Data Pipeline §6.4, "additive... ohne Änderung bestehender Semantik": §8.7.1/§18.4 add previously-unstated but not-previously-contradicted content (the general obligation already existed via Data Pipeline §5.8's "über alle nachgelagerten Stufen hinweg"); no removal, rename, type change, or semantic-meaning change occurred, so Major is not warranted; the change exceeds pure "redaktionelle Metadatenkorrektur" because a genuinely new, previously-unstated concrete invariant and test requirement is introduced, so Patch is insufficient — Minor is the correct classification |

**Versions are not raised for any document beyond what is individually justified above.** No document receives a version increment solely because other documents in the family are being bumped.

---

## 9. Dependency Matrix

7×7 matrix: rows = citing document, columns = cited document, cell = declared version currently cited → correct version to cite after this plan's corrections are applied (Section 8). A dash means the citing document does not declare a dependency on that document (either because none exists, or because the cited document is downstream, not upstream, of the citing one — no such reverse citations exist anywhere in the family, confirmed by direct search across all seven documents in this and the prior two verification passes).

| Citing → / Cited ↓ | Data Pipeline | Data Validation | Indicator | Signal Transf. | Regime and Gate | Label | Reproducibility |
|---|---|---|---|---|---|---|---|
| **Data Pipeline** | — | — | — | — | — | — | — |
| **Data Validation** | `0.7.0` → **`0.7.1`** | — | — | — | — | — | — |
| **Indicator** | `0.7.0` → **`0.7.1`** | `0.4.0` → **`0.4.2`** | — | — | — | — | — |
| **Signal Transformation** | `0.7.0` → **`0.7.1`** | `0.4.0` → **`0.4.2`** | `0.4.0` → **`0.4.2`** | — | — | — | — |
| **Regime and Gate** | `0.7.0` → **`0.7.1`** | `0.4.0` → **`0.4.2`** | `0.4.0` → **`0.4.2`** | `0.4.0` → **`0.4.1`** | — | — | — |
| **Label and Forward Return** | `0.7.0` → **`0.7.1`** | `0.4.0` → **`0.4.2`** | `0.4.0` → **`0.4.2`** | `0.4.0` → **`0.4.1`** | `0.5.0` → **`0.5.1`** | — | — |
| **Reproducibility** | `0.7.0` → **`0.7.1`** | `0.4.0` → **`0.4.2`** | `0.4.0` → **`0.4.2`** | `0.4.0` → **`0.4.1`** | `0.5.0` → **`0.5.1`** | `0.4.0` → **`0.4.1`** | — (self) |

**On dependency binding style**: the family's existing model cites each dependency as a single, exact document version (e.g., "Version 0.7.0"), not as a compatible-range or unversioned reference. This plan introduces **no new versioning architecture** — it keeps this exact single-version-citation model and simply corrects the cited value in each case to match the actual current (post-correction) version of the cited document, per the task's explicit instruction not to introduce a new versioning scheme for this cycle.

---

## 10. RFC-2119 Assessment

Covered in full under Section 6 (SCR7-MIN-05): `REJECTED`. No location was found, across any document, where a German modal verb ("muss", "darf nicht", "soll", "darf") produced a materially different normative strength than the formally-defined RFC-2119 keyword it stands in for, and no cross-document disagreement traceable to this stylistic pattern was found. No correction included in the confirmed set.

---

## 11. Generator and Newline Assessment

Covered in full under Section 6 (SCR7-MIN-04). The generator's `read_text()`/`read_bytes()` asymmetry is a real, latent characteristic of the code, but:
- the documented, executed round-trip test (byte-exact match, independently reproduced in `RCC_002_SCR_007_FULL_SCOPE_REPLACEMENT_REVIEW_2026-07-27.md` Section 7 and re-confirmed for this plan) already excludes this deviation from manifesting on the current, all-LF repository state;
- per this task's explicit rule, a deviation already excluded by a passing test must not remain classified as a current Minor defect.

Reclassified: `Future Architecture Risk` / `Observation`. Not included in the confirmed correction set for this cycle.

---

## 12. Cross-Reference Assessment

Every genuine cross-reference to Data Pipeline's Row-Preservation principle found across the family (Data Validation §20 Kriterium 16; Indicator §26.2; Signal Transformation §28.2; Regime and Gate §30; Label §22; Reproducibility §8.7.1) was independently re-checked for: (a) existence of the target paragraph — confirmed, Data Pipeline §5.8 exists and contains the quoted principle in every case; (b) correct document naming — confirmed, all six citing documents name `RCC_002_DATA_PIPELINE_SPECIFICATION` (or an unambiguous equivalent) correctly; (c) version correctness — not applicable, since these are paragraph-level cross-references, not document-version citations (those are covered separately in Section 9); (d) semantically matching target content — confirmed in every case, the cited §5.8 content matches the concretization claimed by the citing document.

The one coincidental, non-substantive numbering collision (Regime and Gate's own local §5.8, "Profilversionen") was assessed in Section 6 (SCR7-MIN-06): `REJECTED` as requiring correction — no genuine cross-document citation was ever found to rely on the bare, undisambiguated string "§5.8" in a way that could resolve to the wrong document, since every real cross-reference explicitly names its target document.

No additional cross-reference is recommended anywhere in this plan beyond what Section 14 already lists, per the task's instruction to recommend additional cross-references only where a real ambiguity would otherwise exist — none was found beyond the items already in the confirmed correction set.

---

## 13. Confirmed Correction Set

Only the following are included as required corrections (all other candidates were rejected or reclassified as Observation/Future Architecture Risk in Sections 6/10/11 and are explicitly excluded from this set):

1. **SCR7-MIN-02** — Label and Forward Return §17.4 wording correction.
2. **SCR7-MIN-03 (Signal Transformation only)** — add one Property-Tests criterion to Signal Transformation §32.
3. **SCR7-MIN-07** — Reproducibility Status field / §29 governance-narrative refresh.
4. **SCR7-MIN-08** — add one S7→S8 reconciliation criterion to Reproducibility §25.
5. **SCR7-MAJ-02** — Reproducibility §12.3 table correction.
6. **SCR7-MAJ-03** — version increments (Section 8) and dependency-citation corrections (Section 9) across six documents.

---

## 14. File-by-File Correction Plan

### `docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`

No correction required. No confirmed finding touches this document; its content and version (`0.7.1`) remain unchanged.

### `docs/specifications/RCC_002_DATA_VALIDATION_2026-07-23.md`

| Field | Value |
|---|---|
| Finding ID | SCR7-MAJ-03 |
| Current state | Version `0.4.1`; Document-Control cites Data Pipeline as "Version 0.7.0" |
| Affected paragraph | Document-Control metadata table (line ~15) |
| Change type | Dependency Correction + Version Correction |
| Exact change | Update "Übergeordnetes Dokument" cell from "Version 0.7.0" to "Version 0.7.1"; update own Version field from `0.4.1` to `0.4.2` |
| New document version | `0.4.2` |
| Dependent follow-up changes | None (no document cites Data Validation's own version except Indicator, Signal Transformation, Regime and Gate, Label, and Reproducibility — all separately corrected below to cite `0.4.2`) |
| Required tests | None (metadata-only change) |
| Required re-review | Re-inclusion in bundle regeneration and hash re-verification (Section 16) |

### `docs/specifications/RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md`

| Field | Value |
|---|---|
| Finding ID | SCR7-MAJ-03 |
| Current state | Version `0.4.1`; Document-Control cites Data Pipeline as "0.7.0", Data Validation as "0.4.0" |
| Affected paragraph | Document-Control metadata table (lines ~15–16) |
| Change type | Dependency Correction + Version Correction |
| Exact change | Update Data Pipeline citation to "0.7.1"; update Data Validation citation to "0.4.2"; update own Version field from `0.4.1` to `0.4.2` |
| New document version | `0.4.2` |
| Dependent follow-up changes | Signal Transformation, Regime and Gate, Label, Reproducibility all cite Indicator's version — separately corrected below to cite `0.4.2` |
| Required tests | None (metadata-only) |
| Required re-review | Bundle regeneration and hash re-verification |

### `docs/specifications/RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md`

| Field | Value |
|---|---|
| Finding ID | SCR7-MIN-03 (Signal Transformation only) + SCR7-MAJ-03 |
| Current state | Version `0.4.0`; Document-Control cites Data Pipeline "0.7.0", Data Validation "0.4.0", Indicator "0.4.0"; §32 Publication Gate has 17 criteria, none naming Property-Tests |
| Affected paragraphs | Document-Control metadata table (lines ~15–16); §32 (Publication Gate) |
| Change type | Normative Correction (§32 addition) + Dependency Correction + Version Correction |
| Exact change | (a) Add new §32 criterion: *"18. Property-Tests bestanden sind"* (or integrated at an appropriate position, renumbering the trailing "Manifest, Rollenregister und Checksummen vollständig sind" item to 19 if inserted before it); (b) update Data Pipeline citation to "0.7.1", Data Validation to "0.4.2", Indicator to "0.4.2"; (c) update own Version field from `0.4.0` to `0.4.1` |
| New document version | `0.4.1` |
| Dependent follow-up changes | Regime and Gate, Label, Reproducibility all cite Signal Transformation's version — separately corrected below to cite `0.4.1` |
| Required tests | Confirm the existing property-based test suite for Signal Transformation already covers the bullets in §29.10 (it should, since the Gate criterion only newly makes passing them a *named* publication precondition — it does not require new test content) |
| Required re-review | A narrow, targeted re-check that §32's new criterion 18 does not conflict with the `PASS_WITH_APPROVED_EXCEPTIONS` carve-out list (which already excludes overriding "Rollenverletzungen" and similar — should be extended to also exclude overriding a failed Property-Test, for full consistency with Indicator's own carve-out treatment of its criterion 16); bundle regeneration and hash re-verification |

### `docs/specifications/RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md`

| Field | Value |
|---|---|
| Finding ID | SCR7-MAJ-03 |
| Current state | Version `0.5.0`; Document-Control cites Data Pipeline "0.7.0", Data Validation "0.4.0", Indicator "0.4.0", Signal Transformation "0.4.0" |
| Affected paragraph | Document-Control metadata table (lines ~15–16) |
| Change type | Dependency Correction + Version Correction |
| Exact change | Update citations to "0.7.1" / "0.4.2" / "0.4.2" / "0.4.1" respectively; update own Version field from `0.5.0` to `0.5.1` |
| New document version | `0.5.1` |
| Dependent follow-up changes | Label and Reproducibility cite Regime and Gate's version — separately corrected below to cite `0.5.1` |
| Required tests | None (metadata-only) |
| Required re-review | Bundle regeneration and hash re-verification |

### `docs/specifications/RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md`

| Field | Value |
|---|---|
| Finding ID | SCR7-MIN-02 + SCR7-MAJ-03 |
| Current state | Version `0.4.0`; §17.4 contains the ambiguous "nicht mit null aufgefüllt" clause; Document-Control cites Data Pipeline "0.7.0", Data Validation "0.4.0", Indicator "0.4.0", Signal Transformation "0.4.0", Regime and Gate "0.5.0" |
| Affected paragraphs | §17.4; Document-Control metadata table |
| Change type | Normative Correction (wording clarification, no behavior change) + Dependency Correction + Version Correction |
| Exact change | (a) Reword §17.4's final sentence to: *"Diese Zeilen werden nicht entfernt und nicht durch synthetische Ersatzzeilen ersetzt; die betroffenen Feldwerte folgen der Nullsemantik aus §18.3."*, replacing "Sie werden nicht mit null aufgefüllt und nicht entfernt."; (b) update the five dependency citations to "0.7.1" / "0.4.2" / "0.4.2" / "0.4.1" / "0.5.1"; (c) update own Version field from `0.4.0` to `0.4.1` |
| New document version | `0.4.1` |
| Dependent follow-up changes | Reproducibility cites Label's version — separately corrected below to cite `0.4.1` |
| Required tests | Confirm no existing test or downstream text relies on the literal (ambiguous) former wording of §17.4; none was found in this or the prior two verification passes |
| Required re-review | A targeted re-read of §17/§18 together to confirm the reworded §17.4 and existing §18.3 are now unambiguous as a pair; bundle regeneration and hash re-verification |

### `docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md`

| Field | Value |
|---|---|
| Finding ID | SCR7-MIN-07 + SCR7-MIN-08 + SCR7-MAJ-02 + SCR7-MAJ-03 |
| Current state | Version `0.6.0`; Status field and §29 describe "SCR-005-Corrected Draft – Scientific Consistency Re-Review 006 Pending"; §12.3 lists stale/self-contradictory versions; §25 lacks an S7→S8 reconciliation checklist item; Document-Control dependency citations are stale |
| Affected paragraphs | Header (Status, Version, Primäre Abhängigkeit, Fachliche Abhängigkeiten); §12.3; §25; §29 |
| Change type | Version Correction + Dependency Correction + Normative Correction (§25 addition, purely additive) + Editorial Correction (§12.3, Status, §29) |
| Exact change | (a) Update own Version field from `0.6.0` to `0.7.0`; (b) update Status field to reflect actual current governance state (e.g., *"C1-Corrected; RCC-002-SCR-007 Full-Scope Replacement Scientific Consistency Review completed; Minor Findings verification and correction plan issued; Editorial Pass and Internal Certification pending"* — the exact wording is an editorial matter for whoever applies this plan, not prescribed further here to avoid over-specifying prose that is not this plan's normative concern); (c) update "Primäre Abhängigkeit"/"Fachliche Abhängigkeiten" to cite Data Pipeline "0.7.1", Data Validation "0.4.2", Indicator "0.4.2", Signal Transformation "0.4.1", Regime and Gate "0.5.1", Label "0.4.1"; (d) replace §12.3's table with the values in Section 15 below; (e) add to §25: a new checklist item, positioned after the existing S7 item, reading *"S7→S8-Row-Preservation-Reconciliation (§18.4) bestanden"*; (f) update §29's "Sie aktualisiert die Spezifikationsabhängigkeiten auf" list and its "Der aktuelle Status lautet" / "Nächste vorgeschriebene Schritte" text to match (b) and (c) |
| New document version | `0.7.0` |
| Dependent follow-up changes | None further — Reproducibility has no known dependents within this family |
| Required tests | None beyond the general reconciliation-test requirements already defined in §18.4 (unchanged in substance — this plan only adds a checklist reference to the existing test, it does not alter the test itself) |
| Required re-review | Full re-read of the amended header/§12.3/§25/§29 block for internal self-consistency (no other document reads its own metadata back into itself the way §12.3 currently does, so this is the one location requiring a dedicated self-consistency check after editing); bundle regeneration and hash re-verification |

---

## 15. Required Version Changes

| Document | Version before this plan | Version after this plan |
|---|---|---|
| Data Pipeline | `0.7.1` | `0.7.1` (unchanged) |
| Data Validation | `0.4.1` | `0.4.2` |
| Indicator | `0.4.1` | `0.4.2` |
| Signal Transformation | `0.4.0` | `0.4.1` |
| Regime and Gate | `0.5.0` | `0.5.1` |
| Label and Forward Return | `0.4.0` | `0.4.1` |
| Reproducibility and Manifest | `0.6.0` | `0.7.0` |

**Final §12.3 Target Table** (the exact table Reproducibility §12.3 must contain once all corrections in this plan are applied — this is also the target state for §29's dependency list and for the illustrative `specification_profile` array in §24, for full internal consistency, though §24 already carries its own "use real values" disclaimer and is lower priority):

| Dokument-ID | Version |
|---|---:|
| `RCC_002_DATA_PIPELINE_SPECIFICATION` | `0.7.1` |
| `RCC-002-DV` | `0.4.2` |
| `RCC-002-IS` | `0.4.2` |
| `RCC-002-ST` | `0.4.1` |
| `RCC-002-RG` | `0.5.1` |
| `RCC-002-LF` | `0.4.1` |
| `RCC-002-RM` | `0.7.0` |

---

## 16. Required Validation

After applying the corrections in Section 14 (not performed in this planning cycle):

1. Re-run `scripts/build_rcc002_spec_bundle.py` against the corrected `docs/specifications/` files to regenerate the bundle.
2. Regenerate `docs/review/RCC_002_C1_CORRECTED_BUNDLE_MANIFEST_2026-07-25.md` (or its successor manifest) with the new per-file line/byte/SHA-256 values and the new document versions.
3. Independently recompute SHA-256/line/byte counts for the new bundle and manifest and compare against the newly generated values (input control, as performed in `RCC_002_SCR_007_FULL_SCOPE_REPLACEMENT_REVIEW_2026-07-27.md` Sections 6–7).
4. Perform a fresh generator round-trip test (temporary output, byte-exact comparison, then delete the temporary file) against the corrected source files.
5. Confirm Signal Transformation's existing property-based test suite already exercises every bullet newly named as a Gate precondition in §32 criterion 18 (Section 14); no new test content should be required, only confirmation that existing coverage matches the newly-named criterion.
6. Confirm no other document's text (outside the seven canonical specifications and the review documents already named here) references any of the six pre-correction version strings being changed in Section 15.

---

## 17. Required Re-Review

1. A full hash/round-trip re-verification of the newly regenerated bundle and manifest (as in Section 16), independent of this plan.
2. A targeted, not full-scope, Scientific Consistency re-check limited to: (a) the reworded Label §17.4 read together with §18.3, (b) the new Signal Transformation §32 criterion 18 read together with its existing `PASS_WITH_APPROVED_EXCEPTIONS` carve-out list, (c) the corrected Reproducibility §12.3/§25/header/§29 block for internal self-consistency. A full-scope replacement review of the entire seven-document family is not required again, since no other content changed.
3. A Disposition / Closure Record (a new, separate document, not an edit to `RCC_002_SCR_007_FULL_SCOPE_REPLACEMENT_REVIEW_2026-07-27.md` itself) that formally reconciles: the original SCR-007 verdict (`FAIL`), the Major Findings Verification's reassessment (zero confirmed Major findings), and this Minor Findings Verification's reassessment (six confirmed, non-blocking Minor findings; four candidates rejected or downgraded to Observation/Future Architecture Risk) into one coherent, current, citable review status for RCC-002. This record does not modify SCR-007's own file, consistent with the instruction that the original document remain unaltered.
4. The still-outstanding full-scope replacement Architecture Integrity Review (noted as required but not yet performed by `RCC_002_PRE_CERTIFICATION_STATUS_2026-07-27.md`) remains a separate, independent prerequisite for Editorial Pass and Internal Certification, unaffected by this plan.

---

## 18. SCR-007 Verdict Reassessment

1. **Is there still a confirmed Major Finding?** No. All three of SCR-007's original Major Findings were independently re-derived in `RCC_002_SCR_007_MAJOR_FINDINGS_VERIFICATION_2026-07-27.md`: one rejected outright (SCR7-MAJ-01), two confirmed but reclassified as Minor (SCR7-MAJ-02, SCR7-MAJ-03). This verification pass, covering the eight original Minor Findings, found zero new Major-severity issues.
2. **Is there a certification-blocking Minor Finding?** No. The six confirmed Minor findings (Section 13) are each local, unambiguously correctable by a wording change, a one-line checklist/criterion addition, or a version/citation correction, and none challenges the scientific architecture (row preservation, gate logic, signal derivation, or leakage isolation remain fully sound, as independently re-confirmed across all three verification passes to date).
3. **Was SCR-007's `FAIL` verdict still justified after independent verification?** No — it was justified *at the time SCR-007 was written*, given the finding classifications then in force, but is no longer justified once those classifications are independently re-derived: zero Critical, zero confirmed Major, and only non-blocking Minor findings remain.
4. **Corrected intermediate verdict**: **`PASS WITH MINOR CORRECTIONS`** — per the review order's own rule (*"keine Critical Findings, keine Major Findings, ausschließlich lokale Minor Findings bestehen, diese die wissenschaftliche Grundarchitektur nicht infrage stellen"*), which is exactly the state this three-part verification (SCR-007 → Major Findings Verification → this Minor Findings Verification) establishes.
5. **Review steps to repeat after correction**: Section 16 (validation) and Section 17 (re-review) in full; no new full-scope Scientific Consistency Review of the whole family is required, since the corrections are narrow and localized; the outstanding full-scope replacement Architecture Integrity Review remains independently required regardless of this plan.

---

## 19. Certification Impact

Editorial Pass and Internal Certification remain blocked only by: (a) applying the six confirmed corrections in Section 14, (b) the validation and re-review steps in Sections 16–17, and (c) the still-outstanding, independently-required full-scope replacement Architecture Integrity Review noted in `RCC_002_PRE_CERTIFICATION_STATUS_2026-07-27.md`. No confirmed finding from this or the prior two verification passes blocks certification on scientific-architecture grounds; all remaining blockers are process/completeness steps (apply corrections → re-validate → re-review → complete the still-pending AIR), not open scientific defects.

---

## 20. Final Decision

```text
Findings verified:            10  (8 original Minor + 2 downgraded Major candidates)
Confirmed:                     6  (SCR7-MIN-02, SCR7-MIN-03/Signal-Transformation,
                                    SCR7-MIN-07, SCR7-MIN-08, SCR7-MAJ-02, SCR7-MAJ-03)
Partially Confirmed:            2  (SCR7-MIN-03 overall [split], SCR7-MIN-08 [narrowed])
Rejected:                       4  (SCR7-MIN-01, SCR7-MIN-03/Indicator, SCR7-MIN-05, SCR7-MIN-06)
Duplicate:                      0

Major (reassessed):             0
Minor (reassessed):             6
Observation (reassessed):       4  (includes SCR7-MIN-03/Indicator and SCR7-MIN-04's
                                     Future-Architecture-Risk companion observation)
No Finding:                     0

Certification-blocking findings remaining: none (process/completeness steps remain,
                                             not open scientific or architectural defects)

Recommended corrected SCR-007 intermediate verdict: PASS WITH MINOR CORRECTIONS
```

No file other than this report was created or modified. No specification, bundle, or manifest file was changed. No commit was created.

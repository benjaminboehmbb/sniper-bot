# RCC-002 DVSEV-001 — Targeted Correction Record

## 1. Finding

`DVSEV-001`, from `docs/review/RCC_002_DVSEV_001_REASON_CODE_SEVERITY_CORRECTION_PROPOSAL_2026-07-27.md`
(the approved investigation/correction proposal, independently re-verified
against the working tree before implementation began — matched exactly):
`RCC_002_DATA_VALIDATION` §16.2 requires every registered Reason Code to
possess "eine Standard-Severity", and §24.1 Nr. 3 lists this as a precondition
for `Approved for Implementation` ("alle Reason Codes, Prioritäten, Severities
und Buildwirkungen registriert sind"). Of the 32 registered `DV_`-prefixed
reason codes, only 6 had a severity stated anywhere in the certified text
(`DV_DUPLICATE_CONFLICT`, `DV_OHLC_INVARIANT_FAILED`, `DV_VOLUME_NEGATIVE`,
`DV_PARSE_NUMERIC_FAILED`, `DV_PARSE_TIMESTAMP_FAILED` via the §14.1 bridge,
and `DV_FILE_SUSPECTED_ROW_LIMIT_TRUNCATION` conditionally). The remaining 26
had none, directly blocking deterministic computation of `quality_status`
(§15, "höchste registrierte Severity aller aktiven `quality_reason_codes`")
and `quality_gate_pass` (§15.1). This is a distinct gap from the
already-acknowledged, still-open `Reason-Code-Prioritätsregister` (sort
order) named in §25.1.

## 2. Normative Entscheidung

Per the approved proposal: a new §16.3 "Reason-Code-Severity-Register" is
added to `RCC_002_DATA_VALIDATION`, providing the missing Standard-Severity
for all 32 registered reason codes. The 6 pre-existing explicit assignments
are carried over unchanged; the 26 previously unassigned codes receive a
severity derived exclusively from existing build effects, fail-closed rules,
validation semantics, and governance requirements already stated elsewhere in
the same document (no new criteria invented). No existing rule, reason code,
or severity assignment is altered.

## 3. Geänderte Dateien

| File | Reason |
|---|---|
| `docs/specifications/RCC_002_DATA_VALIDATION_2026-07-23.md` | Primary correction: new §16.3 inserted after §16.2, before §17; own version bump; Review-Nachweis row |
| `docs/specifications/RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md` | Mechanical dependency-citation follow-on only (Data Validation → 0.5.0); own version **unchanged** |
| `docs/specifications/RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md` | Mechanical dependency-citation follow-on only (Data Validation → 0.5.0); own version **unchanged** |
| `docs/specifications/RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md` | Mechanical dependency-citation follow-on only (Data Validation → 0.5.0); own version **unchanged** |
| `docs/specifications/RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md` | Mechanical dependency-citation follow-on only (Data Validation → 0.5.0); own version **unchanged** |
| `docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md` | Mechanical follow-on: header dependency citation, §12.3 table row, Status field, new dated §29 paragraph; own version bumped (Patch) |

**Not changed**: `docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`
— confirmed byte-identical before and after (Section 9). No implementation
file (`rcc002/`, `tests/rcc002/`) was changed — explicitly out of scope for
this cycle.

## 4. Versionsänderungen

| Document | Before | After | Change type |
|---|---|---|---|
| Data Pipeline | `0.7.1` | `0.7.1` | Unchanged |
| Data Validation | `0.4.2` | `0.5.0` | **Minor** — additive normative content, closes an existing MUST-level registration gap, no existing semantics altered |
| Indicator | `0.4.3` | `0.4.3` | **Unchanged** — mechanical citation-only follow-on |
| Signal Transformation | `0.4.2` | `0.4.2` | **Unchanged** — mechanical citation-only follow-on |
| Regime and Gate | `0.5.1` | `0.5.1` | **Unchanged** — mechanical citation-only follow-on |
| Label and Forward Return | `0.4.1` | `0.4.1` | **Unchanged** — mechanical citation-only follow-on |
| Reproducibility and Manifest | `0.7.1` | `0.7.2` | **Patch** — mechanical citation/profile correction only, no normative content change |

## 5. Exakte Textänderung — Data Validation §16.3

New subsection inserted verbatim after §16.2's closing sentence
("Threadplanung, Eingabedateireihenfolge oder Hash-Iteration abhängen.") and
before "## 17. Reconciliation zwischen Stufen": a 32-row table (`#`, Reason
Code, Standard-Severity, Normative Referenz), two lead-in paragraphs stating
the register's purpose and its relationship to pre-existing explicit
assignments, and one closing paragraph attributing the newly-derived
assignments to this correction cycle with a reference to the underlying
proposal document. Full text: see the specification file itself
(`docs/specifications/RCC_002_DATA_VALIDATION_2026-07-23.md`, §16.3) and the
identical draft in
`docs/review/RCC_002_DVSEV_001_REASON_CODE_SEVERITY_CORRECTION_PROPOSAL_2026-07-27.md`
§1.

No existing sentence in §16.1, §16.2, or any other section of Data Validation
was altered or removed.

### Document-Control header (Data Validation)

`Version` field incremented (`0.4.2`→`0.5.0`). One new Review-Nachweis row
added, following the established table format:

> "| Reason-Code-Severity-Korrekturzyklus | `RCC-002-DVSEV-001` umgesetzt | Version 0.5.0, 2026-07-27: neuer Abschnitt 16.3 „Reason-Code-Severity-Register" ergänzt die in §16.2 geforderte, bislang für 26 von 32 Reason Codes fehlende Standard-Severity und schließt damit die Abnahmevoraussetzung §24.1 Nr. 3. Additive Ergänzung; keine bestehende Regel, kein bestehender Reason Code und keine bestehende Severity-Zuweisung wurde verändert. |"

## 6. Mechanische Folgeänderungen

| Document | Field changed | Old value | New value | Reason |
|---|---|---|---|---|
| Indicator | Header "Direkte Abhängigkeit" (Data Validation) | `0.4.2` | `0.5.0` | Data Validation's own version changed |
| Signal Transformation | Header "Direkte Abhängigkeiten" (Data Validation) | `0.4.2` | `0.5.0` | Same |
| Regime and Gate | Header "Direkte Abhängigkeiten" (Data Validation) | `0.4.2` | `0.5.0` | Same |
| Label and Forward Return | Header "Direkte Abhängigkeiten" (Data Validation) | `0.4.2` | `0.5.0` | Same |
| Reproducibility | Header "Fachliche Abhängigkeiten" (Data Validation) | `0.4.2` | `0.5.0` | Same |
| Reproducibility | §12.3 table, `RCC-002-DV` row | `0.4.2` | `0.5.0` | Same |
| Reproducibility | §12.3 table, `RCC-002-RM` row (self) | `0.7.1` | `0.7.2` | Reproducibility's own version changed (Section 4) |
| Reproducibility | New §29 paragraph | — | Appended, mechanical | Documents the mechanical patch, following this document's established per-version changelog-paragraph convention; prior version-labeled paragraphs left unmodified (historical accuracy preserved, same pattern as the two prior correction cycles) |
| Reproducibility | Header "Status" field | Prior text | Appended "DVSEV-001-Folgekorrektur (Data-Validation-Abhängigkeit) mechanisch nachgezogen" | Factual update, not a new normative rule |
| Reproducibility | §29 "Der aktuelle Status lautet" | Prior text | Appended DVSEV-001 completion clause | Factual update, mirrors header Status field |

Indicator, Signal Transformation, Regime and Gate, and Label and Forward
Return received **only** the citation-value correction in the table above —
no changelog row, no version change, consistent with the approved proposal's
version matrix (all four listed as unchanged).

## 7. Validierung

| Check | Result |
|---|---|
| §16.3 contains a severity for all 32 codes registered in §16.2 | PASS — programmatically verified, exact set match, same order |
| No code added or removed relative to §16.2's Mindestcodes list | PASS — set difference empty in both directions |
| No severity cell empty or malformed | PASS |
| All 6 pre-existing explicit severities preserved unchanged (`DV_DUPLICATE_CONFLICT`, `DV_OHLC_INVARIANT_FAILED`, `DV_VOLUME_NEGATIVE`, `DV_PARSE_NUMERIC_FAILED`, `DV_PARSE_TIMESTAMP_FAILED` = `CRITICAL`) | PASS — programmatically verified against §16.3 table cells |
| No existing rule in §5.2, §6–§14, §15, §20, §25.1 altered | PASS — targeted diff review; only §16.2's trailing blank line and the new §16.3 block were touched |
| `quality_status`/`quality_gate_pass` formulas (§15, §15.1) unaltered | PASS |
| §20 Publication Gate criterion 12 and exception clause unaltered | PASS |
| §25.1 "Reason-Code-Prioritätsregister" (distinct, still-open gap) unaffected | PASS — not referenced or resolved by this cycle |
| Version matrix is consistent | PASS — Section 4, independently re-verified against all seven document headers after editing |
| All live dependency references to Data Validation are current (`0.5.0`) | PASS — full-family grep found zero stale citations of Data Validation `0.4.2` outside historical narrative blocks (which correctly retain pre-cycle values) |
| Reproducibility §12.3 is current | PASS — all seven rows match the post-cycle header versions exactly, including the self-reference |
| No implementation file (`rcc002/`, `tests/rcc002/`) touched | PASS — confirmed via `git status --porcelain rcc002 tests/rcc002`, both fully untracked/unchanged |
| No other normative change made | PASS — confirmed via targeted diff review of every edited location |

## 8. Bundle

| Field | Value |
|---|---|
| Generator | `scripts/build_rcc002_spec_bundle.py` — not modified (existing `--output` argument sufficient) |
| Output path | `docs/review/RCC_002_DVSEV001_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md` (new filename; previous bundle not overwritten) |
| Lines | 14,070 |
| Bytes | 501,799 |
| SHA-256 | `8a6ab7d732e02727199e704313c38959161c3929441fddce34b4ee4f2586d9ee` |

## 9. Manifest

| Field | Value |
|---|---|
| Manifest path | `docs/review/RCC_002_DVSEV001_CORRECTED_BUNDLE_MANIFEST_2026-07-27.md` (new filename; previous manifest not overwritten) |
| SHA-256 | computed independently in Section 10 below (self-referential value omitted here to avoid a circular hash statement inside the manifest itself; see the manifest file's own Section 2 for its declared bundle identity) |

## 10. Hashes

| Artifact | SHA-256 |
|---|---|
| Data Pipeline (unchanged) | `529f83a27c0464af0954213ffc0e81b26819bf846a1b7a6085a6b323bddf87a2` |
| Data Validation | `bceb8e0dba5e8a71dad012499165d139dbf8a450afea2d9525a0a4d5e4cc28f1` |
| Indicator | `e0f8641cc95575338adad3e2e636740d22de1349926f80d87f03f20fb8564af5` |
| Signal Transformation | `0538a660631aad1fa73a5db72bc45eba8d0c73ce2199f96b47c264be8136b4a5` |
| Regime and Gate | `26d675e26cc5a014c962ed51910f170e3369a1e39e34ca1cfec9027ce5f5eeff` |
| Label and Forward Return | `8f6c02e13378521b4ae09b08d2ad3c610a27383a2d6a589e003e4febcacceb33` |
| Reproducibility and Manifest | `3f795db4ffb9427efa73519c8390cf21bda67e82e0313b037d59b57027dca846` |
| New Bundle | `8a6ab7d732e02727199e704313c38959161c3929441fddce34b4ee4f2586d9ee` |
| Previous Bundle (unchanged, AIR4-MIN-01) | `39314fd6b6c186c3bc27932c701a36d1456f8f0a6009518617e6af592cea139a` |
| Previous Manifest (unchanged, AIR4-MIN-01) | `5d7792cb12306708aedc5dfd051d6a7eba20c6640fbe4e04566af18724969682` |
| Certified baseline still referenced by `rcc002/__init__.py` (unchanged in this cycle) | Bundle `39314fd6…39a`; Manifest `5d7792cb…682` — both independently re-verified byte-identical to the constants in `rcc002/__init__.py` |

## 11. Round-trip

The generator was executed a second time, independently, with identical
arguments against a temporary output path. Result: 14,070 lines / 501,799
bytes, SHA-256 `8a6ab7d732e02727199e704313c38959161c3929441fddce34b4ee4f2586d9ee`
— exact match to Section 8. `diff` reported no differences. The temporary
file was deleted after verification.

**Round-trip result: byte-exact.**

## 12. Abweichungen

None from the approved proposal's scope or version matrix. One editorial
improvement over the draft in the proposal document: the closing paragraph
of §16.3 was rephrased from the proposal's "unterliegen der Freigabe durch
die zuständige Prüfinstanz" (future-tense, pending approval) to a
past-tense attribution ("wurden im Rahmen des Korrekturzyklus
`RCC-002-DVSEV-001` … hergeleitet, geprüft und freigegeben"), since the
proposal was approved before insertion — a wording adjustment for
correctness given the approval already occurred, not a semantic change to
any severity assignment.

## 13. Closure Readiness

`DVSEV-001` is ready for closure verification against this record: all 32
reason codes now have a deterministic Standard-Severity; the 6 pre-existing
explicit assignments are unchanged; the 26 newly-derived assignments are
each grounded in an existing, cited normative statement; the version and
dependency matrices are fully consistent; Reproducibility §12.3 is current;
the bundle and manifest are regenerated and independently round-trip
verified; no implementation file was touched. A fokussierte Re-Review
(scoped per the approved proposal §6.4 item 6) remains the next required
step before Editorial Pass and before implementation resumes at Step 4.

## 14. Final Decision

```text
Status: PASS

Finding DVSEV-001: CLOSED (specification correction).

6 specifications touched (Data Validation, Indicator, Signal
Transformation, Regime and Gate, Label and Forward Return, Reproducibility
and Manifest); 1 unchanged (Data Pipeline, byte-identical, independently
confirmed).

Reason-Code-Severity-Register: all 32 registered reason codes now carry a
deterministic Standard-Severity in Data Validation §16.3.
6 pre-existing explicit severities: unchanged.
26 newly-derived severities: each grounded in an existing cited rule.
No new reason code, no removed reason code, no altered existing severity.
Version and dependency matrices: fully consistent.
Reproducibility §12.3: current.
Bundle and manifest regenerated under new filenames; previous
(AIR4-MIN-01) bundle and manifest confirmed byte-identical and untouched,
and independently re-verified against rcc002/__init__.py's certified
constants (unchanged in this cycle, by explicit instruction).
Round-trip byte-exact.
No implementation file touched.
No commit created.
```

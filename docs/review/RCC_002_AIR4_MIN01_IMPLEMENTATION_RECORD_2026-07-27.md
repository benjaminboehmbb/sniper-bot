# RCC-002 AIR4-MIN-01 — Targeted Correction Implementation Record

## 1. Finding

`AIR4-MIN-01`, from `docs/review/RCC_002_AIR_004_FULL_SCOPE_REPLACEMENT_ARCHITECTURE_INTEGRITY_REVIEW_2026-07-27.md` (SHA-256 `1dd0c03880fb7978b93b758b9ec3b1ec9c887a625c19ddc9ece1e8209d9ed1bc`, independently re-verified against the working tree before implementation began; matched exactly), Section 34: the `PASS_WITH_APPROVED_EXCEPTIONS` carve-out lists in Indicator §30 and Signal Transformation §32 did not state whether their enumerated non-overridable categories were exhaustive or illustrative, allowing two conformant implementations of the exception-approval mechanism to diverge on whether a failed Property-Test requirement could be waved through as a non-blocking exception.

## 2. Ausgangsproblem

Quoted (pre-correction) carve-out text, identical in structure in both documents:

> Indicator §30: *"`PASS_WITH_APPROVED_EXCEPTIONS` darf ausschließlich nicht blockierende, vollständig dokumentierte Berichtsbefunde betreffen. Es darf weder ein ungültiges S2-Feld noch einen regelwidrig gebildeten `x_valid`-Status, einen Schemafehler, einen Segmentfehler, einen nicht endlichen gültigen Wert oder eine fehlgeschlagene Reconciliation überstimmen."*
>
> Signal Transformation §32: *"`PASS_WITH_APPROVED_EXCEPTIONS` darf ausschließlich nicht blockierende, vollständig dokumentierte Berichtsbefunde betreffen. Es darf weder Schemafehler noch falsche Feldwerte, unzulässige Nullwerte, Segmentfehler, nicht endliche gültige Werte, Rollenverletzungen oder eine fehlgeschlagene Reconciliation überstimmen."*

Neither list named "a failed Property-Test requirement" (Indicator criterion 16; Signal Transformation criterion 18) among its enumerated non-overridable categories, even though passing Property-Tests is itself a MUST-level Publication Gate criterion in both documents.

## 3. Normative Entscheidung

Per the correction order: **the carve-out lists are exhaustive**. No unlisted condition may be approved under `PASS_WITH_APPROVED_EXCEPTIONS` without a normative specification change, a version increment, a review, and a renewed certification assessment. Human approval alone does not extend the normative exception scope.

## 4. Geänderte Dateien

| File | Reason |
|---|---|
| `docs/specifications/RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md` | Primary correction: exhaustive-carve-out clause added to §30; own version bump; changelog row |
| `docs/specifications/RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md` | Primary correction: exhaustive-carve-out clause added to §32; own version bump; changelog row; Indicator dependency citation corrected |
| `docs/specifications/RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md` | Mechanical dependency-citation follow-on only (Indicator, Signal Transformation); own version **unchanged**, per explicit instruction |
| `docs/specifications/RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md` | Mechanical dependency-citation follow-on only (Indicator, Signal Transformation); own version **unchanged**, per explicit instruction |
| `docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md` | Mechanical follow-on: header dependency citations, §12.3 table, one new dated §29 paragraph documenting the mechanical patch; own version bumped (Patch, per explicit instruction) |

**Not changed**: `docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md` and `docs/specifications/RCC_002_DATA_VALIDATION_2026-07-23.md` — confirmed byte-identical before and after (Section 8).

## 5. Versionsänderungen

| Document | Before | After | Change type |
|---|---|---|---|
| Data Pipeline | `0.7.1` | `0.7.1` | Unchanged |
| Data Validation | `0.4.2` | `0.4.2` | Unchanged |
| Indicator | `0.4.2` | `0.4.3` | Patch — normative carve-out clarification |
| Signal Transformation | `0.4.1` | `0.4.2` | Patch — normative carve-out clarification |
| Regime and Gate | `0.5.1` | `0.5.1` | **Unchanged** — mechanical citation-only follow-on, per explicit instruction |
| Label and Forward Return | `0.4.1` | `0.4.1` | **Unchanged** — mechanical citation-only follow-on, per explicit instruction |
| Reproducibility and Manifest | `0.7.0` | `0.7.1` | Patch — mechanical citation/profile correction only, no normative content change |

## 6. Exakte Textänderungen

### Indicator §30 (new paragraph, appended after the existing carve-out sentence)

> "Die in diesem Abschnitt aufgeführten Ausnahmefälle für `PASS_WITH_APPROVED_EXCEPTIONS` sind abschließend. Kein hier nicht aufgeführter Fall darf unter diesem Gate-Status genehmigt werden, ohne zuvor eine normative Spezifikationsänderung, eine Versionsanhebung, einen Review und eine erneute Zertifizierungsbewertung zu durchlaufen. Eine menschliche Genehmigung allein erweitert nicht den normativen Ausnahmeumfang."

No existing sentence in §30 was altered or removed.

### Signal Transformation §32 (identical clause, appended after the existing carve-out sentence)

> "Die in diesem Abschnitt aufgeführten Ausnahmefälle für `PASS_WITH_APPROVED_EXCEPTIONS` sind abschließend. Kein hier nicht aufgeführter Fall darf unter diesem Gate-Status genehmigt werden, ohne zuvor eine normative Spezifikationsänderung, eine Versionsanhebung, einen Review und eine erneute Zertifizierungsbewertung zu durchlaufen. Eine menschliche Genehmigung allein erweitert nicht den normativen Ausnahmeumfang."

No existing sentence in §32 was altered or removed. The two clauses are verbatim-identical in normative content (only the surrounding document context differs), satisfying the requirement that the semantics be fully preserved while allowing terminological document-local fit — in this case no terminological adaptation was even necessary, since both documents already share the same `PASS_WITH_APPROVED_EXCEPTIONS` vocabulary.

### Both documents — Document-Control header

`Version` field incremented (`0.4.2`→`0.4.3` Indicator; `0.4.1`→`0.4.2` Signal Transformation). One new Review-Nachweis row added to each, following the established table format:

> "| AIR4-MIN-01 Correction | `RCC-002-AIR-004` Minor Finding behoben | Version 0.4.x, 2026-07-27: Clarified that PASS_WITH_APPROVED_EXCEPTIONS carve-outs are exhaustive and cannot be extended by approval alone. |"

## 7. Mechanische Folgeänderungen

Documented here explicitly before implementation, per the correction order's requirement:

| Document | Field changed | Old value | New value | Reason |
|---|---|---|---|---|
| Signal Transformation | Header "Direkte Abhängigkeiten" (Indicator) | `0.4.2` | `0.4.3` | Indicator's own version changed |
| Regime and Gate | Header "Direkte Abhängigkeiten" (Indicator) | `0.4.2` | `0.4.3` | Indicator's own version changed |
| Regime and Gate | Header "Direkte Abhängigkeiten" (Signal Transformation) | `0.4.1` | `0.4.2` | Signal Transformation's own version changed |
| Label and Forward Return | Header "Direkte Abhängigkeiten" (Indicator) | `0.4.2` | `0.4.3` | Indicator's own version changed |
| Label and Forward Return | Header "Direkte Abhängigkeiten" (Signal Transformation) | `0.4.1` | `0.4.2` | Signal Transformation's own version changed |
| Reproducibility | Header "Fachliche Abhängigkeiten" (Indicator) | `0.4.2` | `0.4.3` | Indicator's own version changed |
| Reproducibility | Header "Fachliche Abhängigkeiten" (Signal Transformation) | `0.4.1` | `0.4.2` | Signal Transformation's own version changed |
| Reproducibility | §12.3 table, `RCC-002-IS` row | `0.4.2` | `0.4.3` | Same |
| Reproducibility | §12.3 table, `RCC-002-ST` row | `0.4.1` | `0.4.2` | Same |
| Reproducibility | §12.3 table, `RCC-002-RM` row (self) | `0.7.0` | `0.7.1` | Reproducibility's own version changed (Section 5) |
| Reproducibility | New §29 paragraph | — | Appended, mechanical | Documents the mechanical patch, following this document's established per-version changelog-paragraph convention; the prior "Version 0.7.0 bewahrt..." paragraph was left unmodified (historical accuracy preserved, same reasoning as the prior Minor Correction Cycle) |
| Reproducibility | Header "Status" field | Prior text | Appended "SCR-008 und AIR-004 durchgeführt; AIR4-MIN-01... behoben" | Factual update, not a new normative rule |
| Reproducibility | §29 "Der aktuelle Status lautet" / "Nächste vorgeschriebene Schritte" | Prior text | Updated to reflect SCR-008/AIR-004 completion and AIR4-MIN-01 closure | Factual update, mirrors header Status field per this document's own established consistency requirement |

Regime and Gate and Label and Forward Return received **only** the citation-value corrections in the table above — no changelog row, no version change, per the correction order's explicit versionsmatrix (both listed as unchanged).

## 8. Validierung

| Check | Result |
|---|---|
| Indicator §30 contains the exhaustive carve-out rule | PASS |
| Signal Transformation §32 contains the same semantics | PASS |
| Both rules are mutually non-contradictory | PASS — verbatim-identical clause |
| No new exception type was added | PASS — confirmed via direct grep for `PASS_WITH_APPROVED_EXCEPTIONS`/`PASS`/`FAIL` occurrences in both documents; enum remains exactly `PASS`/`FAIL`/`PASS_WITH_APPROVED_EXCEPTIONS` |
| No automatic exception approval was introduced | PASS — the added clause only restricts, it does not describe any automated grant path; "vollständig dokumentierte... genehmigt" (human documentation/approval) remains the only path, now explicitly bounded in scope |
| Human approval remains required but non-scope-extending | PASS — new clause's last sentence states this directly |
| Version matrix is consistent | PASS — Section 5, independently re-verified against all seven document headers after editing |
| All live dependency references are current | PASS — full-family grep found zero stale citations of Indicator `0.4.2` or Signal Transformation `0.4.1` outside this cycle's own historical narrative blocks (which correctly retain pre-cycle values, per the same historical/current separation established in the prior Minor Correction Cycle) |
| Reproducibility §12.3 is current | PASS — all seven rows match the post-cycle header versions exactly, including the self-reference |
| No rejected or Observation-level finding was implemented | PASS — no other AIR-004/SCR-008 finding was touched; F-1 through F-4, O-1 through O-9 all remain untouched, as instructed |
| No other normative change was made | PASS — confirmed via targeted diff review of every edited location; no Publication Gate criterion, invariant, truth table, or test requirement was altered anywhere |

## 9. Bundle

| Field | Value |
|---|---|
| Generator | `scripts/build_rcc002_spec_bundle.py` — not modified (existing `--output` argument sufficient) |
| Output path | `docs/review/RCC_002_AIR4_MIN01_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md` (new filename; previous bundle not overwritten) |
| Lines | 13,980 |
| Bytes | 495,922 |
| SHA-256 | `39314fd6b6c186c3bc27932c701a36d1456f8f0a6009518617e6af592cea139a` |

## 10. Manifest

| Field | Value |
|---|---|
| Manifest path | `docs/review/RCC_002_AIR4_MIN01_CORRECTED_BUNDLE_MANIFEST_2026-07-27.md` (new filename; previous manifest not overwritten) |
| Lines | 86 |
| Bytes | 6,327 |
| SHA-256 | `5d7792cb12306708aedc5dfd051d6a7eba20c6640fbe4e04566af18724969682` |

## 11. Hashes

| Artifact | SHA-256 |
|---|---|
| Data Pipeline (unchanged) | `529f83a27c0464af0954213ffc0e81b26819bf846a1b7a6085a6b323bddf87a2` |
| Data Validation (unchanged) | `9bb70245d2001ee2676f63a9e89b396c9b71dc575e72da6084dd617ce41b258d` |
| Indicator | `80e77f3a29e753b028d479a0a383010ce7c16804a74420f465e99eb4dcdfe70b` |
| Signal Transformation | `5981aa15c317d5675e9adc71aecd7a26dc7abbfe0f5ac45947faa993c7022a0b` |
| Regime and Gate | `ad981e2dcdc935aef1a3f6f107e0bfce4070b6926d2eb65da4fe209a31c2c346` |
| Label and Forward Return | `99b68f1933859f4da1a92676e9fb6c3a8b78f25eeb2ad4b4fd42db66769751b9` |
| Reproducibility and Manifest | `20a50faf2851db7fcf85bc0c776b592f39a08259b32e7b80b80866b5d4e60619` |
| New Bundle | `39314fd6b6c186c3bc27932c701a36d1456f8f0a6009518617e6af592cea139a` |
| New Manifest | `5d7792cb12306708aedc5dfd051d6a7eba20c6640fbe4e04566af18724969682` |
| Previous Bundle (unchanged) | `8bd00fd09055e0055b09642edbdddf105c25ea1f36b720c1892f07d360aca75f` |
| Previous Manifest (unchanged) | `7edd5c28d20db328be64394b615c3cadec81ecbaaac8ccca05577586c251c030` |
| Source AIR-004 Report (unchanged) | `1dd0c03880fb7978b93b758b9ec3b1ec9c887a625c19ddc9ece1e8209d9ed1bc` |

## 12. Round-trip

The generator was executed a second time, independently, with identical arguments against a temporary output path. Result: 13,980 lines / 495,922 bytes, SHA-256 `39314fd6b6c186c3bc27932c701a36d1456f8f0a6009518617e6af592cea139a` — exact match to Section 9. `diff` reported no differences. The temporary file was deleted after verification.

**Round-trip result: byte-exact.**

## 13. Abweichungen

None from the approved scope or the explicit version instructions. One execution-method note, consistent with the established convention already used in the prior Minor Correction Cycle: Reproducibility §29's historical "Version 0.7.0 bewahrt..." paragraph was left unmodified, and a new, separately dated "Version 0.7.1..." paragraph was appended, to avoid retroactively rewriting a version-labeled historical statement — this is the same, already-accepted pattern used for the 0.6.0→0.7.0 transition, applied identically here, not a new deviation type.

## 14. Closure Readiness

`AIR4-MIN-01` is ready for closure verification against this record: the exhaustive-carve-out rule is present, identical in semantics, and non-contradictory in both Indicator §30 and Signal Transformation §32; no new exception type or automatic-approval path was introduced; the version and dependency matrices are fully consistent; Reproducibility §12.3 is current; the bundle and manifest are regenerated and independently round-trip-verified. A fokussierte Re-Review (per AIR-004's own Section 42, Required Next Actions) remains the next required step before Editorial Pass.

## 15. Final Decision

```text
Status: PASS

Finding AIR4-MIN-01: CLOSED.

5 specifications touched (Indicator, Signal Transformation, Regime and Gate,
Label and Forward Return, Reproducibility and Manifest); 2 unchanged
(Data Pipeline, Data Validation, byte-identical, independently confirmed).

Carve-out lists: explicitly exhaustive in both affected documents.
No new exception type introduced.
No automatic exception approval introduced.
Human approval remains required and does not extend normative scope.
Version and dependency matrices: fully consistent.
Reproducibility §12.3: current.
Bundle and manifest regenerated under new filenames; previous bundle,
manifest, SCR-008, and AIR-004 report all confirmed byte-identical and
untouched.
Round-trip byte-exact.
No commit created.
```

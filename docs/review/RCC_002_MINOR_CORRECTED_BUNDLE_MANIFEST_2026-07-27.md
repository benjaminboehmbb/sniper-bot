# RCC-002 Minor Corrected Bundle Manifest

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Governance- und Identitätsnachweis |
| Dokument-ID | `RCC-002-MINOR-CORRECTED-BUNDLE-MANIFEST` |
| Titel | Bundle Manifest — RCC-002 Minor Corrected Full Specification Bundle |
| Version | 1.0.0 |
| Datum | 2026-07-27 |
| Status | Kandidat — Minor Correction Cycle umgesetzt; SCR-008 (fokussierte Re-Review), Full-Scope Replacement Architecture Integrity Review, Editorial Pass und Internal Certification ausstehend |
| Speicherort im Repository | `docs/review/RCC_002_MINOR_CORRECTED_BUNDLE_MANIFEST_2026-07-27.md` |
| Dateiname | `RCC_002_MINOR_CORRECTED_BUNDLE_MANIFEST_2026-07-27.md` |
| Abhängigkeiten | `docs/review/RCC_002_MINOR_CORRECTION_IMPLEMENTATION_PLAN_2026-07-27.md`; `docs/review/RCC_002_SCR_007_MINOR_FINDINGS_VERIFICATION_AND_CORRECTION_PLAN_2026-07-27.md`; `docs/review/RCC_002_SCR_007_MAJOR_FINDINGS_VERIFICATION_2026-07-27.md`; `docs/review/RCC_002_SCR_007_FULL_SCOPE_REPLACEMENT_REVIEW_2026-07-27.md`; `docs/review/RCC_002_MINOR_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md`; `scripts/build_rcc002_spec_bundle.py` |
| Referenziert durch | fokussierte Re-Review (SCR-008, ausstehend); Full-Scope Replacement Architecture Integrity Review (ausstehend) |
| Autoritative Sprache | Deutsch für normative Erläuterung; englische Feld- und Konstantennamen wie im Quellmaterial |
| Änderung gegenüber der vorigen Bundle-Fassung | Minor Correction Cycle umgesetzt gemäß `RCC_002_MINOR_CORRECTION_IMPLEMENTATION_PLAN_2026-07-27.md`: 18 einzelne Änderungen an sechs von sieben Spezifikationen (Data Pipeline unverändert); Versionsanhebungen Data Validation 0.4.1→0.4.2, Indicator 0.4.1→0.4.2, Signal Transformation 0.4.0→0.4.1, Regime and Gate 0.5.0→0.5.1, Label and Forward Return 0.4.0→0.4.1, Reproducibility and Manifest 0.6.0→0.7.0; sämtliche bestätigten Abhängigkeitsversions-Zitatstellen korrigiert; Label §17.4 Terminologiekorrektur; Signal Transformation §32 neues Kriterium 18 „Property-Tests bestanden sind"; Reproducibility §12.3-Tabelle korrigiert, §25 neuer Prüfpunkt, Status-/§29-Aktualisierung. Keine Architekturänderung, keine neue Testmethodik, keine neue Versionierungsarchitektur. |

## 1. Vollständige Dateiliste in Bundle-Reihenfolge

| # | Datei | Version | Zeilen | Bytes | SHA-256 | Geändert im Minor Correction Cycle? |
|---:|---|---|---:|---:|---|:---:|
| 1 | `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md` | 0.7.1 | 2592 | 134284 | `529f83a27c0464af0954213ffc0e81b26819bf846a1b7a6085a6b323bddf87a2` | Nein — unverändert, byte-identisch |
| 2 | `RCC_002_DATA_VALIDATION_2026-07-23.md` | 0.4.2 | 1382 | 46926 | `9bb70245d2001ee2676f63a9e89b396c9b71dc575e72da6084dd617ce41b258d` | Ja — Version, Abhängigkeitszitat, Änderungsverlaufseintrag |
| 3 | `RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md` | 0.4.2 | 1742 | 50958 | `58bbdbe9d0d0beda43f1fbec443814aa23a6deec5f2152371aa4ef1ac6bbdf9c` | Ja — Version, zwei Abhängigkeitszitate, Änderungsverlaufseintrag |
| 4 | `RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md` | 0.4.1 | 1665 | 53228 | `0a9c5f2d345add8cc2627e2771bfaea9f951ba8bb7484f1fa1d9c51b054ae81c` | Ja — Version, drei Abhängigkeitszitate, §32 neues Kriterium 18, Änderungsverlaufseintrag |
| 5 | `RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md` | 0.5.1 | 2216 | 68324 | `369ecc70b6f9a9cfad8fab8cc5e4f81412afc1706f1c9c0e6d99eda435f02f35` | Ja — Version, vier Abhängigkeitszitate, Änderungsverlaufseintrag |
| 6 | `RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md` | 0.4.1 | 2017 | 60288 | `81f48b30984944dc4218857167e508bb7ff0dc5fa541b607b110333e784bc7d0` | Ja — Version, fünf Abhängigkeitszitate (Kopfzeile) plus ein weiteres Abhängigkeitszitat in §26.1, §17.4 Terminologiekorrektur, Änderungsverlaufseintrag |
| 7 | `RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md` | 0.7.0 | 2245 | 76769 | `e2c866eb43bf082f25ec92ad3cc7767a9257efc5623f4fb8891d87eb5e904438` | Ja — Version, sechs Abhängigkeitszitate (Kopfzeile) plus ein weiteres Abhängigkeitszitat in §7.9-Bezug, §12.3-Tabelle, §25 neuer Prüfpunkt, Status-Feld, neuer §29-Absatz |

Alle historischen Passagen des Musters „Version X bewahrt ... und aktualisiert
die Abhängigkeiten auf: ..." wurden bewusst **nicht** verändert, da sie den
Zustand einer vergangenen Version dokumentieren, nicht den aktuellen Zustand;
eine Änderung dieser Passagen hätte historische Aussagen rückwirkend
verfälscht. Ausschließlich Kopfzeilen-Metadaten, das aktuell gültige
Spezifikationsprofil (§12.3 in Reproducibility), aktuell gültige
Einzelverweise auf Data Pipeline außerhalb historischer Blöcke sowie die in
`RCC_002_MINOR_CORRECTION_IMPLEMENTATION_PLAN_2026-07-27.md` bestätigten
inhaltlichen Einzeländerungen (Label §17.4; Signal Transformation §32
Kriterium 18; Reproducibility §25 Prüfpunkt) wurden geändert.

## 2. Bundle-Identität

| Feld | Wert |
|---|---|
| Datei | `docs/review/RCC_002_MINOR_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md` |
| Zeilen | 13926 |
| Bytes | 493231 |
| SHA-256 | `8bd00fd09055e0055b09642edbdddf105c25ea1f36b720c1892f07d360aca75f` |

## 3. Referenzidentität des vorigen Bundles (unverändert)

| Feld | Wert |
|---|---|
| Datei | `docs/review/RCC_002_C1_CORRECTED_FULL_SPEC_BUNDLE_2026-07-25.md` |
| Zeilen | 13876 |
| Bytes | 489881 |
| SHA-256 | `18faca1d09411eb7c5b440833c8cc7fcac2a6f1870669f961653412163435198` |

Das vorige Bundle wurde nicht überschrieben, nicht gelöscht und nicht
verändert (siehe Abschnitt 7).

## 4. Git-Zustand vor der Änderung

| Feld | Wert |
|---|---|
| Git-Commit vor der Änderung (HEAD) | `e2e1d022e37bc871d5024d79cf9484c3a1ee9df1` |
| Zustand der Arbeitskopie | `docs/specifications/` und `docs/review/` vollständig untracked (nie committet); alle in diesem Zyklus geänderten oder erzeugten Dateien bleiben untracked |
| Commit im Rahmen dieser Aufgabe | Keiner — kein Commit erstellt |

## 5. Generierungsbefehl

```bash
python3 scripts/build_rcc002_spec_bundle.py \
  --title "RCC-002 Minor Corrected Full Specification Bundle" \
  --korrekturstand "Minor Correction Cycle 2026-07-27 (RCC-002-SCR-007-MinFV): version 0.4.2/0.4.2/0.4.1/0.5.1/0.4.1/0.7.0 bumps for Data Validation, Indicator, Signal Transformation, Regime and Gate, Label and Forward Return, Reproducibility and Manifest; dependency-citation corrections; Label §17.4 terminology correction; Signal Transformation §32 Property-Tests criterion; Reproducibility §12.3/§25/Status/§29 corrections. Data Pipeline unchanged at 0.7.1." \
  --output docs/review/RCC_002_MINOR_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md
```

Generator: `scripts/build_rcc002_spec_bundle.py` — **unverändert** gegenüber
der Fassung, die das vorige Bundle erzeugt hat (identisch mit der Version, die
`docs/review/RCC_002_C1_CORRECTED_FULL_SPEC_BUNDLE_2026-07-25.md` erzeugte).
Der Generator unterstützte bereits vor diesem Zyklus ein explizites
`--output`-Argument; keine Codeänderung war erforderlich. Normalisierungs- und
Hashlogik unverändert.

## 6. Übertragung bestehender Freigaben — ausdrücklicher Hinweis

```text
RCC-002-SCR-007 (FAIL, später durch Major- und Minor-Findings-Verifikation
auf PASS WITH MINOR CORRECTIONS neu bewertet) bezieht sich ausschließlich auf
RCC_002_C1_CORRECTED_FULL_SPEC_BUNDLE_2026-07-25.md.

Keine dieser Freigaben überträgt sich automatisch auf
RCC_002_MINOR_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md.

Reviewstatus für das minor-korrigierte Paket (Stand 2026-07-27):

    RCC-002-SCR-007: bezieht sich auf das vorige Bundle; seine
        Neubewertung (PASS WITH MINOR CORRECTIONS) beruht auf den in diesem
        Bundle nun umgesetzten Korrekturen.

    Fokussierte Re-Review (SCR-008) der sechs geänderten Dokumente:
        AUSSTEHEND.

    Full-Scope Replacement Architecture Integrity Review: AUSSTEHEND.

    Editorial Pass: AUSSTEHEND.

    Internal Certification: AUSSTEHEND.
```

## 7. Unveränderte Artefakte

Das vorige Bundle `RCC_002_C1_CORRECTED_FULL_SPEC_BUNDLE_2026-07-25.md` und
sein Manifest `RCC_002_C1_CORRECTED_BUNDLE_MANIFEST_2026-07-25.md` wurden
nicht überschrieben, nicht gelöscht und nicht verändert (unabhängig erneut
per Hash-Vergleich bestätigt, siehe Abschnitt 3). Alle übrigen
`docs/review/`-Dateien wurden nicht verändert.

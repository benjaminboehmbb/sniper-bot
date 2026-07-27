# RCC-002 C1 Corrected Bundle Manifest

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Governance- und Identitätsnachweis |
| Dokument-ID | `RCC-002-C1-CORRECTED-BUNDLE-MANIFEST` |
| Titel | Bundle Manifest — RCC-002 C1 Corrected Full Specification Bundle |
| Version | 1.2.0 |
| Datum | 2026-07-25 |
| Status | Kandidat — Editorial Pass gesperrt bis Klärung von C2 (Scientific Consistency Review und Architecture Integrity Review beide bestanden mit Minor/Major Findings, AIR-Major-Finding umgesetzt) |
| Speicherort im Repository | `docs/review/RCC_002_C1_CORRECTED_BUNDLE_MANIFEST_2026-07-25.md` |
| Dateiname | `RCC_002_C1_CORRECTED_BUNDLE_MANIFEST_2026-07-25.md` |
| Abhängigkeiten | `RCC_002_C1_VERIFICATION_RECORD_2026-07-25.md`; `RCC_002_C1_IMPACT_ANALYSIS_2026-07-25.md`; `RCC_002_C1_SCIENTIFIC_CONSISTENCY_REVIEW_2026-07-25.md`; `RCC_002_C2_REVIEW_LINEAGE_INVESTIGATION_2026-07-25.md`; `RCC_002_AIR_003_C1_ARCHITECTURE_REVIEW_2026-07-25.md`; `RCC_002_C1_CORRECTED_FULL_SPEC_BUNDLE_2026-07-25.md`; `scripts/build_rcc002_spec_bundle.py` |
| Referenziert durch | Editorial Pass (gesperrt, siehe §6) |
| Autoritative Sprache | Deutsch für normative Erläuterung; englische Feld- und Konstantennamen wie im Quellmaterial |
| Änderung gegenüber 1.1.0 | `RCC-002-AIR-003` durchgeführt (PASS WITH MINOR CORRECTIONS); dessen Major Finding AIR3-M1 (fehlende S7→S8-Row-Preservation-Invariante) sowie Minor Finding AIR3-m1 (fehlende §5.8-Rückverweise) umgesetzt: neue Unterabschnitt 8.7.1 und Reconciliation-Test in `RCC_002_REPRODUCIBILITY_AND_MANIFEST`; Rückverweise auf Data Pipeline §5.8 in allen sechs übrigen Dokumenten ergänzt; keine Versionserhöhung vorgenommen (explizite Weisung für diesen Korrekturzyklus; fachliche Neubewertung der Versionierungsfrage nicht Gegenstand dieses Zyklus); Bundle neu erzeugt, alle Hashes aktualisiert |

## 1. Vollständige Dateiliste in Bundle-Reihenfolge

| # | Datei | Version | Zeilen | Bytes | SHA-256 | Geändert für C1/AIR-003? |
|---:|---|---|---:|---:|---|:---:|
| 1 | `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md` | 0.7.1 | 2592 | 134284 | `529f83a27c0464af0954213ffc0e81b26819bf846a1b7a6085a6b323bddf87a2` | Ja (§5.8 neu; Patch 0.7.0→0.7.1); in diesem Zyklus unverändert |
| 2 | `RCC_002_DATA_VALIDATION_2026-07-23.md` | 0.4.1 | 1381 | 46721 | `5366fba100373e62e114faabca680800faf8d9528e40bf4666b4c675387526c2` | Ja (§20 Kriterium 16; Patch 0.4.0→0.4.1); jetzt zusätzlich §5.8-Rückverweis |
| 3 | `RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md` | 0.4.1 | 1741 | 50753 | `31dce315299ec485c20ca8c84714d3a97fa696f893447af542dd835a02dd433f` | Ja (§4.3; §30 Kriterium 2; Patch 0.4.0→0.4.1); jetzt zusätzlich §5.8-Rückverweis |
| 4 | `RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md` | 0.4.0 | 1663 | 52988 | `82e099fe89982f4544e7a89f184653066d1871815006eea7bc64b4efbbafa1c7` | Jetzt: §5.8-Rückverweis (§28.2) |
| 5 | `RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md` | 0.5.0 | 2215 | 68119 | `134f6c1db3160dc3d84cc0fc005d183c4856e8af6b0cccbc2ed61e9ad8e1aaf9` | Jetzt: §5.8-Rückverweis (§30) |
| 6 | `RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md` | 0.4.0 | 2015 | 59993 | `91f87f1841cd47a01d3b848f626159d1f5adf0be88f9fdb571e25a2ad229152c` | Jetzt: §5.8-Rückverweis (§22) |
| 7 | `RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md` | 0.6.0 | 2202 | 74822 | `9cf6de39c32be4d4bc2ea56e2eb0a5dddf1f29dee8adc965df1f930eef81dac6` | Jetzt: neue §8.7.1 (S8-Row-Preservation-Invariante), S8-Reconciliation-Test in §18.4, §5.8-Rückverweis |

Zeilen 1–3 enthalten zusätzlich zur C1-Fachkorrektur je einen
Review-Nachweis-Eintrag „C1 Patch Release“ mit dem Wortlaut „patch release:
normative clarification of Canonical Row Preservation semantics (C1). No
intended behavioural change.“, gemäß Empfehlung aus
`RCC_002_C1_SCIENTIFIC_CONSISTENCY_REVIEW_2026-07-25.md`, Major Finding M1.

Zeilen 2, 3, 4, 5, 6 enthalten je einen kurzen Rückverweis auf
`RCC_002_DATA_PIPELINE_SPECIFICATION` §5.8, unmittelbar an der Stelle, an
der die jeweilige Zeilenzahl-Invariante bereits normiert war. Zeile 7
(Reproducibility) enthält zusätzlich die neue normative
Row-Preservation-Invariante für S8 (§8.7.1) und das zugehörige
Reconciliation-Testerfordernis (§18.4), gemäß Major Finding AIR3-M1 aus
`RCC_002_AIR_003_C1_ARCHITECTURE_REVIEW_2026-07-25.md`. Keine der sieben
Versionsnummern wurde in diesem Zyklus verändert (explizite Weisung).

Dateien 4–7 sind byte-, zeilen- und hashgleich mit den in
`RCC_002_SCR_005_CORRECTED_FULL_SPEC_BUNDLE_2026-07-24.md` eingebetteten
Fassungen (verifiziert vor jeder Änderung).

## 2. Bundle-Identität

| Feld | Wert |
|---|---|
| Datei | `docs/review/RCC_002_C1_CORRECTED_FULL_SPEC_BUNDLE_2026-07-25.md` |
| Zeilen | 13876 |
| Bytes | 489881 |
| SHA-256 | `18faca1d09411eb7c5b440833c8cc7fcac2a6f1870669f961653412163435198` |
| Zeilendelta zur vorigen Fassung | +54 (Data Validation +3, Indicator +2, Signal Transformation +2, Regime and Gate +3, Label +2, Reproducibility +42; ausschließlich §5.8-Rückverweise sowie die neue §8.7.1/§18.4-Ergänzung in Reproducibility) |
| Vorgängerfassung dieses Bundles | Post-Versionierung/Härtung vom 2026-07-25, 13822 Zeilen, 487878 Bytes, SHA-256 `481ecdf75f502c9bb0930cfe625336aaeb7fdffa32c1c402c78a01e39e7c6017` — durch diese Version ersetzt (nicht separat aufbewahrt) |

## 3. Referenzidentität des alten Bundles (unverändert)

| Feld | Wert |
|---|---|
| Datei | `docs/review/RCC_002_SCR_005_CORRECTED_FULL_SPEC_BUNDLE_2026-07-24.md` |
| Zeilen | 13776 |
| Bytes | 485064 |
| SHA-256 | `5aae1bd7107ace3baf1de8178349169249b387756fe406598a8a7fad1ed190b2` |

Zur Einordnung: `RCC-002-SCR-006` und `RCC-002-AIR-002` referenzieren in
ihren eigenen Dokumentmetadaten den Paket-SHA-256
`33aac77fe96147c8d81e8683db470f50780159b7168e1139214592f7fd6e26c5` — dieser
stimmt nicht mit dem tatsächlichen, hier unabhängig nachgemessenen Hash des
alten Bundles überein. Diese Diskrepanz wurde im vorausgehenden
unabhängigen Review vom 2026-07-25 als eigener Befund dokumentiert und ist
von der vorliegenden C1-Korrektur nicht betroffen; sie wird hier nur zur
vollständigen Provenienz mitgeführt.

## 4. Git-Zustand vor der Änderung

| Feld | Wert |
|---|---|
| Git-Commit vor der Änderung (HEAD) | `e2e1d022e37bc871d5024d79cf9484c3a1ee9df1` |
| Zustand der Arbeitskopie | `docs/specifications/` vollständig untracked (nie committet); `docs/review/RCC_002_SCR_005_CORRECTED_FULL_SPEC_BUNDLE_2026-07-24.md`, `RCC_002_SCR_006_FINDINGS_2026-07-24.md`, `RCC_002_AIR_002_FINDINGS_2026-07-24.md` bereits in `e2e1d02` committet; diverse ältere `docs/review/`-Dateien weiterhin untracked seit Sessionbeginn |
| Commit im Rahmen dieser Aufgabe | Keiner — noch kein Commit erstellt |

## 5. Generierungsbefehl

```bash
python3 scripts/build_rcc002_spec_bundle.py \
  --title "RCC-002 C1 Corrected Full Specification Bundle" \
  --korrekturstand "C1-Corrected Draft – full re-review pending (Row Preservation harmonization S2-S7 [C1] + S7-S8 explicit invariant and cross-references [post-AIR-003]; patch versions 0.7.1/0.4.1/0.4.1 unchanged)" \
  --output docs/review/RCC_002_C1_CORRECTED_FULL_SPEC_BUNDLE_2026-07-25.md
```

Generator: `scripts/build_rcc002_spec_bundle.py` (neu erstellt; im Repository
existierte zuvor kein dokumentierter oder auffindbarer Bundle-Generator).
Der Generator führt die sieben Dateien unter `docs/specifications/` in der
durch das alte Bundle etablierten festen Reihenfolge ohne inhaltliche
Transformation zusammen und wurde vor produktivem Einsatz durch einen
Round-Trip-Test verifiziert: eine Ausführung gegen unveränderte, aus dem
alten Bundle rekonstruierte Quelldateien reproduziert
`RCC_002_SCR_005_CORRECTED_FULL_SPEC_BUNDLE_2026-07-24.md` byte-exakt
(identischer SHA-256).

Am 2026-07-25 gehärtet (Empfehlungen aus
`RCC_002_C1_SCIENTIFIC_CONSISTENCY_REVIEW_2026-07-25.md`, Minor Findings
m1/m2), ohne Änderung am Bundle-Format selbst:

- klare Fehlermeldung statt rohem Traceback bei fehlender Quelldatei;
- Erkennung doppelt vorkommender Dateinamen in der festen Dokumentliste;
- Prüfung der erwarteten Dokumentanzahl (genau 7) gegen den tatsächlichen
  Verzeichnisinhalt von `docs/specifications/`;
- Erkennung unerwarteter zusätzlicher `.md`-Dateien im Quellverzeichnis;
- Schreiben mit `newline="\n"` für plattformunabhängig deterministische
  Bundle-Bytes.

Die Härtung wurde durch drei Negativtests verifiziert (fehlende Datei,
zusätzliche Datei, danach erneuter Erfolgslauf) sowie durch einen erneuten
Round-Trip-Test nach der Härtung.

## 6. Übertragung bestehender Freigaben — ausdrücklicher Hinweis

```text
RCC-002-SCR-006 (PASSED) bezieht sich ausschließlich auf
RCC_002_SCR_005_CORRECTED_FULL_SPEC_BUNDLE_2026-07-24.md.

RCC-002-AIR-002 (PASSED) bezieht sich ausschließlich auf
RCC_002_SCR_005_CORRECTED_FULL_SPEC_BUNDLE_2026-07-24.md.

Editorial Pass und Internal Certification wurden für das alte Bundle
weder in den vorliegenden Unterlagen als durchgeführt noch als
bestanden dokumentiert.

Keine dieser Freigaben überträgt sich automatisch auf
RCC_002_C1_CORRECTED_FULL_SPEC_BUNDLE_2026-07-25.md.

Reviewstatus für das C1-korrigierte Paket (Stand 2026-07-25):

    Scientific Consistency Review (RCC-002-C1-SCR): BESTANDEN
        mit Minor Findings (siehe
        RCC_002_C1_SCIENTIFIC_CONSISTENCY_REVIEW_2026-07-25.md);
        das Major Finding (Versionierung) wurde umgesetzt.

    Architecture Integrity Review (RCC-002-AIR-003): BESTANDEN
        mit Minor Findings (siehe
        RCC_002_AIR_003_C1_ARCHITECTURE_REVIEW_2026-07-25.md);
        das Major Finding AIR3-M1 (fehlende S7-S8-Row-Preservation-
        Invariante) sowie Minor Finding AIR3-m1 (fehlende
        §5.8-Rückverweise) wurden umgesetzt. Minor Finding AIR3-m2
        (kein eigenständiges S8-Publication-Gate-Kapitel) bleibt
        bestehen; gemäß Auftrag wurde kein neues S8-Publication-Gate
        eingeführt.

    Alle übrigen Gates: AUSSTEHEND.

Insbesondere weiterhin ausstehend:
  - Editorial Pass
  - Internal Certification
  - Claude Independent Architecture Review
  - Gemini Independent Scientific and Adversarial Audit
  - ChatGPT Final Consolidation
  - Baseline V1 Certified

Zusätzlich gesperrt bis zur Klärung von Finding C2 (Hash-Diskrepanz des
alten SCR-005-Bundles gegenüber dem in RCC-002-SCR-006/RCC-002-AIR-002
referenzierten Hash — siehe
docs/review/RCC_002_C2_REVIEW_LINEAGE_INVESTIGATION_2026-07-25.md):
Architecture Integrity Review, Editorial Pass, Internal Certification und
alle nachfolgenden Gates.
```

## 7. Unveränderte Artefakte

Das alte Bundle `RCC_002_SCR_005_CORRECTED_FULL_SPEC_BUNDLE_2026-07-24.md`
wurde nicht überschrieben, nicht gelöscht und nicht verändert (siehe
Abschnitt 3 zur unveränderten Hash-Identität). `RCC_002_SCR_006_FINDINGS_
2026-07-24.md` und `RCC_002_AIR_002_FINDINGS_2026-07-24.md` wurden ebenfalls
nicht verändert.

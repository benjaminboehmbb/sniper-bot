# RCC-002 DVSEV-001 Corrected Bundle Manifest

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Governance- und Identitätsnachweis |
| Dokument-ID | `RCC-002-DVSEV001-CORRECTED-BUNDLE-MANIFEST` |
| Titel | Bundle Manifest — RCC-002 DVSEV-001 Corrected Full Specification Bundle |
| Version | 1.0.0 |
| Datum | 2026-07-27 |
| Status | Kandidat — DVSEV-001 umgesetzt; fokussierte Re-Review, Editorial Pass und Internal Certification ausstehend |
| Speicherort im Repository | `docs/review/RCC_002_DVSEV001_CORRECTED_BUNDLE_MANIFEST_2026-07-27.md` |
| Dateiname | `RCC_002_DVSEV001_CORRECTED_BUNDLE_MANIFEST_2026-07-27.md` |
| Abhängigkeiten | `docs/review/RCC_002_DVSEV_001_REASON_CODE_SEVERITY_CORRECTION_PROPOSAL_2026-07-27.md`; `docs/review/RCC_002_DVSEV001_CORRECTION_RECORD_2026-07-27.md`; `docs/review/RCC_002_DVSEV001_IMPACT_ANALYSIS_2026-07-27.md`; `docs/review/RCC_002_DVSEV001_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md`; `scripts/build_rcc002_spec_bundle.py` |
| Referenziert durch | fokussierte Re-Review von DVSEV-001 (ausstehend); Editorial Pass (ausstehend) |
| Autoritative Sprache | Deutsch für normative Erläuterung; englische Feld-, Reason-Code- und Konstantennamen wie im Quellmaterial |
| Änderung gegenüber der vorigen Bundle-Fassung | Ausschließlich DVSEV-001-Korrektur umgesetzt: neuer Abschnitt 16.3 „Reason-Code-Severity-Register" in Data Validation, der die in §16.2 geforderte und in §24.1 Nr. 3 vorausgesetzte Standard-Severity für alle 32 registrierten Reason Codes vollständig und deterministisch festlegt (6 bereits bestehende Zuordnungen unverändert übernommen, 26 neu ergänzt); Data Validation 0.4.2→0.5.0 (Minor); mechanische Abhängigkeitszitat-Folgeanpassungen in Indicator, Signal Transformation, Regime and Gate, Label and Forward Return (jeweils ohne eigene Versionsänderung) und in Reproducibility and Manifest 0.7.1→0.7.2 (rein mechanisch: Kopfzeile, §12.3-Tabelle, neuer datierter Abschnitt-29-Absatz, Statuszeile). Data Pipeline unverändert. Keine bestehende Regel, kein bestehender Reason Code und keine bestehende Severity-Zuweisung wurde verändert. |

## 1. Vollständige Dateiliste in Bundle-Reihenfolge

| # | Datei | Version | Zeilen | Bytes | SHA-256 | Geändert für DVSEV-001? |
|---:|---|---|---:|---:|---|:---:|
| 1 | `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md` | 0.7.1 | 2592 | 134284 | `529f83a27c0464af0954213ffc0e81b26819bf846a1b7a6085a6b323bddf87a2` | Nein — unverändert, byte-identisch |
| 2 | `RCC_002_DATA_VALIDATION_2026-07-23.md` | 0.5.0 | 1437 | 51646 | `bceb8e0dba5e8a71dad012499165d139dbf8a450afea2d9525a0a4d5e4cc28f1` | Ja — neuer §16.3 „Reason-Code-Severity-Register"; Version 0.4.2→0.5.0; neuer Review-Nachweis-Eintrag |
| 3 | `RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md` | 0.4.3 | 1751 | 51591 | `e0f8641cc95575338adad3e2e636740d22de1349926f80d87f03f20fb8564af5` | Ja — ausschließlich mechanische Zitat-Korrektur (Data-Validation-Abhängigkeit auf 0.5.0); eigene Version unverändert |
| 4 | `RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md` | 0.4.2 | 1674 | 53861 | `0538a660631aad1fa73a5db72bc45eba8d0c73ce2199f96b47c264be8136b4a5` | Ja — ausschließlich mechanische Zitat-Korrektur (Data-Validation-Abhängigkeit auf 0.5.0); eigene Version unverändert |
| 5 | `RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md` | 0.5.1 | 2216 | 68324 | `26d675e26cc5a014c962ed51910f170e3369a1e39e34ca1cfec9027ce5f5eeff` | Ja — ausschließlich mechanische Zitat-Korrektur (Data-Validation-Abhängigkeit auf 0.5.0); eigene Version unverändert |
| 6 | `RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md` | 0.4.1 | 2017 | 60288 | `8f6c02e13378521b4ae09b08d2ad3c610a27383a2d6a589e003e4febcacceb33` | Ja — ausschließlich mechanische Zitat-Korrektur (Data-Validation-Abhängigkeit auf 0.5.0); eigene Version unverändert |
| 7 | `RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md` | 0.7.2 | 2316 | 79532 | `3f795db4ffb9427efa73519c8390cf21bda67e82e0313b037d59b57027dca846` | Ja — mechanisch: Kopfzeile, §12.3-Tabelle, Statuszeile, neuer datierter Abschnitt-29-Absatz, Version |

Zeilen 3–6 (Indicator; Signal Transformation; Regime and Gate; Label and
Forward Return) erhalten **keine** eigene Versionsänderung: ihre Änderung
ist ausschließlich die mechanische Aktualisierung der zitierten
Data-Validation-Version von `0.4.2` auf `0.5.0` in der jeweiligen
Dokumentmetadaten-Kopfzeile — kein Feld, keine Regel und kein Reason Code
dieser vier Dokumente wurde verändert. Byte- und Zeilenzahl-Deltas
gegenüber der vorigen Bundle-Fassung bestehen ausschließlich, weil
`0.4.2` und `0.5.0` gleich lang sind (je 5 Zeichen); die Zeilenzahl
bleibt in allen vier Fällen exakt unverändert.

## 2. Bundle-Identität

| Feld | Wert |
|---|---|
| Datei | `docs/review/RCC_002_DVSEV001_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md` |
| Zeilen | 14070 |
| Bytes | 501799 |
| SHA-256 | `8a6ab7d732e02727199e704313c38959161c3929441fddce34b4ee4f2586d9ee` |
| Zeilendelta zur vorigen Fassung | +90 (Data Validation +55: neuer §16.3-Abschnitt inkl. 32-zeiliger Tabelle und Review-Nachweis-Zeile; Reproducibility +35: neuer §29-Absatz, Abhängigkeitsblock, Statuszeile, Kopfzeile, §12.3-Zeile; Indicator/Signal Transformation/Regime and Gate/Label and Forward Return je 0 Zeilendelta — reine Inhaltsänderung derselben Zeile) |
| Vorgängerfassung dieses Bundles | `RCC_002_AIR4_MIN01_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md`, 13980 Zeilen, 495922 Bytes, SHA-256 `39314fd6b6c186c3bc27932c701a36d1456f8f0a6009518617e6af592cea139a` — durch diese Version ersetzt als aktueller Bearbeitungsstand (nicht überschrieben, nicht gelöscht; siehe Abschnitt 3 und 6) |

## 3. Referenzidentität des vorigen Bundles (unverändert)

| Feld | Wert |
|---|---|
| Datei | `docs/review/RCC_002_AIR4_MIN01_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md` |
| Zeilen | 13980 |
| Bytes | 495922 |
| SHA-256 | `39314fd6b6c186c3bc27932c701a36d1456f8f0a6009518617e6af592cea139a` |

Unabhängig neu berechnet und mit dem in `rcc002/__init__.py` fest
kodierten `CERTIFIED_BUNDLE_SHA256` verglichen: **identisch**. Das
bisher zertifizierte Bundle bleibt bis zu einer expliziten
Freigabeentscheidung (Re-Review, Editorial Pass, Internal Certification)
referenziert; `rcc002/__init__.py` wurde in diesem Korrekturzyklus
**nicht** verändert (siehe Abschnitt 7, Downstream-Hinweis).

## 4. Git-Zustand vor der Änderung

| Feld | Wert |
|---|---|
| Git-Commit vor der Änderung (HEAD) | `b3851fec9d247ed6fa2539210ea62d5087f9dd8a` |
| Zustand der Arbeitskopie | `docs/specifications/` und `docs/review/` vollständig untracked (nie committet); `rcc002/` und `tests/rcc002/` vollständig untracked |
| Commit im Rahmen dieser Aufgabe | Keiner — kein Commit erstellt |

## 5. Generierungsbefehl

```bash
python3 scripts/build_rcc002_spec_bundle.py \
  --title "RCC-002 DVSEV-001 Corrected Full Specification Bundle" \
  --korrekturstand "DVSEV-001-Corrected Draft -- Reason-Code-Severity-Register (Data Validation sec. 16.3) added, closing Sec. 16.2/24.1(3) gap; Data Validation 0.4.2->0.5.0, Reproducibility 0.7.1->0.7.2 (mechanical), downstream dependency citations updated; full re-review pending" \
  --output docs/review/RCC_002_DVSEV001_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md
```

Generator: `scripts/build_rcc002_spec_bundle.py` — **unverändert**. Bereits
vorhandenes `--output`-Argument verwendet; keine Codeänderung erforderlich.

## 6. Unveränderte Artefakte

Das vorige Bundle `RCC_002_AIR4_MIN01_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md`
und sein Manifest `RCC_002_AIR4_MIN01_CORRECTED_BUNDLE_MANIFEST_2026-07-27.md`
wurden nicht überschrieben, nicht gelöscht und nicht verändert (Hash-Vergleich
siehe Abschnitt 3). Alle vorangegangenen Korrekturzyklen (`C1`,
`Minor Correction Cycle`, `AIR4-MIN-01`) und ihre Artefakte bleiben
unverändert.

## 7. Downstream-Hinweis (nicht Teil dieses Korrekturzyklus)

`rcc002/__init__.py` referenziert weiterhin
`CERTIFIED_BUNDLE_PATH = RCC_002_AIR4_MIN01_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md`
und den zugehörigen `CERTIFIED_BUNDLE_SHA256`. Dieser Zeiger wurde in
diesem Zyklus **bewusst nicht aktualisiert**, da die Aufgabenstellung für
diesen Korrekturzyklus ausdrücklich keine Implementierungsänderung umfasst
("Do not resume implementation"). Die Aktualisierung von
`rcc002/__init__.py` auf das DVSEV-001-Bundle sowie die in
`RCC_002_DVSEV_001_REASON_CODE_SEVERITY_CORRECTION_PROPOSAL_2026-07-27.md`
§6.3 benannten Code- und Testanpassungen
(`rcc002/s0/integrity.py::TruncationFinding.severity` Standardwert,
zentrales Severity-Register-Modul für Schritt 4) bleiben ausdrücklich der
Implementierungsfortsetzung (Schritt 4) vorbehalten.

# RCC-002 AIR4-MIN-01 Corrected Bundle Manifest

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Governance- und Identitätsnachweis |
| Dokument-ID | `RCC-002-AIR4-MIN01-CORRECTED-BUNDLE-MANIFEST` |
| Titel | Bundle Manifest — RCC-002 AIR4-MIN-01 Corrected Full Specification Bundle |
| Version | 1.0.0 |
| Datum | 2026-07-27 |
| Status | Kandidat — AIR4-MIN-01 geschlossen; fokussierte Re-Review, Editorial Pass und Internal Certification ausstehend |
| Speicherort im Repository | `docs/review/RCC_002_AIR4_MIN01_CORRECTED_BUNDLE_MANIFEST_2026-07-27.md` |
| Dateiname | `RCC_002_AIR4_MIN01_CORRECTED_BUNDLE_MANIFEST_2026-07-27.md` |
| Abhängigkeiten | `docs/review/RCC_002_AIR_004_FULL_SCOPE_REPLACEMENT_ARCHITECTURE_INTEGRITY_REVIEW_2026-07-27.md`; `docs/review/RCC_002_AIR4_MIN01_IMPLEMENTATION_RECORD_2026-07-27.md`; `docs/review/RCC_002_AIR4_MIN01_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md`; `scripts/build_rcc002_spec_bundle.py` |
| Referenziert durch | fokussierte Re-Review von AIR4-MIN-01 (ausstehend); Editorial Pass (ausstehend) |
| Autoritative Sprache | Deutsch für normative Erläuterung; englische Feld- und Konstantennamen wie im Quellmaterial |
| Änderung gegenüber der vorigen Bundle-Fassung | Ausschließlich AIR4-MIN-01-Korrektur umgesetzt: `PASS_WITH_APPROVED_EXCEPTIONS`-Carve-out-Listen in Indicator §30 und Signal Transformation §32 als abschließend klargestellt (kein neuer Ausnahmetyp, keine automatische Freigabe); Indicator 0.4.2→0.4.3, Signal Transformation 0.4.1→0.4.2; mechanische Abhängigkeitszitat-Folgeanpassungen in Regime and Gate und Label and Forward Return (jeweils ohne eigene Versionsänderung); Reproducibility and Manifest 0.7.0→0.7.1 (rein mechanisch: Kopfzeile, §12.3, neuer datierter §29-Absatz). Data Pipeline und Data Validation unverändert. Keine Architekturänderung, keine neue Ausnahmeart. |

## 1. Vollständige Dateiliste in Bundle-Reihenfolge

| # | Datei | Version | Zeilen | Bytes | SHA-256 | Geändert für AIR4-MIN-01? |
|---:|---|---|---:|---:|---|:---:|
| 1 | `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md` | 0.7.1 | 2592 | 134284 | `529f83a27c0464af0954213ffc0e81b26819bf846a1b7a6085a6b323bddf87a2` | Nein — unverändert, byte-identisch |
| 2 | `RCC_002_DATA_VALIDATION_2026-07-23.md` | 0.4.2 | 1382 | 46926 | `9bb70245d2001ee2676f63a9e89b396c9b71dc575e72da6084dd617ce41b258d` | Nein — unverändert, byte-identisch |
| 3 | `RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md` | 0.4.3 | 1751 | 51591 | `80e77f3a29e753b028d479a0a383010ce7c16804a74420f465e99eb4dcdfe70b` | Ja — §30 abschließende Carve-out-Klarstellung, Version, Änderungsverlaufseintrag |
| 4 | `RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md` | 0.4.2 | 1674 | 53861 | `5981aa15c317d5675e9adc71aecd7a26dc7abbfe0f5ac45947faa993c7022a0b` | Ja — §32 abschließende Carve-out-Klarstellung, Version, Indicator-Zitat, Änderungsverlaufseintrag |
| 5 | `RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md` | 0.5.1 | 2216 | 68324 | `ad981e2dcdc935aef1a3f6f107e0bfce4070b6926d2eb65da4fe209a31c2c346` | Ja — ausschließlich mechanische Zitat-Korrektur (Indicator/Signal Transformation); eigene Version unverändert |
| 6 | `RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md` | 0.4.1 | 2017 | 60288 | `99b68f1933859f4da1a92676e9fb6c3a8b78f25eeb2ad4b4fd42db66769751b9` | Ja — ausschließlich mechanische Zitat-Korrektur (Indicator/Signal Transformation); eigene Version unverändert |
| 7 | `RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md` | 0.7.1 | 2281 | 78142 | `20a50faf2851db7fcf85bc0c776b592f39a08259b32e7b80b80866b5d4e60619` | Ja — mechanisch: Kopfzeile, §12.3-Tabelle, neuer datierter §29-Absatz, Version |

Zeilen 5 und 6 (Regime and Gate; Label and Forward Return) erhalten **keine**
eigene Versionsänderung, entsprechend der ausdrücklichen Vorgabe des
AIR4-MIN-01-Korrekturauftrags: ihre Änderung ist ausschließlich eine
mechanische Abhängigkeitszitat-Korrektur ohne inhaltliche Bedeutung für das
jeweilige Dokument selbst.

## 2. Bundle-Identität

| Feld | Wert |
|---|---|
| Datei | `docs/review/RCC_002_AIR4_MIN01_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md` |
| Zeilen | 13980 |
| Bytes | 495922 |
| SHA-256 | `39314fd6b6c186c3bc27932c701a36d1456f8f0a6009518617e6af592cea139a` |

## 3. Referenzidentität des vorigen Bundles (unverändert)

| Feld | Wert |
|---|---|
| Datei | `docs/review/RCC_002_MINOR_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md` |
| Zeilen | 13926 |
| Bytes | 493231 |
| SHA-256 | `8bd00fd09055e0055b09642edbdddf105c25ea1f36b720c1892f07d360aca75f` |

Das vorige Bundle wurde nicht überschrieben, nicht gelöscht und nicht
verändert (siehe Abschnitt 6).

## 4. Git-Zustand vor der Änderung

| Feld | Wert |
|---|---|
| Git-Commit vor der Änderung (HEAD) | `e2e1d022e37bc871d5024d79cf9484c3a1ee9df1` |
| Zustand der Arbeitskopie | `docs/specifications/` und `docs/review/` vollständig untracked (nie committet) |
| Commit im Rahmen dieser Aufgabe | Keiner — kein Commit erstellt |

## 5. Generierungsbefehl

```bash
python3 scripts/build_rcc002_spec_bundle.py \
  --title "RCC-002 AIR4-MIN-01 Corrected Full Specification Bundle" \
  --korrekturstand "AIR4-MIN-01 targeted correction 2026-07-27: PASS_WITH_APPROVED_EXCEPTIONS carve-outs in Indicator §30 and Signal Transformation §32 clarified as exhaustive (no new exception type, no automatic approval). Indicator 0.4.2->0.4.3, Signal Transformation 0.4.1->0.4.2. Mechanical dependency-citation follow-ons in Regime and Gate, Label and Forward Return (no version change), and Reproducibility and Manifest (0.7.0->0.7.1, citations + §12.3 only). Data Pipeline and Data Validation unchanged." \
  --output docs/review/RCC_002_AIR4_MIN01_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md
```

Generator: `scripts/build_rcc002_spec_bundle.py` — **unverändert**. Bereits
vorhandenes `--output`-Argument verwendet; keine Codeänderung erforderlich.

## 6. Unveränderte Artefakte

Das vorige Bundle `RCC_002_MINOR_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md`
und sein Manifest wurden nicht überschrieben, nicht gelöscht und nicht
verändert (Hash-Vergleich siehe Abschnitt 3). `RCC_002_SCR_008_FULL_SCOPE_
RE_REVIEW_2026-07-27.md` und `RCC_002_AIR_004_FULL_SCOPE_REPLACEMENT_
ARCHITECTURE_INTEGRITY_REVIEW_2026-07-27.md` wurden ebenfalls nicht
verändert.

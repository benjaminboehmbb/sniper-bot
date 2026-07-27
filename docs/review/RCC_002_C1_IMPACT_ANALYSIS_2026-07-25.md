# RCC-002 C1 Impact Analysis

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Review- und Wirkungsanalyse |
| Dokument-ID | `RCC-002-C1-IMPACT-ANALYSIS` |
| Titel | Impact Analysis — RCC-002 Finding C1 (Row-Disposition-Widerspruch) |
| Version | 1.0.0 |
| Datum | 2026-07-25 |
| Status | Abgeschlossen — normative Harmonisierung ohne Verhaltensänderung |
| Speicherort im Repository | `docs/review/RCC_002_C1_IMPACT_ANALYSIS_2026-07-25.md` |
| Dateiname | `RCC_002_C1_IMPACT_ANALYSIS_2026-07-25.md` |
| Abhängigkeiten | `RCC_002_C1_VERIFICATION_RECORD_2026-07-25.md`; `RCC_002_SCR_005_CORRECTED_FULL_SPEC_BUNDLE_2026-07-24.md`; geänderte Quelldokumente unter `docs/specifications/` |
| Referenziert durch | `RCC_002_C1_CORRECTED_BUNDLE_MANIFEST_2026-07-25.md`; `RCC_002_C1_CORRECTED_FULL_SPEC_BUNDLE_2026-07-25.md` |
| Autoritative Sprache | Deutsch für normative Erläuterung; englische Feld- und Konstantennamen wie im Quellmaterial |

## 1. Direkt betroffene Dokumente und Normstellen

| Dokument | Version vorher → nachher | Normstelle | Art der Änderung |
|---|---|---|---|
| `RCC_002_DATA_PIPELINE_SPECIFICATION` | 0.7.0 (Inhalt unverändert versioniert) | neu: §5.8 „Kanonisches Row-Preservation-Prinzip“ | Ergänzung eines globalen Architekturprinzips |
| `RCC_002_DATA_VALIDATION` | 0.4.0 (Inhalt unverändert versioniert) | §20, Kriterium 16 | Präzisierung: deterministischer Wert statt Row-Filtering-Wortlaut |
| `RCC_002_INDICATOR_SPECIFICATION` | 0.4.0 (Inhalt unverändert versioniert) | §4.3; §30, Kriterium 2 | Präzisierung: deterministischer Wert statt Row-Filtering-Wortlaut |

Die Versionsfelder der drei Dokumente wurden bewusst **nicht** hochgezählt.
Dies ist eine Wortlautkorrektur eines nachgewiesenen internen Widerspruchs
innerhalb desselben Freigabezyklus (Harmonisierung auf das bereits an
anderer Stelle in denselben Dokumenten geltende Modell), keine neue
fachliche Festlegung. Eine Versionsentscheidung sowie die Aktualisierung der
Review-Nachweis-Tabellen (Scientific Consistency Review, Architecture
Integrity Review) bleiben dem vorgeschriebenen nächsten Review-Schritt
vorbehalten (siehe Abschnitt 6 und Governance-Wirkung, Abschnitt 8).

## 2. Indirekt geprüfte Dokumente

Alle sieben kanonischen Spezifikationen wurden auf Vorkommen von
`quality_gate_pass=true`, `quality_gate_pass=false`, „kanonisch
veröffentlicht“, „Publication Build“, „Publication Gate“, „Zeile
entfernen/ausschließen“, „Row Preservation“, `S2_rows` bis `S7_rows`,
`BLOCK_BOTH`, „Quarantäne“ und „Abbruch“ durchsucht:

- `RCC_002_SIGNAL_TRANSFORMATION_SPECIFICATION` — konsistent, unverändert.
- `RCC_002_REGIME_AND_GATE_SPECIFICATION` — konsistent, unverändert
  (enthält die am häufigsten referenzierte, bereits korrekte
  `BLOCK_BOTH`-Wahrheitstabelle sowie `S5_rows = S4_rows`).
- `RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION` — konsistent,
  unverändert (`S7_rows = S6_rows`; Qualitätsvertrag bezieht sich auf
  einzelne verwendete Preiszeilen, nicht auf Zeilenexistenz).
- `RCC_002_REPRODUCIBILITY_AND_MANIFEST_SPECIFICATION` — konsistent,
  unverändert (Quarantäne ausschließlich als Artefakt-/Ergebnis-Status
  definiert).

Für keines dieser vier Dokumente wurde ein echter normativer Widerspruch
zum bestätigten Modell (Row Preservation) festgestellt. Es wurden daher
keine Änderungen vorgenommen.

## 3. Unveränderte Architekturprinzipien

Folgende bereits bestehende, mit Row Preservation konsistente Verträge
bleiben vollständig unverändert und wurden durch die Korrektur lediglich
explizit normativ verankert, nicht neu geschaffen:

- `S3_rows = S2_rows`, `S4_rows = S3_rows`, `S5_rows = S4_rows`,
  `S7_rows = S6_rows`.
- die S6-Wahrheitstabelle (`data_gate_pass = quality_gate_pass`;
  `gültig/false/nicht ausgewertet → BLOCK_BOTH`).
- die Trennung von `gate_valid=true` (gültiges `BLOCK_BOTH`) und
  `gate_valid=false` (`INVALID`).
- die Segment-ID-Bildung (`market_segment_id`, `indicator_segment_id`) für
  Zeilen mit `quality_gate_pass=false`.
- `PASS_WITH_APPROVED_EXCEPTIONS` als Build-Level-Ausnahmemechanismus.
- Abbruch und Quarantäne als Artefakt-/Build-Level-Mechanismen.

## 4. Implementierungswirkung

Für eine künftige Implementierung ändert sich die fachliche Zielsemantik
**nicht** — die Korrektur beseitigt lediglich eine Textstelle, die, wörtlich
implementiert, mit den übrigen 90 % der Spezifikationsfamilie unvereinbar
gewesen wäre und andernfalls zu einer von zwei fehlerhaften Implementierungen
geführt hätte:

1. eine Implementierung, die `S3_rows = S2_rows` bricht (durch stillschweigende
   Zeilenfilterung in S2 oder S3), oder
2. eine Implementierung, die den kanonischen S6-Zustand `BLOCK_BOTH` für
   qualitätsbedingt blockierte Zeilen niemals erreichen kann, weil solche
   Zeilen bereits vor S6 aus dem Datenstrom entfernt wurden.

Nach der Korrektur ist eindeutig spezifiziert, dass Implementierungen Zeilen
mit `quality_gate_pass=false` durchgängig mitführen und ausschließlich über
Gültigkeits-/Reason-Code-Felder sowie `BLOCK_BOTH` behandeln müssen.

## 5. Testwirkung

Die Korrektur macht bestehende, bereits spezifizierte Testanforderungen
konsistent erfüllbar, ohne neue Testanforderungen einzuführen:

- Reconciliation-Tests (`S3_rows = S2_rows` etc.) und die
  `BLOCK_BOTH`-Testfälle in `RCC_002_REGIME_AND_GATE_SPECIFICATION` §32
  waren zuvor gegenüber `RCC_002_DATA_VALIDATION` §20/`RCC_002_INDICATOR_
  SPECIFICATION` §30 widersprüchlich spezifiziert; ein Testsystem, das
  beide Kriteriensätze wörtlich implementiert hätte, konnte sie nicht
  gleichzeitig bestehen.
- Nach der Korrektur sind Golden-Test-Fälle für „strukturell gültige Zeile,
  `quality_gate_pass=false`, Zeile bleibt erhalten, `BLOCK_BOTH` bei S6“
  widerspruchsfrei aus allen sieben Dokumenten ableitbar.

## 6. Governance-Wirkung

- Die Korrektur berührt ausschließlich Wortlaut innerhalb bereits
  bestehender, im Bundle enthaltener Kriterien; sie führt keine neue
  RCC-000-Spezifikation, keine achte RCC-002-Kernspezifikation und keine
  neue Architekturentscheidung ein.
- Da `RCC-002-SCR-006` und `RCC-002-AIR-002` das ursprüngliche Paket bereits
  als „Bestanden“ geführt hatten, gilt: diese Freigaben bezogen sich auf den
  **vor** dieser Korrektur bestehenden Wortlaut. Die vorliegende Änderung
  erfordert einen erneuten, fokussierten Re-Review nach demselben Muster wie
  `RCC-002-SCR-005` → `RCC-002-SCR-006` (siehe
  `RCC_002_C1_CORRECTED_BUNDLE_MANIFEST_2026-07-25.md`, das SCR-006/AIR-002/
  Editorial Pass/Internal Certification des alten Bundles ausdrücklich nicht
  auf das neue Bundle überträgt).
- Unabhängig von C1 wurde festgestellt (und im Verification Record
  dokumentiert), dass `docs/specifications/` vor dieser Korrektur veraltete,
  vor-SCR-005 Entwürfe enthielt und nie mit dem tatsächlich geprüften
  Bundle-Inhalt übereinstimmte. Dieser Sachverhalt wurde vor jeder
  inhaltlichen Änderung an den Nutzer eskaliert und erst nach dessen
  Entscheidung (Wiederherstellung der Quelldateien aus dem geprüften Bundle)
  behoben; er ist eine separate Governance-Beobachtung und nicht Teil der
  fachlichen C1-Korrektur selbst.

## 7. Risiko bei Nichtkorrektur

Ohne Korrektur bliebe ein Implementierungsteam vor einer nicht auflösbaren
Spezifikationslücke: zwei Kriterien verlangen wörtlich Zeilenfilterung,
mindestens fünf weitere Kernverträge verlangen wörtlich Zeilenerhalt. Jede
Wahl würde einen der beiden Vertragssätze verletzen, mit direkten Folgen für
Reproduzierbarkeit (Zeilenzahl-Invarianten), Datenqualitäts-Gate-Semantik
(`BLOCK_BOTH` vs. Nichterreichbarkeit) und nachgelagerte Label-/
Backtest-Konsistenz.

## 8. Risiko der Korrektur

Die Korrektur selbst birgt geringes Risiko, da sie:

- keine Zeilenfilterung einführt,
- keine bestehende Pipeline-Architektur verändert,
- keine neue Priorisierungsregel erzeugt, die lokale Stage Contracts
  pauschal überschreibt,
- ausschließlich die Minderheitsposition (zwei Kriterien in zwei Dokumenten)
  an die bereits dominante, mehrfach unabhängig bestätigte Mehrheitsposition
  (fünf Dokumente, einschließlich der von SCR-006 geprüften S6-
  Wahrheitstabelle) angleicht.

Verbleibendes Restrisiko: die Korrektur wurde bisher nur intern verifiziert
(dieses Dokument und der Verification Record), nicht durch einen
unabhängigen Scientific-Consistency- oder Architecture-Integrity-Re-Review
bestätigt.

## 9. Vollständige Liste aller tatsächlich vorgenommenen Änderungen

1. `docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`:
   neue Untersektion „5.8 Kanonisches Row-Preservation-Prinzip“ nach §5.7,
   vor „## 6. Kanonischer Datenfluss“. Keine sonstige Änderung.
2. `docs/specifications/RCC_002_DATA_VALIDATION_2026-07-23.md`: §20,
   Kriterium 16 umformuliert (deterministischer Wert statt
   `quality_gate_pass=true`-Pflicht; expliziter Row-Preservation-Zusatz).
   Kriterien 1–15 und 17–18 unverändert, Nummerierung unverändert.
3. `docs/specifications/RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md`:
   §4.3, Absatz „Im kanonischen S3-Publication-Build …“ ersetzt durch
   row-preservation-konformen Wortlaut; §30, Kriterium 2 umformuliert
   (deterministischer Wert statt `quality_gate_pass=true`-Pflicht). Übrige
   Kriterien und Abschnitte unverändert, Nummerierung unverändert.
4. Vorbedingung (siehe Verification Record §8): alle sieben Dateien unter
   `docs/specifications/` wurden vor den obigen drei Änderungen
   deckungsgleich aus `RCC_002_SCR_005_CORRECTED_FULL_SPEC_BUNDLE_2026-07-24.md`
   rekonstruiert, da die zuvor dort liegenden Dateien veraltete Entwürfe
   waren. Die vier nicht in Punkt 1–3 genannten Dateien
   (`RCC_002_SIGNAL_TRANSFORMATION_SPECIFICATION`,
   `RCC_002_REGIME_AND_GATE_SPECIFICATION`,
   `RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION`,
   `RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md`) entsprechen nach
   dieser Rekonstruktion exakt dem im alten Bundle enthaltenen Inhalt
   (Zeilen-, Byte- und SHA-256-gleich mit der dortigen Datei-Tabelle) und
   wurden danach nicht weiter verändert.
5. Keine Zeilenfilterung, keine Row-Deletion-Logik, keine neue
   RCC-000-Spezifikation, keine achte RCC-002-Kernspezifikation eingeführt.

## 10. Ergebnis

```text
Normative Harmonisierung.
Keine beabsichtigte Änderung des kanonischen Pipeline-Verhaltens.
```

Die Korrektur beseitigt einen internen Wortlaut-Widerspruch zugunsten des
bereits an fünf von sieben Dokumentstellen geltenden, von `RCC-002-SCR-006`
unabhängig bestätigten Row-Preservation-Modells. Das fachliche Verhalten der
Pipeline — welche Zeilen im kanonischen Artefakt verbleiben, welche Werte
sie tragen und wie S6 sie klassifiziert — ändert sich dadurch nicht; es wird
lediglich für alle sieben Dokumente widerspruchsfrei dokumentiert.

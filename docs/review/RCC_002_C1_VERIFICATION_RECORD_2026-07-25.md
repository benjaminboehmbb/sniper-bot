# RCC-002 C1 Verification Record

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Review- und Verifikationsnachweis |
| Dokument-ID | `RCC-002-C1-VERIFICATION-RECORD` |
| Titel | Verification Record — RCC-002 Finding C1 (Row-Disposition-Widerspruch) |
| Version | 1.0.0 |
| Datum | 2026-07-25 |
| Status | Abgeschlossen — Entscheidung VERIFIED |
| Speicherort im Repository | `docs/review/RCC_002_C1_VERIFICATION_RECORD_2026-07-25.md` |
| Dateiname | `RCC_002_C1_VERIFICATION_RECORD_2026-07-25.md` |
| Abhängigkeiten | `RCC_002_SCR_005_CORRECTED_FULL_SPEC_BUNDLE_2026-07-24.md`; `RCC_002_SCR_006_FINDINGS_2026-07-24.md`; `RCC_002_AIR_002_FINDINGS_2026-07-24.md`; unabhängiger adversarialer Architektur-Review vom 2026-07-25 (nicht als eigenständiges Dokument abgelegt) |
| Referenziert durch | `RCC_002_C1_IMPACT_ANALYSIS_2026-07-25.md`; `RCC_002_C1_CORRECTED_BUNDLE_MANIFEST_2026-07-25.md`; `RCC_002_C1_CORRECTED_FULL_SPEC_BUNDLE_2026-07-25.md` |
| Autoritative Sprache | Deutsch für normative Erläuterung; englische Feld- und Konstantennamen wie im Quellmaterial |

## 1. Finding C1

Ein unabhängiger adversarialer Review des Pakets
`RCC_002_SCR_005_CORRECTED_FULL_SPEC_BUNDLE_2026-07-24.md` stellte fest, dass
zwei sich gegenseitig ausschließende normative Modelle für den Umgang mit
Zeilen mit `quality_gate_pass=false` gleichzeitig als verbindlich formuliert
waren:

- **Modell A (Row Filtering):** `RCC_002_DATA_VALIDATION` §20 Kriterium 16
  und `RCC_002_INDICATOR_SPECIFICATION` §4.3 sowie §30 Kriterium 2
  verlangten, dass jede veröffentlichte kanonische S2- beziehungsweise
  S3-Zeile `quality_gate_pass=true` besitzt — dem Wortlaut nach ein
  Ausschluss ungültiger Zeilen aus dem kanonischen Artefakt.
- **Modell B (Row Preservation):** die S6-Wahrheitstabelle in
  `RCC_002_DATA_PIPELINE_SPECIFICATION` §7.7 (unverändert bestätigt in
  `RCC-002-SCR-006` §5.4 als Schließung von `SCR-005-M02`), die
  Zeileninvarianten `S3_rows = S2_rows` (Indicator §26.2) und
  `S4_rows = S3_rows` (Signal Transformation §28.2) sowie die
  Segmentierungsregel in Indicator §21.2 verlangten, dass Zeilen mit
  `quality_gate_pass=false` unverändert im kanonischen Datenstrom bis
  mindestens S6 verbleiben und dort als gültiges `BLOCK_BOTH` erscheinen.

Beide Modelle können nicht gleichzeitig zutreffen, ohne dass entweder die
Zeileninvarianten oder die S6-Wahrheitstabelle verletzt werden.

## 2. Geprüfte Normstellen

| Dokument | Stelle | Aussage | Modell |
|---|---|---|---|
| `RCC_002_DATA_VALIDATION` | §20, Kriterium 16 | „jede veröffentlichte kanonische S2-Zeile `quality_gate_pass=true` besitzt“ | A |
| `RCC_002_INDICATOR_SPECIFICATION` | §4.3 | „Im kanonischen S3-Publication-Build muss jede Eingabezeile `quality_gate_pass=true` besitzen“ | A |
| `RCC_002_INDICATOR_SPECIFICATION` | §30, Kriterium 2 | „jede S2-Eingabezeile `quality_gate_pass=true` besitzt“ | A |
| `RCC_002_INDICATOR_SPECIFICATION` | §21.2 | „Zeilen mit `quality_gate_pass=false` erhalten eine Segment-ID“ | B |
| `RCC_002_INDICATOR_SPECIFICATION` | §26.2 | `S3_rows = S2_rows`, keine Ausnahme | B |
| `RCC_002_SIGNAL_TRANSFORMATION_SPECIFICATION` | §5.3, §28.2 | `quality_gate_pass=false` als blockierender, aber nicht zeilenentfernender Status; `S4_rows = S3_rows` | B |
| `RCC_002_DATA_PIPELINE_SPECIFICATION` | §7.7 | S6-Wahrheitstabelle: strukturell gültige Zeile mit `quality_gate_pass=false` → kanonisches `BLOCK_BOTH` | B |
| `RCC_002_REGIME_AND_GATE_SPECIFICATION` | §13.2, §30 | dieselbe Wahrheitstabelle; `S5_rows = S4_rows` | B |
| `RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION` | §5.5, §22 | Qualitätsvertrag je verwendeter Preiszeile; `S7_rows = S6_rows` | B |
| `RCC-002-SCR-006` (Vorgängerreview) | §5.4 | bestätigt die S6-Wahrheitstabelle unverändert als Schließung von `SCR-005-M02` | B |

## 3. Gegenhypothese: separate row-gefilterte Publikation

Vor der Entscheidung wurde geprüft, ob eine plausible Lesart existiert, nach
der Modell A tatsächlich gemeint und implementierbar ist — insbesondere die
Hypothese, dass ungültige Zeilen aus dem „veröffentlichten kanonischen“
Artefakt selektiv entfernt werden, während ein separates, nicht-kanonisches
Artefakt sie weiterführt.

Diese Gegenhypothese wurde geprüft und verworfen:

- Es existiert an keiner Stelle der Spezifikationsfamilie ein Mechanismus für
  eine **zeilenselektive** Veröffentlichung. Jede Erwähnung von
  Zeilenentfernung (`RCC_002_INDICATOR_SPECIFICATION`,
  `RCC_002_SIGNAL_TRANSFORMATION_SPECIFICATION`,
  `RCC_002_REGIME_AND_GATE_SPECIFICATION`,
  `RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION`, jeweils Abschnitt
  „Zeileninvariante“) formuliert ausdrücklich das Gegenteil: „keine Zeile
  entfernen“.
- Wäre Modell A korrekt, müsste jede historische BTCUSDT-1-Minuten-Zeitreihe
  mit auch nur einer einzigen zeilenweisen Qualitätsauffälligkeit über Jahre
  hinweg die gesamte S2-Veröffentlichung blockieren, da Kriterium 16 als
  Allquantor über sämtliche veröffentlichten Zeilen formuliert ist. Dies
  steht im Widerspruch zum eigens vorgesehenen Mechanismus
  `PASS_WITH_APPROVED_EXCEPTIONS`, der genau für den Fall nicht
  blockierender Einzelbefunde existiert.

## 4. Ergebnis der Quarantäne-/Abort-Prüfung

Geprüft wurde, ob die dokumentierten Mechanismen `Abbruch` (Build-Abbruch)
und `Quarantäne` eine implizite Row-Filtering-Semantik tragen könnten.

Ergebnis: **Nein.** Beide Mechanismen sind in der gesamten
Spezifikationsfamilie ausschließlich Artefakt- oder Build-Level-Konzepte:

- `RCC_002_DATA_VALIDATION` §2 (Begriffe): „Quarantäne: isolierter Zustand
  für fehlerhafte oder ungeklärte **Artefakte**“.
- `RCC_002_REPRODUCIBILITY_AND_MANIFEST` §8.1 und §19.4: „Quarantäne:
  Abgetrennter Status für unvollständige, fehlerhafte oder nicht
  freigegebene **Ergebnisse**“ / „Quarantänisierte **Artefakte**“.
- `RCC_002_DATA_VALIDATION` §16.1 (Severity-Tabelle): `CRITICAL` →
  „sofortiger Abbruch oder Quarantäne“ — beides bezogen auf den gesamten
  Build beziehungsweise das gesamte Artefakt, nicht auf Einzelzeilen.
- „Stage-Abbruch“ (`RCC_002_DATA_PIPELINE_SPECIFICATION` §7.7,
  `RCC_002_DATA_VALIDATION` §20) ist ausschließlich für **strukturelle**
  Eingangsfehler (Schema, Schlüssel, Sortierung, Segmentvertrag) definiert,
  niemals für eine ansonsten strukturell gültige Zeile mit
  `quality_gate_pass=false`.

Es existiert somit kein dokumentierter Mechanismus, der Modell A
implementierbar machen würde, ohne einen der beiden vorgenannten Begriffe
neu und abweichend zu definieren.

## 5. Entscheidung

```text
VERIFIED
```

Finding C1 ist ein echter normativer Widerspruch. Die Zielsemantik ist
Modell B (Row Preservation). Modell A war in den drei genannten Normstellen
fehlerhaft formuliert und wurde entsprechend korrigiert.

## 6. Begründung

1. Modell B verfügt über einen vollständig ausgearbeiteten, mehrfach
   redundant abgesicherten Implementierungspfad (Segment-IDs,
   `x_valid=false`, `y_valid=false`, `regime_valid=false`, `BLOCK_BOTH`,
   Zeileninvarianten `S3_rows = S2_rows` bis `S7_rows = S6_rows`) über fünf
   der sieben Dokumente hinweg.
2. Modell A verfügt über keinen einzigen dokumentierten
   Implementierungsmechanismus für selektive Zeilenentfernung; die einzigen
   verfügbaren Mechanismen (Abbruch, Quarantäne) sind nachweislich
   Artefakt-/Build-Level-Konzepte.
3. `RCC-002-SCR-006` hat die S6-Wahrheitstabelle (Kern von Modell B) bereits
   unabhängig geprüft und als Schließung von `SCR-005-M02` bestätigt. Eine
   Entscheidung für Modell A hätte diese bereits bestandene Prüfung
   nachträglich entwertet.
4. Modell A hätte in Kombination mit `PASS_WITH_APPROVED_EXCEPTIONS` und der
   Realität mehrjähriger Marktzeitreihen zu einer praktisch nicht
   erfüllbaren Anforderung geführt.

## 7. Gewählte Zielsemantik

`quality_gate_pass` steuert die **semantische Verwendbarkeit** einer Zeile
in nachgelagerten Berechnungen, nicht ihre **kanonische Existenz** im
Artefakt. Zeilen mit `quality_gate_pass=false` bleiben mit unveränderter
Row Identity, Row Order und Row Count im kanonischen Artefakt erhalten und
werden downstream ausschließlich durch deterministische, fail-closed
Zustände repräsentiert (ungültige/Null-Werte, `BLOCK_BOTH`). Eine Abweichung
von dieser Regel ist ausschließlich über einen vollständigen,
ausdrücklich normierten Build-Abbruch oder eine Artefakt-Quarantäne
zulässig — niemals über eine stillschweigende Zeilenfilterung innerhalb
eines veröffentlichten kanonischen Artefakts.

Diese Zielsemantik wurde als neues Architekturprinzip „5.8 Kanonisches
Row-Preservation-Prinzip“ in `RCC_002_DATA_PIPELINE_SPECIFICATION`
verankert und in den drei widersprüchlichen Normstellen (`RCC_002_DATA_
VALIDATION` §20 Kriterium 16; `RCC_002_INDICATOR_SPECIFICATION` §4.3 und
§30 Kriterium 2) entsprechend präzisiert. Details der Änderungen und ihrer
Wirkung stehen in `RCC_002_C1_IMPACT_ANALYSIS_2026-07-25.md`.

## 8. Hinweis zur Ausgangslage der Quelldokumente

Vor der Korrektur wurde festgestellt, dass die zum Zeitpunkt der Prüfung in
`docs/specifications/` vorliegenden Dateien veraltete, dem SCR-005-Zyklus
vorausgehende Entwürfe waren (Data Pipeline 0.6.0 statt 0.7.0, übrige
Dokumente jeweils eine Minor-Version älter als im geprüften Bundle
enthalten) und nicht mit dem Inhalt von
`RCC_002_SCR_005_CORRECTED_FULL_SPEC_BUNDLE_2026-07-24.md` übereinstimmten.
Vor Anwendung der C1-Korrektur wurden die sieben kanonischen Quelldokumente
daher zunächst deckungsgleich aus dem geprüften Bundle rekonstruiert
(verifiziert durch Zeilen-, Byte- und SHA-256-Gleichheit mit der im Bundle
selbst geführten Datei-Tabelle). Dieser Sachverhalt ist Teil des
unabhängigen Reviews vom 2026-07-25 und wird hier dokumentiert, weil er die
Ausgangslage für die vorliegende Korrektur bildet.

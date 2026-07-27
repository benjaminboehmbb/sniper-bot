# RCC-002 Minor Correction Cycle — Implementation Plan

## 0. Document Control

| Field | Value |
|---|---|
| Document Class | Verbindlicher Implementierungsplan (Planungsdokument, keine Ausführung) |
| Plan ID | `RCC-002-MINOR-CORRECTION-PLAN-2026-07-27` |
| Date | 2026-07-27 |
| Status | Plan vollständig, nicht ausgeführt |
| Grundlagen | ausschließlich: die sieben aktuellen kanonischen Spezifikationen unter `docs/specifications/`; `docs/review/RCC_002_SCR_007_FULL_SCOPE_REPLACEMENT_REVIEW_2026-07-27.md` (SHA-256 `175d489133f833a6aca6ca0aa80e1658cb54ff3672e224a51d778cb6e422cf39`); `docs/review/RCC_002_SCR_007_MAJOR_FINDINGS_VERIFICATION_2026-07-27.md` (SHA-256 `7aef0a8e92aded7945724cfc037896bbe1d6811be1b54e4fc99fd6025e63e287`); `docs/review/RCC_002_SCR_007_MINOR_FINDINGS_VERIFICATION_AND_CORRECTION_PLAN_2026-07-27.md` (SHA-256 `e1c7b1e5c4f4318b04369c6eef4aad5bf018eeca49bbcc91fc52165a3b464f8e`) |
| Working Mode | Planungsdokument. Keine Spezifikation, kein Bundle, kein Manifest verändert oder erzeugt. Keine Versionsnummer in einer realen Datei verändert. Kein Commit erstellt. |
| Ausgeschlossene, verworfene Findings (nicht Teil dieses Plans) | `SCR7-MIN-01` (REJECTED — Observation), `SCR7-MIN-03`/Indicator-Anteil (REJECTED — Observation, bereits über §30 Kriterium 16 MUST-verpflichtend getestet), `SCR7-MIN-04` (auf Future Architecture Risk/Observation herabgestuft — durch bestandenen Round-trip-Test bereits ausgeschlossen), `SCR7-MIN-05` (REJECTED — Observation), `SCR7-MIN-06` (REJECTED als Korrekturbedarf — Observation/Future Architecture Risk) |

---

## 1. Executive Summary

Dieser Plan enthält den vollständigen, endgültigen Änderungsumfang für den Minor-Correction-Cycle, abgeleitet ausschließlich aus den sechs in `RCC_002_SCR_007_MINOR_FINDINGS_VERIFICATION_AND_CORRECTION_PLAN_2026-07-27.md` bestätigten Findings: `SCR7-MIN-02`, `SCR7-MIN-03` (nur Signal-Transformation-Anteil), `SCR7-MIN-07`, `SCR7-MIN-08`, `SCR7-MAJ-02`, `SCR7-MAJ-03`.

Der Änderungsumfang betrifft **sechs von sieben** kanonischen Spezifikationen. `RCC_002_DATA_PIPELINE_SPECIFICATION` erhält **keine** Änderung — kein bestätigtes Finding betrifft dieses Dokument.

Der Plan umfasst **18 einzelne, dokumentbezogene Änderungen**, ausschließlich der Kategorien Version Correction, Dependency Correction, Editorial Correction und Terminology Correction. Keine Architekturänderung. Keine neue Testmethodik. Keine neue Versionierungsarchitektur.

---

## 2. Änderungen nach Datei

### 2.1 `docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`

**Keine Änderung.** Kein bestätigtes Finding betrifft dieses Dokument. Version bleibt `0.7.1`.

---

### 2.2 `docs/specifications/RCC_002_DATA_VALIDATION_2026-07-23.md`

#### Änderung DV-1

1. **Finding-ID:** `SCR7-MAJ-03`
2. **Datei:** `docs/specifications/RCC_002_DATA_VALIDATION_2026-07-23.md`
3. **Aktuelle Version:** `0.4.1`
4. **Neue Version:** `0.4.2`
5. **Paragraph:** Dokumentmetadaten (Feld „Version")
6. **Änderungstyp:** Version Correction
7. **Exakte Beschreibung:** Feld „Version" in der Dokumentmetadaten-Tabelle von `0.4.1` auf `0.4.2` ändern.
8. **Begründung:** Im laufenden Korrekturzyklus wurde dem Dokument ein neuer §5.8-Rückverweis-Satz hinzugefügt (reine Querverweis-Ergänzung, keine Änderung einer bestehenden testbaren Anforderung); nach der eigenen Kompatibilitätsregel des Dokumentfamilien-Leitdokuments (Data Pipeline §6.4: „Patch: redaktionelle oder nichtsemantische Metadatenkorrektur") ist dies mindestens Patch-pflichtig.
9. **Folgeänderungen:** Jedes Dokument, das Data Validation als Abhängigkeit zitiert (Indicator, Signal Transformation, Regime and Gate, Label and Forward Return, Reproducibility), muss seine Zitatstelle auf `0.4.2` aktualisieren (siehe jeweilige Dependency-Correction-Einträge unten).
10. **Validierung:** Sichtprüfung der Kopfzeile nach Änderung; Teil der globalen Bundle-/Manifest-Regeneration (Abschnitt 5).

#### Änderung DV-2

1. **Finding-ID:** `SCR7-MAJ-03`
2. **Datei:** `docs/specifications/RCC_002_DATA_VALIDATION_2026-07-23.md`
3. **Aktuelle Version:** n/a (betrifft zitierte Fremdversion, nicht die eigene Dokumentversion)
4. **Neue Version:** n/a
5. **Paragraph:** Dokumentmetadaten, Zeile „Übergeordnetes Dokument"
6. **Änderungstyp:** Dependency Correction
7. **Exakte Beschreibung:** Zelle „Übergeordnetes Dokument | `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`, Version 0.7.0" ändern zu „... Version 0.7.1".
8. **Begründung:** Data Pipeline wurde bereits im ursprünglichen C1-Zyklus auf `0.7.1` gepatcht; die Zitatstelle in Data Validation wurde dabei nie aktualisiert (bestätigt in `RCC_002_SCR_007_MAJOR_FINDINGS_VERIFICATION_2026-07-27.md`, Abschnitt 8).
9. **Folgeänderungen:** Keine (Data Pipeline selbst ändert sich nicht).
10. **Validierung:** Grep-Prüfung nach Änderung, dass keine Zitatstelle mehr „Version 0.7.0" enthält.

---

### 2.3 `docs/specifications/RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md`

#### Änderung IS-1

1. **Finding-ID:** `SCR7-MAJ-03`
2. **Datei:** `docs/specifications/RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md`
3. **Aktuelle Version:** `0.4.1`
4. **Neue Version:** `0.4.2`
5. **Paragraph:** Dokumentmetadaten (Feld „Version")
6. **Änderungstyp:** Version Correction
7. **Exakte Beschreibung:** Feld „Version" von `0.4.1` auf `0.4.2` ändern.
8. **Begründung:** Wie DV-1 — neuer §5.8-Rückverweis-Satz in diesem Zyklus hinzugefügt, Patch-pflichtig nach Data Pipeline §6.4.
9. **Folgeänderungen:** Signal Transformation, Regime and Gate, Label and Forward Return, Reproducibility zitieren Indicator als Abhängigkeit und müssen auf `0.4.2` aktualisiert werden.
10. **Validierung:** Sichtprüfung; Teil der globalen Bundle-/Manifest-Regeneration.

#### Änderung IS-2

1. **Finding-ID:** `SCR7-MAJ-03`
2. **Datei:** `docs/specifications/RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md`
3. **Aktuelle Version:** n/a (Fremdversionen)
4. **Neue Version:** n/a
5. **Paragraph:** Dokumentmetadaten, Zeilen „Übergeordnetes Dokument" und „Direkte Abhängigkeit"
6. **Änderungstyp:** Dependency Correction
7. **Exakte Beschreibung:** „Übergeordnetes Dokument | ... Version 0.7.0" → „... Version 0.7.1"; „Direkte Abhängigkeit | `RCC_002_DATA_VALIDATION_2026-07-23.md`, Version 0.4.0" → „... Version 0.4.2".
8. **Begründung:** Data Pipeline ist bereits `0.7.1`; Data Validation wird durch DV-1 auf `0.4.2` angehoben — beide Zitatstellen sind sonst veraltet.
9. **Folgeänderungen:** Keine über die bereits geplanten Änderungen hinaus.
10. **Validierung:** Grep-Prüfung, dass keine Zitatstelle mehr „Version 0.7.0" oder „Version 0.4.0" (bezogen auf Data Validation) enthält.

---

### 2.4 `docs/specifications/RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md`

#### Änderung ST-1

1. **Finding-ID:** `SCR7-MAJ-03`
2. **Datei:** `docs/specifications/RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md`
3. **Aktuelle Version:** `0.4.0`
4. **Neue Version:** `0.4.1`
5. **Paragraph:** Dokumentmetadaten (Feld „Version")
6. **Änderungstyp:** Version Correction
7. **Exakte Beschreibung:** Feld „Version" von `0.4.0` auf `0.4.1` ändern.
8. **Begründung:** Neuer §5.8-Rückverweis-Satz in diesem Zyklus hinzugefügt; dieses Dokument erhielt im gesamten bisherigen Korrekturzyklus noch keinen einzigen Versionsschritt, obwohl sich sein Inhalt bereits geändert hat.
9. **Folgeänderungen:** Regime and Gate, Label and Forward Return, Reproducibility zitieren Signal Transformation und müssen auf `0.4.1` aktualisiert werden.
10. **Validierung:** Sichtprüfung; Teil der globalen Bundle-/Manifest-Regeneration.

#### Änderung ST-2

1. **Finding-ID:** `SCR7-MAJ-03`
2. **Datei:** `docs/specifications/RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md`
3. **Aktuelle Version:** n/a (Fremdversionen)
4. **Neue Version:** n/a
5. **Paragraph:** Dokumentmetadaten, Zeilen „Übergeordnetes Dokument" und „Direkte Abhängigkeiten"
6. **Änderungstyp:** Dependency Correction
7. **Exakte Beschreibung:** „Version 0.7.0" (Data Pipeline) → „Version 0.7.1"; „Version 0.4.0" (Data Validation) → „Version 0.4.2"; „Version 0.4.0" (Indicator) → „Version 0.4.2".
8. **Begründung:** Alle drei zitierten Dokumente ändern sich in diesem Zyklus (Data Pipeline bereits zuvor auf 0.7.1, Data Validation und Indicator durch DV-1/IS-1 auf 0.4.2).
9. **Folgeänderungen:** Keine zusätzlichen.
10. **Validierung:** Grep-Prüfung der drei Zitatstellen.

#### Änderung ST-3

1. **Finding-ID:** `SCR7-MIN-03` (nur Signal-Transformation-Anteil; Indicator-Anteil verworfen, siehe Abschnitt 0)
2. **Datei:** `docs/specifications/RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md`
3. **Aktuelle Version:** — (inhaltliche Änderung, versionsseitig durch ST-1 abgedeckt)
4. **Neue Version:** —
5. **Paragraph:** §32 „Publication Gate"
6. **Änderungstyp:** Editorial Correction
7. **Exakte Beschreibung:** Neues Kriterium in die nummerierte Liste von §32 einfügen: „18. Property-Tests bestanden sind". Bestehende Liste (aktuell 17 Kriterien) bleibt inhaltlich unverändert; nur ein zusätzlicher Listenpunkt.
8. **Begründung:** `RCC_002_SCR_007_MINOR_FINDINGS_VERIFICATION_AND_CORRECTION_PLAN_2026-07-27.md` (Abschnitt 6, SCR7-MIN-03) bestätigt: Indicator §30 Kriterium 16 macht „Property-Tests bestanden" bereits zur Publication-Gate-Pflichtbedingung; Signal Transformation §32 besitzt kein analoges Kriterium, obwohl §29.10 dieselbe Testkategorie beschreibt. Diese Ergänzung schließt die Asymmetrie zwischen den beiden Geschwisterdokumenten, ohne neue Testinhalte einzuführen (die Eigenschaften aus §29.10 existieren bereits).
9. **Folgeänderungen:** Keine an anderen Dokumenten. (Eine Erweiterung der `PASS_WITH_APPROVED_EXCEPTIONS`-Ausnahmeliste um einen expliziten Ausschluss für fehlgeschlagene Property-Tests wurde in der Verifikation nur als Prüfpunkt für die Re-Review genannt, nicht als eigenständig bestätigte Änderung — daher nicht Teil dieses Plans; siehe Validierung.)
10. **Validierung:** Bestätigen, dass die bestehende Property-Test-Suite von Signal Transformation bereits alle in §29.10 genannten Eigenschaften abdeckt (keine neue Testimplementierung erforderlich); gezielte Prüfung, ob die `PASS_WITH_APPROVED_EXCEPTIONS`-Ausnahmeliste in §32 mit dem neuen Kriterium 18 konsistent ist.

---

### 2.5 `docs/specifications/RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md`

#### Änderung RG-1

1. **Finding-ID:** `SCR7-MAJ-03`
2. **Datei:** `docs/specifications/RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md`
3. **Aktuelle Version:** `0.5.0`
4. **Neue Version:** `0.5.1`
5. **Paragraph:** Dokumentmetadaten (Feld „Version")
6. **Änderungstyp:** Version Correction
7. **Exakte Beschreibung:** Feld „Version" von `0.5.0` auf `0.5.1` ändern.
8. **Begründung:** Neuer §5.8-Rückverweis-Satz in diesem Zyklus hinzugefügt; wie ST-1, bislang kein Versionsschritt im gesamten Korrekturzyklus.
9. **Folgeänderungen:** Label and Forward Return, Reproducibility zitieren Regime and Gate und müssen auf `0.5.1` aktualisiert werden.
10. **Validierung:** Sichtprüfung; Teil der globalen Bundle-/Manifest-Regeneration.

#### Änderung RG-2

1. **Finding-ID:** `SCR7-MAJ-03`
2. **Datei:** `docs/specifications/RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md`
3. **Aktuelle Version:** n/a (Fremdversionen)
4. **Neue Version:** n/a
5. **Paragraph:** Dokumentmetadaten, Zeilen „Übergeordnetes Dokument" und „Direkte Abhängigkeiten"
6. **Änderungstyp:** Dependency Correction
7. **Exakte Beschreibung:** „Version 0.7.0" (Data Pipeline) → „Version 0.7.1"; „Version 0.4.0" (Data Validation) → „Version 0.4.2"; „Version 0.4.0" (Indicator) → „Version 0.4.2"; „Version 0.4.0" (Signal Transformation) → „Version 0.4.1".
8. **Begründung:** Alle vier zitierten Dokumente ändern sich in diesem Zyklus (siehe DV-1, IS-1, ST-1).
9. **Folgeänderungen:** Keine zusätzlichen.
10. **Validierung:** Grep-Prüfung der vier Zitatstellen.

---

### 2.6 `docs/specifications/RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md`

#### Änderung LF-1

1. **Finding-ID:** `SCR7-MAJ-03`
2. **Datei:** `docs/specifications/RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md`
3. **Aktuelle Version:** `0.4.0`
4. **Neue Version:** `0.4.1`
5. **Paragraph:** Dokumentmetadaten (Feld „Version")
6. **Änderungstyp:** Version Correction
7. **Exakte Beschreibung:** Feld „Version" von `0.4.0` auf `0.4.1` ändern.
8. **Begründung:** Neuer §5.8-Rückverweis-Satz **und** die Wortlautkorrektur in §17.4 (LF-3) fallen in diesen Zyklus; beide sind einzeln bereits Patch-pflichtig nach Data Pipeline §6.4 („redaktionelle... Metadatenkorrektur"); zusammen bleiben sie Patch-Klasse, da §17.4 keine tatsächliche Verhaltensänderung bewirkt (§18.3 bestimmt bereits das tatsächlich geforderte Verhalten).
9. **Folgeänderungen:** Reproducibility zitiert Label and Forward Return und muss auf `0.4.1` aktualisiert werden.
10. **Validierung:** Sichtprüfung; Teil der globalen Bundle-/Manifest-Regeneration.

#### Änderung LF-2

1. **Finding-ID:** `SCR7-MAJ-03`
2. **Datei:** `docs/specifications/RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md`
3. **Aktuelle Version:** n/a (Fremdversionen)
4. **Neue Version:** n/a
5. **Paragraph:** Dokumentmetadaten, Zeilen „Übergeordnetes Dokument" und „Direkte Abhängigkeiten"
6. **Änderungstyp:** Dependency Correction
7. **Exakte Beschreibung:** „Version 0.7.0" (Data Pipeline) → „Version 0.7.1"; „Version 0.4.0" (Data Validation) → „Version 0.4.2"; „Version 0.4.0" (Indicator) → „Version 0.4.2"; „Version 0.4.0" (Signal Transformation) → „Version 0.4.1"; „Version 0.5.0" (Regime and Gate) → „Version 0.5.1".
8. **Begründung:** Alle fünf zitierten Dokumente ändern sich in diesem Zyklus (siehe DV-1, IS-1, ST-1, RG-1).
9. **Folgeänderungen:** Keine zusätzlichen.
10. **Validierung:** Grep-Prüfung der fünf Zitatstellen.

#### Änderung LF-3

1. **Finding-ID:** `SCR7-MIN-02`
2. **Datei:** `docs/specifications/RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md`
3. **Aktuelle Version:** — (versionsseitig durch LF-1 abgedeckt)
4. **Neue Version:** —
5. **Paragraph:** §17.4 „Tail"
6. **Änderungstyp:** Terminology Correction
7. **Exakte Beschreibung:** Letzten Satz von §17.4 — aktuell: „Sie werden nicht mit null aufgefüllt und nicht entfernt." — ersetzen durch: „Diese Zeilen werden nicht entfernt und nicht durch synthetische Ersatzzeilen ersetzt; die betroffenen Feldwerte folgen der Nullsemantik aus §18.3." Kein weiterer Satz in §17.4 wird verändert.
8. **Begründung:** `RCC_002_SCR_007_MINOR_FINDINGS_VERIFICATION_AND_CORRECTION_PLAN_2026-07-27.md` (Abschnitt 6, SCR7-MIN-02) bestätigt einen echten Wortlautkonflikt: §17.4 „nicht mit null aufgefüllt" liest sich isoliert widersprüchlich zu §18.3 „alle numerischen Felder ... sind null" für denselben Tail-Zeilen-Fall. §18.3 ist die maßgebliche, dediziert benannte Nullsemantik-Sektion und bestimmt das tatsächlich geforderte Verhalten; die Neuformulierung entfernt die Mehrdeutigkeit, ohne das geforderte Verhalten zu ändern.
9. **Folgeänderungen:** Keine an anderen Dokumenten.
10. **Validierung:** Gemeinsame Lektüre von §17.4 und §18.3 nach der Änderung zur Bestätigung, dass beide Abschnitte widerspruchsfrei zusammen gelesen werden können; Bestätigung, dass kein bestehender Test oder nachgelagerter Text auf dem alten Wortlaut beruht (bereits in der Vorverifikation geprüft, kein solcher Bezug gefunden).

---

### 2.7 `docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md`

#### Änderung RM-1

1. **Finding-ID:** `SCR7-MAJ-03`
2. **Datei:** `docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md`
3. **Aktuelle Version:** `0.6.0`
4. **Neue Version:** `0.7.0`
5. **Paragraph:** Dokumentmetadaten (Feld „Version")
6. **Änderungstyp:** Version Correction
7. **Exakte Beschreibung:** Feld „Version" von `0.6.0` auf `0.7.0` ändern.
8. **Begründung:** Dieses Dokument erhielt in diesem Zyklus eine neue MUST-Invariante (§8.7.1, `S8_rows = S7_rows`) und ein neues verpflichtendes Testerfordernis (§18.4) — nach Data Pipeline §6.4 „Minor: additive optionale Felder ohne Änderung bestehender Semantik" ist dies mindestens Minor-pflichtig, da echter neuer normativer Inhalt (nicht nur redaktionell) hinzugefügt wurde, ohne bestehende Semantik zu entfernen, umzubenennen oder ihre Bedeutung zu ändern (kein Major-Kriterium erfüllt). Bestätigt in `RCC_002_SCR_007_MAJOR_FINDINGS_VERIFICATION_2026-07-27.md`, Abschnitt 7.
9. **Folgeänderungen:** Kein bekanntes abhängiges Dokument zitiert Reproducibility als Abhängigkeit.
10. **Validierung:** Sichtprüfung; Teil der globalen Bundle-/Manifest-Regeneration.

#### Änderung RM-2

1. **Finding-ID:** `SCR7-MAJ-03`
2. **Datei:** `docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md`
3. **Aktuelle Version:** n/a (Fremdversionen)
4. **Neue Version:** n/a
5. **Paragraph:** Dokumentmetadaten, Zeilen „Primäre Abhängigkeit" und „Fachliche Abhängigkeiten"
6. **Änderungstyp:** Dependency Correction
7. **Exakte Beschreibung:** „Primäre Abhängigkeit | ... Version 0.7.0" → „... Version 0.7.1"; „Fachliche Abhängigkeiten" — „Version 0.4.0" (Data Validation) → „0.4.2"; „Version 0.4.0" (Indicator) → „0.4.2"; „Version 0.4.0" (Signal Transformation) → „0.4.1"; „Version 0.5.0" (Regime and Gate) → „0.5.1"; „Version 0.4.0" (Label and Forward Return) → „0.4.1".
8. **Begründung:** Alle sechs zitierten Dokumente ändern sich in diesem Zyklus (Data Pipeline bereits zuvor auf 0.7.1; die übrigen fünf durch DV-1, IS-1, ST-1, RG-1, LF-1).
9. **Folgeänderungen:** Keine zusätzlichen.
10. **Validierung:** Grep-Prüfung der sechs Zitatstellen.

#### Änderung RM-3

1. **Finding-ID:** `SCR7-MAJ-02`
2. **Datei:** `docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md`
3. **Aktuelle Version:** n/a (betrifft Tabelle, nicht die Dokumentversion selbst)
4. **Neue Version:** n/a
5. **Paragraph:** §12.3 „Spezifikationsprofil"
6. **Änderungstyp:** Dependency Correction
7. **Exakte Beschreibung:** Tabelle vollständig ersetzen durch:
   ```
   | Dokument-ID | Version |
   |---|---:|
   | `RCC_002_DATA_PIPELINE_SPECIFICATION` | `0.7.1` |
   | `RCC-002-DV` | `0.4.2` |
   | `RCC-002-IS` | `0.4.2` |
   | `RCC-002-ST` | `0.4.1` |
   | `RCC-002-RG` | `0.5.1` |
   | `RCC-002-LF` | `0.4.1` |
   | `RCC-002-RM` | `0.7.0` |
   ```
8. **Begründung:** `RCC_002_SCR_007_MAJOR_FINDINGS_VERIFICATION_2026-07-27.md` (Abschnitt 6) bestätigt: die Tabelle ist gegenüber allen sieben tatsächlichen Dokumentversionen um ein bis zwei Generationen veraltet und widerspricht zusätzlich der eigenen Kopfzeilen-Version des Dokuments (`0.5.0` in der Tabelle gegenüber `0.6.0`/neu `0.7.0` in Kopfzeile/§29). Die Tabelle steht unter einer MUST-Formulierung („MUSS mindestens folgende Dokumente referenzieren") und muss daher korrekt sein.
9. **Folgeänderungen:** Keine zusätzlichen (Werte sind bereits mit RM-1/RM-2 sowie DV-1/IS-1/ST-1/RG-1/LF-1 konsistent).
10. **Validierung:** Abgleich der neuen Tabelle gegen die tatsächlichen Kopfzeilen-Versionsfelder aller sieben Dokumente nach Abschluss aller Änderungen dieses Plans; Bestätigung, dass die `RCC-002-RM`-Zeile mit der eigenen, neuen Kopfzeilen-Version (`0.7.0`, siehe RM-1) übereinstimmt.

#### Änderung RM-4

1. **Finding-ID:** `SCR7-MAJ-03`
2. **Datei:** `docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md`
3. **Aktuelle Version:** —
4. **Neue Version:** —
5. **Paragraph:** §29 „Schlussbestimmung", Abschnitt „Sie aktualisiert die Spezifikationsabhängigkeiten auf"
6. **Änderungstyp:** Dependency Correction
7. **Exakte Beschreibung:** Die dort aufgeführte Liste der sechs Abhängigkeitsversionen (aktuell: Data Pipeline 0.7.0; Data Validation 0.4.0; Indicator 0.4.0; Signal Transformation 0.4.0; Regime and Gate 0.5.0; Label and Forward Return — in der Liste selbst zuletzt unvollständig geführt) durch dieselben sechs Zielwerte wie in RM-2 ersetzen (0.7.1 / 0.4.2 / 0.4.2 / 0.4.1 / 0.5.1 / 0.4.1).
8. **Begründung:** §29 führt dieselbe Abhängigkeitsliste wie die Kopfzeile in Prosaform separat; beide Stellen müssen nach Anwendung von RM-2 konsistent bleiben.
9. **Folgeänderungen:** Keine zusätzlichen.
10. **Validierung:** Abgleich §29-Liste gegen Kopfzeile (RM-2) nach Änderung.

#### Änderung RM-5

1. **Finding-ID:** `SCR7-MIN-07`
2. **Datei:** `docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md`
3. **Aktuelle Version:** —
4. **Neue Version:** —
5. **Paragraph:** Dokumentmetadaten (Feld „Status"); §29 „Der aktuelle Status lautet" und „Nächste vorgeschriebene Schritte"
6. **Änderungstyp:** Editorial Correction
7. **Exakte Beschreibung:** Feld „Status" — aktuell „SCR-005-Corrected Draft – Scientific Consistency Re-Review 006 Pending" — sowie die wortgleiche Formulierung in §29 durch eine den tatsächlichen Governance-Stand widerspiegelnde Formulierung ersetzen (z. B. Verweis auf C1-Korrektur abgeschlossen, RCC-002-SCR-007 Full-Scope-Review durchgeführt, Major-/Minor-Findings-Verifikation abgeschlossen, Editorial Pass/Internal Certification ausstehend); die „Nächste vorgeschriebene Schritte"-Liste in §29, die `RCC-002-SCR-006` als noch ausstehenden Schritt nennt, entsprechend aktualisieren, da SCR-006 durch SCR-007 in seiner wissenschaftlichen Vertrauensfunktion ersetzt wurde.
8. **Begründung:** `RCC_002_SCR_007_MINOR_FINDINGS_VERIFICATION_AND_CORRECTION_PLAN_2026-07-27.md` (Abschnitt 6, SCR7-MIN-07) bestätigt: Status-Feld und §29 beschreiben einen Governance-Stand vor C1/AIR-003, obwohl der normative Textkörper desselben Dokuments bereits post-AIR-003-Inhalte (§8.7.1 etc.) enthält — ein interner Selbstwiderspruch über den eigenen Bearbeitungsstand.
9. **Folgeänderungen:** Keine an anderen Dokumenten (dies betrifft ausschließlich Reproducibilitys eigene Selbstbeschreibung).
10. **Validierung:** Interne Konsistenzprüfung, dass Status-Feld, §29-Statustext und der tatsächliche normative Inhalt des Dokuments (inklusive der in diesem Plan vorgesehenen Änderungen) übereinstimmen.

#### Änderung RM-6

1. **Finding-ID:** `SCR7-MIN-08`
2. **Datei:** `docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md`
3. **Aktuelle Version:** —
4. **Neue Version:** —
5. **Paragraph:** §25 „Veröffentlichungs-Gate"
6. **Änderungstyp:** Cross Reference Correction
7. **Exakte Beschreibung:** Neuen Checklistenpunkt in §25 einfügen, unmittelbar nach dem bestehenden Punkt „S7-Horizon- und Feldnamensraum eindeutig nachgewiesen": „- [ ] S7→S8-Row-Preservation-Reconciliation (§18.4) bestanden". Kein bestehender Checklistenpunkt wird verändert oder entfernt.
8. **Begründung:** `RCC_002_SCR_007_MINOR_FINDINGS_VERIFICATION_AND_CORRECTION_PLAN_2026-07-27.md` (Abschnitt 6, SCR7-MIN-08) bestätigt: §25 benennt explizite Vertragsnachweise für S2, S5/S6 und S7, aber keinen analogen expliziten Punkt für die S7→S8-Grenze, obwohl §18.4 im selben Dokument bereits einen konkreten, falsifizierbaren Test dafür definiert. Der neue Punkt verweist lediglich auf den bereits bestehenden Test; es wird kein neuer Test eingeführt.
9. **Folgeänderungen:** Keine an anderen Dokumenten.
10. **Validierung:** Bestätigung, dass §18.4 unverändert bleibt und der neue Checklistenpunkt exakt auf dessen fünf bestehende Prüfprädikate verweist, ohne deren Inhalt zu verändern.

---

## 3. Dateigruppierung

| Datei | Anzahl Änderungen | Versionsänderung | Änderungsarten | Notwendige Validierung |
|---|---:|---|---|---|
| Data Pipeline | 0 | `0.7.1` (unverändert) | — | Keine (unverändert) |
| Data Validation | 2 | `0.4.1` → `0.4.2` | Version Correction (1), Dependency Correction (1) | Grep-Abgleich Zitatstelle; Bundle-/Manifest-Regeneration |
| Indicator | 2 | `0.4.1` → `0.4.2` | Version Correction (1), Dependency Correction (1) | Grep-Abgleich zweier Zitatstellen; Bundle-/Manifest-Regeneration |
| Signal Transformation | 3 | `0.4.0` → `0.4.1` | Version Correction (1), Dependency Correction (1), Editorial Correction (1) | Grep-Abgleich dreier Zitatstellen; Bestätigung bestehender Property-Test-Abdeckung; Bundle-/Manifest-Regeneration |
| Regime and Gate | 2 | `0.5.0` → `0.5.1` | Version Correction (1), Dependency Correction (1) | Grep-Abgleich vierer Zitatstellen; Bundle-/Manifest-Regeneration |
| Label and Forward Return | 3 | `0.4.0` → `0.4.1` | Version Correction (1), Dependency Correction (1), Terminology Correction (1) | Grep-Abgleich fünf Zitatstellen; gemeinsame Lektüre §17.4/§18.3; Bundle-/Manifest-Regeneration |
| Reproducibility and Manifest | 6 | `0.6.0` → `0.7.0` | Version Correction (1), Dependency Correction (3: Kopfzeile, §12.3, §29-Liste), Editorial Correction (1: Status/§29), Cross Reference Correction (1: §25) | Grep-Abgleich sechs Kopfzeilen-Zitatstellen plus §12.3/§29-Konsistenz; interne Selbstkonsistenzprüfung; Bundle-/Manifest-Regeneration |
| **Summe** | **18** | — | — | — |

---

## 4. Globale Validierung — vollständiger Ablauf

1. **Spezifikationen ändern** — die 18 Änderungen aus Abschnitt 2 in den sechs betroffenen Dateien unter `docs/specifications/` anwenden; `RCC_002_DATA_PIPELINE_SPECIFICATION` bleibt unangetastet.
2. **Interne Konsistenzprüfung** — für jedes geänderte Dokument: Kopfzeilen-Version gegen alle sechs (bzw. für Reproducibility: alle drei) internen Vorkommen dieser Version abgleichen (Abschnitt 2, Feld „Validierung" je Änderung); anschließend eine dokumentübergreifende Grep-Prüfung, dass keine der sechs alten Versionszeichenketten (`0.7.0`, `0.4.0` [Data Validation], `0.4.0` [Indicator], `0.4.0` [Signal Transformation], `0.5.0` [Regime and Gate], `0.4.0` [Label]) an einer Zitatstelle in irgendeinem der sieben Dokumente mehr vorkommt.
3. **Bundle erzeugen** — `scripts/build_rcc002_spec_bundle.py` gegen die sieben (sechs geänderten plus ein unveränderten) Quelldateien ausführen, neues Bundle erzeugen.
4. **Manifest erzeugen** — neues Manifest mit den aktualisierten Zeilen-, Byte- und SHA-256-Werten für alle sieben eingebetteten Dokumente sowie der neuen Bundle-Gesamtidentität erstellen.
5. **Hashprüfung** — SHA-256, Zeilen- und Bytezahl von Bundle und Manifest unabhängig neu berechnen und mit den im Manifest behaupteten Werten abgleichen.
6. **Round-trip** — Generator erneut gegen die Quelldateien in ein temporäres Verzeichnis ausführen; bytegenauen Abgleich mit dem neuen Bundle bestätigen; temporäre Datei löschen.
7. **`git diff --check`** — auf alle sieben geänderten/unveränderten Spezifikationsdateien sowie das neue Bundle/Manifest anwenden.
8. **SCR-008** — neuer, fokussierter Scientific Consistency Review, beschränkt auf die sechs tatsächlich geänderten Dokumente und die drei in Abschnitt 2 genannten inhaltlichen Einzeländerungen (LF-3, ST-3, RM-6) sowie die Versions-/Abhängigkeitskonsistenz (kein neuer Full-Scope-Review der gesamten Familie erforderlich, da keine weiteren Inhalte betroffen sind).
9. **AIR-004** — die weiterhin ausstehende, unabhängig erforderliche Full-Scope-Replacement Architecture Integrity Review (siehe `RCC_002_PRE_CERTIFICATION_STATUS_2026-07-27.md`), unverändert durch diesen Plan.
10. **Internal Certification** — erst nach bestandenem SCR-008 und AIR-004.
11. **Release** — erst nach Internal Certification, gemäß bestehendem Freigabeprozess.

---

## 5. Änderungsstatistik

| Kennzahl | Wert |
|---|---|
| Bestätigte Minor Findings | 6 (`SCR7-MIN-02`, `SCR7-MIN-03`/Signal-Transformation, `SCR7-MIN-07`, `SCR7-MIN-08`, `SCR7-MAJ-02`, `SCR7-MAJ-03`) |
| Tatsächlich umzusetzende Änderungen | 18 |
| Änderungen je Dokument | Data Pipeline: 0; Data Validation: 2; Indicator: 2; Signal Transformation: 3; Regime and Gate: 2; Label and Forward Return: 3; Reproducibility: 6 |
| Dokumente ohne Änderungen | Data Pipeline (`RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`) |
| Versionsübersicht alt → neu | Data Pipeline `0.7.1` (unverändert); Data Validation `0.4.1`→`0.4.2`; Indicator `0.4.1`→`0.4.2`; Signal Transformation `0.4.0`→`0.4.1`; Regime and Gate `0.5.0`→`0.5.1`; Label and Forward Return `0.4.0`→`0.4.1`; Reproducibility `0.6.0`→`0.7.0` |
| Ausschließlich redaktionelle Änderungen? | Überwiegend ja (Version-/Dependency-/Terminology-/Editorial-Korrekturen ohne Verhaltensänderung); zwei Änderungen (ST-3, RM-6) haben einen bestätigten, eng begrenzten normativen Effekt |
| Neue normative Inhalte? | Begrenzt ja: ST-3 erhebt eine bereits bestehende, bisher nur SHOULD-getestete Eigenschaftsgruppe zu einer benannten Publication-Gate-Pflichtbedingung (keine neue Testmethodik); RM-6 verweist auf einen bereits bestehenden Test (§18.4) in einer Checkliste, ohne neuen Test zu definieren. Kein neues Invariant, kein neuer Wahrheitswert, keine neue Architekturregel. |
| Architekturänderungen? | Nein |
| Erwartete Bundleänderung | Ja — sechs von sieben eingebetteten Dokumenten ändern Zeilen-/Byte-/Hashwert; Bundle-Gesamtzeilen-/Byte-/Hashwert ändert sich entsprechend |
| Erwartete Manifeständerung | Ja — alle sechs geänderten Per-Datei-Einträge sowie die Bundle-Gesamtidentität müssen im Manifest neu geführt werden |

---

## 6. Plausibilitätsprüfung

| Prüfpunkt | Ergebnis |
|---|---|
| Keine verworfenen Findings übernommen? | Bestätigt — `SCR7-MIN-01`, `SCR7-MIN-03`/Indicator-Anteil, `SCR7-MIN-04`, `SCR7-MIN-05`, `SCR7-MIN-06` sind explizit ausgeschlossen (Abschnitt 0); keiner erscheint in Abschnitt 2. |
| Keine Observation als Pflichtkorrektur? | Bestätigt — alle in Abschnitt 2 gelisteten 18 Änderungen stammen ausschließlich aus den sechs als `CONFIRMED` (bzw. für `SCR7-MIN-03`/`SCR7-MIN-08` als im Signal-Transformation-/Reproducibility-Anteil `CONFIRMED`/`PARTIALLY CONFIRMED`) eingestuften Findings; keine als `Observation` oder `Future Architecture Risk` klassifizierte Feststellung wurde in den Änderungsumfang aufgenommen. |
| Keine doppelte Änderung? | Bestätigt — jede Zitatstellen-Korrektur wird genau einmal pro Dokument geplant; die §12.3-Tabellenkorrektur (RM-3) und die Kopfzeilen-/§29-Korrekturen (RM-2/RM-4) betreffen unterschiedliche Textstellen mit denselben Zielwerten, nicht denselben Text zweimal. |
| Keine unnötige Versionsanhebung? | Bestätigt — Data Pipeline erhält keine Versionsanhebung (kein Inhalt geändert); jede der sechs übrigen Anhebungen ist einzeln, dokumentbezogen begründet (Abschnitt 2, Feld 8), nicht pauschal. |
| Keine unbegründete Architekturänderung? | Bestätigt — keine der 18 Änderungen führt eine neue Architekturregel, ein neues Invariant, eine neue Priorität oder eine neue Spezifikation ein; ST-3 und RM-6 verweisen ausschließlich auf bereits bestehende, bereits normierte Tests. |
| Keine Änderung an Data Pipeline? | Bestätigt — Abschnitt 2.1: keine Änderung. |

---

## 7. Terminal-Bestätigung dieses Plans

Dieser Plan selbst wurde **nicht ausgeführt**. Es wurde keine Spezifikation, kein Bundle und kein Manifest geändert oder erzeugt. Es wurde kein Commit erstellt. Ausschließlich diese Plandatei wurde neu angelegt.

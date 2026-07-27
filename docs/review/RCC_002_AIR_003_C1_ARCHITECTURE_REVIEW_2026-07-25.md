# RCC-002 AIR-003 — Architecture Integrity Review der C1-Korrektur

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Fokussierter Architecture Integrity Review |
| Dokument-ID | `RCC-002-AIR-003` |
| Titel | Architecture Integrity Review — RCC-002 C1-Korrektur |
| Version | 1.0.0 |
| Datum | 2026-07-25 |
| Status | Abgeschlossen — Urteil: PASS WITH MINOR CORRECTIONS |
| Prüfgegenstand | `docs/review/RCC_002_C1_CORRECTED_FULL_SPEC_BUNDLE_2026-07-25.md` |
| Geprüfte Zusatzartefakte | `RCC_002_C1_VERIFICATION_RECORD_2026-07-25.md`; `RCC_002_C1_IMPACT_ANALYSIS_2026-07-25.md`; `RCC_002_C1_SCIENTIFIC_CONSISTENCY_REVIEW_2026-07-25.md`; `RCC_002_C2_REVIEW_LINEAGE_INVESTIGATION_2026-07-25.md`; `RCC_002_C1_CORRECTED_BUNDLE_MANIFEST_2026-07-25.md`; `scripts/build_rcc002_spec_bundle.py` |
| Vorgängerreview | `RCC-002-C1-SCR` (bestanden mit Minor Findings, 2026-07-25) |
| Speicherort im Repository | `docs/review/RCC_002_AIR_003_C1_ARCHITECTURE_REVIEW_2026-07-25.md` |
| Dateiname | `RCC_002_AIR_003_C1_ARCHITECTURE_REVIEW_2026-07-25.md` |
| Referenziert durch | Editorial Pass (gesperrt bis Klärung von C2, siehe Abschnitt 9) |
| Unabhängigkeit | Durchgeführt von derselben Ausführungsinstanz, die C1 implementiert und den vorausgehenden Scientific Consistency Review durchgeführt hat. Methodik: aktive Suche nach Gegenbeispielen (Prüfbereich D) statt Bestätigung der Vorbefunde; jede Aussage ist an eine Zitatstelle oder einen ausgeführten Befehl gebunden. |

Es wurden **keine Dateien verändert und kein Commit erstellt**, mit
Ausnahme dieses Berichts selbst.

---

## 1. Urteil

```text
PASS WITH MINOR CORRECTIONS
```

Die Row-Preservation-Architektur ist für S2 bis S7 vollständig, konsistent
und mit expliziten Invarianten sowie Tests abgesichert — hier wurde aktiv
nach Gegenbeispielen gesucht und keines gefunden. Es besteht jedoch ein
neuer, bisher nicht berichteter **Major Finding**: die S7→S8-Grenze
(Label → Reproducibility/Export) besitzt keine explizite
Row-Preservation-Invariante und keinen entsprechenden Test, obwohl jede
andere Stufengrenze (S3 bis S7) diese durchgängig führt. Ein **Minor
Finding** betrifft die fehlende Rückverweisung der sechs unveränderten
Dokumente auf die neue Data-Pipeline-§5.8. Kein Critical Finding.

---

## 2. Critical Findings

Keine. Innerhalb der geprüften Kette S2→S3→S4→S5→S6→S7 wurde aktiv nach
Widersprüchen zur Row-Preservation-Architektur gesucht (Prüfbereich B, D)
und keiner gefunden.

---

## 3. Major Findings

### AIR3-M1 — Keine explizite Row-Preservation-Invariante an der S7→S8-Grenze

**Befund:** Für jede Stufengrenze von S3 bis S7 existiert eine explizite,
wörtlich genannte Zeilenzahl-Invariante mit zugehörigem Testerfordernis:

| Grenze | Invariante | Fundstelle |
|---|---|---|
| S2→S3 | `S3_rows = S2_rows` | Indicator §26.2, §27.7, §30 |
| S3→S4 | `S4_rows = S3_rows` | Signal Transformation §28.2 |
| S4→S5 | `S5_rows = S4_rows` | Regime and Gate §30 |
| S5→S6 | `S6_rows = S5_rows` | Regime and Gate §30 |
| S6→S7 | `S7_rows = S6_rows` | Label and Forward Return §22 |
| **S7→S8** | **keine gefunden** | — |

`RCC_002_DATA_PIPELINE_SPECIFICATION` §7.9 definiert S8 ausschließlich als
positive Feld-Allowlist („Jede View ist eine positive, fail-closed
Feld-Allowlist“) ohne jede Erwähnung einer Zeilenfilterung — das spricht
inhaltlich für Row Preservation auch an dieser Grenze. Auch das neue
§5.8-Prinzip ist als allgemeiner, stufenübergreifender Grundsatz formuliert
(„über alle nachgelagerten Stufen hinweg“) und deckt S8 damit dem Wortlaut
nach ab. Es fehlt jedoch:

- eine explizite `S8_rows = S7_rows`-artige Aussage in
  `RCC_002_DATA_PIPELINE_SPECIFICATION` §7.9 oder
  `RCC_002_REPRODUCIBILITY_AND_MANIFEST` §7–§8;
- ein entsprechendes Testerfordernis (die übrigen Grenzen fordern jeweils
  explizit einen Reconciliation-Test; für S8-Views ist ein solcher Test
  nirgends verlangt);
- eine explizite Aussage im generischen Publication-Gate-Katalog
  (`RCC_002_DATA_PIPELINE_SPECIFICATION` §12), der zwar „Zeilenzahl­verän­
  derungen vollständig erklärt“ als Kriterium 3 führt, dies aber allgemein
  für den gesamten Datenbuild formuliert, nicht spezifisch für S8-Views
  gegenüber S7.

`RCC_002_REPRODUCIBILITY_AND_MANIFEST` §7.3 definiert `Zeilenanzahl` zwar
als Bestandteil des semantischen Fingerprints jedes Artefakts — das ist
ein **Erkennungsmechanismus** für Abweichungen, keine **Vorgabe**, dass die
S8-Zeilenzahl mit S7 übereinstimmen muss.

**Warum das relevant ist:** Dies ist exakt dieselbe Kategorie von Lücke,
die zu Finding C1 geführt hat — eine implizit angenommene, aber nirgends
explizit normierte Row-Preservation-Eigenschaft an genau der Stelle, an
der der Begriff „kanonisch veröffentlicht“ (Publication) zum zweiten Mal
im Paket eine zentrale Rolle spielt. Eine künftige Änderung an §7.9 oder
an der Reproducibility-Spezifikation könnte hier unbemerkt denselben Fehler
wiederholen, den C1 gerade an der S2/S3-Publication-Gate-Formulierung
korrigiert hat.

**Empfehlung (nicht selbst umgesetzt):** `S8_rows = S7_rows` (je View,
unter Berücksichtigung, dass Label-Research und Audit zusätzlich S7-Felder
führen, aber keine Zeilen filtern) explizit in
`RCC_002_DATA_PIPELINE_SPECIFICATION` §7.9 aufnehmen und ein
entsprechendes Reconciliation-Testerfordernis in
`RCC_002_REPRODUCIBILITY_AND_MANIFEST` ergänzen.

---

## 4. Minor Findings

### AIR3-m1 — §5.8 wird von keinem der sechs übrigen Dokumente referenziert

Geprüft: alle sechs nachgeordneten Spezifikationen wurden nach „5.8“,
„Row-Preservation-Prinzip“ und „Row Preservation Prinzip“ durchsucht. Es
wurden ausschließlich zwei zufällige Nummerierungskollisionen gefunden
(„5.8 Profilversionen“ in Regime and Gate, „5.8 Dataset Artifact Set ID“
in Reproducibility) — keine inhaltliche Rückverweisung. Die inhaltliche
Konsistenz der sechs Dokumente mit §5.8 ist dennoch vollständig gegeben
(siehe `RCC_002_C1_SCIENTIFIC_CONSISTENCY_REVIEW_2026-07-25.md`, Prüfung
C). Das Fehlen einer expliziten Rückverweisung ist ein reines
Wartbarkeitsrisiko (siehe Abschnitt 7), keine aktuelle Inkonsistenz.

### AIR3-m2 — Generischer Publication-Gate-Katalog (§12) bleibt auf Stufenebene, nicht View-Ebene

`RCC_002_DATA_PIPELINE_SPECIFICATION` §12 formuliert „Jede Stufe besitzt
ein eigenes Publication Gate“ und listet S0 bis S7 implizit über die
einzelnen Fachspezifikationen ab (die jeweils ein eigenes „Publication
Gate“-Kapitel führen: Data Validation §20, Indicator §30, Signal
Transformation §32, Regime and Gate §35/§36, Label §38). Für S8 existiert
kein analoges, eigenständiges Kapitel „Publication Gate“ in irgendeinem
Dokument — S8-Kriterien sind ausschließlich verstreut in
`RCC_002_DATA_PIPELINE_SPECIFICATION` §12 (Punkte 8–10) und
`RCC_002_REPRODUCIBILITY_AND_MANIFEST` §25 „Veröffentlichungs-Gate“
(datensatzweit, nicht view-spezifisch) enthalten. Dies ist mit AIR3-M1
verwandt, aber eigenständig: selbst wenn AIR3-M1 behoben wird, bliebe S8
die einzige Stufe ohne dediziertes Publication-Gate-Kapitel.

---

## 5. Positive Findings

- **Prüfbereich B (Stage Contracts):** An jeder der fünf explizit
  angefragten Grenzen (S2→S3, S3→S4, S4→S5, S6→S7 [„Regime→Label“, da
  Regime and Gate S5 und S6 in einem Dokument führt], S7→S8) ist
  eindeutig definiert, welche Felder übernommen werden (vollständig,
  unverändert, in fixierter Spaltenreihenfolge), welche Felder neu
  entstehen dürfen (nur die jeweils registrierten Stufenerweiterungen)
  und welche Invarianten gelten. Für S2 bis S7 ist dies zusätzlich durch
  eine explizite Zeilenzahl-Gleichung abgesichert (siehe Tabelle in
  AIR3-M1).
- **Prüfbereich D (Negative Tests):** Aktiv gesucht und **nicht
  gefunden**: ein Fall, in dem `quality_gate_pass=false`,
  `BLOCK_BOTH`, Artefakt-Quarantäne oder vollständiger Build-Abbruch zu
  einer Zeilenlöschung führen würde. Insbesondere wurde geprüft, ob eine
  „komplett ungültige Zeile“ (alle abgeleiteten Felder ungültig)
  einen Sonderfall darstellt: Primärschlüssel- und OHLCV-Pflichtfelder
  sind durch die S2-Härte-Invarianten (CRITICAL bei Verletzung, Abbruch
  oder Quarantäne auf Artefaktebene) bereits vor S3 abgesichert, sodass
  eine Zeile mit gültigem Schlüssel aber vollständig ungültigen
  abgeleiteten Feldern architektonisch möglich, aber nicht
  widersprüchlich behandelt ist — sie bleibt mit `x=null` für alle
  betroffenen Felder im Datenstrom.
- **Prüfbereich A (Architekturprinzipien):** Keine versteckten
  Widersprüche zwischen Row Preservation, Fail-Closed-Verhalten,
  Build-Abbruch und Artefakt-Quarantäne gefunden. Die in §5.8 explizit
  formulierte Trennung („Beide wirken auf das gesamte Artefakt oder den
  gesamten Build, nicht auf einzelne Zeilen“) ist mit jeder untersuchten
  Einzelstelle (`Stage-Abbruch` ausschließlich bei strukturellen
  Fehlern; `Quarantäne` ausschließlich artefakt-/build-bezogen)
  widerspruchsfrei.
- **Prüfbereich C (Architektur-Invarianten):** Determinismus,
  Build-Reproduzierbarkeit und Manifest-Reproduzierbarkeit sind für S2
  bis S7 durchgängig mit Zeilenzahl-, Row-Identity- und
  Row-Order-Garantien unterlegt; keine indirekten Konflikte zwischen
  diesen Invarianten und der C1-Korrektur gefunden.
- Die vier unveränderten Dokumente (Signal Transformation, Regime and
  Gate, Label and Forward Return, Reproducibility and Manifest) sind seit
  der ersten C1-Fassung nachweislich byte-identisch geblieben
  (unabhängig für diesen Review erneut per Hash-Vergleich bestätigt).

---

## 6. Bewertung der Architektur

Die Row-Preservation-Architektur ist für den Kernpfad S2 bis S7 —
denjenigen Teil der Pipeline, in dem die ursprüngliche C1-Inkonsistenz
tatsächlich auftrat — vollständig, in sich geschlossen und durch
mehrschichtige, redundante Mechanismen abgesichert (Zeilenzahl-Gleichungen,
Segment-IDs, feldbezogene Validitätsflags, `BLOCK_BOTH`-Wahrheitstabelle).
Die Architektur bricht nicht an der Stelle, an der die C1-Korrektur
angesetzt hat. Sie ist jedoch an der S8-Grenze **unvollständig
spezifiziert**, nicht **widersprüchlich** — ein wichtiger Unterschied, der
die Einstufung als Major (nicht Critical) begründet.

## 7. Bewertung der Wartbarkeit

Die Dokumentstruktur trennt globale Prinzipien (Data Pipeline §5) von
lokalen Stufenregeln grundsätzlich sauber, und §5.8 fügt sich in Form und
Sprache nahtlos in die bestehenden §5.1–§5.7 ein (siehe
`RCC_002_C1_SCIENTIFIC_CONSISTENCY_REVIEW_2026-07-25.md`, Prüfung B).
Das Wartbarkeitsrisiko liegt nicht in der Formulierung selbst, sondern
darin, dass die sechs nachgeordneten Dokumente ihre jeweiligen
`Sn_rows = Sn-1_rows`-Invarianten weiterhin unabhängig und ohne
Rückverweis auf §5.8 führen (AIR3-m1). Das Muster „ein Prinzip, mehrfach
unabhängig lokal repliziert, ohne zentrale Rückverweisung“ ist genau das
Muster, das C1 ursprünglich hat auseinanderdriften lassen.

## 8. Bewertung der Erweiterbarkeit

Neue Horizonte, Assets oder Profile (gemäß den jeweiligen
„Erweiterung“-Abschnitten der Einzeldokumente) lösen laut Spezifikation
durchgängig einen erneuten Review-Zyklus aus, wenn sie fachliche Semantik,
Schemas oder Identitätsvorabbildungen berühren. Die C1-Korrektur selbst
fügt keine neue Erweiterungsachse hinzu und beeinträchtigt diesen
Mechanismus nicht. Der unter AIR3-M1 benannte Lückentyp würde sich bei
einer künftigen achten Pipeline-Stufe oder einem neuen S8-View
voraussichtlich wiederholen, sofern die Empfehlung aus Abschnitt 3 nicht
umgesetzt wird.

## 9. Bewertung der C2-Auswirkung

**Beobachtung:** Finding C2 betrifft ausschließlich die Frage, ob die
Bytes von `RCC_002_SCR_005_CORRECTED_FULL_SPEC_BUNDLE_2026-07-24.md` mit
dem von `RCC-002-SCR-006`/`RCC-002-AIR-002` referenzierten Hash
übereinstimmen (siehe
`RCC_002_C2_REVIEW_LINEAGE_INVESTIGATION_2026-07-25.md`). Der vorliegende
Review (wie bereits `RCC-002-C1-SCR`) wurde direkt gegen die tatsächlich im
Repository vorliegenden Bytes durchgeführt und ist davon unabhängig
durchführbar und in sich schlüssig.

**Schlussfolgerung:** C2 betrifft nach dem hier verfügbaren Faktenstand
**ausschließlich Governance und Nachvollziehbarkeit** der Freigabekette
(welches Dokument wurde wann von wem als geprüft bestätigt), **nicht** die
fachliche Architektur der C1-Korrektur selbst. Die in diesem Review
geprüften Architektureigenschaften (Row Preservation, Stage Contracts,
Invarianten) sind Eigenschaften des vorliegenden Texts und unabhängig
davon feststellbar, ob dieser Text mit dem SCR-006/AIR-002-referenzierten
Hash übereinstimmt. Diese Einschätzung ist mit der gebotenen Vorsicht zu
lesen: sie bewertet, *was der Text aussagt*, nicht, *ob der Text
identisch mit dem ist, was SCR-006/AIR-002 tatsächlich geprüft haben* —
Letzteres bleibt ungeklärt und ist nicht Gegenstand dieses Reviews.

---

## 10. Empfohlene nächste Schritte

1. AIR3-M1 durch eine Governance-Entscheidung adressieren: explizite
   `S8_rows = S7_rows`-Invariante (je View) und zugehöriges
   Reconciliation-Testerfordernis ergänzen — analog zum Muster, das C1
   bereits für S2 bis S7 etabliert hat. Diese Ergänzung selbst würde
   erneut Scientific-Consistency- und Architecture-Integrity-Prüfung
   benötigen.
2. AIR3-m1/m2 bei nächster Gelegenheit beheben (Rückverweis auf §5.8 aus
   den sechs Dokumenten; eigenständiges S8-Publication-Gate-Kapitel).
3. Unabhängig von 1. und 2.: C2 gemäß
   `RCC_002_C2_REVIEW_LINEAGE_INVESTIGATION_2026-07-25.md` §10 klären, da
   Editorial Pass und Internal Certification weiterhin bis zur Klärung
   gesperrt bleiben (siehe `RCC_002_C1_CORRECTED_BUNDLE_MANIFEST_2026-07-25.md`
   §6) — unabhängig vom PASS-Urteil dieses Architecture Integrity Reviews.
4. Editorial Pass erst nach 1. (oder einer expliziten, begründeten
   Governance-Entscheidung, AIR3-M1 als akzeptiertes Risiko zurückzustellen)
   und nach Klärung von C2.

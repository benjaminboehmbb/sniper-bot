# RCC-002 C1 Scientific Consistency Review

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Fokussierter Scientific Consistency Re-Review |
| Dokument-ID | `RCC-002-C1-SCR` |
| Titel | Scientific Consistency Review — RCC-002 C1-Korrektur |
| Version | 1.0.0 |
| Datum | 2026-07-25 |
| Status | Abgeschlossen — Urteil: PASS WITH MINOR CORRECTIONS |
| Prüfgegenstand | `docs/review/RCC_002_C1_CORRECTED_FULL_SPEC_BUNDLE_2026-07-25.md` |
| Referenzartefakt | `docs/review/RCC_002_SCR_005_CORRECTED_FULL_SPEC_BUNDLE_2026-07-24.md` |
| Geprüfte Zusatzartefakte | `RCC_002_C1_VERIFICATION_RECORD_2026-07-25.md`; `RCC_002_C1_IMPACT_ANALYSIS_2026-07-25.md`; `RCC_002_C1_CORRECTED_BUNDLE_MANIFEST_2026-07-25.md`; `scripts/build_rcc002_spec_bundle.py`; alle sieben Dateien unter `docs/specifications/` |
| Speicherort im Repository | `docs/review/RCC_002_C1_SCIENTIFIC_CONSISTENCY_REVIEW_2026-07-25.md` |
| Dateiname | `RCC_002_C1_SCIENTIFIC_CONSISTENCY_REVIEW_2026-07-25.md` |
| Vorgängerreview | keiner (erster Review der C1-Korrektur) |
| Referenziert durch | ausstehender Architecture Integrity Review der C1-Korrektur |
| Unabhängigkeit | Review durchgeführt von derselben Ausführungsinstanz, die die C1-Korrektur implementiert hat; Methodik ist daher diff- und hash-basiert (nicht meinungsbasiert), um Bestätigungsverzerrung zu minimieren |

Es wurden **keine Dateien verändert und kein Commit erstellt**, mit
Ausnahme dieses Berichts selbst.

---

## 1. Urteil

```text
PASS WITH MINOR CORRECTIONS
```

Die C1-Korrektur beseitigt den bestätigten Widerspruch vollständig,
korrekt und ohne unbeabsichtigte Nebenwirkungen. Ein Major Finding
(Versionierung) und zwei Minor Findings (Generator-Robustheit) verbleiben.
Ein bereits vor der C1-Korrektur bestehendes, von ihr unabhängiges
Critical-Finding (C2, Hash-Diskrepanz des alten Bundles) bleibt offen und
blockiert weiterhin jeden Schritt nach diesem Review (siehe Abschnitt 9).

---

## 2. Critical Findings

Keine. Die C1-Korrektur selbst enthält keinen fortbestehenden
Architekturwiderspruch; Generator und neues Bundle sind vertrauenswürdig;
die Quelldokumente entsprechen nachweislich der geprüften SCR-005-Baseline
plus exakt den beabsichtigten Änderungen.

---

## 3. Major Findings

### M1 — Versionsnummern der drei geänderten Dokumente nicht erhöht

`RCC_002_C1_IMPACT_ANALYSIS_2026-07-25.md` §1 begründet ausdrücklich die
Entscheidung, die Versionsfelder von Data Pipeline (0.7.0), Data Validation
(0.4.0) und Indicator (0.4.0) unverändert zu lassen, mit der Begründung
„Wortlautkorrektur … keine neue fachliche Festlegung“.

Bei unabhängiger Prüfung wird diese Entscheidung als nicht ausreichend
begründet bewertet:

- Die eigene Kompatibilitätsregel des Datenpipeline-Dokuments (§6.4) sieht
  bereits für „redaktionelle oder nichtsemantische Metadatenkorrektur“
  mindestens einen Patch-Schritt vor. Die C1-Korrektur ändert wörtlich
  gefasste, testbare Publication-Gate-Kriterien — das ist mehr als eine
  reine Metadatenkorrektur.
- Der gesamte Anlass dieser Korrektur (Finding C1) sowie das separat
  dokumentierte Finding C2 zeigen beide, dass unversionierte
  Textänderungen an genau dieser Dokumentfamilie bereits zu
  Rückverfolgbarkeitsproblemen geführt haben. Zwei Fassungen desselben
  Dokuments mit identischem Versions-Tag („0.7.0“), aber unterschiedlichem
  Bytegehalt, sind genau das Muster, das zu C2 geführt hat.
- Ein künftiger Leser, der `RCC_002_DATA_PIPELINE_SPECIFICATION` „Version
  0.7.0“ zitiert, kann nicht mehr eindeutig zwischen der SCR-006/AIR-002-
  geprüften und der C1-korrigierten Fassung unterscheiden, ohne den
  Byte-Hash zu prüfen.

**Empfehlung:** Patch-Versionsschritt für alle drei geänderten Dokumente
(z. B. Data Pipeline 0.7.0 → 0.7.1, Data Validation 0.4.0 → 0.4.1, Indicator
0.4.0 → 0.4.1) vor jedem weiteren Review-Schritt. Siehe Prüfung D für die
vollständige Klassifikation. Diese Empfehlung wird hier nur ausgesprochen,
nicht selbst umgesetzt.

---

## 4. Minor Findings

### m1 — Generator: unbehandelte Ausnahme bei fehlender Quelldatei

`scripts/build_rcc002_spec_bundle.py` bricht bei einer fehlenden
Quelldatei mit einem rohen `FileNotFoundError`-Traceback ab, nicht mit
einer klaren, governance-tauglichen Fehlermeldung. Das Verhalten ist
sicher (kein stiller Fehlschlag, kein fehlerhaftes Bundle wird erzeugt),
aber nicht benutzerfreundlich. Empfehlung: expliziter Existenzcheck mit
klarer Fehlermeldung vor dem Lesen jeder Datei.

### m2 — Generator: keine explizite Newline-Portabilität

`Path.write_text(bundle, encoding="utf-8")` erzwingt kein `newline="\n"`.
Auf der aktuellen Linux-Umgebung ist das Verhalten nachweislich
deterministisch (Round-Trip-Test bytegleich bestanden), auf einer
Windows-Umgebung könnte die Standard-Newline-Übersetzung abweichende Bytes
erzeugen. Da `RCC_002_REPRODUCIBILITY_AND_MANIFEST` §16 geräteübergreifende
Reproduktion als Anforderung führt, ist dies für einen Bundle-Generator
potenziell relevant. Empfehlung: `newline="\n"` explizit setzen.

### m3 — §5.8 spricht das Verbot gültiger Indikator-/Signalwerte nur implizit aus

Data Pipeline §5.8 listet zulässige Reaktionen („ungültige oder
Null-Indikatorwerte …“), formuliert aber kein explizites Verbot gültiger
Werte für `quality_gate_pass=false`-Zeilen. Die explizite Verbotsformel
existiert bereits an der fachlich richtigen Stelle (Indicator §4.3/§30
sowie die unveränderte `x_valid`-Formel in Indicator §20.1), sodass keine
normative Lücke entsteht — die Beobachtung betrifft ausschließlich die
Robustheit der Formulierung in §5.8 selbst als allgemeines
Architekturprinzip.

---

## 5. Positive Findings

- Die vier korrigierten Normstellen sind inhaltlich **untereinander
  konsistent** und jeweils vollständig in sich stimmig (Prüfung B: alle
  zehn geforderten Dimensionen — normative Klarheit, RFC-2119-Konsistenz,
  Stage-Contract-Übereinstimmung, `S3_rows = S2_rows`, Erreichbarkeit von
  `quality_gate_pass=false`, Verbot gültiger Indikatorwerte, Row Identity/
  Order, Verhältnis zu Abbruch/Quarantäne, Publication-Semantik, keine
  implizite Row Deletion — erfüllt, keine neue Prioritätsregel erzeugt).
- Der strukturierte Bundle-Diff (Prüfung A) zeigt **ausschließlich**
  die drei beabsichtigten Normstellen-Änderungen plus die notwendige
  Header-/Tabellenaktualisierung; alle vier unveränderten Dokumente
  (Signal Transformation, Regime and Gate, Label and Forward Return,
  Reproducibility and Manifest) sind byte-identisch mit ihrer im
  SCR-005-Bundle eingebetteten Fassung. Keine Klasse-C- oder
  Klasse-D-Abweichung gefunden.
- Der Generator reproduziert das alte SCR-005-Bundle **byte-exakt**
  (identischer SHA-256) aus unveränderten, aus dem alten Bundle
  rekonstruierten Quelldateien — unabhängig nachvollzogen, nicht nur
  behauptet.
- Alle in `RCC_002_C1_CORRECTED_BUNDLE_MANIFEST_2026-07-25.md`
  behaupteten Zeilen-, Byte- und SHA-256-Werte wurden unabhängig neu
  berechnet und stimmen exakt überein (Prüfung E).
- Die systemweite Suche (Prüfung C, erweitert um englische Begriffe wie
  „row identity“, „excluded“, „removed“, „filtered“, „dropped“,
  „quarantine“, „abort“) fand keinen weiteren Widerspruch zu §5.8 in
  keinem der sieben Dokumente.
- Das Manifest benennt korrekt und unmissverständlich, dass SCR-006,
  AIR-002, Editorial Pass und Internal Certification des alten Bundles
  nicht auf das neue Bundle übertragen werden, und setzt den neuen
  Reviewstatus explizit auf „vollständige Re-Reviews ausstehend“.

---

## 6. Bundle-Diff-Ergebnis (Prüfung A)

Strukturierter Diff zwischen den aus beiden Bundles extrahierten sieben
Einzeldokumenten plus Kopfbereich:

| Bestandteil | Ergebnis | Klasse |
|---|---|---|
| Kopfbereich (Titel, Korrekturstand, Datei-Tabelle) | geändert (Titel, Korrekturstand-Text, drei Tabellenzeilen mit neuen Zeilen-/Byte-/Hashwerten) | **B** — notwendige Manifeständerung |
| Data Pipeline | +31 Zeilen (§5.8 neu) | **A** — beabsichtigt |
| Data Validation | §20 Kriterium 16 umformuliert | **A** — beabsichtigt |
| Indicator | §4.3 und §30 Kriterium 2 umformuliert | **A** — beabsichtigt |
| Signal Transformation | keine Änderung (bytegleich) | — |
| Regime and Gate | keine Änderung (bytegleich) | — |
| Label and Forward Return | keine Änderung (bytegleich) | — |
| Reproducibility and Manifest | keine Änderung (bytegleich) | — |

**Keine Klasse-C- oder Klasse-D-Abweichung gefunden.** Die
Dokumentgrenzen, die Reihenfolge (identisch zur alten Reihenfolge) und die
`## Quelldatei:`-Header sind in allen sieben eingebetteten Dokumenten
korrekt. Der Generator reproduziert das alte Bundle byte-exakt aus
unveränderten Quelldateien (SHA-256-Übereinstimmung, siehe Prüfung E).

---

## 7. Bewertung der Versionsnummern (Prüfung D)

| Dimension | Bewertung |
|---|---|
| Art der Änderung | Normative Klarstellung ohne beabsichtigte Verhaltensänderung — aber mit wörtlicher Änderung testbarer Kriterien, nicht reine Metadatenkorrektur |
| Rein redaktionell? | Nein — die alte Formulierung war wörtlich implementierbar (wenn auch falsch); die neue Formulierung ändert den literalen Prüftext |
| Normative Architekturänderung? | Nein — keine neue Architekturentscheidung, keine neue Priorität, keine neue Spezifikation |
| Mindestens Patch-Bump erforderlich? | **Ja, nach Einschätzung dieses Reviews** (siehe Major Finding M1) |

Empfehlung: Patch-Bump für alle drei Dokumente. Keine Versionsänderung
wurde im Rahmen dieses Reviews selbst vorgenommen.

---

## 8. Generator-/Manifest-Bewertung (Prüfung E)

| Kriterium | Ergebnis |
|---|---|
| Deterministische Dateireihenfolge | Bestanden — feste Liste, keine Verzeichnis-Iteration |
| Deterministische Trennzeichen/Newlines | Bestanden auf der aktuellen Linux-Umgebung (Round-Trip bytegleich); Portabilitätsschwäche siehe m2 |
| Keine Inhaltstransformation | Bestanden — einzige Operation ist `rstrip("\n")` + ein `\n` |
| Verhalten bei fehlender Quelldatei | Bricht sicher ab (kein stilles Fehlverhalten), aber mit rohem Traceback statt klarer Meldung — siehe m1 |
| Verhalten bei zusätzlichen Quelldateien | Zusätzliche, nicht in der festen Liste enthaltene Dateien werden ignoriert (sicher, aber ohne Warnung) |
| Verhalten bei doppelt benannten Quelldateien | Szenario durch feste Dateiliste und Dateisystem-Eindeutigkeit ausgeschlossen; nicht separat testbar |
| Reproduzierbarer Generierungsbefehl | Dokumentiert und im Manifest angegeben; unabhängig ausgeführt und verifiziert |
| Manifest-Hashes/Zeilen/Bytes vs. tatsächliche Dateien | Alle acht geprüften Werte unabhängig neu berechnet — **vollständige Übereinstimmung** |
| Vollständige Dateiliste | Alle sieben Dateien im Manifest gelistet, Reihenfolge korrekt |
| Kennzeichnung ausstehender Re-Reviews | Korrekt und vollständig |
| Aussage zur Nichtübertragung alter Zertifizierungen | Korrekt, unmissverständlich, mit Nennung aller betroffenen Gates |

---

## 9. C2-Auswirkung auf die Review-Lineage (Prüfung F)

Tatsächlich gemessene Werte (mehrfach unabhängig reproduziert: direkte
Hash-Berechnung, byte-exakter Generator-Round-Trip, erneute Messung im
Rahmen dieses Reviews):

```text
Tatsächlicher SHA-256 von RCC_002_SCR_005_CORRECTED_FULL_SPEC_BUNDLE_2026-07-24.md:
    5aae1bd7107ace3baf1de8178349169249b387756fe406598a8a7fad1ed190b2

Von RCC-002-SCR-006 und RCC-002-AIR-002 referenzierter Paket-SHA-256:
    33aac77fe96147c8d81e8683db470f50780159b7168e1139214592f7fd6e26c5
```

Diese beiden Werte stimmen nicht überein. Die Ursache dieser Diskrepanz
ist **nicht ermittelt** und wird hier ausdrücklich nicht spekulativ
erklärt.

**Stellt die Differenz die Review-Lineage des alten Bundles infrage?** Ja.
Die in `RCC-002-AIR-002` §2 formulierte Reviewvoraussetzung („genau
dasselbe Paket wie SCR-006“) stützt sich ausschließlich auf einen
Hash-Abgleich zwischen zwei Dokumenten, nicht auf eine Neuberechnung gegen
die tatsächliche Datei. Es ist damit derzeit nicht verifizierbar, dass
SCR-006 und AIR-002 sich auf die Bytes beziehen, die tatsächlich im
Repository liegen.

**Kann der C1-Re-Review unabhängig davon belastbar durchgeführt werden?**
Ja, mit einer wichtigen Einschränkung. Dieser Review (Prüfung A–E) basiert
ausschließlich auf einem direkten Diff gegen die tatsächlich im Repository
vorliegenden Bytes von `RCC_002_SCR_005_CORRECTED_FULL_SPEC_BUNDLE_2026-07-24.md`
— er setzt an keiner Stelle voraus, dass diese Bytes mit dem
`33aac77f…`-Hash übereinstimmen. Die hier getroffenen Aussagen („der
strukturierte Diff zeigt ausschließlich die beabsichtigten Änderungen“)
sind daher in sich schlüssig und unabhängig überprüfbar. **Was dieser
Review nicht leisten kann:** bestätigen, dass die als „SCR-005-Corrected“
gelabelten Inhalte, auf denen die C1-Korrektur aufbaut, tatsächlich
identisch mit dem sind, was SCR-006 und AIR-002 inhaltlich geprüft haben.
Sollte sich herausstellen, dass die tatsächlichen Bytes von den
SCR-006/AIR-002-geprüften Inhalten abweichen, müsste auch die C1-Korrektur
gegen die dann korrekt identifizierte Baseline neu bewertet werden.

**Welche C2-Untersuchung ist zwingend vor AIR, Editorial Pass oder
Certification abzuschließen?**

1. Feststellen, ob überhaupt eine historische Artefaktversion mit Hash
   `33aac77f…` auffindbar ist (Backup, Git-Reflog, lokale Historie außerhalb
   des Repositories, Erzeugungsprotokoll).
2. Falls auffindbar: Byte-Diff zwischen dieser Version und der aktuell im
   Repository committeten Version (`5aae1bd7…`) bilden und klassifizieren
   (z. B. Zeilenende-/Whitespace-Artefakt vs. inhaltliche Abweichung).
3. Falls nicht auffindbar: SCR-006 und AIR-002 können nicht als gültig für
   das aktuell vorliegende Artefakt betrachtet werden; ein vollständiger,
   nicht fokussierter Re-Review beider Stufen gegen die tatsächlichen Bytes
   ist erforderlich, bevor irgendein nachfolgendes Gate (einschließlich des
   hier durchgeführten C1-Re-Reviews) als Grundlage für Editorial Pass oder
   Certification dienen kann.
4. Unabhängig vom Ergebnis: `RCC-002-SCR-006` und `RCC-002-AIR-002` um eine
   Korrektur oder einen Vermerk ergänzen, der den tatsächlich geprüften
   Hash zweifelsfrei dokumentiert, damit sich diese Diskrepanz nicht in der
   C1-Fassung oder künftigen Fassungen wiederholt.

Bis Punkt 1–4 abgeschlossen sind, gilt die Freigabekette
SCR-005 → SCR-006 → AIR-002 als **nicht abschließend verifiziert**,
unabhängig vom Ergebnis dieses C1-Reviews.

---

## 10. Exakt erforderliche nächste Schritte

1. **Vor jedem weiteren Review-Gate:** C2-Untersuchung gemäß Abschnitt 9,
   Punkte 1–4, abschließen.
2. **Governance-Entscheidung einholen:** Patch-Versionsschritt für die drei
   geänderten Dokumente (Major Finding M1) genehmigen oder mit expliziter
   Gegenbegründung ablehnen.
3. **Optional, vor Implementierungsfreigabe (nicht blockierend für den
   nächsten Review-Schritt):** die zwei Minor Findings am Generator (m1,
   m2) beheben.
4. **Erst nach 1 und 2:** fokussierter Architecture Integrity Re-Review der
   C1-Korrektur, im selben Prüfumfang wie dieser Scientific Consistency
   Review (die vier geänderten Normstellen plus deren Wirkung auf Stage
   Contracts, Schemaeigentum und Publikationsgrenzen).
5. Editorial Pass, Internal Certification und alle nachfolgenden Gates
   bleiben bis zur Klärung von C2 gesperrt, unabhängig vom Ausgang von
   Schritt 4.

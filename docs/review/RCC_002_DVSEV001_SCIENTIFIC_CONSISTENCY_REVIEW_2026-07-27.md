# RCC-002 DVSEV-001 — Scientific Consistency Review

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Fokussierter Scientific Consistency Review |
| Dokument-ID | `RCC-002-DVSEV001-SCR` |
| Datum | 2026-07-27 |
| Status | Abgeschlossen — Urteil: PASS |
| Prüfgegenstand | Ausschließlich der DVSEV-001-Diff: neuer §16.3 in `RCC_002_DATA_VALIDATION` (Version 0.4.2→0.5.0) und die fünf mechanischen Zitat-Folgeanpassungen |
| Explizit außerhalb des Prüfumfangs | Jede wissenschaftliche Fragestellung, die bereits von SCR-007, seinen zwei Findings-Verifikationen oder SCR-008 abschließend behandelt wurde und von DVSEV-001 nicht berührt wird |
| Vorgängerreview (dieser Zyklus) | `RCC_002_DVSEV001_EDITORIAL_PASS_2026-07-27.md` (PASS); die bereits durchgeführte fokussierte Review der vier schwächer belegten Severities (`DV_TIME_OUT_OF_RANGE`, `DV_GAP_DETECTED`, `DV_FILE_EMPTY`, `DV_VOLUME_ZERO_OBSERVED`) — hier nicht wiederholt, sondern als Ausgangsbefund übernommen und in Prüfbereich D um zusätzliche, in jener Review nicht behandelte Aspekte ergänzt |
| Methodik | Aktive Suche nach Gegenbeispielen statt Bestätigung der Vorbefunde; jede Aussage ist an eine Zitatstelle oder einen ausgeführten Befehl gebunden |

Es wurden **keine Dateien verändert und kein Commit erstellt**, mit
Ausnahme dieses Berichts selbst.

---

## 1. Urteil

```text
PASS
```

Kein Critical, Major oder Minor Finding. Ein Observation-Finding (siehe
Abschnitt 5) zu einer bereits vor DVSEV-001 bestehenden, durch DVSEV-001
lediglich stärker sichtbar gemachten offenen Frage.

---

## 2. Prüfbereich A — Determinismus und Reproduzierbarkeit

Das neue §16.3 ist eine statische, versionierte Tabelle ohne Laufzeitzustand,
Zufallsquelle oder Abhängigkeit von Ausführungsreihenfolge. Es führt keine
neue Berechnung, keinen neuen Zufallsmechanismus und keine neue
Zeitabhängigkeit ein.

**Aktiv geprüft:** Könnte die Reihenfolge der 32 Tabellenzeilen die
Sortierung von `quality_reason_codes` beeinflussen? Nein — §16.2 bindet die
Sortierung explizit an ein separates, weiterhin offenes
„Reason-Code-Prioritätsregister" (§25.1), nicht an die Zeilenreihenfolge von
§16.3. Die Tabelle in §16.3 folgt der Reihenfolge der `Mindestcodes`-Liste
aus §16.2 rein zur Lesbarkeit; dies wurde programmatisch verifiziert
(identische Menge, identische Reihenfolge). Keine versteckte Kopplung
gefunden.

**Ergebnis:** Kein Determinismus- oder Reproduzierbarkeitsproblem.

---

## 3. Prüfbereich B — Konsistenz mit `quality_status`/`quality_gate_pass` (§15, §15.1)

Die Formel „`quality_status` wird aus der höchsten registrierten Severity
aller aktiven `quality_reason_codes` gebildet" (§15) setzt implizit eine
Ordnung `INFO < WARN < ERROR < CRITICAL` voraus. Diese Ordnung ist bereits
durch die Aufzählungsreihenfolge in §15 selbst und durch die Tabelle in
§16.1 (identische Reihenfolge) festgelegt — DVSEV-001 fügt keine neue
Ordnungsannahme hinzu und widerspricht der bestehenden nicht.

**Aktiv geprüft:** Existiert eine der 32 zugewiesenen Severities, die mit
einer bereits bestehenden Formel kollidiert? Für alle 6 bereits explizit
normierten Codes wurde die §16.3-Zuordnung gegen den Wortlaut der
zitierten Stelle geprüft — wortidentisch übernommen (programmatisch
verifiziert). Für die 26 neu zugeordneten Codes wurde jede zitierte Stelle
einzeln gelesen; keine davon widerspricht einer anderen Stelle, die
dieselbe Severity anders beziffern würde.

**Aktiv geprüft (Gegenbeispielsuche):** Könnte eine der 8 neu als `WARN`
eingestuften Codes durch §15.1s Klausel „jeder aktive `WARN` … muss …
ausdrücklich als nicht blockierend klassifiziert" faktisch zu
`quality_gate_pass=false` führen, obwohl der Reason Code selbst als „nicht
blockierend" im Sinne von §16.1 gedacht ist? **Ja, das ist der Fall — aber
das ist keine neu durch DVSEV-001 eingeführte Inkonsistenz.** §15.1 verlangt
bereits vor DVSEV-001 eine explizite Klassifikation jedes aktiven `WARN`
durch ein „versioniertes Qualitätsprofil"; dieses Profil selbst ist Teil des
in §25.1 weiterhin offenen Parameters „Validierungsregelprofil und
`quality_rule_version`". DVSEV-001 macht lediglich sichtbar, dass nun 8
konkrete Codes (zuvor: unbekannt viele, da unregistriert) dieser noch
ausstehenden Klassifikation bedürfen. Dies ist eine Konsequenz der
Vervollständigung des Registers, keine neue Inkonsistenz (siehe Abschnitt 5,
Observation-Finding).

**Ergebnis:** Kein Widerspruch zu §15/§15.1. Ein bereits bestehender, noch
offener Abhängigkeitsparameter (§25.1) wird durch DVSEV-001 konkreter,
nicht neu geschaffen.

---

## 4. Prüfbereich C — Konsistenz mit Testanforderungen (§21) und Publication Gate (§20)

**Aktiv geprüft:** Benennt eines der in §21.3 aufgeführten Golden-Fixture-
Kategorien ("vollständig gültige Zeitreihe", "jede kritische Fehlerklasse",
"genehmigte Provider-Lücke", "Partition mit Überlappung", "historische
Excel-Trunkierung", "inkrementelle Quellrevision") einen konkreten
Reason Code mit einer dort bereits festgelegten, von §16.3 abweichenden
Severity-Erwartung? Nein — keine der sechs Kategorien nennt einen
spezifischen `DV_`-Code mit einer eigenen Severity-Festlegung.

**Zusätzlich gefunden (positiv, nicht in der vorausgehenden fokussierten
Review erfasst):** §21.1 listet „Reason-Code- und Severity-Mapping"
ausdrücklich als **Mindestanforderung** für Unit-Tests. Vor DVSEV-001 war
diese Testanforderung für 26 der 32 Codes nicht erfüllbar, da keine
Severity registriert war. DVSEV-001 stellt damit nicht nur keine
Inkonsistenz dar, sondern schließt eine Lücke, die eine bereits bindende
Testanforderung andernfalls unerfüllbar gemacht hätte.

**Aktiv geprüft:** Widerspricht eine der 32 Zuordnungen der
Property-Test-Anforderung aus §21.2 („keine Zeile mit blockierendem
Reason Code erhält `quality_gate_pass=true`")? Nein — für alle 13
`CRITICAL`- und 4 `ERROR`-Codes blockiert die Severity `quality_gate_pass`
per §15.1 unmittelbar; für die 8 `WARN`-Codes gilt die in Abschnitt 3
diskutierte, bereits bestehende explizite Klassifikationspflicht; für die 7
`INFO`-Codes ist Nichtblockierung per §16.1-Definition („keine
Blockierung") korrekt.

**Aktiv geprüft:** Widerspricht eine der 32 Zuordnungen Publication-Gate-
Kriterium 12 (§20, „kein `ERROR` oder `CRITICAL` offen ist") oder der
Ausnahmeregel („darf weder einen aktiven zeilenbezogenen `ERROR` oder
`CRITICAL` überstimmen")? Nein — beide bleiben unverändert und wortgleich
mit den neuen Zuordnungen vereinbar.

**Ergebnis:** Kein Widerspruch. Eine bereits bindende, zuvor unerfüllbare
Testanforderung wird durch DVSEV-001 erfüllbar.

---

## 5. Observation-Findings

### DVSEV001-O1 — Klassifikationspflicht für 8 `WARN`-Codes bleibt an einen weiterhin offenen Parameter gebunden

**Beobachtung:** §15.1 verlangt für `quality_gate_pass=true`, dass jeder
aktive `WARN`-Code durch das „versionierte Qualitätsprofil" (`quality_rule_
version`) explizit als nicht blockierend klassifiziert ist. Dieses Profil
ist weiterhin ein offener Implementierungsparameter (§25.1). DVSEV-001
identifiziert nun konkret die 8 Codes, für die diese Klassifikation vor
Abschluss von Implementierungsschritt 4 (S2) getroffen werden muss:
`DV_SCHEMA_UNEXPECTED_COLUMN`, `DV_GAP_DETECTED`, `DV_VOLUME_ZERO_OBSERVED`,
und die sechs `DV_ANOMALY_*`-Codes.

**Warum das relevant ist:** Ohne diese Klassifikation würde per Fail-
closed-Standardverhalten jede Zeile mit einem dieser 8 aktiven Codes
`quality_gate_pass=false` erhalten — was fachlich korrekt sein kann (z. B.
bei `DV_GAP_DETECTED`, wo `quality_gap_before`/`quality_gap_after` ohnehin
gesonderte Felder sind), aber für einige Codes (z. B.
`DV_ANOMALY_EXTREME_VOLUME`, laut §13.1 ausdrücklich „Untersuchung, nicht
stille Datenbereinigung") möglicherweise nicht die beabsichtigte, praktisch
nutzbare Standardauslegung ist.

**Einstufung:** Observation, kein Finding, das DVSEV-001 selbst betrifft.
DVSEV-001 hat diesen Parameter nicht neu geschaffen und ist nicht dafür
verantwortlich, ihn zu schließen — das bleibt Gegenstand des bereits in
§25.1 dokumentierten, separaten offenen Punkts.

**Empfehlung (nicht selbst umgesetzt):** Vor Implementierungsschritt 4 das
„versionierte Qualitätsprofil" für mindestens diese 8 Codes definieren,
entweder als Teil der Umsetzung von §25.1 oder als eigener, kleiner
Folgekorrekturzyklus.

---

## 6. Positive Findings

- Alle 32 Reason Codes besitzen nach DVSEV-001 eine deterministische
  Standard-Severity; die in §24.1 Nr. 3 formulierte Abnahmevoraussetzung
  ist für diesen Aspekt erstmals erfüllbar.
- Die bereits bindende Testanforderung „Reason-Code- und Severity-Mapping"
  (§21.1) ist nun erstmals für alle 32 Codes erfüllbar.
- Keine der 32 Zuordnungen widerspricht einer bestehenden Formel, einem
  bestehenden Golden-Fixture-Bereich oder einer bestehenden Property-Test-
  Anforderung.
- Fail-closed-Philosophie durchgängig gewahrt: keine der 26 neuen
  Zuordnungen schwächt eine bestehende Blockierungswirkung ab; im
  Zweifel wurde die konservativere, stärker belegte Auslegung gewählt
  (siehe die bereits durchgeführte fokussierte Review der vier
  schwächer belegten Fälle).
- AFML-/Backtest-Integrity-Erwägungen (`docs/POLICIES/`) sind nicht
  berührt: DVSEV-001 ändert keine Trainings-, Validierungs- oder
  Backtest-Methodik, sondern ausschließlich die S2-Datenqualitäts-
  Severity-Registrierung.

---

## 7. Ergebnis

```text
PASS

Keine Critical, Major oder Minor Findings.
Ein Observation-Finding (DVSEV001-O1) zu einem bereits vor DVSEV-001
bestehenden, weiterhin offenen Implementierungsparameter (§25.1) — nicht
durch DVSEV-001 verursacht, durch DVSEV-001 lediglich konkretisiert.
Determinismus, Reproduzierbarkeit, quality_status/quality_gate_pass-
Konsistenz, Testanforderungs- und Publication-Gate-Konsistenz: bestätigt.
```

# RCC-002 Specification Family – Scientific Consistency Review Report

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Scientific Consistency Review Report |
| Speicherort | `docs/review/` |
| Dateiname | `RCC_002_SPECIFICATION_FAMILY_SCR_REPORT_2026-07-23.md` |
| Dokument-ID | `RCC-002-SCR-001` |
| Version | `0.1.0` |
| Datum | `2026-07-23` |
| Reviewgegenstand | Vollständige RCC-002-Spezifikationsfamilie |
| Reviewstufe | Scientific Consistency Review |
| Status | `NOT_PASSED – CORRECTION REQUIRED` |
| Abhängigkeit | `RCC_002_SPECIFICATION_FAMILY_SCR_INPUT_2026-07-23.md` |
| Referenziert durch | RCC-002-Korrekturlauf; SCR-Re-Review; Architecture Integrity Review |

## 1. Reviewumfang

Geprüft wurden:

1. `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`, Version 0.2.0;
2. `RCC_002_DATA_VALIDATION_2026-07-23.md`, Version 0.1.0;
3. `RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md`, Version 0.1.0;
4. `RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md`, Version 0.1.0;
5. `RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md`, Version 0.1.0;
6. `RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md`, Version 0.1.0;
7. `RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md`, Version 0.1.0.

Geprüfte Konsistenzdimensionen:

- Stufenverträge S0–S8;
- kanonische und nichtkanonische Datenansichten;
- Zeit-, Verfügbarkeits- und Kausalitätssemantik;
- Lücken-, Segment- und Warm-up-Regeln;
- Indikatorformeln und Seeds;
- Signalvorzeichen, Rollen und Invalid-Semantik;
- Regime- und Gate-Zustandsmaschinen;
- Forward Returns, Kosten, MFE/MAE und Barrier-Labels;
- Feldnamen und Schemafamilien;
- Build-, Run-, Dataset-, Artifact- und Manifestidentitäten;
- Dataset Lineage und Knowledge Lineage;
- Rebuild- und Cross-Device-Regeln;
- redaktionelle Integrität normativer Passagen.

## 2. Gesamturteil

Der Scientific Consistency Review ist in der vorliegenden Fassung:

```text
NOT_PASSED – CORRECTION REQUIRED
```

Begründung:

- fünf normative Schnittstellen- oder Reproduzierbarkeitskonflikte;
- zwei beschädigte Textpassagen in einer normativen Spezifikation;
- mehrere begrenzte Präzisierungsbedarfe.

Die Befunde erfordern keine grundlegende Änderung der RCC-002-Architektur.
Betroffen sind hauptsächlich Verträge zwischen Dokumenten und die
Implementierbarkeit der Manifestregeln.

Nach Korrektur ist ein fokussierter SCR-Re-Review erforderlich.

## 3. Bestätigte wissenschaftliche Konsistenz

### 3.1 Datenfluss

Die Stufenfolge:

```text
S0 Source
→ S1 Normalized
→ S2 Validated
→ S3 Indicators
→ S4 Signals
→ S5 Regimes
→ S6 Gates
→ S7 Labels
→ S8 Export
```

ist kausal, modular und wissenschaftlich nachvollziehbar.

### 3.2 Point-in-Time-Korrektheit

Bestätigt:

- S0 bis S6 verwenden keine Zukunftsdaten;
- S7 ist die einzige reguläre Stufe, die Zukunftsdaten neu berechnet;
- S7-Felder werden aus Live-/Paper-Views ausgeschlossen;
- Regimepersistenz schreibt frühere Zustände nicht rückwirkend um;
- Forward-Label-Verfügbarkeit wird erst nach Schluss der Horizontendkerze
  angenommen.

### 3.3 Indikatorformeln

Die kanonischen Definitionen sind intern konsistent für:

- SMA 200;
- EMA 50 mit SMA-Seed;
- RSI 14 nach Wilder;
- MACD 12/26/9;
- Bollinger Bands 20/2 mit `ddof=0`;
- Stochastic %K 14;
- ATR 14 nach Wilder;
- ROC 12;
- OBV;
- CCI 20 mit fensterbezogener Mean Absolute Deviation;
- MFI 14;
- ADX 14 nach Wilder.

Seeds, erste gültige Indizes und Warm-up-Matrix stimmen überein.

### 3.4 Signaltransformation

Bestätigt:

- `+1` beziehungsweise positive Scores sind long-supportive;
- `-1` beziehungsweise negative Scores sind short-supportive;
- Trend-, Volatilitäts- und Trendstärkefelder bleiben von
  Richtungssignalen getrennt;
- ungültig wird nicht als neutral interpretiert;
- Legacy-Reproduktion bleibt vom kanonischen Profil getrennt.

### 3.5 Regime und Gates

Bestätigt:

- Rohregime verwendet Close relativ zu SMA 200 und den kausalen
  SMA-200-Slope über 1.440 Minuten;
- der erste Rohregimewert bei lückenfreiem Segment liegt am Index 1.639;
- der erste dreifach bestätigte effektive Zustand liegt am Index 1.641;
- Unknown setzt Candidate State deterministisch zurück;
- Regime und Handelsfreigabe sind getrennte Verantwortlichkeiten;
- das offene Forschungsgate und trendgerichtete Kandidatengates sind
  unterscheidbar.

### 3.6 Labels und Forward Returns

Bestätigt:

- Close-to-Close- und Next-Open-to-Close-Semantik;
- Long-/Short-Vorzeichen;
- Horizonte 1, 5, 15, 60, 240 und 1.440 Minuten;
- Roundtrip-Kostenbaseline `0.0004`;
- MFE-/MAE-Formeln;
- Barrier-Ambiguität bei unbekannter Intrabar-Reihenfolge;
- Gap-, Segment- und Tail-Invalidität;
- Purging über splitüberschreitende Zukunftsfenster;
- unabhängige Berechnung von Outcomes vor Gate-Gruppierungen.

## 4. Blockierende Befunde

### SCR-B01 – Widersprüchliche kanonische S2-Lückenpolitik

**Schweregrad:** `BLOCKER`

**Betroffene Dokumente:**

- Data Pipeline Specification, Abschnitt 7.3;
- Data Validation Specification, Abschnitte 11.3 und 11.4.

**Befund:**

Die Data Pipeline Specification nennt als zulässiges Ergebnis der
S2-Lückenbehandlung:

```text
deterministische synthetische Kerze nach separat freigegebener Regel
```

Die Data Validation Specification verlangt dagegen:

```text
Der kanonische beobachtete S2-Datensatz enthält ausschließlich beobachtete
Kerzen. Synthetische Kontinuitätsdaten liegen in einer separaten Ansicht.
```

Damit ist unklar, ob synthetische Kerzen Teil des kanonischen
`S2_VALIDATED`-Artefakts sein dürfen.

**Verbindliche Auflösung:**

- Der kanonische beobachtete S2-Datensatz enthält ausschließlich beobachtete
  Kerzen.
- Eine synthetische Kontinuitätsansicht ist nur als separates,
  nichtkanonisches und eindeutig gekennzeichnetes Artefakt zulässig.
- Die Data Pipeline Specification muss an die präzisere Data Validation
  Specification angepasst werden.

**Akzeptanztest:**

Kein normativer Satz darf synthetische Kerzen als Bestandteil des kanonischen
beobachteten S2-Artefakts zulassen.

### SCR-B02 – Inkonsistenter S6-Ausgabevertrag

**Schweregrad:** `BLOCKER`

**Betroffene Dokumente:**

- Data Pipeline Specification, Abschnitt 7.7;
- Regime and Gate Specification, Abschnitt 18.

**Befund:**

Die übergeordnete Spezifikation verlangt:

```text
gate_reason_codes
gate_model_id
gate_model_version
```

Die Fachspezifikation verlangt:

```text
gate_reason_codes_long
gate_reason_codes_short
gate_profile_id
gate_profile_version
```

Diese Feldfamilien sind nicht äquivalent. Eine Implementierung könnte zwei
unterschiedliche S6-Schemata erzeugen.

**Verbindliche Auflösung:**

Der verbindliche Mindestvertrag lautet:

```text
allow_long
allow_short
data_gate_pass
gate_state
gate_reason_codes_long
gate_reason_codes_short
gate_profile_id
gate_profile_version
gate_valid
gate_evaluated_at
```

Die Data Pipeline Specification muss diesen Vertrag übernehmen.

Ein optionales gemeinsames `gate_reason_codes` darf nur zusätzlich existieren,
wenn seine Aggregationsregel registriert und eindeutig ist.

### SCR-B03 – Inkonsistente S7-Präfixe und unvollständige Feldklassen

**Schweregrad:** `BLOCKER`

**Betroffene Dokumente:**

- Data Pipeline Specification, Abschnitt 9;
- Label and Forward Return Specification, Abschnitt 20.

**Befund:**

Die Data Pipeline Specification reserviert:

```text
forward_*
label_*
```

Die Label-Spezifikation verwendet:

```text
fwd_*
label_*
barrier_*
```

Damit:

- widersprechen sich `forward_*` und `fwd_*`;
- fehlt `barrier_*` in der übergeordneten Feldklassifikation.

**Verbindliche Auflösung:**

Der übergeordnete S7-Präfixvertrag lautet:

```text
fwd_*
label_*
barrier_*
```

`forward_*` wird nicht als paralleles Synonym verwendet.

### SCR-B04 – Unvollständiger kanonischer Sortierschlüssel des semantischen Fingerprints

**Schweregrad:** `BLOCKER`

**Betroffene Dokumente:**

- Data Validation Specification, Abschnitt 8.2;
- Reproducibility and Manifest Specification, Abschnitt 7.3.

**Befund:**

Der kanonische Primärschlüssel ist definiert als:

```text
(market_type, symbol, interval, open_time)
```

Die Manifest-Spezifikation definiert die kanonische Zeilenreihenfolge dagegen
nur als:

```text
symbol
UTC-Zeitstempel
gegebenenfalls sekundäre Ereignis-ID
```

`market_type` und `interval` fehlen. Bei Multi-Market- oder
Multi-Interval-Daten ist die Reihenfolge damit nicht vollständig definiert.

**Verbindliche Auflösung:**

Der semantische Fingerprint muss nach dem vollständigen registrierten
kanonischen Primärschlüssel sortieren.

Für die bestehende OHLCV-Familie:

```text
market_type
symbol
interval
open_time
```

Bei noch nicht konsolidierten Multi-Provider-Daten kommt `provider` gemäß
Schemavertrag hinzu.

### SCR-B05 – Physische Partitionierung ist fälschlich Teil der semantischen Gleichheit

**Schweregrad:** `BLOCKER`

**Betroffenes Dokument:**

- Reproducibility and Manifest Specification, Abschnitte 5.6 und 7.3.

**Befund:**

Der semantische Fingerprint soll laut Abschnitt 7.3 die
`Partitionierungslogik` enthalten.

Gleichzeitig soll semantische Gleichheit identische logische Daten trotz
unterschiedlicher Containerbytes erkennen.

Zwei logisch identische Tabellen können unterschiedlich physisch partitioniert
sein. Wenn die physische Partitionierung in den semantischen Hash eingeht,
werden sie trotz identischer Inhalte als semantisch verschieden klassifiziert.

**Verbindliche Auflösung:**

Es sind zwei Ebenen zu trennen:

1. `semantic_sha256`
   - Schema;
   - vollständiger kanonischer Primärschlüssel;
   - logische Datentypen;
   - Nullsemantik;
   - kanonisch sortierte Werte;
   - Zeilenanzahl.

2. `physical_layout_sha256`
   - Dateigrenzen;
   - Partitionierung;
   - Row Groups;
   - Kompression;
   - Writerprofil;
   - Containerparameter.

`artifact_id` darf physische Repräsentationsinformationen enthalten, wenn die
ID ausdrücklich ein physisches Artefakt bezeichnet. Der
`semantic_sha256` darf sie nicht enthalten.

## 5. Wesentliche Präzisierungsbefunde

### SCR-M01 – Kanonisches JSON ist nicht vollständig spezifiziert

**Schweregrad:** `MAJOR`

**Betroffenes Dokument:**

- Reproducibility and Manifest Specification, Abschnitt 6.2.

**Befund:**

Die Formulierung:

```text
Strings ohne Unicode-Normalisierungsambiguität
```

ist nicht implementierbar eindeutig.

Die angegebene Python-nahe Serialisierung definiert außerdem nicht alle
sprachübergreifenden Zahl- und Stringfälle.

**Erforderliche Präzisierung:**

- verbindliche Unicode-Normalisierung, mindestens NFC;
- verbindlicher kanonischer JSON-Standard oder vollständig äquivalente
  projektspezifische Definition;
- eindeutige Zahlserialisierung;
- Tests mit Unicode-, Dezimal-, Escape- und Schlüsselreihenfolge-Fixtures.

Ein geeigneter Standard darf beispielsweise RFC 8785/JCS sein, sofern
Dezimalparameter vorab gemäß RCC-Konfigurationsschema normalisiert werden.

### SCR-M02 – Source-Snapshot-Vorabbildung ist normativ zu unbestimmt

**Schweregrad:** `MAJOR`

**Betroffenes Dokument:**

- Reproducibility and Manifest Specification, Abschnitt 5.3.

**Befund:**

Abrufzeitpunkt und Pfad sollen die deterministische Identität:

```text
nicht zwingend
```

verändern.

Eine deterministische ID benötigt jedoch eine eindeutige Inklusions- und
Exklusionsregel.

**Erforderliche Präzisierung:**

- lokaler Speicherpfad ist niemals Teil der deterministischen Vorabbildung;
- Abrufzeitpunkt ist Run-/Provenienzmetadatum, nicht Teil der
  Source-Snapshot-ID, sofern der Quellinhalt und alle semantischen
  Abrufparameter identisch sind;
- Anbieter-Revisions-ID und inhaltsrelevante Abrufparameter bleiben Teil der
  Vorabbildung.

### SCR-M03 – E3-Anforderung für Manifeste ist zu breit

**Schweregrad:** `MAJOR`

**Betroffenes Dokument:**

- Reproducibility and Manifest Specification, Abschnitt 7.4.

**Befund:**

Die pauschale Regel:

```text
Manifeste müssen E3 erreichen
```

ist für unabhängig neu erzeugte Run Manifests nicht sinnvoll, da `run_id` und
Laufzeitpunkte absichtlich verschieden sind.

**Erforderliche Präzisierung:**

- ein bereits veröffentlichtes Manifest muss bei Integritätsprüfung E3
  erreichen;
- unabhängig neu erzeugte Run Manifests verschiedener Runs dürfen
  unterschiedliche Bytes besitzen;
- deterministische Manifest-Vorabbildungen und identische persistierte
  Manifestartefakte müssen getrennt geprüft werden.

### SCR-M04 – Build-relevante Umgebungsparameter benötigen eine Allowlist

**Schweregrad:** `MAJOR`

**Betroffenes Dokument:**

- Reproducibility and Manifest Specification, Abschnitt 5.4.

**Befund:**

Der Ausdruck:

```text
relevante deterministische Umgebungsparameter
```

ist ohne Registry nicht eindeutig.

**Erforderliche Präzisierung:**

- versionierte Allowlist buildidentitätsrelevanter Umgebungsparameter;
- übrige Hostinformationen ausschließlich im Run Manifest;
- CPU-Modell und Hostname verändern nicht automatisch die Build-ID;
- Bibliotheks-, Numerik-, Locale-, Zeitzonen- und Threadparameter werden nur
  dann Teil der Build-ID, wenn das aktive Buildprofil sie als
  semantikrelevant registriert.

## 6. Redaktionell beschädigte normative Passagen

### SCR-E01 – Beschädigtes Falsifikationskriterium

**Schweregrad:** `EDITORIAL-BLOCKING`

**Dokument:**

- Regime and Gate Specification, Abschnitt 25.

Beschädigter Text:

```text
Vorteil besteht nur auf bereitset nach Gebühren und Slippage
```

Der Satz besitzt keine eindeutige Semantik und ist zu entfernen.

Die bereits vorhandenen, verständlichen Kriterien:

```text
Wirkung verschwindet nach Gebühren und Slippage
Vorteil besteht nur auf zur Auswahl verwendeten Daten
```

decken die beabsichtigte Prüfung ab.

### SCR-E02 – Beschädigte Passage zur synthetischen Regimeansicht

**Schweregrad:** `EDITORIAL-BLOCKING`

**Dokument:**

- Regime and Gate Specification, Abschnitt 27.3.

Beschädigter Text:

```text
Es darf benötigt:

- eigene Profil-ID,
- eigenen Build,
- separate Sensitivitätsanalyse.

 kanonische beobachtete Regime nicht überschreiben.
```

Verbindliche Ersatzfassung:

```text
Regime auf synthetischen Kontinuitätsdaten benötigt:

- eine eigene Profil-ID,
- einen eigenen Build,
- eine separate Sensitivitätsanalyse.

Es darf das kanonische beobachtete Regime nicht überschreiben.
```

## 7. Nichtblockierende Hinweise

### SCR-N01 – Normative Sprachmischung

Die ersten sechs Dokumente verwenden überwiegend `MUST`, `SHOULD` und `MAY`,
die Manifest-Spezifikation überwiegend `MUSS`, `SOLL` und `DARF`.

Die Bedeutung ist erklärt und aktuell nicht fachlich widersprüchlich.
Im Editorial Pass sollte die normative Sprache familienweit vereinheitlicht
werden.

### SCR-N02 – Dokumentmetadaten sind nicht vollständig vereinheitlicht

Die Manifest-Spezifikation verwendet teilweise andere Metadatenfeldnamen und
Statusformulierungen als die übrigen Dokumente.

Dies ist im Editorial Pass zu harmonisieren.

### SCR-N03 – Gate-Profil versus Gate-Modell

Die Fachspezifikation verwendet fachlich sinnvoll `gate_profile_id`.
Die übergeordnete Spezifikation verwendet `gate_model_id`.

Die Auflösung erfolgt bereits durch SCR-B02. Im Editorial Pass ist zusätzlich
zu prüfen, ob `model` ausschließlich für S5-Regimemodelle und `profile`
ausschließlich für S6-Gateprofile verwendet wird.

## 8. Korrekturmatrix

| Befund | Zu korrigierendes Dokument | Zielversion |
|---|---|---:|
| SCR-B01 | Data Pipeline Specification | 0.3.0 |
| SCR-B02 | Data Pipeline Specification | 0.3.0 |
| SCR-B03 | Data Pipeline Specification | 0.3.0 |
| SCR-B04 | Reproducibility and Manifest Specification | 0.2.0 |
| SCR-B05 | Reproducibility and Manifest Specification | 0.2.0 |
| SCR-M01 bis M04 | Reproducibility and Manifest Specification | 0.2.0 |
| SCR-E01 bis E02 | Regime and Gate Specification | 0.2.0 |

Die übrigen vier Fachspezifikationen benötigen aufgrund dieses SCR derzeit
keine wissenschaftliche Inhaltsänderung:

- Data Validation;
- Indicator;
- Signal Transformation;
- Label and Forward Return.

Sie erhalten ihren finalen SCR-Status erst nach bestandenem Familien-Re-Review.

## 9. Verbindlicher Korrekturablauf

1. Data Pipeline Specification vollständig auf Version 0.3.0 korrigieren.
2. Regime and Gate Specification vollständig auf Version 0.2.0 korrigieren.
3. Reproducibility and Manifest Specification vollständig auf Version 0.2.0
   korrigieren.
4. RCC-002-SCR-Input aus den sieben aktuellen Fassungen neu erzeugen.
5. Fokussierten Re-Review aller Befunde SCR-B01 bis SCR-M04 durchführen.
6. Zusätzlich Regression gegen die als konsistent bestätigten Formeln und
   Stufenregeln durchführen.
7. Bei bestandenem Re-Review den Status aller sieben Dokumente auf
   `Scientific Consistency Review Passed` aktualisieren.
8. Danach Architecture Integrity Review durchführen.
9. Danach unabhängige Reviews durch Gemini und Claude durchführen.

## 10. Re-Review-Akzeptanzkriterien

Der SCR-Re-Review besteht nur, wenn:

- [ ] der kanonische S2-Datensatz eindeutig beobachtet und nichtsynthetisch ist;
- [ ] synthetische Kontinuitätsansichten separat identifiziert sind;
- [ ] exakt ein verbindlicher S6-Mindestvertrag existiert;
- [ ] S7 familienweit `fwd_*`, `label_*` und `barrier_*` verwendet;
- [ ] der semantische Fingerprint den vollständigen Primärschlüssel nutzt;
- [ ] semantischer Inhalt und physische Partitionierung getrennt gehasht werden;
- [ ] JSON-Kanonisierung implementierbar eindeutig ist;
- [ ] Source-Snapshot-ID keine optionalen Identitätsbestandteile besitzt;
- [ ] E3-Anforderungen zwischen Persistenzprüfung und Cross-Run-Vergleich
  unterscheiden;
- [ ] buildidentitätsrelevante Umgebungsparameter registriert sind;
- [ ] beide beschädigten Regime-/Gate-Passagen vollständig repariert sind;
- [ ] keine neue Abweichung bei Formeln, Warm-up, Kausalität, Gate- oder
  Labelsemantik eingeführt wurde.

## 11. Reviewentscheidung

```text
Scientific Consistency Review: NOT PASSED
Architecture Integrity Review: BLOCKED
External Gemini Review: NOT YET STARTED
External Claude Review: NOT YET STARTED
Implementation Release: BLOCKED
```

Die Architektur bleibt grundsätzlich tragfähig. Der nächste zulässige Schritt
ist der kontrollierte Korrekturlauf der drei in Abschnitt 8 genannten
Dokumente. Eine Implementierung vor bestandenem SCR-Re-Review ist nicht
freigegeben.
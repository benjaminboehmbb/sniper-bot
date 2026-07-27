# RCC-002 AIR4-MIN-01 Corrected Full Specification Bundle

Enthaltene Spezifikationen: 7

Korrekturstand: AIR4-MIN-01 targeted correction 2026-07-27: PASS_WITH_APPROVED_EXCEPTIONS carve-outs in Indicator §30 and Signal Transformation §32 clarified as exhaustive (no new exception type, no automatic approval). Indicator 0.4.2->0.4.3, Signal Transformation 0.4.1->0.4.2. Mechanical dependency-citation follow-ons in Regime and Gate, Label and Forward Return (no version change), and Reproducibility and Manifest (0.7.0->0.7.1, citations + §12.3 only). Data Pipeline and Data Validation unchanged.

## Eingebettete Spezifikationsstände

| Datei | Version | Zeilen | Bytes | SHA-256 |
|---|---:|---:|---:|---|
| `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md` | `0.7.1` | 2592 | 134284 | `529f83a27c0464af0954213ffc0e81b26819bf846a1b7a6085a6b323bddf87a2` |
| `RCC_002_DATA_VALIDATION_2026-07-23.md` | `0.4.2` | 1382 | 46926 | `9bb70245d2001ee2676f63a9e89b396c9b71dc575e72da6084dd617ce41b258d` |
| `RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md` | `0.4.3` | 1751 | 51591 | `80e77f3a29e753b028d479a0a383010ce7c16804a74420f465e99eb4dcdfe70b` |
| `RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md` | `0.4.2` | 1674 | 53861 | `5981aa15c317d5675e9adc71aecd7a26dc7abbfe0f5ac45947faa993c7022a0b` |
| `RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md` | `0.5.1` | 2216 | 68324 | `ad981e2dcdc935aef1a3f6f107e0bfce4070b6926d2eb65da4fe209a31c2c346` |
| `RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md` | `0.4.1` | 2017 | 60288 | `99b68f1933859f4da1a92676e9fb6c3a8b78f25eeb2ad4b4fd42db66769751b9` |
| `RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md` | `0.7.1` | 2281 | 78142 | `20a50faf2851db7fcf85bc0c776b592f39a08259b32e7b80b80866b5d4e60619` |

---
# Eingebettetes Dokument 1 von 7

## Quelldatei: `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`

# RCC-002 Data Pipeline Specification

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Wissenschaftliche und technische Kernspezifikation |
| Dokument-ID | `RCC_002_DATA_PIPELINE_SPECIFICATION` |
| Version | 0.7.1 |
| Datum | 2026-07-23 |
| Status | SCR-005-Corrected Draft – Scientific Consistency Re-Review 006 Pending |
| Speicherort im Repository | `docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md` |
| Dateiname | `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md` |
| Geltungsbereich | Kanonische Forschungsdatenpipeline für BTCUSDT und spätere weitere Assets/Zeitebenen |
| Primäre Abhängigkeiten | `Master_Analysis_Blueprint.md`; historische BTC-Pipeline; GS-Pipeline-Artefakte; RCC-002-Nachfolgespezifikationen |
| Referenziert durch | künftige RCC-002-Implementierung; Analyse-Runner; SimTrader; Live-/Paper-Trading-Paritätsprüfung; Dataset Manifest |
| Autoritative Sprache | Englisch für Code, Schemas und Feldnamen; Deutsch für die normative Erläuterung |

### Review-Nachweis

| Review | Status | Ergebnis |
|---|---|---|
| Interne Struktur- und Konsistenzprüfung | Bestanden mit Überarbeitung | Stufenverträge, Leakage-Schutz, Qualitätsflag-Propagation, Korrekturregeln und Publication Gate ergänzt beziehungsweise präzisiert |
| Scientific Consistency Review | `RCC-002-SCR-004` bestanden | Alle in `RCC-002-SCR-004` geprüften Befunde geschlossen; erneuter fokussierter Review nach den semantisch relevanten AIR-001-Korrekturen erforderlich |
| Architecture Integrity Review | `RCC-002-AIR-001` nicht bestanden; Korrektur eingearbeitet | Version 0.6.0 korrigiert die diesem Dokument zugeordneten Teile von `AIR-001-B01`, `AIR-001-B02`, `AIR-001-B03`, `AIR-001-M01`, `AIR-001-M02`, `AIR-001-M03` und `AIR-001-m01`; dokumentübergreifender Re-Review ausstehend |
| Scientific Consistency Re-Review 005 | `RCC-002-SCR-005` nicht bestanden; Korrektur eingearbeitet | Version 0.7.0 korrigiert `SCR-005-B01`, `SCR-005-B02`, `SCR-005-M01`, `SCR-005-M02`, `SCR-005-M03` und materialisiert `AIR-005-H01`; SCR-006 ausstehend |
| C1 Patch Release | `RCC-002-C1-SCR` bestanden mit Minor Findings | Version 0.7.1: patch release: normative clarification of Canonical Row Preservation semantics (C1) via neue Untersektion 5.8. No intended behavioural change. |
| Editorial Pass | Ausstehend | Nach bestandenem Architecture Integrity Review |
| Internal Certification | Ausstehend | Nach bestandenem Editorial Pass |
| Claude Independent Architecture Review | Ausstehend | Erst nach Internal Certification |
| Gemini Independent Scientific and Adversarial Audit | Ausstehend | Erst nach bestandenem Claude-Review |
| ChatGPT Final Consolidation | Ausstehend | Erst nach abgeschlossenem Gemini-Audit |
| Baseline V1 Certified | Nicht erreicht | Erst nach abgeschlossener finaler Konsolidierung und Schließung aller wesentlichen Befunde |

## 1. Zweck

Dieses Dokument definiert die übergeordnete Architektur, die verbindlichen
Schnittstellen und die wissenschaftlichen Kontrollanforderungen der
RCC-002-Datenpipeline.

Die Pipeline muss aus historischen und aktuellen OHLCV-Rohdaten einen
reproduzierbaren, kausalen und manifestgebundenen Datensatz erzeugen, der
gleichzeitig verwendbar ist für:

- wissenschaftliche Strategieforschung,
- deterministische Backtests,
- Paper Trading,
- spätere Live-Trading-Parität,
- Regime- und Zustandsanalysen,
- Forward-Return- und Label-Analysen,
- unabhängige Reproduktion und Auditierung.

Dieses Dokument definiert bewusst nicht sämtliche mathematischen
Schwellenwerte und Versionen einzelner Indikatoren, Signaltransformationen,
Regimemodelle oder Labels. Diese werden in nachgeordneten Spezifikationen
festgelegt. Dieses Dokument definiert jedoch verbindlich, wie diese
Komponenten zusammenwirken müssen.

## 2. Normative Begriffe

Die Begriffe `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT` und `MAY` sind
normativ zu verstehen:

- `MUST`: zwingende Anforderung;
- `MUST NOT`: zwingendes Verbot;
- `SHOULD`: begründeter Standardfall;
- `SHOULD NOT`: nur mit dokumentierter Ausnahme zulässig;
- `MAY`: optionale, aber zulässige Ausprägung.

## 3. Geltungsbereich

RCC-002 umfasst die vollständige Datenverarbeitung von unveränderten
Quellartefakten bis zu konsumfertigen Forschungs-, Backtest- und
Live-/Paper-Views.

Enthalten sind:

1. Rohdatenaufnahme und Quellidentität.
2. Normalisierung von Zeit, Schema und Datentypen.
3. Datenvalidierung und kontrollierte Lückenbehandlung.
4. Berechnung kausaler Rohindikatoren.
5. Versionierte Signaltransformation.
6. Reine Marktregimeklassifikation.
7. Getrennte Long-/Short-Handels-Gates.
8. Forward Returns und Forschungslabels.
9. Export in manifestgebundene Artefakte.
10. Qualitäts-, Reproduzierbarkeits- und Publication Gates.

Nicht enthalten sind:

- konkrete Entry- und Exit-Entscheidungen einer Strategie;
- Positionsgrößensteuerung;
- Order-Routing;
- Börsenadapter;
- Live-Execution-State;
- Portfoliosteuerung;
- Strategieparameteroptimierung.

Diese nachgelagerten Systeme dürfen RCC-002-Artefakte konsumieren, aber ihre
Entscheidungslogik darf nicht rückwirkend in die Datenpipeline einfließen.

## 4. Evidenzbasis und Legacy-Befunde

RCC-002 basiert auf der Rekonstruktion mindestens zweier historischer
Pipeline-Generationen.

### 4.1 Historische BTC-Pipeline

Verifizierter Datenfluss:

```text
data/btcusdt_1m_spot_filled.csv
→ build_price_data_with_signals.py
→ data/price_data_with_signals.csv
→ tools/add_regime.py
→ data/price_data_with_signals_regime.csv
```

Verifizierte Eigenschaften:

- 2.721.034 Zeilen der zwölf binären Signalspalten wurden gegen den
  historischen Builder geprüft.
- Ergebnis: null Abweichungen.
- 1.048.575 Zeilen der vier Regimefelder wurden gegen `tools/add_regime.py`
  mit `adx_min=15.0` geprüft.
- Ergebnis: null Abweichungen.

Die historischen Signale waren:

```text
rsi_signal
macd_signal
bollinger_signal
ma200_signal
stoch_signal
atr_signal
ema50_signal
adx_signal
cci_signal
mfi_signal
obv_signal
roc_signal
```

Die historische Regimelogik war:

```text
bull:
close > ma200
ema50 > ma200
roc > 0
adx >= 15

bear:
close < ma200
ema50 < ma200
roc < 0
adx >= 15

sonst:
side
```

### 4.2 GS-Pipeline

Die spätere GS-Generation führte unter anderem ein:

- kontinuierliche Signalwerte im Bereich `[-1, +1]`;
- stärkere Trennung von Rohindikator und Signaltransformation;
- vereinfachte Regimeklassifikation;
- getrennte Felder `allow_long` und `allow_short`;
- zusätzliche Forward-Return-Felder;
- assetübergreifende Verwendung.

Der ursprüngliche BTC-GS-Datensatz ist nicht vollständig verfügbar. Deshalb
darf RCC-002 keine nicht verifizierbare Behauptung über dessen exakte
historische Erzeugung als gesicherte Tatsache behandeln.

### 4.3 Konsequenz für RCC-002

RCC-002 übernimmt weder die historische BTC-Pipeline noch die GS-Pipeline
unverändert.

Stattdessen gilt:

- Legacy-Logik wird als versionierbare Referenz erhalten.
- Neue kanonische Logik wird modular spezifiziert.
- Regime und Handels-Gates werden getrennt.
- Datenqualität und Warm-up werden explizit modelliert.
- Labels werden strikt von Live-/Paper-Features getrennt.
- jeder Build wird vollständig manifestiert.

## 5. Architekturprinzipien

### 5.1 Trennung der Verantwortlichkeiten

Jede Pipeline-Stufe besitzt genau eine primäre Verantwortung.

Eine Stufe darf keine fachlich fremde Entscheidung implizit übernehmen.

Beispiele:

- ADX darf als Rohindikator berechnet werden.
- Ob ADX einen Gate-Zustand beeinflusst, gehört in ein Gate-Profil.
- Forward Returns dürfen in S7 berechnet werden.
- Sie dürfen niemals in S0 bis S6 einfließen.

### 5.2 Determinismus

Identische Eingabebytes, identische Codeversion und identische
`semantic_build_configuration` müssen dieselben semantischen Ausgaben
erzeugen.

Zulässige physische Unterschiede, etwa Parquet-Metadaten oder
Kompressionsdetails, müssen durch getrennte semantische und physische Hashes
erkennbar sein.

Nichtdeterministische Operationen sind unzulässig, sofern sie nicht:

- explizit registriert,
- mit festem Seed versehen,
- vollständig manifestiert und
- durch Reproduktionstests abgesichert sind.

### 5.3 Point-in-Time-Korrektheit

Für jede Zeile mit Entscheidungszeitpunkt `t` dürfen S0 bis S6 ausschließlich
Informationen verwenden, die spätestens zu `t` verfügbar waren.

Unzulässig sind insbesondere:

- zentrierte Rolling Windows;
- rückwirkend berechnete Glättungen mit Zukunftswerten;
- Backfill aus zukünftigen Zeilen;
- interpolierte Marktwerte über Lücken;
- normalisierte Features mit Statistiken aus dem Gesamtdatensatz;
- Regimepersistenz, die zukünftige Zustände zur rückwirkenden Glättung nutzt.

### 5.4 Fail-Closed

Wenn eine Pflichtinformation ungültig, unbekannt, nicht warmgelaufen oder
nicht reproduzierbar ist, muss die betroffene Stufe fail-closed reagieren.

Für Handels-Gates bedeutet dies grundsätzlich:

```text
allow_long = false
allow_short = false
```

Eine Ausnahme ist nur über ein explizites, versioniertes Forschungsprofil
zulässig und darf niemals stillschweigend aktiviert werden.

### 5.5 Unveränderlichkeit und Lineage

Quellartefakte, Zwischenartefakte und veröffentlichte Datensätze dürfen nach
ihrer Veröffentlichung nicht still überschrieben werden.

Eine Korrektur erzeugt:

- ein neues versioniertes Artefakt;
- eine neue Identität;
- eine dokumentierte Eltern-Kind-Beziehung;
- einen Korrekturgrund;
- einen neuen Manifestnachweis.

### 5.6 Konfigurierbarkeit ohne implizite Semantik

Parameter müssen in versionierten Konfigurationen liegen.

Dateinamen, Verzeichnisnamen, Hostnamen oder Ausführungsreihenfolge dürfen
keine versteckte fachliche Bedeutung tragen.

Jeder Build muss mindestens folgende Identitäten referenzieren:

- Datenprofil;
- Indikatorprofil;
- Signalprofil;
- Regimeprofil;
- Gate-Profil;
- Labelprofil;
- Manifestprofil.

RCC-002 trennt Konfiguration normativ in zwei Namensräume.

#### 5.6.1 Semantische Build-Konfiguration

`semantic_build_configuration` enthält ausschließlich Einstellungen, die
Werte, Gültigkeit, Zeilenmitgliedschaft, fachliche Bedeutung oder logische
Schemas eines Builds beeinflussen.

Mindestens eingeschlossen sind:

- Quellen- und Konsolidierungspolitik;
- `source_expectations` mit `timezone`, `expected_start` und `expected_end`;
- Datenvalidierungs- und Qualitätsregeln;
- Segmentierungs- und Resetregeln;
- Indikatorprofile;
- Signalprofile;
- Regimemodelle;
- Gate-Profile;
- Horizon-, Kosten- und Barrier-Profile;
- numerische Präzisions-, Rundungs- und Toleranzprofile;
- logische Schema- und Viewversionen.

Die kanonische Vorabbildung wird als
`semantic_build_configuration_sha256` gehasht.

Jede Änderung von `semantic_build_configuration_sha256` erzeugt einen neuen
`build_id` und einen neuen `dataset_id`. Dies gilt auch dann, wenn der
materialisierte Tabelleninhalt zufällig identisch bleibt.

#### 5.6.2 Physische Veröffentlichungskonfiguration

`physical_publication_configuration` enthält ausschließlich Einstellungen
der Speicherung und Verpackung, die den semantischen Tabelleninhalt nicht
verändern.

Mindestens eingeschlossen sind:

- Partitions- und Dateigrenzen;
- Row-Group-Profil;
- Kompressionsalgorithmus und Kompressionsstufe;
- Dictionary-Encoding;
- Writerprofil und Writer-Version;
- Container-Metadaten;
- physische Verzeichnisstruktur.

Die kanonische Vorabbildung wird als
`physical_publication_configuration_sha256` gehasht.

Dieser Hash darf weder `build_id` noch `dataset_id` beeinflussen. Er
beeinflusst:

- `physical_layout_sha256`;
- `artifact_id`;
- `dataset_artifact_set_id`.

Eine rein physische Neuverpackung:

- behält `build_id`;
- behält `dataset_id`;
- erzeugt neue physische Artefaktidentitäten;
- erzeugt eine neue `dataset_artifact_set_id`.

#### 5.6.3 Verbot unklassifizierter Konfiguration

Jede wirksame Konfigurationsoption muss genau einem der beiden Namensräume
zugeordnet sein.

Unklassifizierte Optionen sind in kanonischen Builds unzulässig.

Run-Metadaten wie Hostname, Benutzername, Startzeitpunkt, temporärer Pfad oder
zufällige Laufzeit-ID gehören in keinen der beiden Konfigurationshashes.

### 5.7 Qualitätsflag-Propagation

Qualitäts- und Gültigkeitsinformationen dürfen nicht beim Übergang zwischen
Pipeline-Stufen verloren gehen.

Jede nachgelagerte Stufe muss relevante vorgelagerte Felder entweder:

1. unverändert weiterführen oder
2. in eine dokumentierte, strengere Gültigkeitsentscheidung überführen.

Eine Stufe darf einen ungültigen oder unbekannten Eingangszustand nicht
stillschweigend als gültigen neutralen Zustand interpretieren.

### 5.8 Kanonisches Row-Preservation-Prinzip

Jede Zeile, die in die kanonische Pipeline aufgenommen wurde, muss ihre
kanonische Row Identity über alle nachgelagerten Stufen hinweg bewahren.

Pipeline-Stufen dürfen kanonische Zeilen aufgrund von
`quality_gate_pass=false` weder stillschweigend entfernen noch unterdrücken,
duplizieren, zusammenführen oder umordnen.

`quality_gate_pass` bestimmt die semantische Verwendbarkeit einer Zeile,
nicht ihre kanonische Existenz.

Zeilen mit `quality_gate_pass=false` müssen im kanonischen Artefakt
verbleiben und werden durch deterministische fail-closed Zustände
repräsentiert.

Zulässige Reaktionen sind insbesondere:

- ungültige oder Null-Indikatorwerte;
- ungültige Signalwerte;
- nachgelagerte Gate-Zustände wie `BLOCK_BOTH`.

Eine Abweichung von der Row Preservation ist ausschließlich durch einen
ausdrücklich normierten vollständigen Build-Abbruch oder eine
Artefakt-Quarantäne zulässig. Beide wirken auf das gesamte Artefakt oder den
gesamten Build, nicht auf einzelne Zeilen.

Publication Gates regeln die Veröffentlichbarkeit und semantische Gültigkeit
abgeleiteter Werte. Sie dürfen nicht implizit als Row-Deletion-Regeln
ausgelegt werden.

## 6. Kanonischer Datenfluss

Die RCC-002-Pipeline besteht aus:

1. `S0_SOURCE`: unveränderte Quellartefakte und Quellenmanifest.
2. `S1_NORMALIZED`: kanonische Zeit-, Feld- und Typnormalisierung.
3. `S2_VALIDATED`: validierte Zeitreihe und Qualitätsflags.
4. `S3_INDICATORS`: Rohindikatoren, Gültigkeitsfelder und Reason Codes.
5. `S4_SIGNALS`: versionierte Signaltransformationen.
6. `S5_REGIMES`: reine Marktklassifikationen.
7. `S6_GATES`: getrennte Handelsfreigaben und Gate-Gründe.
8. `S7_LABELS`: Forward Returns und Forschungslabels.
9. `S8_EXPORT`: konsumfertige, manifestgebundene Datensätze.

### 6.1 Verbindliche Stufenverträge

Jede Stufe muss definieren:

- akzeptierte Eingabeschemaversion;
- erzeugte Ausgabeschemaversion;
- Pflichtfelder;
- Datentypen;
- Primärschlüssel;
- Sortierungsanforderung;
- Warm-up-Regel;
- Null- und Invaliditätssemantik;
- Fehlerverhalten;
- Zeilenzahl-Invariante;
- Komponenten-ID und Komponenten-Version.

Eine Stufe darf Eingaben mit unbekannter oder inkompatibler Schemaversion
nicht stillschweigend verarbeiten.

### 6.2 Kanonisches Stufenschemaregister

Jede RCC-002-Schemaidentität verwendet genau drei Darstellungen:

```text
schema_id=<unversionierte ID>
schema_version=<SemVer ohne weitere ID-Bestandteile>
schema_ref=<schema_id>/<schema_version>
```

Beispiel:

```text
schema_id=rcc002.stage.s3-indicators
schema_version=1.0.0
schema_ref=rcc002.stage.s3-indicators/1.0.0
```

`schema_ref` wird ausschließlich deterministisch aus `schema_id` und
`schema_version` abgeleitet. Eine Version im Wert von `schema_id` ist
unzulässig. Diese Regel gilt für Stage-, View-, State- und Manifestschemas,
Zeilenmetadaten, Stage Manifests, Registry-Einträge und
Kompatibilitätsprüfungen.

Folgende logische Schemaidentitäten sind für die erste RCC-002-Baseline
reserviert:

| Stufe | `schema_id` | `schema_version` | `schema_ref` |
|---|---|---|---|
| `S0_SOURCE` | `rcc002.stage.s0-source` | `1.0.0` | `rcc002.stage.s0-source/1.0.0` |
| `S1_NORMALIZED` | `rcc002.stage.s1-normalized` | `1.0.0` | `rcc002.stage.s1-normalized/1.0.0` |
| `S2_VALIDATED` | `rcc002.stage.s2-validated` | `1.0.0` | `rcc002.stage.s2-validated/1.0.0` |
| `S3_INDICATORS` | `rcc002.stage.s3-indicators` | `1.0.0` | `rcc002.stage.s3-indicators/1.0.0` |
| `S4_SIGNALS` | `rcc002.stage.s4-signals` | `1.0.0` | `rcc002.stage.s4-signals/1.0.0` |
| `S5_REGIMES` | `rcc002.stage.s5-regimes` | `1.0.0` | `rcc002.stage.s5-regimes/1.0.0` |
| `S6_GATES` | `rcc002.stage.s6-gates` | `1.0.0` | `rcc002.stage.s6-gates/1.0.0` |
| `S7_LABELS` | `rcc002.stage.s7-labels` | `1.0.0` | `rcc002.stage.s7-labels/1.0.0` |

`S8_EXPORT` akzeptiert eine freigegebene Kombination registrierter
Stufenschemareferenzen und erzeugt ein registriertes View-Schema mit derselben
dreiteiligen Identitätskonvention.

Die S7-Berechnung darf S0-bis-S6-Felder durchreichen, aber nicht verändern.
Die S7-Schema-ID kennzeichnet die zusätzliche Zukunftsinformation.

Die Schema-ID umfasst:

- kanonische Feldnamen;
- Datentypen;
- Nullbarkeit;
- Feldreihenfolge für kanonische Fingerprints;
- Primärschlüssel;
- Sortierungsvertrag;
- Erzeugerstufe jedes Feldes;
- Enum- und Reason-Code-Register;
- Kompatibilitätsregeln.

Eine Änderung dieser Eigenschaften benötigt mindestens eine neue
Schemaversion.

### 6.3 Schemaeigentum und Erweiterungsfelder

Jedes Feld besitzt genau eine normative Erzeugerstufe.

Nachgelagerte Stufen dürfen ein Feld:

- unverändert durchreichen;
- in einer neuen, eindeutig benannten Ableitung verwenden;
- aufgrund einer strengeren eigenen Regel zusätzlich invalidieren.

Sie dürfen weder Wert noch Semantik eines vorgelagerten Feldes unter
demselben Namen verändern.

Profilabhängige Erweiterungsfelder sind nur zulässig, wenn:

- ihr Feldname registriert ist;
- Datentyp und Nullbarkeit registriert sind;
- ihre Erzeugerstufe feststeht;
- ihr Profil und ihre Version manifestiert sind;
- die S8-View-Allowlist sie ausdrücklich zulässt.

### 6.4 Kompatibilitätsregeln

Für logische Stufenschemas gilt semantische Versionierung:

- Patch: redaktionelle oder nichtsemantische Metadatenkorrektur;
- Minor: additive optionale Felder ohne Änderung bestehender Semantik;
- Major: Entfernung, Umbenennung, Typänderung, neue Nullsemantik,
  Schlüsseländerung oder fachliche Bedeutungsänderung.

Eine konsumierende Stufe darf eine neuere Minor-Version nur akzeptieren, wenn
ihre registrierte Kompatibilitätsregel dies ausdrücklich erlaubt.

Unbekannte Major-Versionen sind fail-closed abzulehnen.

## 7. Stufenspezifikation

### 7.1 S0_SOURCE – Rohdatenaufnahme

S0 besteht aus zwei getrennten normativen Objekten:

1. unveränderten Quellartefakten;
2. genau einem zugehörigen `source_manifest`.

Quellbytes werden nicht modifiziert. Archiv- oder Kompressionsformate bleiben
als Quellartefakt erhalten. Dekomprimierte Ableitungen erhalten eigene
Artefaktidentitäten. Die Quellartefakte selbst besitzen kein zusätzlich
erfundenes RCC-Zeilenschema.

Der folgende Vertrag ist ausschließlich der Feldvertrag des
`source_manifest`:

| Feld | Logischer Typ | Nullbar | Eigentümerobjekt | Bedeutung |
|---|---|:---:|---|---|
| `source_snapshot_id` | UTF-8-String | Nein | `source_manifest` | Deterministische Identität der Quellenfassung |
| `provider` | UTF-8-String | Nein | `source_manifest` | Kanonische Providerkennung |
| `market_type` | UTF-8-String | Nein | `source_manifest` | Registrierter Markttyp |
| `symbol` | UTF-8-String | Nein | `source_manifest` | Registriertes Symbol |
| `interval` | UTF-8-String | Nein | `source_manifest` | Registriertes Datenintervall |
| `retrieved_at_utc` | UTC-Timestamp in Millisekunden | Nein | `source_manifest` | Provenienzzeitpunkt des Abrufs; nicht Teil der Source-ID |
| `source_file_name` | UTF-8-String | Nein | `source_manifest` | Ursprünglicher Dateiname ohne lokale Pfadsemantik |
| `source_byte_sha256` | 64-stelliger Lowercase-Hex-String | Nein | `source_manifest` | SHA-256 der unveränderten Quellbytes |
| `source_revision` | UTF-8-String | Ja | `source_manifest` | Providerrevision, falls verfügbar |
| `source_format` | UTF-8-String | Nein | `source_manifest` | Registrierte Format- und Schemafamilie |
| `source_location` | UTF-8-String | Nein | `source_manifest` | Dokumentierte Herkunft oder portable Quellenreferenz |
| `license_or_terms_ref` | UTF-8-String | Ja | `source_manifest` | Referenz auf Nutzungsbedingungen |

`provider` und `retrieved_at_utc` sind die einzigen kanonischen Feldnamen.
`source_provider` und `source_retrieved_at_utc` sind ausschließlich zulässige
Legacy-Eingangsaliasse mit folgender gerichteter Migrationsabbildung:

```text
source_provider           -> provider
source_retrieved_at_utc   -> retrieved_at_utc
```

Die umgekehrte Abbildung ist unzulässig. Legacy-Aliasse dürfen nur vor
Erzeugung des kanonischen `source_manifest` durch ein versioniertes
Migrationsprofil akzeptiert werden und erscheinen weder im kanonischen
Source Manifest noch im S1-Ausgang.

Die folgenden drei Felder gehören ausschließlich zum normativen Objekt
`semantic_build_configuration.source_expectations`:

| Feld | Logischer Typ | Nullbar | Bedeutung |
|---|---|:---:|---|
| `timezone` | UTF-8-String | Nein | deklarierte Zeitzone für die deterministische Interpretation nicht eindeutig zonierter Quellzeiten |
| `expected_start` | UTC-Timestamp in Millisekunden | Nein | erwarteter erster Intervallbeginn des Validierungsumfangs |
| `expected_end` | UTC-Timestamp in Millisekunden | Nein | erwarteter letzter Intervallbeginn des Validierungsumfangs |

Sie sind keine S0-Zeilenfelder und keine Source-Manifest-Felder. Ein
Validierungsauftrag referenziert die unveränderte
`semantic_build_configuration`; er darf keine konkurrierenden Werte für diese
drei Felder enthalten.

Für die Identitätswirkung gilt:

- `source_snapshot_id` wird aus den quellinhaltlichen und semantischen
  Abrufmerkmalen einschließlich `provider`, `market_type`, `symbol`,
  `interval`, geordneter Quellbyte-Hashes, `source_revision` und
  registrierter semantischer Abrufparameter gebildet;
- `retrieved_at_utc`, lokale Pfade, Hostdaten und Transport-Retrys beeinflussen
  `source_snapshot_id` nicht;
- `timezone`, `expected_start` und `expected_end` gehen über
  `semantic_build_configuration_sha256` in `build_id` und `dataset_id` ein,
  nicht in `source_snapshot_id`.

`source_revision` darf null sein, wenn der Provider keine Revision ausweist.
Dieser Zustand muss im Source Manifest explizit dokumentiert werden.

### 7.2 S1_NORMALIZED – Normalisierung

S1 normalisiert:

- Zeitstempel nach UTC;
- Feldnamen;
- Datentypen;
- Intervallbezeichnung;
- Markttyp;
- Symbolbezeichnung;
- numerische Darstellung.

Der kanonische Primärschlüssel lautet:

```text
market_type
symbol
interval
open_time
```

Wenn mehrere Provider innerhalb eines noch nicht konsolidierten Datensatzes
vorkommen, wird `provider` unmittelbar vor `market_type` Teil des
Primärschlüssels und der Sortierreihenfolge.

Der kanonische S1-Zeilenvertrag enthält mindestens:

| Feld | Logischer Typ | Nullbar | Erzeugerstufe |
|---|---|:---:|---|
| `source_snapshot_id` | UTF-8-String | Nein | S0 |
| `source_row_id` | UTF-8-String | Nein | S1 |
| `provider` | UTF-8-String | Nein | S0/S1 |
| `market_type` | UTF-8-String | Nein | S0/S1 |
| `symbol` | UTF-8-String | Nein | S0/S1 |
| `interval` | UTF-8-String | Nein | S0/S1 |
| `open_time` | UTC-Timestamp in Millisekunden | Nein | S1 |
| `close_time` | UTC-Timestamp in Millisekunden | Nein | S1 |
| `open` | Float64 | Nein | S1 |
| `high` | Float64 | Nein | S1 |
| `low` | Float64 | Nein | S1 |
| `close` | Float64 | Nein | S1 |
| `volume` | Float64 | Nein | S1 |

`source_row_id` identifiziert die normalisierte Zeile innerhalb des
`source_snapshot_id` deterministisch. Seine Vorabbildung und
Kanonisierungsregel müssen versioniert sein.

Quellfelder wie Quote Volume, Trade Count oder Taker Volume sind nur dann
kanonische Erweiterungsfelder, wenn sie mit Datentyp, Nullsemantik und
Providerabbildung im S1-Schema registriert sind.

Für 1-Minuten-Bars gilt:

```text
close_time = open_time + 60 Sekunden - 1 Millisekunde
```

sofern die Quellsemantik dieselbe geschlossene Kerzenkonvention verwendet.

S1 darf:

- keine fehlenden Bars erzeugen;
- keine Preise interpolieren;
- keine Duplikate willkürlich entfernen;
- keine Indikatoren berechnen.

### 7.3 S2_VALIDATED – Validierung und kanonische Zeitreihe

S2 führt mindestens folgende Prüfungen aus:

- Primärschlüsseleindeutigkeit;
- strenge Sortierung;
- Intervallausrichtung;
- Zeitlückenerkennung;
- Duplikaterkennung;
- OHLC-Konsistenz;
- nichtnegative Volumina;
- endliche numerische Werte;
- Quellüberlappungen;
- Providerkonflikte;
- monotone Marktsegmentbildung.

Die kanonische S2-Lückenpolitik lautet:

- S2 darf fehlende Markt-Bars nicht als echte OHLCV-Beobachtungen erzeugen.
- Die kanonische validierte Marktansicht bleibt beobachtungsbasiert und
  enthält ausschließlich reale oder nach einer expliziten
  Quellenkorrekturspolitik ausgewählte Quell-Bars.
- Jede zeitliche Unterbrechung erzeugt eine neue `market_segment_id`.
- Rolling Windows und zeitabhängige Transformationen dürfen
  `market_segment_id`-Grenzen nicht überschreiten.
- Ein optionales regelmäßiges Zeitraster darf ausschließlich als getrennte
  Diagnose- oder Monitoring-View erzeugt werden.
- Synthetische Rasterzeilen müssen mindestens
  `quality_is_observed=false`, `quality_is_synthetic=true`,
  `quality_market_values_valid=false` und `quality_gate_pass=false` tragen.
- Synthetische Rasterzeilen dürfen keine erfundenen OHLCV-Werte als gültige
  Marktbeobachtung ausweisen und dürfen nicht in kanonische
  Forschungs-, Backtest-, Paper- oder Live-Views gelangen.

Der kanonische S2-Qualitätsvertrag lautet:

| Feld | Logischer Typ | Nullbar | Bedeutung |
|---|---|:---:|---|
| `market_segment_id` | UTF-8-String | Nein | Maximale zeitlich zusammenhängende beobachtete Marktsequenz |
| `quality_is_observed` | Boolean | Nein | Zeile stammt aus einer beobachteten Quellkerze |
| `quality_is_synthetic` | Boolean | Nein | Zeile wurde ausschließlich für eine getrennte Diagnoseansicht erzeugt |
| `quality_has_source_conflict` | Boolean | Nein | Aktiver, nicht durch eine genehmigte deterministische Regel aufgelöster Quellkonflikt |
| `quality_gap_before` | Boolean | Nein | Mindestens ein erwartetes Intervall vor der Zeile fehlt |
| `quality_gap_after` | Boolean | Nein | Mindestens ein erwartetes Intervall nach der Zeile fehlt |
| `quality_timestamp_valid` | Boolean | Nein | Zeitstempel und Intervallausrichtung sind gültig |
| `quality_ohlc_valid` | Boolean | Nein | OHLC-Invarianten sind erfüllt |
| `quality_volume_valid` | Boolean | Nein | Volumen ist endlich und nicht negativ |
| `quality_market_values_valid` | Boolean | Nein | Sämtliche kanonischen Marktpflichtwerte sind gültig |
| `quality_status` | Enum | Nein | `PASS`, `WARN`, `ERROR` oder `CRITICAL` |
| `quality_reason_codes` | Geordnete Liste aus UTF-8-Strings | Nein | Vollständige maschinenlesbare Qualitätsgründe |
| `quality_rule_version` | UTF-8-String | Nein | Version des angewandten Qualitätsregelwerks |
| `quality_gate_pass` | Boolean | Nein | Verbindliche S2-Freigabe für qualitätsgesicherte nachgelagerte Nutzung |

Andere Namen wie `segment_id`, `is_observed_bar`, `synthetic_bar`,
`source_conflict`, `market_values_valid`, `quality_reason_mask` oder
`quality_anomaly_flags` sind keine parallelen kanonischen Felder.

Historische Namen dürfen nur über eine versionierte Migrationsabbildung in
den kanonischen Vertrag überführt werden.

#### 7.3.1 Bildung der `market_segment_id`

Eine neue `market_segment_id` beginnt:

- am Anfang jeder Kombination aus `market_type`, `symbol` und `interval`;
- nach jeder Abweichung vom exakt erwarteten nächsten `open_time`;
- nach einer Änderung der kanonischen Marktidentität;
- nach einer ausdrücklich genehmigten Segment-Resetregel.

Ein ungültiger OHLC- oder Volumenwert ändert nicht rückwirkend die zeitliche
Marktsegmentdefinition. Er setzt jedoch `quality_gate_pass=false`.

`indicator_segment_id` wird erst in S3 erzeugt. Die ID verfeinert die
`market_segment_id`, indem sie zusätzlich nach ungültigen Pflichtinputs oder
rekursiven State Resets neu beginnt.

S7-Zukunftsfenster dürfen nur Bars derselben `market_segment_id` verwenden.
Zusätzlich müssen sämtliche vom jeweiligen Labelprofil benötigten
Zukunftswerte gültig und beobachtet sein.

#### 7.3.2 Bildung von `quality_gate_pass`

`quality_gate_pass=true` gilt genau dann, wenn:

- `quality_is_observed=true`;
- `quality_is_synthetic=false`;
- `quality_has_source_conflict=false`;
- `quality_timestamp_valid=true`;
- `quality_ohlc_valid=true`;
- `quality_volume_valid=true`;
- `quality_market_values_valid=true`;
- kein Reason Code mit Buildwirkung `ERROR` oder `CRITICAL` aktiv ist;
- jeder aktive `WARN` durch das versionierte Qualitätsprofil ausdrücklich als
  nicht blockierend klassifiziert ist.

In jedem anderen Fall gilt `quality_gate_pass=false`.

Wurde ein Quellkonflikt durch eine genehmigte deterministische Regel
aufgelöst, gilt für die ausgewählte kanonische Zeile
`quality_has_source_conflict=false`. Die ursprüngliche Kollision, alle
Kandidaten, die Auswahlregel und der zugehörige Reason Code bleiben im
Validierungsbericht und in der Lineage erhalten.

`data_gate_pass` in S6 übernimmt für jeden schema-, schlüssel-, sortierungs-
und segmentgültigen Eingang exakt `quality_gate_pass`. Verletzungen dieser
Strukturverträge sind stageweite Eingangsfehler und erzeugen keine kanonische
S6-Zeile.

S2 darf Quellkonflikte nicht still durch „letzte Zeile gewinnt“ lösen.

Jede automatische Auswahlregel muss:

- explizit konfiguriert;
- deterministisch;
- manifestiert;
- separat testbar sein.

### 7.4 S3_INDICATORS – Indikatorberechnung

S3 berechnet ausschließlich Rohindikatoren und deren Gültigkeitszustände.

S3 muss:

- nur S2-freigegebene Marktwerte verwenden;
- innerhalb einer `indicator_segment_id` berechnen;
- Warm-up je Indikator explizit ausweisen;
- jeden Indikator mit eindeutiger ID und Version berechnen;
- Formeln und Parameter in der Indicator Specification referenzieren;
- numerische Bibliotheks- und Versionsabhängigkeiten dokumentieren.

S3 darf keine Handelsfreigaben oder Forward Labels erzeugen.

Für jeden Indikator `x` sind mindestens vorgesehen:

```text
x
x_valid
x_warmup_complete
x_reason_codes
```

`x_reason_codes` ist eine geordnete maschinenlesbare Liste.

Bei `x_valid=false` darf `x` keinen scheinbar gültigen neutralen Ersatzwert
enthalten.

Zusätzlich erzeugt S3 mindestens:

```text
indicator_profile_id
indicator_profile_version
indicator_schema_id
indicator_schema_version
indicator_schema_ref
indicator_segment_id
```

`indicator_segment_id` beginnt neu:

- an jeder `market_segment_id`-Grenze;
- nach einem ungültigen Pflichtinput;
- nach einem expliziten rekursiven State Reset.

Sie darf eine `market_segment_id` verfeinern, aber niemals mehrere
`market_segment_id`-Werte zusammenführen.

Falls mehrere Implementierungen desselben Indikators unterstützt werden,
müssen sie unterschiedliche Komponenten-IDs besitzen.

### 7.5 S4_SIGNALS – Signaltransformation

S4 transformiert Rohindikatoren in standardisierte Signale.

RCC-002 muss mindestens zwei klar getrennte Signalprofilklassen unterstützen:

1. eine versionierte Legacy-Reproduktion binärer Signale;
2. ein kanonisches kontinuierliches Signalprofil.

Zulässiger Wertebereich kontinuierlicher Richtungssignale:

```text
-1.0 <= signal <= 1.0
```

Dabei gilt:

- `+1`: maximal bullische Ausprägung;
- `0`: neutral;
- `-1`: maximal bearische Ausprägung.

Nichtdirektionale Größen wie ATR oder ADX dürfen nicht ohne explizite
Transformation als Richtungssignal bezeichnet werden.

Ein nichtdirektionales Signal muss semantisch getrennt werden, beispielsweise:

```text
atr_quality
trend_strength
volatility_state
```

Jede Signaltransformation muss:

- kausal;
- monoton oder ausdrücklich als nichtmonoton dokumentiert;
- begrenzt;
- null- und invaliditätssicher;
- versioniert;
- unabhängig testbar sein.

S4 erzeugt zusätzlich mindestens:

```text
signal_profile_id
signal_profile_version
signal_schema_id
signal_schema_version
signal_schema_ref
```

Für jedes Signal `y` erzeugt S4 zusätzlich:

```text
y_valid
y_reason_codes
```

Ein einziges globales Gültigkeitsfeld darf unterschiedliche
Signalgültigkeiten nicht verdecken.

S4 behält `market_segment_id` und `indicator_segment_id` unverändert bei.

### 7.6 S5_REGIMES – Marktklassifikation

S5 beschreibt den Markt, nicht die Strategieentscheidung.

Jedes Regimemodell muss:

- eine Modell-ID und Version besitzen;
- ausschließlich S0-bis-S4-Daten verwenden;
- kausal sein;
- unbekannte und ungültige Zustände explizit ausweisen;
- Rohzustand und gegebenenfalls persistierten Zustand trennen;
- seine Übergangslogik dokumentieren.

Der kanonische serialisierte S5-Zustandsraum lautet:

```text
BULL
SIDE
BEAR
UNKNOWN
```

`BULL`, `SIDE` und `BEAR` sind gültige Marktklassen.

`UNKNOWN` ist ausschließlich ein Invalid-/Unavailable-Zustand. Er darf nicht
als fachlich neutrales `SIDE` behandelt werden.

Ein zusätzlicher S5-Regimewert `INVALID` ist nicht zulässig. Die
Invaliditätsursache wird durch `regime_valid=false` und
`regime_reason_codes` ausgedrückt.

S5 erzeugt mindestens:

```text
regime_raw
regime_effective
regime_candidate
regime_candidate_count
regime_transition_flag
regime_transition_from
regime_transition_to
ma200_slope_1440_pct
trend_strength
volatility_relative
regime_model_id
regime_model_version
regime_schema_id
regime_schema_version
regime_schema_ref
regime_valid
regime_reason_codes
```

Reason Codes werden als geordnete maschinenlesbare Liste gespeichert.

Historische BTC- und GS-Regimelogiken bleiben als reproduzierbare
Vergleichsmodelle zulässig, gelten aber nicht automatisch als RCC-002-Standard.

### 7.7 S6_GATES – Handelsfreigaben

S6 muss Marktdatenqualität und das gewählte registrierte Gate-Profil in
getrennte Long-/Short-Entscheidungsfelder überführen.

Vor jeder zeilenweisen S6-Auswertung MUSS der gesamte S5-Eingang den
registrierten Schema-, Primärschlüssel-, Sortierungs- und Segmentvertrag
erfüllen. Eine Verletzung ist ein stageweiter Eingangsfehler, bricht S6 ab und
erzeugt keine kanonische S6-Zeile.

Für jeden strukturell gültigen S6-Eingang gilt ausschließlich:

```text
data_gate_pass = quality_gate_pass
```

Die normative Wahrheitstabelle lautet:

| Strukturvertrag | `quality_gate_pass` | Profilpflichtinputs | Ergebnis |
|---|:---:|---|---|
| ungültig | beliebig | nicht ausgewertet | Stage-Abbruch; keine S6-Zeile |
| gültig | `false` | nicht ausgewertet | `data_gate_pass=false`; `gate_valid=true`; beide Richtungen `false`; `gate_state=BLOCK_BOTH` |
| gültig | `true` | gültig | `data_gate_pass=true`; profilspezifische Auswertung; `gate_valid=true`; `gate_state` aus den beiden Richtungsentscheidungen |
| gültig | `true` | ungültig | `data_gate_pass=true`; `gate_valid=false`; beide Richtungen `false`; `gate_state=INVALID` |

Ein gültiges `BLOCK_BOTH` und ein ungültiges `INVALID` dürfen nicht
zusammengeführt werden. Schlüssel-, Schema- oder Segmentprüfungen dürfen
`data_gate_pass` nicht durch eine zusätzliche boolesche Konjunktion
umdefinieren.

Regime-, Trendstärke-, Volatilitäts-, Liquiditäts- oder weitere
Zustandsbedingungen dürfen nur durch ein explizit registriertes und
versioniertes Gate-Profil einfließen.

Eine bloße Verfügbarkeit eines solchen Feldes erzeugt keine implizite
Gate-Bedingung.

Die kanonische S6-Pflichtausgabe lautet:

```text
allow_long
allow_short
data_gate_pass
gate_state
gate_reason_codes_long
gate_reason_codes_short
gate_profile_id
gate_profile_version
gate_schema_id
gate_schema_version
gate_schema_ref
gate_valid
gate_evaluated_at
regime_model_id
regime_model_version
```

Dabei gilt:

- `allow_long` und `allow_short` sind getrennte Entscheidungen.
- Ein Zustand darf beide Richtungen blockieren.
- Ein Forschungsprofil darf beide Richtungen erlauben.
- Ungültige Pflichtinputs müssen fail-closed behandelt werden.
- Gate-Gründe werden je Richtung als geordnete maschinenlesbare
  Reason-Code-Liste gespeichert.
- Die Anwendung eines ausgewählten Profils muss deterministisch sein.

`gate_state` verwendet ausschließlich:

```text
ALLOW_BOTH
ALLOW_LONG_ONLY
ALLOW_SHORT_ONLY
BLOCK_BOTH
INVALID
```

`gate_valid=true` bedeutet, dass alle für das aktive Gate-Profil benötigten
Inputs gültig waren und die Policy deterministisch ausgewertet wurde.

`gate_valid=false` führt zu:

```text
gate_state = INVALID
allow_long = false
allow_short = false
```

`gate_evaluated_at` ist der deterministische Point-in-Time-
Verfügbarkeitszeitpunkt der ausgewerteten Marktzeile, standardmäßig deren
`close_time`. Es ist kein Build-Wanduhrzeitstempel.

Ein gültiges `BLOCK_BOTH` ist von `INVALID` zu unterscheiden.

Das frühere Feld `gate_inputs_valid` wird nicht parallel geführt.
Seine Semantik ist vollständig in `gate_valid` enthalten.

Das frühere Feld `gate_reason_mask` wird nicht parallel geführt.

Mehrere Profilbedingungen dürfen zu einer Gate-Entscheidung beitragen, jedoch
nur, wenn ihre Aggregationsregel registriert, versioniert und eindeutig ist.

`model` bezeichnet in RCC-002 das S5-Regimemodell. `profile` bezeichnet die
aktive S6-Gatepolicy.

### 7.8 S7_LABELS – Forward Returns und Labels

S7 darf Zukunftsinformationen verwenden, aber ausschließlich zur Erzeugung
klar gekennzeichneter Forschungsziele.

Nur S7 darf regulär Felder mit folgenden Präfixen erzeugen:

```text
fwd_
label_
barrier_
```

Das verbindliche RCC-002-Horizon-Register der ersten Baseline lautet:

```text
H001 = 1 Minute
H005 = 5 Minuten
H015 = 15 Minuten
H060 = 60 Minuten
H240 = 240 Minuten
H1440 = 1440 Minuten
```

Zulässige Horizon-Suffixe sind:

```text
_h001
_h005
_h015
_h060
_h240
_h1440
```

Ein 30-Minuten-Horizont gehört nicht zur ersten kanonischen Baseline. Seine
spätere Aufnahme erfordert eine neue Horizon-Registry-Version und die
vorgeschriebenen wissenschaftlichen und architektonischen Reviews.

S7 erzeugt mindestens:

```text
label_profile_id
label_profile_version
label_schema_id
label_schema_version
label_schema_ref
horizon_registry_id
```

Hinzu kommen die registrierten familien- und horizonspezifischen:

- Forward-Return-Felder;
- Richtungslabels;
- MFE-/MAE-Felder;
- Barrier-Ergebnisse;
- Gültigkeitsfelder;
- Reason-Code-Listen;
- Verfügbarkeitszeitpunkte;
- `label_segment_id_h` je Familie und Horizont.

S7-Felder dürfen niemals:

- in S0 bis S6 zurückpropagieren;
- in Live-/Paper-Feature-Views enthalten sein;
- für Point-in-Time-Gates verwendet werden;
- ohne explizite Forschungsfreigabe exportiert werden.

Die Stufenzugehörigkeit jedes S7-Feldes wird im S7-Schema registriert.
Präfixe sind eine zusätzliche Schutzschicht und ersetzen diese
Schema-Provenienz nicht.

### 7.9 S8_EXPORT – Konsumartefakte

S8 verwendet ausschließlich die nachfolgende versionsgebundene Registry.
Jede View ist eine positive, fail-closed Feld-Allowlist. Ein Feld ist nur
zulässig, wenn sein Name vollständig in der View-Liste enthalten ist und
genau einen Eintrag in der Eigentums- und Leakage-Registry besitzt.

#### 7.9.1 Kanonische Feld-Eigentums- und Leakage-Registry

Die Registry ist normativ. Die Feldlisten sind vollständig expandiert;
Schablonen, Wildcards und implizite Profilfelder sind unzulässig.

```json
{
  "field_registry_id": "RCC002_S8_FIELD_OWNERSHIP_V1",
  "field_registry_version": "1.0.0",
  "groups": [
    {
      "field_owner_stage": "S0_SOURCE",
      "leakage_class": "POINT_IN_TIME",
      "fields": [
        "source_snapshot_id", "provider", "market_type", "symbol", "interval"
      ]
    },
    {
      "field_owner_stage": "S1_NORMALIZED",
      "leakage_class": "POINT_IN_TIME",
      "fields": [
        "source_row_id", "open_time", "close_time", "open", "high", "low", "close", "volume"
      ]
    },
    {
      "field_owner_stage": "S2_VALIDATED",
      "leakage_class": "POINT_IN_TIME",
      "fields": [
        "market_segment_id", "quality_is_observed", "quality_is_synthetic", "quality_has_source_conflict",
        "quality_gap_before", "quality_gap_after", "quality_timestamp_valid", "quality_ohlc_valid",
        "quality_volume_valid", "quality_market_values_valid", "quality_status", "quality_reason_codes",
        "quality_rule_version", "quality_gate_pass"
      ]
    },
    {
      "field_owner_stage": "S3_INDICATORS",
      "leakage_class": "POINT_IN_TIME",
      "fields": [
        "indicator_profile_id", "indicator_profile_version", "indicator_schema_id", "indicator_schema_version",
        "indicator_schema_ref", "indicator_segment_id", "sma_close_200", "sma_close_200_valid",
        "sma_close_200_warmup_complete", "sma_close_200_reason_codes", "ema_close_50", "ema_close_50_valid",
        "ema_close_50_warmup_complete", "ema_close_50_reason_codes", "rsi_wilder_14", "rsi_wilder_14_valid",
        "rsi_wilder_14_warmup_complete", "rsi_wilder_14_reason_codes", "macd_line_12_26",
        "macd_line_12_26_valid", "macd_line_12_26_warmup_complete", "macd_line_12_26_reason_codes",
        "macd_signal_line_12_26_9", "macd_signal_line_12_26_9_valid",
        "macd_signal_line_12_26_9_warmup_complete", "macd_signal_line_12_26_9_reason_codes",
        "macd_hist_12_26_9", "macd_hist_12_26_9_valid", "macd_hist_12_26_9_warmup_complete",
        "macd_hist_12_26_9_reason_codes", "bb_mid_20", "bb_mid_20_valid", "bb_mid_20_warmup_complete",
        "bb_mid_20_reason_codes", "bb_upper_20_2", "bb_upper_20_2_valid", "bb_upper_20_2_warmup_complete",
        "bb_upper_20_2_reason_codes", "bb_lower_20_2", "bb_lower_20_2_valid", "bb_lower_20_2_warmup_complete",
        "bb_lower_20_2_reason_codes", "bb_width_20_2", "bb_width_20_2_valid", "bb_width_20_2_warmup_complete",
        "bb_width_20_2_reason_codes", "stoch_k_14", "stoch_k_14_valid", "stoch_k_14_warmup_complete",
        "stoch_k_14_reason_codes", "true_range", "true_range_valid", "true_range_warmup_complete",
        "true_range_reason_codes", "atr_wilder_14", "atr_wilder_14_valid", "atr_wilder_14_warmup_complete",
        "atr_wilder_14_reason_codes", "roc_close_12_pct", "roc_close_12_pct_valid",
        "roc_close_12_pct_warmup_complete", "roc_close_12_pct_reason_codes", "obv", "obv_valid",
        "obv_warmup_complete", "obv_reason_codes", "typical_price", "typical_price_valid",
        "typical_price_warmup_complete", "typical_price_reason_codes", "cci_20", "cci_20_valid",
        "cci_20_warmup_complete", "cci_20_reason_codes", "mfi_14", "mfi_14_valid", "mfi_14_warmup_complete",
        "mfi_14_reason_codes", "plus_di_14", "plus_di_14_valid", "plus_di_14_warmup_complete",
        "plus_di_14_reason_codes", "minus_di_14", "minus_di_14_valid", "minus_di_14_warmup_complete",
        "minus_di_14_reason_codes", "dx_14", "dx_14_valid", "dx_14_warmup_complete", "dx_14_reason_codes",
        "adx_wilder_14", "adx_wilder_14_valid", "adx_wilder_14_warmup_complete", "adx_wilder_14_reason_codes"
      ]
    },
    {
      "field_owner_stage": "S4_SIGNALS",
      "leakage_class": "POINT_IN_TIME",
      "fields": [
        "signal_profile_id", "signal_profile_version", "signal_schema_id", "signal_schema_version",
        "signal_schema_ref", "sig_rsi_mr_d", "sig_rsi_mr_d_valid", "sig_rsi_mr_d_reason_codes",
        "sig_macd_momentum_d", "sig_macd_momentum_d_valid", "sig_macd_momentum_d_reason_codes",
        "sig_bollinger_mr_d", "sig_bollinger_mr_d_valid", "sig_bollinger_mr_d_reason_codes", "sig_stoch_mr_d",
        "sig_stoch_mr_d_valid", "sig_stoch_mr_d_reason_codes", "sig_cci_mr_d", "sig_cci_mr_d_valid",
        "sig_cci_mr_d_reason_codes", "sig_mfi_mr_d", "sig_mfi_mr_d_valid", "sig_mfi_mr_d_reason_codes",
        "sig_obv_momentum_d", "sig_obv_momentum_d_valid", "sig_obv_momentum_d_reason_codes",
        "sig_roc_momentum_d", "sig_roc_momentum_d_valid", "sig_roc_momentum_d_reason_codes",
        "state_ma200_trend_d", "state_ma200_trend_d_valid", "state_ma200_trend_d_reason_codes",
        "state_ema50_trend_d", "state_ema50_trend_d_valid", "state_ema50_trend_d_reason_codes",
        "state_atr_relative_d", "state_atr_relative_d_valid", "state_atr_relative_d_reason_codes",
        "state_adx_strength_d", "state_adx_strength_d_valid", "state_adx_strength_d_reason_codes",
        "score_rsi_mr_c", "score_rsi_mr_c_valid", "score_rsi_mr_c_reason_codes", "score_macd_momentum_c",
        "score_macd_momentum_c_valid", "score_macd_momentum_c_reason_codes", "score_bollinger_mr_c",
        "score_bollinger_mr_c_valid", "score_bollinger_mr_c_reason_codes", "score_stoch_mr_c",
        "score_stoch_mr_c_valid", "score_stoch_mr_c_reason_codes", "score_cci_mr_c", "score_cci_mr_c_valid",
        "score_cci_mr_c_reason_codes", "score_mfi_mr_c", "score_mfi_mr_c_valid", "score_mfi_mr_c_reason_codes",
        "score_obv_momentum_c", "score_obv_momentum_c_valid", "score_obv_momentum_c_reason_codes",
        "score_roc_momentum_c", "score_roc_momentum_c_valid", "score_roc_momentum_c_reason_codes",
        "score_ma200_trend_c", "score_ma200_trend_c_valid", "score_ma200_trend_c_reason_codes",
        "score_ema50_trend_c", "score_ema50_trend_c_valid", "score_ema50_trend_c_reason_codes",
        "score_atr_relative_c", "score_atr_relative_c_valid", "score_atr_relative_c_reason_codes",
        "score_adx_strength_c", "score_adx_strength_c_valid", "score_adx_strength_c_reason_codes"
      ]
    },
    {
      "field_owner_stage": "S5_REGIMES",
      "leakage_class": "POINT_IN_TIME",
      "fields": [
        "regime_raw", "regime_effective", "regime_candidate", "regime_candidate_count",
        "regime_transition_flag", "regime_transition_from", "regime_transition_to", "ma200_slope_1440_pct",
        "trend_strength", "trend_strength_valid", "trend_strength_reason_codes", "volatility_relative",
        "volatility_relative_valid", "volatility_relative_reason_codes", "regime_model_id",
        "regime_model_version", "regime_schema_id", "regime_schema_version", "regime_schema_ref",
        "regime_valid", "regime_reason_codes"
      ]
    },
    {
      "field_owner_stage": "S6_GATES",
      "leakage_class": "POINT_IN_TIME",
      "fields": [
        "allow_long", "allow_short", "data_gate_pass", "gate_state", "gate_reason_codes_long",
        "gate_reason_codes_short", "gate_profile_id", "gate_profile_version", "gate_schema_id",
        "gate_schema_version", "gate_schema_ref", "gate_valid", "gate_evaluated_at"
      ]
    },
    {
      "field_owner_stage": "S7_LABELS",
      "leakage_class": "FUTURE_OUTCOME",
      "fields": [
        "label_profile_id", "label_profile_version", "label_schema_id", "label_schema_version",
        "label_schema_ref", "horizon_registry_id", "horizon_registry_version", "cost_profile_id",
        "cost_profile_version", "barrier_profile_id", "barrier_profile_version",
        "label_reason_code_registry_version", "label_numeric_profile_id", "label_numeric_profile_version",
        "label_horizon_bars_h001", "label_available_at_h001", "fwd_cc_valid_h001", "fwd_cc_reason_codes_h001",
        "fwd_cc_label_segment_id_h001", "fwd_cc_long_ret_h001", "fwd_cc_short_ret_h001", "fwd_cc_log_ret_h001",
        "fwd_cc_short_log_ret_h001", "fwd_noc_valid_h001", "fwd_noc_reason_codes_h001",
        "fwd_noc_label_segment_id_h001", "fwd_noc_long_ret_h001", "fwd_noc_short_ret_h001",
        "fwd_noc_long_net_proxy_fee_rt_0004_h001", "fwd_noc_short_net_proxy_fee_rt_0004_h001",
        "fwd_excursion_valid_h001", "fwd_excursion_reason_codes_h001", "fwd_excursion_label_segment_id_h001",
        "fwd_long_mfe_h001", "fwd_long_mae_h001", "fwd_short_mfe_h001", "fwd_short_mae_h001",
        "fwd_long_mfe_first_bar_h001", "fwd_long_mae_first_bar_h001", "fwd_short_mfe_first_bar_h001",
        "fwd_short_mae_first_bar_h001", "label_cc_direction_valid_h001", "label_cc_direction_reason_codes_h001",
        "label_cc_direction_segment_id_h001", "label_cc_long_direction_h001", "label_cc_short_direction_h001",
        "label_noc_direction_valid_h001", "label_noc_direction_reason_codes_h001",
        "label_noc_direction_segment_id_h001", "label_noc_long_direction_h001",
        "label_noc_short_direction_h001", "label_noc_long_net_proxy_fee_rt_0004_direction_h001",
        "label_noc_short_net_proxy_fee_rt_0004_direction_h001", "barrier_valid_h001",
        "barrier_reason_codes_h001", "barrier_label_segment_id_h001", "barrier_long_outcome_tp050_sl020_h001",
        "barrier_short_outcome_tp050_sl020_h001", "barrier_long_first_hit_bar_tp050_sl020_h001",
        "barrier_short_first_hit_bar_tp050_sl020_h001", "barrier_long_first_hit_time_tp050_sl020_h001",
        "barrier_short_first_hit_time_tp050_sl020_h001", "label_horizon_bars_h005", "label_available_at_h005",
        "fwd_cc_valid_h005", "fwd_cc_reason_codes_h005", "fwd_cc_label_segment_id_h005", "fwd_cc_long_ret_h005",
        "fwd_cc_short_ret_h005", "fwd_cc_log_ret_h005", "fwd_cc_short_log_ret_h005", "fwd_noc_valid_h005",
        "fwd_noc_reason_codes_h005", "fwd_noc_label_segment_id_h005", "fwd_noc_long_ret_h005",
        "fwd_noc_short_ret_h005", "fwd_noc_long_net_proxy_fee_rt_0004_h005",
        "fwd_noc_short_net_proxy_fee_rt_0004_h005", "fwd_excursion_valid_h005",
        "fwd_excursion_reason_codes_h005", "fwd_excursion_label_segment_id_h005", "fwd_long_mfe_h005",
        "fwd_long_mae_h005", "fwd_short_mfe_h005", "fwd_short_mae_h005", "fwd_long_mfe_first_bar_h005",
        "fwd_long_mae_first_bar_h005", "fwd_short_mfe_first_bar_h005", "fwd_short_mae_first_bar_h005",
        "label_cc_direction_valid_h005", "label_cc_direction_reason_codes_h005",
        "label_cc_direction_segment_id_h005", "label_cc_long_direction_h005", "label_cc_short_direction_h005",
        "label_noc_direction_valid_h005", "label_noc_direction_reason_codes_h005",
        "label_noc_direction_segment_id_h005", "label_noc_long_direction_h005",
        "label_noc_short_direction_h005", "label_noc_long_net_proxy_fee_rt_0004_direction_h005",
        "label_noc_short_net_proxy_fee_rt_0004_direction_h005", "barrier_valid_h005",
        "barrier_reason_codes_h005", "barrier_label_segment_id_h005", "barrier_long_outcome_tp050_sl020_h005",
        "barrier_short_outcome_tp050_sl020_h005", "barrier_long_first_hit_bar_tp050_sl020_h005",
        "barrier_short_first_hit_bar_tp050_sl020_h005", "barrier_long_first_hit_time_tp050_sl020_h005",
        "barrier_short_first_hit_time_tp050_sl020_h005", "label_horizon_bars_h015", "label_available_at_h015",
        "fwd_cc_valid_h015", "fwd_cc_reason_codes_h015", "fwd_cc_label_segment_id_h015", "fwd_cc_long_ret_h015",
        "fwd_cc_short_ret_h015", "fwd_cc_log_ret_h015", "fwd_cc_short_log_ret_h015", "fwd_noc_valid_h015",
        "fwd_noc_reason_codes_h015", "fwd_noc_label_segment_id_h015", "fwd_noc_long_ret_h015",
        "fwd_noc_short_ret_h015", "fwd_noc_long_net_proxy_fee_rt_0004_h015",
        "fwd_noc_short_net_proxy_fee_rt_0004_h015", "fwd_excursion_valid_h015",
        "fwd_excursion_reason_codes_h015", "fwd_excursion_label_segment_id_h015", "fwd_long_mfe_h015",
        "fwd_long_mae_h015", "fwd_short_mfe_h015", "fwd_short_mae_h015", "fwd_long_mfe_first_bar_h015",
        "fwd_long_mae_first_bar_h015", "fwd_short_mfe_first_bar_h015", "fwd_short_mae_first_bar_h015",
        "label_cc_direction_valid_h015", "label_cc_direction_reason_codes_h015",
        "label_cc_direction_segment_id_h015", "label_cc_long_direction_h015", "label_cc_short_direction_h015",
        "label_noc_direction_valid_h015", "label_noc_direction_reason_codes_h015",
        "label_noc_direction_segment_id_h015", "label_noc_long_direction_h015",
        "label_noc_short_direction_h015", "label_noc_long_net_proxy_fee_rt_0004_direction_h015",
        "label_noc_short_net_proxy_fee_rt_0004_direction_h015", "barrier_valid_h015",
        "barrier_reason_codes_h015", "barrier_label_segment_id_h015", "barrier_long_outcome_tp050_sl020_h015",
        "barrier_short_outcome_tp050_sl020_h015", "barrier_long_first_hit_bar_tp050_sl020_h015",
        "barrier_short_first_hit_bar_tp050_sl020_h015", "barrier_long_first_hit_time_tp050_sl020_h015",
        "barrier_short_first_hit_time_tp050_sl020_h015", "label_horizon_bars_h060", "label_available_at_h060",
        "fwd_cc_valid_h060", "fwd_cc_reason_codes_h060", "fwd_cc_label_segment_id_h060", "fwd_cc_long_ret_h060",
        "fwd_cc_short_ret_h060", "fwd_cc_log_ret_h060", "fwd_cc_short_log_ret_h060", "fwd_noc_valid_h060",
        "fwd_noc_reason_codes_h060", "fwd_noc_label_segment_id_h060", "fwd_noc_long_ret_h060",
        "fwd_noc_short_ret_h060", "fwd_noc_long_net_proxy_fee_rt_0004_h060",
        "fwd_noc_short_net_proxy_fee_rt_0004_h060", "fwd_excursion_valid_h060",
        "fwd_excursion_reason_codes_h060", "fwd_excursion_label_segment_id_h060", "fwd_long_mfe_h060",
        "fwd_long_mae_h060", "fwd_short_mfe_h060", "fwd_short_mae_h060", "fwd_long_mfe_first_bar_h060",
        "fwd_long_mae_first_bar_h060", "fwd_short_mfe_first_bar_h060", "fwd_short_mae_first_bar_h060",
        "label_cc_direction_valid_h060", "label_cc_direction_reason_codes_h060",
        "label_cc_direction_segment_id_h060", "label_cc_long_direction_h060", "label_cc_short_direction_h060",
        "label_noc_direction_valid_h060", "label_noc_direction_reason_codes_h060",
        "label_noc_direction_segment_id_h060", "label_noc_long_direction_h060",
        "label_noc_short_direction_h060", "label_noc_long_net_proxy_fee_rt_0004_direction_h060",
        "label_noc_short_net_proxy_fee_rt_0004_direction_h060", "barrier_valid_h060",
        "barrier_reason_codes_h060", "barrier_label_segment_id_h060", "barrier_long_outcome_tp050_sl020_h060",
        "barrier_short_outcome_tp050_sl020_h060", "barrier_long_first_hit_bar_tp050_sl020_h060",
        "barrier_short_first_hit_bar_tp050_sl020_h060", "barrier_long_first_hit_time_tp050_sl020_h060",
        "barrier_short_first_hit_time_tp050_sl020_h060", "label_horizon_bars_h240", "label_available_at_h240",
        "fwd_cc_valid_h240", "fwd_cc_reason_codes_h240", "fwd_cc_label_segment_id_h240", "fwd_cc_long_ret_h240",
        "fwd_cc_short_ret_h240", "fwd_cc_log_ret_h240", "fwd_cc_short_log_ret_h240", "fwd_noc_valid_h240",
        "fwd_noc_reason_codes_h240", "fwd_noc_label_segment_id_h240", "fwd_noc_long_ret_h240",
        "fwd_noc_short_ret_h240", "fwd_noc_long_net_proxy_fee_rt_0004_h240",
        "fwd_noc_short_net_proxy_fee_rt_0004_h240", "fwd_excursion_valid_h240",
        "fwd_excursion_reason_codes_h240", "fwd_excursion_label_segment_id_h240", "fwd_long_mfe_h240",
        "fwd_long_mae_h240", "fwd_short_mfe_h240", "fwd_short_mae_h240", "fwd_long_mfe_first_bar_h240",
        "fwd_long_mae_first_bar_h240", "fwd_short_mfe_first_bar_h240", "fwd_short_mae_first_bar_h240",
        "label_cc_direction_valid_h240", "label_cc_direction_reason_codes_h240",
        "label_cc_direction_segment_id_h240", "label_cc_long_direction_h240", "label_cc_short_direction_h240",
        "label_noc_direction_valid_h240", "label_noc_direction_reason_codes_h240",
        "label_noc_direction_segment_id_h240", "label_noc_long_direction_h240",
        "label_noc_short_direction_h240", "label_noc_long_net_proxy_fee_rt_0004_direction_h240",
        "label_noc_short_net_proxy_fee_rt_0004_direction_h240", "barrier_valid_h240",
        "barrier_reason_codes_h240", "barrier_label_segment_id_h240", "barrier_long_outcome_tp050_sl020_h240",
        "barrier_short_outcome_tp050_sl020_h240", "barrier_long_first_hit_bar_tp050_sl020_h240",
        "barrier_short_first_hit_bar_tp050_sl020_h240", "barrier_long_first_hit_time_tp050_sl020_h240",
        "barrier_short_first_hit_time_tp050_sl020_h240", "label_horizon_bars_h1440", "label_available_at_h1440",
        "fwd_cc_valid_h1440", "fwd_cc_reason_codes_h1440", "fwd_cc_label_segment_id_h1440",
        "fwd_cc_long_ret_h1440", "fwd_cc_short_ret_h1440", "fwd_cc_log_ret_h1440", "fwd_cc_short_log_ret_h1440",
        "fwd_noc_valid_h1440", "fwd_noc_reason_codes_h1440", "fwd_noc_label_segment_id_h1440",
        "fwd_noc_long_ret_h1440", "fwd_noc_short_ret_h1440", "fwd_noc_long_net_proxy_fee_rt_0004_h1440",
        "fwd_noc_short_net_proxy_fee_rt_0004_h1440", "fwd_excursion_valid_h1440",
        "fwd_excursion_reason_codes_h1440", "fwd_excursion_label_segment_id_h1440", "fwd_long_mfe_h1440",
        "fwd_long_mae_h1440", "fwd_short_mfe_h1440", "fwd_short_mae_h1440", "fwd_long_mfe_first_bar_h1440",
        "fwd_long_mae_first_bar_h1440", "fwd_short_mfe_first_bar_h1440", "fwd_short_mae_first_bar_h1440",
        "label_cc_direction_valid_h1440", "label_cc_direction_reason_codes_h1440",
        "label_cc_direction_segment_id_h1440", "label_cc_long_direction_h1440",
        "label_cc_short_direction_h1440", "label_noc_direction_valid_h1440",
        "label_noc_direction_reason_codes_h1440", "label_noc_direction_segment_id_h1440",
        "label_noc_long_direction_h1440", "label_noc_short_direction_h1440",
        "label_noc_long_net_proxy_fee_rt_0004_direction_h1440",
        "label_noc_short_net_proxy_fee_rt_0004_direction_h1440", "barrier_valid_h1440",
        "barrier_reason_codes_h1440", "barrier_label_segment_id_h1440",
        "barrier_long_outcome_tp050_sl020_h1440", "barrier_short_outcome_tp050_sl020_h1440",
        "barrier_long_first_hit_bar_tp050_sl020_h1440", "barrier_short_first_hit_bar_tp050_sl020_h1440",
        "barrier_long_first_hit_time_tp050_sl020_h1440", "barrier_short_first_hit_time_tp050_sl020_h1440"
      ]
    },
    {
      "field_owner_stage": "S0_SOURCE",
      "leakage_class": "PROVENANCE_METADATA",
      "fields": [
        "retrieved_at_utc", "source_file_name", "source_byte_sha256", "source_revision", "source_format",
        "source_location", "license_or_terms_ref"
      ]
    },
    {
      "field_owner_stage": "S8_EXPORT",
      "leakage_class": "AUDIT_METADATA",
      "fields": [
        "manifest_schema_id", "manifest_schema_version", "manifest_schema_ref", "manifest_type", "manifest_id",
        "created_at_utc", "dataset_id", "dataset_artifact_set_id", "build_id", "run_id", "artifact_id",
        "relative_path", "media_type", "schema_id", "schema_version", "schema_ref", "schema_fingerprint_sha256",
        "field_registry_sha256", "view_allowlist_sha256", "byte_sha256", "semantic_sha256",
        "physical_layout_sha256", "publication_status"
      ]
    }
  ]
}
```

Für jedes Feld einer View werden `field_owner_stage` und
`leakage_class` durch den eindeutigen Registry-Eintrag bestimmt.
Fehlt ein Eintrag oder existieren mehrere Einträge, ist die View
ungültig und darf nicht veröffentlicht werden.

#### 7.9.2 Kanonische Allowlist-Hashbildung

Für jede View wird folgende Vorabbildung nach RFC 8785/JCS kanonisiert
und mit SHA-256 gehasht:

```json
{
  "allowed_producer_stages": ["<ordered stages>"],
  "fields": [
    {
      "field_name": "<field>",
      "field_owner_stage": "<registry owner>",
      "leakage_class": "<registry leakage class>"
    }
  ]
}
```

Feld- und Stufenreihenfolge sind Teil der Vorabbildung. `schema_id`,
`schema_version`, `schema_ref` und `allowlist_sha256` selbst sind nicht
Bestandteil des Allowlist-Hashes; sie gehören zum übergeordneten
View-Schema-Fingerprint.

#### 7.9.3 Vollständig materialisierte positive View-Allowlists

##### 7.9.3.1 `research-features`

```json
{
  "schema_id": "rcc002.view.research-features",
  "schema_version": "1.0.0",
  "schema_ref": "rcc002.view.research-features/1.0.0",
  "allowlist_sha256": "2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e",
  "allowed_producer_stages": [
    "S0_SOURCE", "S1_NORMALIZED", "S2_VALIDATED", "S3_INDICATORS", "S4_SIGNALS", "S5_REGIMES", "S6_GATES"
  ],
  "fields": [
    "source_snapshot_id", "provider", "market_type", "symbol", "interval", "source_row_id", "open_time",
    "close_time", "open", "high", "low", "close", "volume", "market_segment_id", "quality_is_observed",
    "quality_is_synthetic", "quality_has_source_conflict", "quality_gap_before", "quality_gap_after",
    "quality_timestamp_valid", "quality_ohlc_valid", "quality_volume_valid", "quality_market_values_valid",
    "quality_status", "quality_reason_codes", "quality_rule_version", "quality_gate_pass",
    "indicator_profile_id", "indicator_profile_version", "indicator_schema_id", "indicator_schema_version",
    "indicator_schema_ref", "indicator_segment_id", "sma_close_200", "sma_close_200_valid",
    "sma_close_200_warmup_complete", "sma_close_200_reason_codes", "ema_close_50", "ema_close_50_valid",
    "ema_close_50_warmup_complete", "ema_close_50_reason_codes", "rsi_wilder_14", "rsi_wilder_14_valid",
    "rsi_wilder_14_warmup_complete", "rsi_wilder_14_reason_codes", "macd_line_12_26", "macd_line_12_26_valid",
    "macd_line_12_26_warmup_complete", "macd_line_12_26_reason_codes", "macd_signal_line_12_26_9",
    "macd_signal_line_12_26_9_valid", "macd_signal_line_12_26_9_warmup_complete",
    "macd_signal_line_12_26_9_reason_codes", "macd_hist_12_26_9", "macd_hist_12_26_9_valid",
    "macd_hist_12_26_9_warmup_complete", "macd_hist_12_26_9_reason_codes", "bb_mid_20", "bb_mid_20_valid",
    "bb_mid_20_warmup_complete", "bb_mid_20_reason_codes", "bb_upper_20_2", "bb_upper_20_2_valid",
    "bb_upper_20_2_warmup_complete", "bb_upper_20_2_reason_codes", "bb_lower_20_2", "bb_lower_20_2_valid",
    "bb_lower_20_2_warmup_complete", "bb_lower_20_2_reason_codes", "bb_width_20_2", "bb_width_20_2_valid",
    "bb_width_20_2_warmup_complete", "bb_width_20_2_reason_codes", "stoch_k_14", "stoch_k_14_valid",
    "stoch_k_14_warmup_complete", "stoch_k_14_reason_codes", "true_range", "true_range_valid",
    "true_range_warmup_complete", "true_range_reason_codes", "atr_wilder_14", "atr_wilder_14_valid",
    "atr_wilder_14_warmup_complete", "atr_wilder_14_reason_codes", "roc_close_12_pct", "roc_close_12_pct_valid",
    "roc_close_12_pct_warmup_complete", "roc_close_12_pct_reason_codes", "obv", "obv_valid",
    "obv_warmup_complete", "obv_reason_codes", "typical_price", "typical_price_valid",
    "typical_price_warmup_complete", "typical_price_reason_codes", "cci_20", "cci_20_valid",
    "cci_20_warmup_complete", "cci_20_reason_codes", "mfi_14", "mfi_14_valid", "mfi_14_warmup_complete",
    "mfi_14_reason_codes", "plus_di_14", "plus_di_14_valid", "plus_di_14_warmup_complete",
    "plus_di_14_reason_codes", "minus_di_14", "minus_di_14_valid", "minus_di_14_warmup_complete",
    "minus_di_14_reason_codes", "dx_14", "dx_14_valid", "dx_14_warmup_complete", "dx_14_reason_codes",
    "adx_wilder_14", "adx_wilder_14_valid", "adx_wilder_14_warmup_complete", "adx_wilder_14_reason_codes",
    "signal_profile_id", "signal_profile_version", "signal_schema_id", "signal_schema_version",
    "signal_schema_ref", "sig_rsi_mr_d", "sig_rsi_mr_d_valid", "sig_rsi_mr_d_reason_codes",
    "sig_macd_momentum_d", "sig_macd_momentum_d_valid", "sig_macd_momentum_d_reason_codes",
    "sig_bollinger_mr_d", "sig_bollinger_mr_d_valid", "sig_bollinger_mr_d_reason_codes", "sig_stoch_mr_d",
    "sig_stoch_mr_d_valid", "sig_stoch_mr_d_reason_codes", "sig_cci_mr_d", "sig_cci_mr_d_valid",
    "sig_cci_mr_d_reason_codes", "sig_mfi_mr_d", "sig_mfi_mr_d_valid", "sig_mfi_mr_d_reason_codes",
    "sig_obv_momentum_d", "sig_obv_momentum_d_valid", "sig_obv_momentum_d_reason_codes", "sig_roc_momentum_d",
    "sig_roc_momentum_d_valid", "sig_roc_momentum_d_reason_codes", "state_ma200_trend_d",
    "state_ma200_trend_d_valid", "state_ma200_trend_d_reason_codes", "state_ema50_trend_d",
    "state_ema50_trend_d_valid", "state_ema50_trend_d_reason_codes", "state_atr_relative_d",
    "state_atr_relative_d_valid", "state_atr_relative_d_reason_codes", "state_adx_strength_d",
    "state_adx_strength_d_valid", "state_adx_strength_d_reason_codes", "score_rsi_mr_c", "score_rsi_mr_c_valid",
    "score_rsi_mr_c_reason_codes", "score_macd_momentum_c", "score_macd_momentum_c_valid",
    "score_macd_momentum_c_reason_codes", "score_bollinger_mr_c", "score_bollinger_mr_c_valid",
    "score_bollinger_mr_c_reason_codes", "score_stoch_mr_c", "score_stoch_mr_c_valid",
    "score_stoch_mr_c_reason_codes", "score_cci_mr_c", "score_cci_mr_c_valid", "score_cci_mr_c_reason_codes",
    "score_mfi_mr_c", "score_mfi_mr_c_valid", "score_mfi_mr_c_reason_codes", "score_obv_momentum_c",
    "score_obv_momentum_c_valid", "score_obv_momentum_c_reason_codes", "score_roc_momentum_c",
    "score_roc_momentum_c_valid", "score_roc_momentum_c_reason_codes", "score_ma200_trend_c",
    "score_ma200_trend_c_valid", "score_ma200_trend_c_reason_codes", "score_ema50_trend_c",
    "score_ema50_trend_c_valid", "score_ema50_trend_c_reason_codes", "score_atr_relative_c",
    "score_atr_relative_c_valid", "score_atr_relative_c_reason_codes", "score_adx_strength_c",
    "score_adx_strength_c_valid", "score_adx_strength_c_reason_codes", "regime_raw", "regime_effective",
    "regime_candidate", "regime_candidate_count", "regime_transition_flag", "regime_transition_from",
    "regime_transition_to", "ma200_slope_1440_pct", "trend_strength", "trend_strength_valid",
    "trend_strength_reason_codes", "volatility_relative", "volatility_relative_valid",
    "volatility_relative_reason_codes", "regime_model_id", "regime_model_version", "regime_schema_id",
    "regime_schema_version", "regime_schema_ref", "regime_valid", "regime_reason_codes", "allow_long",
    "allow_short", "data_gate_pass", "gate_state", "gate_reason_codes_long", "gate_reason_codes_short",
    "gate_profile_id", "gate_profile_version", "gate_schema_id", "gate_schema_version", "gate_schema_ref",
    "gate_valid", "gate_evaluated_at"
  ]
}
```

##### 7.9.3.2 `backtest-inputs`

```json
{
  "schema_id": "rcc002.view.backtest-inputs",
  "schema_version": "1.0.0",
  "schema_ref": "rcc002.view.backtest-inputs/1.0.0",
  "allowlist_sha256": "2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e",
  "allowed_producer_stages": [
    "S0_SOURCE", "S1_NORMALIZED", "S2_VALIDATED", "S3_INDICATORS", "S4_SIGNALS", "S5_REGIMES", "S6_GATES"
  ],
  "fields": [
    "source_snapshot_id", "provider", "market_type", "symbol", "interval", "source_row_id", "open_time",
    "close_time", "open", "high", "low", "close", "volume", "market_segment_id", "quality_is_observed",
    "quality_is_synthetic", "quality_has_source_conflict", "quality_gap_before", "quality_gap_after",
    "quality_timestamp_valid", "quality_ohlc_valid", "quality_volume_valid", "quality_market_values_valid",
    "quality_status", "quality_reason_codes", "quality_rule_version", "quality_gate_pass",
    "indicator_profile_id", "indicator_profile_version", "indicator_schema_id", "indicator_schema_version",
    "indicator_schema_ref", "indicator_segment_id", "sma_close_200", "sma_close_200_valid",
    "sma_close_200_warmup_complete", "sma_close_200_reason_codes", "ema_close_50", "ema_close_50_valid",
    "ema_close_50_warmup_complete", "ema_close_50_reason_codes", "rsi_wilder_14", "rsi_wilder_14_valid",
    "rsi_wilder_14_warmup_complete", "rsi_wilder_14_reason_codes", "macd_line_12_26", "macd_line_12_26_valid",
    "macd_line_12_26_warmup_complete", "macd_line_12_26_reason_codes", "macd_signal_line_12_26_9",
    "macd_signal_line_12_26_9_valid", "macd_signal_line_12_26_9_warmup_complete",
    "macd_signal_line_12_26_9_reason_codes", "macd_hist_12_26_9", "macd_hist_12_26_9_valid",
    "macd_hist_12_26_9_warmup_complete", "macd_hist_12_26_9_reason_codes", "bb_mid_20", "bb_mid_20_valid",
    "bb_mid_20_warmup_complete", "bb_mid_20_reason_codes", "bb_upper_20_2", "bb_upper_20_2_valid",
    "bb_upper_20_2_warmup_complete", "bb_upper_20_2_reason_codes", "bb_lower_20_2", "bb_lower_20_2_valid",
    "bb_lower_20_2_warmup_complete", "bb_lower_20_2_reason_codes", "bb_width_20_2", "bb_width_20_2_valid",
    "bb_width_20_2_warmup_complete", "bb_width_20_2_reason_codes", "stoch_k_14", "stoch_k_14_valid",
    "stoch_k_14_warmup_complete", "stoch_k_14_reason_codes", "true_range", "true_range_valid",
    "true_range_warmup_complete", "true_range_reason_codes", "atr_wilder_14", "atr_wilder_14_valid",
    "atr_wilder_14_warmup_complete", "atr_wilder_14_reason_codes", "roc_close_12_pct", "roc_close_12_pct_valid",
    "roc_close_12_pct_warmup_complete", "roc_close_12_pct_reason_codes", "obv", "obv_valid",
    "obv_warmup_complete", "obv_reason_codes", "typical_price", "typical_price_valid",
    "typical_price_warmup_complete", "typical_price_reason_codes", "cci_20", "cci_20_valid",
    "cci_20_warmup_complete", "cci_20_reason_codes", "mfi_14", "mfi_14_valid", "mfi_14_warmup_complete",
    "mfi_14_reason_codes", "plus_di_14", "plus_di_14_valid", "plus_di_14_warmup_complete",
    "plus_di_14_reason_codes", "minus_di_14", "minus_di_14_valid", "minus_di_14_warmup_complete",
    "minus_di_14_reason_codes", "dx_14", "dx_14_valid", "dx_14_warmup_complete", "dx_14_reason_codes",
    "adx_wilder_14", "adx_wilder_14_valid", "adx_wilder_14_warmup_complete", "adx_wilder_14_reason_codes",
    "signal_profile_id", "signal_profile_version", "signal_schema_id", "signal_schema_version",
    "signal_schema_ref", "sig_rsi_mr_d", "sig_rsi_mr_d_valid", "sig_rsi_mr_d_reason_codes",
    "sig_macd_momentum_d", "sig_macd_momentum_d_valid", "sig_macd_momentum_d_reason_codes",
    "sig_bollinger_mr_d", "sig_bollinger_mr_d_valid", "sig_bollinger_mr_d_reason_codes", "sig_stoch_mr_d",
    "sig_stoch_mr_d_valid", "sig_stoch_mr_d_reason_codes", "sig_cci_mr_d", "sig_cci_mr_d_valid",
    "sig_cci_mr_d_reason_codes", "sig_mfi_mr_d", "sig_mfi_mr_d_valid", "sig_mfi_mr_d_reason_codes",
    "sig_obv_momentum_d", "sig_obv_momentum_d_valid", "sig_obv_momentum_d_reason_codes", "sig_roc_momentum_d",
    "sig_roc_momentum_d_valid", "sig_roc_momentum_d_reason_codes", "state_ma200_trend_d",
    "state_ma200_trend_d_valid", "state_ma200_trend_d_reason_codes", "state_ema50_trend_d",
    "state_ema50_trend_d_valid", "state_ema50_trend_d_reason_codes", "state_atr_relative_d",
    "state_atr_relative_d_valid", "state_atr_relative_d_reason_codes", "state_adx_strength_d",
    "state_adx_strength_d_valid", "state_adx_strength_d_reason_codes", "score_rsi_mr_c", "score_rsi_mr_c_valid",
    "score_rsi_mr_c_reason_codes", "score_macd_momentum_c", "score_macd_momentum_c_valid",
    "score_macd_momentum_c_reason_codes", "score_bollinger_mr_c", "score_bollinger_mr_c_valid",
    "score_bollinger_mr_c_reason_codes", "score_stoch_mr_c", "score_stoch_mr_c_valid",
    "score_stoch_mr_c_reason_codes", "score_cci_mr_c", "score_cci_mr_c_valid", "score_cci_mr_c_reason_codes",
    "score_mfi_mr_c", "score_mfi_mr_c_valid", "score_mfi_mr_c_reason_codes", "score_obv_momentum_c",
    "score_obv_momentum_c_valid", "score_obv_momentum_c_reason_codes", "score_roc_momentum_c",
    "score_roc_momentum_c_valid", "score_roc_momentum_c_reason_codes", "score_ma200_trend_c",
    "score_ma200_trend_c_valid", "score_ma200_trend_c_reason_codes", "score_ema50_trend_c",
    "score_ema50_trend_c_valid", "score_ema50_trend_c_reason_codes", "score_atr_relative_c",
    "score_atr_relative_c_valid", "score_atr_relative_c_reason_codes", "score_adx_strength_c",
    "score_adx_strength_c_valid", "score_adx_strength_c_reason_codes", "regime_raw", "regime_effective",
    "regime_candidate", "regime_candidate_count", "regime_transition_flag", "regime_transition_from",
    "regime_transition_to", "ma200_slope_1440_pct", "trend_strength", "trend_strength_valid",
    "trend_strength_reason_codes", "volatility_relative", "volatility_relative_valid",
    "volatility_relative_reason_codes", "regime_model_id", "regime_model_version", "regime_schema_id",
    "regime_schema_version", "regime_schema_ref", "regime_valid", "regime_reason_codes", "allow_long",
    "allow_short", "data_gate_pass", "gate_state", "gate_reason_codes_long", "gate_reason_codes_short",
    "gate_profile_id", "gate_profile_version", "gate_schema_id", "gate_schema_version", "gate_schema_ref",
    "gate_valid", "gate_evaluated_at"
  ]
}
```

##### 7.9.3.3 `paper`

```json
{
  "schema_id": "rcc002.view.paper",
  "schema_version": "1.0.0",
  "schema_ref": "rcc002.view.paper/1.0.0",
  "allowlist_sha256": "2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e",
  "allowed_producer_stages": [
    "S0_SOURCE", "S1_NORMALIZED", "S2_VALIDATED", "S3_INDICATORS", "S4_SIGNALS", "S5_REGIMES", "S6_GATES"
  ],
  "fields": [
    "source_snapshot_id", "provider", "market_type", "symbol", "interval", "source_row_id", "open_time",
    "close_time", "open", "high", "low", "close", "volume", "market_segment_id", "quality_is_observed",
    "quality_is_synthetic", "quality_has_source_conflict", "quality_gap_before", "quality_gap_after",
    "quality_timestamp_valid", "quality_ohlc_valid", "quality_volume_valid", "quality_market_values_valid",
    "quality_status", "quality_reason_codes", "quality_rule_version", "quality_gate_pass",
    "indicator_profile_id", "indicator_profile_version", "indicator_schema_id", "indicator_schema_version",
    "indicator_schema_ref", "indicator_segment_id", "sma_close_200", "sma_close_200_valid",
    "sma_close_200_warmup_complete", "sma_close_200_reason_codes", "ema_close_50", "ema_close_50_valid",
    "ema_close_50_warmup_complete", "ema_close_50_reason_codes", "rsi_wilder_14", "rsi_wilder_14_valid",
    "rsi_wilder_14_warmup_complete", "rsi_wilder_14_reason_codes", "macd_line_12_26", "macd_line_12_26_valid",
    "macd_line_12_26_warmup_complete", "macd_line_12_26_reason_codes", "macd_signal_line_12_26_9",
    "macd_signal_line_12_26_9_valid", "macd_signal_line_12_26_9_warmup_complete",
    "macd_signal_line_12_26_9_reason_codes", "macd_hist_12_26_9", "macd_hist_12_26_9_valid",
    "macd_hist_12_26_9_warmup_complete", "macd_hist_12_26_9_reason_codes", "bb_mid_20", "bb_mid_20_valid",
    "bb_mid_20_warmup_complete", "bb_mid_20_reason_codes", "bb_upper_20_2", "bb_upper_20_2_valid",
    "bb_upper_20_2_warmup_complete", "bb_upper_20_2_reason_codes", "bb_lower_20_2", "bb_lower_20_2_valid",
    "bb_lower_20_2_warmup_complete", "bb_lower_20_2_reason_codes", "bb_width_20_2", "bb_width_20_2_valid",
    "bb_width_20_2_warmup_complete", "bb_width_20_2_reason_codes", "stoch_k_14", "stoch_k_14_valid",
    "stoch_k_14_warmup_complete", "stoch_k_14_reason_codes", "true_range", "true_range_valid",
    "true_range_warmup_complete", "true_range_reason_codes", "atr_wilder_14", "atr_wilder_14_valid",
    "atr_wilder_14_warmup_complete", "atr_wilder_14_reason_codes", "roc_close_12_pct", "roc_close_12_pct_valid",
    "roc_close_12_pct_warmup_complete", "roc_close_12_pct_reason_codes", "obv", "obv_valid",
    "obv_warmup_complete", "obv_reason_codes", "typical_price", "typical_price_valid",
    "typical_price_warmup_complete", "typical_price_reason_codes", "cci_20", "cci_20_valid",
    "cci_20_warmup_complete", "cci_20_reason_codes", "mfi_14", "mfi_14_valid", "mfi_14_warmup_complete",
    "mfi_14_reason_codes", "plus_di_14", "plus_di_14_valid", "plus_di_14_warmup_complete",
    "plus_di_14_reason_codes", "minus_di_14", "minus_di_14_valid", "minus_di_14_warmup_complete",
    "minus_di_14_reason_codes", "dx_14", "dx_14_valid", "dx_14_warmup_complete", "dx_14_reason_codes",
    "adx_wilder_14", "adx_wilder_14_valid", "adx_wilder_14_warmup_complete", "adx_wilder_14_reason_codes",
    "signal_profile_id", "signal_profile_version", "signal_schema_id", "signal_schema_version",
    "signal_schema_ref", "sig_rsi_mr_d", "sig_rsi_mr_d_valid", "sig_rsi_mr_d_reason_codes",
    "sig_macd_momentum_d", "sig_macd_momentum_d_valid", "sig_macd_momentum_d_reason_codes",
    "sig_bollinger_mr_d", "sig_bollinger_mr_d_valid", "sig_bollinger_mr_d_reason_codes", "sig_stoch_mr_d",
    "sig_stoch_mr_d_valid", "sig_stoch_mr_d_reason_codes", "sig_cci_mr_d", "sig_cci_mr_d_valid",
    "sig_cci_mr_d_reason_codes", "sig_mfi_mr_d", "sig_mfi_mr_d_valid", "sig_mfi_mr_d_reason_codes",
    "sig_obv_momentum_d", "sig_obv_momentum_d_valid", "sig_obv_momentum_d_reason_codes", "sig_roc_momentum_d",
    "sig_roc_momentum_d_valid", "sig_roc_momentum_d_reason_codes", "state_ma200_trend_d",
    "state_ma200_trend_d_valid", "state_ma200_trend_d_reason_codes", "state_ema50_trend_d",
    "state_ema50_trend_d_valid", "state_ema50_trend_d_reason_codes", "state_atr_relative_d",
    "state_atr_relative_d_valid", "state_atr_relative_d_reason_codes", "state_adx_strength_d",
    "state_adx_strength_d_valid", "state_adx_strength_d_reason_codes", "score_rsi_mr_c", "score_rsi_mr_c_valid",
    "score_rsi_mr_c_reason_codes", "score_macd_momentum_c", "score_macd_momentum_c_valid",
    "score_macd_momentum_c_reason_codes", "score_bollinger_mr_c", "score_bollinger_mr_c_valid",
    "score_bollinger_mr_c_reason_codes", "score_stoch_mr_c", "score_stoch_mr_c_valid",
    "score_stoch_mr_c_reason_codes", "score_cci_mr_c", "score_cci_mr_c_valid", "score_cci_mr_c_reason_codes",
    "score_mfi_mr_c", "score_mfi_mr_c_valid", "score_mfi_mr_c_reason_codes", "score_obv_momentum_c",
    "score_obv_momentum_c_valid", "score_obv_momentum_c_reason_codes", "score_roc_momentum_c",
    "score_roc_momentum_c_valid", "score_roc_momentum_c_reason_codes", "score_ma200_trend_c",
    "score_ma200_trend_c_valid", "score_ma200_trend_c_reason_codes", "score_ema50_trend_c",
    "score_ema50_trend_c_valid", "score_ema50_trend_c_reason_codes", "score_atr_relative_c",
    "score_atr_relative_c_valid", "score_atr_relative_c_reason_codes", "score_adx_strength_c",
    "score_adx_strength_c_valid", "score_adx_strength_c_reason_codes", "regime_raw", "regime_effective",
    "regime_candidate", "regime_candidate_count", "regime_transition_flag", "regime_transition_from",
    "regime_transition_to", "ma200_slope_1440_pct", "trend_strength", "trend_strength_valid",
    "trend_strength_reason_codes", "volatility_relative", "volatility_relative_valid",
    "volatility_relative_reason_codes", "regime_model_id", "regime_model_version", "regime_schema_id",
    "regime_schema_version", "regime_schema_ref", "regime_valid", "regime_reason_codes", "allow_long",
    "allow_short", "data_gate_pass", "gate_state", "gate_reason_codes_long", "gate_reason_codes_short",
    "gate_profile_id", "gate_profile_version", "gate_schema_id", "gate_schema_version", "gate_schema_ref",
    "gate_valid", "gate_evaluated_at"
  ]
}
```

##### 7.9.3.4 `live`

```json
{
  "schema_id": "rcc002.view.live",
  "schema_version": "1.0.0",
  "schema_ref": "rcc002.view.live/1.0.0",
  "allowlist_sha256": "2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e",
  "allowed_producer_stages": [
    "S0_SOURCE", "S1_NORMALIZED", "S2_VALIDATED", "S3_INDICATORS", "S4_SIGNALS", "S5_REGIMES", "S6_GATES"
  ],
  "fields": [
    "source_snapshot_id", "provider", "market_type", "symbol", "interval", "source_row_id", "open_time",
    "close_time", "open", "high", "low", "close", "volume", "market_segment_id", "quality_is_observed",
    "quality_is_synthetic", "quality_has_source_conflict", "quality_gap_before", "quality_gap_after",
    "quality_timestamp_valid", "quality_ohlc_valid", "quality_volume_valid", "quality_market_values_valid",
    "quality_status", "quality_reason_codes", "quality_rule_version", "quality_gate_pass",
    "indicator_profile_id", "indicator_profile_version", "indicator_schema_id", "indicator_schema_version",
    "indicator_schema_ref", "indicator_segment_id", "sma_close_200", "sma_close_200_valid",
    "sma_close_200_warmup_complete", "sma_close_200_reason_codes", "ema_close_50", "ema_close_50_valid",
    "ema_close_50_warmup_complete", "ema_close_50_reason_codes", "rsi_wilder_14", "rsi_wilder_14_valid",
    "rsi_wilder_14_warmup_complete", "rsi_wilder_14_reason_codes", "macd_line_12_26", "macd_line_12_26_valid",
    "macd_line_12_26_warmup_complete", "macd_line_12_26_reason_codes", "macd_signal_line_12_26_9",
    "macd_signal_line_12_26_9_valid", "macd_signal_line_12_26_9_warmup_complete",
    "macd_signal_line_12_26_9_reason_codes", "macd_hist_12_26_9", "macd_hist_12_26_9_valid",
    "macd_hist_12_26_9_warmup_complete", "macd_hist_12_26_9_reason_codes", "bb_mid_20", "bb_mid_20_valid",
    "bb_mid_20_warmup_complete", "bb_mid_20_reason_codes", "bb_upper_20_2", "bb_upper_20_2_valid",
    "bb_upper_20_2_warmup_complete", "bb_upper_20_2_reason_codes", "bb_lower_20_2", "bb_lower_20_2_valid",
    "bb_lower_20_2_warmup_complete", "bb_lower_20_2_reason_codes", "bb_width_20_2", "bb_width_20_2_valid",
    "bb_width_20_2_warmup_complete", "bb_width_20_2_reason_codes", "stoch_k_14", "stoch_k_14_valid",
    "stoch_k_14_warmup_complete", "stoch_k_14_reason_codes", "true_range", "true_range_valid",
    "true_range_warmup_complete", "true_range_reason_codes", "atr_wilder_14", "atr_wilder_14_valid",
    "atr_wilder_14_warmup_complete", "atr_wilder_14_reason_codes", "roc_close_12_pct", "roc_close_12_pct_valid",
    "roc_close_12_pct_warmup_complete", "roc_close_12_pct_reason_codes", "obv", "obv_valid",
    "obv_warmup_complete", "obv_reason_codes", "typical_price", "typical_price_valid",
    "typical_price_warmup_complete", "typical_price_reason_codes", "cci_20", "cci_20_valid",
    "cci_20_warmup_complete", "cci_20_reason_codes", "mfi_14", "mfi_14_valid", "mfi_14_warmup_complete",
    "mfi_14_reason_codes", "plus_di_14", "plus_di_14_valid", "plus_di_14_warmup_complete",
    "plus_di_14_reason_codes", "minus_di_14", "minus_di_14_valid", "minus_di_14_warmup_complete",
    "minus_di_14_reason_codes", "dx_14", "dx_14_valid", "dx_14_warmup_complete", "dx_14_reason_codes",
    "adx_wilder_14", "adx_wilder_14_valid", "adx_wilder_14_warmup_complete", "adx_wilder_14_reason_codes",
    "signal_profile_id", "signal_profile_version", "signal_schema_id", "signal_schema_version",
    "signal_schema_ref", "sig_rsi_mr_d", "sig_rsi_mr_d_valid", "sig_rsi_mr_d_reason_codes",
    "sig_macd_momentum_d", "sig_macd_momentum_d_valid", "sig_macd_momentum_d_reason_codes",
    "sig_bollinger_mr_d", "sig_bollinger_mr_d_valid", "sig_bollinger_mr_d_reason_codes", "sig_stoch_mr_d",
    "sig_stoch_mr_d_valid", "sig_stoch_mr_d_reason_codes", "sig_cci_mr_d", "sig_cci_mr_d_valid",
    "sig_cci_mr_d_reason_codes", "sig_mfi_mr_d", "sig_mfi_mr_d_valid", "sig_mfi_mr_d_reason_codes",
    "sig_obv_momentum_d", "sig_obv_momentum_d_valid", "sig_obv_momentum_d_reason_codes", "sig_roc_momentum_d",
    "sig_roc_momentum_d_valid", "sig_roc_momentum_d_reason_codes", "state_ma200_trend_d",
    "state_ma200_trend_d_valid", "state_ma200_trend_d_reason_codes", "state_ema50_trend_d",
    "state_ema50_trend_d_valid", "state_ema50_trend_d_reason_codes", "state_atr_relative_d",
    "state_atr_relative_d_valid", "state_atr_relative_d_reason_codes", "state_adx_strength_d",
    "state_adx_strength_d_valid", "state_adx_strength_d_reason_codes", "score_rsi_mr_c", "score_rsi_mr_c_valid",
    "score_rsi_mr_c_reason_codes", "score_macd_momentum_c", "score_macd_momentum_c_valid",
    "score_macd_momentum_c_reason_codes", "score_bollinger_mr_c", "score_bollinger_mr_c_valid",
    "score_bollinger_mr_c_reason_codes", "score_stoch_mr_c", "score_stoch_mr_c_valid",
    "score_stoch_mr_c_reason_codes", "score_cci_mr_c", "score_cci_mr_c_valid", "score_cci_mr_c_reason_codes",
    "score_mfi_mr_c", "score_mfi_mr_c_valid", "score_mfi_mr_c_reason_codes", "score_obv_momentum_c",
    "score_obv_momentum_c_valid", "score_obv_momentum_c_reason_codes", "score_roc_momentum_c",
    "score_roc_momentum_c_valid", "score_roc_momentum_c_reason_codes", "score_ma200_trend_c",
    "score_ma200_trend_c_valid", "score_ma200_trend_c_reason_codes", "score_ema50_trend_c",
    "score_ema50_trend_c_valid", "score_ema50_trend_c_reason_codes", "score_atr_relative_c",
    "score_atr_relative_c_valid", "score_atr_relative_c_reason_codes", "score_adx_strength_c",
    "score_adx_strength_c_valid", "score_adx_strength_c_reason_codes", "regime_raw", "regime_effective",
    "regime_candidate", "regime_candidate_count", "regime_transition_flag", "regime_transition_from",
    "regime_transition_to", "ma200_slope_1440_pct", "trend_strength", "trend_strength_valid",
    "trend_strength_reason_codes", "volatility_relative", "volatility_relative_valid",
    "volatility_relative_reason_codes", "regime_model_id", "regime_model_version", "regime_schema_id",
    "regime_schema_version", "regime_schema_ref", "regime_valid", "regime_reason_codes", "allow_long",
    "allow_short", "data_gate_pass", "gate_state", "gate_reason_codes_long", "gate_reason_codes_short",
    "gate_profile_id", "gate_profile_version", "gate_schema_id", "gate_schema_version", "gate_schema_ref",
    "gate_valid", "gate_evaluated_at"
  ]
}
```

##### 7.9.3.5 `label-research`

```json
{
  "schema_id": "rcc002.view.label-research",
  "schema_version": "1.0.0",
  "schema_ref": "rcc002.view.label-research/1.0.0",
  "allowlist_sha256": "0e223d60ed4139f73194f1cb3b886a8eface9229183ad522a093e966827518cc",
  "allowed_producer_stages": [
    "S0_SOURCE", "S1_NORMALIZED", "S2_VALIDATED", "S3_INDICATORS", "S4_SIGNALS", "S5_REGIMES", "S6_GATES",
    "S7_LABELS"
  ],
  "fields": [
    "source_snapshot_id", "provider", "market_type", "symbol", "interval", "source_row_id", "open_time",
    "close_time", "open", "high", "low", "close", "volume", "market_segment_id", "quality_is_observed",
    "quality_is_synthetic", "quality_has_source_conflict", "quality_gap_before", "quality_gap_after",
    "quality_timestamp_valid", "quality_ohlc_valid", "quality_volume_valid", "quality_market_values_valid",
    "quality_status", "quality_reason_codes", "quality_rule_version", "quality_gate_pass",
    "indicator_profile_id", "indicator_profile_version", "indicator_schema_id", "indicator_schema_version",
    "indicator_schema_ref", "indicator_segment_id", "sma_close_200", "sma_close_200_valid",
    "sma_close_200_warmup_complete", "sma_close_200_reason_codes", "ema_close_50", "ema_close_50_valid",
    "ema_close_50_warmup_complete", "ema_close_50_reason_codes", "rsi_wilder_14", "rsi_wilder_14_valid",
    "rsi_wilder_14_warmup_complete", "rsi_wilder_14_reason_codes", "macd_line_12_26", "macd_line_12_26_valid",
    "macd_line_12_26_warmup_complete", "macd_line_12_26_reason_codes", "macd_signal_line_12_26_9",
    "macd_signal_line_12_26_9_valid", "macd_signal_line_12_26_9_warmup_complete",
    "macd_signal_line_12_26_9_reason_codes", "macd_hist_12_26_9", "macd_hist_12_26_9_valid",
    "macd_hist_12_26_9_warmup_complete", "macd_hist_12_26_9_reason_codes", "bb_mid_20", "bb_mid_20_valid",
    "bb_mid_20_warmup_complete", "bb_mid_20_reason_codes", "bb_upper_20_2", "bb_upper_20_2_valid",
    "bb_upper_20_2_warmup_complete", "bb_upper_20_2_reason_codes", "bb_lower_20_2", "bb_lower_20_2_valid",
    "bb_lower_20_2_warmup_complete", "bb_lower_20_2_reason_codes", "bb_width_20_2", "bb_width_20_2_valid",
    "bb_width_20_2_warmup_complete", "bb_width_20_2_reason_codes", "stoch_k_14", "stoch_k_14_valid",
    "stoch_k_14_warmup_complete", "stoch_k_14_reason_codes", "true_range", "true_range_valid",
    "true_range_warmup_complete", "true_range_reason_codes", "atr_wilder_14", "atr_wilder_14_valid",
    "atr_wilder_14_warmup_complete", "atr_wilder_14_reason_codes", "roc_close_12_pct", "roc_close_12_pct_valid",
    "roc_close_12_pct_warmup_complete", "roc_close_12_pct_reason_codes", "obv", "obv_valid",
    "obv_warmup_complete", "obv_reason_codes", "typical_price", "typical_price_valid",
    "typical_price_warmup_complete", "typical_price_reason_codes", "cci_20", "cci_20_valid",
    "cci_20_warmup_complete", "cci_20_reason_codes", "mfi_14", "mfi_14_valid", "mfi_14_warmup_complete",
    "mfi_14_reason_codes", "plus_di_14", "plus_di_14_valid", "plus_di_14_warmup_complete",
    "plus_di_14_reason_codes", "minus_di_14", "minus_di_14_valid", "minus_di_14_warmup_complete",
    "minus_di_14_reason_codes", "dx_14", "dx_14_valid", "dx_14_warmup_complete", "dx_14_reason_codes",
    "adx_wilder_14", "adx_wilder_14_valid", "adx_wilder_14_warmup_complete", "adx_wilder_14_reason_codes",
    "signal_profile_id", "signal_profile_version", "signal_schema_id", "signal_schema_version",
    "signal_schema_ref", "sig_rsi_mr_d", "sig_rsi_mr_d_valid", "sig_rsi_mr_d_reason_codes",
    "sig_macd_momentum_d", "sig_macd_momentum_d_valid", "sig_macd_momentum_d_reason_codes",
    "sig_bollinger_mr_d", "sig_bollinger_mr_d_valid", "sig_bollinger_mr_d_reason_codes", "sig_stoch_mr_d",
    "sig_stoch_mr_d_valid", "sig_stoch_mr_d_reason_codes", "sig_cci_mr_d", "sig_cci_mr_d_valid",
    "sig_cci_mr_d_reason_codes", "sig_mfi_mr_d", "sig_mfi_mr_d_valid", "sig_mfi_mr_d_reason_codes",
    "sig_obv_momentum_d", "sig_obv_momentum_d_valid", "sig_obv_momentum_d_reason_codes", "sig_roc_momentum_d",
    "sig_roc_momentum_d_valid", "sig_roc_momentum_d_reason_codes", "state_ma200_trend_d",
    "state_ma200_trend_d_valid", "state_ma200_trend_d_reason_codes", "state_ema50_trend_d",
    "state_ema50_trend_d_valid", "state_ema50_trend_d_reason_codes", "state_atr_relative_d",
    "state_atr_relative_d_valid", "state_atr_relative_d_reason_codes", "state_adx_strength_d",
    "state_adx_strength_d_valid", "state_adx_strength_d_reason_codes", "score_rsi_mr_c", "score_rsi_mr_c_valid",
    "score_rsi_mr_c_reason_codes", "score_macd_momentum_c", "score_macd_momentum_c_valid",
    "score_macd_momentum_c_reason_codes", "score_bollinger_mr_c", "score_bollinger_mr_c_valid",
    "score_bollinger_mr_c_reason_codes", "score_stoch_mr_c", "score_stoch_mr_c_valid",
    "score_stoch_mr_c_reason_codes", "score_cci_mr_c", "score_cci_mr_c_valid", "score_cci_mr_c_reason_codes",
    "score_mfi_mr_c", "score_mfi_mr_c_valid", "score_mfi_mr_c_reason_codes", "score_obv_momentum_c",
    "score_obv_momentum_c_valid", "score_obv_momentum_c_reason_codes", "score_roc_momentum_c",
    "score_roc_momentum_c_valid", "score_roc_momentum_c_reason_codes", "score_ma200_trend_c",
    "score_ma200_trend_c_valid", "score_ma200_trend_c_reason_codes", "score_ema50_trend_c",
    "score_ema50_trend_c_valid", "score_ema50_trend_c_reason_codes", "score_atr_relative_c",
    "score_atr_relative_c_valid", "score_atr_relative_c_reason_codes", "score_adx_strength_c",
    "score_adx_strength_c_valid", "score_adx_strength_c_reason_codes", "regime_raw", "regime_effective",
    "regime_candidate", "regime_candidate_count", "regime_transition_flag", "regime_transition_from",
    "regime_transition_to", "ma200_slope_1440_pct", "trend_strength", "trend_strength_valid",
    "trend_strength_reason_codes", "volatility_relative", "volatility_relative_valid",
    "volatility_relative_reason_codes", "regime_model_id", "regime_model_version", "regime_schema_id",
    "regime_schema_version", "regime_schema_ref", "regime_valid", "regime_reason_codes", "allow_long",
    "allow_short", "data_gate_pass", "gate_state", "gate_reason_codes_long", "gate_reason_codes_short",
    "gate_profile_id", "gate_profile_version", "gate_schema_id", "gate_schema_version", "gate_schema_ref",
    "gate_valid", "gate_evaluated_at", "label_profile_id", "label_profile_version", "label_schema_id",
    "label_schema_version", "label_schema_ref", "horizon_registry_id", "horizon_registry_version",
    "cost_profile_id", "cost_profile_version", "barrier_profile_id", "barrier_profile_version",
    "label_reason_code_registry_version", "label_numeric_profile_id", "label_numeric_profile_version",
    "label_horizon_bars_h001", "label_available_at_h001", "fwd_cc_valid_h001", "fwd_cc_reason_codes_h001",
    "fwd_cc_label_segment_id_h001", "fwd_cc_long_ret_h001", "fwd_cc_short_ret_h001", "fwd_cc_log_ret_h001",
    "fwd_cc_short_log_ret_h001", "fwd_noc_valid_h001", "fwd_noc_reason_codes_h001",
    "fwd_noc_label_segment_id_h001", "fwd_noc_long_ret_h001", "fwd_noc_short_ret_h001",
    "fwd_noc_long_net_proxy_fee_rt_0004_h001", "fwd_noc_short_net_proxy_fee_rt_0004_h001",
    "fwd_excursion_valid_h001", "fwd_excursion_reason_codes_h001", "fwd_excursion_label_segment_id_h001",
    "fwd_long_mfe_h001", "fwd_long_mae_h001", "fwd_short_mfe_h001", "fwd_short_mae_h001",
    "fwd_long_mfe_first_bar_h001", "fwd_long_mae_first_bar_h001", "fwd_short_mfe_first_bar_h001",
    "fwd_short_mae_first_bar_h001", "label_cc_direction_valid_h001", "label_cc_direction_reason_codes_h001",
    "label_cc_direction_segment_id_h001", "label_cc_long_direction_h001", "label_cc_short_direction_h001",
    "label_noc_direction_valid_h001", "label_noc_direction_reason_codes_h001",
    "label_noc_direction_segment_id_h001", "label_noc_long_direction_h001", "label_noc_short_direction_h001",
    "label_noc_long_net_proxy_fee_rt_0004_direction_h001",
    "label_noc_short_net_proxy_fee_rt_0004_direction_h001", "barrier_valid_h001", "barrier_reason_codes_h001",
    "barrier_label_segment_id_h001", "barrier_long_outcome_tp050_sl020_h001",
    "barrier_short_outcome_tp050_sl020_h001", "barrier_long_first_hit_bar_tp050_sl020_h001",
    "barrier_short_first_hit_bar_tp050_sl020_h001", "barrier_long_first_hit_time_tp050_sl020_h001",
    "barrier_short_first_hit_time_tp050_sl020_h001", "label_horizon_bars_h005", "label_available_at_h005",
    "fwd_cc_valid_h005", "fwd_cc_reason_codes_h005", "fwd_cc_label_segment_id_h005", "fwd_cc_long_ret_h005",
    "fwd_cc_short_ret_h005", "fwd_cc_log_ret_h005", "fwd_cc_short_log_ret_h005", "fwd_noc_valid_h005",
    "fwd_noc_reason_codes_h005", "fwd_noc_label_segment_id_h005", "fwd_noc_long_ret_h005",
    "fwd_noc_short_ret_h005", "fwd_noc_long_net_proxy_fee_rt_0004_h005",
    "fwd_noc_short_net_proxy_fee_rt_0004_h005", "fwd_excursion_valid_h005", "fwd_excursion_reason_codes_h005",
    "fwd_excursion_label_segment_id_h005", "fwd_long_mfe_h005", "fwd_long_mae_h005", "fwd_short_mfe_h005",
    "fwd_short_mae_h005", "fwd_long_mfe_first_bar_h005", "fwd_long_mae_first_bar_h005",
    "fwd_short_mfe_first_bar_h005", "fwd_short_mae_first_bar_h005", "label_cc_direction_valid_h005",
    "label_cc_direction_reason_codes_h005", "label_cc_direction_segment_id_h005",
    "label_cc_long_direction_h005", "label_cc_short_direction_h005", "label_noc_direction_valid_h005",
    "label_noc_direction_reason_codes_h005", "label_noc_direction_segment_id_h005",
    "label_noc_long_direction_h005", "label_noc_short_direction_h005",
    "label_noc_long_net_proxy_fee_rt_0004_direction_h005",
    "label_noc_short_net_proxy_fee_rt_0004_direction_h005", "barrier_valid_h005", "barrier_reason_codes_h005",
    "barrier_label_segment_id_h005", "barrier_long_outcome_tp050_sl020_h005",
    "barrier_short_outcome_tp050_sl020_h005", "barrier_long_first_hit_bar_tp050_sl020_h005",
    "barrier_short_first_hit_bar_tp050_sl020_h005", "barrier_long_first_hit_time_tp050_sl020_h005",
    "barrier_short_first_hit_time_tp050_sl020_h005", "label_horizon_bars_h015", "label_available_at_h015",
    "fwd_cc_valid_h015", "fwd_cc_reason_codes_h015", "fwd_cc_label_segment_id_h015", "fwd_cc_long_ret_h015",
    "fwd_cc_short_ret_h015", "fwd_cc_log_ret_h015", "fwd_cc_short_log_ret_h015", "fwd_noc_valid_h015",
    "fwd_noc_reason_codes_h015", "fwd_noc_label_segment_id_h015", "fwd_noc_long_ret_h015",
    "fwd_noc_short_ret_h015", "fwd_noc_long_net_proxy_fee_rt_0004_h015",
    "fwd_noc_short_net_proxy_fee_rt_0004_h015", "fwd_excursion_valid_h015", "fwd_excursion_reason_codes_h015",
    "fwd_excursion_label_segment_id_h015", "fwd_long_mfe_h015", "fwd_long_mae_h015", "fwd_short_mfe_h015",
    "fwd_short_mae_h015", "fwd_long_mfe_first_bar_h015", "fwd_long_mae_first_bar_h015",
    "fwd_short_mfe_first_bar_h015", "fwd_short_mae_first_bar_h015", "label_cc_direction_valid_h015",
    "label_cc_direction_reason_codes_h015", "label_cc_direction_segment_id_h015",
    "label_cc_long_direction_h015", "label_cc_short_direction_h015", "label_noc_direction_valid_h015",
    "label_noc_direction_reason_codes_h015", "label_noc_direction_segment_id_h015",
    "label_noc_long_direction_h015", "label_noc_short_direction_h015",
    "label_noc_long_net_proxy_fee_rt_0004_direction_h015",
    "label_noc_short_net_proxy_fee_rt_0004_direction_h015", "barrier_valid_h015", "barrier_reason_codes_h015",
    "barrier_label_segment_id_h015", "barrier_long_outcome_tp050_sl020_h015",
    "barrier_short_outcome_tp050_sl020_h015", "barrier_long_first_hit_bar_tp050_sl020_h015",
    "barrier_short_first_hit_bar_tp050_sl020_h015", "barrier_long_first_hit_time_tp050_sl020_h015",
    "barrier_short_first_hit_time_tp050_sl020_h015", "label_horizon_bars_h060", "label_available_at_h060",
    "fwd_cc_valid_h060", "fwd_cc_reason_codes_h060", "fwd_cc_label_segment_id_h060", "fwd_cc_long_ret_h060",
    "fwd_cc_short_ret_h060", "fwd_cc_log_ret_h060", "fwd_cc_short_log_ret_h060", "fwd_noc_valid_h060",
    "fwd_noc_reason_codes_h060", "fwd_noc_label_segment_id_h060", "fwd_noc_long_ret_h060",
    "fwd_noc_short_ret_h060", "fwd_noc_long_net_proxy_fee_rt_0004_h060",
    "fwd_noc_short_net_proxy_fee_rt_0004_h060", "fwd_excursion_valid_h060", "fwd_excursion_reason_codes_h060",
    "fwd_excursion_label_segment_id_h060", "fwd_long_mfe_h060", "fwd_long_mae_h060", "fwd_short_mfe_h060",
    "fwd_short_mae_h060", "fwd_long_mfe_first_bar_h060", "fwd_long_mae_first_bar_h060",
    "fwd_short_mfe_first_bar_h060", "fwd_short_mae_first_bar_h060", "label_cc_direction_valid_h060",
    "label_cc_direction_reason_codes_h060", "label_cc_direction_segment_id_h060",
    "label_cc_long_direction_h060", "label_cc_short_direction_h060", "label_noc_direction_valid_h060",
    "label_noc_direction_reason_codes_h060", "label_noc_direction_segment_id_h060",
    "label_noc_long_direction_h060", "label_noc_short_direction_h060",
    "label_noc_long_net_proxy_fee_rt_0004_direction_h060",
    "label_noc_short_net_proxy_fee_rt_0004_direction_h060", "barrier_valid_h060", "barrier_reason_codes_h060",
    "barrier_label_segment_id_h060", "barrier_long_outcome_tp050_sl020_h060",
    "barrier_short_outcome_tp050_sl020_h060", "barrier_long_first_hit_bar_tp050_sl020_h060",
    "barrier_short_first_hit_bar_tp050_sl020_h060", "barrier_long_first_hit_time_tp050_sl020_h060",
    "barrier_short_first_hit_time_tp050_sl020_h060", "label_horizon_bars_h240", "label_available_at_h240",
    "fwd_cc_valid_h240", "fwd_cc_reason_codes_h240", "fwd_cc_label_segment_id_h240", "fwd_cc_long_ret_h240",
    "fwd_cc_short_ret_h240", "fwd_cc_log_ret_h240", "fwd_cc_short_log_ret_h240", "fwd_noc_valid_h240",
    "fwd_noc_reason_codes_h240", "fwd_noc_label_segment_id_h240", "fwd_noc_long_ret_h240",
    "fwd_noc_short_ret_h240", "fwd_noc_long_net_proxy_fee_rt_0004_h240",
    "fwd_noc_short_net_proxy_fee_rt_0004_h240", "fwd_excursion_valid_h240", "fwd_excursion_reason_codes_h240",
    "fwd_excursion_label_segment_id_h240", "fwd_long_mfe_h240", "fwd_long_mae_h240", "fwd_short_mfe_h240",
    "fwd_short_mae_h240", "fwd_long_mfe_first_bar_h240", "fwd_long_mae_first_bar_h240",
    "fwd_short_mfe_first_bar_h240", "fwd_short_mae_first_bar_h240", "label_cc_direction_valid_h240",
    "label_cc_direction_reason_codes_h240", "label_cc_direction_segment_id_h240",
    "label_cc_long_direction_h240", "label_cc_short_direction_h240", "label_noc_direction_valid_h240",
    "label_noc_direction_reason_codes_h240", "label_noc_direction_segment_id_h240",
    "label_noc_long_direction_h240", "label_noc_short_direction_h240",
    "label_noc_long_net_proxy_fee_rt_0004_direction_h240",
    "label_noc_short_net_proxy_fee_rt_0004_direction_h240", "barrier_valid_h240", "barrier_reason_codes_h240",
    "barrier_label_segment_id_h240", "barrier_long_outcome_tp050_sl020_h240",
    "barrier_short_outcome_tp050_sl020_h240", "barrier_long_first_hit_bar_tp050_sl020_h240",
    "barrier_short_first_hit_bar_tp050_sl020_h240", "barrier_long_first_hit_time_tp050_sl020_h240",
    "barrier_short_first_hit_time_tp050_sl020_h240", "label_horizon_bars_h1440", "label_available_at_h1440",
    "fwd_cc_valid_h1440", "fwd_cc_reason_codes_h1440", "fwd_cc_label_segment_id_h1440", "fwd_cc_long_ret_h1440",
    "fwd_cc_short_ret_h1440", "fwd_cc_log_ret_h1440", "fwd_cc_short_log_ret_h1440", "fwd_noc_valid_h1440",
    "fwd_noc_reason_codes_h1440", "fwd_noc_label_segment_id_h1440", "fwd_noc_long_ret_h1440",
    "fwd_noc_short_ret_h1440", "fwd_noc_long_net_proxy_fee_rt_0004_h1440",
    "fwd_noc_short_net_proxy_fee_rt_0004_h1440", "fwd_excursion_valid_h1440",
    "fwd_excursion_reason_codes_h1440", "fwd_excursion_label_segment_id_h1440", "fwd_long_mfe_h1440",
    "fwd_long_mae_h1440", "fwd_short_mfe_h1440", "fwd_short_mae_h1440", "fwd_long_mfe_first_bar_h1440",
    "fwd_long_mae_first_bar_h1440", "fwd_short_mfe_first_bar_h1440", "fwd_short_mae_first_bar_h1440",
    "label_cc_direction_valid_h1440", "label_cc_direction_reason_codes_h1440",
    "label_cc_direction_segment_id_h1440", "label_cc_long_direction_h1440", "label_cc_short_direction_h1440",
    "label_noc_direction_valid_h1440", "label_noc_direction_reason_codes_h1440",
    "label_noc_direction_segment_id_h1440", "label_noc_long_direction_h1440", "label_noc_short_direction_h1440",
    "label_noc_long_net_proxy_fee_rt_0004_direction_h1440",
    "label_noc_short_net_proxy_fee_rt_0004_direction_h1440", "barrier_valid_h1440",
    "barrier_reason_codes_h1440", "barrier_label_segment_id_h1440", "barrier_long_outcome_tp050_sl020_h1440",
    "barrier_short_outcome_tp050_sl020_h1440", "barrier_long_first_hit_bar_tp050_sl020_h1440",
    "barrier_short_first_hit_bar_tp050_sl020_h1440", "barrier_long_first_hit_time_tp050_sl020_h1440",
    "barrier_short_first_hit_time_tp050_sl020_h1440"
  ]
}
```

##### 7.9.3.6 `audit`

```json
{
  "schema_id": "rcc002.view.audit",
  "schema_version": "1.0.0",
  "schema_ref": "rcc002.view.audit/1.0.0",
  "allowlist_sha256": "3c29f3219e65ca87df199a52dc8d15b54a6ea28884a863d1479d27e8a2401b56",
  "allowed_producer_stages": [
    "S0_SOURCE", "S1_NORMALIZED", "S2_VALIDATED", "S3_INDICATORS", "S4_SIGNALS", "S5_REGIMES", "S6_GATES",
    "S7_LABELS", "S8_EXPORT"
  ],
  "fields": [
    "source_snapshot_id", "provider", "market_type", "symbol", "interval", "source_row_id", "open_time",
    "close_time", "open", "high", "low", "close", "volume", "market_segment_id", "quality_is_observed",
    "quality_is_synthetic", "quality_has_source_conflict", "quality_gap_before", "quality_gap_after",
    "quality_timestamp_valid", "quality_ohlc_valid", "quality_volume_valid", "quality_market_values_valid",
    "quality_status", "quality_reason_codes", "quality_rule_version", "quality_gate_pass",
    "indicator_profile_id", "indicator_profile_version", "indicator_schema_id", "indicator_schema_version",
    "indicator_schema_ref", "indicator_segment_id", "sma_close_200", "sma_close_200_valid",
    "sma_close_200_warmup_complete", "sma_close_200_reason_codes", "ema_close_50", "ema_close_50_valid",
    "ema_close_50_warmup_complete", "ema_close_50_reason_codes", "rsi_wilder_14", "rsi_wilder_14_valid",
    "rsi_wilder_14_warmup_complete", "rsi_wilder_14_reason_codes", "macd_line_12_26", "macd_line_12_26_valid",
    "macd_line_12_26_warmup_complete", "macd_line_12_26_reason_codes", "macd_signal_line_12_26_9",
    "macd_signal_line_12_26_9_valid", "macd_signal_line_12_26_9_warmup_complete",
    "macd_signal_line_12_26_9_reason_codes", "macd_hist_12_26_9", "macd_hist_12_26_9_valid",
    "macd_hist_12_26_9_warmup_complete", "macd_hist_12_26_9_reason_codes", "bb_mid_20", "bb_mid_20_valid",
    "bb_mid_20_warmup_complete", "bb_mid_20_reason_codes", "bb_upper_20_2", "bb_upper_20_2_valid",
    "bb_upper_20_2_warmup_complete", "bb_upper_20_2_reason_codes", "bb_lower_20_2", "bb_lower_20_2_valid",
    "bb_lower_20_2_warmup_complete", "bb_lower_20_2_reason_codes", "bb_width_20_2", "bb_width_20_2_valid",
    "bb_width_20_2_warmup_complete", "bb_width_20_2_reason_codes", "stoch_k_14", "stoch_k_14_valid",
    "stoch_k_14_warmup_complete", "stoch_k_14_reason_codes", "true_range", "true_range_valid",
    "true_range_warmup_complete", "true_range_reason_codes", "atr_wilder_14", "atr_wilder_14_valid",
    "atr_wilder_14_warmup_complete", "atr_wilder_14_reason_codes", "roc_close_12_pct", "roc_close_12_pct_valid",
    "roc_close_12_pct_warmup_complete", "roc_close_12_pct_reason_codes", "obv", "obv_valid",
    "obv_warmup_complete", "obv_reason_codes", "typical_price", "typical_price_valid",
    "typical_price_warmup_complete", "typical_price_reason_codes", "cci_20", "cci_20_valid",
    "cci_20_warmup_complete", "cci_20_reason_codes", "mfi_14", "mfi_14_valid", "mfi_14_warmup_complete",
    "mfi_14_reason_codes", "plus_di_14", "plus_di_14_valid", "plus_di_14_warmup_complete",
    "plus_di_14_reason_codes", "minus_di_14", "minus_di_14_valid", "minus_di_14_warmup_complete",
    "minus_di_14_reason_codes", "dx_14", "dx_14_valid", "dx_14_warmup_complete", "dx_14_reason_codes",
    "adx_wilder_14", "adx_wilder_14_valid", "adx_wilder_14_warmup_complete", "adx_wilder_14_reason_codes",
    "signal_profile_id", "signal_profile_version", "signal_schema_id", "signal_schema_version",
    "signal_schema_ref", "sig_rsi_mr_d", "sig_rsi_mr_d_valid", "sig_rsi_mr_d_reason_codes",
    "sig_macd_momentum_d", "sig_macd_momentum_d_valid", "sig_macd_momentum_d_reason_codes",
    "sig_bollinger_mr_d", "sig_bollinger_mr_d_valid", "sig_bollinger_mr_d_reason_codes", "sig_stoch_mr_d",
    "sig_stoch_mr_d_valid", "sig_stoch_mr_d_reason_codes", "sig_cci_mr_d", "sig_cci_mr_d_valid",
    "sig_cci_mr_d_reason_codes", "sig_mfi_mr_d", "sig_mfi_mr_d_valid", "sig_mfi_mr_d_reason_codes",
    "sig_obv_momentum_d", "sig_obv_momentum_d_valid", "sig_obv_momentum_d_reason_codes", "sig_roc_momentum_d",
    "sig_roc_momentum_d_valid", "sig_roc_momentum_d_reason_codes", "state_ma200_trend_d",
    "state_ma200_trend_d_valid", "state_ma200_trend_d_reason_codes", "state_ema50_trend_d",
    "state_ema50_trend_d_valid", "state_ema50_trend_d_reason_codes", "state_atr_relative_d",
    "state_atr_relative_d_valid", "state_atr_relative_d_reason_codes", "state_adx_strength_d",
    "state_adx_strength_d_valid", "state_adx_strength_d_reason_codes", "score_rsi_mr_c", "score_rsi_mr_c_valid",
    "score_rsi_mr_c_reason_codes", "score_macd_momentum_c", "score_macd_momentum_c_valid",
    "score_macd_momentum_c_reason_codes", "score_bollinger_mr_c", "score_bollinger_mr_c_valid",
    "score_bollinger_mr_c_reason_codes", "score_stoch_mr_c", "score_stoch_mr_c_valid",
    "score_stoch_mr_c_reason_codes", "score_cci_mr_c", "score_cci_mr_c_valid", "score_cci_mr_c_reason_codes",
    "score_mfi_mr_c", "score_mfi_mr_c_valid", "score_mfi_mr_c_reason_codes", "score_obv_momentum_c",
    "score_obv_momentum_c_valid", "score_obv_momentum_c_reason_codes", "score_roc_momentum_c",
    "score_roc_momentum_c_valid", "score_roc_momentum_c_reason_codes", "score_ma200_trend_c",
    "score_ma200_trend_c_valid", "score_ma200_trend_c_reason_codes", "score_ema50_trend_c",
    "score_ema50_trend_c_valid", "score_ema50_trend_c_reason_codes", "score_atr_relative_c",
    "score_atr_relative_c_valid", "score_atr_relative_c_reason_codes", "score_adx_strength_c",
    "score_adx_strength_c_valid", "score_adx_strength_c_reason_codes", "regime_raw", "regime_effective",
    "regime_candidate", "regime_candidate_count", "regime_transition_flag", "regime_transition_from",
    "regime_transition_to", "ma200_slope_1440_pct", "trend_strength", "trend_strength_valid",
    "trend_strength_reason_codes", "volatility_relative", "volatility_relative_valid",
    "volatility_relative_reason_codes", "regime_model_id", "regime_model_version", "regime_schema_id",
    "regime_schema_version", "regime_schema_ref", "regime_valid", "regime_reason_codes", "allow_long",
    "allow_short", "data_gate_pass", "gate_state", "gate_reason_codes_long", "gate_reason_codes_short",
    "gate_profile_id", "gate_profile_version", "gate_schema_id", "gate_schema_version", "gate_schema_ref",
    "gate_valid", "gate_evaluated_at", "label_profile_id", "label_profile_version", "label_schema_id",
    "label_schema_version", "label_schema_ref", "horizon_registry_id", "horizon_registry_version",
    "cost_profile_id", "cost_profile_version", "barrier_profile_id", "barrier_profile_version",
    "label_reason_code_registry_version", "label_numeric_profile_id", "label_numeric_profile_version",
    "label_horizon_bars_h001", "label_available_at_h001", "fwd_cc_valid_h001", "fwd_cc_reason_codes_h001",
    "fwd_cc_label_segment_id_h001", "fwd_cc_long_ret_h001", "fwd_cc_short_ret_h001", "fwd_cc_log_ret_h001",
    "fwd_cc_short_log_ret_h001", "fwd_noc_valid_h001", "fwd_noc_reason_codes_h001",
    "fwd_noc_label_segment_id_h001", "fwd_noc_long_ret_h001", "fwd_noc_short_ret_h001",
    "fwd_noc_long_net_proxy_fee_rt_0004_h001", "fwd_noc_short_net_proxy_fee_rt_0004_h001",
    "fwd_excursion_valid_h001", "fwd_excursion_reason_codes_h001", "fwd_excursion_label_segment_id_h001",
    "fwd_long_mfe_h001", "fwd_long_mae_h001", "fwd_short_mfe_h001", "fwd_short_mae_h001",
    "fwd_long_mfe_first_bar_h001", "fwd_long_mae_first_bar_h001", "fwd_short_mfe_first_bar_h001",
    "fwd_short_mae_first_bar_h001", "label_cc_direction_valid_h001", "label_cc_direction_reason_codes_h001",
    "label_cc_direction_segment_id_h001", "label_cc_long_direction_h001", "label_cc_short_direction_h001",
    "label_noc_direction_valid_h001", "label_noc_direction_reason_codes_h001",
    "label_noc_direction_segment_id_h001", "label_noc_long_direction_h001", "label_noc_short_direction_h001",
    "label_noc_long_net_proxy_fee_rt_0004_direction_h001",
    "label_noc_short_net_proxy_fee_rt_0004_direction_h001", "barrier_valid_h001", "barrier_reason_codes_h001",
    "barrier_label_segment_id_h001", "barrier_long_outcome_tp050_sl020_h001",
    "barrier_short_outcome_tp050_sl020_h001", "barrier_long_first_hit_bar_tp050_sl020_h001",
    "barrier_short_first_hit_bar_tp050_sl020_h001", "barrier_long_first_hit_time_tp050_sl020_h001",
    "barrier_short_first_hit_time_tp050_sl020_h001", "label_horizon_bars_h005", "label_available_at_h005",
    "fwd_cc_valid_h005", "fwd_cc_reason_codes_h005", "fwd_cc_label_segment_id_h005", "fwd_cc_long_ret_h005",
    "fwd_cc_short_ret_h005", "fwd_cc_log_ret_h005", "fwd_cc_short_log_ret_h005", "fwd_noc_valid_h005",
    "fwd_noc_reason_codes_h005", "fwd_noc_label_segment_id_h005", "fwd_noc_long_ret_h005",
    "fwd_noc_short_ret_h005", "fwd_noc_long_net_proxy_fee_rt_0004_h005",
    "fwd_noc_short_net_proxy_fee_rt_0004_h005", "fwd_excursion_valid_h005", "fwd_excursion_reason_codes_h005",
    "fwd_excursion_label_segment_id_h005", "fwd_long_mfe_h005", "fwd_long_mae_h005", "fwd_short_mfe_h005",
    "fwd_short_mae_h005", "fwd_long_mfe_first_bar_h005", "fwd_long_mae_first_bar_h005",
    "fwd_short_mfe_first_bar_h005", "fwd_short_mae_first_bar_h005", "label_cc_direction_valid_h005",
    "label_cc_direction_reason_codes_h005", "label_cc_direction_segment_id_h005",
    "label_cc_long_direction_h005", "label_cc_short_direction_h005", "label_noc_direction_valid_h005",
    "label_noc_direction_reason_codes_h005", "label_noc_direction_segment_id_h005",
    "label_noc_long_direction_h005", "label_noc_short_direction_h005",
    "label_noc_long_net_proxy_fee_rt_0004_direction_h005",
    "label_noc_short_net_proxy_fee_rt_0004_direction_h005", "barrier_valid_h005", "barrier_reason_codes_h005",
    "barrier_label_segment_id_h005", "barrier_long_outcome_tp050_sl020_h005",
    "barrier_short_outcome_tp050_sl020_h005", "barrier_long_first_hit_bar_tp050_sl020_h005",
    "barrier_short_first_hit_bar_tp050_sl020_h005", "barrier_long_first_hit_time_tp050_sl020_h005",
    "barrier_short_first_hit_time_tp050_sl020_h005", "label_horizon_bars_h015", "label_available_at_h015",
    "fwd_cc_valid_h015", "fwd_cc_reason_codes_h015", "fwd_cc_label_segment_id_h015", "fwd_cc_long_ret_h015",
    "fwd_cc_short_ret_h015", "fwd_cc_log_ret_h015", "fwd_cc_short_log_ret_h015", "fwd_noc_valid_h015",
    "fwd_noc_reason_codes_h015", "fwd_noc_label_segment_id_h015", "fwd_noc_long_ret_h015",
    "fwd_noc_short_ret_h015", "fwd_noc_long_net_proxy_fee_rt_0004_h015",
    "fwd_noc_short_net_proxy_fee_rt_0004_h015", "fwd_excursion_valid_h015", "fwd_excursion_reason_codes_h015",
    "fwd_excursion_label_segment_id_h015", "fwd_long_mfe_h015", "fwd_long_mae_h015", "fwd_short_mfe_h015",
    "fwd_short_mae_h015", "fwd_long_mfe_first_bar_h015", "fwd_long_mae_first_bar_h015",
    "fwd_short_mfe_first_bar_h015", "fwd_short_mae_first_bar_h015", "label_cc_direction_valid_h015",
    "label_cc_direction_reason_codes_h015", "label_cc_direction_segment_id_h015",
    "label_cc_long_direction_h015", "label_cc_short_direction_h015", "label_noc_direction_valid_h015",
    "label_noc_direction_reason_codes_h015", "label_noc_direction_segment_id_h015",
    "label_noc_long_direction_h015", "label_noc_short_direction_h015",
    "label_noc_long_net_proxy_fee_rt_0004_direction_h015",
    "label_noc_short_net_proxy_fee_rt_0004_direction_h015", "barrier_valid_h015", "barrier_reason_codes_h015",
    "barrier_label_segment_id_h015", "barrier_long_outcome_tp050_sl020_h015",
    "barrier_short_outcome_tp050_sl020_h015", "barrier_long_first_hit_bar_tp050_sl020_h015",
    "barrier_short_first_hit_bar_tp050_sl020_h015", "barrier_long_first_hit_time_tp050_sl020_h015",
    "barrier_short_first_hit_time_tp050_sl020_h015", "label_horizon_bars_h060", "label_available_at_h060",
    "fwd_cc_valid_h060", "fwd_cc_reason_codes_h060", "fwd_cc_label_segment_id_h060", "fwd_cc_long_ret_h060",
    "fwd_cc_short_ret_h060", "fwd_cc_log_ret_h060", "fwd_cc_short_log_ret_h060", "fwd_noc_valid_h060",
    "fwd_noc_reason_codes_h060", "fwd_noc_label_segment_id_h060", "fwd_noc_long_ret_h060",
    "fwd_noc_short_ret_h060", "fwd_noc_long_net_proxy_fee_rt_0004_h060",
    "fwd_noc_short_net_proxy_fee_rt_0004_h060", "fwd_excursion_valid_h060", "fwd_excursion_reason_codes_h060",
    "fwd_excursion_label_segment_id_h060", "fwd_long_mfe_h060", "fwd_long_mae_h060", "fwd_short_mfe_h060",
    "fwd_short_mae_h060", "fwd_long_mfe_first_bar_h060", "fwd_long_mae_first_bar_h060",
    "fwd_short_mfe_first_bar_h060", "fwd_short_mae_first_bar_h060", "label_cc_direction_valid_h060",
    "label_cc_direction_reason_codes_h060", "label_cc_direction_segment_id_h060",
    "label_cc_long_direction_h060", "label_cc_short_direction_h060", "label_noc_direction_valid_h060",
    "label_noc_direction_reason_codes_h060", "label_noc_direction_segment_id_h060",
    "label_noc_long_direction_h060", "label_noc_short_direction_h060",
    "label_noc_long_net_proxy_fee_rt_0004_direction_h060",
    "label_noc_short_net_proxy_fee_rt_0004_direction_h060", "barrier_valid_h060", "barrier_reason_codes_h060",
    "barrier_label_segment_id_h060", "barrier_long_outcome_tp050_sl020_h060",
    "barrier_short_outcome_tp050_sl020_h060", "barrier_long_first_hit_bar_tp050_sl020_h060",
    "barrier_short_first_hit_bar_tp050_sl020_h060", "barrier_long_first_hit_time_tp050_sl020_h060",
    "barrier_short_first_hit_time_tp050_sl020_h060", "label_horizon_bars_h240", "label_available_at_h240",
    "fwd_cc_valid_h240", "fwd_cc_reason_codes_h240", "fwd_cc_label_segment_id_h240", "fwd_cc_long_ret_h240",
    "fwd_cc_short_ret_h240", "fwd_cc_log_ret_h240", "fwd_cc_short_log_ret_h240", "fwd_noc_valid_h240",
    "fwd_noc_reason_codes_h240", "fwd_noc_label_segment_id_h240", "fwd_noc_long_ret_h240",
    "fwd_noc_short_ret_h240", "fwd_noc_long_net_proxy_fee_rt_0004_h240",
    "fwd_noc_short_net_proxy_fee_rt_0004_h240", "fwd_excursion_valid_h240", "fwd_excursion_reason_codes_h240",
    "fwd_excursion_label_segment_id_h240", "fwd_long_mfe_h240", "fwd_long_mae_h240", "fwd_short_mfe_h240",
    "fwd_short_mae_h240", "fwd_long_mfe_first_bar_h240", "fwd_long_mae_first_bar_h240",
    "fwd_short_mfe_first_bar_h240", "fwd_short_mae_first_bar_h240", "label_cc_direction_valid_h240",
    "label_cc_direction_reason_codes_h240", "label_cc_direction_segment_id_h240",
    "label_cc_long_direction_h240", "label_cc_short_direction_h240", "label_noc_direction_valid_h240",
    "label_noc_direction_reason_codes_h240", "label_noc_direction_segment_id_h240",
    "label_noc_long_direction_h240", "label_noc_short_direction_h240",
    "label_noc_long_net_proxy_fee_rt_0004_direction_h240",
    "label_noc_short_net_proxy_fee_rt_0004_direction_h240", "barrier_valid_h240", "barrier_reason_codes_h240",
    "barrier_label_segment_id_h240", "barrier_long_outcome_tp050_sl020_h240",
    "barrier_short_outcome_tp050_sl020_h240", "barrier_long_first_hit_bar_tp050_sl020_h240",
    "barrier_short_first_hit_bar_tp050_sl020_h240", "barrier_long_first_hit_time_tp050_sl020_h240",
    "barrier_short_first_hit_time_tp050_sl020_h240", "label_horizon_bars_h1440", "label_available_at_h1440",
    "fwd_cc_valid_h1440", "fwd_cc_reason_codes_h1440", "fwd_cc_label_segment_id_h1440", "fwd_cc_long_ret_h1440",
    "fwd_cc_short_ret_h1440", "fwd_cc_log_ret_h1440", "fwd_cc_short_log_ret_h1440", "fwd_noc_valid_h1440",
    "fwd_noc_reason_codes_h1440", "fwd_noc_label_segment_id_h1440", "fwd_noc_long_ret_h1440",
    "fwd_noc_short_ret_h1440", "fwd_noc_long_net_proxy_fee_rt_0004_h1440",
    "fwd_noc_short_net_proxy_fee_rt_0004_h1440", "fwd_excursion_valid_h1440",
    "fwd_excursion_reason_codes_h1440", "fwd_excursion_label_segment_id_h1440", "fwd_long_mfe_h1440",
    "fwd_long_mae_h1440", "fwd_short_mfe_h1440", "fwd_short_mae_h1440", "fwd_long_mfe_first_bar_h1440",
    "fwd_long_mae_first_bar_h1440", "fwd_short_mfe_first_bar_h1440", "fwd_short_mae_first_bar_h1440",
    "label_cc_direction_valid_h1440", "label_cc_direction_reason_codes_h1440",
    "label_cc_direction_segment_id_h1440", "label_cc_long_direction_h1440", "label_cc_short_direction_h1440",
    "label_noc_direction_valid_h1440", "label_noc_direction_reason_codes_h1440",
    "label_noc_direction_segment_id_h1440", "label_noc_long_direction_h1440", "label_noc_short_direction_h1440",
    "label_noc_long_net_proxy_fee_rt_0004_direction_h1440",
    "label_noc_short_net_proxy_fee_rt_0004_direction_h1440", "barrier_valid_h1440",
    "barrier_reason_codes_h1440", "barrier_label_segment_id_h1440", "barrier_long_outcome_tp050_sl020_h1440",
    "barrier_short_outcome_tp050_sl020_h1440", "barrier_long_first_hit_bar_tp050_sl020_h1440",
    "barrier_short_first_hit_bar_tp050_sl020_h1440", "barrier_long_first_hit_time_tp050_sl020_h1440",
    "barrier_short_first_hit_time_tp050_sl020_h1440", "retrieved_at_utc", "source_file_name",
    "source_byte_sha256", "source_revision", "source_format", "source_location", "license_or_terms_ref",
    "manifest_schema_id", "manifest_schema_version", "manifest_schema_ref", "manifest_type", "manifest_id",
    "created_at_utc", "dataset_id", "dataset_artifact_set_id", "build_id", "run_id", "artifact_id",
    "relative_path", "media_type", "schema_id", "schema_version", "schema_ref", "schema_fingerprint_sha256",
    "field_registry_sha256", "view_allowlist_sha256", "byte_sha256", "semantic_sha256",
    "physical_layout_sha256", "publication_status"
  ]
}
```

#### 7.9.4 View-Invarianten und Negativtests

Verbindlich gelten:

- Paper und Live besitzen bytegleich dieselbe geordnete Feldliste und
  deshalb denselben Allowlist-Hash;
- Research Features, Backtest Inputs, Paper und Live enthalten kein Feld
  mit `field_owner_stage=S7_LABELS` oder
  `leakage_class=FUTURE_OUTCOME`;
- für diese vier Views wird jedes registrierte S7-Feld einzeln injiziert
  und muss abgelehnt werden;
- zusätzliche Negativtests injizieren unbekannte Felder sowie Felder mit
  `fwd_`, `label_` und `barrier_` bei fehlender oder absichtlich falscher
  Eigentümermetadaten;
- Präfixprüfungen ergänzen die Eigentums- und Leakage-Prüfung, ersetzen
  sie aber nicht;
- ein unbekanntes Feld, eine unbekannte Eigentümerstufe, eine unbekannte
  Leakage-Klasse, ein nicht erlaubter Erzeuger oder ein Hashfehler führt
  fail-closed zur Ablehnung der vollständigen View.

Backtest- und Research-Feature-Views werden für Outcome-Auswertungen
ausschließlich über den kanonischen Primärschlüssel
`(market_type, symbol, interval, open_time)` mit einer ausdrücklich
ausgewählten Label-Research-View verbunden. Für noch nicht konsolidierte
Multi-Provider-Daten enthält der Join-Schlüssel zusätzlich `provider`.

## 8. Datenformate

### 8.1 Kanonisches Speicherformat

Bevorzugtes Format für große Tabellen:

```text
Parquet
```

CSV darf verwendet werden für:

- kleine Prüfextrakte;
- menschenlesbare Diagnosen;
- Legacy-Kompatibilität;
- externe Vergleichstests.

CSV darf nicht alleiniger kanonischer Speicher großer RCC-002-Datensätze sein,
wenn dadurch Datentyp-, Nullwert- oder Performanceprobleme entstehen.

### 8.2 Partitionierung

Partitionierung darf keine fachliche Semantik verändern.

Zulässige Partitionsmerkmale:

- Markt;
- Symbol;
- Intervall;
- Jahr;
- Monat;
- Pipeline-Stufe;
- Dataset-Version.

Partitionsgrenzen dürfen:

- keine Rolling-Berechnung ohne Warm-up-Kontext erzwingen;
- keine Segmentgrenzen verdecken;
- keine Zeilenreihenfolge semantisch verändern.

Partitionierte und unpartitionierte Verarbeitung müssen semantisch identische
Ergebnisse liefern.

## 9. Schema- und Namensregeln

Alle kanonischen Feldnamen verwenden:

```text
lower_snake_case
```

Zeitfelder müssen ihre Semantik erkennen lassen:

```text
open_time
close_time
event_time
available_at
generated_at
```

Boolesche Qualitätsfelder verwenden vorzugsweise:

```text
is_*
has_*
*_valid
*_complete
*_pass
```

IDs und Versionen müssen getrennt sein:

```text
component_id
component_version
schema_id
schema_version
schema_ref
profile_id
profile_version
```

`schema_id` ist stets unversioniert. `schema_version` enthält ausschließlich
die Version. `schema_ref` ist stets die qualifizierte, deterministisch
abgeleitete Referenz `<schema_id>/<schema_version>`.

Eine fachliche Bedeutungsänderung benötigt eine neue Komponenten- oder
Schemaversion.

## 10. Warm-up, Nullwerte und Gültigkeitsfelder

Warm-up-Zeilen dürfen nicht still als neutrale Marktzustände gelten.

Für jede abgeleitete Größe muss unterscheidbar sein:

1. gültiger numerischer Wert;
2. fachlich neutraler Wert;
3. Warm-up noch nicht abgeschlossen;
4. ungültige Eingabe;
5. Datenlücke oder Segmentgrenze;
6. Berechnungsfehler.

`NaN`, `0` und `false` dürfen nicht austauschbar verwendet werden.

Ein Vergleich mit `NaN`, der technisch `false` ergibt, darf nicht automatisch
als fachliches Signal `0` interpretiert werden.

## 11. Manifest und Provenienz

Jeder Build muss ein maschinenlesbares Manifest erzeugen.

Das Manifest enthält mindestens:

- `dataset_id`;
- `build_id`;
- Build-Zeitpunkt in UTC;
- Symbol, Markt und Intervall;
- Quellartefakte und Quellchecksummen;
- Code-Commit;
- Status des Git-Worktrees;
- Python- und Bibliotheksversionen;
- `semantic_build_configuration_sha256`;
- `physical_publication_configuration_sha256`;
- Schema- und Komponenten-Versionen;
- Zeilenanzahlen je Stufe;
- Zeitbereich je Stufe;
- Qualitätsmetriken;
- Warnungen und Fehler;
- Artefaktpfade;
- semantische und physische Hashes;
- Review- und Freigabestatus.

Das Manifest darf keine Geheimnisse enthalten.

### 11.1 Quellkorrekturen und Revisionshistorie

Wenn ein Provider historische Daten korrigiert oder ersetzt, muss die neue
Fassung:

- einen neuen `source_snapshot_id`;
- neue Quellartefakthashes;
- einen Revisionsgrund;
- eine Beziehung zur ersetzten Fassung;
- einen neuen nachgelagerten Build erzeugen.

## 12. Qualitäts-Gates

Jede Stufe besitzt ein eigenes Publication Gate.

Eine Stufe darf nur veröffentlicht werden, wenn:

- ihr Schema gültig ist;
- Pflichtfelder vollständig sind;
- Schlüssel- und Sortierungsregeln erfüllt sind;
- Zeilenzahlveränderungen erklärt sind;
- deterministische Tests bestanden wurden;
- bekannte Invaliditätszustände quantifiziert sind;
- das Manifest aktualisiert ist.

Der gesamte Dataset Build darf nur veröffentlicht werden, wenn:

1. alle Pflichtschemas erfüllt sind;
2. alle kritischen S2-Prüfungen bestanden wurden;
3. Zeilenzahlveränderungen vollständig erklärt sind;
4. keine unerlaubten Zukunftsdaten in S0 bis S6 vorkommen;
5. Warm-up- und Invalid-Zustände korrekt markiert sind;
6. Manifest und Checksummen vollständig sind;
7. ein deterministischer Vergleichsbuild bestanden wurde;
8. sämtliche S8-View-Allowlists ihrem registrierten Schema entsprechen;
9. Research-Feature-, Backtest-Input-, Paper- und Live-Views keine
   S7-Felder enthalten;
10. kein unbekanntes oder eigentümerloses Feld veröffentlicht wird.

## 13. Reproduzierbarkeitsprüfungen

Mindestens erforderlich:

### R1 – Wiederholung auf demselben Gerät

Zwei Clean Builds mit identischen Inputs müssen semantisch identisch sein.

### R2 – Wiederholung auf einem zweiten Gerät

Ein zweites Gerät muss denselben semantischen Dataset-Fingerprint erzeugen.

Physische Artefakthashes dürfen nur dann abweichen, wenn die Abweichung durch
zulässige Container- oder Kompressionsdetails erklärt wird.

### R3 – Partitionierungsparität

Partitionierter und unpartitionierter Build müssen semantisch identisch sein.

### R4 – Chunking-Parität

Unterschiedliche Chunk-Größen dürfen keine fachlichen Ergebnisse verändern.

### R5 – Point-in-Time-Test

Eine Änderung an Zeilen nach Zeitpunkt `t` darf S0-bis-S6-Werte bei `t` nicht
verändern.

### R6 – Legacy-Reproduktion

Registrierte Legacy-Profile müssen die verifizierten historischen
Signal- beziehungsweise Regimeausgaben innerhalb der definierten
Vergleichsmenge reproduzieren.

### R7 – Identitätswirkungs-Golden-Tests

Golden Tests müssen mindestens folgende Fälle prüfen:

1. semantische Konfigurationsänderung mit geändertem Output:
   `build_id` und `dataset_id` neu;
2. semantische Konfigurationsänderung mit zufällig identischem Output:
   `build_id` und `dataset_id` neu;
3. reine physische Neuverpackung:
   `build_id` und `dataset_id` gleich, physische Artefaktidentitäten und
   `dataset_artifact_set_id` neu;
4. ausschließlich neue `run_id`:
   `build_id`, `dataset_id` und bei identischen Bytes auch
   `dataset_artifact_set_id` gleich.

## 14. Fehler- und Wiederanlaufverhalten

Ein fehlgeschlagener Build darf keine teilweise erzeugten Artefakte als final
veröffentlichen.

Erforderlich sind:

- temporäre Ausgabepfade;
- atomare Veröffentlichung;
- Stage-Status;
- Fehlerklassifikation;
- wiederaufnehmbare Stufen;
- unveränderliche veröffentlichte Artefakte;
- Quarantäne unvollständiger Ergebnisse.

Ein Resume darf nur erfolgen, wenn:

- Eingaben unverändert sind;
- `semantic_build_configuration_sha256` unverändert ist;
- Codeidentität unverändert ist;
- bereits erzeugte Stufenartefakte ihre Prüfungen bestehen.

Eine geänderte `physical_publication_configuration` darf bereits verifizierte
semantische Stufenausgaben neu verpacken. Dabei entstehen neue physische
Artefaktidentitäten; die semantischen Fingerprints müssen unverändert bleiben.

## 15. Forschungs- und Produktionsparität

Research, Backtest, Paper und Live müssen dieselben kausalen
Transformationskomponenten verwenden können.

Unterschiede dürfen nur durch explizite View- oder Profilwahl entstehen.

Beispiele:

- Label Research darf ausdrücklich ausgewählte S7-Labels enthalten.
- Research-Feature-Views enthalten ausschließlich S0 bis S6.
- Backtests dürfen Kostenmodelle ergänzen.
- Paper und Live dürfen ausschließlich explizit freigegebene Felder
  konsumieren, die in S0 bis S6 erzeugt wurden.
- Paper und Live müssen identische Feature-, Signal-, Regime- und
  Gate-Versionen verwenden, sofern kein dokumentierter A/B-Test vorliegt.

Eine separate, manuell nachgebaute Live-Indikatorlogik ist unzulässig, wenn
sie nicht automatisch gegen die kanonische Pipeline geprüft wird.

## 16. Erweiterbarkeit

Neue Assets, Intervalle oder Indikatoren dürfen die Kernverträge nicht
brechen.

Erweiterungen müssen:

- eigene Profile oder Komponenten-IDs erhalten;
- bestehende Felder nicht still umdeuten;
- Schemamigrationen dokumentieren;
- bestehende Reproduktionstests weiterhin bestehen;
- neue asset- oder intervallspezifische Warm-up-Regeln ausweisen.

Assetübertragung darf nicht als wissenschaftliche Gleichwertigkeit
missverstanden werden.

Ein für BTC definiertes Profil ist auf ETH oder andere Assets nur nach
expliziter Validierung zulässig.

## 17. Sicherheits- und Governance-Regeln

- Rohdaten und veröffentlichte Builds müssen standardmäßig schreibgeschützt
  behandelt werden.
- Kanonische Builds müssen in versionierten, schreibgeschützten Zielpfaden
  veröffentlicht werden.
- Temporäre Dateien dürfen nicht als veröffentlichte Artefakte referenziert
  werden.
- Zugangsdaten dürfen weder in Daten noch in Manifesten gespeichert werden.
- Jeder manuelle Eingriff benötigt einen Audit-Eintrag.
- Jede fachliche Regeländerung benötigt eine Versionsänderung und einen
  neuen Build.
- Ein Dataset darf nicht allein anhand eines Dateinamens als kanonisch gelten.

## 18. Abnahmekriterien für RCC-002

RCC-002 ist als Spezifikation implementierungsbereit, wenn:

1. alle nachgeordneten Spezifikationen vorliegen;
2. jede Stufe und jede S8-View einen eindeutigen versionierten
   Schemavertrag besitzt;
3. alle mathematischen Komponenten versioniert sind;
4. Warm-up-, Invaliditäts- und Lückensemantik eindeutig sind;
5. Regime und Gate logisch getrennt sind;
6. S7-Leakage technisch ausgeschlossen ist;
7. Manifest und Identitätssystem vollständig spezifiziert sind;
8. Reproduzierbarkeitstests definiert sind;
9. Publication Gates definiert sind;
10. sämtliche vor `Approved for Implementation` erforderlichen Entscheidungen
    nach Abschnitt 20.1 geschlossen sind;
11. Scientific Consistency Review bestanden ist;
12. Architecture Integrity Review bestanden ist;
13. Editorial Pass bestanden ist;
14. Internal Certification bestanden ist;
15. Claude Independent Architecture Review bestanden ist;
16. Gemini Independent Scientific and Adversarial Audit bestanden ist;
17. ChatGPT Final Consolidation abgeschlossen ist;
18. alle wesentlichen Befunde geschlossen sind;
19. der Status `Baseline V1 Certified` dokumentiert ist.

## 19. Nachgeordnete Spezifikationen

Verbindlich vorgesehen:

```text
RCC_002_DATA_VALIDATION_2026-07-23.md
RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md
RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md
RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md
RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md
RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md
```

Diese Dokumente dürfen die hier definierten Architekturgrenzen präzisieren,
aber nicht stillschweigend verändern.

## 20. Offene Entscheidungen

### 20.1 Vor `Approved for Implementation` zu schließen

Vor einer Implementierungsfreigabe müssen festgelegt und versioniert sein:

- vollständige logische Stufenschemas;
- vollständige logische S8-View-Schemas und positive Feld-Allowlists;
- Schema-IDs, Versionen und Kompatibilitätsregeln;
- kanonische Feld-, Enum- und Reason-Code-Register;
- Identitätsvorabbildungen;
- Trennung und Hashregeln von semantischer und physischer Konfiguration;
- Bibliotheksauswahl oder kontrollierte Eigenimplementierung je Indikator;
- numerische Präzisions-, Rundungs- und Toleranzprofile;
- technischer Build-Einstiegspunktvertrag;
- Lockdateistrategie und ausführbare Umgebungsdefinition;
- JSON-Schema-Strategie und verbindliche Schemaablage;
- Test-, Paritäts- und Abnahmekriterien.

### 20.2 Während der Implementierung konkretisierbar

Innerhalb der vorab festgelegten physischen Profile dürfen während der
Implementierung konkretisiert werden:

- Partitionsgrößen und Dateigrenzen;
- Row-Group-Größen;
- Kompressionsstufe;
- Writeroptimierungen;
- Retentionsparameter für temporäre und quarantänisierte Artefakte;
- technisch gleichwertige portable Speicherorte.

Diese Konkretisierungen dürfen keine fachliche Semantik, kein logisches Schema
und keinen semantischen Fingerprint verändern.

Eine Änderung mit Wirkung auf:

- wissenschaftliche Regeln;
- logische Stufenschemas;
- S8-View-Allowlists;
- Identitätsvorabbildungen;
- semantische Konfigurationsgrenzen

muss die betroffenen früheren Review-Gates erneut durchlaufen.

Die fachlichen Regeln für Gap-Handling, Zeitsemantik, Indikatoren, Signale,
Regime, Gates, Horizonte und Kosten sind in den nachgeordneten
Spezifikationen bereits festgelegt und dürfen nicht als offene
Implementierungsentscheidung neu interpretiert werden.

## 21. Aktueller Freigabestatus

`RCC-002-SCR-004` bestätigte die dort geprüften wissenschaftlichen
Korrekturen als geschlossen.

Der vollständige Architecture Integrity Review `RCC-002-AIR-001` bewertete
die Spezifikationsfamilie als:

```text
NOT PASSED – ARCHITECTURE CORRECTIONS REQUIRED
```

Version 0.7.0 bewahrt die AIR-001-Korrekturen aus Version 0.6.0 und
korrigiert zusätzlich die diesem Dokument zugeordneten Teile von:

- `SCR-005-B01` – einheitlicher kanonischer Primärschlüssel und
  `interval`-Vertrag;
- `SCR-005-B02` – autoritativer S0- und Source-Manifest-Vertrag;
- `SCR-005-M01` – einheitliche Trennung von `schema_id`,
  `schema_version` und `schema_ref`;
- `SCR-005-M02` – einzige normative Wahrheitstabelle für
  `data_gate_pass`;
- `SCR-005-M03` – einheitliche Dataset-ID-Wirkung semantischer
  Konfigurationsänderungen;
- `AIR-005-H01` – sechs vollständig materialisierte positive
  S8-Feld-Allowlists einschließlich Registry, Hashes und Negativtests.

Die Befunde sind erst geschlossen, wenn:

- alle abhängigen Spezifikationen konsistent aktualisiert sind;
- die vollständige Spezifikationsfamilie neu paketiert ist;
- ein fokussierter Scientific Consistency Re-Review die semantisch relevanten
  Änderungen bestanden hat;
- der fokussierte Architecture Integrity Re-Review sämtliche sieben Befunde
  als geschlossen bestätigt.

Der aktuelle Status lautet:

```text
SCR-005-Corrected Draft – Scientific Consistency Re-Review 006 Pending
```

Die Spezifikationsfamilie ist noch nicht zur Implementierung freigegeben.

Nächste vorgeschriebene Schritte:

1. abhängige Spezifikationen und ihre Versionsreferenzen korrigieren;
2. vollständige interne Qualitätskontrolle;
3. neues vollständiges Spezifikationspaket;
4. fokussierter Scientific Consistency Re-Review;
5. fokussierter Architecture Integrity Re-Review;
6. Editorial Pass;
7. Internal Certification;
8. Claude Independent Architecture Review;
9. Gemini Independent Scientific and Adversarial Audit;
10. ChatGPT Final Consolidation;
11. `Baseline V1 Certified`;
12. Implementierungsfreigabe und Implementierung, primär mit Claude Code.

---

# Eingebettetes Dokument 2 von 7

## Quelldatei: `RCC_002_DATA_VALIDATION_2026-07-23.md`

# RCC-002 Data Validation Specification

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Scientific Software Specification |
| Dokument-ID | RCC-002-DV |
| Titel | Data Validation Specification |
| Speicherort im Repository | `docs/specifications/RCC_002_DATA_VALIDATION_2026-07-23.md` |
| Dateiname | `RCC_002_DATA_VALIDATION_2026-07-23.md` |
| Version | 0.4.2 |
| Datum | 2026-07-23 |
| Status | SCR-005-Corrected Draft – Scientific Consistency Re-Review 006 Pending |
| Übergeordnetes Dokument | `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`, Version 0.7.1 |
| Geltungsbereich | S0_SOURCE, S1_NORMALIZED und S2_VALIDATED der RCC-002-Datenpipeline |
| Referenziert durch | RCC-002-Implementierung; Dataset Manifest; Pipeline Quality Gates; Reproduzierbarkeitsprüfung |
| Autoritative Sprache | Englisch für Code, Schemas, Feldnamen und Fehlercodes; Deutsch für normative Erläuterungen |

### Review-Nachweis

| Prüfung | Status | Ergebnis |
|---|---|---|
| Interne Strukturprüfung | Bestanden | Kapitel, Nummerierung und Querverweise konsistent |
| Methodische Konsistenzprüfung | Bestanden | Fail-closed, Point-in-Time-Korrektheit und Lineage durchgängig berücksichtigt |
| Regelkonfliktprüfung | Bestanden | Duplikat-, Lücken-, Korrektur- und Veröffentlichungsregeln eindeutig priorisiert |
| Vollständigkeitsprüfung | Bestanden | Datei-, Schema-, Zeitachsen-, OHLCV-, Qualitäts- und Reconciliation-Prüfungen enthalten |
| Scientific Consistency Review | `RCC-002-SCR-004` bestanden | Die dort geprüften wissenschaftlichen Befunde sind geschlossen; erneuter fokussierter Review nach den semantisch relevanten AIR-001-Korrekturen erforderlich |
| Architecture Integrity Review | `RCC-002-AIR-001` nicht bestanden; Korrektur eingearbeitet | Version 0.3.0 korrigiert die diesem Dokument zugeordneten Teile von `AIR-001-B01`, `AIR-001-M01` und `AIR-001-M03`; dokumentübergreifender Re-Review ausstehend |
| Scientific Consistency Re-Review 005 | `RCC-002-SCR-005` nicht bestanden; Korrektur eingearbeitet | Version 0.4.0 korrigiert `SCR-005-B02` und `SCR-005-M02`; SCR-006 ausstehend |
| C1 Patch Release | `RCC-002-C1-SCR` bestanden mit Minor Findings | Version 0.4.1: patch release: normative clarification of Canonical Row Preservation semantics (C1) in §20 Kriterium 16. No intended behavioural change. |
| Minor Correction Cycle | `RCC-002-SCR-007-MinFV` umgesetzt | Version 0.4.2, 2026-07-27: Minor correction cycle: version, dependency, terminology, checklist and cross-reference consistency corrections. |

## 1. Zweck

Dieses Dokument definiert die verbindliche Validierung von Roh- und
normalisierten Marktdaten innerhalb der RCC-002-Datenpipeline.

Ziel ist nicht, Marktdaten nachträglich plausibel erscheinen zu lassen, sondern:

- technische Beschädigungen sicher zu erkennen,
- beobachtete Marktereignisse von Datenfehlern zu unterscheiden,
- jede Korrektur oder Ableitung nachvollziehbar zu machen,
- unerklärte Zeilenverluste und Trunkierungen auszuschließen,
- eine belastbare Grundlage für Indikatoren, Signale, Regime und Labels zu
  schaffen.

Keine nachgelagerte Strategie- oder Modellqualität kann Fehler in S0 bis S2
kompensieren. Deshalb arbeitet diese Validierung bei strukturellen und
semantischen Kernfehlern standardmäßig fail-closed.

## 2. Normative Begriffe

`MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT` und `MAY` besitzen dieselbe normative
Bedeutung wie im übergeordneten RCC-002-Dokument.

Zusätzlich gelten:

- **Beobachtete Kerze:** direkt aus einer dokumentierten Quelle übernommene
  Marktbeobachtung.
- **Synthetische Kerze:** deterministisch erzeugte Ersatzzeile ohne direkte
  Marktbeobachtung.
- **Lücke:** mindestens ein erwarteter Zeitindex ohne beobachtete Kerze.
- **Identisches Duplikat:** mehrere Zeilen mit demselben kanonischen Schlüssel
  und identischem kanonischem Inhalt.
- **Konfligierendes Duplikat:** mehrere Zeilen mit demselben kanonischen
  Schlüssel, aber unterschiedlichen kanonischen Werten.
- **Kanonischer Build:** vollständig validierter, manifestgebundener und
  veröffentlichter Pipeline-Build.
- **Quarantäne:** isolierter Zustand für fehlerhafte oder ungeklärte Artefakte,
  die nicht nachgelagert konsumiert werden dürfen.

## 3. Validierungsgrundsätze

### 3.1 Keine stille Reparatur

RCC-002 MUST NOT:

- ungültige Werte still ersetzen,
- konflikthafte Duplikate willkürlich auswählen,
- Lücken ohne Kennzeichnung füllen,
- Zeitstempel ohne protokollierte Regel verschieben,
- Zeilen ohne dokumentierten Reason Code entfernen,
- numerische Parsing-Fehler in Nullwerte umwandeln.

### 3.2 Beobachtung und Interpretation trennen

Ungewöhnliche, aber technisch mögliche Marktwerte dürfen nicht allein aufgrund
statistischer Auffälligkeit gelöscht werden.

Beispielsweise können folgende Werte reale Marktereignisse darstellen:

- sehr große Returns,
- extremes Volumen,
- lange Kerzen,
- sprunghafte Volatilität,
- Nullvolumen in einzelnen Intervallen.

Solche Werte werden geprüft und gegebenenfalls markiert. Automatische
Verwerfung ist nur bei einer objektiv verletzten Invariante zulässig.

### 3.3 Unveränderliche Rohdaten

S0-Artefakte MUST byteweise unverändert bleiben. Normalisierung, Deduplizierung
oder Typkonvertierung erfolgt ausschließlich in neu erzeugten S1-Artefakten.

### 3.4 Vollständige Reconciliation

Jede Veränderung von:

- Dateizahl,
- Bytezahl,
- Zeilenzahl,
- Zeitbereich,
- Spaltenzahl,
- Nullwertzahl

MUST zwischen den Pipeline-Stufen erklärt und im Manifest dokumentiert werden.

### 3.5 Validierungsreihenfolge

Prüfungen MUST in dieser Reihenfolge erfolgen:

1. Artefakt- und Dateiintegrität.
2. Parsing und Basisschema.
3. Datentypen und kanonische Schlüssel.
4. Zeitachse und Abdeckung.
5. Duplikate und Quellkollisionen.
6. OHLCV-Invarianten.
7. Plausibilitäts- und Anomalieflags.
8. Reconciliation.
9. Publication Gate.

Spätere Prüfungen dürfen einen früheren kritischen Fehler nicht überschreiben.

## 4. Validierungsprofile

RCC-002 definiert drei Profile.

### 4.1 `SOURCE_AUDIT`

Zweck:

- unveränderte S0-Artefakte inventarisieren,
- Dateivollständigkeit und Checksummen prüfen,
- Quellmetadaten erfassen.

Dieses Profil verändert keine Daten.

### 4.2 `CANONICAL_BUILD`

Zweck:

- S1 normalisieren,
- S2 validieren,
- kanonische beobachtete Marktzeitreihe erzeugen.

Dieses Profil ist streng. Kritische Fehler blockieren den Build.

### 4.3 `DIAGNOSTIC_RESEARCH`

Zweck:

- ungeklärte oder historische Legacy-Dateien untersuchen,
- Fehlerverteilung und Rekonstruktionsmöglichkeiten analysieren.

Ausgaben dieses Profils MUST als nichtkanonisch markiert werden und dürfen
nicht versehentlich als Produktions- oder Referenzdaten dienen.

## 5. Eingabevertrag

### 5.1 Mindestmetadaten je Quelle

Vor dem Parsing MUST mindestens bekannt sein:

| Feld | Logischer Typ | Nullbar | Anforderung |
|---|---|:---:|---|
| `source_snapshot_id` | UTF-8-String | Nein | Deterministische Identität der unveränderten Quellenfassung |
| `provider` | UTF-8-String | Nein | Kanonische Anbieterkennung, z. B. Binance |
| `market_type` | UTF-8-String | Nein | Registrierter Markttyp, z. B. Spot oder Futures |
| `symbol` | UTF-8-String | Nein | Registriertes Symbol, z. B. BTCUSDT |
| `interval` | UTF-8-String | Nein | Registriertes Datenintervall, z. B. `1m` |
| `retrieved_at_utc` | UTC-Timestamp in Millisekunden | Nein | Provenienzzeitpunkt des Abrufs; nicht Teil der Source-ID |
| `source_file_name` | UTF-8-String | Nein | Ursprünglicher Dateiname ohne lokale Pfadsemantik |
| `source_byte_sha256` | 64-stelliger Lowercase-Hex-String | Nein | SHA-256 der unveränderten Quellbytes |
| `source_revision` | UTF-8-String | Ja | Providerrevision, falls verfügbar |
| `source_format` | UTF-8-String | Nein | Dateityp und Schemafamilie |
| `source_location` | UTF-8-String | Nein | Dokumentierte Herkunft oder portable Quellenreferenz |
| `license_or_terms_ref` | UTF-8-String | Ja | Referenz auf Nutzungsbedingungen |

Fehlende Identitäts- oder Zeitmetadaten blockieren `CANONICAL_BUILD`.

Die kanonischen Feldnamen lauten `provider` und `retrieved_at_utc`.
`source_provider` und `source_retrieved_at_utc` dürfen nur als registrierte
Legacy-Eingangsaliase akzeptiert und nicht parallel in S0 oder S1
weitergeführt werden.

Der S0-Source-Manifest-Eintrag muss das Schema
`rcc002.stage.s0-source/1.0.0` erfüllen.
Die unveränderten Quelldateien selbst behalten ihr dokumentiertes
Providerformat und werden durch diesen Manifest-Eintrag referenziert.

Die Validierung bezieht zusätzlich genau folgende Werte ausschließlich aus
`semantic_build_configuration.source_expectations`:

| Feld | Logischer Typ | Nullbar | Validierungswirkung |
|---|---|:---:|---|
| `timezone` | UTF-8-String | Nein | deterministische Interpretation nicht eindeutig zonierter Quellzeiten |
| `expected_start` | UTC-Timestamp in Millisekunden | Nein | erwarteter erster Intervallbeginn |
| `expected_end` | UTC-Timestamp in Millisekunden | Nein | erwarteter letzter Intervallbeginn |

Diese Felder sind weder S0-Zeilenfelder noch Source-Manifest-Felder. Der
Validierungsauftrag MUSS die bereits gehashte semantische Build-Konfiguration
referenzieren und DARF keine abweichenden lokalen Werte bereitstellen. Jede
Änderung eines dieser drei Felder ändert
`semantic_build_configuration_sha256`, `build_id` und `dataset_id`, nicht
jedoch allein aufgrund dieser Änderung `source_snapshot_id`.

### 5.2 Erwartetes Quelldateiinventar

Bei monatlich oder täglich partitionierten Quellen MUST vor dem Einlesen eine
erwartete Dateiliste erzeugt werden.

Für jede erwartete Periode werden erfasst:

- erwarteter Dateiname,
- vorhanden/nicht vorhanden,
- Dateigröße,
- Quellchecksumme, falls angeboten,
- lokal berechnete Checksumme,
- Downloadstatus,
- Extraktionsstatus.

Eine fehlende erwartete Partition ist mindestens `ERROR`. Sie wird erst dann
auf `WARN` herabgestuft, wenn die Quelle für diesen Zeitraum nachweislich keine
Daten bereitstellt und dies als genehmigte Ausnahme dokumentiert wurde.

## 6. Dateiintegrität

### 6.1 Zulässige Dateizustände

Jedes S0-Artefakt erhält genau einen Zustand:

- `RECEIVED_UNVERIFIED`,
- `VERIFIED`,
- `MISSING`,
- `CORRUPT`,
- `CHECKSUM_MISMATCH`,
- `EXTRACTION_FAILED`,
- `QUARANTINED`.

Nur `VERIFIED` darf regulär in S1 eingehen.

### 6.2 Pflichtprüfungen

Für jede Datei MUST geprüft werden:

- Datei existiert,
- Datei ist regulär lesbar,
- Größe ist größer als null,
- Format oder Archiv kann geöffnet werden,
- erwartete interne Datei ist vorhanden,
- Header ist vorhanden und parsebar,
- lokale SHA-256-Checksumme wurde berechnet,
- angebotene Anbieterchecksumme stimmt, sofern verfügbar,
- keine unerwarteten zusätzlichen Nutzdaten wurden still übernommen.

### 6.3 Spreadsheet-Grenzprüfung

Tabellen mit folgenden verdächtigen Zeilenzahlen MUST einen speziellen
Trunkierungsbefund erzeugen:

- 65.535 Datenzeilen plus Kopfzeile,
- 1.048.575 Datenzeilen plus Kopfzeile,
- andere bekannte Format- oder Toolgrenzen.

Der Fehlercode lautet:

`DV_FILE_SUSPECTED_ROW_LIMIT_TRUNCATION`.

Bei einer vorgelagerten Datei mit mehr Zeilen oder einem erwarteten längeren
Zeitbereich ist dieser Befund `CRITICAL`.

XLSX, XLS und ODS sind als kanonische S0-bis-S2-Transformationsformate
unzulässig.

## 7. Parsing und kanonisches Schema

### 7.1 Pflichtfelder

S1 akzeptiert ausschließlich S0-Eingaben, die dem Schema
`rcc002.stage.s0-source/1.0.0` entsprechen.

S1 erzeugt das Schema `rcc002.stage.s1-normalized/1.0.0`.

Das S1-Mindestschema lautet:

| Feld | Kanonischer Typ | Null zulässig | Erzeugerstufe |
|---|---|:---:|---|
| `source_snapshot_id` | UTF-8-String | Nein | S0; durch S1 unverändert übernommen |
| `source_row_id` | UTF-8-String | Nein | S1 |
| `provider` | UTF-8-String | Nein | S0; durch S1 kanonisch übernommen |
| `market_type` | UTF-8-String | Nein | S0; durch S1 kanonisch übernommen |
| `symbol` | UTF-8-String | Nein | S0; durch S1 kanonisch übernommen |
| `interval` | UTF-8-String | Nein | S0; durch S1 kanonisch übernommen |
| `open_time` | UTC-Timestamp in Millisekunden | Nein | S1 |
| `close_time` | UTC-Timestamp in Millisekunden | Nein | S1 |
| `open` | Float64 | Nein | S1 |
| `high` | Float64 | Nein | S1 |
| `low` | Float64 | Nein | S1 |
| `close` | Float64 | Nein | S1 |
| `volume` | Float64 | Nein | S1 |

`source_id` ist kein kanonischer Feldname. Historische Eingaben müssen ihn
über eine versionierte Migrationsabbildung in `source_snapshot_id`
überführen.

`source_row_id` muss deterministisch als UTF-8-String erzeugt werden. Eine
parallele typabhängige Darstellung als Integer ist unzulässig.

Optionale Quellfelder wie `quote_volume` oder `trade_count` dürfen nur
aufgenommen werden, wenn Feldname, Typ, Nullsemantik und Providerabbildung im
S1-Schema registriert sind.

### 7.2 Numerisches Parsing

Numerische Felder MUST:

- ohne localeabhängige Mehrdeutigkeit gelesen werden,
- `NaN`, `+Inf` und `-Inf` erkennen,
- ungültige Zeichenfolgen als Parsing-Fehler melden,
- ohne vorherige Rundung in den kanonischen Typ überführt werden.

Ein Parsing-Fehler in einem OHLCV-Pflichtfeld ist `CRITICAL`.

### 7.3 Zusätzliche Quellfelder

Zusätzliche Felder MAY erhalten bleiben, wenn:

- ihre Semantik dokumentiert ist,
- sie einen registrierten kanonischen Namen erhalten,
- sie keine Pflichtfelder überschreiben,
- Datentyp und Nullsemantik definiert sind.

Nicht registrierte Zusatzfelder MUST im Schema-Report erscheinen.

### 7.4 Schema-Fingerprint

Jedes S1- und S2-Artefakt MUST einen Schema-Fingerprint besitzen, der mindestens
berücksichtigt:

- geordnete Feldnamen,
- Datentypen,
- Nullzulässigkeit,
- Primärschlüssel,
- Schemaversion,
- Erzeugerstufe jedes Feldes,
- Enum- und Reason-Code-Register.

Die verbindlichen Schema-IDs lauten:

```text
rcc002.stage.s1-normalized/1.0.0
rcc002.stage.s2-validated/1.0.0
```

Unbekannte Major-Versionen werden fail-closed abgelehnt.

Additive optionale Felder einer neueren Minor-Version dürfen nur verarbeitet
werden, wenn eine registrierte Kompatibilitätsregel dies ausdrücklich erlaubt.

## 8. Zeitsemantik

### 8.1 Kanonische Zeitzone

Alle kanonischen Zeitstempel MUST UTC darstellen. Naive Zeitstempel ohne
nachweisbare Quellzeitzone sind für `CANONICAL_BUILD` unzulässig.

### 8.2 Kerzenidentität

Der kanonische Primärschlüssel einer Einzelasset-Zeitreihe lautet:

`(market_type, symbol, interval, open_time)`.

Bei Multi-Provider-Daten kommt `provider` hinzu, solange noch keine
freigegebene Konsolidierung erfolgt ist. `provider` steht dann unmittelbar
vor `market_type` im Primärschlüssel und in der Sortierreihenfolge.

### 8.3 Intervallausrichtung

Für BTCUSDT `1m` gilt:

- `open_time` liegt exakt auf einer UTC-Minute,
- aufeinanderfolgende erwartete `open_time`-Werte unterscheiden sich um
  60 Sekunden,
- `close_time` entspricht der dokumentierten Anbietersemantik,
- eine abweichende Endzeitkonvention wird normalisiert, aber nicht geraten.

Die allgemeine Regel lautet:

`open_time % interval_duration == 0`

für epochbasierte Zeitstempel.

### 8.4 Entscheidungszeitpunkt

S2 MUST unterscheiden:

- Intervallbeginn,
- Intervallende,
- Zeitpunkt, zu dem eine geschlossene Kerze verfügbar ist.

Indikatoren oder Signale für Kerze `t` dürfen im späteren Handel erst nach dem
definierten Verfügbarkeitszeitpunkt dieser Kerze verwendet werden.

### 8.5 Sortierung

S1 und S2 MUST nach dem vollständigen kanonischen Schlüssel aufsteigend
sortiert sein.

Unsortierte Quelldaten dürfen in S1 deterministisch sortiert werden, sofern:

- die ursprüngliche Reihenfolge über `source_row_id` erhalten bleibt,
- der Befund protokolliert wird,
- keine konflikthaften Schlüssel verdeckt werden.

## 9. Abdeckung und erwartete Zeilenzahl

### 9.1 Inklusive Grenzen

Wenn `expected_start` und `expected_end` jeweils Intervallbeginne und beide
inklusive sind, lautet die erwartete Zeilenzahl:

`expected_rows = ((expected_end - expected_start) / interval_duration) + 1`

Die Division MUST ohne Rest aufgehen.

### 9.2 Pflichtvergleich

Für jede Stufe werden dokumentiert:

- erwartete Zeilen,
- gelesene Zeilen,
- parsebare Zeilen,
- eindeutige Schlüssel,
- ausgegebene Zeilen,
- erste und letzte Zeit,
- fehlende Intervalle,
- zusätzliche Intervalle außerhalb des erwarteten Bereichs.

### 9.3 Bereichsüberschreitung

Zeilen vor `expected_start` oder nach `expected_end` dürfen nicht still
verworfen werden.

Sie werden:

- bei falscher Konfiguration als Konfigurationsfehler behandelt oder
- bei unerwarteten Quelldaten separat ausgewiesen und quarantänisiert.

## 10. Duplikate und Quellkollisionen

### 10.1 Identische Duplikate

Identische Duplikate MAY in S1 deterministisch auf eine Zeile reduziert werden,
wenn:

- alle kanonischen Werte identisch sind,
- alle Quellreferenzen erhalten bleiben,
- Anzahl und Zeitpunkte protokolliert werden,
- die Deduplizierungsregel versioniert ist.

Die ausgegebene S1-Zeile führt genau eine deterministisch gewählte
`source_row_id` als primäre Zeilenreferenz. Sämtliche weiteren kollabierten
`source_row_id`-Werte werden verlustfrei im Duplicate Report und in der
Lineage-Abbildung der ausgegebenen Zeile geführt.

Der Reason Code lautet:

`DV_DUPLICATE_IDENTICAL_COLLAPSED`.

### 10.2 Konfligierende Duplikate

Konfligierende Duplikate sind in `CANONICAL_BUILD` `CRITICAL`.

Sie dürfen nur durch eine separat genehmigte, deterministische
Quellenprioritätsregel aufgelöst werden. Diese Regel MUST dokumentieren:

- bevorzugte Quelle,
- Begründung,
- Vergleichsfelder,
- verworfene Werte,
- betroffene Zeitpunkte,
- Regelversion.

Ohne diese Regel bricht der Build ab.

### 10.3 Überlappende Partitionen

Überlappungen zwischen Tages-, Monats- oder Update-Dateien werden vor einer
Deduplizierung vollständig gezählt und klassifiziert.

Eine typische Update-Überlappung gilt nicht automatisch als harmlos; ihre Werte
müssen identisch sein oder nach einer genehmigten Revisionsregel verarbeitet
werden.

## 11. Lückenerkennung

### 11.1 Definition

Eine Lücke liegt vor, wenn zwischen zwei gültigen kanonischen Schlüsseln
mindestens ein erwarteter Intervallbeginn fehlt.

Für jede Lücke MUST erfasst werden:

- `gap_start`,
- `gap_end`,
- `missing_intervals`,
- vorherige und nächste vorhandene Kerze,
- betroffene Quellpartitionen,
- bekannte Anbieter- oder Marktereignisse,
- Klassifikation,
- Genehmigungsstatus.

### 11.2 Lückenklassen

Zulässige Klassen:

- `SOURCE_FILE_MISSING`,
- `SOURCE_ROW_MISSING`,
- `PROVIDER_OUTAGE_CONFIRMED`,
- `MARKET_NOT_AVAILABLE`,
- `PARSING_LOSS`,
- `FILTERING_LOSS`,
- `UNKNOWN`.

`PARSING_LOSS`, `FILTERING_LOSS` und `UNKNOWN` sind im kanonischen
Publication Gate mindestens `ERROR`; ungeklärte systematische Lücken sind
`CRITICAL`.

### 11.3 Kanonische Lückenpolitik

Der kanonische beobachtete S2-Datensatz MUST ausschließlich beobachtete Kerzen
enthalten. Fehlende Marktbeobachtungen werden nicht im selben Artefakt durch
synthetische Kerzen ersetzt.

Damit bleiben:

- tatsächlich beobachtete Daten,
- diagnostizierte Lücken,
- optionale Kontinuitätsableitungen

fachlich getrennt.

#### 11.3.1 Kanonische Marktsegment-ID

S2 erzeugt für jede kanonische beobachtete Zeile eine
`market_segment_id`.

Eine neue `market_segment_id` beginnt:

- am Anfang jeder Kombination aus `market_type`, `symbol` und `interval`;
- nach jeder Abweichung vom exakt erwarteten nächsten `open_time`;
- nach einer Änderung der kanonischen Marktidentität;
- nach einer ausdrücklich genehmigten und versionierten Segment-Resetregel.

Die ID muss deterministisch aus:

- kanonischer Marktidentität;
- erstem `open_time` des Segments;
- Intervall;
- `segment_id_profile_id`;
- `segment_id_profile_version`

gebildet werden. Eine zufällige UUID ist unzulässig.

Ein ungültiger OHLC- oder Volumenwert ändert nicht rückwirkend die zeitliche
Marktsegmentdefinition. Er setzt für die betroffene Zeile jedoch
`quality_gate_pass=false`.

`indicator_segment_id` gehört zu S3. Die ID darf die `market_segment_id`
verfeinern, aber niemals mehrere Marktsegmente zusammenführen.

#### 11.3.2 Gap-Felder

Für jede beobachtete S2-Zeile gilt:

- `quality_gap_before=true`, wenn unmittelbar vor der Zeile mindestens ein
  erwartetes Intervall fehlt;
- `quality_gap_after=true`, wenn unmittelbar nach der Zeile mindestens ein
  erwartetes Intervall fehlt;
- am äußeren angeforderten Zeitraumrand entsteht kein Gap-Flag allein wegen
  fehlender Daten außerhalb von `expected_start` bis `expected_end`.

### 11.4 Optionale Kontinuitätsansicht

Eine separate synthetisch vervollständigte Ansicht MAY erzeugt werden, wenn ein
nachgelagerter Algorithmus eine regelmäßige Zeitachse zwingend benötigt.

Dann gelten mindestens:

- eigener Artefaktname und eigene View-ID,
- eigenes registriertes Diagnoseschema,
- `quality_is_observed = false`,
- `quality_is_synthetic = true`,
- `quality_market_values_valid = false`,
- `quality_gate_pass = false`,
- `quality_gap_id`,
- dokumentierte Erzeugungsregel,
- keine Überschreibung beobachteter Kerzen,
- Ausschluss aus kanonischen Returns und Labels als Standard,
- gesonderte Sensitivitätsanalyse.

Eine übliche synthetische OHLC-Regel wie
`open = high = low = close = previous_close` und `volume = 0` ist erst nach
separater Freigabe zulässig; dieses Dokument genehmigt sie nicht automatisch.

## 12. OHLCV-Invarianten

### 12.1 Harte Preisregeln

Für jede beobachtete Kerze MUST gelten:

- `open > 0`,
- `high > 0`,
- `low > 0`,
- `close > 0`,
- `high >= open`,
- `high >= close`,
- `high >= low`,
- `low <= open`,
- `low <= close`.

Eine Verletzung ist `CRITICAL`.

### 12.2 Volumenregeln

MUST gelten:

- `volume >= 0`,
- `quote_volume >= 0`, sofern vorhanden,
- `trade_count >= 0`, sofern vorhanden,
- `trade_count` ist ganzzahlig.

Negatives Volumen oder negativer Trade Count ist `CRITICAL`.

Nullvolumen ist nicht automatisch ungültig, erzeugt aber:

`DV_VOLUME_ZERO_OBSERVED`.

Häufigkeit, zeitliche Cluster und Zusammenhang mit Lücken oder
Anbieterstörungen MUST im Report erscheinen.

### 12.3 Optionale Konsistenzprüfungen

Wenn die Quelle zusätzliche Felder liefert, SHOULD geprüft werden:

- `quote_volume` gegenüber Preis- und Basisvolumengrößenordnung,
- Taker-Buy-Volumen gegen Gesamtvolumen,
- Trade Count gegen Nullvolumen,
- Anbieter-ID oder Sequenznummer auf Kontinuität.

Diese Prüfungen dürfen ohne belastbare exakte Invariante zunächst Warnungen
erzeugen, aber keine realen Marktdaten automatisch löschen.

## 13. Anomalieerkennung

### 13.1 Zweck

Anomalieerkennung dient der Untersuchung, nicht der stillen Datenbereinigung.

### 13.2 Mindestflags

S2 SHOULD mindestens erzeugen:

- extreme absolute Kerzenrendite,
- extreme High-Low-Range,
- extremes Volumen,
- ungewöhnlich langer Nullvolumen-Cluster,
- identische OHLC-Werte über ungewöhnlich viele Kerzen,
- Preis- oder Volumensprung an Partitionsgrenzen.

Diese Anomalieergebnisse werden über registrierte Reason Codes in
`quality_reason_codes` sowie im Findings-Artefakt abgebildet. Ein zusätzliches
paralleles kanonisches Feld `quality_anomaly_flags` wird nicht erzeugt.

### 13.3 Schwellenwerte

Schwellenwerte MUST:

- robust und kausal berechnet werden,
- pro Asset und Intervall konfiguriert sein,
- ihre Warm-up-Periode ausweisen,
- nicht aus dem späteren Testzeitraum optimiert werden.

Anomalieflags dürfen die Originalwerte nicht verändern.

### 13.4 Externe Bestätigung

Bei kritischen Auffälligkeiten MAY eine unabhängige Quelle zur Bestätigung
verwendet werden.

Die externe Quelle, der Vergleichszeitpunkt und das Ergebnis werden im
Validierungsreport dokumentiert. Ein externer Vergleich ersetzt nicht die
Lineage der Primärquelle.

## 14. Nullwerte und fehlende Werte

### 14.1 Pflichtfelder

Nullwerte in Primärschlüssel-, Zeit- oder OHLCV-Pflichtfeldern sind
`CRITICAL`.

### 14.2 Optionale Felder

Nullwerte in optionalen Quellfeldern sind zulässig, wenn:

- die Quelle das Feld für den gesamten Datensatz nicht liefert oder
- die Nullsemantik explizit dokumentiert ist.

Mischungen aus vorhandenen und fehlenden Werten müssen gezählt und untersucht
werden.

### 14.3 Kein implizites Auffüllen

Forward Fill, Backward Fill, Mittelwert-Imputation oder Nullersetzung sind in
S1 und im kanonischen beobachteten S2-Artefakt verboten.

## 15. Qualitätsfelder

S2 erzeugt das Schema `rcc002.stage.s2-validated/1.0.0`.

S2 führt sämtliche kanonischen S1-Felder und den vollständigen Primärschlüssel
unverändert weiter. Die nachfolgenden Qualitätsfelder werden ausschließlich
ergänzt.

Der kanonische Qualitätsvertrag lautet:

| Feld | Logischer Typ | Nullbar | Bedeutung |
|---|---|:---:|---|
| `market_segment_id` | UTF-8-String | Nein | Deterministische Identität der zeitlich zusammenhängenden beobachteten Marktsequenz |
| `quality_is_observed` | Boolean | Nein | Zeile stammt aus einer beobachteten Quellkerze |
| `quality_is_synthetic` | Boolean | Nein | Zeile gehört ausschließlich zu einer getrennten synthetischen Diagnoseansicht |
| `quality_has_source_conflict` | Boolean | Nein | Aktiver, nicht genehmigt aufgelöster Quellkonflikt |
| `quality_gap_before` | Boolean | Nein | Mindestens ein erwartetes Intervall vor dieser Zeile fehlt |
| `quality_gap_after` | Boolean | Nein | Mindestens ein erwartetes Intervall nach dieser Zeile fehlt |
| `quality_timestamp_valid` | Boolean | Nein | Zeitstempel, Zeitzone und Intervallausrichtung sind gültig |
| `quality_ohlc_valid` | Boolean | Nein | Sämtliche harten OHLC-Invarianten sind erfüllt |
| `quality_volume_valid` | Boolean | Nein | Volumenpflichtwerte sind endlich und nicht negativ |
| `quality_market_values_valid` | Boolean | Nein | Sämtliche kanonischen Marktpflichtwerte sind gültig |
| `quality_status` | Enum | Nein | `PASS`, `WARN`, `ERROR` oder `CRITICAL` |
| `quality_reason_codes` | Geordnete Liste aus UTF-8-Strings | Nein | Vollständige maschinenlesbare Qualitätsgründe |
| `quality_rule_version` | UTF-8-String | Nein | Version des angewandten Qualitätsregelwerks |
| `quality_gate_pass` | Boolean | Nein | Verbindliche S2-Freigabe für qualitätsgesicherte nachgelagerte Nutzung |

Die Liste `quality_reason_codes` ist:

- stabil sortiert nach registrierter Reason-Code-Priorität;
- leer, wenn kein Reason Code aktiv ist;
- niemals null;
- kein Bitfeld und keine implizite Maske.

`quality_anomaly_flags`, `quality_reason_mask`, `segment_id`,
`is_observed_bar`, `synthetic_bar`, `source_conflict` und
`market_values_valid` sind keine parallelen kanonischen S2-Felder.

Für den kanonischen beobachteten S2-Datensatz gilt:

- `quality_is_observed=true`;
- `quality_is_synthetic=false`.

`quality_status` wird aus der höchsten registrierten Severity aller aktiven
`quality_reason_codes` gebildet:

- kein aktiver Code oder ausschließlich `INFO` ergibt `PASS`;
- höchste Severity `WARN` ergibt `WARN`;
- höchste Severity `ERROR` ergibt `ERROR`;
- höchste Severity `CRITICAL` ergibt `CRITICAL`.

### 15.1 Bildung von `quality_gate_pass`

`quality_gate_pass=true` gilt genau dann, wenn:

- `quality_is_observed=true`;
- `quality_is_synthetic=false`;
- `quality_has_source_conflict=false`;
- `quality_timestamp_valid=true`;
- `quality_ohlc_valid=true`;
- `quality_volume_valid=true`;
- `quality_market_values_valid=true`;
- kein aktiver Reason Code die Buildwirkung `ERROR` oder `CRITICAL` besitzt;
- jeder aktive `WARN` durch das versionierte Qualitätsprofil ausdrücklich als
  nicht blockierend klassifiziert ist.

In jedem anderen Fall gilt `quality_gate_pass=false`.

Ein technisch fehlender Pflichtinput darf nicht durch einen neutralen Wert
ersetzt werden, um `quality_gate_pass=true` zu erreichen.

### 15.2 Genehmigt aufgelöste Quellkonflikte

Wurde ein Quellkonflikt durch eine genehmigte deterministische Regel
aufgelöst, gilt für die ausgewählte kanonische Zeile:

```text
quality_has_source_conflict=false
```

Zusätzlich wird mindestens folgender Reason Code geführt:

```text
DV_SOURCE_CONFLICT_RESOLVED
```

Die ursprüngliche Kollision, sämtliche Kandidaten, die Auswahlregel,
verworfene Werte und die Auflösungsreferenz bleiben im Duplicate Report und
in der Lineage erhalten.

### 15.3 Übergabe an S6

Für jeden schema-, primärschlüssel-, sortierungs- und segmentgültigen
S6-Eingang gilt exakt:

```text
data_gate_pass = quality_gate_pass
```

Schema-, Schlüssel-, Sortierungs- oder Segmentvertragsverletzungen sind keine
zusätzlichen booleschen Bestandteile von `data_gate_pass`. Sie sind stageweite
S6-Eingangsfehler, führen zum Abbruch und erzeugen keine kanonische S6-Zeile.

Bei strukturell gültigem Eingang und `quality_gate_pass=false` wird eine
kanonische S6-Zeile mit `data_gate_pass=false`, `gate_valid=true`,
`gate_state=BLOCK_BOTH` und beiden Richtungen `false` erzeugt. Profilabhängige
Pflichtinputs werden in diesem Fall nicht ausgewertet.

Bei strukturell gültigem Eingang und `quality_gate_pass=true` werden die
Pflichtinputs des aktiven Gate-Profils geprüft. Ungültige Profilinputs führen
zu `gate_valid=false` und `gate_state=INVALID`; gültige Profilinputs führen
zur profilspezifischen Auswertung.

S6 darf eine S2-Zeile mit `quality_gate_pass=false` niemals freigeben.

Nachgelagerte Rolling-Berechnungen müssen zusätzlich erkennen können, ob ihr
Eingabefenster eine Lückengrenze überschreitet.

## 16. Severity- und Reason-Code-System

### 16.1 Severity

| Severity | Bedeutung | Buildwirkung |
|---|---|---|
| `INFO` | dokumentierter Normalzustand | keine Blockierung |
| `WARN` | Auffälligkeit ohne nachgewiesene Integritätsverletzung | Veröffentlichung möglich, wenn akzeptiert |
| `ERROR` | relevante Qualitätsverletzung | Veröffentlichung standardmäßig blockiert |
| `CRITICAL` | strukturelle oder semantische Kernverletzung | sofortiger Abbruch oder Quarantäne |

### 16.2 Reason-Code-Regeln

Jeder Reason Code MUST:

- stabil und maschinenlesbar sein,
- mit `DV_` beginnen,
- genau eine primäre Bedeutung besitzen,
- eine Standard-Severity besitzen,
- betroffene Artefakte und Zeilen referenzieren können.

Mindestcodes:

- `DV_FILE_MISSING`,
- `DV_FILE_EMPTY`,
- `DV_FILE_CORRUPT`,
- `DV_CHECKSUM_MISMATCH`,
- `DV_FILE_SUSPECTED_ROW_LIMIT_TRUNCATION`,
- `DV_SCHEMA_REQUIRED_COLUMN_MISSING`,
- `DV_SCHEMA_UNEXPECTED_COLUMN`,
- `DV_PARSE_TIMESTAMP_FAILED`,
- `DV_PARSE_NUMERIC_FAILED`,
- `DV_TIME_NOT_UTC`,
- `DV_TIME_MISALIGNED`,
- `DV_TIME_OUT_OF_RANGE`,
- `DV_DUPLICATE_IDENTICAL_COLLAPSED`,
- `DV_DUPLICATE_CONFLICT`,
- `DV_SOURCE_CONFLICT_RESOLVED`,
- `DV_GAP_DETECTED`,
- `DV_GAP_UNEXPLAINED`,
- `DV_TIME_GAP_SEGMENT_STARTED`,
- `DV_NUMERIC_NONFINITE`,
- `DV_OHLC_INVARIANT_FAILED`,
- `DV_VOLUME_NEGATIVE`,
- `DV_VOLUME_ZERO_OBSERVED`,
- `DV_ANOMALY_EXTREME_CANDLE_RETURN`,
- `DV_ANOMALY_EXTREME_HIGH_LOW_RANGE`,
- `DV_ANOMALY_EXTREME_VOLUME`,
- `DV_ANOMALY_ZERO_VOLUME_CLUSTER`,
- `DV_ANOMALY_REPEATED_IDENTICAL_OHLC`,
- `DV_ANOMALY_PARTITION_BOUNDARY_JUMP`,
- `DV_SYNTHETIC_ROW_NONCANONICAL`,
- `DV_APPROVED_WARNING_ACTIVE`,
- `DV_ROW_RECONCILIATION_FAILED`,
- `DV_SCHEMA_FINGERPRINT_MISMATCH`.

Jede `quality_reason_codes`-Liste wird nach einer versionierten
Reason-Code-Priorität sortiert. Die Reihenfolge darf nicht von
Threadplanung, Eingabedateireihenfolge oder Hash-Iteration abhängen.

## 17. Reconciliation zwischen Stufen

### 17.1 S0 zu S1

MUST dokumentiert werden:

`source_rows = parsed_rows + rejected_rows`

und:

`parsed_rows = normalized_rows + duplicate_rows_removed + out_of_scope_rows`

Jeder Summand benötigt eine nichtnegative Ganzzahl und gegebenenfalls
Reason-Code-Aufschlüsselung.

Zusätzlich muss für jede S1-Zeile genau ein gültiger:

- `source_snapshot_id`;
- `source_row_id`;
- `provider`

auf eine inventarisierte S0-Quelle zurückführen.

### 17.2 S1 zu S2

Standardmäßig gilt:

`s2_observed_rows = s1_unique_valid_rows`

Abweichungen sind nur zulässig, wenn jede betroffene Zeile mit Reason Code und
Quellreferenz dokumentiert ist.

Für jede veröffentlichte S2-Zeile müssen zusätzlich gelten:

- genau eine `market_segment_id`;
- genau ein `quality_status`;
- genau eine `quality_rule_version`;
- eine nicht-nullbare `quality_reason_codes`-Liste;
- genau ein boolescher Wert für `quality_gate_pass`.

### 17.3 Zeitachsen-Reconciliation

MUST gelten:

`expected_intervals = observed_unique_intervals + missing_intervals`

für den definierten inklusiven Zeitraum.

Zusätzliche Intervalle außerhalb des Zeitraums werden separat gezählt und
dürfen die Gleichung nicht verdecken.

Die Summe der beobachteten Zeilen aller `market_segment_id`-Werte muss exakt
`s2_observed_rows` ergeben.

## 18. Inkrementelle Aktualisierung

### 18.1 Source Snapshot

Jeder Aktualisierungslauf erzeugt einen neuen Run-Nachweis.

Ein neuer `source_snapshot_id` entsteht nur, wenn sich mindestens eines der
folgenden Merkmale ändert:

- Quellbytes;
- Providerrevision;
- semantische Abrufparameter;
- logische Quellenabdeckung;
- normiertes Quelldateiinventar.

Ein erneuter Abruf identischer Quellbytes mit identischen semantischen
Abrufmerkmalen behält denselben `source_snapshot_id`.

Abrufzeitpunkt, Hostname, Benutzername, lokaler Pfad, Retry-Anzahl oder
Cache-Ort dürfen die Source-ID nicht verändern.

### 18.2 Überlappungsfenster

Ein inkrementeller Download SHOULD ein konfiguriertes Überlappungsfenster mit
dem bisherigen Ende enthalten, um:

- nachträgliche Anbieteränderungen,
- unvollständige letzte Partitionen,
- Downloadgrenzen

zu erkennen.

### 18.3 Revisionsvergleich

Überlappende Schlüssel werden feldweise verglichen.

Bei Änderungen MUST dokumentiert werden:

- alter Wert,
- neuer Wert,
- Quelle und Abrufzeit beider Versionen,
- Anzahl betroffener Kerzen,
- frühester und spätester Änderungszeitpunkt,
- Rebuild-Reichweite.

Eine Änderung bestehender Quelldaten erzeugt einen neuen Build; der alte Build
bleibt unverändert.

### 18.4 Unvollständige laufende Kerzen

Noch nicht abgeschlossene Kerzen dürfen nicht in einen kanonischen historischen
S2-Build aufgenommen werden.

Der Abschlussstatus richtet sich nach der dokumentierten
Provider-Zeitsemantik, nicht allein nach lokalem Empfang.

## 19. Validierungsoutputs

Jeder Lauf MUST mindestens erzeugen:

1. `validation_summary.json`
2. `validation_findings.csv` oder gleichwertiges Parquet-Artefakt
3. `gap_report.csv`
4. `duplicate_report.csv`
5. `schema_report.json`
6. `row_reconciliation.json`
7. `source_inventory.json`
8. aktualisierten Manifestabschnitt

### 19.1 `validation_summary.json`

Mindestfelder:

- `validation_run_id`,
- `build_id`,
- `profile`,
- `rule_version`,
- `input_schema_id`,
- `output_schema_id`,
- `semantic_build_configuration_sha256`,
- `started_at_utc`,
- `completed_at_utc`,
- `status`,
- Findings je Severity,
- erste und letzte Zeit,
- erwartete und tatsächliche Zeilen,
- Lückenanzahl und fehlende Intervalle,
- Anzahl und Zeitabdeckung der `market_segment_id`-Werte,
- Duplikatanzahl nach Klasse,
- synthetische Zeilen,
- S1- und S2-Schema-Fingerprints,
- Artefaktchecksummen.

### 19.2 Findings

Jedes Finding enthält:

- `finding_id`,
- `reason_code`,
- `severity`,
- `stage`,
- `artifact_id`,
- optionalen Zeilen- oder Zeitbezug,
- beobachteten Wert,
- erwartete Regel,
- Status,
- genehmigte Ausnahme,
- Auflösungsreferenz.

## 20. Publication Gate

Ein S2-Artefakt darf nur als kanonisch veröffentlicht werden, wenn:

1. alle erwarteten S0-Partitionen vorhanden oder genehmigt ausgenommen sind;
2. alle verwendeten S0-Dateien `VERIFIED` sind;
3. S0, S1 und S2 ihre registrierten Schema-IDs und Datentypen vollständig
   erfüllen;
4. Zeitstempel UTC, eindeutig und korrekt ausgerichtet sind;
5. keine ungeklärten konflikthaften Duplikate bestehen;
6. keine harte OHLCV-Invariante verletzt ist;
7. alle Lücken vollständig inventarisiert und klassifiziert sind;
8. keine synthetische Zeile im beobachteten kanonischen Artefakt enthalten ist;
9. Reconciliation-Gleichungen exakt erfüllt sind;
10. Startzeit, Endzeit und Zeilenzahl mit dem Manifest übereinstimmen;
11. Schema- und Artefaktchecksummen erzeugt wurden;
12. kein `ERROR` oder `CRITICAL` offen ist;
13. jede S2-Zeile genau eine gültige `market_segment_id` besitzt;
14. sämtliche kanonischen S2-Qualitätsfelder vorhanden und nicht null sind;
15. `quality_gate_pass` für jede Zeile exakt nach Abschnitt 15.1 berechnet
    wurde;
16. jede veröffentlichte kanonische S2-Zeile einen vollständig und
    deterministisch berechneten booleschen `quality_gate_pass`-Wert besitzt;
    Zeilen mit `quality_gate_pass=false` bleiben Bestandteil des
    kanonischen S2-Artefakts, werden nicht stillschweigend entfernt und
    werden von nachgelagerten Stufen gemäß deren Stage Contracts
    fail-closed verarbeitet;
17. `quality_reason_codes` deterministisch sortiert ist;
18. S2 exakt das Schema `rcc002.stage.s2-validated/1.0.0` erfüllt.

Kriterium 16 konkretisiert für S2 das kanonische
Row-Preservation-Prinzip aus `RCC_002_DATA_PIPELINE_SPECIFICATION` §5.8.

Der Gate-Status lautet genau:

- `PASS`,
- `FAIL`,
- `PASS_WITH_APPROVED_EXCEPTIONS`.

`PASS_WITH_APPROVED_EXCEPTIONS` benötigt eine versionierte
Ausnahmeentscheidung mit Verantwortlichem, Begründung und Geltungsbereich.

Eine Ausnahme darf:

- einen `WARN` ausdrücklich als nicht blockierend klassifizieren;
- eine fehlende erwartete Quellpartition auf `WARN` herabstufen, wenn
  nachweislich keine Providerdaten existieren;
- eine rein diagnostische Einschränkung dokumentieren.

Sie darf weder einen aktiven zeilenbezogenen `ERROR` oder `CRITICAL`
überstimmen noch `quality_gate_pass=false` in `true` umwandeln.

## 21. Testanforderungen

### 21.1 Unit Tests

Mindestens erforderlich:

- gültige Einzelkerze;
- jede OHLC-Verletzung separat;
- negative und null Volumina;
- ungültige numerische Werte;
- UTC- und Alignment-Fälle;
- identische und konflikthafte Duplikate;
- Einzel- und Mehrfachlücken;
- inklusive Zeilenzahlformel;
- Spreadsheet-Zeilenlimit-Erkennung;
- Schema-Fingerprint;
- Reason-Code- und Severity-Mapping;
- deterministische `market_segment_id`;
- `quality_gap_before` und `quality_gap_after` an inneren und äußeren Grenzen;
- vollständige Wahrheitstabelle von `quality_gate_pass`;
- genehmigt aufgelöster und aktiver Quellkonflikt;
- deterministische Sortierung von `quality_reason_codes`;
- Ablehnung historischer Aliasfelder im kanonischen Ausgang.

### 21.2 Property-Based Tests

SHOULD geprüft werden:

- Sortierung verändert keine eindeutigen Inhalte;
- Deduplizierung identischer Zeilen ist idempotent;
- erneute Validierung eines unveränderten S2-Artefakts erzeugt identische
  Ergebnisse;
- Reconciliation bleibt für zufällige gültige Zeitreihen erfüllt;
- eingefügte Lücken werden vollständig und exakt erkannt;
- gleiche Marktidentität und gleiche Lücken erzeugen dieselben
  `market_segment_id`-Werte;
- keine Zeile mit blockierendem Reason Code erhält
  `quality_gate_pass=true`;
- eine zusätzliche physische Partitionierung verändert keine S1- oder
  S2-Semantik.

### 21.3 Golden Fixtures

Es MUST kleine versionierte Referenzdatensätze geben für:

- vollständig gültige Zeitreihe;
- jede kritische Fehlerklasse;
- genehmigte Provider-Lücke;
- Partition mit Überlappung;
- historische Excel-Trunkierung;
- inkrementelle Quellrevision.

Erwartete Reports und Exit-Codes werden gemeinsam mit den Fixtures versioniert.

### 21.4 Integration Tests

Mindestens erforderlich:

- vollständiger S0-bis-S2-Minibuild;
- Abbruch bei korrupter Partition;
- Abbruch bei konflikthaftem Duplikat;
- erfolgreicher Build mit identischem Duplikat und vollständiger Lineage;
- erfolgreicher beobachteter Build mit dokumentierter Lücke;
- getrennte Erzeugung einer optionalen synthetischen Kontinuitätsansicht;
- deterministischer Wiederholungsbuild;
- Ablehnung einer unbekannten S1- oder S2-Major-Schemaversion;
- vollständige Übergabe von `quality_gate_pass` an `data_gate_pass`.

## 22. Legacy-Validierung

### 22.1 Historische Signaldatei

Die verifizierte Übereinstimmung der zwölf Signalregeln über 2.721.034 Zeilen
belegt die Signaltransformation, nicht automatisch:

- vollständige Rohdatenabdeckung;
- fehlerfreie Zeitachse;
- korrekte Warm-up-Behandlung;
- Abwesenheit von Quelllücken.

Diese Punkte müssen bei einer Legacy-Reproduktion separat geprüft werden.

### 22.2 Historische Regimedatei

Die null Regelabweichungen über 1.048.575 Datenzeilen bestätigen die
Regimeberechnung innerhalb des vorhandenen Ausschnitts.

Die exakte Zeilenzahl an der Excel-Grenze und die längere vorgelagerte
Signaldatei erzwingen jedoch:

- Status `NON_CANONICAL_LEGACY_ARTIFACT`;
- Finding `DV_FILE_SUSPECTED_ROW_LIMIT_TRUNCATION`;
- keine Verwendung als vollständige RCC-002-Referenz;
- reproduzierbaren Neubau der Regimefelder aus einer vollständigen validierten
  Eingabe.

### 22.3 Legacy-Vergleich

RCC-002 MUST Legacy-Ergebnisse nicht durch Überschreiben historischer Dateien
„reparieren“.

Stattdessen werden getrennt erhalten und vergleichend dokumentiert:

- Originalartefakt;
- rekonstruierter Legacy-Build;
- neuer RCC-002-Build.

## 23. Implementierungsanforderungen

Die Implementierung MUST:

- als eigenständig testbare Module strukturiert sein;
- `semantic_build_configuration` und
  `physical_publication_configuration` getrennt verarbeiten;
- Konfigurationen statt fest codierter Projektpfade verwenden;
- unbekannte oder unklassifizierte Konfigurationsoptionen fail-closed
  ablehnen;
- die registrierten S0-, S1- und S2-Schema-IDs prüfen;
- historische Aliasfelder vor dem kanonischen Ausgang vollständig auflösen;
- atomar schreiben;
- temporäre Dateien nach Fehlern eindeutig markieren;
- strukturierte Exit-Codes liefern;
- keine Warnung ausschließlich als Terminaltext verlieren;
- bei kritischen Fehlern einen von null verschiedenen Exit-Code liefern;
- Reports vor einem kontrollierten Abbruch vollständig schreiben, soweit
  technisch sicher möglich;
- existierende kanonische Artefakte nicht still überschreiben.

Die Implementierung SHOULD Streaming oder partitionierte Verarbeitung
unterstützen, ohne dass sich Validierungsregeln gegenüber einem vollständigen
In-Memory-Build ändern.

## 24. Abnahmekriterien

### 24.1 Spezifikationsreife vor Implementierungsfreigabe

Die Spezifikation ist bereit für `Approved for Implementation`, wenn:

1. S0-, S1- und S2-Schema-IDs, Felder, Typen und Nullsemantik vollständig
   festgelegt sind;
2. alle Regeln in maschinenlesbar umsetzbare Prüfverträge überführt sind;
3. alle Reason Codes, Prioritäten, Severities und Buildwirkungen registriert
   sind;
4. `market_segment_id`, Qualitätsfelder und `quality_gate_pass` eindeutig
   spezifiziert sind;
5. `semantic_build_configuration` und
   `physical_publication_configuration` vollständig getrennt sind;
6. Golden-Fixture-Inhalte und erwartete Resultate spezifiziert sind;
7. Unit-, Property- und Integrationstestverträge vollständig definiert sind;
8. Manifest-, Reconciliation- und Publication-Gate-Verträge vollständig
   definiert sind;
9. alle vorgeschriebenen internen und externen Review-Gates der
   Spezifikationsbaseline bestanden sind;
10. keine offene Entscheidung die fachliche Semantik oder ein logisches
    Schema verändern kann.

### 24.2 Abnahme der Implementierung

Die spätere Implementierung ist akzeptiert, wenn:

1. alle Golden Fixtures exakt bestanden sind;
2. Unit-, Property- und Integrationstests bestanden sind;
3. die BTCUSDT-1m-Rohdaten vollständig inventarisiert wurden;
4. erwartete Zeilenzahl und Zeitabdeckung unabhängig verifiziert wurden;
5. die Legacy-Trunkierung reproduzierbar erkannt wird;
6. ein deterministischer S0-bis-S2-Vollbuild auf der Workstation bestanden
   ist;
7. ein unabhängiger Rebuild mindestens semantische Gleichheit erreicht;
8. Manifest und Reconciliation ohne offene Fehler vollständig sind;
9. alle S2-Publication-Gates automatisiert geprüft werden;
10. keine physische Partitionierungs- oder Writeränderung die semantischen
    S1- oder S2-Fingerprints verändert.

## 25. Offene Implementierungsparameter

### 25.1 Vor `Approved for Implementation` festzulegen

Folgende semantische Profile müssen vor der Implementierungsfreigabe
versioniert vorliegen:

- Validierungsregelprofil und `quality_rule_version`;
- Reason-Code-Prioritätsregister;
- statistische Schwellenwerte für nicht destruktive Anomalieflags;
- Registry zulässiger Provider-Ausnahmen;
- Segment-ID-Kanonisierungsprofil;
- Schema-Kompatibilitätsprofil;
- Länge und Semantik des inkrementellen Überlappungsfensters;
- numerische Präzisions- und Toleranzprofile.

Der kanonische Timestamp-Typ ist bereits festgelegt als:

```text
UTC-Timestamp in Millisekunden
```

### 25.2 Während der Implementierung konkretisierbar

Folgende physische Parameter dürfen innerhalb registrierter Profile während
der Implementierung konkretisiert werden:

- Parquet-Kompression;
- Row-Group-Größe;
- physische Partitionsgröße;
- Writeroptimierungen;
- Aufbewahrungsdauer temporärer und quarantänisierter Artefakte;
- portable physische Speicherorte.

Diese Parameter gehören zur
`physical_publication_configuration` und dürfen weder fachliche Werte noch
logische S1-/S2-Schemas oder semantische Fingerprints verändern.

## 26. Freigabestatus und nächster Schritt

`RCC-002-SCR-004` bestätigte die dort geprüften wissenschaftlichen
Korrekturen als geschlossen.

Der vollständige Architecture Integrity Review `RCC-002-AIR-001` bewertete
die Spezifikationsfamilie als:

```text
NOT PASSED – ARCHITECTURE CORRECTIONS REQUIRED
```

Version 0.4.0 bewahrt die AIR-001-Korrekturen aus Version 0.3.0 und
korrigiert zusätzlich:

- `SCR-005-B02` – eindeutige Eigentumszuordnung von S0-Provenienz,
  Source Manifest und `semantic_build_configuration.source_expectations`;
- `SCR-005-M02` – eindeutige Übergabe von `quality_gate_pass` an S6 sowie
  Stage-Abbruch bei strukturell ungültigem Eingang.

Sie aktualisiert außerdem die übergeordnete Abhängigkeit auf:

```text
RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md
Version 0.7.0
```

Die Befunde sind erst geschlossen, wenn alle abhängigen Spezifikationen
konsistent aktualisiert, neu paketiert und erneut geprüft sind.

Der aktuelle Status lautet:

```text
SCR-005-Corrected Draft – Scientific Consistency Re-Review 006 Pending
```

Nächste vorgeschriebene Schritte:

1. übrige abhängige Spezifikationen korrigieren;
2. vollständige interne Qualitätskontrolle;
3. neues vollständiges Spezifikationspaket;
4. fokussierter Scientific Consistency Re-Review;
5. fokussierter Architecture Integrity Re-Review;
6. Editorial Pass;
7. Internal Certification;
8. Claude Independent Architecture Review;
9. Gemini Independent Scientific and Adversarial Audit;
10. ChatGPT Final Consolidation;
11. `Baseline V1 Certified`;
12. Implementierungsfreigabe.

---

# Eingebettetes Dokument 3 von 7

## Quelldatei: `RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md`

# RCC-002 Indicator Specification

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Scientific Software Specification |
| Dokument-ID | RCC-002-IS |
| Titel | Indicator Specification |
| Speicherort im Repository | `docs/specifications/RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md` |
| Dateiname | `RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md` |
| Version | 0.4.3 |
| Datum | 2026-07-23 |
| Status | SCR-005-Corrected Draft – Scientific Consistency Re-Review 006 Pending |
| Übergeordnetes Dokument | `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`, Version 0.7.1 |
| Direkte Abhängigkeit | `RCC_002_DATA_VALIDATION_2026-07-23.md`, Version 0.4.2 |
| Geltungsbereich | S3_INDICATORS der RCC-002-Datenpipeline |
| Referenziert durch | Signaltransformation; Regime- und Gate-Spezifikation; Labels; Backtest; Paper-/Live-Parität |
| Autoritative Sprache | Mathematische Definitionen und englische Feldnamen sind normativ; deutsche Erläuterungen dienen der fachlichen Präzisierung |

### Review-Nachweis

| Prüfung | Status | Ergebnis |
|---|---|---|
| Struktur- und Nummerierungsprüfung | Bestanden | Kapitel und Indikatorregister vollständig |
| Formel- und Indexprüfung | Bestanden | Fenstergrenzen, Seeds und erste gültige Zeitpunkte explizit |
| Nullfallprüfung | Bestanden | Division-durch-null- und Flat-Market-Fälle definiert |
| Kausalitätsprüfung | Bestanden | Keine zentrierten oder zukunftsbezogenen Berechnungen |
| Lücken- und Partitionsprüfung | Bestanden | State Reset, State Carry und Rebuild-Reichweite definiert |
| Legacy-Trennungsprüfung | Bestanden | Reproduktion und neuer kanonischer Standard bleiben getrennt |
| Scientific Consistency Review | `RCC-002-SCR-004` bestanden | Die dort geprüften wissenschaftlichen Befunde sind geschlossen; erneuter fokussierter Review nach den semantisch relevanten AIR-001-Korrekturen erforderlich |
| Architecture Integrity Review | `RCC-002-AIR-001` nicht bestanden; Korrektur eingearbeitet | Version 0.3.0 korrigiert die diesem Dokument zugeordneten Teile von `AIR-001-B01`, `AIR-001-M01` und `AIR-001-M03`; dokumentübergreifender Re-Review ausstehend |
| Scientific Consistency Re-Review 005 | `RCC-002-SCR-005` nicht bestanden; Korrektur eingearbeitet | Version 0.4.0 vereinheitlicht die Schemaidentität gemäß `SCR-005-M01`; SCR-006 ausstehend |
| C1 Patch Release | `RCC-002-C1-SCR` bestanden mit Minor Findings | Version 0.4.1: patch release: normative clarification of Canonical Row Preservation semantics (C1) in §4.3 und §30 Kriterium 2. No intended behavioural change. |
| Minor Correction Cycle | `RCC-002-SCR-007-MinFV` umgesetzt | Version 0.4.2, 2026-07-27: Minor correction cycle: version, dependency, terminology, checklist and cross-reference consistency corrections. |
| AIR4-MIN-01 Correction | `RCC-002-AIR-004` Minor Finding behoben | Version 0.4.3, 2026-07-27: Clarified that PASS_WITH_APPROVED_EXCEPTIONS carve-outs are exhaustive and cannot be extended by approval alone. |

## 1. Zweck

Dieses Dokument definiert die kanonischen mathematischen und technischen
Berechnungsregeln der RCC-002-Indikatoren.

Es beseitigt insbesondere Mehrdeutigkeiten bei:

- Glättungsverfahren,
- Initialisierung und Seed-Werten,
- Rolling-Window-Grenzen,
- Standardabweichungsdefinition,
- Nullnennern,
- Warm-up,
- Datenlücken,
- Partitionsübergängen,
- numerischer Präzision,
- Legacy-Reproduktion.

Ziel ist, dass dieselben validierten OHLCV-Daten auf Workstation, Notebook,
Backtest, Paper Trading und Live-System dieselben Indikatorwerte erzeugen.

## 2. Geltungsbereich

### 2.1 Enthaltene kanonische Indikatoren

RCC-002 spezifiziert:

1. Simple Moving Average 200.
2. Exponential Moving Average 50.
3. Relative Strength Index 14 nach Wilder.
4. MACD 12/26 mit Signal 9 und Histogramm.
5. Bollinger Bands 20/2.
6. Stochastic %K 14.
7. Average True Range 14 nach Wilder.
8. Rate of Change 12.
9. On-Balance Volume.
10. Commodity Channel Index 20.
11. Money Flow Index 14.
12. Average Directional Index 14 nach Wilder.

### 2.2 Nicht enthalten

Nicht Gegenstand dieses Dokuments sind:

- bullish/bearish/neutral Signalgrenzen,
- Gewichtung oder Kombination von Indikatoren,
- Marktregime,
- Long-/Short-Gates,
- Strategie-Entry oder -Exit,
- Positionsgröße,
- Forward Returns oder Labels.

Diese Entscheidungen gehören in nachgelagerte Spezifikationen.

## 3. Normative Konventionen

### 3.1 Zeitindex

`t` bezeichnet die Position einer vollständig geschlossenen, validierten und
zeitlich geordneten Kerze.

Für jeden Indikatorwert bei `t` dürfen ausschließlich Daten mit Index
`i <= t` verwendet werden.

### 3.2 Preise und Volumen

Es gelten:

- `O_t`: Open,
- `H_t`: High,
- `L_t`: Low,
- `C_t`: Close,
- `V_t`: Basisasset-Volumen.

Alle Eingaben stammen aus S2_VALIDATED.

### 3.3 Fenster

Ein Rolling Window der Länge `n` bei `t` umfasst einschließlich beider Grenzen:

`[t - n + 1, ..., t]`

Es enthält exakt `n` zeitlich zusammenhängende gültige Beobachtungen.

`min_periods` MUST dem vollständigen Fenster `n` entsprechen, sofern bei einem
Indikator keine abweichende Regel ausdrücklich definiert ist.

### 3.4 Numerische Präzision

Kanonische Berechnungen und persistierte numerische Indikatorfelder MUST
IEEE-754 Binary64 (`float64`) gemäß dem registrierten numerischen Profil
verwenden.

Zwischenergebnisse dürfen:

- nicht auf Anzeigepräzision gerundet,
- nicht in `float32` herabgestuft,
- nicht durch formatierte Textwerte ersetzt,
- nicht ohne eigenes numerisches Profil in höherer Präzision berechnet und
  anschließend zurückkonvertiert

werden.

Rundung ist nur in nichtkanonischen Berichten zulässig.

### 3.5 Ungültiger Wert

Ein noch nicht berechenbarer oder qualitätsbedingt ungültiger Indikatorwert
wird im logischen S3-Schema als `null` gespeichert und durch sein separates
Validitätsfeld ausgewiesen.

Eine Implementierung darf während der Berechnung intern IEEE-754 `NaN`
verwenden, muss diesen Zustand vor der kanonischen Serialisierung jedoch
deterministisch in logisches `null` überführen. Unendliche Werte sind weder
intern als gültiges Ergebnis noch im kanonischen Ausgang zulässig.

`0` ist ein fachlicher Wert und darf nicht allgemein für „ungültig“ verwendet
werden.

### 3.6 Kausalität

Unzulässig sind:

- `center=True`,
- negative Shifts zur Feature-Bildung,
- Backward Fill,
- Normalisierung gegen zukünftige oder vollständige Datensatzstatistiken,
- rückwirkende Neuberechnung früherer Regime- oder Signalzustände anhand
  späterer Werte.

## 4. Eingabevertrag

### 4.1 Eingabeschema

S3 akzeptiert ausschließlich:

```text
rcc002.stage.s2-validated/1.0.0
```

und erzeugt:

```text
rcc002.stage.s3-indicators/1.0.0
```

Unbekannte Major-Versionen werden fail-closed abgelehnt. Additive optionale
Felder einer neueren Minor-Version dürfen nur bei einer registrierten
Kompatibilitätsregel übernommen werden.

### 4.2 Pflichtfelder

S3 benötigt:

- `source_snapshot_id`,
- `source_row_id`,
- `provider`,
- `market_type`,
- `symbol`,
- `interval`,
- `open_time`,
- `close_time`,
- `open`,
- `high`,
- `low`,
- `close`,
- `volume`,
- `market_segment_id`,
- `quality_is_observed`,
- `quality_is_synthetic`,
- `quality_has_source_conflict`,
- `quality_gap_before`,
- `quality_gap_after`,
- `quality_timestamp_valid`,
- `quality_ohlc_valid`,
- `quality_volume_valid`,
- `quality_market_values_valid`,
- `quality_status`,
- `quality_reason_codes`,
- `quality_rule_version`,
- `quality_gate_pass`.

Sämtliche S2-Felder werden mit identischem Namen, logischem Typ,
Nullverhalten und Wert unverändert in S3 weitergeführt.

### 4.3 Eingabeinvarianten

Vor S3 MUST gelten:

- Zeitindex streng aufsteigend,
- Primärschlüssel eindeutig,
- kanonischer Schlüssel
  `(market_type, symbol, interval, open_time)` vollständig,
- bei unkonsolidierten Multi-Provider-Daten zusätzlich `provider`
  unmittelbar vor `market_type` im Schlüssel und in der Sortierreihenfolge,
- OHLCV-Invarianten bestanden,
- keine nicht endlichen Pflichtwerte,
- sämtliche S2-Qualitätsfelder vorhanden und nicht null,
- `quality_gate_pass` deterministisch nach der Data Validation Specification
  berechnet,
- Schema-ID und Schema-Fingerprint freigegeben.

S3 darf eine unvalidierte Rohdatei nicht direkt konsumieren.

Jede S2-Eingabezeile muss einen gültigen und deterministisch nach der Data
Validation Specification berechneten booleschen `quality_gate_pass`-Wert
besitzen. Zeilen mit `quality_gate_pass=false` bleiben Teil des
kanonischen Datenstroms und des kanonischen S3-Artefakts; für sie werden
keine gültigen Indikatorwerte erzeugt und keine Indikatorwerte als gültig
veröffentlicht. Row Identity, Zeilenreihenfolge und `S3_rows = S2_rows`
bleiben davon unberührt. Diagnoseberechnungen dürfen zusätzliche
Informationen erzeugen, dürfen aber die kanonische
Row-Preservation-Semantik nicht verändern.

### 4.4 Synthetische Kerzen

Kanonische Indikatoren werden standardmäßig ausschließlich auf beobachteten
Kerzen berechnet.

Indikatoren auf einer synthetischen Kontinuitätsansicht benötigen:

- eigene Build- und View-ID,
- eigene Indikatorprofil-ID,
- explizite Kennzeichnung,
- getrennte Sensitivitätsanalyse.

Sie dürfen kanonische beobachtete Indikatoren nicht überschreiben.

### 4.5 Schlüssel, Sortierung und Zeileninvariante

S3 übernimmt den vollständigen S2-Primärschlüssel und dessen aufsteigende
Sortierung unverändert.

Es muss gelten:

```text
S3_rows = S2_rows
```

S3 darf keine Zeile hinzufügen, entfernen, duplizieren oder umsortieren.

## 5. Indikatorregister

Das kanonische Profil lautet:

```text
indicator_profile_id=RCC002_CANONICAL_INDICATORS_V1
indicator_profile_version=1.0.0
indicator_schema_id=rcc002.stage.s3-indicators
indicator_schema_version=1.0.0
indicator_schema_ref=rcc002.stage.s3-indicators/1.0.0
```

`indicator_schema_ref` ist die deterministisch abgeleitete qualifizierte
Referenz und kein konkurrierender Schema-ID-Wert.

| ID | Kanonische Felder | Parameter | Eingaben |
|---|---|---|---|
| `SMA_CLOSE_V1` | `sma_close_200` | `n=200` | `close` |
| `EMA_CLOSE_V1` | `ema_close_50` | `n=50` | `close` |
| `RSI_WILDER_V1` | `rsi_wilder_14` | `n=14` | `close` |
| `MACD_EMA_V1` | `macd_line_12_26`, `macd_signal_line_12_26_9`, `macd_hist_12_26_9` | `fast=12`, `slow=26`, `signal=9` | `close` |
| `BBANDS_POP_V1` | `bb_mid_20`, `bb_upper_20_2`, `bb_lower_20_2`, `bb_width_20_2` | `n=20`, `k=2`, `ddof=0` | `close` |
| `STOCH_K_V1` | `stoch_k_14` | `n=14` | `high`, `low`, `close` |
| `ATR_WILDER_V1` | `true_range`, `atr_wilder_14` | `n=14` | `high`, `low`, `close` |
| `ROC_SIMPLE_V1` | `roc_close_12_pct` | `n=12` | `close` |
| `OBV_V1` | `obv` | Seed `0` | `close`, `volume` |
| `CCI_MAD_V1` | `typical_price`, `cci_20` | `n=20`, constant `0.015` | `high`, `low`, `close` |
| `MFI_V1` | `mfi_14` | `n=14` | `high`, `low`, `close`, `volume` |
| `ADX_WILDER_V1` | `plus_di_14`, `minus_di_14`, `dx_14`, `adx_wilder_14` | `n=14` | `high`, `low`, `close` |

Die positive Allowlist kanonischer numerischer S3-Indikatorfelder lautet in
dieser Reihenfolge:

1. `sma_close_200`;
2. `ema_close_50`;
3. `rsi_wilder_14`;
4. `macd_line_12_26`;
5. `macd_signal_line_12_26_9`;
6. `macd_hist_12_26_9`;
7. `bb_mid_20`;
8. `bb_upper_20_2`;
9. `bb_lower_20_2`;
10. `bb_width_20_2`;
11. `stoch_k_14`;
12. `true_range`;
13. `atr_wilder_14`;
14. `roc_close_12_pct`;
15. `obv`;
16. `typical_price`;
17. `cci_20`;
18. `mfi_14`;
19. `plus_di_14`;
20. `minus_di_14`;
21. `dx_14`;
22. `adx_wilder_14`.

Für jedes Feld `x` dieser Allowlist erzeugt S3 unmittelbar anschließend:

```text
x
x_valid
x_warmup_complete
x_reason_codes
```

Dabei gilt:

- `x` hat den logischen Typ nullable `Float64`;
- `x_valid` hat den nicht-nullbaren Typ Boolean;
- `x_warmup_complete` hat den nicht-nullbaren Typ Boolean;
- `x_reason_codes` hat den nicht-nullbaren Typ geordnete Liste aus
  UTF-8-Strings.

S3 ist Eigentümerstufe aller vier Felder jeder Indikatorgruppe.

Jede Änderung einer Formel, Initialisierung, Nullfallregel oder
Warm-up-Semantik benötigt eine neue Indikator-ID oder Major-Version.

Additive neue Indikatorgruppen benötigen mindestens eine neue Minor-Version
des S3-Schemas. Änderungen an Namen, Typen, Nullsemantik, Formeln,
Segmentierung oder Gültigkeitssemantik benötigen eine neue Major-Version.

Historische Namen wie `ma200`, `ema50`, `rsi`, `macd_hist`, `bb_upper`,
`bb_lower`, `bb_width`, `stoch_k`, `atr`, `roc`, `cci`, `mfi` oder `adx`
sind keine kanonischen S3-Aliasfelder. Sie dürfen nur innerhalb eines
registrierten Legacy-Profils verwendet werden. Eine bloße Umbenennung in ein
kanonisches Feld ist unzulässig, wenn Formel, Seed, Warm-up oder
Lückenverhalten nicht nachweislich identisch sind.

## 6. Gemeinsame Hilfsdefinitionen

### 6.1 Simple Moving Average

Für eine Serie `X` und Fenster `n`:

`SMA_n(X)_t = (1 / n) * sum(X_i, i=t-n+1...t)`

Der erste gültige Wert liegt bei `t = n - 1`, sofern die Serie am Index `0`
beginnt und das Fenster qualitätsgültig ist.

### 6.2 Kanonische EMA

Für Periode `n`:

`alpha = 2 / (n + 1)`

Seed:

`EMA_n(X)_(n-1) = SMA_n(X)_(n-1)`

Rekursion für `t >= n`:

`EMA_n(X)_t = alpha * X_t + (1 - alpha) * EMA_n(X)_(t-1)`

Vor `t = n - 1` ist die EMA logisch `null`. Eine interne
Berechnungsrepräsentation als `NaN` richtet sich nach Abschnitt 3.5.

Diese Seed-Regel ist normativ. Eine Bibliotheksfunktion darf nur verwendet
werden, wenn sie exakt dieselben Werte erzeugt.

### 6.3 Wilder Average

Für eine nichtnegative Serie `X` und Periode `n`:

Seed:

`WilderAvg_n(X)_s = mean(X_i, i=s-n+1...s)`

Rekursion:

`WilderAvg_n(X)_t = ((n - 1) * WilderAvg_n(X)_(t-1) + X_t) / n`

Der Indikatorabschnitt legt jeweils fest, welcher Index `s` das erste
vollständige Seed-Fenster beendet.

### 6.4 Wilder Smoothed Sum

Für Directional Movement werden geglättete Summen verwendet.

Seed:

`WilderSum_n(X)_s = sum(X_i, i=s-n+1...s)`

Rekursion:

`WilderSum_n(X)_t = WilderSum_n(X)_(t-1) - WilderSum_n(X)_(t-1)/n + X_t`

### 6.5 Lokaler Segmentindex

Alle in den Formeln verwendeten Indizes beginnen innerhalb jeder
berechnungsfähigen `indicator_segment_id` erneut bei lokalem Index `0`.

Ein Wert mit lokalem Index `t` darf ausschließlich:

- qualitätsfreigegebene Zeilen derselben `market_segment_id`;
- Zeilen derselben `indicator_segment_id`;
- gegenwarts- oder vergangenheitsbezogene Werte mit lokalem Index `i <= t`

verwenden.

Globale Dateizeilennummern oder Partitionsgrenzen dürfen Seed, Warm-up oder
Fenstergrenzen nicht verändern.

## 7. Simple Moving Average 200

### 7.1 Definition

`sma_close_200_t = SMA_200(C)_t`

### 7.2 Gültigkeit

Erster mathematisch gültiger Wert:

`t = 199`

Er ist nur qualitätsgültig, wenn alle 200 Kerzen beobachtet, gültig und
zeitlich zusammenhängend sind.

### 7.3 Nullfall

Da alle Close-Preise positiv sein müssen, existiert kein zulässiger
Division-durch-null-Fall.

## 8. Exponential Moving Average 50

### 8.1 Definition

`ema_close_50_t = EMA_50(C)_t`

mit:

`alpha = 2 / 51`

### 8.2 Seed

`ema_close_50_49 = mean(C_0...C_49)`

### 8.3 Gültigkeit

Erster mathematisch gültiger Wert:

`t = 49`

Nach einer Datenlücke wird der EMA-Zustand zurückgesetzt. Ein neuer gültiger
Seed benötigt 50 aufeinanderfolgende qualitätsgültige Kerzen.

## 9. Relative Strength Index 14

### 9.1 Preisänderung

Für `t >= 1`:

`delta_t = C_t - C_(t-1)`

`gain_t = max(delta_t, 0)`

`loss_t = max(-delta_t, 0)`

### 9.2 Seed

Die ersten 14 Änderungen sind:

`delta_1...delta_14`

Damit:

`avg_gain_14 = mean(gain_1...gain_14)`

`avg_loss_14 = mean(loss_1...loss_14)`

### 9.3 Rekursion

Für `t >= 15`:

`avg_gain_t = ((13 * avg_gain_(t-1)) + gain_t) / 14`

`avg_loss_t = ((13 * avg_loss_(t-1)) + loss_t) / 14`

### 9.4 RSI

Wenn `avg_gain_t > 0` und `avg_loss_t > 0`:

`RS_t = avg_gain_t / avg_loss_t`

`rsi_wilder_14_t = 100 - 100 / (1 + RS_t)`

### 9.5 Nullfälle

- Wenn `avg_gain_t = 0` und `avg_loss_t = 0`, dann RSI `= 50`.
- Wenn `avg_gain_t > 0` und `avg_loss_t = 0`, dann RSI `= 100`.
- Wenn `avg_gain_t = 0` und `avg_loss_t > 0`, dann RSI `= 0`.

### 9.6 Gültigkeit

Erster gültiger Wert:

`t = 14`

Es werden damit 15 Close-Preise und 14 Preisänderungen benötigt.

## 10. MACD 12/26/9

### 10.1 Fast und Slow EMA

`ema_fast_t = EMA_12(C)_t`

`ema_slow_t = EMA_26(C)_t`

### 10.2 MACD-Linie

`macd_line_12_26_t = ema_fast_t - ema_slow_t`

Erster gültiger Wert:

`t = 25`

### 10.3 Signallinie

Die Signallinie ist eine kanonische EMA 9 der gültigen MACD-Linie.

Seed:

`macd_signal_line_12_26_9_33 = mean(macd_line_25...macd_line_33)`

Rekursion ab `t = 34` mit:

`alpha_signal = 2 / 10`

### 10.4 Histogramm

`macd_hist_12_26_9_t = macd_line_12_26_t - macd_signal_line_12_26_9_t`

Erster gültiger Signal- und Histogrammwert:

`t = 33`

### 10.5 Qualitätsregel

Fast EMA, Slow EMA und Signal-EMA müssen aus derselben lückenfreien
Beobachtungssequenz stammen.

## 11. Bollinger Bands 20/2

### 11.1 Mittellinie

`bb_mid_20_t = SMA_20(C)_t`

### 11.2 Populationsstandardabweichung

`variance_t = (1/20) * sum((C_i - bb_mid_20_t)^2, i=t-19...t)`

`std_pop_20_t = sqrt(variance_t)`

Damit gilt ausdrücklich:

`ddof = 0`

### 11.3 Bänder

`bb_upper_20_2_t = bb_mid_20_t + 2 * std_pop_20_t`

`bb_lower_20_2_t = bb_mid_20_t - 2 * std_pop_20_t`

### 11.4 Bandbreite

`bb_width_20_2_t = (bb_upper_20_2_t - bb_lower_20_2_t) / bb_mid_20_t`

Da Close-Preise positiv sind, muss `bb_mid_20_t > 0` gelten.

### 11.5 Gültigkeit

Erster gültiger Wert aller Bollinger-Felder:

`t = 19`

## 12. Stochastic %K 14

### 12.1 Fensterextreme

`lowest_low_14_t = min(L_i, i=t-13...t)`

`highest_high_14_t = max(H_i, i=t-13...t)`

### 12.2 Definition

Wenn:

`highest_high_14_t > lowest_low_14_t`

dann:

`stoch_k_14_t = 100 * (C_t - lowest_low_14_t) / (highest_high_14_t - lowest_low_14_t)`

### 12.3 Flat-Window-Fall

Wenn:

`highest_high_14_t = lowest_low_14_t`

dann:

- `stoch_k_14_t = 50`,
- Qualitätsflag `IND_STOCH_FLAT_WINDOW`.

Der Wert 50 beschreibt fehlende Lageinformation innerhalb eines vollständig
flachen Fensters und ist nicht „ungültig“.

### 12.4 Gültigkeit

Erster gültiger Wert:

`t = 13`

## 13. True Range und Average True Range 14

### 13.1 True Range

Für den ersten Index einer lückenfreien Sequenz:

`true_range_0 = H_0 - L_0`

Für `t >= 1`:

`true_range_t = max(H_t - L_t, abs(H_t - C_(t-1)), abs(L_t - C_(t-1)))`

### 13.2 ATR-Seed

`atr_wilder_14_13 = mean(true_range_0...true_range_13)`

### 13.3 Rekursion

Für `t >= 14`:

`atr_wilder_14_t = ((13 * atr_wilder_14_(t-1)) + true_range_t) / 14`

### 13.4 Gültigkeit

- `true_range` ist ab dem ersten Index einer lückenfreien Sequenz gültig.
- `atr_wilder_14` ist erstmals bei `t = 13` gültig.

Nach einer Lücke wird `C_(t-1)` nicht über die Lücke hinweg verwendet. Die
erste Kerze der neuen Sequenz beginnt erneut mit `H_t - L_t`.

## 14. Rate of Change 12

### 14.1 Definition

`roc_close_12_pct_t = 100 * (C_t / C_(t-12) - 1)`

### 14.2 Gültigkeit

Erster gültiger Wert:

`t = 12`

Es werden 13 Close-Preise benötigt.

`C_(t-12)` muss aufgrund der S2-Preisregeln größer als null sein.

## 15. On-Balance Volume

### 15.1 Seed

Am ersten Index einer lückenfreien Sequenz:

`obv_0 = 0`

### 15.2 Rekursion

Für `t >= 1`:

- Wenn `C_t > C_(t-1)`, dann `obv_t = obv_(t-1) + V_t`.
- Wenn `C_t < C_(t-1)`, dann `obv_t = obv_(t-1) - V_t`.
- Wenn `C_t = C_(t-1)`, dann `obv_t = obv_(t-1)`.

### 15.3 Gültigkeit und Vergleichbarkeit

OBV ist ab dem Seed gültig.

Der absolute OBV-Wert hängt vom Startpunkt der Sequenz ab. Deshalb MUST:

- der Seed-Zeitpunkt dokumentiert,
- bei kanonischen Vollbuilds derselbe Datensatzanfang verwendet,
- bei Partitionen der exakte Zustand übernommen

werden.

Nach einer echten Datenlücke beginnt für die neue unabhängige Sequenz ein neuer
OBV-Seed bei null. Die gemeinsame `indicator_segment_id` weist diese
Vergleichsgrenze aus. Ein paralleles Feld `obv_segment_id` ist unzulässig.

## 16. Commodity Channel Index 20

### 16.1 Typical Price

`typical_price_t = (H_t + L_t + C_t) / 3`

### 16.2 Fenstermean

`tp_sma_20_t = mean(typical_price_i, i=t-19...t)`

### 16.3 Mean Absolute Deviation

`tp_mad_20_t = (1/20) * sum(abs(typical_price_i - tp_sma_20_t), i=t-19...t)`

Die Abweichungen beziehen sich auf den Mittelwert desselben aktuellen
20-Kerzen-Fensters.

### 16.4 Definition

Wenn `tp_mad_20_t > 0`:

`cci_20_t = (typical_price_t - tp_sma_20_t) / (0.015 * tp_mad_20_t)`

### 16.5 Flat-Window-Fall

Wenn `tp_mad_20_t = 0`:

- `cci_20_t = 0`,
- Qualitätsflag `IND_CCI_ZERO_MAD`.

### 16.6 Gültigkeit

- `typical_price` ist ab der ersten gültigen Kerze verfügbar.
- `cci_20` ist erstmals bei `t = 19` gültig.

## 17. Money Flow Index 14

### 17.1 Typical Price und Raw Money Flow

`typical_price_t = (H_t + L_t + C_t) / 3`

`raw_money_flow_t = typical_price_t * V_t`

### 17.2 Gerichteter Money Flow

Für `t >= 1`:

- Wenn `typical_price_t > typical_price_(t-1)`, dann:
  - `positive_flow_t = raw_money_flow_t`
  - `negative_flow_t = 0`
- Wenn `typical_price_t < typical_price_(t-1)`, dann:
  - `positive_flow_t = 0`
  - `negative_flow_t = raw_money_flow_t`
- Bei Gleichheit:
  - `positive_flow_t = 0`
  - `negative_flow_t = 0`

### 17.3 14-Perioden-Summen

`positive_sum_14_t = sum(positive_flow_i, i=t-13...t)`

`negative_sum_14_t = sum(negative_flow_i, i=t-13...t)`

### 17.4 MFI

Wenn beide Summen positiv sind:

`money_flow_ratio_t = positive_sum_14_t / negative_sum_14_t`

`mfi_14_t = 100 - 100 / (1 + money_flow_ratio_t)`

### 17.5 Nullfälle

- Wenn beide Summen null sind, dann MFI `= 50`.
- Wenn `positive_sum_14_t > 0` und `negative_sum_14_t = 0`, dann MFI `= 100`.
- Wenn `positive_sum_14_t = 0` und `negative_sum_14_t > 0`, dann MFI `= 0`.

### 17.6 Gültigkeit

Der erste gültige Wert liegt bei:

`t = 14`

Begründung: Für die 14 gerichteten Flows `1...14` werden 15 Typical-Price-Werte
`0...14` benötigt.

## 18. Average Directional Index 14

### 18.1 True Range

Für `t >= 1`:

`TR_t = max(H_t - L_t, abs(H_t - C_(t-1)), abs(L_t - C_(t-1)))`

### 18.2 Directional Movement

`up_move_t = H_t - H_(t-1)`

`down_move_t = L_(t-1) - L_t`

Dann:

- Wenn `up_move_t > down_move_t` und `up_move_t > 0`:
  - `plus_dm_t = up_move_t`
  - `minus_dm_t = 0`
- Wenn `down_move_t > up_move_t` und `down_move_t > 0`:
  - `plus_dm_t = 0`
  - `minus_dm_t = down_move_t`
- Andernfalls:
  - `plus_dm_t = 0`
  - `minus_dm_t = 0`

Bei Gleichheit von positiven `up_move_t` und `down_move_t` werden beide auf
null gesetzt.

### 18.3 Geglättete 14er-Summen

Am Index `t = 14`:

`tr_sum_14_14 = sum(TR_i, i=1...14)`

`plus_dm_sum_14_14 = sum(plus_dm_i, i=1...14)`

`minus_dm_sum_14_14 = sum(minus_dm_i, i=1...14)`

Für `t >= 15` gilt jeweils die Wilder-Sum-Rekursion:

`smoothed_t = smoothed_(t-1) - smoothed_(t-1)/14 + current_t`

### 18.4 Directional Indicators

Wenn `tr_sum_14_t > 0`:

`plus_di_14_t = 100 * plus_dm_sum_14_t / tr_sum_14_t`

`minus_di_14_t = 100 * minus_dm_sum_14_t / tr_sum_14_t`

Wenn `tr_sum_14_t = 0`, werden beide DI-Werte auf `0` gesetzt und
`IND_ADX_ZERO_TR` markiert.

### 18.5 Directional Index

Wenn:

`plus_di_14_t + minus_di_14_t > 0`

dann:

`dx_14_t = 100 * abs(plus_di_14_t - minus_di_14_t) / (plus_di_14_t + minus_di_14_t)`

Wenn die Summe null ist:

`dx_14_t = 0`

### 18.6 ADX-Seed

Der erste ADX ist der Mittelwert der ersten 14 gültigen DX-Werte:

`adx_wilder_14_27 = mean(dx_14_i, i=14...27)`

### 18.7 ADX-Rekursion

Für `t >= 28`:

`adx_wilder_14_t = ((13 * adx_wilder_14_(t-1)) + dx_14_t) / 14`

### 18.8 Gültigkeit

- `plus_di_14`, `minus_di_14` und `dx_14`: erstmals `t = 14`.
- `adx_wilder_14`: erstmals `t = 27`.

Es werden 28 aufeinanderfolgende Kerzen für den ersten ADX benötigt.

## 19. Warm-up-Matrix

| Feld | Erster gültiger Index | Erforderliche Kerzen |
|---|---:|---:|
| `typical_price` | 0 | 1 |
| `true_range` | 0 | 1 |
| `obv` | 0 | 1 |
| `roc_close_12_pct` | 12 | 13 |
| `stoch_k_14` | 13 | 14 |
| `atr_wilder_14` | 13 | 14 |
| `rsi_wilder_14` | 14 | 15 |
| `mfi_14` | 14 | 15 |
| `plus_di_14`, `minus_di_14`, `dx_14` | 14 | 15 |
| `bb_mid_20`, `bb_upper_20_2`, `bb_lower_20_2`, `bb_width_20_2` | 19 | 20 |
| `cci_20` | 19 | 20 |
| `macd_line_12_26` | 25 | 26 |
| `adx_wilder_14` | 27 | 28 |
| `macd_signal_line_12_26_9`, `macd_hist_12_26_9` | 33 | 34 |
| `ema_close_50` | 49 | 50 |
| `sma_close_200` | 199 | 200 |

Die Indizes beziehen sich auf den Beginn einer lückenfreien Sequenz.

## 20. Gültigkeits- und Qualitätsfelder

### 20.1 Feldbezogene Gültigkeit

Für jedes kanonische numerische Indikatorfeld `x` sind exakt die in
Abschnitt 5 definierten Begleitfelder vorgeschrieben:

```text
x_valid
x_warmup_complete
x_reason_codes
```

Eine alternative parallele Validitätsmaske ist im kanonischen S3-Schema
unzulässig.

`x_warmup_complete=true` gilt genau dann, wenn seit Beginn der aktuellen
berechnungsfähigen `indicator_segment_id` sämtliche für `x` erforderlichen
gültigen Beobachtungen oder rekursiven Seeds vorliegen.

Für eine Zeile mit `quality_gate_pass=false` gilt für jedes Indikatorfeld
`x_warmup_complete=false`, `x_valid=false` und `x=null`.

`x_valid=true` gilt genau dann, wenn:

- `quality_gate_pass=true`;
- `x_warmup_complete=true`;
- alle feldspezifischen Eingaben gültig sind;
- kein erforderliches Fenster eine `market_segment_id`- oder
  `indicator_segment_id`-Grenze überschreitet;
- ein erforderlicher rekursiver State vorhanden und verifiziert ist;
- das Ergebnis endlich ist;
- sämtliche feldspezifischen Bereichsinvarianten erfüllt sind.

In jedem anderen Fall gilt `x_valid=false` und `x=null`.

### 20.2 Reason-Code-Vertrag

`x_reason_codes` ist:

- eine nach registrierter Priorität deterministisch sortierte Liste;
- leer, wenn kein Reason Code aktiv ist;
- niemals null;
- ausschließlich auf das Feld `x` bezogen.

Das Register lautet:

```text
indicator_reason_code_registry_version=1.0.0
```

| Reason Code | Standard-Severity | `x_valid` | Bedeutung |
|---|---|:---:|---|
| `IND_WARMUP_INCOMPLETE` | `INFO` | `false` | Erforderlicher Seed oder vollständiges Fenster fehlt |
| `IND_INPUT_INVALID` | `ERROR` | `false` | Mindestens ein feldspezifischer Pflichtinput ist ungültig |
| `IND_WINDOW_CROSSES_MARKET_SEGMENT` | `ERROR` | `false` | Fenster überschreitet eine `market_segment_id`-Grenze |
| `IND_WINDOW_CROSSES_INDICATOR_SEGMENT` | `ERROR` | `false` | Fenster überschreitet eine `indicator_segment_id`-Grenze |
| `IND_SYNTHETIC_INPUT_DISALLOWED` | `ERROR` | `false` | Nicht zugelassene synthetische Eingabe |
| `IND_STATE_MISSING` | `CRITICAL` | `false` | Erwarteter rekursiver Fortsetzungsstate fehlt |
| `IND_STATE_MISMATCH` | `CRITICAL` | `false` | State passt nicht zu Build, Schema, Profil oder Schlüssel |
| `IND_NONFINITE_RESULT` | `CRITICAL` | `false` | Berechnung ergab `NaN`, `+Inf` oder `-Inf` |
| `IND_RANGE_INVARIANT_FAILED` | `CRITICAL` | `false` | Feldspezifische Bereichsinvariante verletzt |
| `IND_PROFILE_MISMATCH` | `CRITICAL` | `false` | Indikator- oder Segmentierungsprofil stimmt nicht |
| `IND_SCHEMA_MISMATCH` | `CRITICAL` | `false` | Eingabe-, Ausgabe- oder State-Schema stimmt nicht |

Die Listenreihenfolge folgt einer versionierten, im Register enthaltenen
Priorität und darf nicht von Threadplanung, Feldreihenfolge oder
Hash-Iteration abhängen.

### 20.3 Nichtkritische Sonderfälle

| Reason Code | Standard-Severity | Betroffene Felder | Definierter Wert |
|---|---|---|---:|
| `IND_STOCH_FLAT_WINDOW` | `INFO` | `stoch_k_14` | `50` |
| `IND_CCI_ZERO_MAD` | `INFO` | `cci_20` | `0` |
| `IND_ADX_ZERO_TR` | `INFO` | `plus_di_14`, `minus_di_14`, `dx_14`, gegebenenfalls `adx_wilder_14` | `0` gemäß ADX-Regeln |

Diese Sonderfälle besitzen definierte numerische Werte und sind nicht
automatisch ungültig. Der zugehörige Wert bleibt bei erfüllten übrigen Regeln
gültig, und der Sonderfallcode wird in `x_reason_codes` geführt.

### 20.4 Bereichsprüfungen

MUST gelten:

- `0 <= rsi_wilder_14 <= 100`,
- `0 <= stoch_k_14 <= 100`,
- `atr_wilder_14 >= 0`,
- `0 <= mfi_14 <= 100`,
- `0 <= plus_di_14 <= 100`,
- `0 <= minus_di_14 <= 100`,
- `0 <= dx_14 <= 100`,
- `0 <= adx_wilder_14 <= 100`,
- `bb_upper_20_2 >= bb_mid_20 >= bb_lower_20_2`,
- `bb_width_20_2 >= 0`.

Eine Verletzung nach zulässiger Float-Toleranz ist `CRITICAL`.

### 20.5 Zeilenbezogene Metadaten

S3 ergänzt auf jeder Zeile exakt:

| Feld | Logischer Typ | Nullbar | Bedeutung |
|---|---|:---:|---|
| `indicator_profile_id` | UTF-8-String | Nein | Kanonische Profil-ID |
| `indicator_profile_version` | UTF-8-String | Nein | Semantische Profilversion |
| `indicator_schema_id` | UTF-8-String | Nein | `rcc002.stage.s3-indicators` |
| `indicator_schema_version` | UTF-8-String | Nein | `1.0.0` |
| `indicator_schema_ref` | UTF-8-String | Nein | `rcc002.stage.s3-indicators/1.0.0` |
| `indicator_segment_id` | UTF-8-String | Nein | Deterministische S3-Berechnungssegment-ID |

Diese Felder gehören S3. Gleichnamige Eingabefelder sind unzulässig, sofern
sie nicht im Rahmen einer explizit geprüften S3-Revalidierung exakt denselben
Wert tragen.

## 21. Datenlücken und Segmentierung

### 21.1 Grundregel

Kein kanonischer Rolling- oder rekursiver Zustand darf eine echte Datenlücke
stillschweigend überbrücken.

### 21.2 Segment-ID

S3 MUST eine `indicator_segment_id` führen.

Die kanonische Segmentierungsregel lautet:

```text
indicator_segment_profile_id=RCC002_INDICATOR_SEGMENTATION_V1
indicator_segment_profile_version=1.0.0
```

Eine neue `indicator_segment_id` beginnt:

- an der ersten Zeile jeder `market_segment_id`;
- wenn `quality_gate_pass` gegenüber der vorherigen Zeile wechselt;
- nach einem expliziten rekursiven State Reset.

Damit bildet jede `indicator_segment_id` eine maximale zusammenhängende
Zeilenfolge mit:

- genau einer `market_segment_id`;
- konstantem `quality_gate_pass`;
- unverändertem Segmentierungsprofil;
- keinem internen expliziten State Reset.

Die ID wird deterministisch aus:

- `market_segment_id`;
- erstem `open_time` der Indikatorsequenz;
- `quality_gate_pass` der Sequenz;
- `indicator_profile_id`;
- `indicator_profile_version`;
- `indicator_segment_profile_id`;
- `indicator_segment_profile_version`

gebildet. Zufällige UUIDs sind unzulässig.

Eine `indicator_segment_id` darf genau eine `market_segment_id` referenzieren
und niemals mehrere Marktsegmente zusammenführen.

Zeilen mit `quality_gate_pass=false` erhalten eine Segment-ID, dürfen aber
keinen gültigen Indikatorwert erzeugen. Die erste nachfolgende wieder
qualitätsgültige Zeile beginnt ein neues Indikatorsegment.

### 21.3 Rolling-Indikatoren

Nach Segmentbeginn werden Rolling-Indikatoren erst nach ihrem vollständigen
Warm-up wieder gültig. Kein Rolling Window darf eine
`indicator_segment_id`-Grenze überschreiten.

### 21.4 Rekursive Indikatoren

EMA, RSI, ATR, OBV und ADX werden nach Segmentbeginn gemäß ihren Seed-Regeln
neu initialisiert.

Dadurch werden keine unbekannten Marktbewegungen über eine Lücke implizit als
unveränderte Zustände behandelt.

MACD einschließlich seiner Signal-EMA wird ebenfalls vollständig innerhalb
des neuen Segments neu initialisiert.

### 21.5 Sensitivitätsanalyse

Spätere Forschung MAY alternative Lückenpolitiken prüfen. Jede Alternative
benötigt:

- eigene Profil-ID,
- eigenen Build,
- getrennte Ergebnisse,
- Vergleich gegen die kanonische Reset-Regel.

## 22. Partitionierte Berechnung

### 22.1 Äquivalenzanforderung

Ein partitionierter Vollbuild MUST nach feldspezifischer Toleranz dieselben
Werte erzeugen wie ein serieller Build über dieselben lückenfreien Eingaben.

### 22.2 Rolling State

Für reine Rolling-Indikatoren MAY die nächste Partition die erforderlichen
vorherigen Beobachtungen als Overlap lesen.

Der Overlap wird nicht doppelt ausgegeben.

### 22.3 Rekursiver State

Rekursive Indikatoren benötigen einen expliziten State Snapshot.

Der logische State-Vertrag lautet:

```text
indicator_state_schema_id=rcc002.state.s3-indicators
indicator_state_schema_version=1.0.0
indicator_state_schema_ref=rcc002.state.s3-indicators/1.0.0
```

Dieser enthält mindestens:

- letzte kanonische Schlüsselposition,
- `market_segment_id`,
- `indicator_segment_id`,
- `indicator_profile_id`,
- `indicator_profile_version`,
- EMA-Zustände,
- RSI Average Gain und Average Loss,
- ATR-Zustand,
- OBV-Zustand,
- ADX geglättete TR-/DM-Summen und ADX-Zustand,
- erforderliche vorherige OHLC-/Typical-Price-Werte,
- noch nicht abgeschlossene Warm-up-Puffer und Warm-up-Zähler,
- `indicator_state_schema_id`,
- `indicator_state_schema_version`,
- `indicator_state_schema_ref`,
- Checksumme.

### 22.4 State-Sicherheit

Ein State Snapshot darf nur verwendet werden, wenn:

- Parent-Build-ID stimmt,
- vorherige Partition erfolgreich validiert wurde,
- Schlüssel direkt anschließt,
- State-Checksumme stimmt,
- Profil-, Schema-, Segmentierungs- und Indikatorversionen identisch sind.

Bei einem kanonischen Fortsetzungsbuild wird andernfalls abgebrochen.
Ein neuer Segment-Seed ist nur nach einer expliziten, manifestierten
State-Resetentscheidung zulässig und muss eine neue `indicator_segment_id`
beginnen. Ein stiller Fallback ist unzulässig.

## 23. Inkrementelle Neuberechnung

### 23.1 Neue Daten ohne historische Revision

Neue, direkt anschließende Kerzen MAY mit dem validierten End-State des
vorherigen Builds berechnet werden.

### 23.2 Historische Revision

Wird eine historische Kerze geändert, gelten:

- Rolling-Indikatoren müssen mindestens ab der frühesten geänderten Kerze bis
  zum Ende ihres maximalen Einflussfensters neu berechnet werden.
- Rekursive Indikatoren müssen ab der frühesten geänderten Kerze bis zum Ende
  des Datensatzes neu berechnet werden.
- Abhängige Signale, Regime, Gates und Labels müssen entsprechend invalidiert
  und neu erzeugt werden.

Eine angenommene numerische „Konvergenz“ rekursiver Indikatoren darf im
kanonischen Build nicht als Ersatz für die vollständige Neuberechnung dienen.

## 24. Legacy-Kompatibilitätsprofil

### 24.1 Zweck

Das Profil `LEGACY_BTC_SIGNAL_BUILDER_V1` dient ausschließlich der
reproduzierbaren historischen Vergleichsrechnung.

Es ist nicht der kanonische RCC-002-Indikatorstandard.

### 24.2 Verifizierte Legacy-Grundlage

Der historische Builder:

`archive/HISTORICAL_K3_K10_2026-01-06/scripts_legacy_from_root/build_price_data_with_signals.py`

stimmt bei den zwölf daraus abgeleiteten Signalspalten über 2.721.034 geprüfte
Zeilen ohne Abweichung mit der vorhandenen Datei überein.

### 24.3 Relevante Legacy-Abweichungen

Das Legacy-Profil reproduziert unter anderem:

- RSI über Pandas `ewm(alpha=1/14, adjust=False)` ohne kanonischen
  Wilder-SMA-Seed,
- MACD-EMAs über `ewm(span=n, adjust=False)` mit Pandas-Startwert,
- Bollinger-Standardabweichung mit Pandas-Standard `ddof=1`,
- ATR als einfacher Rolling Mean des True Range,
- ADX über Rolling-Summen und anschließenden Rolling Mean,
- teilweise aufgefüllte Warm-up-Werte,
- implizite Signalwerte `0` bei nicht berechenbaren Vergleichen.

### 24.4 Trennungsregeln

Legacy-Werte MUST:

- eigene Profil- und Feldbezeichner besitzen,
- getrennt von RCC-002-Kanonicalwerten gespeichert werden,
- im Manifest als Legacy markiert sein,
- nicht unbemerkt in neue Signale oder Regime eingehen.

Ein Vergleichsdatensatz MAY beide Profile enthalten, wenn jede Spalte eindeutig
zugeordnet ist.

## 25. Bibliotheksunabhängigkeit

### 25.1 Formel ist autoritativ

Keine externe Indikatorbibliothek ist alleinige fachliche Referenz.

Eine Bibliothek MAY verwendet werden, wenn Konformitätstests belegen, dass sie
für:

- Seed,
- Rekursion,
- Fenstergrenzen,
- Nullfälle,
- Warm-up,
- Lückenverhalten

dieselben Ergebnisse wie diese Spezifikation erzeugt.

### 25.2 Versionsbindung

Verwendete Versionen von Python, NumPy, Pandas, PyArrow und optionalen
Indikatorbibliotheken MUST im Manifest dokumentiert und in der
Ausführungsumgebung fixiert werden.

Numerisch oder semantisch wirksame Bibliotheks- und Laufzeitversionen gehören
zum registrierten Umgebungs- und numerischen Determinismusprofil der
`semantic_build_configuration`. Writer-, Kompressions- oder reine
Containerparameter gehören dagegen zur
`physical_publication_configuration`.

## 26. Ausgabevertrag

### 26.1 Pflichtausgaben

S3 erzeugt exakt das logische Schema:

```text
rcc002.stage.s3-indicators/1.0.0
```

Das kanonische Zeilenschema enthält:

- sämtliche S2-Eingabefelder unverändert,
- `indicator_profile_id`,
- `indicator_profile_version`,
- `indicator_schema_id`,
- `indicator_schema_version`,
- `indicator_segment_id`,
- für jedes Feld `x` aus Abschnitt 5 die Gruppe
  `x`, `x_valid`, `x_warmup_complete`, `x_reason_codes`.

Zusätzlich erzeugt die Stufe als getrennte Artefakte oder
Manifestbestandteile:

- den S3-Schema-Fingerprint;
- State Snapshots je abgeschlossener Partition;
- den Indikator-Validierungsbericht.

### 26.2 Keine Zeilenänderung

S3 darf im kanonischen beobachteten Datensatz:

- keine Zeile hinzufügen,
- keine Zeile entfernen,
- keinen OHLCV-Wert verändern.

Es muss gelten:

`S3_rows = S2_rows`

und der kanonische Schlüssel jeder Zeile muss identisch bleiben. Dies
konkretisiert für S3 das kanonische Row-Preservation-Prinzip aus
`RCC_002_DATA_PIPELINE_SPECIFICATION` §5.8.

### 26.3 Spaltenreihenfolge

Die Spaltenreihenfolge lautet:

1. sämtliche S2-Felder in unveränderter S2-Schemareihenfolge;
2. `indicator_profile_id`;
3. `indicator_profile_version`;
4. `indicator_schema_id`;
5. `indicator_schema_version`;
6. `indicator_segment_id`;
7. die Indikatorgruppen in der Allowlist-Reihenfolge aus Abschnitt 5.

Innerhalb jeder Indikatorgruppe lautet die Reihenfolge:

```text
x
x_valid
x_warmup_complete
x_reason_codes
```

### 26.4 Schema-Fingerprint und Kompatibilität

Der S3-Schema-Fingerprint umfasst mindestens:

- geordnete Feldnamen;
- logische Datentypen;
- Nullbarkeit;
- Eigentümerstufe;
- Primärschlüssel;
- Sortierung;
- Schema-ID und Schemaversion;
- Indikator- und Profil-IDs;
- Reason-Code-Register;
- Segmentierungsprofil.

Unbekannte Major-Versionen sind fail-closed abzulehnen.

Nicht registrierte zusätzliche Felder, historische Aliasfelder oder
abweichende Begleitfeldnamen machen das Artefakt nicht kanonisch.

### 26.5 Verbotene S3-Ausgaben

S3 darf keine:

- Signale;
- Regime;
- Long-/Short-Gates;
- Forward Returns;
- Labels;
- Strategieentscheidungen;
- physischen Layoutidentitäten als fachliche Zeilenfelder

erzeugen.

## 27. Testanforderungen

### 27.1 Unit Tests

Für jeden Indikator sind erforderlich:

- minimaler gültiger Input,
- Warm-up unmittelbar vor und am ersten gültigen Index,
- konstante Preisserie,
- streng steigende Serie,
- streng fallende Serie,
- wechselnde Serie,
- Nullvolumenfälle,
- definierte Nullnenner,
- Lücke und State Reset,
- nicht endliche Eingabe,
- Bereichsinvarianten,
- `x_valid`,
- `x_warmup_complete`,
- deterministische `x_reason_codes`,
- logisches `null` bei `x_valid=false`.

### 27.2 Handberechnete Golden Fixtures

Jeder Indikator benötigt mindestens einen kleinen, unabhängig berechneten
Golden Fixture mit:

- Eingangswerten,
- Zwischengrößen,
- erwarteten Ausgabewerten,
- zulässiger Toleranz.

Für RSI und ADX müssen Seed und mindestens zwei Rekursionsschritte enthalten
sein.

### 27.3 Referenzvergleich

SHOULD zusätzlich erfolgen:

- Vergleich gegen mindestens eine unabhängige Implementierung,
- dokumentierte Analyse jeder Abweichung,
- keine Anpassung der kanonischen Formel allein zur Übereinstimmung mit einer
  Bibliothek.

### 27.4 Kausalitätstest

Für jeden Indikator MUST gelten:

Wenn alle Eingaben bis einschließlich `t` unverändert bleiben und ausschließlich
Werte nach `t` verändert werden, darf sich der Indikatorwert bei `t` nicht
ändern.

### 27.5 Partitionsparität

Ein identischer Datensatz wird:

- seriell,
- in Monatspartitionen,
- in künstlich ungleich großen Partitionen

berechnet. Die Ergebnisse müssen innerhalb der definierten Toleranz
übereinstimmen.

### 27.6 Legacy-Golden-Test

Das Legacy-Profil MUST die bekannten historischen Indikator- und Signalwerte
innerhalb der dokumentierten Legacy-Semantik reproduzieren.

### 27.7 Schema- und Segmenttests

Mindestens erforderlich:

- Annahme von `rcc002.stage.s2-validated/1.0.0`;
- Ablehnung unbekannter S2- oder S3-Major-Versionen;
- exakte S3-Spaltenallowlist und Spaltenreihenfolge;
- unveränderte S2-Felder und Primärschlüssel;
- `S3_rows = S2_rows`;
- deterministische `indicator_segment_id`;
- neue Indikatorsegment-ID an jeder `market_segment_id`-Grenze;
- neue Indikatorsegment-ID beim Wechsel von `quality_gate_pass`;
- neue Indikatorsegment-ID nach explizitem State Reset;
- kein gültiger Indikatorwert bei `quality_gate_pass=false`;
- kein Rolling Window über eine Markt- oder Indikatorsegmentgrenze;
- keine Zusammenführung mehrerer `market_segment_id`-Werte;
- Ablehnung historischer Aliasfelder im kanonischen S3-Ausgang;
- exakter State-Snapshot-Vertrag
  `rcc002.state.s3-indicators/1.0.0`.

### 27.8 Property-Based Tests

SHOULD geprüft werden:

- spätere Eingangswerte verändern keinen früheren Indikatorwert;
- zusätzliche physische Partitionierung verändert keine S3-Semantik;
- identische Eingaben und Profile erzeugen identische Segment-IDs;
- jeder gültige Wert ist endlich;
- jeder ungültige Wert ist logisch `null`;
- `x_valid=true` impliziert `x_warmup_complete=true`;
- kein Feld mit einem invalidierenden Reason Code besitzt `x_valid=true`;
- jede `indicator_segment_id` referenziert genau eine
  `market_segment_id`.

## 28. Numerische Toleranzen

Das normative numerische Profil lautet:

```text
indicator_numeric_profile_id=RCC002_FLOAT64_INDICATOR_NUMERICS_V1
indicator_numeric_profile_version=1.0.0
```

### 28.1 Kanonischer Wiederholungsbuild

Bei identischer Umgebung und identischer Serialisierung wird
Checksum-Gleichheit erwartet.

### 28.2 Unabhängiger Implementierungsvergleich

Standardtoleranz für endliche `float64`-Werte:

- `absolute_tolerance = 1e-12`,
- `relative_tolerance = 1e-10`.

Der Vergleich gilt komponentenweise nach:

```text
abs(a - b) <= absolute_tolerance
               + relative_tolerance * max(abs(a), abs(b))
```

Logische Nullwerte werden ausschließlich positionsgleich mit logischen
Nullwerten verglichen. `NaN`, `+Inf` oder `-Inf` gelten nicht als gültige
Vergleichswerte.

Abweichende feldspezifische Toleranzen benötigen:

- dokumentierte Begründung,
- registrierte Feldzuordnung,
- Testabdeckung,
- Freigabe.

### 28.3 Grenzwertentscheidungen

Signal- oder Gate-Entscheidungen an Schwellenwerten dürfen nicht durch
Berichtsrundung erfolgen. Sie verwenden die ungerundeten kanonischen Werte.

### 28.4 Operations- und Determinismusgrenzen

Die Implementierung muss vor `Approved for Implementation` festlegen und
versionieren:

- Reihenfolge nicht assoziativer Float-Operationen;
- zulässige oder deaktivierte FMA-Nutzung;
- Parallelreduktionsregeln;
- Behandlung von Subnormalwerten;
- Null- und Nichtendlichkeitskonvertierung;
- Referenzimplementierung für Golden Fixtures;
- gebundene numerische Bibliotheken und Versionen.

Eine Änderung dieser Regeln verändert mindestens das numerische Profil und
erfordert Determinismus-, Golden- und Partitionsparitätstests.

## 29. Validierungsbericht

Der S3-Bericht enthält mindestens:

- Build- und Profil-ID,
- Eingabe- und Ausgabeschema-ID,
- S2- und S3-Schema-Fingerprint,
- `semantic_build_configuration_sha256`,
- numerisches Profil,
- Segmentierungsprofil,
- Indikatorversionen,
- Zeilenzahl,
- erste und letzte Zeit,
- ersten gültigen Index je Feld und Segment,
- Anzahl gültiger und ungültiger Werte,
- Ungültigkeitsgründe,
- Sonderfallflags,
- Minimal- und Maximalwerte,
- Bereichsverletzungen,
- Segment- und Lückenanzahl,
- Zuordnung jeder `indicator_segment_id` zu genau einer
  `market_segment_id`,
- Anzahl der Wechsel von `quality_gate_pass`,
- State-Snapshot-Prüfungen,
- Partitionsparität,
- Golden-Test-Ergebnisse,
- Output-Checksumme.

## 30. Publication Gate

S3 darf nur veröffentlicht werden, wenn:

1. S2 vollständig kanonisch veröffentlicht ist;
2. jede S2-Eingabezeile einen gültigen und deterministisch berechneten
   booleschen `quality_gate_pass`-Wert besitzt; Zeilen mit
   `quality_gate_pass=false` bleiben im kanonischen Datensatz, erzeugen
   keine gültigen Indikatorwerte, und die Row-Count- und
   Row-Identity-Invarianten bleiben erfüllt;
3. das Eingangsschema exakt
   `rcc002.stage.s2-validated/1.0.0` erfüllt;
4. das Ausgangsschema exakt
   `rcc002.stage.s3-indicators/1.0.0` erfüllt;
5. Eingabe- und Ausgabefingerprints stimmen;
6. alle Profil-, Schema-, Segmentierungs- und Indikatorversionen registriert
   sind;
7. keine Zeile, kein Primärschlüssel und kein S2-Feld verändert wurde;
8. `S3_rows = S2_rows` gilt;
9. für jedes Feld `x` die Begleitfelder vollständig und nicht null sind;
10. `x_valid`, `x_warmup_complete`, `x_reason_codes` und logische Nullwerte
    exakt nach Abschnitt 20 gebildet wurden;
11. keine nicht endlichen gültigen Indikatorwerte bestehen;
12. alle Bereichsinvarianten bestanden sind;
13. jede `indicator_segment_id` genau eine `market_segment_id` referenziert;
14. keine Berechnung eine Markt- oder Indikatorsegmentgrenze überschreitet;
15. State Snapshots das Schema
    `rcc002.state.s3-indicators/1.0.0` erfüllen;
16. Golden-, Schema-, Segment-, Kausalitäts- und Property-Tests bestanden
    sind;
17. serieller und partitionierter Build übereinstimmen;
18. keine historischen Aliasfelder oder nicht registrierten Zusatzfelder
    enthalten sind;
19. Manifest, Berichte und Checksummen vollständig sind.

Der Gate-Status lautet:

- `PASS`,
- `FAIL`,
- `PASS_WITH_APPROVED_EXCEPTIONS`.

`PASS_WITH_APPROVED_EXCEPTIONS` darf ausschließlich nicht blockierende,
vollständig dokumentierte Berichtsbefunde betreffen. Es darf weder ein
ungültiges S2-Feld noch einen regelwidrig gebildeten `x_valid`-Status, einen
Schemafehler, einen Segmentfehler, einen nicht endlichen gültigen Wert oder
eine fehlgeschlagene Reconciliation überstimmen.

Die in diesem Abschnitt aufgeführten Ausnahmefälle für
`PASS_WITH_APPROVED_EXCEPTIONS` sind abschließend. Kein hier nicht
aufgeführter Fall darf unter diesem Gate-Status genehmigt werden, ohne
zuvor eine normative Spezifikationsänderung, eine Versionsanhebung, einen
Review und eine erneute Zertifizierungsbewertung zu durchlaufen. Eine
menschliche Genehmigung allein erweitert nicht den normativen
Ausnahmeumfang.

## 31. Offene Implementierungsparameter

### 31.1 Vor `Approved for Implementation` festzulegen

Folgende semantische oder determinismusrelevante Festlegungen müssen
versioniert vorliegen:

- vollständiges maschinenlesbares S3-Schema;
- vollständiges Indikator- und Reason-Code-Register;
- `indicator_profile_id` und Profilversion;
- Segment-ID-Kanonisierungs- und Hashprofil;
- State-Snapshot-Schema und State-Checksum-Profil;
- numerisches Determinismusprofil einschließlich Operationsreihenfolge;
- gebundene Referenzbibliotheken und Versionen;
- feldbezogene Referenztoleranzen;
- Golden-Fixture-Inhalte und erwartete Resultate;
- Build-Einstiegspunktvertrag;
- Umgebungs- und Lockstrategie;
- Schema-Kompatibilitäts- und Migrationsregeln.

Diese Festlegungen gehören zur `semantic_build_configuration`, soweit sie
fachliche Werte, Validität, Segmentierung, Schema oder Reproduzierbarkeit
beeinflussen.

### 31.2 Während der Implementierung konkretisierbar

Innerhalb vorher festgelegter physischer Profile dürfen konkretisiert werden:

- physische Partitionsgrößen;
- Parquet-Row-Group-Größen;
- Kompressionsstufe;
- Writeroptimierungen;
- Cache- und temporäre Speicherorte;
- Retentionsparameter temporärer State Snapshots.

Diese Parameter gehören zur `physical_publication_configuration`. Sie dürfen
weder Indikatorwerte noch Gültigkeit, Segment-IDs, logisches S3-Schema,
`build_id` oder `dataset_id` verändern.

Jede spätere Änderung mit Wirkung auf fachliche Semantik, logische Schemas,
Identitätsvorabbildungen oder numerische Determinismusregeln muss die
betroffenen Review-Gates erneut durchlaufen.

## 32. Abnahmekriterien

### 32.1 Spezifikationsreife vor Implementierungsfreigabe

Die Spezifikation ist bereit für `Approved for Implementation`, wenn:

1. sämtliche logischen S2-Eingangs- und S3-Ausgangsfelder mit Typ,
   Nullsemantik, Eigentümerstufe und Reihenfolge festgelegt sind;
2. alle Formeln, Seeds, Warm-up-Grenzen und Nullfälle eindeutig sind;
3. alle `x_valid`-, `x_warmup_complete`- und `x_reason_codes`-Regeln
   maschinenlesbar definiert sind;
4. `market_segment_id` und `indicator_segment_id` eindeutig abgegrenzt sind;
5. Segment-, Profil-, Schema-, State- und numerische IDs versioniert sind;
6. semantische und physische Konfiguration getrennt sind;
7. Golden-, Unit-, Property-, Schema-, Segment-, Kausalitäts- und
   Integrationstestverträge vollständig sind;
8. Publication Gate und Manifestverträge vollständig sind;
9. kanonisches und Legacy-Profil strikt getrennt sind;
10. alle vorgeschriebenen internen und externen Review-Gates der
    Spezifikationsbaseline bestanden sind;
11. keine offene Entscheidung fachliche Werte, Gültigkeit, Segmentierung,
    logisches Schema oder Identitätsvorabbildungen verändern kann.

### 32.2 Abnahme der Implementierung

Die spätere Implementierung ist akzeptiert, wenn:

1. alle Golden Fixtures exakt innerhalb der registrierten Toleranzen bestanden
   sind;
2. sämtliche Unit-, Property-, Schema-, Segment-, Kausalitäts- und
   Integrationstests bestanden sind;
3. State Snapshot und Partitionsparität bestanden sind;
4. der BTCUSDT-1m-Vollbuild auf der Workstation bestanden ist;
5. ein unabhängiger Rebuild mindestens semantische Gleichheit erreicht;
6. keine Zeile und kein S2-Feld verändert wurde;
7. Schema-, Zeilen- und Segment-Reconciliation vollständig sind;
8. Manifest und Knowledge Lineage vollständig sind;
9. keine offene kritische Inkonsistenz besteht;
10. das S3-Publication-Gate automatisiert bestanden ist.

## 33. Freigabestatus und nächster Schritt

`RCC-002-SCR-004` bestätigte die dort geprüften wissenschaftlichen
Korrekturen als geschlossen.

Der vollständige Architecture Integrity Review `RCC-002-AIR-001` bewertete
die Spezifikationsfamilie als:

```text
NOT PASSED – ARCHITECTURE CORRECTIONS REQUIRED
```

Version 0.4.0 bewahrt die AIR-001-Korrekturen aus Version 0.3.0 und
korrigiert zusätzlich:

- `SCR-005-M01` – unversionierte `indicator_schema_id` und
  `indicator_state_schema_id`, getrennte Versionen sowie eindeutig
  abgeleitete qualifizierte Schemareferenzen.

Sie aktualisiert außerdem die Abhängigkeiten auf:

```text
RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md
Version 0.7.0

RCC_002_DATA_VALIDATION_2026-07-23.md
Version 0.4.0
```

Die Befunde sind erst geschlossen, wenn alle abhängigen Spezifikationen
konsistent aktualisiert, neu paketiert und erneut geprüft sind.

Der aktuelle Status lautet:

```text
SCR-005-Corrected Draft – Scientific Consistency Re-Review 006 Pending
```

Nächste vorgeschriebene Schritte:

1. übrige abhängige Spezifikationen korrigieren;
2. vollständige interne Qualitätskontrolle;
3. neues vollständiges Spezifikationspaket;
4. fokussierter Scientific Consistency Re-Review;
5. fokussierter Architecture Integrity Re-Review;
6. Editorial Pass;
7. Internal Certification;
8. Claude Independent Architecture Review;
9. Gemini Independent Scientific and Adversarial Audit;
10. ChatGPT Final Consolidation;
11. `Baseline V1 Certified`;
12. Implementierungsfreigabe.

---

# Eingebettetes Dokument 4 von 7

## Quelldatei: `RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md`

# RCC-002 Signal Transformation Specification

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Scientific Software Specification |
| Dokument-ID | RCC-002-ST |
| Titel | Signal Transformation Specification |
| Speicherort im Repository | `docs/specifications/RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md` |
| Dateiname | `RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md` |
| Version | 0.4.2 |
| Datum | 2026-07-23 |
| Status | SCR-005-Corrected Draft – Scientific Consistency Re-Review 006 Pending |
| Übergeordnetes Dokument | `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`, Version 0.7.1 |
| Direkte Abhängigkeiten | `RCC_002_DATA_VALIDATION_2026-07-23.md`, Version 0.4.2; `RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md`, Version 0.4.3 |
| Geltungsbereich | S4_SIGNALS der RCC-002-Datenpipeline |
| Referenziert durch | Regime- und Gate-Spezifikation; Strategieforschung; Backtest; Paper-/Live-Parität |
| Autoritative Sprache | Englische Feldnamen, Profil-IDs und mathematische Regeln sind normativ; deutsche Erläuterungen präzisieren die Semantik |

### Review-Nachweis

| Prüfung | Status | Ergebnis |
|---|---|---|
| Struktur- und Nummerierungsprüfung | Bestanden | Profile, Rollen und Feldgruppen vollständig |
| Vorzeichenprüfung | Bestanden | `+1` durchgängig long-supportive, `-1` durchgängig short-supportive |
| Rollenprüfung | Bestanden | Richtung, Trend, Volatilität und Trendstärke getrennt |
| Grenzwertprüfung | Bestanden | Gleichheit, Nullfälle, Clipping und Ungültigkeit definiert |
| Kausalitätsprüfung | Bestanden | Nur aktuelle und vergangene S3-Werte verwendet |
| Legacy-Trennungsprüfung | Bestanden | Historische Reproduktion überschreibt keine kanonischen Signale |
| Scientific Consistency Review | `RCC-002-SCR-004` bestanden | Die dort geprüften wissenschaftlichen Befunde sind geschlossen; erneuter fokussierter Review nach den semantisch relevanten AIR-001-Korrekturen erforderlich |
| Architecture Integrity Review | `RCC-002-AIR-001` nicht bestanden; Korrektur eingearbeitet | Version 0.3.0 korrigiert die diesem Dokument zugeordneten Teile von `AIR-001-B03`, `AIR-001-M01` und `AIR-001-M03`; dokumentübergreifender Re-Review ausstehend |
| Scientific Consistency Re-Review 005 | `RCC-002-SCR-005` nicht bestanden; Korrektur eingearbeitet | Version 0.4.0 korrigiert `SCR-005-B01` und `SCR-005-M01`; SCR-006 ausstehend |
| Minor Correction Cycle | `RCC-002-SCR-007-MinFV` umgesetzt | Version 0.4.1, 2026-07-27: Minor correction cycle: version, dependency, terminology, checklist and cross-reference consistency corrections. |
| AIR4-MIN-01 Correction | `RCC-002-AIR-004` Minor Finding behoben | Version 0.4.2, 2026-07-27: Clarified that PASS_WITH_APPROVED_EXCEPTIONS carve-outs are exhaustive and cannot be extended by approval alone. |

## 1. Zweck

Dieses Dokument definiert, wie kanonische S3-Indikatoren in standardisierte,
maschinenlesbare S4-Signale und Zustandsmerkmale transformiert werden.

Es löst insbesondere folgende historische Probleme:

- binäre Legacy-Signale bildeten fast ausschließlich bullish Bedingungen ab,
- `0` bedeutete gleichzeitig neutral, bearish oder nicht berechenbar,
- ATR und ADX wurden teilweise wie Richtungssignale behandelt,
- Trendfilter und Entry-Timing waren nicht sauber getrennt,
- dieselben Feldnamen konnten Indikatorlinien und Handelssignale bezeichnen,
- kontinuierliche GS-Scores waren nicht vollständig versioniert erhalten.

S4 erzeugt keine Trades. Es beschreibt ausschließlich die aus Indikatoren
ableitbare Evidenz zum Zeitpunkt `t`.

## 2. Geltungsbereich

### 2.1 Enthalten

S4 umfasst:

- Signalrollen und Vorzeichenkonvention,
- diskrete Richtungssignale,
- kontinuierliche Richtungsscores,
- Trendzustände,
- Volatilitätszustände,
- Trendstärkezustände,
- Validität und Qualitätsflags,
- Legacy-Kompatibilitätsprofile,
- Output- und Testverträge.

### 2.2 Nicht enthalten

Nicht Gegenstand dieses Dokuments sind:

- Kombination mehrerer Signale zu einer Strategie,
- Entry- oder Exit-Regeln,
- Regimeklassifikation,
- Long-/Short-Handelsfreigabe,
- Cooldown oder Loss-Cluster-Gates,
- Positionsgröße,
- Gewinn- oder Verlustlabels.

Insbesondere ist ein positives Signal keine automatische Handelsfreigabe.

## 3. Grundsemantik

### 3.1 Richtungsvorzeichen

Für alle kanonischen diskreten Richtungssignale und kontinuierlichen
Richtungsscores gilt:

- `+1`: unterstützt eine Long-Hypothese,
- `0`: neutral beziehungsweise keine gerichtete Evidenz,
- `-1`: unterstützt eine Short-Hypothese.

Diese Bedeutung darf profilübergreifend nicht invertiert werden.

### 3.2 Ungültigkeit

Ungültigkeit wird im logischen S4-Schema ausschließlich als `null` plus
feldbezogenes Validitätsfeld dargestellt.

Ein internes IEEE-754-`NaN` darf während einer Berechnung vorübergehend
verwendet werden. Vor Schema-Validierung, Fingerprinting oder Veröffentlichung
muss es jedoch in logisches `null` überführt werden. `NaN`, `+Inf` und `-Inf`
sind keine zulässigen gültigen oder veröffentlichten S4-Werte.

Ungültigkeit darf nicht als:

- `0`,
- `-1`,
- `false`

kodiert werden, wenn dadurch Neutralität, Short-Evidenz oder ein schwacher
Zustand vorgetäuscht würde.

### 3.3 Signalrollen

Jedes S4-Feld gehört genau einer Rolle an:

| Rolle | Bedeutung | Zulässiger Wertebereich |
|---|---|---|
| `DIRECTION_DISCRETE` | diskrete Long-/Short-Evidenz | `{-1, 0, +1}` |
| `DIRECTION_SCORE` | kontinuierliche Long-/Short-Evidenz | `[-1, +1]` |
| `TREND_STATE` | Richtung eines Preis-/Trendverhältnisses | `{-1, 0, +1}` oder `[-1,+1]` |
| `VOLATILITY_STATE` | relative Volatilität ohne Handelsrichtung | `{-1,0,+1}` oder `[-1,+1]` |
| `TREND_STRENGTH` | richtungslose Trendstärke | `[0,1]` |
| `VALIDITY` | fachliche Berechenbarkeit | Boolean/Reason Code |

`VOLATILITY_STATE` und `TREND_STRENGTH` dürfen nicht ohne eine separat
spezifizierte Regel als Long- oder Short-Stimme summiert werden.

## 4. Profile

### 4.1 Kanonisches Gesamtprofil

Die erste kanonische S4-Baseline lautet:

```text
signal_profile_id=RCC002_CANONICAL_SIGNALS_V1
signal_profile_version=1.0.0
signal_schema_id=rcc002.stage.s4-signals
signal_schema_version=1.0.0
signal_schema_ref=rcc002.stage.s4-signals/1.0.0
```

`signal_schema_id` ist unversioniert. `signal_schema_ref` wird ausschließlich
als `<signal_schema_id>/<signal_schema_version>` abgeleitet.

Das Gesamtprofil erzeugt gemeinsam und atomar:

- die diskreten Felder aus `RCC_DISCRETE_V1`;
- die kontinuierlichen Felder aus `RCC_CONTINUOUS_V1`;
- für jedes erzeugte Feld die zugehörigen Begleitfelder;
- die fünf verbindlichen Profil- und Schemametadaten.

Ein kanonischer S4-Build darf nicht nur eine nicht ausgewiesene Teilmenge
dieses Gesamtprofils unter derselben Schema-ID veröffentlichen.

### 4.2 `RCC_DISCRETE_V1`

Erzeugt:

- diskrete Mean-Reversion-Signale,
- diskrete Momentum-/Volumen-Signale,
- diskrete Trendzustände,
- diskrete Volatilitäts- und Trendstärkezustände.

### 4.3 `RCC_CONTINUOUS_V1`

Erzeugt dimensionslose kontinuierliche Scores mit festen, versionierten
Transformationen.

Diese Scores sind Forschungsfeatures. Ihre Definition genehmigt weder ihre
Gewichtung noch ihre Verwendung in einer Strategie.

### 4.4 `LEGACY_BTC_BINARY_V1`

Reproduziert die zwölf historisch verifizierten 0/1-Signalspalten.

Das Profil ist ausschließlich für:

- Reproduktion,
- Vergleich,
- Knowledge Lineage

zulässig.

Das Legacy-Profil gehört nicht zum kanonischen S4-Ausgangsschema. Es wird als
separates Vergleichsartefakt mit eigener Schema-ID veröffentlicht:

```text
rcc002.comparison.s4-legacy-btc-binary/1.0.0
```

### 4.5 Profilkombination

Ein Build MAY mehrere Profile parallel berechnen, wenn:

- Feldnamen eindeutig sind,
- jede Spalte eine Profil-ID trägt oder über das Schema zugeordnet ist,
- kein Profil ein anderes überschreibt,
- das Manifest alle aktiven Profile aufführt;
- kanonische S4-Ausgabe und Legacy-Vergleichsartefakt getrennte
  Schema- und Artefaktidentitäten besitzen.

Das kanonische S4-Artefakt enthält ausschließlich das kanonische
Gesamtprofil. Ein Legacy-Artefakt darf nicht unter
`rcc002.stage.s4-signals/1.0.0` veröffentlicht werden.

Diskrete und kontinuierliche Profile sind parallele Repräsentationen. Ein
diskretes Feld darf nicht nachträglich aus dem Vorzeichen seines
kontinuierlichen Gegenstücks abgeleitet werden. Insbesondere können strikte
diskrete Grenzwerte an einem exakten Schwellenwert neutral sein, während der
kontinuierliche Score dort bereits einen definierten Ankerwert erreicht.

## 5. Eingabevertrag

### 5.1 Akzeptiertes Eingangsschema

S4 akzeptiert für die erste Baseline ausschließlich:

```text
rcc002.stage.s3-indicators/1.0.0
```

Eine unbekannte Major-Version wird fail-closed abgelehnt. Eine neuere
Minor-Version darf nur aufgrund einer registrierten S4-Kompatibilitätsregel
akzeptiert werden.

### 5.2 Pflichtfelder aus S3

S4 verwendet:

- `market_type`;
- `symbol`;
- `interval`;
- `open_time`;
- `market_segment_id`;
- `indicator_segment_id`;
- `quality_gate_pass`;
- `close`;
- `volume`;
- `sma_close_200`;
- `ema_close_50`;
- `rsi_wilder_14`;
- `macd_hist_12_26_9`;
- `bb_mid_20`;
- `bb_upper_20_2`;
- `bb_lower_20_2`;
- `stoch_k_14`;
- `atr_wilder_14`;
- `roc_close_12_pct`;
- `obv`;
- `cci_20`;
- `mfi_14`;
- `adx_wilder_14`;
- zu jedem verwendeten Indikator `x` die S3-Begleitfelder
  `x_valid`, `x_warmup_complete` und `x_reason_codes`.

Zusätzlich berechnet S4 kausal:

- SMA 200 des gültigen ATR innerhalb desselben Segments,
- SMA 50 des gültigen OBV innerhalb desselben Segments,
- Summe des Volumens über 50 gültige Kerzen.

Diese S4-Hilfsgrößen sind Teil des Signalprofils und keine nachträgliche
Änderung der S3-Indikatorformeln.

### 5.3 Eingabeinvarianten

S4 MUST:

- ausschließlich freigegebene S3-Artefakte konsumieren,
- `signal_profile_id` aus der semantischen Buildkonfiguration bestimmen,
- S3-Schema-, Indikatorprofil-, Segmentprofil- und numerische Profilversion
  prüfen,
- den kanonischen Schlüssel unverändert erhalten,
- die Sortierung `(market_type, symbol, interval, open_time)` unverändert
  erhalten,
- `market_segment_id` und `indicator_segment_id` unverändert durchreichen,
- Segmentgrenzen respektieren,
- keine ungültigen S3-Werte transformieren,
- `quality_gate_pass=false` als blockierenden Eingangsstatus behandeln.

S4 darf keine neue Markt- oder Indikatorsegment-ID erzeugen. Ein zusätzlicher
Rolling-Warm-up in S4 verändert weder `market_segment_id` noch
`indicator_segment_id`; er wirkt ausschließlich auf die feldbezogene
S4-Gültigkeit.

### 5.4 Primärschlüssel und Zeilenreihenfolge

Der logische Primärschlüssel bleibt:

```text
(market_type, symbol, interval, open_time)
```

Die kanonische Sortierung bleibt:

```text
market_type ASC, symbol ASC, interval ASC, open_time ASC
```

Wenn S3 noch nicht konsolidierte Multi-Provider-Daten enthält, MUSS
`provider` als zusätzlicher registrierter Schlüsselbestandteil unmittelbar
vor `market_type` geführt werden. Nach dokumentierter Providerkonsolidierung
entfällt `provider` aus dem Schlüssel, bleibt aber als Provenienzfeld erhalten.

`timeframe` ist kein Aliasfeld des kanonischen S4-Schemas. Ein historischer
Eingang mit `timeframe` MUSS vor S3 durch ein versioniertes Migrationsprofil
nach `interval` überführt werden; S4 selbst darf keine stille Umbenennung
vornehmen.

Duplikate, Schlüsseländerungen oder eine Änderung der semantischen
Zeilenreihenfolge sind blockierende Fehler.

### 5.5 Eingangsablehnung

S4 bricht vor einer fachlichen Transformation ab, wenn mindestens eine der
folgenden Bedingungen erfüllt ist:

- inkompatible oder unbekannte S3-Schema-ID;
- fehlendes Pflichtfeld;
- nicht registrierter Datentyp oder nicht registrierte Nullbarkeit;
- ungültiger Primärschlüssel;
- nichtkanonische Sortierung;
- fehlende S3-Profilmetadaten;
- unbekannte Reason-Code-Registry;
- widersprüchliche S3-Begleitfelder;
- nicht veröffentlichter oder nicht bestandener S3-Publication-Status.

## 6. Gemeinsame Funktionen

### 6.1 Clipping

`clip(x, a, b) = min(max(x, a), b)`

### 6.2 Vorzeichenfunktion

`sign3(x)`:

- `+1`, wenn `x > 0`,
- `0`, wenn `x = 0`,
- `-1`, wenn `x < 0`.

Float-Gleichheit wird auf dem ungerundeten kanonischen Wert geprüft.

### 6.3 Sichere Division

Eine kontinuierliche Transformation mit Nenner `d` ist regulär gültig, wenn:

`d > 0`

Definierte Nullfälle werden im jeweiligen Abschnitt geregelt. Es darf kein
willkürliches globales Epsilon in die fachliche Formel eingefügt werden.

### 6.4 Vollständige Rolling Windows

S4-Rolling-Hilfsgrößen verwenden:

- ausschließlich dasselbe `indicator_segment_id`,
- vollständige Fenster,
- `min_periods = window`,
- ausschließlich Werte mit `quality_gate_pass=true`,
- ausschließlich erforderliche Eingaben mit `x_valid=true`,
- keine synthetischen oder ungültigen Inputs im kanonischen Profil.

Ein Fenster darf weder eine `market_segment_id`- noch eine
`indicator_segment_id`-Grenze überschreiten.

### 6.5 Auswertungsreihenfolge

Für jedes S4-Feld gilt:

1. Schema- und Profilverträglichkeit prüfen;
2. erforderliche S3-Begleitfelder prüfen;
3. zusätzlichen S4-Warm-up prüfen;
4. Sonder- und Nullnennerfall prüfen;
5. ungerundete Transformation berechnen;
6. gegebenenfalls clippen;
7. Endlichkeit und Wertebereich prüfen;
8. Wert, `y_valid` und `y_reason_codes` gemeinsam serialisieren.

Eine spätere Prüfung darf einen zuvor festgestellten invalidierenden Grund
nicht verdecken.

## 7. Feldregister

### 7.1 Diskrete Richtungssignale

| Feld | Rolle | Quelle |
|---|---|---|
| `sig_rsi_mr_d` | `DIRECTION_DISCRETE` | RSI 14 |
| `sig_macd_momentum_d` | `DIRECTION_DISCRETE` | MACD-Histogramm |
| `sig_bollinger_mr_d` | `DIRECTION_DISCRETE` | Bollinger Bands |
| `sig_stoch_mr_d` | `DIRECTION_DISCRETE` | Stochastic %K |
| `sig_cci_mr_d` | `DIRECTION_DISCRETE` | CCI |
| `sig_mfi_mr_d` | `DIRECTION_DISCRETE` | MFI |
| `sig_obv_momentum_d` | `DIRECTION_DISCRETE` | OBV relativ zu SMA 50 |
| `sig_roc_momentum_d` | `DIRECTION_DISCRETE` | ROC 12 |

### 7.2 Diskrete Zustände

| Feld | Rolle | Quelle |
|---|---|---|
| `state_ma200_trend_d` | `TREND_STATE` | Close relativ zu SMA 200 |
| `state_ema50_trend_d` | `TREND_STATE` | Close relativ zu EMA 50 |
| `state_atr_relative_d` | `VOLATILITY_STATE` | ATR 14 relativ zu ATR-SMA 200 |
| `state_adx_strength_d` | `TREND_STRENGTH` | ADX 14 relativ zu 25 |

### 7.3 Kontinuierliche Felder

| Feld | Rolle |
|---|---|
| `score_rsi_mr_c` | `DIRECTION_SCORE` |
| `score_macd_momentum_c` | `DIRECTION_SCORE` |
| `score_bollinger_mr_c` | `DIRECTION_SCORE` |
| `score_stoch_mr_c` | `DIRECTION_SCORE` |
| `score_cci_mr_c` | `DIRECTION_SCORE` |
| `score_mfi_mr_c` | `DIRECTION_SCORE` |
| `score_obv_momentum_c` | `DIRECTION_SCORE` |
| `score_roc_momentum_c` | `DIRECTION_SCORE` |
| `score_ma200_trend_c` | `TREND_STATE` |
| `score_ema50_trend_c` | `TREND_STATE` |
| `score_atr_relative_c` | `VOLATILITY_STATE` |
| `score_adx_strength_c` | `TREND_STRENGTH` |

Suffixe:

- `_d`: diskret,
- `_c`: kontinuierlich.

### 7.4 Kanonische S4-Feld- und Begleitfeld-Allowlist

Das kanonische S4-Ausgangsschema enthält alle S3-Felder unverändert und genau
die in diesem Abschnitt registrierten S4-Felder.

Für jedes der folgenden 24 Basisfelder `y` erzeugt S4 genau:

```text
y
y_valid
y_reason_codes
```

#### 7.4.1 Diskrete Basisfelder

| Feld | Logischer Typ | Nullbar | Rolle | Eigentümer |
|---|---|---:|---|---|
| `sig_rsi_mr_d` | `Int8` | ja | `DIRECTION_DISCRETE` | `S4_SIGNALS` |
| `sig_macd_momentum_d` | `Int8` | ja | `DIRECTION_DISCRETE` | `S4_SIGNALS` |
| `sig_bollinger_mr_d` | `Int8` | ja | `DIRECTION_DISCRETE` | `S4_SIGNALS` |
| `sig_stoch_mr_d` | `Int8` | ja | `DIRECTION_DISCRETE` | `S4_SIGNALS` |
| `sig_cci_mr_d` | `Int8` | ja | `DIRECTION_DISCRETE` | `S4_SIGNALS` |
| `sig_mfi_mr_d` | `Int8` | ja | `DIRECTION_DISCRETE` | `S4_SIGNALS` |
| `sig_obv_momentum_d` | `Int8` | ja | `DIRECTION_DISCRETE` | `S4_SIGNALS` |
| `sig_roc_momentum_d` | `Int8` | ja | `DIRECTION_DISCRETE` | `S4_SIGNALS` |
| `state_ma200_trend_d` | `Int8` | ja | `TREND_STATE` | `S4_SIGNALS` |
| `state_ema50_trend_d` | `Int8` | ja | `TREND_STATE` | `S4_SIGNALS` |
| `state_atr_relative_d` | `Int8` | ja | `VOLATILITY_STATE` | `S4_SIGNALS` |
| `state_adx_strength_d` | `Int8` | ja | `TREND_STRENGTH` | `S4_SIGNALS` |

`state_adx_strength_d` verwendet trotz seines `Int8`-Typs ausschließlich
`{0,1}`. Alle übrigen diskreten Felder verwenden ausschließlich
`{-1,0,+1}`.

#### 7.4.2 Kontinuierliche Basisfelder

| Feld | Logischer Typ | Nullbar | Rolle | Eigentümer |
|---|---|---:|---|---|
| `score_rsi_mr_c` | `Float64` | ja | `DIRECTION_SCORE` | `S4_SIGNALS` |
| `score_macd_momentum_c` | `Float64` | ja | `DIRECTION_SCORE` | `S4_SIGNALS` |
| `score_bollinger_mr_c` | `Float64` | ja | `DIRECTION_SCORE` | `S4_SIGNALS` |
| `score_stoch_mr_c` | `Float64` | ja | `DIRECTION_SCORE` | `S4_SIGNALS` |
| `score_cci_mr_c` | `Float64` | ja | `DIRECTION_SCORE` | `S4_SIGNALS` |
| `score_mfi_mr_c` | `Float64` | ja | `DIRECTION_SCORE` | `S4_SIGNALS` |
| `score_obv_momentum_c` | `Float64` | ja | `DIRECTION_SCORE` | `S4_SIGNALS` |
| `score_roc_momentum_c` | `Float64` | ja | `DIRECTION_SCORE` | `S4_SIGNALS` |
| `score_ma200_trend_c` | `Float64` | ja | `TREND_STATE` | `S4_SIGNALS` |
| `score_ema50_trend_c` | `Float64` | ja | `TREND_STATE` | `S4_SIGNALS` |
| `score_atr_relative_c` | `Float64` | ja | `VOLATILITY_STATE` | `S4_SIGNALS` |
| `score_adx_strength_c` | `Float64` | ja | `TREND_STRENGTH` | `S4_SIGNALS` |

#### 7.4.3 Begleitfelder

Für jedes registrierte Basisfeld `y` gilt:

| Feldmuster | Logischer Typ | Nullbar | Eigentümer | Semantik |
|---|---|---:|---|---|
| `y_valid` | `Boolean` | nein | `S4_SIGNALS` | fachliche Verwendbarkeit von `y` |
| `y_reason_codes` | geordnete Liste `Utf8` | nein | `S4_SIGNALS` | deterministische Gründe und Hinweise |

Eine leere Reason-Code-Liste wird als leere Liste, nicht als `null`,
serialisiert.

### 7.5 S4-Metadaten

S4 erzeugt einmal je Zeile folgende nicht nullbaren Metadaten:

| Feld | Logischer Typ | Normativer Wert |
|---|---|---|
| `signal_profile_id` | `Utf8` | `RCC002_CANONICAL_SIGNALS_V1` |
| `signal_profile_version` | `Utf8` | `1.0.0` |
| `signal_schema_id` | `Utf8` | `rcc002.stage.s4-signals` |
| `signal_schema_version` | `Utf8` | `1.0.0` |
| `signal_schema_ref` | `Utf8` | `rcc002.stage.s4-signals/1.0.0` |

Der vollständig qualifizierte Ausgangsschemabezeichner lautet:

```text
rcc002.stage.s4-signals/1.0.0
```

### 7.6 Kanonische Feldreihenfolge

Die kanonische Reihenfolge lautet:

1. alle Felder von `rcc002.stage.s3-indicators/1.0.0` in unveränderter
   S3-Reihenfolge;
2. `signal_profile_id`;
3. `signal_profile_version`;
4. `signal_schema_id`;
5. `signal_schema_version`;
6. die 24 Basisfelder in der Reihenfolge aus den Abschnitten 7.4.1 und 7.4.2;
7. unmittelbar nach jedem Basisfeld `y` die Felder `y_valid` und
   `y_reason_codes`.

Nicht registrierte Zusatzfelder, Legacy-Felder oder alternative
Begleitfeldnamen machen das Artefakt nicht kanonisch.

### 7.7 Schema-Fingerprint

Der S4-Schema-Fingerprint umfasst mindestens:

- geordnete Feldnamen;
- logische Datentypen;
- Nullbarkeit;
- Feldrollen;
- Eigentümerstufen;
- Primärschlüssel und Sortierung;
- Schema-ID und Schemaversion;
- Profil-ID und Profilversion;
- Reason-Code-Register und dessen Version;
- Wertebereiche und Nullsemantik;
- Kompatibilitätsregeln.

### 7.8 Kompatibilitäts- und Migrationsregeln

Für `rcc002.stage.s4-signals` gilt semantische Versionierung:

- Patch: ausschließlich redaktionelle oder nichtsemantische Metadatenkorrektur;
- Minor: additive optionale Felder ohne Änderung bestehender Semantik;
- Major: Entfernung, Umbenennung, Typänderung, Rollenänderung, neue
  Nullsemantik, Schlüsseländerung oder fachliche Bedeutungsänderung.

Eine neue Minor-Version wird nur akzeptiert, wenn der Konsument sie in einer
registrierten Kompatibilitätsregel freigibt. Unbekannte Major-Versionen sind
fail-closed abzulehnen.

Historische Namen wie `rsi_signal`, `macd_signal`, `atr_signal` oder
`adx_signal` sind keine kanonischen Aliase. Ihre Semantik ist
profilabhängig und darf nicht durch bloße Umbenennung migriert werden.

### 7.9 Verbotene S4-Ausgaben

S4 darf insbesondere keine der folgenden fachlichen Ausgaben erzeugen:

- `market_regime`;
- `regime_state`;
- `regime_raw_state`;
- `regime_persisted_state`;
- `allow_long`;
- `allow_short`;
- `data_gate_pass`;
- `gate_state`;
- `gate_valid`;
- Forward Returns;
- Labels;
- Strategieentscheidungen.

Regime entstehen ausschließlich in S5, Handels-Gates ausschließlich in S6
und Zukunftsinformation ausschließlich in S7. Damit bleibt der korrigierte
S5-/S6-Vertrag aus `AIR-001-B03` frei von konkurrierenden S4-Ausgaben.

## 8. RSI-Transformation

### 8.1 Diskret

Für gültigen `rsi_wilder_14_t`:

- wenn RSI `< 30`: `sig_rsi_mr_d = +1`,
- wenn RSI `> 70`: `sig_rsi_mr_d = -1`,
- andernfalls: `sig_rsi_mr_d = 0`.

Bei exakt 30 oder 70 ist das Signal neutral.

### 8.2 Kontinuierlich

`score_rsi_mr_c = clip((50 - rsi_wilder_14) / 20, -1, +1)`

Damit gilt:

- RSI 30 oder niedriger: maximal long-supportive,
- RSI 50: neutral,
- RSI 70 oder höher: maximal short-supportive.

## 9. MACD-Transformation

### 9.1 Diskret

`sig_macd_momentum_d = sign3(macd_hist_12_26_9)`

Damit:

- positives Histogramm: `+1`,
- negatives Histogramm: `-1`,
- exakt null: `0`.

### 9.2 Kontinuierlich

Wenn `atr_wilder_14 > 0`:

`score_macd_momentum_c = clip(macd_hist_12_26_9 / atr_wilder_14, -1, +1)`

Die ATR-Normalisierung macht das Histogramm dimensionslos und reduziert reine
Preisniveaueffekte.

Wenn ATR `= 0`:

- MACD-Histogramm `= 0`: Score `= 0`,
- MACD-Histogramm `!= 0`: ungültig mit
  `SIG_MACD_ZERO_ATR_CONFLICT`.

## 10. Bollinger-Transformation

### 10.1 Diskret

- Wenn `close < bb_lower_20_2`: `sig_bollinger_mr_d = +1`.
- Wenn `close > bb_upper_20_2`: `sig_bollinger_mr_d = -1`.
- Andernfalls: `sig_bollinger_mr_d = 0`.

Bei exakter Berührung eines Bandes ist das Signal neutral.

### 10.2 Kontinuierlich

Definiere:

`half_band_width = bb_upper_20_2 - bb_mid_20`

Wenn `half_band_width > 0`:

`score_bollinger_mr_c = clip((bb_mid_20 - close) / half_band_width, -1, +1)`

Damit:

- unteres Band: `+1`,
- Mittellinie: `0`,
- oberes Band: `-1`.

Wenn `half_band_width = 0`:

- `close = bb_mid_20`: Score `= 0`,
- andernfalls: ungültig mit `SIG_BB_ZERO_WIDTH_CONFLICT`.

## 11. Stochastic-Transformation

### 11.1 Diskret

- Wenn `stoch_k_14 < 20`: `sig_stoch_mr_d = +1`.
- Wenn `stoch_k_14 > 80`: `sig_stoch_mr_d = -1`.
- Andernfalls: `sig_stoch_mr_d = 0`.

Bei exakt 20 oder 80 ist das Signal neutral.

### 11.2 Kontinuierlich

`score_stoch_mr_c = clip((50 - stoch_k_14) / 30, -1, +1)`

Stochastic 20 entspricht `+1`, 50 entspricht `0`, 80 entspricht `-1`.

## 12. CCI-Transformation

### 12.1 Diskret

- Wenn `cci_20 < -100`: `sig_cci_mr_d = +1`.
- Wenn `cci_20 > +100`: `sig_cci_mr_d = -1`.
- Andernfalls: `sig_cci_mr_d = 0`.

Bei exakt `-100` oder `+100` ist das Signal neutral.

### 12.2 Kontinuierlich

`score_cci_mr_c = clip(-cci_20 / 100, -1, +1)`

CCI `-100` entspricht `+1`; CCI `+100` entspricht `-1`.

## 13. MFI-Transformation

### 13.1 Diskret

- Wenn `mfi_14 < 20`: `sig_mfi_mr_d = +1`.
- Wenn `mfi_14 > 80`: `sig_mfi_mr_d = -1`.
- Andernfalls: `sig_mfi_mr_d = 0`.

Bei exakt 20 oder 80 ist das Signal neutral.

### 13.2 Kontinuierlich

`score_mfi_mr_c = clip((50 - mfi_14) / 30, -1, +1)`

MFI 20 entspricht `+1`, 50 entspricht `0`, 80 entspricht `-1`.

## 14. OBV-Transformation

### 14.1 Hilfsgrößen

Innerhalb desselben Segments:

`obv_sma_50_t = mean(obv_i, i=t-49...t)`

`volume_sum_50_t = sum(volume_i, i=t-49...t)`

### 14.2 Diskret

`sig_obv_momentum_d = sign3(obv - obv_sma_50)`

### 14.3 Kontinuierlich

Wenn `volume_sum_50 > 0`:

`score_obv_momentum_c = clip((obv - obv_sma_50) / volume_sum_50, -1, +1)`

Wenn `volume_sum_50 = 0`:

- `obv = obv_sma_50`: Score `= 0`,
- andernfalls: ungültig mit `SIG_OBV_ZERO_VOLUME_CONFLICT`.

### 14.4 Gültigkeit

Beide OBV-Transformationen benötigen 50 gültige OBV- und Volumenwerte
innerhalb desselben Segments.

## 15. ROC-Transformation

### 15.1 Diskret

`sig_roc_momentum_d = sign3(roc_close_12_pct)`

### 15.2 Kontinuierlich

Definiere die aktuelle ATR-Quote:

`atr_fraction_t = atr_wilder_14_t / close_t`

und den ROC als Dezimalreturn:

`roc_fraction_t = roc_close_12_pct_t / 100`

Wenn `atr_fraction_t > 0`:

`score_roc_momentum_c = clip(roc_fraction_t / atr_fraction_t, -1, +1)`

Wenn `atr_fraction_t = 0`:

- ROC `= 0`: Score `= 0`,
- ROC `!= 0`: ungültig mit `SIG_ROC_ZERO_ATR_CONFLICT`.

## 16. MA200-Trendzustand

### 16.1 Diskret

`state_ma200_trend_d = sign3(close - sma_close_200)`

### 16.2 Kontinuierlich

Wenn `atr_wilder_14 > 0`:

`score_ma200_trend_c = clip((close - sma_close_200) / atr_wilder_14, -1, +1)`

Wenn ATR `= 0`:

- `close = sma_close_200`: Score `= 0`,
- andernfalls: ungültig mit `SIG_MA200_ZERO_ATR_CONFLICT`.

### 16.3 Rolle

Dieses Feld ist ein Trendzustand, kein Entry-Timing-Signal.

## 17. EMA50-Trendzustand

### 17.1 Diskret

`state_ema50_trend_d = sign3(close - ema_close_50)`

### 17.2 Kontinuierlich

Wenn `atr_wilder_14 > 0`:

`score_ema50_trend_c = clip((close - ema_close_50) / atr_wilder_14, -1, +1)`

Wenn ATR `= 0`:

- `close = ema_close_50`: Score `= 0`,
- andernfalls: ungültig mit `SIG_EMA50_ZERO_ATR_CONFLICT`.

### 17.3 Rolle

Dieses Feld ist ein Trendzustand, kein Entry-Timing-Signal.

## 18. ATR-Volatilitätszustand

### 18.1 Hilfsgröße

Innerhalb desselben Segments:

`atr_sma_200_t = mean(atr_wilder_14_i, i=t-199...t)`

### 18.2 Diskret

`state_atr_relative_d = sign3(atr_wilder_14 - atr_sma_200)`

Damit:

- `+1`: ATR oberhalb des 200er-ATR-Mittels,
- `0`: exakt gleich,
- `-1`: ATR unterhalb des Mittels.

Das Vorzeichen beschreibt hohe oder niedrige relative Volatilität, nicht
Long- oder Short-Richtung.

### 18.3 Kontinuierlich

Wenn `atr_wilder_14 > 0` und `atr_sma_200 > 0`:

`score_atr_relative_c = clip(log(atr_wilder_14 / atr_sma_200) / log(2), -1, +1)`

Interpretation:

- ATR doppelt so hoch wie Referenz oder höher: `+1`,
- identische ATR: `0`,
- ATR halb so hoch wie Referenz oder niedriger: `-1`.

Wenn beide Werte null sind:

`score_atr_relative_c = 0`

Wenn `atr_wilder_14 = 0` und `atr_sma_200 > 0`:

`score_atr_relative_c = -1`

Wenn `atr_wilder_14 > 0` und `atr_sma_200 = 0`, ist der Zustand mit
`SIG_ATR_RATIO_ZERO_CONFLICT` ungültig. Dieser Fall verletzt bei einem
vollständigen nichtnegativen 200er-Fenster zugleich eine
Berechnungskonsistenzannahme und muss untersucht werden.

### 18.4 Gültigkeit

Der Zustand benötigt 200 gültige ATR-Werte innerhalb desselben Segments.

## 19. ADX-Trendstärkezustand

### 19.1 Diskret

- Wenn `adx_wilder_14 > 25`: `state_adx_strength_d = 1`.
- Wenn `adx_wilder_14 <= 25`: `state_adx_strength_d = 0`.

Dieses Feld besitzt kein negatives Richtungsvorzeichen.

### 19.2 Kontinuierlich

`score_adx_strength_c = clip((adx_wilder_14 - 15) / 10, 0, 1)`

Damit:

- ADX `<= 15`: `0`,
- ADX `= 20`: `0.5`,
- ADX `>= 25`: `1`.

### 19.3 Rolle

ADX beschreibt Trendstärke. Die Trendrichtung stammt nicht aus ADX, sondern
aus getrennten Trend- oder Regimefeldern.

## 20. Diskrete Regelmatrix

| Feld | `+1` | `0` | `-1` |
|---|---|---|---|
| `sig_rsi_mr_d` | RSI `<30` | RSI `30...70` | RSI `>70` |
| `sig_macd_momentum_d` | Hist `>0` | Hist `=0` | Hist `<0` |
| `sig_bollinger_mr_d` | Close `< lower` | innerhalb inkl. Bänder | Close `> upper` |
| `sig_stoch_mr_d` | %K `<20` | `%K 20...80` | %K `>80` |
| `sig_cci_mr_d` | CCI `<-100` | CCI `-100...100` | CCI `>100` |
| `sig_mfi_mr_d` | MFI `<20` | MFI `20...80` | MFI `>80` |
| `sig_obv_momentum_d` | OBV `> SMA50` | gleich | OBV `< SMA50` |
| `sig_roc_momentum_d` | ROC `>0` | ROC `=0` | ROC `<0` |
| `state_ma200_trend_d` | Close `> SMA200` | gleich | Close `< SMA200` |
| `state_ema50_trend_d` | Close `> EMA50` | gleich | Close `< EMA50` |
| `state_atr_relative_d` | ATR `> ATR-SMA200` | gleich | ATR `< ATR-SMA200` |

`state_adx_strength_d` verwendet ausschließlich `{0,1}`.

## 21. Kontinuierliche Score-Invarianten

MUST gelten:

- alle `DIRECTION_SCORE`-Felder liegen in `[-1,+1]`,
- Trend-Scores liegen in `[-1,+1]`,
- `score_atr_relative_c` liegt in `[-1,+1]`,
- `score_adx_strength_c` liegt in `[0,1]`,
- kein gültiger Score ist `NaN` oder unendlich,
- Clipping wird nach der vollständigen ungerundeten Transformation angewandt.

Clipping darf nicht als Ersatz für einen ungültigen Nenner verwendet werden.

## 22. Warm-up und erste Verfügbarkeit

| Transformation | Zusätzlicher S4-Warm-up |
|---|---:|
| RSI diskret/kontinuierlich | keiner nach gültigem RSI |
| MACD diskret | keiner nach gültigem Histogramm |
| MACD kontinuierlich | gültiges Histogramm und ATR |
| Bollinger diskret/kontinuierlich | keiner nach gültigen Bollinger-Feldern |
| Stochastic diskret/kontinuierlich | keiner nach gültigem %K |
| CCI diskret/kontinuierlich | keiner nach gültigem CCI |
| MFI diskret/kontinuierlich | keiner nach gültigem MFI |
| OBV diskret/kontinuierlich | 50 gültige OBV-/Volumenwerte |
| ROC diskret | keiner nach gültigem ROC |
| ROC kontinuierlich | gültiger ROC und ATR |
| MA200 diskret | gültiger SMA200 |
| MA200 kontinuierlich | gültiger SMA200 und ATR |
| EMA50 diskret | gültiger EMA50 |
| EMA50 kontinuierlich | gültiger EMA50 und ATR |
| ATR relativ | 200 gültige ATR-Werte |
| ADX Stärke | keiner nach gültigem ADX |

Nach einer Segmentgrenze beginnt jeder zusätzliche Rolling-Warm-up erneut.

## 23. Validität und Reason Codes

### 23.1 Verbindliches Validitätsprofil

Das Validitätsprofil lautet:

```text
signal_validity_profile_id=RCC002_SIGNAL_VALIDITY_V1
signal_validity_profile_version=1.0.0
signal_reason_code_registry_version=1.0.0
```

### 23.2 Wahrheitsregel

Für jedes Basisfeld `y` gilt:

```text
y_valid =
    schema_compatible
    AND profile_compatible
    AND quality_gate_pass
    AND all_required_s3_inputs_valid
    AND additional_s4_warmup_complete
    AND denominator_or_defined_null_case_valid
    AND result_is_finite
    AND result_in_registered_range
```

Wenn `y_valid=false`, muss `y=null` sein.

Wenn `y_valid=true`, muss:

- `y` nicht null;
- `y` endlich;
- `y` im registrierten Wertebereich;
- `y_reason_codes` frei von invalidierenden Codes

sein.

Ein definierter mathematischer Nullfall mit explizitem gültigem Ergebnis, etwa
MACD-Histogramm null bei ATR null, ist gültig und erhält den jeweils
definierten Wert. Ein nicht definierter oder widersprüchlicher Nullfall ist
ungültig.

### 23.3 Pflichtfelder

S4 MUST je Transformation ausweisen:

- `y`;
- `y_valid`;
- `y_reason_codes`;
- Profil-ID und Profilversion über die verbindlichen S4-Metadaten;
- Signalrolle über das versionierte Feldregister.

### 23.4 Verbindliches Reason-Code-Register

| Priorität | Code | Invalidierend | Bedeutung |
|---:|---|---:|---|
| 10 | `SIG_SCHEMA_MISMATCH` | ja | S3- oder S4-Schema inkompatibel |
| 20 | `SIG_PROFILE_MISMATCH` | ja | Profil-ID oder Profilversion inkompatibel |
| 30 | `SIG_INPUT_QUALITY_GATE_FAILED` | ja | `quality_gate_pass=false` |
| 40 | `SIG_INPUT_INVALID` | ja | mindestens ein erforderliches S3-Feld ungültig |
| 50 | `SIG_WARMUP_INCOMPLETE` | ja | zusätzliches S4-Fenster unvollständig |
| 60 | `SIG_WINDOW_CROSSES_INDICATOR_SEGMENT` | ja | Fenster würde eine Segmentgrenze überschreiten |
| 70 | `SIG_MACD_ZERO_ATR_CONFLICT` | ja | MACD ungleich null bei ATR null |
| 80 | `SIG_BB_ZERO_WIDTH_CONFLICT` | ja | Close weicht bei Bandbreite null von BB-Mid ab |
| 90 | `SIG_OBV_ZERO_VOLUME_CONFLICT` | ja | OBV-Abweichung bei Volumensumme null |
| 100 | `SIG_ROC_ZERO_ATR_CONFLICT` | ja | ROC ungleich null bei ATR-Quote null |
| 110 | `SIG_MA200_ZERO_ATR_CONFLICT` | ja | MA200-Abstand ungleich null bei ATR null |
| 120 | `SIG_EMA50_ZERO_ATR_CONFLICT` | ja | EMA50-Abstand ungleich null bei ATR null |
| 130 | `SIG_ATR_RATIO_ZERO_CONFLICT` | ja | positive aktuelle ATR bei ATR-Referenz null |
| 140 | `SIG_NONFINITE_RESULT` | ja | Ergebnis ist `NaN` oder unendlich |
| 150 | `SIG_RANGE_INVARIANT_FAILED` | ja | Ergebnis verletzt registrierten Wertebereich |

Die Priorität ist Bestandteil der Registry-Version.

### 23.5 Deterministische Reihenfolge und Serialisierung

`y_reason_codes` ist:

- eine geordnete Liste;
- frei von Duplikaten;
- nach aufsteigender Registry-Priorität sortiert;
- bei fehlenden Codes eine leere Liste;
- niemals `null`.

Unbekannte Codes sind unter Registry-Version `1.0.0` unzulässig.

Eine Implementierung darf mehrere zutreffende Codes sammeln. Sie darf jedoch
keinen Folgecode berechnen, dessen Prüfung selbst einen ungültigen
Zwischenwert auswerten würde. Beispielsweise wird nach einem fehlenden
Eingangswert kein arithmetischer Nichtendlichkeitsfehler künstlich erzeugt.

### 23.6 Propagation

Ist ein erforderlicher S3-Indikator ungültig, ist die abhängige
S4-Transformation ebenfalls ungültig.

Ein nachgelagerter gültiger numerischer Ausdruck darf einen ungültigen
Inputstatus nicht verdecken.

Nicht invalidierende S3-Hinweiscodes bleiben in ihren S3-Begleitfeldern
unverändert erhalten. S4 kopiert sie nicht und erfindet keine
gleichnamigen S4-Codes.

### 23.7 Feldbezogene Eingangsabhängigkeiten

Die Gültigkeit eines S4-Feldes hängt ausschließlich von seinen registrierten
Eingängen ab. Ein ungültiger, aber fachlich nicht benötigter S3-Indikator darf
ein anderes S4-Feld nicht global invalidieren.

Beispiele:

- ungültiger MFI invalidiert keine RSI-Transformation;
- ungültiger ATR invalidiert den diskreten MACD-Wert nicht, wohl aber den
  kontinuierlichen MACD-Score;
- unvollständiger ATR-SMA-200-Warm-up invalidiert nur
  `state_atr_relative_d` und `score_atr_relative_c`.

## 24. Keine Aggregation in S4

S4 MUST NOT automatisch:

- Signale summieren,
- Stimmen zählen,
- Mehrheiten bilden,
- Gewichte anwenden,
- Entry-Schwellen prüfen,
- Long-/Short-Freigaben erzeugen.

Eine spätere Strategie darf beispielsweise nur ausgewählte
`DIRECTION_DISCRETE`-Felder zu einem Timing-Score kombinieren. Diese Auswahl
und Gewichtung benötigt jedoch eine eigene versionierte Strategie- oder
Gate-Spezifikation.

## 25. Legacy-Profil

### 25.1 Felder

`LEGACY_BTC_BINARY_V1` erzeugt exakt:

- `legacy_rsi_signal`,
- `legacy_macd_signal`,
- `legacy_bollinger_signal`,
- `legacy_ma200_signal`,
- `legacy_stoch_signal`,
- `legacy_atr_signal`,
- `legacy_ema50_signal`,
- `legacy_adx_signal`,
- `legacy_cci_signal`,
- `legacy_mfi_signal`,
- `legacy_obv_signal`,
- `legacy_roc_signal`.

### 25.2 Regeln

Auf den Legacy-Indikatorwerten:

- `legacy_rsi_signal = 1`, wenn Legacy-RSI `< 30`, sonst `0`.
- `legacy_macd_signal = 1`, wenn Legacy-MACD-Histogramm `> 0`, sonst `0`.
- `legacy_bollinger_signal = 1`, wenn Close `<` Legacy-BB-Lower, sonst `0`.
- `legacy_ma200_signal = 1`, wenn Close `>` Legacy-MA200, sonst `0`.
- `legacy_stoch_signal = 1`, wenn Legacy-Stochastic `< 20`, sonst `0`.
- `legacy_atr_signal = 1`, wenn Legacy-ATR `>` Legacy-ATR-Rolling-Mean-200,
  sonst `0`.
- `legacy_ema50_signal = 1`, wenn Close `>` Legacy-EMA50, sonst `0`.
- `legacy_adx_signal = 1`, wenn Legacy-ADX `> 25`, sonst `0`.
- `legacy_cci_signal = 1`, wenn Legacy-CCI `< -100`, sonst `0`.
- `legacy_mfi_signal = 1`, wenn Legacy-MFI `< 20`, sonst `0`.
- `legacy_obv_signal = 1`, wenn Legacy-OBV `>` Legacy-OBV-Rolling-Mean-50,
  sonst `0`.
- `legacy_roc_signal = 1`, wenn Legacy-ROC `> 0`, sonst `0`.

### 25.3 Historische Warm-up-Semantik

Zur exakten Reproduktion verwendet das Legacy-Profil die historisch
verifizierte Semantik einschließlich:

- `fillna`-Verhalten des Builders,
- Vergleichen mit `NaN`, die `False` und damit `0` ergaben,
- Legacy-Rolling- und EWM-Definitionen.

Diese Semantik ist im kanonischen RCC-Profil unzulässig.

### 25.4 Empirischer Status

Die zwölf Regeln wurden über 2.721.034 vorhandene Zeilen mit null Abweichungen
gegen `data/price_data_with_signals.csv` validiert.

Dies bestätigt das Legacy-Profil, nicht die wissenschaftliche Eignung der
Regeln als neuer Standard.

### 25.5 Keine implizite Short-Inversion

Ein historisches 0/1-Signal darf nicht automatisch durch:

`short_signal = 1 - long_signal`

in ein Short-Signal umgewandelt werden.

„Bullish Bedingung nicht erfüllt“ ist nicht gleichbedeutend mit „bearish
Bedingung erfüllt“.

## 26. Verhältnis zur bestehenden L1-Logik

Die bisherige L1-Architektur verwendet unter anderem:

- RSI,
- Bollinger,
- Stochastic,
- CCI

als Timing-Score und:

- MA200,
- MFI,
- ATR

in getrennten Filter- oder Qualitätsrollen.

RCC-002 bewahrt diese Trennbarkeit durch Rollenmetadaten. Dieses Dokument
übernimmt jedoch keine konkrete bestehende Entry-, Exit- oder Score-Regel.

Eine spätere Vergleichsimplementierung MUST klar ausweisen:

- verwendetes Signalprofil,
- ausgewählte Felder,
- Score-Regel,
- Filter,
- Schwellenwerte,
- zeitliche Persistenzbedingungen.

## 27. Partitions- und Rebuild-Regeln

### 27.1 Partitionsparität

S4-Rolling-Hilfsgrößen benötigen entweder:

- korrektes Overlap oder
- validierten State.

Ein partitionierter S4-Build MUST innerhalb der definierten Toleranz mit einem
seriellen Build übereinstimmen.

### 27.2 Historische Revision

Bei geänderten S3-Werten:

- unmittelbar abhängige Transformationen werden ab der ersten Änderung neu
  berechnet,
- OBV-SMA-50 und Volumensumme-50 werden bis zum Ende ihres Einflussfensters
  neu berechnet,
- ATR-SMA-200 wird bis zum Ende seines Einflussfensters neu berechnet,
- nachgelagerte Regime, Gates und Strategieresultate werden invalidiert.

### 27.3 Segmentänderung

Ändert sich eine Lückenklassifikation oder Segmentgrenze, wird S4 ab dem
betroffenen Segmentbeginn vollständig neu berechnet.

## 28. Ausgabevertrag

### 28.1 Erzeugtes Ausgangsschema

S4 erzeugt ausschließlich:

```text
rcc002.stage.s4-signals/1.0.0
```

Das Ausgangsschema besteht aus:

1. allen S3-Feldern unverändert;
2. den vier S4-Metadaten aus Abschnitt 7.5;
3. den 24 S4-Basisfeldern aus Abschnitt 7.4;
4. genau zwei Begleitfeldern je S4-Basisfeld.

Rollenregister, Reason-Code-Register, Transformationsbericht und
Output-Checksumme sind registrierte Begleitartefakte oder Manifestinhalte.
Sie werden nicht als unstrukturierte Tabellenfelder wiederholt.

### 28.2 Zeileninvariante

S4 darf:

- keine Zeile hinzufügen,
- keine Zeile entfernen,
- keine S0-bis-S3-Werte verändern.

Es muss gelten:

`S4_rows = S3_rows`

und alle kanonischen Schlüssel müssen unverändert bleiben. Dies
konkretisiert für S4 das kanonische Row-Preservation-Prinzip aus
`RCC_002_DATA_PIPELINE_SPECIFICATION` §5.8.

Zusätzlich muss die zeilenweise Reconciliation für jedes durchgereichte
S3-Feld semantische Gleichheit bestätigen.

### 28.3 Typen und Nullbarkeit

Die logischen Typen und Nullbarkeiten sind ausschließlich jene aus Abschnitt
7.4:

- diskrete Basisfelder: nullable `Int8`;
- kontinuierliche Basisfelder: nullable `Float64`;
- `y_valid`: nicht nullbares `Boolean`;
- `y_reason_codes`: nicht nullbare geordnete Liste `Utf8`;
- S4-Metadaten: nicht nullbares `Utf8`.

Alternative physische Typen sind nur zulässig, wenn sie das registrierte
logische Schema verlustfrei und deterministisch repräsentieren.

### 28.4 Segment- und Gültigkeitsinvariante

S4 muss `market_segment_id` und `indicator_segment_id` byte- beziehungsweise
zeichenidentisch durchreichen.

Es gilt:

```text
S4.market_segment_id = S3.market_segment_id
S4.indicator_segment_id = S3.indicator_segment_id
```

Ein S4-Feld darf in einem zusätzlichen Warm-up-Bereich ungültig sein, ohne
einen neuen Segmentbezeichner zu erzeugen.

### 28.5 Komponentenidentität

Die normative Komponentenidentität lautet:

```text
component_id=RCC002_S4_SIGNAL_TRANSFORMER
component_version=0.3.0
```

Die Implementierung manifestiert zusätzlich:

- Source-Tree- oder Commit-Identität;
- `semantic_build_configuration_sha256`;
- numerisches Profil;
- Eingabe- und Ausgangsschema-Fingerprint;
- Profil- und Registry-Versionen.

### 28.6 Fehlerverhalten

Ein stageweiter Schema-, Profil-, Schlüssel- oder Sortierungsfehler bricht S4
fail-closed ab.

Ein feldbezogener mathematischer oder Warm-up-Fehler invalidiert nur die
registrierten abhängigen S4-Felder, sofern das Eingangsschema als Ganzes
gültig bleibt.

### 28.7 Keine implizite S5-/S6-Erweiterung

S5 konsumiert `rcc002.stage.s4-signals/1.0.0`. S4 darf deshalb weder
Regimezustände vorwegnehmen noch Felder mit S5- oder S6-Eigentum erzeugen.

Die genaue S5-/S6-Zustands- und Gate-Semantik wird ausschließlich in der
Regime- und Gate-Spezifikation festgelegt. Ein später geändertes S5- oder
S6-Schema verändert nicht automatisch den S4-Vertrag.

## 29. Testanforderungen

### 29.1 Grenzwerttests

Für jede diskrete Regel MUST getestet werden:

- knapp unter Schwelle,
- exakt auf Schwelle,
- knapp über Schwelle,
- ungültiger Input.

### 29.2 Vorzeichentests

MUST gelten:

- überverkaufte Mean-Reversion-Zustände erzeugen positive Evidenz,
- überkaufte Mean-Reversion-Zustände erzeugen negative Evidenz,
- positives Momentum erzeugt positive Evidenz,
- negatives Momentum erzeugt negative Evidenz,
- ATR und ADX erzeugen keine Short-/Long-Richtung.

### 29.3 Kontinuierliche Ankerwerte

Mindestens zu testen:

- RSI 30/50/70,
- Stochastic 20/50/80,
- MFI 20/50/80,
- CCI -100/0/+100,
- Close auf BB-Lower/Mid/Upper,
- ADX 15/20/25,
- ATR-Verhältnis 0.5/1/2,
- positive, negative und null normalisierte Momentumwerte.

### 29.4 Monotonietests

Innerhalb des nicht geclippten Bereichs MUST gelten:

- fallender RSI erhöht den Mean-Reversion-Long-Score,
- steigender CCI senkt den Mean-Reversion-Long-Score,
- steigendes MACD-Histogramm erhöht den Momentumscore,
- steigender Close-Abstand über MA/EMA erhöht den Trendscore,
- steigender ADX erhöht oder erhält den Trendstärkescore.

### 29.5 Kausalitätstest

Änderungen nach Zeitpunkt `t` dürfen kein S4-Feld bei `t` verändern.

### 29.6 Legacy-Golden-Test

Das Legacy-Profil MUST die zwölf historischen Signalspalten über den bekannten
Datensatz mit null Regelabweichungen reproduzieren.

### 29.7 Rollen-Sicherheitstest

Ein Schema- oder Aggregationsvalidator MUST verhindern, dass Felder mit Rolle:

- `VOLATILITY_STATE`,
- `TREND_STRENGTH`

ohne explizite Transformationsregel als `DIRECTION_DISCRETE` oder
`DIRECTION_SCORE` behandelt werden.

### 29.8 Schema- und Vertragsprüfung

Mindestens erforderlich sind:

- Annahme von `rcc002.stage.s3-indicators/1.0.0`;
- Ablehnung unbekannter S3- oder S4-Major-Versionen;
- exakte S4-Spaltenallowlist und Spaltenreihenfolge;
- exakte logische Typen und Nullbarkeit;
- unveränderte S3-Felder und Primärschlüssel;
- `S4_rows = S3_rows`;
- unveränderte `market_segment_id`;
- unveränderte `indicator_segment_id`;
- vollständige vier S4-Metadaten;
- exakt zwei Begleitfelder je Basisfeld;
- keine Legacy-, S5-, S6- oder S7-Felder im kanonischen S4-Artefakt;
- Ablehnung unbekannter Reason Codes;
- deterministische Reason-Code-Reihenfolge.

### 29.9 Validitäts- und Nulltests

Für jedes S4-Basisfeld sind zu testen:

- gültiger Minimalfall;
- ungültiger erforderlicher S3-Input;
- irrelevanter ungültiger S3-Input;
- `quality_gate_pass=false`;
- unvollständiger zusätzlicher S4-Warm-up;
- Segmentgrenze innerhalb eines potenziellen Fensters;
- definierter Nullnennerfall;
- widersprüchlicher Nullnennerfall;
- nicht endliches Zwischenergebnis;
- Wertebereichsverletzung;
- `y=null` genau dann, wenn `y_valid=false`;
- leere statt nuller Reason-Code-Liste bei gültigem Standardfall.

### 29.10 Property-Based Tests

SHOULD geprüft werden:

- spätere Eingangswerte verändern kein früheres S4-Feld;
- zusätzliche physische Partitionierung verändert keine S4-Semantik;
- jedes gültige Basisfeld ist endlich und liegt im registrierten Bereich;
- jedes ungültige Basisfeld ist logisch `null`;
- kein invalidierender Reason Code tritt bei `y_valid=true` auf;
- kein Basisfeld besitzt ein nullbares `y_valid` oder `y_reason_codes`;
- kein Rolling Window überschreitet eine Indikatorsegmentgrenze;
- Mean-Reversion-Transformationen besitzen die dokumentierte Monotonie;
- Trendstärke und Volatilität werden nicht als Richtung umgedeutet.

## 30. Numerische Toleranzen

Das normative numerische Profil lautet:

```text
signal_numeric_profile_id=RCC002_FLOAT64_SIGNAL_NUMERICS_V1
signal_numeric_profile_version=1.0.0
```

Für unabhängige `float64`-Vergleiche gelten standardmäßig:

- `absolute_tolerance = 1e-12`,
- `relative_tolerance = 1e-10`.

Diskrete Entscheidungen werden aus ungerundeten Werten gebildet.

Ein Wert innerhalb numerischer Vergleichstoleranz zur Schwelle wird nicht
automatisch als gleich behandelt. Falls eine Schwellen-Hysterese erforderlich
ist, muss sie separat spezifiziert und versioniert werden.

### 30.1 Vergleichsregel

Für unabhängige Implementierungen gilt komponentenweise:

```text
abs(a - b) <= absolute_tolerance
               + relative_tolerance * max(abs(a), abs(b))
```

Logische Nullwerte werden nur positionsgleich mit logischen Nullwerten
verglichen. Diskrete Basisfelder, Validitätsfelder, Reason Codes, Profilfelder
und Schemafelder müssen exakt übereinstimmen.

### 30.2 Operations- und Determinismusgrenzen

Vor `Approved for Implementation` müssen versioniert festgelegt sein:

- Reihenfolge nicht assoziativer Float-Operationen;
- zulässige oder deaktivierte FMA-Nutzung;
- Parallelreduktionsregeln für Rolling-Fenster;
- Behandlung von Subnormalwerten;
- Konvertierung interner `NaN`- und Inf-Werte;
- Referenzimplementierung der Golden Fixtures;
- numerisch wirksame Bibliotheken und Versionen.

Eine Änderung dieser Regeln verändert mindestens das numerische Profil und
erfordert erneute Golden-, Kausalitäts- und Partitionsparitätstests.

## 31. Transformationsbericht

Der Bericht enthält mindestens:

- Build-, Profil- und Schemaversion,
- Eingabe- und Ausgangsschema-ID,
- S3- und S4-Schema-Fingerprint,
- `semantic_build_configuration_sha256`,
- Signal-, Validitäts- und numerisches Profil,
- Reason-Code-Registry-Version,
- Eingabe- und Ausgabezeilen,
- gültige und ungültige Werte je Feld,
- Häufigkeit `-1`, `0`, `+1` je diskretem Feld,
- Minimum, Maximum, Mittelwert und Quantile je kontinuierlichem Feld,
- Clipping-Anteil bei `-1` und `+1`,
- Reason-Code-Häufigkeiten,
- erste gültige Zeit je Feld und Segment,
- Rollenregisterprüfung,
- Kausalitäts- und Partitionsparität,
- Legacy-Vergleich,
- Output-Checksumme.

Ein sehr hoher Clipping-Anteil ist kein automatischer Fehler, erzeugt aber ein
Review-Finding.

## 32. Publication Gate

S4 darf nur veröffentlicht werden, wenn:

1. S3 vollständig freigegeben ist,
2. alle aktiven Profile registriert sind,
3. Vorzeichen- und Rollenregeln bestanden sind,
4. alle diskreten Werte im zulässigen Wertebereich liegen,
5. alle kontinuierlichen Werte im zulässigen Wertebereich liegen,
6. ungültige Inputs korrekt propagiert wurden,
7. keine nicht endlichen gültigen Scores bestehen,
8. Zeilen und vorgelagerte Felder unverändert sind,
9. Grenzwert-, Ankerwert-, Monotonie- und Kausalitätstests bestanden sind,
10. partitionierter und serieller Build übereinstimmen,
11. Legacy- und RCC-Felder strikt getrennt sind,
12. das S4-Schema exakt `rcc002.stage.s4-signals/1.0.0` erfüllt,
13. jedes Basisfeld exakt seine beiden Begleitfelder besitzt,
14. Reason Codes ausschließlich aus Registry-Version `1.0.0` stammen,
15. `market_segment_id` und `indicator_segment_id` unverändert sind,
16. keine S5-, S6- oder S7-Felder enthalten sind,
17. Manifest, Rollenregister und Checksummen vollständig sind,
18. Property-Tests bestanden sind.

Der Gate-Status lautet:

- `PASS`,
- `FAIL`,
- `PASS_WITH_APPROVED_EXCEPTIONS`.

`PASS_WITH_APPROVED_EXCEPTIONS` darf ausschließlich nicht blockierende,
vollständig dokumentierte Berichtsbefunde betreffen. Es darf weder
Schemafehler noch falsche Feldwerte, unzulässige Nullwerte, Segmentfehler,
nicht endliche gültige Werte, Rollenverletzungen oder eine fehlgeschlagene
Reconciliation überstimmen.

Die in diesem Abschnitt aufgeführten Ausnahmefälle für
`PASS_WITH_APPROVED_EXCEPTIONS` sind abschließend. Kein hier nicht
aufgeführter Fall darf unter diesem Gate-Status genehmigt werden, ohne
zuvor eine normative Spezifikationsänderung, eine Versionsanhebung, einen
Review und eine erneute Zertifizierungsbewertung zu durchlaufen. Eine
menschliche Genehmigung allein erweitert nicht den normativen
Ausnahmeumfang.

## 33. Offene Implementierungsparameter

### 33.1 Vor `Approved for Implementation` festzulegen

Folgende semantische oder determinismusrelevante Festlegungen müssen
versioniert vorliegen:

- vollständiges maschinenlesbares S4-Schema;
- vollständiges Signalrollen- und Reason-Code-Register;
- kanonische Profil- und Komponentenregister;
- vollständige Eingangsabhängigkeit je S4-Feld;
- logische Typen, Nullbarkeit und Feldreihenfolge;
- Schema-Fingerprinting- und Kompatibilitätsregeln;
- numerisches Determinismusprofil;
- gebundene numerisch wirksame Bibliotheken und Versionen;
- feldbezogene Referenztoleranzen;
- Golden-Fixture-Inhalte und erwartete Resultate;
- Build-Einstiegspunktvertrag;
- Umgebungs- und Lockstrategie;
- S3→S4-Reconciliation;
- Test- und Abnahmekriterien.

Diese Festlegungen gehören zur `semantic_build_configuration`, soweit sie
fachliche Werte, Gültigkeit, Schema, Profile oder Reproduzierbarkeit
beeinflussen.

### 33.2 Während der Implementierung konkretisierbar

Innerhalb vorher festgelegter physischer Profile dürfen konkretisiert werden:

- physische Partitionsgrößen;
- Parquet-Row-Group-Größen;
- Kompressionsstufe;
- Writeroptimierungen;
- Cache- und temporäre Speicherorte;
- Retentionsparameter temporärer Zwischenartefakte;
- technisch gleichwertige Speicherorte.

Diese Parameter gehören zur `physical_publication_configuration`. Sie dürfen
weder Signalwerte noch Gültigkeit, Reason Codes, logisches S4-Schema,
`build_id` oder `dataset_id` verändern.

Jede spätere Änderung mit Wirkung auf fachliche Semantik, logische Schemas,
Identitätsvorabbildungen oder numerische Determinismusregeln muss die
betroffenen Review-Gates erneut durchlaufen.

## 34. Abnahmekriterien

### 34.1 Spezifikationsreife vor Implementierungsfreigabe

Die Spezifikation ist bereit für `Approved for Implementation`, wenn:

1. alle logischen S3-Eingangs- und S4-Ausgangsfelder mit Typ, Nullsemantik,
   Eigentümerstufe und Reihenfolge festgelegt sind;
2. jede Transformation eine feste Profil- und Feldversion besitzt;
3. alle Formeln, Grenzwerte, Gleichheits-, Warm-up- und Nullfälle eindeutig
   sind;
4. `y_valid` und `y_reason_codes` maschinenlesbar definiert sind;
5. Rollen-Sicherheit und S5-/S6-Abgrenzung vollständig spezifiziert sind;
6. Schema-, Profil-, Registry-, Komponenten- und numerische IDs versioniert
   sind;
7. semantische und physische Konfiguration getrennt sind;
8. Golden-, Unit-, Property-, Schema-, Rollen-, Kausalitäts- und
   Integrationstestverträge vollständig sind;
9. Publication Gate und Manifestvertrag vollständig sind;
10. kanonisches und Legacy-Profil strikt getrennt sind;
11. alle vorgeschriebenen internen und externen Review-Gates der
    Spezifikationsbaseline bestanden sind;
12. keine offene Entscheidung fachliche Werte, Gültigkeit, logisches Schema
    oder Identitätsvorabbildungen verändern kann.

### 34.2 Abnahme der Implementierung

Die spätere Implementierung ist akzeptiert, wenn:

1. alle Transformationen als eigenständige Funktionen testbar sind;
2. Grenzwert-, Ankerwert-, Nullfall- und Golden-Tests bestanden sind;
3. Rollen-Sicherheit technisch erzwungen wird;
4. Legacy-Reproduktion bestanden ist;
5. Schema-, Segment-, Kausalitäts- und Partitionsparität bestanden sind;
6. der BTCUSDT-1m-Vollbuild auf der Workstation erfolgreich ist;
7. ein unabhängiger Rebuild mindestens semantische Gleichheit erreicht;
8. keine Zeile und kein S3-Feld verändert wurde;
9. Manifest und Knowledge Lineage vollständig sind;
10. keine ungeklärten Regel-, Vorzeichen- oder Schnittstellenkonflikte
    bestehen;
11. das S4-Publication-Gate automatisiert bestanden ist.

## 35. Freigabestatus und nächster Schritt

`RCC-002-SCR-004` bestätigte die dort geprüften wissenschaftlichen
Korrekturen als geschlossen.

Der vollständige Architecture Integrity Review `RCC-002-AIR-001` bewertete
die Spezifikationsfamilie als:

```text
NOT PASSED – ARCHITECTURE CORRECTIONS REQUIRED
```

Version 0.4.0 bewahrt die AIR-001-Korrekturen aus Version 0.3.0 und
korrigiert zusätzlich:

- `SCR-005-B01` – vollständiger Schlüssel
  `(market_type, symbol, interval, open_time)`, Multi-Provider-Regel und
  Ausschluss von `timeframe`;
- `SCR-005-M01` – getrennte S4-Schema-ID, Schemaversion und abgeleitete
  Schemareferenz.

Sie aktualisiert außerdem die Abhängigkeiten auf:

```text
RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md
Version 0.7.0

RCC_002_DATA_VALIDATION_2026-07-23.md
Version 0.4.0

RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md
Version 0.4.0
```

Die Befunde sind erst geschlossen, wenn alle abhängigen Spezifikationen
konsistent aktualisiert, neu paketiert und erneut geprüft sind.

Der aktuelle Status lautet:

```text
SCR-005-Corrected Draft – Scientific Consistency Re-Review 006 Pending
```

Nächste vorgeschriebene Schritte:

1. übrige abhängige Spezifikationen korrigieren;
2. vollständige interne Qualitätskontrolle;
3. neues vollständiges Spezifikationspaket;
4. fokussierter Scientific Consistency Re-Review;
5. fokussierter Architecture Integrity Re-Review;
6. Editorial Pass;
7. Internal Certification;
8. Claude Independent Architecture Review;
9. Gemini Independent Scientific and Adversarial Audit;
10. ChatGPT Final Consolidation;
11. `Baseline V1 Certified`;
12. Implementierungsfreigabe.

---

# Eingebettetes Dokument 5 von 7

## Quelldatei: `RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md`

# RCC-002 Regime and Gate Specification

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Scientific Software Specification |
| Dokument-ID | RCC-002-RG |
| Titel | Regime and Gate Specification |
| Speicherort im Repository | `docs/specifications/RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md` |
| Dateiname | `RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md` |
| Version | 0.5.1 |
| Datum | 2026-07-23 |
| Status | SCR-005-Corrected Draft – Scientific Consistency Re-Review 006 Pending |
| Übergeordnetes Dokument | `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`, Version 0.7.1 |
| Direkte Abhängigkeiten | `RCC_002_DATA_VALIDATION_2026-07-23.md`, Version 0.4.2; `RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md`, Version 0.4.3; `RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md`, Version 0.4.2 |
| Geltungsbereich | S5_REGIMES und S6_GATES der RCC-002-Datenpipeline |
| Referenziert durch | Strategieforschung; Backtests; Regimeanalyse; Paper-/Live-Parität; spätere adaptive Steuerung |
| Autoritative Sprache | Englische Feldnamen, Profil-IDs, Zustände und Regeln sind normativ; deutsche Erläuterungen präzisieren die Semantik |

### Review-Nachweis

| Prüfung | Status | Ergebnis |
|---|---|---|
| Struktur- und Nummerierungsprüfung | Bestanden | Regime-, Kontext- und Gate-Ebenen vollständig |
| Verantwortlichkeitstrennung | Bestanden | Marktklassifikation, Trendstärke, Volatilität und Handelsfreigabe getrennt |
| State-Machine-Prüfung | Bestanden | Initialisierung, Persistenz, Übergänge und Segment-Reset eindeutig |
| Fail-closed-Prüfung | Bestanden | Ungültige oder unbekannte Zustände blockieren aktivierte Gates |
| Kausalitätsprüfung | Bestanden | Keine zukunftsbezogenen Regime- oder Gate-Regeln |
| Legacy-Trennungsprüfung | Bestanden | Historische und GS-nahe Vergleichsprofile bleiben nichtkanonische Referenzen |
| Strategietrennungsprüfung | Bestanden | L1-Timing, MFI-Filter, Cooldown und Exit-Regeln nicht in S5/S6 verschoben |
| Scientific Consistency Review | `RCC-002-SCR-004` bestanden | Die dort geprüften wissenschaftlichen Befunde sind geschlossen; erneuter fokussierter Review nach den semantisch relevanten AIR-001-Korrekturen erforderlich |
| Architecture Integrity Review | `RCC-002-AIR-001` nicht bestanden; Korrektur eingearbeitet | Version 0.4.0 korrigiert die diesem Dokument zugeordneten Teile von `AIR-001-B01`, `AIR-001-B03`, `AIR-001-M01` und `AIR-001-M03`; dokumentübergreifender Re-Review ausstehend |
| Scientific Consistency Re-Review 005 | `RCC-002-SCR-005` nicht bestanden; Korrektur eingearbeitet | Version 0.5.0 korrigiert `SCR-005-B01`, `SCR-005-M01` und `SCR-005-M02`; SCR-006 ausstehend |
| Minor Correction Cycle | `RCC-002-SCR-007-MinFV` umgesetzt | Version 0.5.1, 2026-07-27: Minor correction cycle: version, dependency, terminology, checklist and cross-reference consistency corrections. |
| Editorial Pass | Ausstehend | Nach bestandenem Architecture Integrity Review |
| Internal Certification | Ausstehend | Nach bestandenem Editorial Pass |
| Claude Independent Architecture Review | Ausstehend | Erst nach Internal Certification |
| Gemini Independent Scientific and Adversarial Audit | Ausstehend | Erst nach bestandenem Claude-Review |
| ChatGPT Final Consolidation | Ausstehend | Erst nach abgeschlossenem Gemini-Audit |
| Baseline V1 Certified | Nicht erreicht | Erst nach Schließung aller wesentlichen Befunde |

## 1. Zweck

Dieses Dokument definiert:

1. die kausale Beschreibung des Marktregimes in S5 und
2. die davon getrennte Erzeugung von Long-/Short-Freigaben in S6.

Die Spezifikation verhindert, dass:

- eine Marktbezeichnung automatisch als Handelsentscheidung gilt,
- ADX als Richtungsindikator missverstanden wird,
- Volatilität ein implizites Long-/Short-Vorzeichen erhält,
- bestehende Strategieparameter in die Datenpipeline einwandern,
- Regimeregeln anhand späterer Performance rückwirkend umbenannt werden,
- ungültige Daten als neutrales oder handelbares Regime erscheinen.

## 2. Geltungsbereich

### 2.1 Enthalten

Enthalten sind:

- Trendrichtungsregime,
- persistiertes effektives Regime,
- richtungslose Trendstärke,
- relative Volatilität,
- Datenqualitäts-Gate,
- offene Forschungsfreigabe,
- trendgerichtete Gate-Profile,
- Gate-Komposition,
- Reason Codes,
- Legacy- und Vergleichsprofile,
- Tests, Reports und Publication Gates.

### 2.2 Nicht enthalten

Nicht enthalten sind:

- Timing-Score aus RSI, Bollinger, Stochastic und CCI,
- MFI-Entry-Filter,
- Entry-Persistenz einer konkreten Strategie,
- Cooldown,
- Loss-Cluster-Gate,
- TP, SL oder Time-Stop,
- Exit-Regeln,
- Positionsgröße und Kapitalallokation,
- Equity- oder Portfolio-Gates,
- endgültige Aktivierung eines Forschungs-Gates im Live-Betrieb.

Diese Elemente benötigen eigene Strategie-, Execution- oder Risk-Spezifikationen.

## 3. Verantwortlichkeitsebenen

### 3.1 S5 – Marktklassifikation

S5 beantwortet ausschließlich:

- Welche langfristige Trendrichtung ist zum Zeitpunkt `t` beobachtbar?
- Wie stark ist der Trend?
- Liegt die aktuelle ATR oberhalb oder unterhalb ihrer Referenz?
- Ist der Zustand gültig und ausreichend warmgelaufen?

### 3.2 S6 – Handelsfreigabe

S6 beantwortet:

- Darf eine nachgelagerte Strategie Long-Signale prüfen?
- Darf eine nachgelagerte Strategie Short-Signale prüfen?
- Welche Gate-Regel erlaubt oder blockiert die jeweilige Richtung?

### 3.3 Strategieebene

Die Strategieebene entscheidet:

- ob ein konkretes Entry-Signal vorliegt,
- welche Timing-Signale kombiniert werden,
- welche Persistenz ein Entry benötigt,
- ob MFI oder andere Signale als Filter gelten,
- wann eine Position geschlossen wird.

Ein `allow_long = true` erzeugt keinen Long-Trade.

## 4. Vorzeichen- und Zustandssemantik

### 4.1 Trendrichtung

Zulässige Werte:

- `BULL`,
- `SIDE`,
- `BEAR`,
- `UNKNOWN`.

### 4.2 Trendstärke

Zulässige Werte:

- `WEAK`,
- `DEVELOPING`,
- `STRONG`,
- `UNKNOWN`.

Trendstärke besitzt keine Long-/Short-Richtung.

### 4.3 Relative Volatilität

Zulässige Werte:

- `BELOW_REFERENCE`,
- `AT_REFERENCE`,
- `ABOVE_REFERENCE`,
- `UNKNOWN`.

Relative Volatilität besitzt keine Long-/Short-Richtung.

### 4.4 Gate

Long und Short werden getrennt als Boolean gespeichert:

- `allow_long`,
- `allow_short`.

Ein Gate darf beide Richtungen:

- erlauben,
- blockieren

oder nur eine Richtung erlauben.

## 5. Profile und Status

### 5.1 `RCC_TREND_REGIME_RAW_V1`

Kanonische kausale Rohklassifikation anhand:

- Close relativ zu SMA 200,
- kausaler SMA-200-Slope über 1.440 Minuten.

### 5.2 `RCC_TREND_REGIME_PERSISTED_V1`

Persistierte Zustandsmaschine auf Basis des Rohregimes mit:

`confirm_bars = 3`

### 5.3 `RCC_CONTEXT_V1`

Ergänzt:

- ADX-Trendstärke,
- ATR-Relativzustand.

Diese Felder ändern die Regimebezeichnung nicht.

### 5.4 `GATE_RESEARCH_OPEN_V1`

Erlaubt bei gültiger Daten- und Featurelage beide Richtungen.

Dies ist das kanonische Standardprofil für unvoreingenommene
Strategieforschung, weil es keine ungeprüfte Regimezensur einführt.

### 5.5 `GATE_TREND_ALIGNED_V1`

Forschungsprofil:

- effektives Bull-Regime erlaubt Long,
- effektives Bear-Regime erlaubt Short,
- Side und Unknown blockieren beide Richtungen.

ADX wird in diesem Profil nicht als Mindestbedingung verwendet.

### 5.6 `GATE_TREND_STRENGTH_ALIGNED_V1`

Forschungsprofil:

- wie `GATE_TREND_ALIGNED_V1`,
- zusätzlich ADX `> 15`.

Dieses Profil muss vor einer produktiven Aktivierung separat falsifiziert und
Out-of-Sample validiert werden.

### 5.7 Legacy- und Rekonstruktionsprofile

- `LEGACY_BTC_REGIME_V1`,
- `GS_REGIME_RECONSTRUCTION_V1`.

Diese Profile dienen Vergleich und Lineage. Sie sind nicht automatisch
kanonische RCC-002-Gates.

### 5.8 Profilversionen

Für die erste Baseline gilt:

| Profil-ID | Profilversion |
|---|---|
| `RCC_TREND_REGIME_RAW_V1` | `1.0.0` |
| `RCC_TREND_REGIME_PERSISTED_V1` | `1.0.0` |
| `RCC_CONTEXT_V1` | `1.0.0` |
| `GATE_RESEARCH_OPEN_V1` | `1.0.0` |
| `GATE_TREND_ALIGNED_V1` | `1.0.0` |
| `GATE_TREND_STRENGTH_ALIGNED_V1` | `1.0.0` |
| `LEGACY_BTC_REGIME_V1` | `1.0.0` |
| `GS_REGIME_RECONSTRUCTION_V1` | `1.0.0` |

Eine fachliche Regel-, Schwellen-, Persistenz- oder
Pflichtinputänderung benötigt mindestens eine neue Profilversion.

## 6. Eingabevertrag

### 6.1 Akzeptiertes S5-Eingangsschema

S5 akzeptiert für die erste Baseline ausschließlich:

```text
rcc002.stage.s4-signals/1.0.0
```

Eine unbekannte Major-Version wird fail-closed abgelehnt. Eine neuere
Minor-Version darf nur aufgrund einer registrierten S5-Kompatibilitätsregel
akzeptiert werden.

### 6.2 Pflichtfelder für S5

S5 benötigt:

- `market_type`;
- `symbol`;
- `interval`;
- `open_time`;
- `close_time`;
- `market_segment_id`;
- `indicator_segment_id`;
- `quality_gate_pass`;
- `close`;
- `sma_close_200`;
- `sma_close_200_valid`;
- `sma_close_200_warmup_complete`;
- `sma_close_200_reason_codes`;
- `state_atr_relative_d`;
- `state_atr_relative_d_valid`;
- `state_atr_relative_d_reason_codes`;
- `score_atr_relative_c`;
- `score_atr_relative_c_valid`;
- `score_atr_relative_c_reason_codes`;
- `adx_wilder_14`;
- `adx_wilder_14_valid`;
- `adx_wilder_14_warmup_complete`;
- `adx_wilder_14_reason_codes`;
- `state_adx_strength_d`;
- `state_adx_strength_d_valid`;
- `state_adx_strength_d_reason_codes`;
- `score_adx_strength_c`;
- `score_adx_strength_c_valid`;
- `score_adx_strength_c_reason_codes`;
- die S3- und S4-Profil- und Schemametadaten.

Optionale Vergleichs- und Transparenzfelder:

- `state_ma200_trend_d`,
- `state_ema50_trend_d`,
- `sig_roc_momentum_d`.

Legacy- oder Rekonstruktionsprofile dürfen zusätzliche profilgebundene
Pflichtfelder verlangen. Diese werden nicht zu allgemeinen
RCC-TREND-REGIME-Pflichtfeldern.

### 6.3 S5-Hilfsgröße

S5 berechnet den kausalen SMA-200-Slope:

`ma200_slope_1440_pct_t = 100 * (sma_close_200_t / sma_close_200_(t-1440) - 1)`

Voraussetzungen:

- beide SMA-Werte gültig,
- beide Werte größer als null,
- alle erforderlichen Zeitpunkte gehören zum selben Segment,
- zwischen den Vergleichspunkten liegt keine Datenlücke.

### 6.4 Akzeptiertes S6-Eingangsschema

S6 akzeptiert für die erste Baseline ausschließlich:

```text
rcc002.stage.s5-regimes/1.0.0
```

Unbekannte Major-Versionen werden fail-closed abgelehnt.

### 6.5 S6-Pflichtfelder

S6 benötigt:

- alle unverändert durchgereichten S0-bis-S4-Felder;
- `regime_raw`;
- `regime_effective`;
- `regime_valid`;
- `regime_reason_codes`;
- `trend_strength`;
- `trend_strength_valid`;
- `trend_strength_reason_codes`;
- `volatility_relative`;
- `volatility_relative_valid`;
- `volatility_relative_reason_codes`;
- `regime_model_id`;
- `regime_model_version`;
- `regime_schema_id`;
- `regime_schema_version`;
- `regime_schema_ref`;
- die aktive Gate-Profil-ID und Gate-Profilversion aus der
  `semantic_build_configuration`.

### 6.6 Eingabeinvarianten

S5 und S6 MUST:

- ausschließlich freigegebene vorgelagerte Artefakte konsumieren,
- Schema- und Profilversionen prüfen,
- kanonische Schlüssel unverändert erhalten,
- die Sortierung `(market_type, symbol, interval, open_time)` unverändert
  erhalten,
- `market_segment_id` und `indicator_segment_id` unverändert durchreichen,
- Segmentgrenzen respektieren,
- ungültige Inputs nicht als neutral interpretieren.

Der logische Primärschlüssel bleibt in S5 und S6:

```text
(market_type, symbol, interval, open_time)
```

Wenn der Eingang noch nicht konsolidierte Multi-Provider-Daten enthält, MUSS
`provider` als zusätzlicher registrierter Schlüsselbestandteil unmittelbar
vor `market_type` geführt werden. State-, Reconciliation-, Fingerprint- und
Partitionierungsverträge MÜSSEN dieselbe Schlüsselvariante verwenden.

`timeframe` ist kein Aliasfeld eines kanonischen S5- oder S6-Schemas. Eine
Legacy-Migration nach `interval` MUSS vor S4 abgeschlossen sein.

### 6.7 Eingangsablehnung

Die jeweilige Stufe bricht vor einer fachlichen Verarbeitung ab bei:

- inkompatibler oder unbekannter Eingangsschema-ID;
- fehlendem Pflichtfeld;
- nicht registriertem Datentyp oder nicht registrierter Nullbarkeit;
- ungültigem Primärschlüssel;
- nichtkanonischer Sortierung;
- widersprüchlichen Gültigkeitsfeldern;
- unbekannter Profil-, Modell- oder Reason-Code-Registry-Version;
- nicht freigegebenem vorgelagertem Publication-Status.

Ein stageweiter Vertragsfehler wird nicht als zeilenweises `UNKNOWN` oder
`INVALID` weitergeführt, sondern führt zum fail-closed Abbruch der Stufe.

## 7. Rohregime

### 7.1 Bull

`regime_raw = BULL`, wenn gleichzeitig:

- `close > sma_close_200`,
- `ma200_slope_1440_pct > 0`.

### 7.2 Bear

`regime_raw = BEAR`, wenn gleichzeitig:

- `close < sma_close_200`,
- `ma200_slope_1440_pct < 0`.

### 7.3 Side

`regime_raw = SIDE`, wenn alle erforderlichen Inputs gültig sind und weder die
Bull- noch die Bear-Regel vollständig erfüllt ist.

Insbesondere Side:

- Close oberhalb SMA200 bei nichtpositivem Slope,
- Close unterhalb SMA200 bei nichtnegativem Slope,
- exakte Preisgleichheit,
- exakter Slope null.

### 7.4 Unknown

`regime_raw = UNKNOWN`, wenn:

- `quality_gate_pass=false` ist,
- SMA200 oder Slope ungültig ist,
- Warm-up unvollständig ist,
- das Fenster eine Lücke überschreitet,
- `market_segment_id` oder `indicator_segment_id` nicht konsistent ist,
- ein erforderlicher Input nicht endlich ist,
- Profil- oder Segmentkonsistenz fehlt.

### 7.5 Exklusivität

Für jede gültige Zeile gilt genau eine Klasse:

`BULL XOR SIDE XOR BEAR`

`UNKNOWN` ist ausschließlich ein Invalid-/Unavailable-Zustand.

## 8. Warm-up

### 8.1 SMA200

Der erste SMA200 ist innerhalb eines neuen Segments am Index:

`199`

gültig.

### 8.2 Slope

Der erste Slope benötigt zusätzlich 1.440 Minuten Abstand.

Damit liegt der erste mögliche Rohregimewert innerhalb eines lückenfreien
1-Minuten-Segments am Index:

`199 + 1440 = 1639`

Erforderlich sind 1.640 aufeinanderfolgende Kerzen.

### 8.3 Persistiertes Regime

Das effektive Regime benötigt anschließend drei identische gültige Rohzustände.

Der früheste mögliche effektive Zustand liegt daher am Index:

`1641`

### 8.4 Segmentwechsel

Nach jeder Segmentgrenze beginnt der vollständige Warm-up erneut.

## 9. Persistierte Regime-Zustandsmaschine

### 9.1 Zweck

Das persistierte Regime reduziert kurzzeitige Zustandswechsel, ohne
Zukunftsdaten zu verwenden.

### 9.2 Zustandsvariablen

- `regime_effective`,
- `regime_candidate`,
- `regime_candidate_count`,
- `regime_transition_flag`,
- `regime_transition_from`,
- `regime_transition_to`.

### 9.3 Initialisierung

Am Segmentanfang:

- `regime_effective = UNKNOWN`,
- `regime_candidate = UNKNOWN`,
- `regime_candidate_count = 0`.

### 9.4 Verarbeitung eines gültigen Rohzustands

Für `regime_raw_t` in `{BULL, SIDE, BEAR}`:

1. Wenn `regime_raw_t = regime_candidate_(t-1)`:
   - setze `regime_candidate_count =
     min(regime_candidate_count_(t-1) + 1, 3)`.
2. Andernfalls:
   - setze `regime_candidate = regime_raw_t`,
   - setze `regime_candidate_count = 1`.
3. Wenn:
   - `regime_candidate_count >= 3` und
   - `regime_candidate != regime_effective`,
   dann wird `regime_effective = regime_candidate`.
4. Andernfalls bleibt `regime_effective` unverändert.

### 9.5 Verarbeitung von Unknown

Wenn `regime_raw_t = UNKNOWN`:

- `regime_effective_t = UNKNOWN`,
- Candidate und Count werden zurückgesetzt,
- beide Richtungen werden in fail-closed Gates blockiert.

Nach Rückkehr gültiger Daten beginnt die Dreifachbestätigung neu.

### 9.6 Übergangszeitpunkt

Ein Übergang wird auf der dritten bestätigenden geschlossenen Kerze wirksam.

Die Gate-Wirkung darf frühestens nach dem Verfügbarkeitszeitpunkt dieser Kerze
verwendet werden.

Bei einem tatsächlichen Wechsel gilt:

- `regime_transition_flag = true`,
- `regime_transition_from` enthält den vorherigen effektiven Zustand,
- `regime_transition_to` enthält den neuen effektiven Zustand.

Der Wechsel eines zuvor gültigen effektiven Zustands nach `UNKNOWN` ist ein
tatsächlicher Übergang und wird mit `transition_to=UNKNOWN` protokolliert.
Der erstmalige bestätigte Wechsel von `UNKNOWN` nach `BULL`, `SIDE` oder
`BEAR` wird ebenfalls protokolliert.

Am Segmentanfang mit vorherigem und aktuellem Zustand `UNKNOWN` liegt kein
Übergang vor.

Ohne Wechsel gilt:

- `regime_transition_flag = false`,
- From und To sind `null`.

### 9.7 Keine rückwirkende Umschreibung

Die ersten beiden Candidate-Kerzen behalten das vorherige effektive Regime.
Nach der dritten Bestätigung werden frühere Zeilen nicht rückwirkend geändert.

## 10. Trendstärke

### 10.1 Definition

Auf gültigem `adx_wilder_14`:

- ADX `<= 15`: `trend_strength = WEAK`,
- ADX `> 15` und `<= 25`: `trend_strength = DEVELOPING`,
- ADX `> 25`: `trend_strength = STRONG`.

### 10.2 Unknown

Bei ungültigem ADX:

`trend_strength = UNKNOWN`

### 10.3 Richtungsfreiheit

`STRONG` bedeutet nicht Bull und nicht Bear.

Trendrichtung und Trendstärke dürfen nur durch eine explizite Gate-Regel
kombiniert werden.

## 11. Relative Volatilität

### 11.1 Definition

Auf gültigem `state_atr_relative_d`:

- `-1`: `volatility_relative = BELOW_REFERENCE`,
- `0`: `volatility_relative = AT_REFERENCE`,
- `+1`: `volatility_relative = ABOVE_REFERENCE`.

### 11.2 Unknown

Bei ungültigem ATR-Relativzustand:

`volatility_relative = UNKNOWN`

### 11.3 Richtungsfreiheit

`ABOVE_REFERENCE` ist weder bullish noch bearish.

Die bestehende L1-Erkenntnis, dass ATR-Kontexte unterschiedliche
Entry-Schwellen benötigen können, gehört in eine separat versionierte
Strategieregel und nicht in die S5-Regimebezeichnung.

## 12. S5-Ausgabefelder

### 12.1 Erzeugtes Ausgangsschema

S5 erzeugt:

```text
rcc002.stage.s5-regimes/1.0.0
```

Das Ausgangsschema enthält alle S4-Felder unverändert und genau die
registrierten S5-Erweiterungsfelder dieses Abschnitts.

### 12.2 Kanonisches S5-Feldregister

| Feld | Logischer Typ | Nullbar | Eigentümer | Semantik |
|---|---|:---:|---|---|
| `regime_raw` | Enum `RegimeState` | Nein | `S5_REGIMES` | aktueller ungeglätteter Zustand |
| `regime_effective` | Enum `RegimeState` | Nein | `S5_REGIMES` | kausal persistierter Zustand |
| `regime_candidate` | Enum `RegimeState` | Nein | `S5_REGIMES` | aktuell zu bestätigender Zustand |
| `regime_candidate_count` | `UInt8` | Nein | `S5_REGIMES` | Anzahl aufeinanderfolgender Candidate-Bestätigungen, `0...3` |
| `regime_transition_flag` | `Boolean` | Nein | `S5_REGIMES` | tatsächlicher effektiver Zustandswechsel |
| `regime_transition_from` | Enum `RegimeState` | Ja | `S5_REGIMES` | vorheriger effektiver Zustand bei Übergang |
| `regime_transition_to` | Enum `RegimeState` | Ja | `S5_REGIMES` | neuer effektiver Zustand bei Übergang |
| `ma200_slope_1440_pct` | `Float64` | Ja | `S5_REGIMES` | kausaler SMA200-Slope |
| `trend_strength` | Enum `TrendStrength` | Nein | `S5_REGIMES` | richtungslose ADX-Klasse |
| `trend_strength_valid` | `Boolean` | Nein | `S5_REGIMES` | Gültigkeit der Trendstärkeklasse |
| `trend_strength_reason_codes` | geordnete Liste `Utf8` | Nein | `S5_REGIMES` | Trendstärkegründe |
| `volatility_relative` | Enum `VolatilityRelative` | Nein | `S5_REGIMES` | richtungsloser ATR-Relativzustand |
| `volatility_relative_valid` | `Boolean` | Nein | `S5_REGIMES` | Gültigkeit des Volatilitätszustands |
| `volatility_relative_reason_codes` | geordnete Liste `Utf8` | Nein | `S5_REGIMES` | Volatilitätsgründe |
| `regime_model_id` | `Utf8` | Nein | `S5_REGIMES` | aktive kanonische Modell-ID |
| `regime_model_version` | `Utf8` | Nein | `S5_REGIMES` | aktive Modellversion |
| `regime_schema_id` | `Utf8` | Nein | `S5_REGIMES` | `rcc002.stage.s5-regimes` |
| `regime_schema_version` | `Utf8` | Nein | `S5_REGIMES` | `1.0.0` |
| `regime_schema_ref` | `Utf8` | Nein | `S5_REGIMES` | `rcc002.stage.s5-regimes/1.0.0` |
| `regime_valid` | `Boolean` | Nein | `S5_REGIMES` | Gültigkeit von Roh- und Effektivregime |
| `regime_reason_codes` | geordnete Liste `Utf8` | Nein | `S5_REGIMES` | deterministische Regimegründe |

### 12.3 Kanonische Enum-Register

`RegimeState` verwendet ausschließlich:

```text
BULL
SIDE
BEAR
UNKNOWN
```

`TrendStrength` verwendet ausschließlich:

```text
WEAK
DEVELOPING
STRONG
UNKNOWN
```

`VolatilityRelative` verwendet ausschließlich:

```text
BELOW_REFERENCE
AT_REFERENCE
ABOVE_REFERENCE
UNKNOWN
```

Ein S5-Wert `INVALID` ist in keinem dieser Enums zulässig.

### 12.4 Modell- und Schemametadaten

Die erste kanonische Modellidentität lautet:

```text
regime_model_id=RCC002_TREND_CONTEXT_REGIME_V1
regime_model_version=1.0.0
regime_schema_id=rcc002.stage.s5-regimes
regime_schema_version=1.0.0
regime_schema_ref=rcc002.stage.s5-regimes/1.0.0
```

Die Modellidentität umfasst die Rohregime-, Persistenz- und Kontextregeln
dieses Dokuments. Legacy- oder GS-Rekonstruktionsmodelle verwenden eigene
Modell- und Schemaidentitäten.

### 12.5 Regimegültigkeit

Es gilt:

```text
regime_valid =
    required_regime_inputs_valid
    AND slope_warmup_complete
    AND segment_consistent
    AND result_finite
    AND regime_raw IN {BULL, SIDE, BEAR}
    AND regime_effective IN {BULL, SIDE, BEAR}
```

Wenn `regime_valid=false`, gilt:

- `regime_raw=UNKNOWN` oder `regime_effective=UNKNOWN`;
- mindestens ein invalidierender `regime_reason_code`;
- `UNKNOWN` wird nicht als `SIDE` interpretiert.

Während der ersten beiden gültigen Candidate-Kerzen kann
`regime_raw` bereits gültig sein, während `regime_effective=UNKNOWN` bleibt.
In diesem Initialisierungsfall ist `regime_valid=false`, bis erstmals ein
effektiver Zustand bestätigt wurde.

Die Gültigkeit von Trendstärke und Volatilität ist feldbezogen. Ein
ungültiger ADX-Kontext macht ein anderweitig berechenbares Regime nicht
ungültig.

### 12.6 Kontextgültigkeit

Für Trendstärke gilt:

```text
trend_strength_valid = adx_wilder_14_valid
```

Wenn `trend_strength_valid=false`:

```text
trend_strength=UNKNOWN
```

Für relative Volatilität gilt:

```text
volatility_relative_valid = state_atr_relative_d_valid
```

Wenn `volatility_relative_valid=false`:

```text
volatility_relative=UNKNOWN
```

### 12.7 S5-Reason-Code-Register

```text
regime_reason_code_registry_version=1.0.0
```

| Priorität | Code | Ziel | Invalidierend |
|---:|---|---|:---:|
| 30 | `REG_INPUT_QUALITY_GATE_FAILED` | Regime | Ja |
| 40 | `REG_INPUT_INVALID` | Regime | Ja |
| 50 | `REG_WARMUP_INCOMPLETE` | Regime | Ja |
| 60 | `REG_WINDOW_CROSSES_INDICATOR_SEGMENT` | Regime | Ja |
| 70 | `REG_SLOPE_DENOMINATOR_INVALID` | Regime | Ja |
| 80 | `REG_NONFINITE_RESULT` | Regime | Ja |
| 90 | `REG_EFFECTIVE_UNCONFIRMED` | Regime | Ja |
| 100 | `REG_SEGMENT_RESET` | Regime | Ja |
| 110 | `REG_TREND_STRENGTH_INPUT_INVALID` | Trendstärke | Ja |
| 120 | `REG_VOLATILITY_INPUT_INVALID` | Volatilität | Ja |

Die drei Reason-Code-Listen sind:

- nicht null;
- frei von Duplikaten;
- nach aufsteigender Registry-Priorität sortiert;
- bei fehlenden Codes als leere Liste serialisiert.

#### 12.7.1 Regime-Reason-Bildung

`regime_reason_codes` enthält alle sicher feststellbaren zutreffenden Codes:

- `REG_INPUT_QUALITY_GATE_FAILED` bei `quality_gate_pass=false`;
- `REG_INPUT_INVALID` bei ungültigem erforderlichem Preis- oder SMA-Input;
- `REG_WARMUP_INCOMPLETE` vor vollständigem Slope-Warm-up;
- `REG_WINDOW_CROSSES_INDICATOR_SEGMENT`, wenn die Slope-Abhängigkeit eine
  Segmentgrenze überschreiten würde;
- `REG_SLOPE_DENOMINATOR_INVALID` bei nichtpositivem oder ungültigem
  Vergleichs-SMA;
- `REG_NONFINITE_RESULT` bei nicht endlichem Rechenergebnis;
- `REG_EFFECTIVE_UNCONFIRMED`, solange ein gültiger Rohzustand noch keinen
  ersten effektiven Zustand bestätigt hat;
- `REG_SEGMENT_RESET` auf der ersten Zeile nach einem Segmentwechsel.

Bei vollständig gültigem Roh- und Effektivregime ohne zutreffenden Hinweis
ist die Liste leer.

#### 12.7.2 Kontext-Reason-Bildung

`trend_strength_reason_codes` enthält ausschließlich
`REG_TREND_STRENGTH_INPUT_INVALID`, wenn der erforderliche ADX-Input ungültig
ist; andernfalls ist die Liste leer.

`volatility_relative_reason_codes` enthält ausschließlich
`REG_VOLATILITY_INPUT_INVALID`, wenn der erforderliche ATR-Relativzustand
ungültig ist; andernfalls ist die Liste leer.

### 12.8 Kanonische Feldreihenfolge

Die kanonische Reihenfolge lautet:

1. alle S4-Felder in unveränderter S4-Reihenfolge;
2. die S5-Felder in der Reihenfolge aus Abschnitt 12.2.

Nicht registrierte Zusatzfelder oder alternative Aliasfelder machen das
Artefakt nicht kanonisch.

Optionale transparente Evidenzfelder:

- `regime_price_above_ma200`,
- `regime_price_below_ma200`,
- `regime_slope_positive`,
- `regime_slope_negative`.

Diese Evidenzfelder gehören nicht zu
`rcc002.stage.s5-regimes/1.0.0`. Werden sie benötigt, müssen sie in einer
separaten registrierten Diagnose-View veröffentlicht werden.

### 12.9 Schema-Fingerprint und Kompatibilität

Der S5-Schema-Fingerprint umfasst mindestens:

- geordnete Feldnamen;
- logische Datentypen und Nullbarkeit;
- Feld- und Enum-Semantik;
- Eigentümerstufen;
- Primärschlüssel und Sortierung;
- Modell-, Schema- und Registry-Versionen;
- Reason-Code-Prioritäten;
- Kompatibilitätsregeln.

Für S5 gilt semantische Versionierung. Eine neue Minor-Version wird nur
aufgrund einer registrierten Kompatibilitätsregel akzeptiert. Unbekannte
Major-Versionen sind fail-closed abzulehnen.

### 12.10 Komponentenidentität

```text
component_id=RCC002_S5_REGIME_CLASSIFIER
component_version=0.4.0
```

Die Implementierung manifestiert zusätzlich Source-Tree- oder
Commit-Identität, numerisches Profil, Eingangs- und Ausgangsschema-Fingerprint
sowie Modell-, State- und Registry-Versionen.

## 13. Datenqualitäts-Gate

### 13.1 Zweck

Vor jeder Richtungsregel wird ein gemeinsames Datenqualitäts-Gate angewandt.

### 13.2 `data_gate_pass`

S6 bildet:

```text
data_gate_pass = quality_gate_pass
```

`data_gate_pass` ist damit die unveränderte S6-Entscheidungsabbildung des
kanonischen S2-Qualitäts-Gates. Es wird nicht aus Regime-, Signal-, ADX- oder
Strategiefeldern abgeleitet.

Diese Gleichheit gilt ausschließlich nach erfolgreicher stageweiter Prüfung
von Schema, Primärschlüssel, Sortierung und Segmentvertrag. Eine Verletzung
dieser Strukturverträge bricht S6 ab und erzeugt keine kanonische S6-Zeile.
Sie darf weder als `data_gate_pass=false` noch als `gate_state=INVALID`
zeilenweise serialisiert werden.

Die einzige normative Wahrheitstabelle lautet:

| Strukturvertrag | `quality_gate_pass` | Profilpflichtinputs | S6-Ergebnis |
|---|:---:|---|---|
| ungültig | beliebig | nicht ausgewertet | Stage-Abbruch; keine S6-Zeile |
| gültig | `false` | nicht ausgewertet | `data_gate_pass=false`; `gate_valid=true`; `BLOCK_BOTH` |
| gültig | `true` | gültig | `data_gate_pass=true`; profilspezifische Auswertung; `gate_valid=true` |
| gültig | `true` | ungültig | `data_gate_pass=true`; `gate_valid=false`; `INVALID` |

S3-, S4-, Regime- oder ADX-Felder werden erst durch die jeweils konsumierende
Strategie beziehungsweise Richtungsregel geprüft. Dadurch bleibt
`GATE_RESEARCH_OPEN_V1` auch während des S3-/S4-/S5-Warm-ups eine tatsächlich
offene Datenqualitätsbaseline, ohne ungültige Strategiefeatures als gültig
umzudefinieren.

### 13.3 Fail-closed

Wenn `data_gate_pass = false`:

- `allow_long = false`,
- `allow_short = false`,
- beide Richtungslisten enthalten `GATE_DATA_QUALITY_FAILED`.

Dies gilt unabhängig vom gewählten Richtungs-Gate.

Ein deterministisch festgestelltes `data_gate_pass=false` macht das Gate nicht
automatisch ungültig. Wenn alle zur Feststellung benötigten Felder gültig
waren, ist das Gate gültig ausgewertet und erhält:

```text
gate_valid=true
gate_state=BLOCK_BOTH
```

Nur ungültige profilabhängige Pflichtinputs bei strukturell gültigem Eingang
und `data_gate_pass=true` führen zeilenweise zu:

```text
gate_valid=false
gate_state=INVALID
allow_long=false
allow_short=false
```

## 14. `GATE_RESEARCH_OPEN_V1`

### 14.1 Zweck

Dieses Profil stellt eine unzensierte, aber qualitätsgesicherte
Forschungsbaseline bereit.

### 14.2 Regeln

Wenn `data_gate_pass = true`:

- `allow_long = true`,
- `allow_short = true`.

Andernfalls:

- beide `false`.

Wenn `data_gate_pass` deterministisch gebildet wurde, bleibt
`gate_valid=true`. Bei `data_gate_pass=false` ist der Zustand
`BLOCK_BOTH`, nicht `INVALID`.

Ein ungültiges oder noch nicht bestätigtes Regime beeinflusst dieses Profil
nicht und wird deshalb nicht als Gate-Invalidität übernommen.

### 14.3 Status

Dieses Profil ist der kanonische RCC-002-Standardexport für allgemeine
Strategieforschung.

Es ist kein Live-Risikogate.

## 15. `GATE_TREND_ALIGNED_V1`

### 15.1 Long

`allow_long = true`, wenn:

- `data_gate_pass = true`,
- `regime_effective = BULL`.

### 15.2 Short

`allow_short = true`, wenn:

- `data_gate_pass = true`,
- `regime_effective = BEAR`.

### 15.3 Side und Unknown

Bei gültigem:

- `SIDE`

werden beide Richtungen blockiert.

Das Ergebnis ist:

```text
gate_valid=true
gate_state=BLOCK_BOTH
```

Bei `data_gate_pass=true` und zugleich `UNKNOWN` oder `regime_valid=false`
sind die profilabhängigen Pflichtinputs ungültig. Das Ergebnis ist:

```text
gate_valid=false
gate_state=INVALID
allow_long=false
allow_short=false
```

### 15.4 ADX

ADX beeinflusst dieses Profil nicht.

Damit kann der isolierte Effekt reiner Trendrichtung untersucht werden.

## 16. `GATE_TREND_STRENGTH_ALIGNED_V1`

### 16.1 Mindeststärke

Zulässige Stärke:

- `DEVELOPING`,
- `STRONG`.

Dies entspricht:

`adx_wilder_14 > 15`

### 16.2 Long

`allow_long = true`, wenn:

- `data_gate_pass = true`,
- `regime_effective = BULL`,
- `trend_strength in {DEVELOPING, STRONG}`.

### 16.3 Short

`allow_short = true`, wenn:

- `data_gate_pass = true`,
- `regime_effective = BEAR`,
- `trend_strength in {DEVELOPING, STRONG}`.

### 16.4 Blockierung

Gültig mit `gate_state=BLOCK_BOTH` werden beide Richtungen blockiert bei:

- `SIDE`;
- `WEAK`;
- fehlgeschlagenem Daten-Gate.

Bei `data_gate_pass=true` werden beide Richtungen ungültig mit
`gate_state=INVALID` blockiert bei:

- `UNKNOWN`;
- `regime_valid=false`;
- unbekannter oder ungültiger Trendstärke;
- sonstigem ungültigem profilabhängigem Pflichtinput.

## 17. Gate-Komposition

### 17.1 Ausgewähltes Profil

Pro S6-View ist genau ein Richtungsprofil aktiv:

- Research Open,
- Trend Aligned,
- Trend Strength Aligned

oder ein später registriertes Profil.

### 17.2 Kompositionsregel

Für jede Richtung:

`final_allow_direction = data_gate_pass AND profile_allow_direction`

### 17.3 Keine implizite Priorität

Mehrere Richtungsprofile dürfen nicht still durch AND oder OR kombiniert
werden.

Eine kombinierte Policy benötigt:

- eigene Gate-ID,
- eigene Version,
- explizite Wahrheitstabelle,
- eigene Tests.

### 17.4 Long-/Short-Unabhängigkeit

Long und Short werden getrennt berechnet und protokolliert.

Eine blockierte Long-Richtung impliziert keine Short-Freigabe und umgekehrt.

## 18. Gate-Ausgabefelder

### 18.1 Erzeugtes Ausgangsschema

S6 erzeugt:

```text
rcc002.stage.s6-gates/1.0.0
```

Das Ausgangsschema enthält alle S5-Felder unverändert und genau die
registrierten S6-Erweiterungsfelder dieses Abschnitts.

### 18.2 Kanonisches S6-Feldregister

| Feld | Logischer Typ | Nullbar | Eigentümer | Semantik |
|---|---|:---:|---|---|
| `allow_long` | `Boolean` | Nein | `S6_GATES` | Long-Prüfung nach aktivem Profil erlaubt |
| `allow_short` | `Boolean` | Nein | `S6_GATES` | Short-Prüfung nach aktivem Profil erlaubt |
| `data_gate_pass` | `Boolean` | Nein | `S6_GATES` | Abbildung des kanonischen S2-Qualitäts-Gates |
| `gate_state` | Enum `GateState` | Nein | `S6_GATES` | zusammengefasster Gate-Zustand |
| `gate_reason_codes_long` | geordnete Liste `Utf8` | Nein | `S6_GATES` | Long-spezifische Gründe |
| `gate_reason_codes_short` | geordnete Liste `Utf8` | Nein | `S6_GATES` | Short-spezifische Gründe |
| `gate_profile_id` | `Utf8` | Nein | `S6_GATES` | aktive Gatepolicy |
| `gate_profile_version` | `Utf8` | Nein | `S6_GATES` | Version der aktiven Gatepolicy |
| `gate_schema_id` | `Utf8` | Nein | `S6_GATES` | `rcc002.stage.s6-gates` |
| `gate_schema_version` | `Utf8` | Nein | `S6_GATES` | `1.0.0` |
| `gate_schema_ref` | `Utf8` | Nein | `S6_GATES` | `rcc002.stage.s6-gates/1.0.0` |
| `gate_valid` | `Boolean` | Nein | `S6_GATES` | profilabhängige Auswertung vollständig gültig |
| `gate_evaluated_at` | UTC-Timestamp in Millisekunden | Nein | `S6_GATES` | Point-in-Time-Verfügbarkeit der ausgewerteten Zeile |
| `regime_model_id` | `Utf8` | Nein | `S5_REGIMES`, durchgereicht | referenziertes S5-Modell |
| `regime_model_version` | `Utf8` | Nein | `S5_REGIMES`, durchgereicht | referenzierte S5-Modellversion |

`regime_model_id` und `regime_model_version` werden nicht erneut erzeugt,
sondern unverändert aus S5 durchgereicht. Sie stehen in der kanonischen
S6-Pflichtausgabe, besitzen aber weiterhin S5-Eigentum.

### 18.3 Gate-State-Enum

`GateState` verwendet ausschließlich:

- `ALLOW_BOTH`,
- `ALLOW_LONG_ONLY`,
- `ALLOW_SHORT_ONLY`,
- `BLOCK_BOTH`,
- `INVALID`.

Ein zusätzlicher Wert `UNKNOWN` ist in `GateState` nicht zulässig.

### 18.4 Gate-State-Wahrheitsregel

```text
if gate_valid = false:
    gate_state = INVALID
    allow_long = false
    allow_short = false
elif allow_long = true and allow_short = true:
    gate_state = ALLOW_BOTH
elif allow_long = true and allow_short = false:
    gate_state = ALLOW_LONG_ONLY
elif allow_long = false and allow_short = true:
    gate_state = ALLOW_SHORT_ONLY
else:
    gate_state = BLOCK_BOTH
```

Für das jeweils aktive Profil gilt:

- `INVALID`, wenn dessen erforderliche Daten oder Zustände nicht berechenbar
  sind; beide Richtungen sind `false` und `gate_valid = false`.
- `BLOCK_BOTH`, wenn alle erforderlichen Zustände gültig sind, die Policy aber
  keine Richtung erlaubt; `gate_valid = true`.

Ein Unknown-Regime führt daher bei trendgerichteten Profilen zu `INVALID`, beim
regimeunabhängigen `GATE_RESEARCH_OPEN_V1` jedoch nicht.

### 18.5 Profilabhängige Pflichtinputs

Die profilabhängigen Pflichtinputs werden nur ausgewertet, wenn
`data_gate_pass=true`. Bei deterministisch festgestelltem
`data_gate_pass=false` endet die fachliche Auswertung mit einem gültigen
`BLOCK_BOTH`; ungültige nachgelagerte Profilinputs erzeugen in dieser Zeile
keine zusätzliche Gate-Invalidität.

| Gate-Profil | Erforderliche gültige Inputs |
|---|---|
| `GATE_RESEARCH_OPEN_V1` | `data_gate_pass` deterministisch gebildet |
| `GATE_TREND_ALIGNED_V1` | `data_gate_pass`, `regime_valid`, `regime_effective` |
| `GATE_TREND_STRENGTH_ALIGNED_V1` | `data_gate_pass`, `regime_valid`, `regime_effective`, `trend_strength_valid`, `trend_strength` |

`volatility_relative` ist in keinem der drei Baseline-Gateprofile
Pflichtinput. Seine bloße Verfügbarkeit erzeugt keine Gatebedingung.

### 18.6 Gate-Profil- und Schemametadaten

Für alle drei Baseline-Profile gilt:

```text
gate_profile_version=1.0.0
gate_schema_id=rcc002.stage.s6-gates
gate_schema_version=1.0.0
gate_schema_ref=rcc002.stage.s6-gates/1.0.0
```

Genau eine der folgenden Profil-IDs ist je S6-Artefakt aktiv:

```text
GATE_RESEARCH_OPEN_V1
GATE_TREND_ALIGNED_V1
GATE_TREND_STRENGTH_ALIGNED_V1
```

### 18.7 Point-in-Time-Semantik

Es gilt:

```text
gate_evaluated_at = close_time
```

`gate_evaluated_at` ist kein Build-Wanduhrzeitstempel. Eine Gateentscheidung
der Zeile `t` darf erst ab diesem Verfügbarkeitszeitpunkt konsumiert werden.

### 18.8 Kanonische Feldreihenfolge

Die kanonische Reihenfolge lautet:

1. alle S5-Felder in unveränderter S5-Reihenfolge;
2. die S6-eigenen Felder aus Abschnitt 18.2 in Tabellenreihenfolge, wobei die
   bereits vorhandenen S5-Felder `regime_model_id` und
   `regime_model_version` nicht dupliziert werden.

Alternative Aliasfelder wie `gate_inputs_valid` oder `gate_reason_mask` sind
unzulässig.

### 18.9 Schema-Fingerprint und Kompatibilität

Der S6-Schema-Fingerprint umfasst mindestens:

- geordnete Feldnamen;
- logische Datentypen und Nullbarkeit;
- Feld- und Enum-Semantik;
- Eigentümerstufen;
- Primärschlüssel und Sortierung;
- Profil-, Schema- und Registry-Versionen;
- Reason-Code-Prioritäten;
- Kompatibilitätsregeln.

Für S6 gilt semantische Versionierung. Unbekannte Major-Versionen sind
fail-closed abzulehnen. Neue Minor-Versionen benötigen eine registrierte
Kompatibilitätsregel.

### 18.10 Komponentenidentität

```text
component_id=RCC002_S6_GATE_EVALUATOR
component_version=0.4.0
```

Die Implementierung manifestiert zusätzlich Source-Tree- oder
Commit-Identität, Eingangs- und Ausgangsschema-Fingerprint, Gate-Profil und
Reason-Code-Registry-Version.

## 19. Reason Codes

### 19.1 Verbindliches Registry-Profil

```text
gate_reason_code_registry_version=1.0.0
```

### 19.2 Verbindliches S6-Reason-Code-Register

| Priorität | Code | Richtung | Klasse |
|---:|---|---|---|
| 30 | `GATE_INPUT_INVALID` | beide | invalidierend |
| 40 | `GATE_WARMUP_INCOMPLETE` | beide | invalidierend |
| 50 | `GATE_SEGMENT_RESET` | beide | invalidierend |
| 60 | `GATE_REGIME_UNKNOWN` | beide | invalidierend für trendgerichtete Profile |
| 70 | `GATE_TREND_STRENGTH_UNKNOWN` | beide | invalidierend für das Stärkeprofil |
| 80 | `GATE_STATE_INVALID` | beide | invalidierend |
| 90 | `GATE_DATA_QUALITY_FAILED` | beide | gültige Blockierung |
| 100 | `GATE_LONG_BLOCKED_SIDE` | Long | gültige Blockierung |
| 110 | `GATE_LONG_BLOCKED_BEAR` | Long | gültige Blockierung |
| 120 | `GATE_LONG_BLOCKED_WEAK_TREND` | Long | gültige Blockierung |
| 130 | `GATE_SHORT_BLOCKED_SIDE` | Short | gültige Blockierung |
| 140 | `GATE_SHORT_BLOCKED_BULL` | Short | gültige Blockierung |
| 150 | `GATE_SHORT_BLOCKED_WEAK_TREND` | Short | gültige Blockierung |
| 160 | `GATE_LONG_ALLOWED_RESEARCH_OPEN` | Long | Freigabe |
| 170 | `GATE_SHORT_ALLOWED_RESEARCH_OPEN` | Short | Freigabe |
| 180 | `GATE_LONG_ALLOWED_BULL` | Long | Freigabe |
| 190 | `GATE_SHORT_ALLOWED_BEAR` | Short | Freigabe |
| 200 | `GATE_LONG_ALLOWED_BULL_WITH_STRENGTH` | Long | Freigabe |
| 210 | `GATE_SHORT_ALLOWED_BEAR_WITH_STRENGTH` | Short | Freigabe |

Die Einstufung „invalidierend“ ist profilabhängig, soweit die Tabelle dies
ausdrücklich bestimmt. Ein Unknown-Regime invalidiert das Research-Open-Profil
nicht, weil dieses Profil das Regime nicht konsumiert.

### 19.3 Richtungsbezogene Bildung

`gate_reason_codes_long` enthält nur:

- richtungsneutrale System-, Daten- und Invaliditätscodes;
- Long-spezifische Blockierungs- oder Freigabecodes.

`gate_reason_codes_short` enthält nur:

- richtungsneutrale System-, Daten- und Invaliditätscodes;
- Short-spezifische Blockierungs- oder Freigabecodes.

Ein Long-spezifischer Code darf nicht in der Short-Liste erscheinen und
umgekehrt.

### 19.4 Deterministische Serialisierung

Beide Reason-Code-Listen sind:

- nicht null;
- frei von Duplikaten;
- nach aufsteigender Registry-Priorität sortiert;
- bei fehlenden Codes als leere Liste serialisiert.

Unbekannte Codes sind unter Registry-Version `1.0.0` unzulässig.

## 20. Gate-Reason-Priorität

### 20.1 Primärer Reason Code

Der primäre Reason Code einer Richtung ist der erste Code ihrer sortierten
vollständigen Liste.

Ein separates Feld für den primären Reason Code wird in
`rcc002.stage.s6-gates/1.0.0` nicht geführt.

### 20.2 Vollständigkeit

Alle zutreffenden, sicher auswertbaren Gründe bleiben erhalten. Nach einem
stageweiten Schemafehler wird keine zeilenweise Gateausgabe erzeugt. Nach
einem zeilenweisen ungültigen Pflichtinput dürfen keine fachlichen
Folgeprüfungen künstliche Zusatzgründe erzeugen.

### 20.3 Konsistenz mit `gate_valid`

Wenn eine Richtungsliste einen für das aktive Profil invalidierenden Code
enthält:

```text
gate_valid=false
gate_state=INVALID
allow_long=false
allow_short=false
```

Codes der Klasse „gültige Blockierung“ sind mit `gate_valid=true` vereinbar.
Freigabecodes sind nur bei der jeweiligen `allow_* = true` zulässig.

### 20.4 Deterministische Auswertungsreihenfolge

S6 bildet die Reason-Code-Listen in folgender Reihenfolge:

1. Vor der Zeilenauswertung werden Schema-, Schlüssel-, Sortierungs- und
   Segmentvertrag stageweit geprüft. Ein Fehler bricht S6 ohne Zeilenausgabe
   ab.
2. Ist bei strukturell gültigem Eingang `data_gate_pass=false`, erhalten beide Listen ausschließlich
   `GATE_DATA_QUALITY_FAILED`; die Auswertung endet mit gültigem
   `BLOCK_BOTH`.
3. Bei `data_gate_pass=true` werden ausschließlich die Pflichtinputs des
   aktiven Profils geprüft.
4. Sind diese ungültig, werden die Invaliditätscodes nach Abschnitt 20.5
   gebildet; die Auswertung endet mit `INVALID`.
5. Sind alle Pflichtinputs gültig, werden für jede Richtung alle nicht
   erfüllten Policyprädikate als Blockierungscodes oder bei vollständig
   erfüllter Regel genau der registrierte Freigabecode ausgegeben.
6. Abschließend werden die Listen dedupliziert und nach Registry-Priorität
   sortiert.

### 20.5 Abbildung ungültiger S5-Zustände

Bei einem für das aktive Profil erforderlichen ungültigen Regime werden in
beide Richtungslisten aufgenommen:

- `GATE_WARMUP_INCOMPLETE`, wenn `regime_reason_codes`
  `REG_WARMUP_INCOMPLETE` oder `REG_EFFECTIVE_UNCONFIRMED` enthält;
- `GATE_SEGMENT_RESET`, wenn `regime_reason_codes`
  `REG_SEGMENT_RESET` oder `REG_WINDOW_CROSSES_INDICATOR_SEGMENT` enthält;
- immer `GATE_REGIME_UNKNOWN`.

Bei ungültiger erforderlicher Trendstärke wird zusätzlich in beide Listen
aufgenommen:

```text
GATE_TREND_STRENGTH_UNKNOWN
```

Sonstige zeilenbezogene ungültige Pflichtinputs erzeugen:

```text
GATE_INPUT_INVALID
```

### 20.6 Abbildung gültiger Policyzustände

Für `GATE_RESEARCH_OPEN_V1` werden bei `data_gate_pass=true` exakt ausgegeben:

- Long: `GATE_LONG_ALLOWED_RESEARCH_OPEN`;
- Short: `GATE_SHORT_ALLOWED_RESEARCH_OPEN`.

Für `GATE_TREND_ALIGNED_V1` gilt:

| Regime | Long-Code | Short-Code |
|---|---|---|
| `BULL` | `GATE_LONG_ALLOWED_BULL` | `GATE_SHORT_BLOCKED_BULL` |
| `SIDE` | `GATE_LONG_BLOCKED_SIDE` | `GATE_SHORT_BLOCKED_SIDE` |
| `BEAR` | `GATE_LONG_BLOCKED_BEAR` | `GATE_SHORT_ALLOWED_BEAR` |

Für `GATE_TREND_STRENGTH_ALIGNED_V1` werden zunächst dieselben
Regimeblockierungen wie oben gebildet. Zusätzlich erzeugt `WEAK` für die
jeweilige Richtung den entsprechenden
`GATE_*_BLOCKED_WEAK_TREND`-Code.

Bei `DEVELOPING` oder `STRONG` und passender Regimerichtung ersetzt der
jeweilige Aligned-Freigabecode den profilspezifischen Freigabecode:

- Long: `GATE_LONG_ALLOWED_BULL_WITH_STRENGTH`;
- Short: `GATE_SHORT_ALLOWED_BEAR_WITH_STRENGTH`.

Eine Richtung mit mindestens einem Blockierungscode darf keinen Freigabecode
enthalten.

## 21. Historisches BTC-Regime

### 21.1 Profil

`LEGACY_BTC_REGIME_V1`

### 21.2 Regeln

Bull:

- Close `>` Legacy-MA200,
- Legacy-EMA50 `>` Legacy-MA200,
- Legacy-ROC `> 0`,
- Legacy-ADX `>= 15`.

Bear:

- Close `<` Legacy-MA200,
- Legacy-EMA50 `<` Legacy-MA200,
- Legacy-ROC `< 0`,
- Legacy-ADX `>= 15`.

Sonst:

- Side.

### 21.3 Ausgaben

- `legacy_market_regime`,
- `legacy_regime_signal`,
- `legacy_regime_bull`,
- `legacy_regime_bear`.

Diese Felder gehören ausschließlich zum separaten Vergleichsschema:

```text
rcc002.comparison.s5-legacy-btc-regime/1.0.0
```

Sie dürfen nicht im kanonischen
`rcc002.stage.s5-regimes/1.0.0` enthalten sein.

### 21.4 Empirischer Status

Die Regeln stimmen über die vorhandenen 1.048.575 Datenzeilen ohne Abweichung
mit der historischen Regimedatei überein.

Die Datei ist wegen ihrer exakten Excel-Grenzgröße und der längeren
vorgelagerten Signaldatei als wahrscheinlich abgeschnittenes
`NON_CANONICAL_LEGACY_ARTIFACT` zu behandeln.

### 21.5 Architektonische Einordnung

Das Legacy-Regime koppelt:

- Trendrichtung,
- Momentum,
- Trendstärke

in einer Klassifikation.

RCC-002 erhält es zur Reproduktion, übernimmt diese Kopplung aber nicht als
kanonische Architektur.

## 22. GS-Rekonstruktionsprofil

### 22.1 Status

`GS_REGIME_RECONSTRUCTION_V1` ist eine rekonstruierte Vergleichshypothese.

Sie ist nicht empirisch vollständig bestätigt, weil der ursprüngliche
kanonische BTC-GS-Datensatz nicht vollständig erhalten ist.

### 22.2 Rekonstruierte Grundstruktur

Nach bisherigem Evidenzstand:

- Regimerichtung über Close relativ zu MA200 und MA200-Slope,
- Long-/Short-Freigaben separat,
- ADX als Gate- oder Stärkeinformation,
- keine unveränderte Übernahme der historischen BTC-Kopplung.

### 22.3 Kennzeichnung

Jede Ausgabe dieses Profils MUST:

- `reconstruction_status = HYPOTHESIS`,
- Evidenzquellen,
- offene Unsicherheiten,
- rekonstruierte Parameter

im Manifest dokumentieren.

Sie darf nicht als verifizierte historische Wahrheit bezeichnet werden.

Sie verwendet ein separates registriertes Vergleichsschema und darf weder das
kanonische S5-Modell noch das kanonische S6-Gateartefakt überschreiben.

## 23. Verhältnis zur bestehenden L1-Baseline

### 23.1 Aktuelle empirische Referenz

Die bestehende L1-Baseline nutzt:

- MA200 als Long-/Short-Trendfilter,
- MFI als gerichteten Entry-Filter,
- ATR als Qualitätskontext für unterschiedliche Timing-Schwellen,
- einen Timing-Score aus RSI, Bollinger, Stochastic und CCI.

### 23.2 Trennung in RCC-002

Davon gehören:

- MA200-Marktzustand grundsätzlich in S5,
- ATR-Relativzustand grundsätzlich in S5,
- Timing-Score, MFI-Filter und ATR-abhängige Entry-Schwellen in die
  Strategieebene.

### 23.3 Keine automatische Übernahme

Die profitable L1-Baseline belegt nicht automatisch, dass
`GATE_TREND_STRENGTH_ALIGNED_V1` überlegen ist.

Die bisherigen Regimeauswertungen basieren auf bereits ausgewählten Trades und
sind deshalb keine unverzerrte Bewertung aller blockierten und erlaubten
Marktzeitpunkte.

Eine Gate-Aktivierung benötigt eine separate Counterfactual-Analyse.

## 24. Counterfactual-Gate-Evaluation

### 24.1 Zweck

Ein Gate muss nicht nur die ausgeführten Trades analysieren, sondern auch:

- welche Baseline-Trades es erlaubt hätte,
- welche Baseline-Trades es blockiert hätte,
- welche Gewinne und Verluste jeweils betroffen wären,
- wie sich Tradezahl und Marktphasenabdeckung verändern.

### 24.2 Pflichtgruppen

Für jedes Kandidatengate:

1. `ALLOWED_AND_TRADED`,
2. `BLOCKED_BUT_BASELINE_TRADED`,
3. `ALLOWED_NO_BASELINE_ENTRY`,
4. `INVALID_OR_UNKNOWN`.

### 24.3 Mindestmetriken

- Tradezahl,
- Return,
- Profit Factor,
- Winrate,
- Max Drawdown,
- durchschnittlicher PnL,
- Long/Short getrennt,
- Regime und Volatilitätskontext,
- Zeitfensterstabilität,
- Anteil blockierter Gewinner und Verlierer,
- längste Blockierungssequenz.

### 24.4 Keine In-Sample-Aktivierung

Ein Gate darf nicht allein anhand desselben Zeitraums ausgewählt und bewertet
werden.

Erforderlich sind:

- Entwicklungszeitraum,
- Validierungszeitraum,
- unberührter Testzeitraum,
- Walk-Forward- oder vergleichbare zeitgerechte Prüfung.

## 25. Falsifikationskriterien

Ein Forschungs-Gate gilt als nicht ausreichend gestützt, wenn mindestens eine
der folgenden Bedingungen eintritt:

- Verbesserung stammt nur aus einem einzelnen Zeitfenster,
- Tradezahl sinkt so stark, dass Ergebnisse statistisch nicht belastbar sind,
- Drawdown verschlechtert sich wesentlich,
- Profit Factor steigt nur durch wenige extreme Gewinner,
- Long oder Short wird strukturell unzureichend abgedeckt,
- Gate blockiert überproportional robuste Gewinner,
- Ergebnisse brechen bei kleinen Schwellenänderungen zusammen,
- Wirkung verschwindet nach Gebühren und Slippage,
- Vorteil besteht nur auf zur Auswahl verwendeten Daten,
- Unknown- oder Side-Anteil verhindert praktisch den Betrieb.

Konkrete numerische Akzeptanzgrenzen werden vor den Gate-Experimenten in einem
separaten Testplan präregistriert.

## 26. Kausalität und Verfügbarkeit

### 26.1 Kerzenschluss

Regime und Gates bei `t` verwenden ausschließlich vollständig geschlossene und
verfügbare Kerzen bis einschließlich `t`.

### 26.2 Früheste Nutzung

Ein bei Kerze `t` berechneter Gate-Zustand darf frühestens nach dem
Verfügbarkeitszeitpunkt der geschlossenen Kerze `t` verwendet werden.

### 26.3 Keine Zukunftsbestätigung

Unzulässig sind:

- zentrierte Slope-Fenster,
- spätere Preisbewegungen zur Bestätigung früherer Regime,
- rückwirkende Umbenennung von Übergangsperioden,
- Forward Returns als Regimeinput,
- nachträgliches Glätten mit zukünftigen Zuständen.

## 27. Lücken und Segmente

### 27.1 Segment-Reset

Bei einer S2-/S3-Segmentgrenze:

- Slope-Warm-up beginnt neu,
- Rohregime bleibt bis dahin Unknown,
- persistierte State Machine wird zurückgesetzt,
- fail-closed Gates blockieren beide Richtungen.

### 27.2 Keine State-Übernahme über Lücken

Ein effektives Bull- oder Bear-Regime darf nicht über eine ungeklärte
Datenlücke fortgeführt werden.

### 27.3 Synthetische Ansicht

Regime auf synthetischen Kontinuitätsdaten benötigt:

- eine eigene Profil-ID,
- einen eigenen Build,
- eine separate Sensitivitätsanalyse.

Es darf das kanonische beobachtete Regime nicht überschreiben.

## 28. Partitionierte Berechnung

### 28.1 State-Snapshot-Schema

Der kanonische S5-State-Snapshot erfüllt:

```text
state_schema_id=rcc002.state.s5-regimes
state_schema_version=1.0.0
state_schema_ref=rcc002.state.s5-regimes/1.0.0
```

Der S5-State Snapshot enthält mindestens:

- `state_schema_id`;
- `state_schema_version`;
- `state_schema_ref`;
- `parent_build_id`;
- `market_type`;
- `symbol`;
- `interval`;
- `last_open_time`;
- `market_segment_id`;
- `indicator_segment_id`;
- die letzten 1.440 gültigen SMA200-Kontextwerte oder einen semantisch
  äquivalenten registrierten Rolling State;
- `regime_effective`;
- `regime_candidate`;
- `regime_candidate_count`;
- `regime_model_id`;
- `regime_model_version`;
- `state_payload_sha256`.

### 28.2 State-Feldvertrag

| Feld | Logischer Typ | Nullbar |
|---|---|:---:|
| `state_schema_id` | `Utf8` | Nein |
| `state_schema_version` | `Utf8` | Nein |
| `state_schema_ref` | `Utf8` | Nein |
| `parent_build_id` | `Utf8` | Nein |
| `market_type` | `Utf8` | Nein |
| `symbol` | `Utf8` | Nein |
| `interval` | `Utf8` | Nein |
| `last_open_time` | UTC-Timestamp in Millisekunden | Nein |
| `market_segment_id` | `Utf8` | Nein |
| `indicator_segment_id` | `Utf8` | Nein |
| `sma200_context_state` | registrierter geordneter Float64-State | Nein |
| `regime_effective` | Enum `RegimeState` | Nein |
| `regime_candidate` | Enum `RegimeState` | Nein |
| `regime_candidate_count` | `UInt8` | Nein |
| `regime_model_id` | `Utf8` | Nein |
| `regime_model_version` | `Utf8` | Nein |
| `state_payload_sha256` | 64-stelliger Lowercase-Hex-String | Nein |

Für noch nicht konsolidierte Multi-Provider-Daten enthält der Snapshot
zusätzlich das nicht nullbare Feld `provider`. Seine Anwesenheit MUSS der
Schlüsselvariante des zugehörigen S5-Artefakts entsprechen.

Der konkrete semantische Inhalt von `sma200_context_state` muss vor
`Approved for Implementation` versioniert werden. Er muss die serielle
Slope-Berechnung exakt reproduzieren.

### 28.3 Anschlussprüfung

State darf nur übernommen werden, wenn:

- Parent-Build-ID stimmt,
- Schlüssel unmittelbar anschließt,
- kein Gap vorliegt,
- `market_segment_id` und `indicator_segment_id` unverändert fortgesetzt
  werden,
- Modellversion identisch ist,
- State-Schemaversion kompatibel ist,
- State-Checksumme stimmt.

Andernfalls wird der State verworfen und der vollständige S5-Warm-up neu
begonnen.

### 28.4 Parität

Serielle und partitionierte Berechnung MUST identische diskrete Zustände und
innerhalb der Float-Toleranz identische Slope-Werte erzeugen.

S6 ist zeilenweise und benötigt keinen eigenen rekursiven State Snapshot.
Physische Partitionierung darf seine Ausgaben nicht verändern.

## 29. Historische Revision

Bei einer Änderung von OHLCV-, Indikator- oder Signaldaten:

- Slope wird ab der frühesten betroffenen Abhängigkeit neu berechnet,
- Rohregime wird ab dem ersten betroffenen Zeitpunkt neu berechnet,
- die persistierte State Machine wird ab diesem Punkt bis zum Datensatzende
  neu abgespielt,
- alle abhängigen Gate-Views werden neu erzeugt,
- nachgelagerte Strategie- und Labelartefakte werden invalidiert.

Pfadabhängige Regime dürfen nicht nur lokal zeilenweise korrigiert werden.

## 30. Zeilen- und Dateninvarianten

S5 und S6 dürfen:

- keine Zeile hinzufügen,
- keine Zeile entfernen,
- keine vorgelagerten Werte verändern.

Es muss gelten:

`S5_rows = S4_rows`

`S6_rows = S5_rows`

Alle kanonischen Schlüssel bleiben identisch.

Zusätzlich gilt zeilenweise:

```text
S5.market_segment_id = S4.market_segment_id
S5.indicator_segment_id = S4.indicator_segment_id
S6.market_segment_id = S5.market_segment_id
S6.indicator_segment_id = S5.indicator_segment_id
```

S5 und S6 dürfen weder:

- vorgelagerte Gültigkeitsfelder umdeuten;
- S4-Signalwerte verändern;
- neue Markt- oder Indikatorsegment-IDs erzeugen;
- Regime- oder Gatefelder unter Aliasnamen duplizieren;
- S7-Forward-Returns oder Labels erzeugen.

Eine zeilenweise Reconciliation muss für jedes durchgereichte vorgelagerte
Feld semantische Gleichheit bestätigen.

Dies konkretisiert für S5 und S6 das kanonische Row-Preservation-Prinzip
aus `RCC_002_DATA_PIPELINE_SPECIFICATION` §5.8.

## 31. Testanforderungen für S5

### 31.1 Rohregime-Wahrheitstabelle

Mindestens zu testen:

- Preis über SMA und Slope positiv → Bull,
- Preis unter SMA und Slope negativ → Bear,
- Preis über SMA und Slope null/negativ → Side,
- Preis unter SMA und Slope null/positiv → Side,
- Preis gleich SMA → Side,
- ungültiger Preis, SMA oder Slope → Unknown.

### 31.2 Slope

Tests:

- positiver, negativer und null Slope,
- exakte 1.440-Minuten-Distanz,
- unvollständiger Warm-up,
- Lücke innerhalb des Fensters,
- Segmentwechsel,
- Division durch ungültigen oder nichtpositiven SMA.

### 31.3 State Machine

Mindestens:

- Initialisierung mit drei gleichen Zuständen,
- Candidate-Wechsel vor Bestätigung,
- bestätigter Bull-Side-, Side-Bear- und Bear-Bull-Übergang,
- Unknown-Reset,
- keine rückwirkende Änderung,
- Partitionsgrenze während Candidate Count 1 oder 2.

### 31.4 Kontextzustände

- ADX 15, knapp über 15, 25 und knapp über 25,
- ATR relativ `-1`, `0`, `+1`,
- ungültige Inputs.

### 31.5 S5-Schema- und Gültigkeitstests

Mindestens erforderlich:

- Annahme von `rcc002.stage.s4-signals/1.0.0`;
- Ablehnung unbekannter S4- oder S5-Major-Versionen;
- exakte S5-Spaltenallowlist und Spaltenreihenfolge;
- exakte Typen, Nullbarkeit und Enum-Werte;
- `S5_rows = S4_rows`;
- unveränderte S4-Felder und Primärschlüssel;
- unveränderte `market_segment_id` und `indicator_segment_id`;
- `UNKNOWN` statt eines unzulässigen Regimewerts `INVALID`;
- `regime_valid=false` während unbestätigter Initialisierung;
- feldbezogene Kontextgültigkeit unabhängig von `regime_valid`;
- deterministische S5-Reason-Code-Reihenfolge;
- State-Snapshot-Schema `rcc002.state.s5-regimes/1.0.0`;
- Ablehnung eines inkompatiblen oder nicht anschließenden State Snapshots.

## 32. Testanforderungen für S6

### 32.1 Research Open

- `data_gate_pass=true` → beide erlaubt, `ALLOW_BOTH`, `gate_valid=true`;
- deterministisches `data_gate_pass=false` → beide blockiert, `BLOCK_BOTH`,
  `gate_valid=true`;
- strukturell ungültiger Eingang → Stage-Abbruch, keine S6-Zeile.

### 32.2 Trend Aligned

- Bull → nur Long,
- Bear → nur Short,
- Side → beide blockiert, `BLOCK_BOTH`, `gate_valid=true`,
- Unknown → beide blockiert, `INVALID`, `gate_valid=false`.

### 32.3 Trend Strength Aligned

- Bull + Developing/Strong → nur Long,
- Bear + Developing/Strong → nur Short,
- Bull/Bear + Weak → beide blockiert, `BLOCK_BOTH`, `gate_valid=true`,
- Unknown-Stärke → beide blockiert, `INVALID`, `gate_valid=false`.

### 32.4 Reason Codes

Für jede Wahrheitstabellenzeile werden geprüft:

- Boolean-Ausgaben,
- `gate_state`,
- primärer Reason Code,
- vollständige Reason-Code-Liste.

### 32.5 Richtungsunabhängigkeit

Blockierung einer Richtung darf die Gegenrichtung nur freigeben, wenn deren
eigene Regel vollständig erfüllt ist.

### 32.6 S6-Schema- und Gültigkeitstests

Mindestens erforderlich:

- Annahme von `rcc002.stage.s5-regimes/1.0.0`;
- Ablehnung unbekannter S5- oder S6-Major-Versionen;
- exakte S6-Spaltenallowlist und Spaltenreihenfolge;
- exakte Typen, Nullbarkeit und Gate-State-Enums;
- `S6_rows = S5_rows`;
- unveränderte S5-Felder und Primärschlüssel;
- `data_gate_pass = quality_gate_pass`;
- gültiges `BLOCK_BOTH` bei deterministischem Datenqualitätsfehler;
- `INVALID` ausschließlich bei `gate_valid=false`;
- keine Felder `gate_inputs_valid` oder `gate_reason_mask`;
- profilabhängige statt globale Pflichtinputs;
- `gate_evaluated_at = close_time`;
- deterministische, richtungsgetrennte Reason-Code-Listen;
- keine Long-Codes in der Short-Liste und keine Short-Codes in der
  Long-Liste.

## 33. Kausalitäts-, Paritäts- und Property-Tests

### 33.1 Numerisches Profil

Das normative numerische Profil für S5 lautet:

```text
regime_numeric_profile_id=RCC002_FLOAT64_REGIME_NUMERICS_V1
regime_numeric_profile_version=1.0.0
```

Für unabhängige `Float64`-Vergleiche gelten:

- `absolute_tolerance = 1e-12`;
- `relative_tolerance = 1e-10`.

Der Vergleich erfolgt komponentenweise nach:

```text
abs(a - b) <= absolute_tolerance
               + relative_tolerance * max(abs(a), abs(b))
```

Regime-, Kontext-, Gate-, Gültigkeits- und Reason-Code-Ausgaben müssen exakt
übereinstimmen. Schwellenentscheidungen verwenden ungerundete kanonische
Werte.

### 33.2 Verbindliche Eigenschaften

MUST geprüft werden:

- Änderungen nach `t` verändern S5/S6 bei `t` nicht,
- identische Inputs erzeugen identische Outputs,
- Rohregime ist bei gültigen Inputs exklusiv,
- persistiertes Regime besitzt immer genau einen Zustand,
- Candidate Count ist nie negativ,
- Unknown setzt Candidate State deterministisch zurück,
- fail-closed Daten-Gate erlaubt nie eine Richtung bei fehlgeschlagener
  Datenqualität,
- `gate_valid=false` impliziert `gate_state=INVALID`,
- `gate_state=INVALID` impliziert beide Richtungen `false`,
- `gate_state=BLOCK_BOTH` impliziert `gate_valid=true`,
- Gate-State und beide Richtungs-Booleans erfüllen exakt Abschnitt 18.4,
- jedes S5-Enum enthält ausschließlich registrierte Werte,
- serielle und partitionierte Berechnung stimmen überein.

## 34. Regime- und Gate-Bericht

Der Bericht enthält mindestens:

- Build-, Modell- und Profilversionen,
- S4-, S5- und S6-Schema-IDs und Schema-Fingerprints,
- State-Schema-ID und State-Fingerprint,
- `semantic_build_configuration_sha256`,
- Reason-Code-Registry-Versionen,
- Zeilenzahl und Zeitbereich,
- ersten gültigen Roh- und effektiven Regimezeitpunkt,
- Roh- und Effektivverteilung,
- Übergangsmatrix,
- Anzahl und Dauer der Regimeepisoden,
- Candidate-Abbrüche vor Bestätigung,
- Trendstärkeverteilung je Regime,
- Volatilitätsverteilung je Regime,
- `allow_long`-/`allow_short`-Anteile,
- Blockierungsgründe,
- Unknown- und Warm-up-Anteil,
- Segment-Resets,
- Partitions- und Kausalitätstests,
- Legacy-Vergleich,
- Checksummen.

## 35. Publication Gate S5

S5 darf nur veröffentlicht werden, wenn:

1. S4 freigegeben ist,
2. das Eingangsschema exakt `rcc002.stage.s4-signals/1.0.0` erfüllt,
3. das Ausgangsschema exakt `rcc002.stage.s5-regimes/1.0.0` erfüllt,
4. Regime- und Kontextprofile registriert sind,
5. Slope und Warm-up korrekt sind,
6. Rohregime-Wahrheitstabelle bestanden ist,
7. State-Machine-Tests bestanden sind,
8. `UNKNOWN` und `regime_valid` korrekt gebildet sind,
9. Kontextgültigkeit feldbezogen gebildet ist,
10. keine Lücke oder Segmentgrenze überbrückt wird,
11. State Snapshots `rcc002.state.s5-regimes/1.0.0` erfüllen,
12. S5-Reason Codes ausschließlich aus der registrierten Registry stammen,
13. serielle und partitionierte Berechnung übereinstimmen,
14. Zeilen, Primärschlüssel, Segmente und vorgelagerte Werte unverändert sind,
15. Manifest, State-Schema und Checksummen vollständig sind.

## 36. Publication Gate S6

S6 darf nur veröffentlicht werden, wenn:

1. S5 freigegeben ist,
2. das Eingangsschema exakt `rcc002.stage.s5-regimes/1.0.0` erfüllt,
3. das Ausgangsschema exakt `rcc002.stage.s6-gates/1.0.0` erfüllt,
4. Gate-Profil und Profilversion registriert sind,
5. Daten-Gate fail-closed und exakt nach Abschnitt 13 arbeitet,
6. Long-/Short-Wahrheitstabellen bestanden sind,
7. `gate_valid`, `gate_state` und Richtungs-Booleans konsistent sind,
8. profilabhängige Pflichtinputs korrekt angewandt wurden,
9. Reason Codes vollständig, richtungsgetrennt und deterministisch sind,
10. keine ungültige Zeile eine Richtung erlaubt,
11. Gate-Komposition eindeutig ist,
12. `gate_evaluated_at = close_time` gilt,
13. keine veralteten Aliasfelder enthalten sind,
14. serielle und partitionierte Berechnung übereinstimmen,
15. Zeilen, Primärschlüssel, Segmente und vorgelagerte Werte unverändert sind,
16. Manifest und Checksummen vollständig sind.

Der jeweilige Gate-Status lautet:

- `PASS`,
- `FAIL`,
- `PASS_WITH_APPROVED_EXCEPTIONS`.

`PASS_WITH_APPROVED_EXCEPTIONS` darf ausschließlich nicht blockierende,
vollständig dokumentierte Berichtsbefunde betreffen. Es darf weder einen
Schema-, Enum-, State-, Gültigkeits-, Segment-, Reason-Code- oder
Reconciliation-Fehler noch eine unzulässige Richtungsfreigabe überstimmen.

## 37. Offene Implementierungsparameter

### 37.1 Vor `Approved for Implementation` festzulegen

Folgende semantische oder determinismusrelevante Festlegungen müssen
versioniert vorliegen:

- vollständige maschinenlesbare S5- und S6-Schemas;
- vollständige S5- und S6-Feld-, Enum- und Reason-Code-Register;
- Modell-, Profil-, Schema-, State- und Komponentenregister;
- exakter S5-State-Snapshot-Vertrag einschließlich
  `sma200_context_state`;
- Profilabhängigkeiten jedes Gate-Profils;
- numerisches Determinismusprofil für Slope und Rolling State einschließlich
  Operationsreihenfolge, FMA-Regel, Parallelreduktion, Subnormalwerten und
  Nichtendlichkeitskonvertierung;
- gebundene numerisch wirksame Bibliotheken und Versionen;
- Referenztoleranzen;
- Golden-Fixture-Inhalte und erwartete Resultate;
- Build-Einstiegspunktvertrag;
- Umgebungs- und Lockstrategie;
- S4→S5- und S5→S6-Reconciliation;
- Schema-Kompatibilitäts- und Migrationsregeln;
- Test- und Abnahmekriterien.

Diese Festlegungen gehören zur `semantic_build_configuration`, soweit sie
fachliche Zustände, Gültigkeit, Schema, Profile oder Reproduzierbarkeit
beeinflussen.

### 37.2 Während der Implementierung konkretisierbar

Innerhalb vorher festgelegter physischer Profile dürfen konkretisiert werden:

- physische Partitionsgrößen;
- Parquet-Row-Group-Größen;
- Kompressionsstufe;
- Writeroptimierungen;
- Cache- und temporäre Speicherorte;
- Retentionsparameter temporärer State Snapshots;
- technisch gleichwertige Speicherorte.

Diese Parameter gehören zur `physical_publication_configuration`. Sie dürfen
weder Regime- und Gatewerte noch Gültigkeit, Reason Codes, logische S5-/S6-
Schemas, `build_id` oder `dataset_id` verändern.

Jede spätere Änderung mit Wirkung auf fachliche Semantik, logische Schemas,
Identitätsvorabbildungen oder numerische Determinismusregeln muss die
betroffenen Review-Gates erneut durchlaufen.

## 38. Abnahmekriterien

### 38.1 Spezifikationsreife vor Implementierungsfreigabe

Die Spezifikation ist bereit für `Approved for Implementation`, wenn:

1. alle S4-Eingangs-, S5-Ausgangs- und S6-Ausgangsfelder mit Typ,
   Nullsemantik, Eigentümerstufe und Reihenfolge festgelegt sind;
2. alle Regime-, Kontext- und Gate-Enums eindeutig registriert sind;
3. Roh- und Persistenzregime vollständig spezifiziert sind;
4. `UNKNOWN`, `INVALID`, `BLOCK_BOTH`, `regime_valid` und `gate_valid`
   widerspruchsfrei getrennt sind;
5. Trendstärke und Volatilität richtungsfrei bleiben;
6. alle Gate-Profile und ihre Pflichtinputs getrennt festgelegt sind;
7. State-, Profil-, Schema-, Modell-, Komponenten- und Registry-IDs
   versioniert sind;
8. semantische und physische Konfiguration getrennt sind;
9. Golden-, Unit-, Property-, Schema-, State-, Kausalitäts- und
   Integrationstestverträge vollständig sind;
10. Counterfactual-Evaluationspipeline und Falsifikationskriterien
    spezifiziert sind;
11. Publication Gates und Manifestverträge vollständig sind;
12. Legacy- und Rekonstruktionsprofile strikt vom kanonischen Modell getrennt
    sind;
13. alle vorgeschriebenen internen und externen Review-Gates der
    Spezifikationsbaseline bestanden sind;
14. keine offene Entscheidung fachliche Zustände, Gültigkeit, logische
    Schemas oder Identitätsvorabbildungen verändern kann.

### 38.2 Abnahme der Implementierung

Die spätere Implementierung ist akzeptiert, wenn:

1. Roh- und Persistenzregime vollständig implementiert und getestet sind;
2. alle Gate-Profile getrennt testbar sind;
3. Daten-Gate und profilabhängige Invalidität fail-closed arbeiten;
4. State Snapshot und Partitionsparität bestanden sind;
5. S5-/S6-Schema-, Enum-, Gültigkeits- und Reason-Code-Tests bestanden sind;
6. Legacy-Reproduktion und GS-Rekonstruktionsstatus dokumentiert sind;
7. BTCUSDT-1m-Vollbuild auf der Workstation erfolgreich ist;
8. ein unabhängiger Rebuild mindestens semantische Gleichheit erreicht;
9. keine Zeile und kein vorgelagertes Feld verändert wurde;
10. Manifest, Dataset Lineage und Knowledge Lineage vollständig sind;
11. keine offene kritische Regel-, State- oder Rolleninkonsistenz besteht;
12. die S5- und S6-Publication-Gates automatisiert bestanden sind.

## 39. Freigabe und Aktivierung

### 39.1 Spezifikationsfreigabe

Die technische Spezifikation eines Gate-Profils bedeutet nicht seine
Freigabe für Paper oder Live.

### 39.2 Forschungsstatus

Bis zum Abschluss der Counterfactual- und Out-of-Sample-Validierung gelten:

- `GATE_RESEARCH_OPEN_V1`: kanonische Forschungsbaseline,
- `GATE_TREND_ALIGNED_V1`: Forschungskandidat,
- `GATE_TREND_STRENGTH_ALIGNED_V1`: Forschungskandidat.

### 39.3 Produktive Aktivierung

Eine Aktivierung benötigt:

- präregistrierten Testplan,
- vollständige Vergleichsläufe,
- Scientific Consistency Review,
- Architecture Integrity Review,
- Editorial Pass,
- Internal Certification,
- Claude Independent Architecture Review,
- Gemini Independent Scientific and Adversarial Audit,
- ChatGPT Final Consolidation,
- Status `Baseline V1 Certified`,
- dokumentierte Freigabe,
- versionierte Konfigurationsänderung.

## 40. Freigabestatus und nächster Schritt

`RCC-002-SCR-004` bestätigte die dort geprüften wissenschaftlichen
Korrekturen als geschlossen.

Der vollständige Architecture Integrity Review `RCC-002-AIR-001` bewertete
die Spezifikationsfamilie als:

```text
NOT PASSED – ARCHITECTURE CORRECTIONS REQUIRED
```

Version 0.5.0 bewahrt die AIR-001-Korrekturen aus Version 0.4.0 und
korrigiert zusätzlich:

- `SCR-005-B01` – vollständiger S5-/S6-Schlüssel mit `market_type` und
  `interval`, Multi-Provider-Regel sowie angeglichener State-Vertrag;
- `SCR-005-M01` – getrennte Stage- und State-Schema-IDs, Versionen und
  abgeleitete Referenzen;
- `SCR-005-M02` – einzige normative Wahrheitstabelle für
  `data_gate_pass`, `BLOCK_BOTH`, `INVALID` und Stage-Abbruch.

Sie aktualisiert außerdem die Abhängigkeiten auf:

```text
RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md
Version 0.7.0

RCC_002_DATA_VALIDATION_2026-07-23.md
Version 0.4.0

RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md
Version 0.4.0

RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md
Version 0.4.0
```

Die Befunde sind erst geschlossen, wenn alle abhängigen Spezifikationen
konsistent aktualisiert, neu paketiert und erneut geprüft sind.

Der aktuelle Status lautet:

```text
SCR-005-Corrected Draft – Scientific Consistency Re-Review 006 Pending
```

Nächste vorgeschriebene Schritte:

1. übrige abhängige Spezifikationen korrigieren;
2. vollständige interne Qualitätskontrolle;
3. neues vollständiges Spezifikationspaket;
4. fokussierter Scientific Consistency Re-Review;
5. fokussierter Architecture Integrity Re-Review;
6. Editorial Pass;
7. Internal Certification;
8. Claude Independent Architecture Review;
9. Gemini Independent Scientific and Adversarial Audit;
10. ChatGPT Final Consolidation;
11. `Baseline V1 Certified`;
12. Implementierungsfreigabe.

---

# Eingebettetes Dokument 6 von 7

## Quelldatei: `RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md`

# RCC-002 Label and Forward Return Specification

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Scientific Software Specification |
| Dokument-ID | RCC-002-LF |
| Titel | Label and Forward Return Specification |
| Speicherort im Repository | `docs/specifications/RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md` |
| Dateiname | `RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md` |
| Version | 0.4.1 |
| Datum | 2026-07-23 |
| Status | SCR-005-Corrected Draft – Scientific Consistency Re-Review 006 Pending |
| Übergeordnetes Dokument | `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`, Version 0.7.1 |
| Direkte Abhängigkeiten | `RCC_002_DATA_VALIDATION_2026-07-23.md`, Version 0.4.2; `RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md`, Version 0.4.3; `RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md`, Version 0.4.2; `RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md`, Version 0.5.1 |
| Geltungsbereich | S7_LABELS der RCC-002-Datenpipeline |
| Referenziert durch | Strategieevaluation; ML-Datensätze; Counterfactual Gate Evaluation; Walk-Forward- und Robustheitsanalysen |
| Autoritative Sprache | Englische Feldnamen, Profil-IDs, Horizonte und mathematische Regeln sind normativ; deutsche Erläuterungen präzisieren die Semantik |

### Review-Nachweis

| Prüfung | Status | Ergebnis |
|---|---|---|
| Struktur- und Nummerierungsprüfung | Bestanden | Return-, Excursion-, Direction- und Barrier-Familien vollständig |
| Zeitindexprüfung | Bestanden | Entry-, Exit-, Horizont- und Verfügbarkeitszeitpunkte eindeutig |
| Long-/Short-Vorzeichenprüfung | Bestanden | Positive Werte bedeuten in beiden Richtungen Gewinn |
| Leakage-Prüfung | Bestanden | S7-Felder technisch und semantisch von S0–S6 getrennt |
| Lücken- und Tail-Prüfung | Bestanden | Gap Crossing und unvollständige Zukunftshorizonte ungültig |
| Kostenprüfung | Bestanden | Brutto- und Kostenproxy getrennt; Projektbaseline versioniert |
| Intrabar-Prüfung | Bestanden | Gleichzeitige TP-/SL-Berührung als mehrdeutig markiert |
| Split-Prüfung | Bestanden | Purging und Embargo für überlappende Horizonte definiert |
| Scientific Consistency Review | `RCC-002-SCR-004` bestanden | Die dort geprüften wissenschaftlichen Befunde sind geschlossen; erneuter fokussierter Review nach den semantisch relevanten AIR-001-Korrekturen erforderlich |
| Architecture Integrity Review | `RCC-002-AIR-001` nicht bestanden; Korrektur eingearbeitet | Version 0.3.0 korrigiert die diesem Dokument zugeordneten Teile von `AIR-001-B01`, `AIR-001-B02`, `AIR-001-M01` und `AIR-001-M03`; dokumentübergreifender Re-Review ausstehend |
| Scientific Consistency Re-Review 005 | `RCC-002-SCR-005` nicht bestanden; Korrektur eingearbeitet | Version 0.4.0 korrigiert `SCR-005-M01` und materialisiert `AIR-005-H01`; SCR-006 ausstehend |
| Minor Correction Cycle | `RCC-002-SCR-007-MinFV` umgesetzt | Version 0.4.1, 2026-07-27: Minor correction cycle: version, dependency, terminology, checklist and cross-reference consistency corrections. |
| Editorial Pass | Ausstehend | Nach bestandenem Architecture Integrity Review |
| Internal Certification | Ausstehend | Nach bestandenem Editorial Pass |
| Claude Independent Architecture Review | Ausstehend | Erst nach Internal Certification |
| Gemini Independent Scientific and Adversarial Audit | Ausstehend | Erst nach bestandenem Claude-Review |
| ChatGPT Final Consolidation | Ausstehend | Erst nach abgeschlossenem Gemini-Audit |
| Baseline V1 Certified | Nicht erreicht | Erst nach Schließung aller wesentlichen Befunde |

## 1. Zweck

Dieses Dokument definiert die ausschließlich zukunftsbezogene S7-Stufe der
RCC-002-Datenpipeline.

S7 erzeugt:

- deskriptive Forward Returns,
- ausführungsnahe Return-Proxys,
- getrennte Long-/Short-Ergebnisse,
- Maximum Favorable Excursion und Maximum Adverse Excursion,
- diskrete Richtungslabels,
- optionale Barrier-Labels,
- Label-Gültigkeit und Verfügbarkeitszeitpunkte.

S7 darf keine vorgelagerten Features, Signale, Regime oder Gates verändern.

## 2. Zentrale Sicherheitsgrenze

### 2.1 Einzige zukunftsberechnende Stufe

S7 ist die einzige reguläre RCC-002-Stufe, die Werte nach Zeitpunkt `t`
zur Berechnung einer Zeile `t` verwenden darf.

### 2.2 Verbotene Verwendung

S7-Felder dürfen nicht als Input verwendet werden für:

- S0 bis S6,
- Live- oder Paper-Trading-Entscheidungen,
- Indikatoren,
- Signaltransformationen,
- Regime,
- Gates,
- Feature-Normalisierung,
- Auswahl eines Entry-Signals zum selben historischen Zeitpunkt.

### 2.3 Technische Isolation

S7-Felder müssen:

- eigene Präfixe besitzen,
- in einem registrierten S7-Schema liegen,
- durch S8-Allowlist aus Live-/Paper-Views ausgeschlossen werden,
- bei Schema-Verletzung den Build fail-closed abbrechen.

## 3. Normative Zeitsemantik

### 3.1 Signalzeitpunkt

Zeile `t` beschreibt den Zustand nach dem vollständigen Schluss der Kerze `t`.

### 3.2 Deskriptive Preisreferenz

Close-to-Close-Returns verwenden:

- Startpreis `C_t`,
- Endpreis `C_(t+h)`.

Sie beschreiben Marktbewegung, nicht unmittelbar ausführbare Strategie-PnL.

### 3.3 Ausführungsnahe Preisreferenz

Next-Open-to-Close-Returns verwenden:

- Entry-Preisproxy `O_(t+1)`,
- Exit-Preisproxy `C_(t+h)`.

Für `h = 1`:

- Entry `O_(t+1)`,
- Exit `C_(t+1)`.

### 3.4 Horizont

`h` bezeichnet die Anzahl 1-Minuten-Intervalle nach der Signalkerze.

Der Horizon-Endpunkt ist:

`t + h`

### 3.5 Label-Verfügbarkeit

Ein Label mit Horizont `h` ist frühestens verfügbar, nachdem Kerze `t+h`
vollständig geschlossen und validiert wurde.

Mindestfeld:

`label_available_at_h = close_time_(t+h)`

Ein Trainings- oder Evaluationsprozess darf das Label vorher nicht als bekannt
behandeln.

## 4. Horizon-Registry

### 4.1 Kanonische Horizonte

Das allein verbindliche Register lautet:

```text
horizon_registry_id=RCC002_FORWARD_HORIZONS_V1
horizon_registry_version=1.0.0
```

Es enthält:

| ID | Minuten | Fachlicher Kontext |
|---|---:|---|
| `H001` | 1 | unmittelbar nächste Kerze |
| `H005` | 5 | sehr kurzfristig |
| `H015` | 15 | kurzfristig |
| `H060` | 60 | eine Stunde |
| `H240` | 240 | vier Stunden |
| `H1440` | 1.440 | ein Tag |

Die zugehörigen Suffixe lauten exakt:

| Horizon-ID | Feldsuffix |
|---|---|
| `H001` | `_h001` |
| `H005` | `_h005` |
| `H015` | `_h015` |
| `H060` | `_h060` |
| `H240` | `_h240` |
| `H1440` | `_h1440` |

Ein 30-Minuten-Horizont gehört nicht zu Version `1.0.0`.

### 4.2 Erweiterung

Weitere Horizonte benötigen:

- registrierte Horizon-ID,
- exakte Intervalldefinition,
- neue Horizon-Registry-Version,
- aktualisierte Schema- und Labelprofilversion,
- Tests,
- erneuten Scientific Consistency Review,
- erneuten Architecture Integrity Review,
- dokumentierte Rebuild-Auswirkung.

### 4.3 Kein implizites Resampling

Ein Horizont von 60 Minuten bedeutet nicht automatisch eine 1h-OHLC-Kerze.

Er bezeichnet in dieser Spezifikation 60 aufeinanderfolgende 1-Minuten-
Intervalle auf der kanonischen 1m-Zeitachse.

## 5. Eingabevertrag

### 5.1 Eingangsschema

S7 akzeptiert ausschließlich:

```text
rcc002.stage.s6-gates/1.0.0
```

Eine unbekannte oder inkompatible Major-Version ist fail-closed abzulehnen.
Eine kompatible Minor-Version darf nur über eine registrierte
Kompatibilitätsregel akzeptiert werden.

S7 erzeugt:

```text
rcc002.stage.s7-labels/1.0.0
```

### 5.2 Pflichtfelder

S7 konsumiert aus dem S6-Eingang mindestens:

| Feld | Logischer Typ | Eigentümerstufe | Verwendung in S7 |
|---|---|---|---|
| `market_type` | `Utf8` | `S1_NORMALIZED` | Primärschlüssel und Marktidentität |
| `symbol` | `Utf8` | `S1_NORMALIZED` | Primärschlüssel und Marktidentität |
| `interval` | `Utf8` | `S1_NORMALIZED` | Primärschlüssel und Horizon-Interpretation |
| `open_time` | UTC-Timestamp in Millisekunden | `S1_NORMALIZED` | Primärschlüssel und Signalzeitpunkt |
| `close_time` | UTC-Timestamp in Millisekunden | `S1_NORMALIZED` | Verfügbarkeitszeitpunkt der Signalkerze |
| `open` | `Float64` | `S1_NORMALIZED` | Next-Open-Entry und Barrier-Suche |
| `high` | `Float64` | `S1_NORMALIZED` | MFE und Barrier-Suche |
| `low` | `Float64` | `S1_NORMALIZED` | MAE und Barrier-Suche |
| `close` | `Float64` | `S1_NORMALIZED` | Close-to-Close und Horizon-Exit |
| `market_segment_id` | `Utf8` | `S2_VALIDATED` | verbindliche Grenze jedes Zukunftsfensters |
| `quality_is_observed` | `Boolean` | `S2_VALIDATED` | Ausschluss nicht beobachteter Bars |
| `quality_is_synthetic` | `Boolean` | `S2_VALIDATED` | Ausschluss synthetischer Bars |
| `quality_timestamp_valid` | `Boolean` | `S2_VALIDATED` | Zeitachsenvalidität |
| `quality_ohlc_valid` | `Boolean` | `S2_VALIDATED` | OHLC-Gültigkeit |
| `quality_market_values_valid` | `Boolean` | `S2_VALIDATED` | Marktwertgültigkeit |
| `quality_gate_pass` | `Boolean` | `S2_VALIDATED` | kanonische Datenfreigabe |
| `quality_reason_codes` | geordnete Liste `Utf8` | `S2_VALIDATED` | Lineage und Invaliditätsdiagnose |
| `quality_rule_version` | `Utf8` | `S2_VALIDATED` | verwendetes Qualitätsregelwerk |
| `gate_schema_id` | `Utf8` | `S6_GATES` | Eingangsschemaidentität |
| `gate_schema_version` | `Utf8` | `S6_GATES` | Eingangsschemaversion |
| `gate_schema_ref` | `Utf8` | `S6_GATES` | Qualifizierte Eingangsschemareferenz |

Der vollständige Eingang bleibt das registrierte S6-Schema. Die Tabelle
benennt die S7-fachlich benötigte Teilmenge und erlaubt nicht, den übrigen
S6-Vertrag zu entfernen oder umzudeuten.

### 5.3 Eingabeinvarianten

Vor S7 müssen gelten:

- S6 ist freigegeben,
- `gate_schema_id=rcc002.stage.s6-gates`,
- `gate_schema_version=1.0.0`,
- Zeilen sind streng zeitlich sortiert,
- Schlüssel sind eindeutig,
- der kanonische Schlüssel
  `(market_type, symbol, interval, open_time)` ist vollständig,
- bei unkonsolidierten Multi-Provider-Daten ist zusätzlich `provider`
  unmittelbar vor `market_type` im Schlüssel und in der Sortierreihenfolge
  enthalten,
- `interval=1m`,
- Segmentgrenzen sind bekannt,
- S0-bis-S6-Felder entsprechen ihren registrierten Eigentümerstufen,
- keine unbekannten Felder werden stillschweigend als S7-Input interpretiert.

Die Gültigkeit jeder einzelnen Zukunftskerze wird anschließend
familienbezogen geprüft. Eine ungültige Zukunftskerze darf nicht durch eine
gültige Signalkerze überstimmt werden.

### 5.4 Segmentvertrag

Für alle kanonischen S7-Familien ist `market_segment_id` aus S2 die
verbindliche zeitliche Marktsegmentgrenze.

`indicator_segment_id` aus S3 darf:

- für nachgelagerte Featureanalysen durchgereicht werden,
- nicht die S7-Marktsegmentgrenze ersetzen,
- nicht verwendet werden, um ein Zukunftsfenster über eine
  `market_segment_id`-Grenze zu erlauben.

Ein gültiges Zukunftsfenster benötigt für jede Bar von der Signalkerze `t`
bis zur letzten von der Familie verwendeten Zukunftskerze dieselbe
`market_segment_id`.

### 5.5 Qualitätsvertrag

Für jede von einer Label-Familie verwendete Preiszeile muss gelten:

```text
quality_gate_pass = true
quality_is_observed = true
quality_is_synthetic = false
quality_timestamp_valid = true
quality_ohlc_valid = true
quality_market_values_valid = true
```

Die S7-Stufe darf `quality_gate_pass` weder neu bilden noch überstimmen.

Ein qualitätsbedingt ungültiges Zukunftsfenster erzeugt:

- null in allen betroffenen numerischen S7-Feldern,
- `INVALID` in betroffenen Barrier-Outcome-Feldern,
- `*_valid_h=false`,
- mindestens einen passenden registrierten Reason Code.

### 5.6 Feature-Unabhängigkeit

Forward Returns werden ausschließlich aus Preis- und Qualitätsfeldern
berechnet.

Sie dürfen nicht von:

- aktuellem Signal,
- Regime,
- Gate,
- späterem Trade

abhängen. Diese Felder dienen erst nachgelagerten Gruppierungen.

## 6. Gemeinsame Return-Konvention

### 6.1 Long

Für Entry `P_entry` und Exit `P_exit`:

`long_return = P_exit / P_entry - 1`

### 6.2 Short

Für ein linear abgerechnetes Short-Exposure:

`short_return = (P_entry - P_exit) / P_entry`

Damit:

`short_return = -long_return`

bei identischen Entry-/Exit-Preisen und vor Kosten.

### 6.3 Vorzeichen

Für beide Richtungen gilt:

- positiver Return = Gewinn,
- null = unverändert,
- negativer Return = Verlust.

### 6.4 Prozentdarstellung

Kanonische Return-Felder werden als Dezimalbruch gespeichert:

- `0.01` = 1 %,
- `-0.02` = -2 %.

Berichte dürfen zusätzlich Prozentwerte anzeigen, aber nicht anstelle der
kanonischen Dezimalwerte speichern.

## 7. Close-to-Close Forward Returns

### 7.1 Long

Für jeden Horizont `h`:

`fwd_cc_long_ret_h_t = C_(t+h) / C_t - 1`

### 7.2 Short

`fwd_cc_short_ret_h_t = (C_t - C_(t+h)) / C_t`

Damit:

`fwd_cc_short_ret_h_t = -fwd_cc_long_ret_h_t`

### 7.3 Log Return

Optionaler deskriptiver Log Return:

`fwd_cc_log_ret_h_t = log(C_(t+h) / C_t)`

Für eine Short-Richtung:

`fwd_cc_short_log_ret_h_t = -fwd_cc_log_ret_h_t`

### 7.4 Verwendung

Close-to-Close-Returns eignen sich für:

- deskriptive Marktanalysen,
- Signal-Outcome-Analysen,
- richtungsneutrale Vergleichsforschung.

Sie sind kein unmittelbarer Execution-Return.

## 8. Next-Open-to-Close Forward Returns

### 8.1 Long

`fwd_noc_long_ret_h_t = C_(t+h) / O_(t+1) - 1`

### 8.2 Short

`fwd_noc_short_ret_h_t = (O_(t+1) - C_(t+h)) / O_(t+1)`

### 8.3 Gültigkeit

Erforderlich sind:

- Kerze `t+1` vollständig vorhanden,
- Kerze `t+h` vollständig vorhanden,
- alle Kerzen von `t+1` bis `t+h` im selben gültigen Segment.

### 8.4 Interpretation

Dieses Label ist ein ausführungsnaher Preisproxy, aber keine vollständige
Orderausführungssimulation.

Es modelliert nicht:

- Intrabar-Latenz,
- Orderbuchtiefe,
- Partial Fills,
- variable Slippage,
- Funding,
- Liquidation,
- Positionsgrößenwirkung.

## 9. Kostenprofile

### 9.1 Brutto zuerst

Bruttoreturns bleiben immer erhalten.

Kostenbereinigte Felder werden zusätzlich erzeugt und dürfen Bruttowerte nicht
überschreiben.

### 9.2 Projekt-Baseline

`COST_PROXY_FEE_RT_0004_V1`:

- `fee_roundtrip = 0.0004`,
- `slippage_roundtrip = 0`,
- `total_cost_fraction = 0.0004`.

Dies entspricht der aktuellen Projektbaseline von 0,04 % Roundtrip-Fee.

### 9.3 Konfigurierbares Slippage-Profil

Zusätzliche Profile dürfen definieren:

- Entry-Slippage,
- Exit-Slippage,
- Roundtrip-Slippage,
- asymmetrische Long-/Short-Kosten.

Jedes Profil benötigt eine eigene ID und Version.

### 9.4 Linearer Kostenproxy

Für beide Richtungen:

`net_proxy_return = gross_return - total_cost_fraction`

Feldnamen müssen `net_proxy` enthalten.

### 9.5 Einschränkung

Der lineare Kostenproxy ist keine exakte Börsenabrechnung.

Er dient:

- konsistenten Sensitivitätsanalysen,
- Vergleich mit der bestehenden Fee-Konvention,
- Vorfilterung offensichtlich zu kleiner Bruttoeffekte.

Backtests und Execution Layer bleiben für reale Kostenmodellierung
autoritativ.

## 10. Forward Excursions

### 10.1 Zukunftsfenster

Für Next-Open-Entry und Horizont `h`:

`future_window_h = [t+1, ..., t+h]`

Entry:

`P_entry = O_(t+1)`

### 10.2 Long MFE

`fwd_long_mfe_h_t = max(H_i, i=t+1...t+h) / P_entry - 1`

### 10.3 Long MAE

`fwd_long_mae_h_t = min(L_i, i=t+1...t+h) / P_entry - 1`

Wegen `L_(t+1) <= O_(t+1)` gilt:

`fwd_long_mae_h_t <= 0`

### 10.4 Short MFE

`fwd_short_mfe_h_t = (P_entry - min(L_i, i=t+1...t+h)) / P_entry`

### 10.5 Short MAE

`fwd_short_mae_h_t = (P_entry - max(H_i, i=t+1...t+h)) / P_entry`

Wegen `H_(t+1) >= O_(t+1)` gilt:

`fwd_short_mae_h_t <= 0`

Entsprechend gilt für gültige Fenster:

- `fwd_long_mfe_h_t >= 0`,
- `fwd_short_mfe_h_t >= 0`.

### 10.6 Zeit bis Extrem

Zusätzlich:

- `fwd_long_mfe_first_bar_h`,
- `fwd_long_mae_first_bar_h`,
- `fwd_short_mfe_first_bar_h`,
- `fwd_short_mae_first_bar_h`.

Bei mehrfach identischem Extrem wird der erste auftretende Bar-Offset
gespeichert.

Der erste zukünftige Bar besitzt Offset `1`.

## 11. Richtungslabels

### 11.1 Bruttolabel

Für einen Return `r`:

- `+1`, wenn `r > 0`,
- `0`, wenn `r = 0`,
- `-1`, wenn `r < 0`.

Felder:

- `label_cc_long_direction_h`,
- `label_cc_short_direction_h`,
- `label_noc_long_direction_h`,
- `label_noc_short_direction_h`.

### 11.2 Kostenbereinigtes Label

Auf dem Net-Proxy-Return:

- `+1`, wenn `net_proxy_return > 0`,
- `0`, wenn `net_proxy_return = 0`,
- `-1`, wenn `net_proxy_return < 0`.

### 11.3 Kein globaler Deadband

RCC-002 verwendet keinen undokumentierten neutralen Toleranzbereich um null.

Ein Deadband darf als eigenes Profil eingeführt werden, wenn:

- Schwelle präregistriert ist,
- Kostenbezug dokumentiert ist,
- Robustheit separat getestet wird.

## 12. Quantitative Return-Buckets

### 12.1 Zweck

Quantile oder feste Return-Buckets dürfen für Analyse und ML erzeugt werden,
aber nicht implizit aus dem gesamten Datensatz gelernt werden.

### 12.2 Feste Buckets

Ein festes Bucket-Profil benötigt:

- explizite Grenzen,
- Richtung,
- Return-Familie,
- Horizont,
- Kostenprofil.

### 12.3 Datengetriebene Buckets

Quantilgrenzen dürfen ausschließlich auf dem Trainingszeitraum bestimmt
werden.

Dieselben gespeicherten Grenzen werden unverändert auf Validierung und Test
angewandt.

Die Verwendung vollständiger Datensatzquantile ist Leakage.

## 13. Barrier-Label-Grundmodell

### 13.1 Parameter

Ein Barrier-Profil definiert:

- Entry-Preisreferenz,
- Take-Profit-Distanz,
- Stop-Loss-Distanz,
- maximalen Horizont,
- Long-/Short-Richtung,
- Intrabar-Ambiguitätsregel,
- Kostenprofil.

### 13.2 Long-Barrieren

Bei Entry `P_entry`:

`long_tp_price = P_entry * (1 + tp_fraction)`

`long_sl_price = P_entry * (1 - sl_fraction)`

### 13.3 Short-Barrieren

`short_tp_price = P_entry * (1 - tp_fraction)`

`short_sl_price = P_entry * (1 + sl_fraction)`

### 13.4 Ereignisse

Zulässige Outcomes:

- `TP_FIRST`,
- `SL_FIRST`,
- `TIMEOUT`,
- `AMBIGUOUS_BOTH_HIT`,
- `INVALID`.

## 14. Intrabar-Ambiguität

### 14.1 Problem

Mit OHLC-Daten ist die Reihenfolge von High und Low innerhalb derselben Kerze
nicht bekannt.

Wenn in derselben 1m-Kerze sowohl TP als auch SL berührt werden, kann nicht
bestimmt werden, welche Barriere zuerst erreicht wurde.

### 14.2 Kanonische Regel

Der kanonische Barrier-Outcome lautet:

`AMBIGUOUS_BOTH_HIT`

Die Beobachtung darf nicht automatisch als Gewinn oder Verlust klassifiziert
werden.

### 14.3 Sensitivitätsprofile

Zusätzliche Analyseprofile dürfen berechnen:

- `PESSIMISTIC_SL_FIRST`,
- `OPTIMISTIC_TP_FIRST`.

Diese Ergebnisse bleiben getrennt und dürfen den kanonischen Ambiguous-Status
nicht überschreiben.

### 14.4 Keine zufällige Reihenfolge

Eine zufällige TP-/SL-Reihenfolge ist im kanonischen Build unzulässig.

## 15. L1-Vergleichsprofil

### 15.1 Profil-ID

`L1_BARRIER_TP050_SL020_V1`

### 15.2 Parameter

- Entry-Proxy: `O_(t+1)`,
- TP: `0.05`,
- SL: `0.02`,
- Richtung: Long und Short getrennt,
- maximale Horizonte aus der registrierten Horizon-Liste,
- Intrabar-Regel: `AMBIGUOUS_BOTH_HIT`.

### 15.3 Status

Dieses Profil dient dem Vergleich mit der bestehenden L1-Baseline.

Es ersetzt nicht:

- den tatsächlichen L1-Execution Layer,
- signalabhängige Exits,
- Short-Time-Stop,
- Gebührenberechnung im Backtest.

### 15.4 Short-Time-Stop

Der bestehende Short-Time-Stop von 60 Minuten ist eine Execution-Regel und
wird nicht still in das allgemeine Barrier-Profil integriert.

Ein separates Labelprofil darf später den 60-Minuten-Short-Timeout exakt
modellieren.

## 16. Barrier-Suche

### 16.1 Reihenfolge über Kerzen

Kerzen werden chronologisch von `t+1` bis `t+h` geprüft.

### 16.2 Open-Gap-Priorität

Der Open-Preis einer Kerze ist zeitlich vor deren unbekannter Intrabar-
High-/Low-Reihenfolge beobachtbar.

Deshalb wird pro Zukunftskerze zuerst geprüft:

- Long: `open >= long_tp_price` oder `open <= long_sl_price`,
- Short: `open <= short_tp_price` oder `open >= short_sl_price`.

Wird eine Barriere bereits durch den Open-Preis überschritten, gilt diese
Barriere als zuerst getroffen. Erst wenn der Open-Preis zwischen beiden
Barrieren liegt, werden High und Low geprüft.

### 16.3 Erster eindeutiger Treffer

- Nur TP in einer Kerze berührt → `TP_FIRST`.
- Nur SL in einer Kerze berührt → `SL_FIRST`.
- Beide in derselben ersten Trefferkerze → `AMBIGUOUS_BOTH_HIT`.
- Keine Barriere bis Horizontende → `TIMEOUT`.

Die Ambiguitätsregel gilt nur, wenn der Open-Preis keine Barriere bereits
eindeutig ausgelöst hat.

### 16.4 Treffer-Offsets

Gespeichert werden:

- richtungs- und profilspezifisches `barrier_*_first_hit_bar_*_h`,
- richtungs- und profilspezifisches `barrier_*_first_hit_time_*_h`,
- richtungs- und profilspezifisches `barrier_*_outcome_*_h`.

Offset `1` bezeichnet Kerze `t+1`.

Die exakten kanonischen Feldschablonen stehen in Abschnitt 20.8.

## 17. Gültigkeit eines Forward Labels

### 17.1 Vollständiger Horizont

Ein Label ist nur gültig, wenn alle erforderlichen Kerzen bis `t+h`
vorhanden und validiert sind.

### 17.2 Segmentregel

Signalkerze, Entry-Kerze und alle Zukunftskerzen müssen zum selben
beobachteten Segment gehören.

### 17.3 Lücken

Überschreitet ein Zukunftsfenster eine Lücke:

- Return ungültig,
- Excursion ungültig,
- Direction Label ungültig,
- Barrier Label `INVALID`.

Reason Code:

`LBL_WINDOW_CROSSES_MARKET_SEGMENT`

### 17.4 Tail

Für die letzten `h` Zeilen eines Datensatzes fehlen regulär vollständige
Zukunftsdaten.

Diese Werte sind ungültig mit:

`LBL_FUTURE_HORIZON_INCOMPLETE`

Diese Zeilen werden nicht entfernt und nicht durch synthetische Ersatzzeilen
ersetzt; die betroffenen Feldwerte folgen der Nullsemantik aus §18.3.

### 17.5 Synthetische Kerzen

Kanonische Labels dürfen keine synthetischen Zukunftskerzen verwenden.

Ein separates Sensitivitätsprofil benötigt eine eigene Labelprofil-ID.

## 18. Label-Validitätsfelder

### 18.1 Familienbezogene Gültigkeit

Für jeden registrierten Horizont werden exakt folgende
Gültigkeitsfeldschablonen expandiert:

| Feldschablone | Logischer Typ | Nullbar | Bedeutung |
|---|---|:---:|---|
| `fwd_cc_valid_h` | `Boolean` | Nein | Gültigkeit der Close-to-Close-Familie |
| `fwd_cc_reason_codes_h` | geordnete Liste `Utf8` | Nein | Gründe der Close-to-Close-Familie |
| `fwd_cc_label_segment_id_h` | `Utf8` | Ja | bestätigte Segmentidentität des CC-Fensters |
| `fwd_noc_valid_h` | `Boolean` | Nein | Gültigkeit der Next-Open-to-Close-Familie |
| `fwd_noc_reason_codes_h` | geordnete Liste `Utf8` | Nein | Gründe der NOC-Familie |
| `fwd_noc_label_segment_id_h` | `Utf8` | Ja | bestätigte Segmentidentität des NOC-Fensters |
| `fwd_excursion_valid_h` | `Boolean` | Nein | Gültigkeit der Excursion-Familie |
| `fwd_excursion_reason_codes_h` | geordnete Liste `Utf8` | Nein | Gründe der Excursion-Familie |
| `fwd_excursion_label_segment_id_h` | `Utf8` | Ja | bestätigte Segmentidentität des Excursion-Fensters |
| `label_cc_direction_valid_h` | `Boolean` | Nein | Gültigkeit der CC-Richtungslabels |
| `label_cc_direction_reason_codes_h` | geordnete Liste `Utf8` | Nein | Gründe der CC-Richtungslabels |
| `label_cc_direction_segment_id_h` | `Utf8` | Ja | bestätigte Segmentidentität der CC-Richtungslabels |
| `label_noc_direction_valid_h` | `Boolean` | Nein | Gültigkeit der NOC- und Net-Proxy-Richtungslabels |
| `label_noc_direction_reason_codes_h` | geordnete Liste `Utf8` | Nein | Gründe der NOC-Richtungslabels |
| `label_noc_direction_segment_id_h` | `Utf8` | Ja | bestätigte Segmentidentität der NOC-Richtungslabels |
| `barrier_valid_h` | `Boolean` | Nein | Gültigkeit der Long-/Short-Barrier-Familie |
| `barrier_reason_codes_h` | geordnete Liste `Utf8` | Nein | Gründe der Barrier-Familie |
| `barrier_label_segment_id_h` | `Utf8` | Ja | bestätigte Segmentidentität des Barrier-Fensters |

Der abschließende Platzhalter `_h` wird ausschließlich durch einen Suffix
aus Abschnitt 4.1 ersetzt.

Beispiel:

```text
fwd_cc_valid_h060
fwd_cc_reason_codes_h060
fwd_cc_label_segment_id_h060
```

### 18.2 Gemeinsame Horizon-Metadaten

Für jeden Horizont werden außerdem erzeugt:

| Feldschablone | Logischer Typ | Nullbar | Bedeutung |
|---|---|:---:|---|
| `label_horizon_bars_h` | `UInt16` | Nein | registrierte Zahl der 1m-Intervalle |
| `label_available_at_h` | UTC-Timestamp in Millisekunden | Ja | frühester Zeitpunkt, zu dem Ergebnis oder Invalidität vollständig bestimmbar ist |

Für ein vollständiges Horizon-Ende gilt:

```text
label_available_at_h = close_time_(t+h)
```

Bei `LBL_FUTURE_HORIZON_INCOMPLETE` gilt:

```text
label_available_at_h = null
```

### 18.3 Nullsemantik

Wenn ein familienbezogenes `*_valid_h=false` ist:

- alle numerischen Felder dieser Familie und dieses Horizonts sind `null`;
- alle diskreten Richtungsfelder dieser Familie und dieses Horizonts sind
  `null`;
- Barrier-Outcomes lauten `INVALID`;
- Barrier-Trefferbar und -zeit sind `null`;
- die zugehörige Reason-Code-Liste enthält mindestens einen invalidierenden
  Code;
- die familienbezogene Segment-ID ist `null`, wenn keine einzige gültige
  Segmentidentität für das vollständige Fenster bestätigt werden kann.

Ein globales `label_valid` oder `label_valid_h` ist unzulässig, weil es
unterschiedliche Familienvoraussetzungen verdecken würde.

### 18.4 Reason-Code-Listen

Alle familienbezogenen Reason-Code-Listen sind:

- nicht null;
- frei von Duplikaten;
- nach aufsteigender Registry-Priorität sortiert;
- bei fehlenden Codes als leere Liste serialisiert.

## 19. Reason Codes

### 19.1 Registry-Identität

```text
label_reason_code_registry_version=1.0.0
```

### 19.2 Verbindliches Register

| Priorität | Code | Ebene oder Familie | Wirkung |
|---:|---|---|---|
| 10 | `LBL_SCHEMA_MISMATCH` | Stufe | Buildabbruch |
| 20 | `LBL_PROFILE_MISMATCH` | Stufe | Buildabbruch |
| 30 | `LBL_HORIZON_PROFILE_UNKNOWN` | Stufe | Buildabbruch |
| 40 | `LBL_COST_PROFILE_UNKNOWN` | Stufe | Buildabbruch |
| 50 | `LBL_BARRIER_PROFILE_UNKNOWN` | Stufe | Buildabbruch |
| 60 | `LBL_INTERVAL_UNSUPPORTED` | Stufe | Buildabbruch |
| 100 | `LBL_INPUT_INVALID` | alle | invalidierend |
| 110 | `LBL_FUTURE_HORIZON_INCOMPLETE` | alle | invalidierend |
| 120 | `LBL_WINDOW_CROSSES_MARKET_SEGMENT` | alle | invalidierend |
| 130 | `LBL_FUTURE_BAR_QUALITY_FAILED` | alle | invalidierend |
| 140 | `LBL_SYNTHETIC_INPUT_DISALLOWED` | alle | invalidierend |
| 150 | `LBL_ENTRY_PRICE_INVALID` | NOC, Excursion, Direction, Barrier | invalidierend |
| 160 | `LBL_EXIT_PRICE_INVALID` | CC, NOC, Direction | invalidierend |
| 170 | `LBL_NONFINITE_RESULT` | numerische Familien | invalidierend |
| 180 | `LBL_BARRIER_BOTH_HIT` | Barrier | gültiger Informationscode |
| 190 | `LBL_BARRIER_TIMEOUT` | Barrier | gültiger Informationscode |

`LBL_WINDOW_CROSSES_GAP` ist ein historischer Alias und im kanonischen
Schema `rcc002.stage.s7-labels/1.0.0` nicht zulässig. Die kanonische
Segmentverletzung lautet `LBL_WINDOW_CROSSES_MARKET_SEGMENT`.

### 19.3 Bildung

Stageweite Profil- oder Schemafehler erzeugen kein teilweise veröffentlichtes
S7-Zeilenartefakt.

Zeilenbezogene Reason Codes werden familien- und horizonspezifisch gebildet.
Alle sicher feststellbaren Gründe bleiben erhalten, soweit ihre Ermittlung
keine fachliche Auswertung auf ungültigen Werten erfordert.

Bei einer unvollständigen Zukunft gilt ausschließlich:

```text
LBL_FUTURE_HORIZON_INCOMPLETE
```

für die wegen des fehlenden Endes nicht auswertbaren Familien.

Bei einer vorhandenen, aber segmentüberschreitenden Zukunft gilt:

```text
LBL_WINDOW_CROSSES_MARKET_SEGMENT
```

Qualitäts- und Synthetic-Codes dürfen zusätzlich aufgenommen werden, wenn die
betroffene Bar sicher bestimmbar ist.

`LBL_BARRIER_BOTH_HIT` und `LBL_BARRIER_TIMEOUT` sind mit
`barrier_valid_h=true` vereinbar.

## 20. Feldbenennung

### 20.1 Horizontsuffix

Horizonte verwenden das Registry-Suffix:

- `_h001`,
- `_h005`,
- `_h015`,
- `_h060`,
- `_h240`,
- `_h1440`.

### 20.2 Beispiele

- `fwd_cc_long_ret_h060`,
- `fwd_cc_short_ret_h060`,
- `fwd_noc_long_ret_h060`,
- `fwd_noc_short_ret_h060`,
- `fwd_noc_long_net_proxy_fee_rt_0004_h060`,
- `fwd_long_mfe_h060`,
- `fwd_long_mae_h060`,
- `label_noc_long_direction_h060`,
- `barrier_long_outcome_tp050_sl020_h060`.

### 20.3 Präfixschutz

Nur S7 darf regulär Felder mit folgenden Präfixen erzeugen:

- `fwd_`,
- `label_`,
- `barrier_`.

Diese Präfixregel ist eine zusätzliche Schutzschicht. Die autoritative
Leakage-Klassifikation entsteht aus:

```text
field_owner_stage=S7_LABELS
```

Ein S7-Feld bleibt unabhängig von seinem Namen ein S7-Feld.

### 20.4 Kanonische Basisfelder

Die nicht horizonspezifischen S7-Basisfelder lauten exakt:

| Feld | Logischer Typ | Nullbar | Eigentümer |
|---|---|:---:|---|
| `label_profile_id` | `Utf8` | Nein | `S7_LABELS` |
| `label_profile_version` | `Utf8` | Nein | `S7_LABELS` |
| `label_schema_id` | `Utf8` | Nein | `S7_LABELS` |
| `label_schema_version` | `Utf8` | Nein | `S7_LABELS` |
| `label_schema_ref` | `Utf8` | Nein | `S7_LABELS` |
| `horizon_registry_id` | `Utf8` | Nein | `S7_LABELS` |
| `horizon_registry_version` | `Utf8` | Nein | `S7_LABELS` |
| `cost_profile_id` | `Utf8` | Nein | `S7_LABELS` |
| `cost_profile_version` | `Utf8` | Nein | `S7_LABELS` |
| `barrier_profile_id` | `Utf8` | Nein | `S7_LABELS` |
| `barrier_profile_version` | `Utf8` | Nein | `S7_LABELS` |
| `label_reason_code_registry_version` | `Utf8` | Nein | `S7_LABELS` |
| `label_numeric_profile_id` | `Utf8` | Nein | `S7_LABELS` |
| `label_numeric_profile_version` | `Utf8` | Nein | `S7_LABELS` |

### 20.5 Return-Feldschablonen

Für jeden registrierten Horizont werden exakt erzeugt:

| Feldschablone | Logischer Typ | Nullbar |
|---|---|:---:|
| `fwd_cc_long_ret_h` | `Float64` | Ja |
| `fwd_cc_short_ret_h` | `Float64` | Ja |
| `fwd_cc_log_ret_h` | `Float64` | Ja |
| `fwd_cc_short_log_ret_h` | `Float64` | Ja |
| `fwd_noc_long_ret_h` | `Float64` | Ja |
| `fwd_noc_short_ret_h` | `Float64` | Ja |
| `fwd_noc_long_net_proxy_fee_rt_0004_h` | `Float64` | Ja |
| `fwd_noc_short_net_proxy_fee_rt_0004_h` | `Float64` | Ja |

### 20.6 Excursion-Feldschablonen

| Feldschablone | Logischer Typ | Nullbar |
|---|---|:---:|
| `fwd_long_mfe_h` | `Float64` | Ja |
| `fwd_long_mae_h` | `Float64` | Ja |
| `fwd_short_mfe_h` | `Float64` | Ja |
| `fwd_short_mae_h` | `Float64` | Ja |
| `fwd_long_mfe_first_bar_h` | `UInt16` | Ja |
| `fwd_long_mae_first_bar_h` | `UInt16` | Ja |
| `fwd_short_mfe_first_bar_h` | `UInt16` | Ja |
| `fwd_short_mae_first_bar_h` | `UInt16` | Ja |

### 20.7 Richtungslabel-Feldschablonen

| Feldschablone | Logischer Typ | Nullbar |
|---|---|:---:|
| `label_cc_long_direction_h` | `Int8` | Ja |
| `label_cc_short_direction_h` | `Int8` | Ja |
| `label_noc_long_direction_h` | `Int8` | Ja |
| `label_noc_short_direction_h` | `Int8` | Ja |
| `label_noc_long_net_proxy_fee_rt_0004_direction_h` | `Int8` | Ja |
| `label_noc_short_net_proxy_fee_rt_0004_direction_h` | `Int8` | Ja |

Zulässige gültige Werte sind ausschließlich:

```text
-1
0
1
```

### 20.8 Barrier-Feldschablonen

| Feldschablone | Logischer Typ | Nullbar |
|---|---|:---:|
| `barrier_long_outcome_tp050_sl020_h` | Enum `BarrierOutcome` | Nein |
| `barrier_short_outcome_tp050_sl020_h` | Enum `BarrierOutcome` | Nein |
| `barrier_long_first_hit_bar_tp050_sl020_h` | `UInt16` | Ja |
| `barrier_short_first_hit_bar_tp050_sl020_h` | `UInt16` | Ja |
| `barrier_long_first_hit_time_tp050_sl020_h` | UTC-Timestamp in Millisekunden | Ja |
| `barrier_short_first_hit_time_tp050_sl020_h` | UTC-Timestamp in Millisekunden | Ja |

`BarrierOutcome` verwendet ausschließlich:

```text
TP_FIRST
SL_FIRST
TIMEOUT
AMBIGUOUS_BOTH_HIT
INVALID
```

### 20.9 Deterministische Schablonenexpansion

In allen Schablonen wird der abschließende Platzhalter `_h` durch genau einen
registrierten Suffix ersetzt.

Beispiel:

```text
fwd_noc_long_ret_h060
barrier_long_outcome_tp050_sl020_h060
label_noc_direction_reason_codes_h060
```

Die vollständige S7-Feldmenge ist das kartesische Produkt aus:

1. den Basisfeldern aus Abschnitt 20.4,
2. allen Feldschablonen aus den Abschnitten 18.1, 18.2 und 20.5 bis 20.8,
3. allen sechs Suffixen aus Abschnitt 4.1.

Diese Expansion ist normativ und erzeugt keine optionalen oder impliziten
Felder.

### 20.10 Profilkollisionen

Werden mehrere Kosten- oder Barrier-Profile in derselben View gespeichert,
muss der Feldname einen eindeutigen registrierten Profil-Tag enthalten.

Alternativ werden getrennte Views mit identischem Basisschema und jeweils
genau einem Profil erzeugt. Zwei semantisch unterschiedliche Felder dürfen
niemals denselben Namen tragen.

Version `1.0.0` des kanonischen S7-Schemas enthält genau das Kostenprofil
`COST_PROXY_FEE_RT_0004_V1` und das Barrier-Profil
`L1_BARRIER_TP050_SL020_V1`. Ein weiteres Profil benötigt eine neue
kompatible Schemaversion oder eine getrennte registrierte Label-Research-View.

## 21. Output-Profile

### 21.1 Kanonisches Gesamtprofil

Die erste Baseline verwendet genau:

```text
label_profile_id=RCC002_CANONICAL_LABELS_V1
label_profile_version=1.0.0
label_schema_id=rcc002.stage.s7-labels
label_schema_version=1.0.0
label_schema_ref=rcc002.stage.s7-labels/1.0.0
horizon_registry_id=RCC002_FORWARD_HORIZONS_V1
horizon_registry_version=1.0.0
cost_profile_id=COST_PROXY_FEE_RT_0004_V1
cost_profile_version=1.0.0
barrier_profile_id=L1_BARRIER_TP050_SL020_V1
barrier_profile_version=1.0.0
label_reason_code_registry_version=1.0.0
label_numeric_profile_id=RCC002_FLOAT64_LABEL_NUMERICS_V1
label_numeric_profile_version=1.0.0
```

### 21.2 Enthaltene Familien

`RCC002_CANONICAL_LABELS_V1` enthält gemeinsam:

- Close-to-Close-Returns;
- Next-Open-to-Close-Returns;
- Log Returns;
- lineare Net-Proxy-Returns;
- Long-/Short-MFE und -MAE;
- erste Extrem-Offsets;
- Brutto- und Net-Proxy-Richtungslabels;
- Long-/Short-Barrier-Outcomes;
- familienbezogene Gültigkeit, Reason Codes und Segmentidentität;
- Horizon-Bars und Verfügbarkeitszeitpunkte.

Bezeichnungen wie `FORWARD_RETURNS_GROSS_V1`,
`FORWARD_RETURNS_COST_PROXY_V1`, `FORWARD_EXCURSIONS_V1`,
`DIRECTION_LABELS_V1` und `BARRIER_LABELS_V1` bezeichnen
Auswertungsfamilien, aber keine konkurrierenden kanonischen
S7-Stufenschemas.

### 21.3 Komponentenidentität

```text
component_id=RCC002_S7_LABEL_BUILDER
component_version=0.3.0
```

Die Implementierung manifestiert zusätzlich:

- Source-Tree- oder Commit-Identität;
- Eingangs- und Ausgangsschema-Fingerprint;
- Label-, Horizon-, Kosten-, Barrier- und Reason-Code-Profilversionen;
- numerisches Determinismusprofil;
- semantischen Konfigurationshash.

### 21.4 Schema-Kompatibilität

Für S7 gilt semantische Versionierung:

- Patch: keine logische Schema- oder Semantikänderung;
- Minor: ausschließlich registrierte rückwärtskompatible Erweiterung;
- Major: inkompatible Feld-, Typ-, Null-, Enum- oder Bedeutungsänderung.

Eine Implementierung darf unbekannte Felder oder unbekannte Major-Versionen
nicht still akzeptieren.

## 22. Zeilen- und Dateninvarianten

S7 darf:

- keine Zeile hinzufügen,
- keine Zeile entfernen,
- keine S0-bis-S6-Felder verändern.

Es muss gelten:

```text
S7_rows = S6_rows
S7_primary_keys = S6_primary_keys
S7_primary_key_order = S6_primary_key_order
S7_market_segment_id = S6_market_segment_id
S7_fields_owned_by_S0_to_S6 = S6_fields
```

und alle kanonischen Schlüssel bleiben identisch. Dies konkretisiert für S7
das kanonische Row-Preservation-Prinzip aus
`RCC_002_DATA_PIPELINE_SPECIFICATION` §5.8.

S7 darf ausschließlich die in `rcc002.stage.s7-labels/1.0.0`
registrierten Erweiterungsfelder hinzufügen. Nicht registrierte Zusatzfelder,
alternative Aliasfelder oder eine zweite konkurrierende Horizon-Registry
machen das Artefakt nicht kanonisch.

Tail- oder Gap-Labels bleiben als ungültige Werte in ihren ursprünglichen
Zeilen erhalten.

## 23. Partitionierte Berechnung

### 23.1 Forward Overlap

Eine Partition benötigt bis zu:

`max_horizon = 1440`

zukünftige Kerzen als Read-Only-Overlap.

### 23.2 Keine Doppelausgabe

Overlap-Zeilen dienen nur der Labelberechnung und werden nicht doppelt
ausgegeben.

### 23.3 Letzte Partition

Unvollständige Tail-Horizonte der letzten Partition bleiben ungültig.

### 23.4 Parität

Serielle und partitionierte S7-Berechnung muss:

- identische Gültigkeit,
- identische diskrete Outcomes,
- innerhalb der Float-Toleranz identische Returns und Excursions

erzeugen.

## 24. Inkrementelle Aktualisierung

### 24.1 Neue Daten

Bei Datenfortschreibung werden zuvor ungültige Tail-Labels neu berechnet,
sobald ihr vollständiger Zukunftshorizont verfügbar ist.

Mindestens die letzten `max_horizon` bisherigen Zeilen werden erneut geprüft.

### 24.2 Historische Preiskorrektur

Wird Kerze `k` geändert, müssen für jeden Horizont alle Labelzeilen neu geprüft
werden, deren:

- Entry,
- Exit,
- Excursion Window oder
- Barrier Window

Kerze `k` enthält.

Für das Gesamtprofil ist mindestens der Bereich:

`[k - max_horizon, ..., k]`

zu invalidieren und neu zu berechnen.

### 24.3 Segmentänderung

Ändert sich eine Lücke oder Segmentgrenze, werden alle Zukunftsfenster neu
berechnet, die die betroffene Grenze erreichen können.

## 25. Dataset Splits

### 25.1 Zeitgerechte Splits

Training, Validierung und Test müssen chronologisch getrennt werden.

Zufälliges Row-Shuffling vor der Split-Bildung ist für zeitabhängige Labels
unzulässig.

### 25.2 Boundary Crossing

Ein Trainingssample bei `t` darf nicht verwendet werden, wenn sein
Labelhorizont in den Validierungs- oder Testzeitraum hineinreicht.

### 25.3 Purging

Vor jeder nachfolgenden Splitgrenze werden Samples entfernt, deren
Zukunftsfenster die Grenze überschreitet.

Die Purge-Länge richtet sich nach dem tatsächlich verwendeten maximalen
Horizont.

### 25.4 Embargo

Wenn Modell- oder Auswahlverfahren zusätzliche zeitliche Abhängigkeiten
erzeugen, darf nach einer Splitgrenze ein Embargo verwendet werden.

Embargo-Länge und Begründung müssen präregistriert werden.

### 25.5 Überlappende Labels

Forward Labels benachbarter Minuten überlappen stark.

Analysen und Unsicherheitsschätzungen müssen diese serielle Abhängigkeit
berücksichtigen. Die rohe Zeilenzahl darf nicht als Zahl unabhängiger
Beobachtungen interpretiert werden.

## 26. Feature-/Label-Trennung

### 26.1 Verbindliche S8-Viewklassen

Der übergeordnete S8-Vertrag reserviert:

| `schema_id` | `schema_version` | `schema_ref` | S7 zulässig | `allowlist_sha256` |
|---|---|---|:---:|---|
| `rcc002.view.research-features` | `1.0.0` | `rcc002.view.research-features/1.0.0` | Nein | `2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e` |
| `rcc002.view.backtest-inputs` | `1.0.0` | `rcc002.view.backtest-inputs/1.0.0` | Nein | `2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e` |
| `rcc002.view.paper` | `1.0.0` | `rcc002.view.paper/1.0.0` | Nein | `2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e` |
| `rcc002.view.live` | `1.0.0` | `rcc002.view.live/1.0.0` | Nein | `2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e` |
| `rcc002.view.label-research` | `1.0.0` | `rcc002.view.label-research/1.0.0` | Ja | `0e223d60ed4139f73194f1cb3b886a8eface9229183ad522a093e966827518cc` |
| `rcc002.view.audit` | `1.0.0` | `rcc002.view.audit/1.0.0` | Ja | `3c29f3219e65ca87df199a52dc8d15b54a6ea28884a863d1479d27e8a2401b56` |

Die Data-Pipeline-Spezifikation ist Eigentümerin der positiven Feld-Allowlist
jeder View. Die vorliegende Spezifikation ist Eigentümerin der
S7-Feldprovenienz.

Die sechs Allowlists sind in
`RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`, Version `0.7.1`,
Abschnitt 7.9 vollständig expandiert. Die dortige Registry
`RCC002_S8_FIELD_OWNERSHIP_V1`, Version `1.0.0`, ordnet jedem Feld genau eine
Eigentümerstufe und Leakage-Klasse zu. Abweichende lokale Listen sind
unzulässig.

### 26.2 Label-Research-View

Eine ML- oder Outcome-View mit S7-Inhalten verwendet ausschließlich:

```text
rcc002.view.label-research/1.0.0
```

Sie enthält:

- explizit freigegebene Felder aus S0 bis S6;
- explizit ausgewählte und einzeln erlaubte S7-Felder;
- Split- und Purge-Metadaten aus einem registrierten Forschungsvertrag.

Eine Wildcard oder pauschale Freigabe aller zukünftigen S7-Felder ist
unzulässig.

### 26.3 Live-, Paper-, Backtest- und Feature-Views

Diese Views verwenden ausschließlich positive Feld-Allowlists aus S0 bis S6.

Sie müssen primär jedes Feld ausschließen, dessen registrierte
Erzeugerstufe lautet:

```text
S7_LABELS
```

Zusätzlich müssen sie sämtliche Felder mit folgenden Präfixen ausschließen:

- `fwd_*`,
- `label_*`,
- `barrier_*`

Die Präfixprüfung ersetzt weder Feldprovenienz noch positive Allowlist.
Unbekannte Felder und Felder ohne registrierte Eigentümerstufe werden
fail-closed abgelehnt.

### 26.4 Automatischer Leakage-Test

Der Leakage-Test muss fehlschlagen, wenn:

- ein Feld mit `field_owner_stage=S7_LABELS` in einer Research-Feature-,
  Backtest-Input-, Live- oder Paper-View vorkommt,
- ein S7-Präfix in einer dieser Views vorkommt,
- ein unbekanntes Feld durch eine positive Allowlist gelangt,
- ein Feld ohne registrierte Erzeugerstufe freigegeben wird,
- ein Feature erst nach dem Entscheidungszeitpunkt verfügbar ist,
- Splitgrenzen von Labelhorizonten überschritten werden,
- Labelstatistiken zur Feature-Normalisierung verwendet werden.

Der Test muss außerdem nachweisen, dass alle in
`rcc002.stage.s7-labels/1.0.0` registrierten Felder für Live und Paper
abgelehnt werden, auch wenn ein Testfeld absichtlich kein reserviertes Präfix
trägt.

## 27. Counterfactual Gate Evaluation

### 27.1 Unabhängige Outcome-Basis

Forward Returns werden für alle gültigen Zeitpunkte berechnet, unabhängig
davon, ob ein Gate oder Signal aktiv war.

### 27.2 Gruppierung erst nach Berechnung

Erst nach der unabhängigen S7-Berechnung dürfen Outcomes gruppiert werden nach:

- `allow_long`,
- `allow_short`,
- Regime,
- Signalzustand,
- Gate-Profil.

### 27.3 Vermeidung selektiver Labels

Es ist unzulässig, Forward Labels nur für erlaubte oder tatsächlich gehandelte
Zeilen zu erzeugen.

Dies würde die Counterfactual-Analyse verzerren.

## 28. Verhältnis zum Backtest

### 28.1 Label

Ein S7-Label beantwortet eine fest definierte Zukunftsfrage.

### 28.2 Backtest

Ein Backtest modelliert:

- Signalpersistenz,
- tatsächliche Entry-Zeit,
- Positionszustand,
- konkurrierende Exits,
- Cooldown,
- Kosten,
- Kapitalentwicklung.

### 28.3 Keine Ergebnisgleichsetzung

Forward-Return- oder Barrier-Label-Performance darf nicht als identisch mit
Strategieperformance dargestellt werden.

S7 dient:

- Hypothesengenerierung,
- Outcome-Analyse,
- ML-Zielbildung,
- Vorprüfung.

Die Strategievalidierung bleibt separat.

## 29. Legacy- und GS-Lineage

### 29.1 Historische BTC-Pipeline

Der verifizierte historische BTC-Builder erzeugte Indikatoren und
Signalspalten, aber die bisher untersuchte Datei belegt keine vollständig
versionierte kanonische Forward-Return-Stufe.

### 29.2 GS-Dateinamen

Erhaltene GS-Pfade enthalten Bezeichnungen wie:

`GS_PLUS_FORWARD_WITH_SIGNALS`

Dateinamen allein belegen jedoch nicht:

- Forward-Formel,
- Horizont,
- Entry-/Exit-Referenz,
- Kosten,
- Gap-Handling,
- Label-Verfügbarkeit.

### 29.3 Rekonstruktionsstatus

Eine GS-Forward-Rekonstruktion erhält:

`GS_FORWARD_RECONSTRUCTION_V1`

und Status:

`HYPOTHESIS`

bis Builder oder empirisch validierbare Datensätze die Regeln bestätigen.

## 30. Numerische Präzision

### 30.1 Datentyp

Returns, Log Returns und Excursions verwenden mindestens `float64`.

### 30.2 Keine Zwischenrundung

Entry-, Exit-, Extrem- und Kostenberechnungen werden nicht zwischengerundet.

### 30.3 Vergleichstoleranz

Für unabhängige Implementierungsvergleiche:

- `absolute_tolerance = 1e-12`,
- `relative_tolerance = 1e-10`.

Diskrete Labels und Barrier-Outcomes müssen exakt übereinstimmen.

### 30.4 Numerisches Determinismusprofil

Vor `Approved for Implementation` muss ein registriertes numerisches Profil
mindestens festlegen:

- IEEE-754-`Float64` als Berechnungsdomäne;
- Operationsreihenfolge jeder Formel;
- Verhalten bei Division durch null;
- Konvertierung nicht endlicher Resultate in `null` plus Reason Code;
- FMA-Regel;
- Parallelreduktionsregel für Minima und Maxima;
- Behandlung von `-0.0`;
- Logarithmusimplementierung und gebundene numerische Bibliothek;
- exakte Vergleichsregeln für Barrieren und Richtungslabels;
- Referenztoleranzen für unabhängige Implementierungen.

Die erste Baseline reserviert:

```text
label_numeric_profile_id=RCC002_FLOAT64_LABEL_NUMERICS_V1
label_numeric_profile_version=1.0.0
```

Eine Änderung, die diskrete Outcomes, Gültigkeit oder numerische Werte
außerhalb der Referenztoleranzen verändern kann, ist eine semantische
Konfigurationsänderung.

## 31. Testanforderungen – Returns

### 31.1 Handberechnete Fälle

Mindestens:

- steigender Preis,
- fallender Preis,
- unveränderter Preis,
- Long und Short,
- Close-to-Close,
- Next-Open-to-Close,
- Kostenproxy,
- mehrere Horizonte.

### 31.2 Vorzeichenidentität

Vor Kosten muss gelten:

`short_return = -long_return`

für dieselben linearen Entry-/Exit-Referenzen.

### 31.3 Horizon Index

Für jeden Horizont wird geprüft, dass exakt `t+h` verwendet wird und kein
Off-by-one-Fehler besteht.

### 31.4 Tail

Die letzten `h` Zeilen sind für Horizont `h` ungültig, sofern keine späteren
Daten im selben Build verfügbar sind.

## 32. Testanforderungen – Excursions

Mindestens:

- Extrem in erster Zukunftskerze,
- Extrem in letzter Zukunftskerze,
- mehrfach identisches Extrem,
- ausschließlich steigende Serie,
- ausschließlich fallende Serie,
- Gap Crossing,
- Long-/Short-Symmetrie.

MFE-/MAE-Werte werden gegen handberechnete High-/Low-Fenster geprüft.

## 33. Testanforderungen – Barrieren

Mindestens:

- TP in erster Kerze,
- SL in erster Kerze,
- TP vor SL über verschiedene Kerzen,
- SL vor TP über verschiedene Kerzen,
- beide in derselben Kerze,
- Open-Gap über TP beziehungsweise unter SL,
- Open-Gap für Short unter TP beziehungsweise über SL,
- keine Barriere bis Timeout,
- Treffer exakt auf Barriere,
- Long und Short,
- Gap Crossing,
- unvollständiger Tail.

Eine exakte Berührung zählt als Treffer:

- Long TP: `high >= tp_price`,
- Long SL: `low <= sl_price`,
- Short TP: `low <= tp_price`,
- Short SL: `high >= sl_price`.

## 34. Property-, Leakage- und Paritätstests

### 34.1 Property-Tests

Es muss gelten:

- Änderungen nach `t+h` verändern Label `t,h` nicht,
- Änderungen innerhalb des Zukunftsfensters dürfen ausschließlich betroffene
  Labels ändern,
- S7 verändert keine S0-bis-S6-Felder,
- ungültige Zukunftsfenster erzeugen keine numerischen gültigen Labels,
- Live-/Paper-Allowlist enthält keine S7-Felder,
- serielle und partitionierte Berechnung stimmen überein,
- neue Daten vervollständigen nur zuvor unvollständige Tail-Horizonte oder
  davon abhängige Artefakte,
- identische Inputs und Profile erzeugen identische Outputs.

Zusätzlich werden systematisch generierte gültige OHLC-Sequenzen geprüft auf:

- endliche gültige Returns;
- `fwd_cc_short_ret_h = -fwd_cc_long_ret_h`;
- `fwd_noc_short_ret_h = -fwd_noc_long_ret_h`;
- Long- und Short-MFE größer oder gleich null;
- Long- und Short-MAE kleiner oder gleich null;
- Extrem-Offsets im Intervall `1...h`;
- ausschließlich registrierte Direction- und Barrier-Enums.

### 34.2 Schema- und Registry-Tests

Mindestens:

- Annahme von `rcc002.stage.s6-gates/1.0.0`;
- Ablehnung unbekannter S6-Major-Versionen;
- Ausgabe von `rcc002.stage.s7-labels/1.0.0`;
- exakte S7-Basisfeld-Allowlist;
- vollständige Expansion aller Feldschablonen über sechs Horizonte;
- exakte Feldreihenfolge;
- exakte logische Typen und Nullbarkeit;
- exakte Eigentümerstufe `S7_LABELS`;
- exakte Leakage-Klasse `FUTURE_OUTCOME`;
- Ablehnung unbekannter Horizon-, Kosten-, Barrier- und Reason-Code-Profile;
- Ablehnung nicht registrierter Zusatzfelder;
- Schema-Fingerprint-Parität.

### 34.3 Gültigkeits- und Reason-Code-Tests

Mindestens:

- unvollständiger Tail;
- Wechsel von `market_segment_id`;
- ungültige Zukunftskerze;
- synthetische Zukunftskerze;
- ungültiger Entry-Preis;
- ungültiger Exit-Preis;
- nicht endliches Resultat;
- Barrier-Ambiguität;
- Barrier-Timeout;
- leere Reason-Code-Liste bei vollständig gültigem Ergebnis;
- Deduplikation und Prioritätssortierung;
- numerische Nullwerte bei familienbezogener Invalidität;
- `INVALID` für ungültige Barrier-Outcomes.

### 34.4 Leakage-Tests

Für jede der folgenden Views wird jedes registrierte S7-Feld einzeln als
negativer Testfall injiziert:

- `rcc002.view.research-features/1.0.0`;
- `rcc002.view.backtest-inputs/1.0.0`;
- `rcc002.view.paper/1.0.0`;
- `rcc002.view.live/1.0.0`.

Jede Injektion muss unabhängig vom Feldnamen aufgrund von
`field_owner_stage=S7_LABELS` abgelehnt werden.

Zusätzlich werden Testfelder mit den Präfixen `fwd_`, `label_` und `barrier_`
bei fehlender oder absichtlich falscher Eigentümermetadaten abgelehnt.

### 34.5 Reconciliation- und Paritätstests

Mindestens:

- S6→S7-Zeilenzahl;
- Primärschlüssel und Sortierung;
- `market_segment_id`;
- unveränderte S0-bis-S6-Felder;
- serielle gegen partitionierte Berechnung;
- Vollbuild gegen inkrementellen Rebuild;
- Referenzimplementierung gegen Produktionsimplementierung;
- identische semantische Konfiguration bei unterschiedlicher physischer
  Publikationskonfiguration;
- erwartete ID-Wirkung semantischer und physischer
  Konfigurationsänderungen.

## 35. S7-Bericht

Der Bericht enthält mindestens:

- Build-, Schema- und Profilversionen,
- aktive Horizonte,
- Kosten- und Barrier-Profile,
- Zeilenzahl und Zeitbereich,
- gültige und ungültige Labels je Familie und Horizont,
- Tail-Invalidität,
- Gap-Crossing-Invalidität,
- Return-Verteilungen,
- Long-/Short-Symmetrieprüfung,
- MFE-/MAE-Verteilungen,
- Barrier-Outcome-Verteilungen,
- Ambiguous-Anteil,
- verfügbare Labelzeitpunkte,
- Partitionsparität,
- Leakage-Test,
- Output-Checksumme.

## 36. Ausgabevertrag

### 36.1 Logisches Ausgangsschema

S7 erzeugt ausschließlich:

```text
rcc002.stage.s7-labels/1.0.0
```

Das Schema enthält:

1. alle Felder aus `rcc002.stage.s6-gates/1.0.0` unverändert und in
   unveränderter Reihenfolge;
2. die S7-Basisfelder aus Abschnitt 20.4;
3. je Horizon-Suffix die expandierten Felder aus den Abschnitten 18.1, 18.2
   und 20.5 bis 20.8.

### 36.2 Kanonische Feldreihenfolge

Nach den unveränderten S6-Feldern lautet die S7-Reihenfolge:

1. Basisfelder in Tabellenreihenfolge aus Abschnitt 20.4;
2. Horizonte in Reihenfolge `H001`, `H005`, `H015`, `H060`, `H240`,
   `H1440`;
3. innerhalb jedes Horizonts:
   - gemeinsame Horizon-Metadaten,
   - Close-to-Close-Gültigkeit und Werte,
   - Next-Open-to-Close-Gültigkeit und Werte,
   - Excursion-Gültigkeit und Werte,
   - CC- und NOC-Richtungslabel-Gültigkeit und Werte,
   - Barrier-Gültigkeit und Werte.

Die maschinenlesbare Schemaregistry muss diese Reihenfolge vollständig
expandiert enthalten. Eine Implementierung darf die Tabellenreihenfolge nicht
aus eigener Zweckmäßigkeit verändern.

### 36.3 Eigentum und Leakage-Klasse

Für jedes neu erzeugte Feld gilt:

```text
field_owner_stage=S7_LABELS
leakage_class=FUTURE_OUTCOME
live_allowed=false
paper_allowed=false
backtest_input_allowed=false
research_feature_allowed=false
label_research_allowed=true
```

Die konkrete Aufnahme in eine Label-Research- oder Audit-View benötigt
zusätzlich die positive S8-Allowlist.

### 36.4 Schema-Fingerprint

Der logische S7-Schema-Fingerprint umfasst mindestens:

- geordnete Feldnamen;
- logische Datentypen und Nullbarkeit;
- Eigentümerstufe und Leakage-Klasse;
- Primärschlüssel und Sortierung;
- Horizon- und Profilzuordnung;
- Enum- und Reason-Code-Register;
- Feld- und Nullsemantik;
- Schema-Kompatibilitätsregeln.

### 36.5 Reconciliation

Vor Veröffentlichung werden mindestens geprüft:

```text
S7_rows = S6_rows
S7_keys_sha256 = S6_keys_sha256
S7_upstream_fields_semantic_sha256 = S6_fields_semantic_sha256
S7_market_segments_sha256 = S6_market_segments_sha256
```

Eine Abweichung ist ein Publication-Blocker.

### 36.6 Manifestpflicht

Das S7-Stage-Manifest referenziert mindestens:

- Eingangs- und Ausgangsschema-ID samt Version und Fingerprint;
- Komponenten-ID und Version;
- Label-, Horizon-, Kosten-, Barrier-, Reason-Code- und Numerikprofile;
- `semantic_build_configuration_sha256`;
- Code- und Umgebungsidentität;
- Eingangs- und Ausgangsartefakte;
- Reconciliation-Ergebnisse;
- S7-Bericht;
- semantische Output-Checksumme;
- physischen Artefaktbezug.

## 37. Konfiguration und offene Implementierungsparameter

### 37.1 Semantische Build-Konfiguration

Zur `semantic_build_configuration` gehören mindestens:

- Labelprofil;
- Horizon-Registry;
- Kostenprofil;
- Barrier-Profil;
- Intrabar-Ambiguitätsregel;
- Preisreferenzen;
- Return- und Excursion-Formeln;
- Gültigkeits- und Segmentregeln;
- Reason-Code-Registry;
- numerisches Determinismusprofil;
- logische S7-Schema-ID und Version;
- S8-Leakage- und Viewverträge;
- inkrementelle Invalidierungsregeln.

Der Hash:

```text
semantic_build_configuration_sha256
```

beeinflusst `build_id` und damit die Identität des logischen Datasetinhalts.

### 37.2 Physische Veröffentlichungskonfiguration

Zur `physical_publication_configuration` gehören innerhalb eines zuvor
freigegebenen physischen Profils:

- Partitionsgrößen;
- Parquet-Row-Group-Größen;
- Kompressionsstufe;
- Writeroptimierungen;
- temporäre Speicherorte;
- Retention technischer Zwischenartefakte;
- technisch gleichwertige Zielpfade.

Der Hash:

```text
physical_publication_configuration_sha256
```

beeinflusst ausschließlich physische Layout- und Artefaktidentitäten. Eine
reine Neuverpackung darf weder S7-Werte noch Gültigkeit, Reason Codes,
`build_id` oder `dataset_id` verändern.

### 37.3 Vor `Approved for Implementation` festzulegen

Vor Implementierungsfreigabe müssen versioniert vorliegen:

- vollständiges maschinenlesbares S7-Schema;
- vollständig expandiertes S7-Feldregister;
- Horizon-, Label-, Kosten-, Barrier-, Enum- und Reason-Code-Register;
- S7- und S8-Kompatibilitätsregeln;
- positive logische S8-View-Allowlists;
- numerisches Determinismusprofil und gebundene Bibliotheken;
- Referenztoleranzen;
- Golden Fixtures und erwartete Resultate;
- Build-Einstiegspunktvertrag;
- Umgebungs- und Lockstrategie;
- Identitätsvorabbildungen;
- S6→S7-Reconciliation;
- Test- und Abnahmekriterien.

### 37.4 Während der Implementierung konkretisierbar

Während der Implementierung dürfen ausschließlich die physischen Parameter
aus Abschnitt 37.2 innerhalb freigegebener Profile konkretisiert werden.

Jede spätere Änderung mit Wirkung auf fachliche Semantik, logische Schemas,
Identitätsvorabbildungen, Leakage-Schutz oder numerische
Determinismusregeln muss die betroffenen Review-Gates erneut durchlaufen.

## 38. Publication Gate

S7 darf nur veröffentlicht werden, wenn:

1. S6 vollständig freigegeben ist,
2. das Eingangsschema exakt `rcc002.stage.s6-gates/1.0.0` erfüllt,
3. das Ausgangsschema exakt `rcc002.stage.s7-labels/1.0.0` erfüllt,
4. alle Horizonte, Profile, Enums und Reason Codes registriert sind,
5. Feldschablonen vollständig und eindeutig expandiert sind,
6. Entry-, Exit- und Horizon-Indizes korrekt sind,
7. Long-/Short-Vorzeichenprüfung bestanden ist,
8. Kostenprofile Bruttowerte nicht überschreiben,
9. Segment-, Qualitäts- und Tail-Regeln korrekt sind,
10. Barrier-Ambiguität erhalten bleibt,
11. keine nicht endlichen gültigen Labels bestehen,
12. familienbezogene Null- und Gültigkeitsinvarianten erfüllt sind,
13. Zeilen, Primärschlüssel, Segmente und S0-bis-S6-Werte unverändert sind,
14. serielle und partitionierte Berechnung übereinstimmen,
15. inkrementeller Rebuild und Vollbuild semantisch übereinstimmen,
16. stufenbasierte Leakage- und positive Allowlist-Tests bestanden sind,
17. kein S7-Feld in Research-Feature-, Backtest-Input-, Paper- oder
    Live-Views enthalten ist,
18. Reconciliation, Manifest, Schema und Checksummen vollständig sind.

Der Gate-Status lautet:

- `PASS`,
- `FAIL`,
- `PASS_WITH_APPROVED_EXCEPTIONS`.

`PASS_WITH_APPROVED_EXCEPTIONS` darf ausschließlich nicht blockierende,
vollständig dokumentierte Berichtsbefunde betreffen. Es darf weder einen
Schema-, Profil-, Horizon-, Gültigkeits-, Segment-, Leakage-, Reason-Code-,
Reconciliation- oder Identitätsfehler überstimmen.

## 39. Abnahmekriterien

### 39.1 Spezifikationsreife vor Implementierungsfreigabe

Die Spezifikation ist bereit für `Approved for Implementation`, wenn:

1. der S6-Eingangsvertrag vollständig festgelegt ist;
2. genau ein S7-Schema und ein Horizon-Register gelten;
3. alle S7-Basisfelder und Feldschablonen vollständig registriert sind;
4. alle Return-, Excursion-, Direction- und Barrier-Regeln eindeutig sind;
5. Gültigkeit, Nullsemantik, Segmentgrenzen und Verfügbarkeit
   widerspruchsfrei sind;
6. Reason Codes und Enums vollständig versioniert sind;
7. stufenbasierter Leakage-Schutz und positive S8-Allowlists spezifiziert
   sind;
8. semantische und physische Konfiguration getrennt sind;
9. numerisches Determinismusprofil und Referenztoleranzen feststehen;
10. Golden-, Unit-, Property-, Leakage-, Schema-, Reconciliation- und
    Integrationstestverträge vollständig sind;
11. Split-, Purge- und Embargoverträge festgelegt sind;
12. alle vorgeschriebenen internen und externen Review-Gates der
    Spezifikationsbaseline bestanden sind;
13. keine offene Entscheidung fachliche Werte, Gültigkeit, logische Schemas,
    Leakage-Schutz oder Identitätsvorabbildungen verändern kann.

### 39.2 Abnahme der Implementierung

Die spätere Implementierung ist akzeptiert, wenn:

1. alle Return-Familien handberechnet getestet sind;
2. jeder Horizont auf Off-by-one-Fehler geprüft ist;
3. Long-/Short-Symmetrie bestanden ist;
4. Kostenproxy und Bruttowerte getrennt sind;
5. MFE/MAE und Barrier-Logik vollständig getestet sind;
6. Qualitäts-, Tail- und Segmentregeln bestanden sind;
7. Purging und Split-Grenzen getestet sind;
8. S8-Live-/Paper-Allowlist S7 vollständig ausschließt;
9. stufenbasierte Leakage-Tests sämtliche S7-Felder erkennen;
10. serielle, partitionierte, inkrementelle und unabhängige
    Referenzberechnung übereinstimmen;
11. BTCUSDT-1m-Vollbuild auf der Workstation erfolgreich ist;
12. S6→S7-Reconciliation vollständig besteht;
13. Manifest, Dataset Lineage und Knowledge Lineage vollständig sind;
14. das S7-Publication-Gate automatisiert bestanden ist.

## 40. Freigabestatus und nächster Schritt

`RCC-002-SCR-004` bestätigte die dort geprüften wissenschaftlichen
Korrekturen als geschlossen.

Der vollständige Architecture Integrity Review `RCC-002-AIR-001` bewertete
die Spezifikationsfamilie als:

```text
NOT PASSED – ARCHITECTURE CORRECTIONS REQUIRED
```

Version 0.4.0 bewahrt die in Version 0.3.0 geschlossenen
AIR-001-Korrekturen und korrigiert zusätzlich:

- `SCR-005-M01` – unversionierte `schema_id`, getrennte
  `schema_version` und abgeleitete `schema_ref`;
- `AIR-005-H01` – versionsgebundene, vollständig expandierte positive
  S8-Feld-Allowlists einschließlich Eigentümerstufe, Leakage-Klasse,
  Erzeugerstufe, SHA-256 und Fail-closed-Negativtests.

Sie aktualisiert außerdem die Abhängigkeiten auf:

```text
RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md
Version 0.7.0

RCC_002_DATA_VALIDATION_2026-07-23.md
Version 0.4.0

RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md
Version 0.4.0

RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md
Version 0.4.0

RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md
Version 0.5.0
```

Die Befunde sind erst geschlossen, wenn alle abhängigen Spezifikationen
konsistent aktualisiert, neu paketiert und erneut geprüft sind.

Der aktuelle Status lautet:

```text
SCR-005-Corrected Draft – Scientific Consistency Re-Review 006 Pending
```

Nächste vorgeschriebene Schritte:

1. vollständige interne Qualitätskontrolle;
2. neues vollständiges Spezifikationspaket;
3. Scientific Consistency Re-Review 006;
4. nur bei bestandenem SCR-006: fokussierter Architecture Integrity
   Re-Review;
5. Editorial Pass;
6. Internal Certification;
7. Claude Independent Architecture Review;
8. Gemini Independent Scientific and Adversarial Audit;
9. ChatGPT Final Consolidation;
10. `Baseline V1 Certified`;
11. Implementierungsfreigabe.

---

# Eingebettetes Dokument 7 von 7

## Quelldatei: `RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md`

# RCC-002 Reproducibility and Manifest Specification

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Normative technische und wissenschaftliche Spezifikation |
| Speicherort | `docs/specifications/` |
| Dateiname | `RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md` |
| Dokument-ID | `RCC-002-RM` |
| Version | `0.7.1` |
| Datum | `2026-07-23` |
| Status | SCR-005-Corrected Draft – Scientific Consistency Re-Review 006 Pending; RCC-002-SCR-007 Full-Scope Replacement Scientific Consistency Review durchgeführt; Major- und Minor-Findings-Verifikation abgeschlossen; Minor Correction Cycle umgesetzt; SCR-008 und AIR-004 durchgeführt; AIR4-MIN-01-Folgekorrektur mechanisch nachgezogen; Editorial Pass und Internal Certification ausstehend |
| Geltungsbereich | RCC-002-Datenpipeline, Stufen S0–S8 |
| Verbindlichkeit | Normativ für die RCC-002-Implementierung |
| Primäre Abhängigkeit | `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`, Version `0.7.1` |
| Fachliche Abhängigkeiten | `RCC_002_DATA_VALIDATION_2026-07-23.md`, Version `0.4.2`; `RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md`, Version `0.4.3`; `RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md`, Version `0.4.2`; `RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md`, Version `0.5.1`; `RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md`, Version `0.4.1` |
| Referenziert durch | RCC-002-Implementierungsplan; RCC-002-Build- und Prüfwerkzeuge; RCC-002-Dataset-Release-Dokumentation |
| Vorgesehene Reviews | Scientific Consistency Review; Architecture Integrity Review; Editorial Pass; Internal Certification; Claude Independent Architecture Review; Gemini Independent Scientific and Adversarial Audit; ChatGPT Final Consolidation; Baseline V1 Certified |

## Review Evidence

### Internal Review

Vor der ersten Ausgabe wurden geprüft:

- methodische Vollständigkeit der Reproduzierbarkeitsanforderungen;
- Trennung von Daten-, Code-, Konfigurations-, Spezifikations- und Umgebungsprovenienz;
- Zirkelfreiheit der Identitäts- und Hashbildung;
- Trennung deterministischer Build-Identitäten von Laufzeitidentitäten;
- Unterscheidung von Bytegleichheit und semantischer Gleichheit;
- Konsistenz mit den RCC-002-Stufen S0–S8;
- Regeln für atomare Veröffentlichung, Wiederaufnahme und Quarantäne;
- geräteübergreifende Reproduktion auf X1, G15 und Workstation;
- Geheimnisbereinigung und Datenschutz;
- Testbarkeit und maschinelle Validierbarkeit;
- Terminologie, Querverweise und normative Sprache.

Ergebnis: Keine bekannte methodische oder logische Blockade für den ursprünglichen Draft-Status.

### Scientific Consistency Review

Der gemeinsame Scientific Consistency Review der RCC-002-Spezifikationsfamilie vom `2026-07-23` wurde in
`docs/review/RCC_002_SPECIFICATION_FAMILY_SCR_REPORT_2026-07-23.md` dokumentiert.

Für dieses Dokument wurden die Befunde `SCR-B04`, `SCR-B05`, `SCR-M01`, `SCR-M02`, `SCR-M03` und `SCR-M04` als korrekturpflichtig übernommen. Version `0.2.0`:

- verwendet den vollständigen registrierten kanonischen Primärschlüssel;
- trennt semantischen Inhalt von physischem Layout;
- bindet JSON-Kanonisierung an RFC 8785/JCS und zusätzliche RCC-Regeln;
- präzisiert die Vorabbildung des `source_snapshot_id`;
- begrenzt E3 auf identische persistierte Artefakte oder identische vollständige Vorabbildungen;
- führt das versionierte Umgebungsidentitätsprofil `RCC_BUILD_ENV_IDENTITY_V1` ein.

Status nach Korrektur: fokussierter SCR-Re-Review ausstehend.

Der Re-Review `RCC-002-SCR-002` bestätigte die sechs vorgenannten Befunde als
geschlossen und identifizierte `SCR-RR-B02`: Physische `artifact_id`s
propagierten in logisch definierte `build_id` und `dataset_id`. Version `0.3.0`
trennt deshalb logische Build- und Dataset-Identität von der physischen
Artefaktmenge und ersetzt für neue Builds
`RCC_BUILD_ENV_IDENTITY_V1` durch das semantisch begrenzte
`RCC_BUILD_ENV_IDENTITY_V2`. Erneuter fokussierter Re-Review: ausstehend.

Der fokussierte Re-Review `RCC-002-SCR-003` bestätigte die früheren Befunde
als geschlossen und identifizierte:

- `SCR-003-B01`: Die Review- und Freigabesequenz wich von der verbindlichen
  RCC-002-Prüfpipeline ab.
- `SCR-003-B02`: Abhängigkeitsversionen waren innerhalb der
  Spezifikationsfamilie veraltet.
- `SCR-003-m01`: Das ID-Beispiel für `dataset_artifact_set_id` fehlte.
- `SCR-003-m02`: Die Unveränderlichkeitsregel war für neue physische
  Artefaktmengen mehrdeutig.

Version `0.4.0` korrigiert alle vier Befunde. Erneuter fokussierter
Re-Review: ausstehend.

Der Scientific Consistency Re-Review `RCC-002-SCR-004` bestätigte die dort
geprüften wissenschaftlichen Korrekturen als geschlossen.

Der vollständige Architecture Integrity Review `RCC-002-AIR-001` bewertete
die Spezifikationsfamilie als:

```text
NOT PASSED – ARCHITECTURE CORRECTIONS REQUIRED
```

Version `0.5.0` korrigiert die diesem Dokument zugeordneten Teile von:

- `AIR-001-B01` – kanonische S0-Provenienz sowie eindeutige S2-Qualitäts- und
  Segmentreferenzen in Manifesten und Lineage;
- `AIR-001-B02` – einheitlicher S7-Horizon- und Feldnamensraum sowie
  stufenbasierter S8-Leakageschutz;
- `AIR-001-B03` – eindeutige S5-/S6-Schema-, Modell-, Profil- und
  Zustandsreferenzen;
- `AIR-001-M01` – konkrete Stufen- und View-Schema-IDs, Feldregistry-,
  Kompatibilitäts- und Allowlist-Nachweise;
- `AIR-001-M02` – normative Trennung von
  `semantic_build_configuration` und
  `physical_publication_configuration`;
- `AIR-001-M03` – Trennung der vor Implementierungsfreigabe festzulegenden
  Verträge von später konkretisierbaren physischen Parametern;
- `AIR-001-m01` – einheitliche Referenz auf die kanonische
  Data-Pipeline-Dokument-ID `RCC_002_DATA_PIPELINE_SPECIFICATION`.

Die Schließung wird erst im fokussierten Scientific Consistency Re-Review und
Architecture Integrity Re-Review der vollständig aktualisierten
Spezifikationsfamilie bestätigt.

Der Scientific Consistency Re-Review `RCC-002-SCR-005` bewertete das
korrigierte Gesamtpaket als nicht bestanden. Version `0.6.0` korrigiert die
diesem Dokument zugeordneten Teile von `SCR-005-B01`, `SCR-005-B02`,
`SCR-005-M01` und `SCR-005-M03` und materialisiert `AIR-005-H01`. Die
Schließung dieser Punkte ist erst durch `RCC-002-SCR-006` bestätigt.

### Noch ausstehend

- Scientific Consistency Re-Review 006;
- nur bei bestandenem SCR-006: fokussierter Architecture Integrity Re-Review;
- Editorial Pass;
- Internal Certification;
- Claude Independent Architecture Review;
- Gemini Independent Scientific and Adversarial Audit;
- ChatGPT Final Consolidation;
- Baseline V1 Certified;
- Release- und Implementierungsfreigabe.

---

## 1. Zweck

Dieses Dokument definiert, wie jeder RCC-002-Datenstand eindeutig identifiziert, rekonstruiert, geprüft, veröffentlicht und auditiert wird.

Ein RCC-002-Artefakt gilt nur dann als reproduzierbar, wenn mindestens nachvollziehbar ist:

1. aus welchen Quelldaten es entstand;
2. welcher Code verwendet wurde;
3. welche Konfiguration galt;
4. welche Spezifikationsstände verbindlich waren;
5. in welcher Software- und Ausführungsumgebung der Build lief;
6. welche Vorgängerartefakte verarbeitet wurden;
7. welche Prüfungen bestanden wurden;
8. welche Ausgabeartefakte mit welchen Prüfsummen veröffentlicht wurden.

Die Spezifikation verlangt keine bloße Wiederholung eines Dateinamens. Reproduzierbarkeit ist eine überprüfbare Beziehung zwischen Eingaben, Transformationslogik, Umgebung, Ausführung und Ergebnissen.

---

## 2. Normative Begriffe

Die Schlüsselwörter **MUSS**, **DARF NICHT**, **SOLL**, **SOLL NICHT** und **DARF** sind normativ.

| Begriff | Definition |
|---|---|
| Artefakt | Eine gespeicherte Eingabe, Zwischenstufe, Ausgabe, Konfiguration, Prüfausgabe oder Dokumentationseinheit |
| Datenartefakt | Tabellen-, Ereignis-, Parquet-, CSV- oder vergleichbarer Datenbestand |
| Source Snapshot | Unveränderliche, exakt referenzierte Fassung der externen oder rohen Eingabedaten |
| Build | Deterministisch beschriebene Transformation definierter Eingaben mit definiertem Code, Konfiguration und Spezifikationsprofil |
| Run | Konkrete Ausführung eines Builds zu einem bestimmten Zeitpunkt und auf einer bestimmten Umgebung |
| Manifest | Maschinenlesbarer Herkunfts-, Identitäts-, Prüf- und Veröffentlichungsnachweis |
| Bytegleichheit | Identische Bytefolge und damit identischer Datei-Hash |
| Semantische Gleichheit | Gleiche kanonische Dateninhalte trotz möglicherweise unterschiedlicher Containerbytes |
| Dataset Lineage | Abstammung von Datenartefakten über alle Verarbeitungsstufen |
| Knowledge Lineage | Abstammung wissenschaftlicher Regeln, Entscheidungen, Hypothesen und Spezifikationen |
| Publication | Atomare Freigabe eines vollständig geprüften Artefakts |
| Quarantäne | Abgetrennter Status für unvollständige, fehlerhafte oder nicht freigegebene Ergebnisse |

---

## 3. Geltungsbereich

Die Regeln gelten für:

- `S0_SOURCE`;
- `S1_NORMALIZED`;
- `S2_VALIDATED`;
- `S3_INDICATORS`;
- `S4_SIGNALS`;
- `S5_REGIMES`;
- `S6_GATES`;
- `S7_LABELS`;
- `S8_EXPORT`;
- zugehörige Prüfberichte, Schemata, Konfigurationen und Manifeste.

Sie gelten für:

- vollständige Builds;
- inkrementelle Builds;
- Wiederholungs- und Reparatur-Builds;
- Forschungsprofile;
- Kandidaten-Releases;
- zertifizierte Releases.

Live- und Paper-Trading-Zustände dürfen auf RCC-002-Daten referenzieren, gehören aber nicht automatisch zum RCC-002-Dataset-Build.

---

## 4. Reproduzierbarkeitsmodell

RCC-002 unterscheidet vier Ebenen:

| Ebene | Frage | Primärer Nachweis |
|---|---|---|
| Provenienz | Woher stammen Regeln und Daten? | Lineage und Referenzen |
| Identität | Welcher logische Build beziehungsweise Run ist gemeint? | IDs |
| Integrität | Wurden Inhalte verändert? | Prüfsummen und Signaturen |
| Reproduktion | Kann das Ergebnis erneut erzeugt und verglichen werden? | Rebuild-Protokoll und Gleichheitsprüfung |

Keine einzelne Prüfsumme ersetzt das vollständige Modell.

---

## 5. Identitätssystem

### 5.1 Erforderliche IDs

| ID | Gegenstand | Deterministisch |
|---|---|---:|
| `dataset_id` | Logischer veröffentlichter RCC-002-Datenstand | Ja |
| `source_snapshot_id` | Unveränderliche Quelldatenfassung | Ja |
| `build_id` | Logische Transformationsdefinition einschließlich Eingaben | Ja |
| `artifact_id` | Identität eines einzelnen gespeicherten Artefakts aus semantischem Inhalt und physischem Layout | Ja |
| `dataset_artifact_set_id` | Physische Identität der veröffentlichten Artefaktmenge eines Datasets | Ja |
| `run_id` | Konkrete Ausführung | Nein |
| `manifest_id` | Konkreter kanonischer Manifestinhalt | Ja |

### 5.2 ID-Format

Empfohlenes Format:

```text
<type>:sha256:<64 lowercase hex characters>
```

Beispiele:

```text
source:sha256:<digest>
build:sha256:<digest>
artifact:sha256:<digest>
dataset:sha256:<digest>
dataset-artifact-set:sha256:<digest>
manifest:sha256:<digest>
```

`run_id` MUSS als nichtdeterministische Laufzeitidentität erkennbar sein:

```text
run:<UTC timestamp>:<UUIDv7-or-UUIDv4>
```

### 5.3 Source Snapshot ID

Die Vorabbildung des `source_snapshot_id` MUSS ausschließlich quellinhaltliche und semantische Abrufmerkmale enthalten:

- Quellenbezeichnung;
- Markt und Symbol;
- Datenfrequenz;
- normierte Liste aller Quelldateien;
- SHA-256 jeder Quelldatei;
- kanonische semantische Abrufparameter, die Auswahl oder Bedeutung der gelieferten Daten verändern;
- tatsächlich aus den Quellbytes abgeleiteten Abdeckungszeitraum;
- Quellenversions- oder Revisionskennung, soweit verfügbar.

Provider-Revisionskennungen und semantische Abrufparameter MÜSSEN die Identität beeinflussen. Abrufzeitpunkt, lokaler Speicherpfad, Hostname, Benutzername, Transport-Retrys und Cache-Ort sind Run- beziehungsweise Provenienzmetadaten und DÜRFEN den `source_snapshot_id` NICHT verändern.

`timezone`, `expected_start` und `expected_end` gehören ausschließlich zu
`semantic_build_configuration.source_expectations`. Sie beeinflussen
`semantic_build_configuration_sha256`, `build_id` und `dataset_id`, aber
nicht allein aufgrund ihrer Änderung `source_snapshot_id`. Der tatsächliche
Abdeckungszeitraum der unveränderten Quellbytes bleibt dagegen Bestandteil
der Source-Snapshot-Vorabbildung.

### 5.4 Build ID

Der `build_id` MUSS aus einer kanonischen Vorabbildung berechnet werden, die mindestens enthält:

- `source_snapshot_id` oder geordnete logische Parent-Identitäten aus
  `semantic_sha256` und zugehöriger Schema-ID;
- Code-Commit;
- Dirty-Patch-Hash, falls der Arbeitsbaum nicht sauber ist;
- `semantic_build_configuration_sha256`;
- Spezifikationsprofil mit Dokument-IDs und Versionen;
- Pipeline-Profil;
- Schema-IDs;
- `environment_identity_profile_id` und Hash der nach diesem Profil relevanten deterministischen Umgebungsparameter;
- Transformationsstufe oder Stufenbereich.

Nicht Bestandteil der Build-ID sind:

- Start- oder Endzeitpunkt des Runs;
- Hostname;
- zufällige UUID;
- temporärer Pfad;
- `manifest_id`;
- Hash des Manifests, das den `build_id` enthält;
- `physical_publication_configuration_sha256`;
- `physical_layout_sha256`;
- `artifact_id`;
- `dataset_artifact_set_id`;

Damit wird eine zirkuläre Hashdefinition ausgeschlossen.

### 5.5 Run ID

Der `run_id` identifiziert eine konkrete Ausführung desselben logischen Builds. Zwei Runs dürfen denselben `build_id`, aber niemals denselben `run_id` besitzen.

Der Run-Datensatz MUSS enthalten:

- `run_id`;
- `build_id`;
- Start- und Endzeit in UTC;
- Host- und Umgebungsinformationen;
- Prozessstatus;
- Ausführungsparameter;
- Prüf- und Veröffentlichungsstatus.

### 5.6 Artifact ID

Die `artifact_id` MUSS ein konkretes gespeichertes Artefakt identifizieren. Sie darf nicht allein aus Dateiname, Pfad oder semantischem Fingerprint entstehen.

Für Datenartefakte umfasst die Vorabbildung mindestens:

- kanonische Schema-ID;
- `semantic_sha256`;
- `physical_layout_sha256`;
- Byte-Hash des gespeicherten Containers;
- Zeilenanzahl;
- logische Zeitabdeckung.

Der `semantic_sha256` identifiziert den logischen Tabelleninhalt. Der `physical_layout_sha256` identifiziert dessen physische Anordnung. Dadurch erhalten semantisch gleiche, aber physisch unterschiedlich partitionierte oder serialisierte Artefakte unterschiedliche `artifact_id`s, bleiben jedoch über denselben `semantic_sha256` als E2-gleich erkennbar.

### 5.7 Dataset ID

Die `dataset_id` identifiziert die veröffentlichte logische Gesamtheit der S8-Artefakte. Ihre Vorabbildung MUSS enthalten:

- geordnete Liste logischer Dataset-Komponenten mit `logical_name`,
  Schema-ID, `semantic_sha256`, Zeilenanzahl und logischer Zeitabdeckung;
- Release-Schema-ID;
- Dataset-Profil;
- relevanten `build_id`;
- `semantic_build_configuration_sha256`;
- Qualitätsstatus;
- Spezifikationsprofil.

`artifact_id`, `physical_layout_sha256`, `byte_sha256`, Dateipfad,
Partitionierungsstruktur und Writerprofil DÜRFEN den `dataset_id` NICHT
beeinflussen.

### 5.8 Dataset Artifact Set ID

Die `dataset_artifact_set_id` identifiziert die konkrete physische
Veröffentlichungsmenge eines logischen Datasets. Ihre Vorabbildung MUSS
enthalten:

- `dataset_id`;
- geordnete Liste der veröffentlichten `artifact_id`s;
- Veröffentlichungs- beziehungsweise Layoutprofil;
- `physical_publication_configuration_sha256`;
- vollständige Partitions- und Dateigrenzen.

Eine reine Repartitionierung oder Neuverpackung behält bei semantisch
identischen Inhalten denselben `dataset_id`, erzeugt aber eine neue
`dataset_artifact_set_id`.

### 5.9 Manifest ID

Der `manifest_id` wird erst berechnet, nachdem alle anderen deterministischen IDs im Manifest feststehen.

Berechnung:

1. Manifestinhalt ohne Feld `manifest_id` kanonisieren;
2. SHA-256 der kanonischen Bytes berechnen;
3. Ergebnis als `manifest_id` einsetzen;
4. das vollständige Manifest speichern;
5. zusätzlich den Byte-Hash der gespeicherten Manifestdatei protokollieren.

Der `manifest_id` und der Byte-Hash der finalen Datei dürfen verschieden sein, weil das Feld `manifest_id` selbst erst nach der Vorabbildung ergänzt wird.

---

## 6. Hash- und Kanonisierungsregeln

### 6.1 Standardalgorithmus

SHA-256 ist der verbindliche Mindeststandard.

Andere Hashalgorithmen dürfen ergänzend gespeichert werden, ersetzen SHA-256 jedoch nicht.

### 6.2 Kanonisches JSON

Kanonisches JSON MUSS RFC 8785, JSON Canonicalization Scheme (JCS), verwenden. Vor der JCS-Serialisierung gelten zusätzlich folgende RCC-002-Vorverarbeitungsregeln:

- UTF-8 ohne BOM verwenden;
- alle Strings und Objektschlüssel in Unicode NFC normalisieren;
- Objektschlüssel nach JCS sortieren;
- keine semantisch irrelevanten Leerzeichen enthalten;
- Arrays grundsätzlich in ihrer vorhandenen Reihenfolge erhalten;
- Mengenähnliche Arrays nur dann sortieren, wenn ihr Schema eine eindeutige Sortierregel und einen vollständigen Sortierschlüssel registriert;
- Zeilenende LF verwenden;
- nichtendliche Zahlen (`NaN`, `Infinity`, `-Infinity`) verbieten;
- Zeitstempel im UTC-Format mit `Z` speichern;
- fachliche Dezimalwerte als kanonische Dezimalstrings serialisieren.

Verbindliches Profil:

```text
profile_id=RCC_JSON_CANONICALIZATION_V1
base_standard=RFC8785/JCS
encoding=UTF-8
unicode_preprocessing=NFC
non_finite_numbers=forbidden
domain_decimals=canonical_decimal_strings
array_order=schema-defined-or-preserved
```

Für `RCC_JSON_CANONICALIZATION_V1` MÜSSEN Golden Fixtures mit erwarteten kanonischen Bytes und SHA-256-Digests versioniert werden. Implementierungen MÜSSEN diese Fixtures vor einer Veröffentlichung ohne Abweichung bestehen.

### 6.3 Fließkommazahlen

Konfigurationen MÜSSEN fachliche Dezimalparameter als kanonische Dezimalstrings serialisieren. Das Format MUSS ein optionales Minuszeichen, mindestens eine Ganzzahlziffer und nur bei Bedarf einen Dezimalpunkt mit einer oder mehreren Nachkommastellen verwenden. Führende Pluszeichen, Exponenten, unnötige führende Nullen und unnötige nachgestellte Nullen sind verboten; `-0` wird als `0` serialisiert.

Binäre Fließkommawerte in Datenartefakten werden nicht durch JSON-Dezimalstrings ersetzt. Ihre kanonische Wertedarstellung MUSS im registrierten Tabellen-Fingerprint-Profil feldweise definiert sein.

### 6.4 Gemeinsame Konfigurationskanonisierung

Vor jeder Konfigurationshashbildung MUSS:

- die effektive, vollständig aufgelöste Konfiguration verwendet werden;
- Vererbung und Defaults aufgelöst sein;
- jeder Schlüssel genau einer Konfigurationsklasse zugeordnet sein;
- die Reihenfolge nichtsemantischer Schlüssel normalisiert sein;
- jeder Wert mit Typ erhalten bleiben;
- jede Maßeinheit explizit sein;
- jedes Geheimnis entfernt oder durch einen nichtumkehrbaren
  Referenzbezeichner ersetzt sein;
- `RCC_JSON_CANONICALIZATION_V1` angewandt werden.

Nicht erlaubt:

- Hash nur der vom Nutzer überschriebenen Werte;
- Hash eines Dateipfads statt des Inhalts;
- derselbe Schlüssel in beiden Konfigurationsklassen;
- ein nicht klassifizierter wirksamer Schlüssel;
- Speicherung von API-Schlüsseln, Tokens oder Passwörtern;
- Ersetzung eines Geheimnisses durch dessen ungesalzenen Hash, wenn dadurch
  Wörterbuchangriffe möglich werden.

### 6.5 Semantische Build-Konfiguration

Der normative Namensraum lautet:

```text
semantic_build_configuration
semantic_build_configuration_sha256
```

Er enthält ausschließlich Parameter, die mindestens eines der folgenden
Merkmale beeinflussen können:

- logische Datenwerte;
- Zeilenmenge oder Primärschlüssel;
- Gültigkeit, Warm-up oder Reason Codes;
- Segmentbildung oder State Reset;
- Indikator-, Signal-, Regime-, Gate- oder Labelsemantik;
- Horizon-, Kosten- oder Barrier-Profil;
- logisches Stufen- oder View-Schema;
- Feld-Allowlist oder Leakage-Klasse;
- numerisches Determinismusprofil;
- inkrementelle Invalidierungssemantik;
- Identitätsvorabbildungen.

Jede Änderung von `semantic_build_configuration_sha256` erzeugt einen neuen
`build_id` und einen neuen `dataset_id`. Dies gilt auch dann, wenn der
materialisierte Tabelleninhalt zufällig identisch bleibt.

Eigentümer ist die Build-Orchestrierung unter den fachlichen Grenzen der
jeweiligen Stufenspezifikation.

### 6.6 Physische Veröffentlichungskonfiguration

Der normative Namensraum lautet:

```text
physical_publication_configuration
physical_publication_configuration_sha256
```

Er enthält ausschließlich Parameter innerhalb eines zuvor freigegebenen
physischen Profils:

- Dateipartitionierung;
- Partitionsgrößen;
- Parquet-Row-Group-Größen;
- Kompressionsalgorithmus und -stufe;
- Dictionary- und Encoding-Auswahl;
- Writeroptimierungen;
- Containerparameter;
- technisch gleichwertige Speicherorte;
- Retention technischer Zwischenartefakte.

Der Hash beeinflusst:

- `physical_layout_sha256`;
- `artifact_id`;
- `dataset_artifact_set_id`.

Er DARF NICHT beeinflussen:

- `build_id`;
- `dataset_id`;
- `semantic_sha256`;
- logische Werte, Gültigkeit, Reason Codes oder Schemabedeutung.

Eine rein physische Neuverpackung:

- behält `build_id`;
- behält `dataset_id`;
- erzeugt neue physische Artefaktidentitäten;
- erzeugt eine neue `dataset_artifact_set_id`.

Eigentümer ist die S8-Publikations- und Artefaktkomponente.

### 6.7 Identitätswirkung

| Änderung | `build_id` | `dataset_id` | `artifact_id` | `dataset_artifact_set_id` |
|---|:---:|:---:|:---:|:---:|
| semantische Konfiguration | neu | neu | neu | neu |
| reine physische Neuverpackung | gleich | gleich | neu | neu |
| ausschließlich neue `run_id` oder Run-Zeit | gleich | gleich | bei identischen Bytes gleich | gleich |
| Source-Snapshot-Revision | neu | neu | neu | neu |
| Dirty-Patch-Änderung | neu | neu | neu | neu |

Golden Tests MÜSSEN jede Tabellenzeile mit konkreten Vorabbildungen und
erwarteten IDs prüfen. Mindestens erforderlich sind:

1. semantische Konfigurationsänderung mit geändertem Output;
2. semantische Konfigurationsänderung mit zufällig identischem Output;
3. reine physische Neuverpackung;
4. ausschließlich neue `run_id`.

In den ersten beiden Fällen sind `build_id` und `dataset_id` neu. Im dritten
Fall bleiben beide gleich, während physische Artefaktidentitäten und
`dataset_artifact_set_id` neu sind. Im vierten Fall bleiben alle
deterministischen Identitäten gleich.

### 6.8 Zeit und Zeitzonen

Alle Manifestzeitpunkte MÜSSEN UTC verwenden.

Zeitstempel dürfen die `run_id` und den Run-Nachweis beeinflussen, aber keine deterministische `build_id`.

---

## 7. Bytegleichheit und semantische Gleichheit

### 7.1 Bytegleichheit

Bytegleichheit liegt vor, wenn zwei Dateien denselben SHA-256-Bytehash besitzen.

Sie ist für folgende Artefakte anzustreben:

- kanonische JSON-Manifeste;
- reine Textkonfigurationen;
- JSON-Schemata;
- kleine normative CSV-Tabellen bei vollständig fixierter Serialisierung.

### 7.2 Parquet-Einschränkung

Parquet-Dateien können trotz identischer Tabelleninhalte unterschiedliche Bytes besitzen, beispielsweise durch:

- Bibliotheksversionen;
- Writer-Metadaten;
- Kompressionsversionen;
- Row-Group-Grenzen;
- Dictionary-Encoding;
- Dateimetadaten.

Deshalb MUSS RCC-002 für tabellarische Daten neben dem Datei-Bytehash einen semantischen Fingerprint speichern.

### 7.3 Semantischer Fingerprint

Der semantische Fingerprint MUSS mindestens berücksichtigen:

- normierte Spaltenreihenfolge;
- logische Datentypen;
- definierte Nullrepräsentation;
- vollständigen registrierten kanonischen Primärschlüssel;
- kanonische Zeilenreihenfolge nach diesem Primärschlüssel;
- Zeilenanzahl;
- Werte einschließlich expliziter Fließkommaregel;
- Schema-Version.

Für kanonische RCC-002-Marktdaten ist der Primärschlüssel und damit die Sortierreihenfolge:

1. `market_type`;
2. `symbol`;
3. `interval`;
4. `open_time`.

Für noch nicht konsolidierte Multi-Provider-Daten MUSS `provider` unmittelbar
vor `market_type` als weiterer Schlüsselbestandteil und damit als erster
Sortierbestandteil registriert werden. Andere Tabellen MÜSSEN ihren
vollständigen Primärschlüssel im Schema registrieren; eine optionale oder
implizite Ereignis-ID ist unzulässig.

Der `semantic_sha256` DARF folgende physische Merkmale NICHT berücksichtigen:

- Dateigrenzen;
- Verzeichnis- oder Partitionierungsstruktur;
- Row-Group-Grenzen;
- Kompressionsalgorithmus oder -stufe;
- Dictionary-Encoding;
- Writer-Version;
- Container-Metadaten.

Diese Merkmale MÜSSEN separat in einem `physical_layout_sha256` erfasst werden. Dessen Vorabbildung MUSS mindestens Dateigrenzen, Partitionsschlüssel und -werte, Row-Group-Profil, Kompressionsprofil, Writerprofil und relevante Containerparameter enthalten.

Die Vorabbildung MUSS zusätzlich
`physical_publication_configuration_sha256` enthalten. Derselbe physische
Konfigurationshash darf nur verwendet werden, wenn die vollständig aufgelöste
physische Konfiguration identisch ist.

### 7.4 Gleichheitsklassen

| Klasse | Anforderung |
|---|---|
| E0 | Keine Gleichheitsaussage |
| E1 | Schema und Zeilenanzahl gleich |
| E2 | Semantischer Fingerprint gleich |
| E3 | Bytehash gleich |

Veröffentlichte RCC-002-Daten MÜSSEN mindestens E2 erreichen.

Ein bereits persistiertes unveränderliches Manifest oder JSON-Schema MUSS bei jeder späteren Verifikation E3 erreichen. Separat erzeugte Run Manifeste verschiedener Runs müssen wegen `run_id` und Laufzeitstempeln nicht bytegleich sein. E3 zwischen zwei Erzeugungen ist nur dann verpflichtend, wenn ihre vollständige kanonische Vorabbildung einschließlich aller Laufzeitfelder identisch ist.

---

## 8. Manifestarchitektur

### 8.1 Manifesttypen

RCC-002 MUSS mindestens folgende Manifesttypen unterstützen:

| Manifest | Zweck |
|---|---|
| Source Manifest | Externe Quelle und Rohdaten-Snapshot |
| Stage Manifest | Ein- und Ausgaben einer Stufe S0–S8 |
| Run Manifest | Konkrete Ausführung und Umgebung |
| Dataset Manifest | Gesamter veröffentlichter Datenstand |
| Review Manifest | Reviews, Befunde und Freigaben |
| Reproduction Manifest | Ergebnis eines unabhängigen Rebuilds |

### 8.2 Gemeinsame Pflichtfelder

Jedes Manifest MUSS enthalten:

```json
{
  "manifest_schema_id": "string",
  "manifest_schema_version": "string",
  "manifest_schema_ref": "string",
  "manifest_type": "string",
  "manifest_id": "string",
  "created_at_utc": "string",
  "producer": {
    "component": "string",
    "version": "string"
  },
  "project": "RCC-002",
  "status": "string"
}
```

Für sämtliche Stage-, View-, State- und Manifestschemas gilt:

```text
schema_id=<unversionierte ID>
schema_version=<SemVer>
schema_ref=<schema_id>/<schema_version>
```

`schema_ref` ist ausschließlich die deterministisch abgeleitete qualifizierte
Referenz. Eine Version im Wert von `schema_id` ist unzulässig.

`created_at_utc` gehört zum Manifestnachweis, aber nicht zur deterministischen Build-Vorabbildung.

### 8.3 Source Manifest

Das Source Manifest ist das alleinige normative Eigentümerobjekt der
kanonischen S0-Provenienzfelder:

| Feld | Bedeutung |
|---|---|
| `source_snapshot_id` | deterministische Identität der Quelldatenfassung |
| `provider` | kanonische Providerbezeichnung |
| `market_type` | registrierter Markttyp |
| `symbol` | registriertes Symbol |
| `interval` | registriertes Datenintervall |
| `retrieved_at_utc` | tatsächlicher Abrufzeitpunkt, nur Provenienz |
| `source_file_name` | portabler Quelldateiname |
| `source_byte_sha256` | SHA-256 der unveränderten Quellbytes |
| `source_revision` | Providerrevision, soweit verfügbar |
| `source_format` | registrierte Format- und Schemafamilie |
| `source_location` | portable Herkunftsreferenz |
| `license_or_terms_ref` | optionale Referenz auf Nutzungsbedingungen |

`source_provider` und `source_retrieved_at_utc` sind ausschließlich
historische Eingangsaliase. Die einzige zulässige gerichtete
Migrationsabbildung lautet:

```text
source_provider           -> provider
source_retrieved_at_utc   -> retrieved_at_utc
```

Die umgekehrte Aliasrichtung und die parallele Ausgabe beider Namen sind
unzulässig.

`timezone`, `expected_start` und `expected_end` sind keine
Source-Manifest-Felder. Sie werden ausschließlich unter
`semantic_build_configuration.source_expectations` manifestiert. Ein
Validierungsauftrag referenziert diese Konfiguration und darf keine
konkurrierenden Werte enthalten.

Das Manifest MUSS zusätzlich die angewandte Migrationsprofil-ID und deren
Version referenzieren, wenn Aliasfelder importiert wurden.

### 8.4 Stage Manifest

Jede Stufe MUSS dokumentieren:

- `stage_id`;
- `stage_version`;
- `build_id`;
- `run_id`;
- akzeptierte Eingangsschema-ID, Version und daraus abgeleitete Referenz;
- erzeugte Ausgangsschema-ID, Version und daraus abgeleitete Referenz;
- Eingangs- und Ausgangsschema-Fingerprint;
- Parent-Artefakte;
- Ausgabeartefakte;
- `semantic_build_configuration_sha256`;
- `physical_publication_configuration_sha256`, soweit die Stufe physisch
  publiziert;
- Codeprovenienz;
- Spezifikationsprofil;
- Komponenten-ID und Version;
- Profil-, Modell-, State-, Enum- und Reason-Code-Registry-Versionen;
- Feldregistry- und Kompatibilitätsprofil;
- Zeilen- und Zeitbereichsstatistiken;
- Primärschlüssel- und Sortierungsnachweis;
- Segment- und Gültigkeitsreconciliation;
- Validierungsergebnisse;
- Warnungen;
- Fehlerstatus;
- Veröffentlichungsstatus.

Für `S2_VALIDATED` MUSS das Stage Manifest mindestens
`market_segment_id`, `quality_gate_pass`, `quality_rule_version` und die
S2-Reason-Code-Registry referenzieren.

Für `S3_INDICATORS` MUSS es `indicator_segment_id` getrennt von
`market_segment_id` nachweisen.

Für `S5_REGIMES` und `S6_GATES` MUSS es die kanonischen Regime- und
Gate-Schema-, Modell-, Profil-, State- und Reason-Code-Identitäten
referenzieren.

Für `S7_LABELS` MUSS es Horizon-, Label-, Kosten-, Barrier-, Numerik- und
Reason-Code-Profile sowie die Leakage-Klasse der erzeugten Felder
referenzieren.

### 8.5 Dataset Manifest

Das Dataset Manifest MUSS mindestens enthalten:

```json
{
  "dataset_id": "dataset:sha256:<digest>",
  "dataset_artifact_set_id": "dataset-artifact-set:sha256:<digest>",
  "dataset_profile": "rcc002-canonical",
  "build_id": "build:sha256:<digest>",
  "source_snapshot_ids": [],
  "artifacts": [],
  "stages": [],
  "schemas": [],
  "field_registries": [],
  "views": [],
  "specification_profile": [],
  "code_provenance": {},
  "semantic_build_configuration": {
    "canonical_sha256": "string"
  },
  "physical_publication_configuration": {
    "canonical_sha256": "string"
  },
  "environment_reference": {},
  "quality_summary": {},
  "dataset_lineage": {},
  "knowledge_lineage": {},
  "publication": {},
  "reviews": []
}
```

### 8.6 JSON Schema

Jeder Manifesttyp MUSS durch ein versioniertes JSON Schema validiert werden.

Die erste Baseline reserviert:

| Manifesttyp | `schema_id` | `schema_version` | `schema_ref` |
|---|---|---|---|
| Source Manifest | `rcc002.source-manifest` | `1.0.0` | `rcc002.source-manifest/1.0.0` |
| Stage Manifest | `rcc002.stage-manifest` | `1.0.0` | `rcc002.stage-manifest/1.0.0` |
| Run Manifest | `rcc002.run-manifest` | `1.0.0` | `rcc002.run-manifest/1.0.0` |
| Dataset Manifest | `rcc002.dataset-manifest` | `1.0.0` | `rcc002.dataset-manifest/1.0.0` |
| Review Manifest | `rcc002.review-manifest` | `1.0.0` | `rcc002.review-manifest/1.0.0` |
| Reproduction Manifest | `rcc002.reproduction-manifest` | `1.0.0` | `rcc002.reproduction-manifest/1.0.0` |

Die Schemaidentität MUSS:

- eindeutig;
- versioniert;
- unveränderlich nach Release;
- im Manifest referenziert

sein.

Ein Manifest, das sein Schema nicht erfüllt, DARF NICHT veröffentlicht werden.

### 8.7 Kanonisches Stufen- und View-Schemaregister

Das Manifest MUSS die vom Dokument
`RCC_002_DATA_PIPELINE_SPECIFICATION` autoritativ definierten
logischen Schemas referenzieren:

| Stufe | `schema_id` | `schema_version` | `schema_ref` |
|---|---|---|---|
| `S0_SOURCE` | `rcc002.stage.s0-source` | `1.0.0` | `rcc002.stage.s0-source/1.0.0` |
| `S1_NORMALIZED` | `rcc002.stage.s1-normalized` | `1.0.0` | `rcc002.stage.s1-normalized/1.0.0` |
| `S2_VALIDATED` | `rcc002.stage.s2-validated` | `1.0.0` | `rcc002.stage.s2-validated/1.0.0` |
| `S3_INDICATORS` | `rcc002.stage.s3-indicators` | `1.0.0` | `rcc002.stage.s3-indicators/1.0.0` |
| `S4_SIGNALS` | `rcc002.stage.s4-signals` | `1.0.0` | `rcc002.stage.s4-signals/1.0.0` |
| `S5_REGIMES` | `rcc002.stage.s5-regimes` | `1.0.0` | `rcc002.stage.s5-regimes/1.0.0` |
| `S6_GATES` | `rcc002.stage.s6-gates` | `1.0.0` | `rcc002.stage.s6-gates/1.0.0` |
| `S7_LABELS` | `rcc002.stage.s7-labels` | `1.0.0` | `rcc002.stage.s7-labels/1.0.0` |

Für S8 MUSS jedes veröffentlichte View-Artefakt genau eine registrierte
View-Schemaidentität referenzieren:

| `schema_id` | `schema_version` | `schema_ref` | S7 zulässig | `allowlist_sha256` |
|---|---|---|:---:|---|
| `rcc002.view.research-features` | `1.0.0` | `rcc002.view.research-features/1.0.0` | Nein | `2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e` |
| `rcc002.view.backtest-inputs` | `1.0.0` | `rcc002.view.backtest-inputs/1.0.0` | Nein | `2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e` |
| `rcc002.view.paper` | `1.0.0` | `rcc002.view.paper/1.0.0` | Nein | `2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e` |
| `rcc002.view.live` | `1.0.0` | `rcc002.view.live/1.0.0` | Nein | `2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e` |
| `rcc002.view.label-research` | `1.0.0` | `rcc002.view.label-research/1.0.0` | Ja | `0e223d60ed4139f73194f1cb3b886a8eface9229183ad522a093e966827518cc` |
| `rcc002.view.audit` | `1.0.0` | `rcc002.view.audit/1.0.0` | Ja | `3c29f3219e65ca87df199a52dc8d15b54a6ea28884a863d1479d27e8a2401b56` |

Die vollständig expandierten Listen und ihre kanonische Hashvorabbildung
stehen autoritativ in
`RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`, Version `0.7.1`,
Abschnitt 7.9. Die zugehörige Eigentums- und Leakage-Registry lautet
`RCC002_S8_FIELD_OWNERSHIP_V1`, Version `1.0.0`.

Das Manifest referenziert für jede View:

- View-Schema-ID, Version und abgeleitete Referenz;
- logischen Schema-Fingerprint;
- Hash der positiven Feld-Allowlist;
- geordnete erlaubte Felder;
- Eigentümerstufe jedes Feldes;
- Leakage-Klasse jedes Feldes;
- angewandtes Kompatibilitätsprofil.

Eine View mit unbekanntem Feld, fehlender Eigentümerstufe oder nicht
registrierter Schemaerweiterung ist fail-closed abzulehnen.

Research-Feature-, Backtest-Input-, Paper- und Live-Views DÜRFEN kein Feld
mit `field_owner_stage=S7_LABELS` enthalten. Die zusätzliche Präfixprüfung
MUSS `fwd_`, `label_` und `barrier_` ablehnen, ersetzt aber nicht die
stufenbasierte Prüfung.

#### 8.7.1 Row Preservation für S8-Views

Für jedes erfolgreich erzeugte kanonische S8-View-Artefakt MUSS gelten:

```text
S8_rows = S7_rows
```

je View, bezogen auf den vollständigen kanonischen Primärschlüssel
`(market_type, symbol, interval, open_time)` und, bei unkonsolidierten
Multi-Provider-Daten, zusätzlich `provider`.

Row Identity MUSS vollständig erhalten bleiben. Row Order MUSS vollständig
erhalten bleiben.

Export-, Manifest-, Hash- und Reproduzierbarkeitsprozesse DÜRFEN keine
kanonischen Zeilen:

- entfernen,
- zusammenführen,
- duplizieren,
- umordnen.

Dies konkretisiert für S8 das kanonische Row-Preservation-Prinzip aus
`RCC_002_DATA_PIPELINE_SPECIFICATION` §5.8: `quality_gate_pass` und die
positive Feld-Allowlist jeder View bestimmen die semantische Verwendbarkeit
und den Feldumfang einer Zeile, nicht ihre kanonische Existenz im
S8-Artefakt.

Die einzige zulässige Ausnahme von dieser Zeilenerhaltung ist ein
ausdrücklich normierter vollständiger Build-Abbruch oder eine
Artefakt-Quarantäne. Beide wirken auf das gesamte Artefakt oder den
gesamten Build, nicht auf einzelne Zeilen.

### 8.8 Schemaeigentum

Die Data-Pipeline-Spezifikation `RCC_002_DATA_PIPELINE_SPECIFICATION` ist
Eigentümerin der logischen
Stufen- und Viewverträge.

Dieses Dokument `RCC-002-RM` ist Eigentümer der:

- physischen Artefaktidentitäten;
- Manifesttypen und Manifest-Schemas;
- physischen Layoutidentitäten;
- atomaren Veröffentlichung;
- Reproduktions- und Gleichheitsnachweise.

Ein Manifest darf keinen logischen Fachvertrag eigenmächtig erweitern.

---

## 9. Codeprovenienz

### 9.1 Pflichtfelder

```json
{
  "repository": "<repository URL or canonical repository identifier>",
  "commit_sha": "<40-hex commit>",
  "branch_observed": "<informational>",
  "worktree_clean": true,
  "dirty_patch_sha256": null,
  "submodules": [],
  "entrypoint": "<module or command>",
  "code_profile": "<profile id>"
}
```

### 9.2 Commit und Branch

Der Commit-SHA ist normativ. Der Branchname ist nur informativ, da sich Branchzeiger verändern können.

### 9.3 Dirty Worktree

Kanonische Release-Builds SOLLEN aus einem sauberen Arbeitsbaum entstehen.

Falls ein Forschungsbuild aus einem nicht sauberen Arbeitsbaum erfolgt:

- `worktree_clean` MUSS `false` sein;
- ein kanonischer Patch MUSS gesichert werden;
- dessen SHA-256 MUSS in die Build-ID eingehen;
- unversionierte relevante Dateien MÜSSEN eingeschlossen werden;
- der Build DARF nicht als zertifizierter Release gelten, solange die Änderungen nicht versioniert sind.

### 9.4 Generierter Code

Generierter Code MUSS mit Generatorversion, Eingabeartefakten und Ausgabehash dokumentiert werden.

---

## 10. Umgebungsprovenienz

### 10.1 Pflichtumfang

Der Run-Nachweis MUSS mindestens erfassen:

- Betriebssystem und Version;
- WSL-Version beziehungsweise Kernel, falls zutreffend;
- Python-Version, für RCC-002 Zielbaseline Python 3.12;
- Paketlock oder vollständige Paketliste;
- Architektur;
- CPU-Modell;
- Threadkonfiguration;
- Locale;
- Zeitzone;
- relevante Umgebungsvariablen;
- NumPy-, Pandas-, PyArrow- und BLAS-Versionen;
- Kompressionsbibliotheken;
- Random-Seed-Register;
- Hardwarebeschleuniger, falls verwendet.

### 10.2 Deterministisches Umgebungsidentitätsprofil

Ob und welche Umgebungsmerkmale den `build_id` beeinflussen, wird ausschließlich durch ein versioniertes Allowlist-Profil bestimmt.

Das für logisch-semantische Build-Identität verbindliche Profil lautet:

```text
profile_id=RCC_BUILD_ENV_IDENTITY_V2
```

`RCC_BUILD_ENV_IDENTITY_V2` MUSS enthalten:

- Python-Haupt- und Nebenversion;
- Hash der gesperrten Python-Pakete und relevanten nativen Numerikbibliotheken;
- Zeitzone `UTC`;
- kanonisches Locale-Profil;
- registriertes numerisches Präzisions- und Rundungsprofil;
- registrierte Thread- und BLAS-Determinismusparameter;
- registriertes semantisches Numerik- und Fingerprintprofil.

Writer-, Kompressions-, Row-Group-, Partitionierungs- und sonstige
Containerprofile MÜSSEN in der physischen Artefaktprovenienz und im
`physical_layout_sha256` stehen. Sie DÜRFEN den logischen `build_id` NICHT
beeinflussen.

Folgende Merkmale sind standardmäßig ausschließlich Run-Metadaten und DÜRFEN unter `RCC_BUILD_ENV_IDENTITY_V2` den `build_id` NICHT beeinflussen:

- Hostname;
- Benutzername;
- absolute lokale Pfade;
- Start- und Endzeit des Runs;
- CPU-Modell;
- Gerätename.

Ein solches Merkmal darf nur durch eine neue versionierte Profil-ID aufgenommen werden, wenn reproduzierbare Evidenz seine semantische Relevanz nachweist. Profiländerungen DÜRFEN NICHT still erfolgen.

### 10.3 Paketumgebung

Ein ungeprüftes `pip freeze` allein ist nicht ausreichend, wenn:

- lokale Pfade enthalten sind;
- transitive native Bibliotheken fehlen;
- nicht reproduzierbare VCS-Referenzen verwendet werden.

Der Reproduktionssatz SOLL enthalten:

- Lockdatei;
- `pip freeze`;
- Python-Version;
- native Bibliotheksinformationen;
- Container- oder Environment-Definition, falls vorhanden.

### 10.4 Locale und Zeitzone

Builds MÜSSEN unabhängig von lokalen Geräteeinstellungen UTC und definierte numerische Formate verwenden.

Die Umgebung SOLL setzen:

```text
TZ=UTC
LC_ALL=C.UTF-8
LANG=C.UTF-8
```

### 10.5 Threads und numerische Bibliotheken

Threadzahl und BLAS-Backend MÜSSEN protokolliert werden, wenn sie Reduktionsreihenfolgen oder Ergebnisse beeinflussen können.

Für zertifizierte Rebuilds SOLLEN die deterministisch relevanten Threadparameter fixiert sein.

### 10.6 Geheimnisse

Manifeste DÜRFEN NICHT enthalten:

- API-Schlüssel;
- Passwörter;
- Zugriffstokens;
- private Schlüssel;
- vollständige Verbindungszeichenfolgen;
- personenbezogene Zugangsdaten.

Erlaubt sind abstrakte Secret-Referenzen wie:

```text
secret_ref:binance_public_market_data
```

---

## 11. Dataset Lineage

### 11.1 Grundsatz

Jedes Datenartefakt MUSS seine direkten Eltern referenzieren. Aus den direkten Beziehungen MUSS ein vollständiger gerichteter azyklischer Graph rekonstruierbar sein.

### 11.2 Lineage-Knoten

Ein Knoten MUSS enthalten:

- `artifact_id`;
- Artefakttyp;
- Stufe;
- Schema-ID;
- Schemaversion und Schema-Fingerprint;
- Feldregistry- und Allowlist-Hash, soweit anwendbar;
- Bytehash;
- semantischen Fingerprint;
- Dateigröße;
- Zeilenanzahl;
- Spaltenanzahl;
- Zeitbereich;
- Symbolbereich;
- Partitionsinformationen;
- Status.

### 11.3 Lineage-Kanten

Eine Kante MUSS enthalten:

- Parent-`artifact_id`;
- Child-`artifact_id`;
- Transformation;
- `build_id`;
- `run_id`;
- Filter- oder Selektionsinformation;
- gegebenenfalls Revisionsbeziehung.

### 11.4 Vollständigkeitsregel

Ein veröffentlichtes Artefakt ohne vollständig auflösbare Elternkette bis zu einem Source Snapshot ist unzulässig.

### 11.5 S0–S8-Abdeckung

Die Lineage MUSS sichtbar machen:

```text
Source Snapshot
→ S0_SOURCE
→ S1_NORMALIZED
→ S2_VALIDATED
→ S3_INDICATORS
→ S4_SIGNALS
→ S5_REGIMES
→ S6_GATES
→ S7_LABELS
→ S8_EXPORT
```

Ausgelassene Stufen MÜSSEN explizit als nicht anwendbar begründet werden.

### 11.6 Historische Artefakte

Rekonstruierte oder mutmaßlich abgeschnittene historische Artefakte MÜSSEN entsprechend markiert werden:

```text
provenance_status: reconstructed
integrity_status: historically_verified | partially_verified | suspected_truncated
canonical: false
```

Die bekannte historische Regime-Datei mit 1.048.575 Datenzeilen darf wegen des starken Excel-Trunkierungsindizes nicht als kanonische RCC-002-Quelle behandelt werden.

---

## 12. Knowledge Lineage

### 12.1 Zweck

Knowledge Lineage dokumentiert nicht nur, welcher Code lief, sondern warum eine Regel existiert und auf welcher Evidenz sie beruht.

### 12.2 Pflichtobjekte

Knowledge Lineage MUSS enthalten:

- Spezifikationsdokumente mit Dokument-ID und Version;
- wissenschaftliche Entscheidungen;
- Annahmen;
- Hypothesen;
- bekannte Unsicherheiten;
- historische Rekonstruktionen;
- empirische Verifikationen;
- verworfene Alternativen, soweit entscheidungsrelevant;
- Reviewbefunde;
- Freigabeentscheidungen.

### 12.3 Spezifikationsprofil

Das kanonische RCC-002-Profil MUSS mindestens folgende Dokumente
referenzieren:

| Dokument-ID | Version |
|---|---:|
| `RCC_002_DATA_PIPELINE_SPECIFICATION` | `0.7.1` |
| `RCC-002-DV` | `0.4.2` |
| `RCC-002-IS` | `0.4.3` |
| `RCC-002-ST` | `0.4.2` |
| `RCC-002-RG` | `0.5.1` |
| `RCC-002-LF` | `0.4.1` |
| `RCC-002-RM` | `0.7.1` |

Eine bloße Dateinennung ohne Dokument-ID und Version ist nicht ausreichend.

### 12.4 Entscheidungsobjekt

Empfohlenes Format:

```json
{
  "decision_id": "RCC-002-DEC-<number>",
  "title": "string",
  "status": "proposed|accepted|rejected|superseded",
  "effective_from_specification_profile": "string",
  "evidence": [],
  "assumptions": [],
  "alternatives": [],
  "supersedes": [],
  "review_records": []
}
```

### 12.5 Verifizierte historische Erkenntnisse

Die Knowledge Lineage SOLL die bereits empirisch bestätigten Rekonstruktionen referenzieren:

- zwölf historische BTC-Signalregeln mit null Abweichungen über 2.721.034 Zeilen;
- historische Regimeregeln mit null Abweichungen über 1.048.575 Zeilen;
- Trunkierungsverdacht der historischen Regimedatei;
- Trennung historischer binärer Signale von späteren kontinuierlichen GS-Scores;
- bewusste modulare Trennung von Regime und Handels-Gates in RCC-002.

Diese Evidenz begründet Architekturentscheidungen, ersetzt aber keine RCC-002-Neuvalidierung.

---

## 13. Artefaktinventar

Jeder Build MUSS ein Inventar führen:

| Feld | Bedeutung |
|---|---|
| `logical_name` | Stabile fachliche Bezeichnung |
| `artifact_id` | Identität des gespeicherten Artefakts |
| `relative_path` | Pfad innerhalb des Reproduktionssatzes |
| `media_type` | Dateityp |
| `schema_id` | Logisches Schema |
| `schema_version` | Logische Schemaversion |
| `schema_ref` | Qualifizierte Referenz `<schema_id>/<schema_version>` |
| `schema_fingerprint_sha256` | Hash des vollständigen logischen Schemavertrags |
| `field_registry_sha256` | Hash der geordneten Feldregistry |
| `view_allowlist_sha256` | Hash der positiven View-Allowlist, soweit anwendbar |
| `byte_sha256` | Hash der gespeicherten Datei |
| `semantic_sha256` | Hash des kanonischen Inhalts |
| `physical_layout_sha256` | Hash von Partitionierung, Dateigrenzen und Containerprofil |
| `size_bytes` | Dateigröße |
| `row_count` | Zeilenzahl |
| `min_timestamp_utc` | Frühester Datenzeitpunkt |
| `max_timestamp_utc` | Spätester Datenzeitpunkt |
| `publication_status` | Status |

Absolute lokale Pfade dürfen ergänzend im Run Manifest stehen, dürfen aber nicht die portable Artefaktidentität definieren.

---

## 14. Build- und Publikationszustände

### 14.1 Zustandsmodell

| Status | Bedeutung |
|---|---|
| `planned` | Build definiert, nicht gestartet |
| `running` | Ausführung aktiv |
| `validating` | Ausgaben vorhanden, Prüfungen aktiv |
| `failed` | Build oder Pflichtprüfung fehlgeschlagen |
| `quarantined` | Artefakte isoliert, nicht freigegeben |
| `candidate` | Prüfungen bestanden, Freigabe ausstehend |
| `published` | Atomar veröffentlicht |
| `superseded` | Durch neueren Datenstand ersetzt |
| `withdrawn` | Nach Veröffentlichung zurückgezogen |

### 14.2 Atomare Veröffentlichung

Ein Build MUSS zunächst in einem eindeutigen temporären Verzeichnis schreiben.

Veröffentlichung darf erst erfolgen, wenn:

- alle Pflichtartefakte existieren;
- alle Prüfsummen berechnet sind;
- alle Manifest-Schemata gültig sind;
- alle Pflichtprüfungen bestanden sind;
- kein Parent-Artefakt fehlt;
- das Dataset Manifest vollständig ist.

Die Veröffentlichung MUSS durch atomare Umbenennung oder ein funktional gleichwertiges Commit-Verfahren erfolgen.

### 14.3 Kein stilles Überschreiben

Ein bereits veröffentlichter `dataset_artifact_set_id` und sämtliche ihm
zugeordneten Artefakte sind unveränderlich.

Eine semantisch identische Neuverpackung oder Repartitionierung DARF denselben
`dataset_id` behalten, MUSS jedoch einen neuen `dataset_artifact_set_id`
erzeugen.

Bestehende Artefaktmengen und ihre Dateien DÜRFEN dabei NICHT überschrieben,
ersetzt oder still verändert werden.

Ein neuer Inhalt MUSS:

- eine neue Identität erhalten;
- die Vorgängerversion über `supersedes` referenzieren;
- die alte Fassung erhalten.

### 14.4 Teilergebnisse

Teilergebnisse dürfen für Diagnosezwecke erhalten bleiben, MÜSSEN jedoch als `failed` oder `quarantined` markiert werden und DÜRFEN NICHT unter einem finalen Veröffentlichungspfad erscheinen.

---

## 15. Inkrementelle Builds und Revisionen

### 15.1 Inkrementelle Erweiterung

Ein inkrementeller Build MUSS dokumentieren:

- Basis-`dataset_id`;
- neu hinzugefügten Zeitbereich;
- überlappenden Prüfbereich;
- geänderte Source Snapshots;
- betroffene Partitionen;
- unveränderte Partitionen;
- neue Gesamtidentität.

### 15.2 Indikator-Warm-up

Inkrementelle Berechnung MUSS für rollierende und rekursive Indikatoren genügend historische Vorlaufdaten laden.

Der Manifestnachweis MUSS unterscheiden:

- geladener Berechnungsbereich;
- veröffentlichter Zielbereich;
- verworfener Warm-up-Bereich.

### 15.3 Revision externer Quelldaten

Wenn der Anbieter historische Quelldaten revidiert:

- entsteht ein neuer `source_snapshot_id`;
- betroffene Nachfahren erhalten neue IDs;
- die Revision MUSS dokumentiert werden;
- frühere Datenstände bleiben unverändert erhalten;
- `supersedes` und Revisionsgrund MÜSSEN gesetzt werden.

### 15.4 Partielle Wiederverwendung

Wiederverwendete Partitionen MÜSSEN per Hash verifiziert werden. Ein Pfad- oder Dateinamensvergleich reicht nicht aus.

---

## 16. Geräteübergreifende Reproduktion

### 16.1 Zielgeräte

RCC-002 muss grundsätzlich auf folgenden Projektgeräten nachvollziehbar sein:

- X1 Carbon;
- G15/AR15;
- Workstation.

Die Workstation bleibt für vollständige Mehrmillionen-Zeilen-Builds das bevorzugte Ausführungsgerät. Das darf die Portabilität der Spezifikation nicht einschränken.

### 16.2 Gleichheitserwartung

| Situation | Erwartung |
|---|---|
| Gleicher Code, gleiche Lockdatei, identisches `RCC_BUILD_ENV_IDENTITY_V2` | E2 verpflichtend; E3 für Datencontainer nur bei identischem physischen Layoutprofil |
| Unterschiedliche Geräte, sonst identisches Umgebungsidentitätsprofil | E2 verpflichtend; Host- und CPU-Unterschiede allein erzeugen keine neue Build-ID |
| Unabhängige Implementierung derselben Formel | Fachlich definierte Toleranzprüfung plus identische Klassifikationen |
| Unterschiedliche Bibliotheksversionen | Kein Gleichheitsanspruch ohne dokumentierte Kompatibilitätsprüfung |

### 16.3 Numerische Toleranzen

Toleranzen dürfen nur für den Vergleich unabhängiger oder technisch abweichender Implementierungen genutzt werden.

Ein wiederholter Build in derselben gesperrten Umgebung SOLL exakte semantische Gleichheit liefern.

Toleranzen MÜSSEN:

- pro Feld oder Feldklasse festgelegt;
- wissenschaftlich begründet;
- absolut und/oder relativ angegeben;
- vor dem Vergleich definiert;
- im Reproduction Manifest protokolliert

sein.

Toleranzen dürfen keine Regime-, Gate- oder Labelabweichungen verdecken.

### 16.4 Cross-Device-Protokoll

Ein Gerätevergleich MUSS enthalten:

- Quell- und Zielgerät;
- `build_id`;
- beide `run_id`s;
- Umgebungsdifferenzen;
- Bytevergleich;
- semantischen Vergleich;
- Feldtoleranzbericht;
- Klassifikationsvergleich;
- Ergebnisstatus.

---

## 17. Reproduktionssatz

Ein vollständiger Reproduktionssatz MUSS enthalten:

1. Dataset Manifest;
2. alle Stage Manifests;
3. Run Manifest;
4. Source Manifest oder auflösbare Quellenreferenzen;
5. Code-Commit und gegebenenfalls Dirty Patch;
6. vollständig aufgelöste `semantic_build_configuration`;
7. vollständig aufgelöste `physical_publication_configuration`;
8. Lock- und Umgebungsdateien;
9. Manifest-, Stufen- und View-Schemas;
10. Feldregistries und positive View-Allowlists;
11. Spezifikationsprofil;
12. Artefaktinventar;
13. Prüfsummenliste;
14. Validierungs- und Reconciliation-Berichte;
15. dokumentierten Build-Einstiegspunkt;
16. Rebuild-Anweisung;
17. Review- und Freigabestatus.

### 17.1 Rebuild-Einstiegspunkt

Die Implementierung MUSS einen nichtinteraktiven Einstiegspunkt anbieten.

Konzeptionelles Beispiel:

```bash
PYTHONPATH=. python3 -m scripts.build_rcc002 \
  --config configs/rcc002/canonical.json \
  --source-manifest manifests/source/<source_snapshot_id>.json \
  --output-root build/rcc002
```

Der endgültige Befehl wird durch die Implementierung festgelegt und MUSS im Manifest wortgetreu gespeichert werden.

### 17.2 Offline-Reproduktion

Wenn Quelldaten lizenz- oder größenbedingt nicht gebündelt werden können, MUSS der Reproduktionssatz wenigstens:

- eindeutige Quellenreferenzen;
- Prüfsummen;
- Abrufparameter;
- erwartete Größen;
- Zeitabdeckung;
- Integritätsprüfungen

enthalten.

---

## 18. Validierung und Tests

### 18.1 Manifesttests

Pflichttests:

- JSON-Schema gültig;
- alle Pflichtfelder vorhanden;
- alle IDs syntaktisch gültig;
- `manifest_id` korrekt;
- keine zirkuläre ID-Abhängigkeit;
- alle Referenzen auflösbar;
- keine Geheimnisse;
- UTC-Zeitstempel gültig;
- Statusübergänge gültig.

### 18.2 Artefakttests

- Datei vorhanden;
- Bytehash korrekt;
- semantischer Fingerprint korrekt;
- Schema korrekt;
- Zeilenzahl korrekt;
- Zeitbereich korrekt;
- Spaltenreihenfolge korrekt;
- Parent-Beziehung korrekt.

### 18.3 Lineagetests

- Graph azyklisch;
- jedes veröffentlichte Artefakt bis zur Quelle rückverfolgbar;
- keine verwaisten Knoten;
- keine widersprüchlichen Parent-Beziehungen;
- Stage-Reihenfolge fachlich zulässig;
- alle Spezifikationsreferenzen auflösbar.

### 18.4 Rebuildtests

Mindestens:

- Wiederholungsbuild auf demselben Gerät;
- Clean-Environment-Build;
- Cross-Device-Semantikvergleich;
- absichtliche Inputänderung erzeugt neue Build-ID;
- reine Run-Zeitänderung verändert nicht die Build-ID;
- semantische Konfigurationsänderung erzeugt neue Build-ID;
- semantische Konfigurationsänderung erzeugt auch bei zufällig identischem
  Output eine neue Dataset-ID;
- reine physische Konfigurationsänderung behält Build- und Dataset-ID;
- reine physische Konfigurationsänderung erzeugt neue physische
  Artefaktidentitäten;
- Dirty Patch erzeugt neue Build-ID;
- Manifeständerung erzeugt neue Manifest-ID, aber keine rückwirkende Zirkularität.

Zusätzlich:

- alle acht Stufenschema-IDs sind registriert und auflösbar;
- jede Stage-Manifest-Schnittstelle besitzt Eingangs- und Ausgangsschema;
- jede S8-View besitzt eine positive Feld-Allowlist;
- jedes View-Feld besitzt Eigentümerstufe und Leakage-Klasse;
- jedes S7-Feld wird aus Research-Feature-, Backtest-Input-, Paper- und
  Live-Views ausgeschlossen;
- `fwd_`, `label_` und `barrier_` werden zusätzlich präfixbasiert abgelehnt;
- unbekannte Felder und unbekannte Major-Schemaversionen werden fail-closed
  abgelehnt;
- S2-`market_segment_id` und S3-`indicator_segment_id` bleiben getrennt;
- S5-/S6-Modell-, Profil-, State- und Reason-Code-Identitäten bleiben
  auflösbar;
- S7-Horizon-Registry und S7-Feldregistry stimmen mit dem logischen
  S7-Schema überein.

Für jedes erfolgreich erzeugte S8-Artefakt MUSS zusätzlich geprüft werden:

- `S8_rows == S7_rows`;
- vollständige Row Identity Preservation;
- vollständige Row Order Preservation;
- Manifest-Konsistenz;
- Hash-Konsistenz.

### 18.5 Negativtests

Die Tests MÜSSEN fehlschlagen bei:

- manipuliertem Artefakt;
- fehlendem Parent;
- falschem Hash;
- ungültigem Schema;
- Geheimnis im Manifest;
- unbekannter Spezifikationsversion;
- stillem Überschreiben;
- unzulässiger Statusfolge;
- nichtkanonischem Zeitstempel;
- ungeklärtem historischen Artefakt als kanonischer Quelle;
- nicht klassifiziertem Konfigurationsschlüssel;
- demselben Schlüssel in beiden Konfigurationsklassen;
- physischem Parameter in der Build-ID-Vorabbildung;
- semantischem Parameter ausschließlich in der physischen Konfiguration;
- S7-Feld in einer nicht labelberechtigten View;
- View-Feld ohne Eigentümerstufe oder Leakage-Klasse.

---

## 19. Fehlerbehandlung und Wiederaufnahme

### 19.1 Fehlgeschlagener Build

Bei Fehler MUSS:

- der Runstatus `failed` werden;
- die fehlerhafte Stufe dokumentiert werden;
- der Fehlerbericht erhalten bleiben;
- kein finaler Dataset-Pfad veröffentlicht werden;
- vorhandene Teilartefakte quarantänisiert oder kontrolliert entfernt werden.

### 19.2 Wiederaufnahme

Eine Wiederaufnahme darf nur bereits abgeschlossene Stufen wiederverwenden, wenn:

- Parent-Hashes unverändert sind;
- Build-Vorabbildung unverändert ist;
- Artefakthashes stimmen;
- Stage Manifest gültig ist;
- Wiederverwendung im neuen Run Manifest dokumentiert wird.

### 19.3 Wiederholungsversuch

Jeder Versuch erhält eine neue `run_id`. Der `build_id` bleibt gleich, solange die deterministischen Eingaben gleich bleiben.

### 19.4 Quarantäne

Quarantänisierte Artefakte:

- dürfen nicht von produktiven Verbrauchern aufgelöst werden;
- müssen einen Grund enthalten;
- müssen den verursachenden Run referenzieren;
- dürfen nach Korrektur nicht still in-place freigegeben werden.

---

## 20. Audit und Berichterstattung

### 20.1 Auditbericht

Ein Release-Audit MUSS kompakt ausweisen:

- Dataset-ID;
- Build-ID;
- Run-ID des Veröffentlichungsbuilds;
- Source-Snapshot-IDs;
- Code-Commit;
- Spezifikationsprofil;
- `semantic_build_configuration_sha256`;
- `physical_publication_configuration_sha256`;
- Umgebungsprofil;
- Artefakte und Prüfsummen;
- Qualitätsprüfungen;
- Lineage-Status;
- Reviewstatus;
- bekannte Einschränkungen;
- Freigabeentscheidung.

### 20.2 Maschinen- und menschenlesbare Form

Die maschinenlesbaren JSON-Manifeste sind normativ.

Ein menschenlesbarer Markdown- oder HTML-Bericht SOLL daraus generiert werden. Bei Widerspruch gilt das validierte maschinenlesbare Manifest.

### 20.3 Logaufbewahrung

Logs MÜSSEN:

- einem `run_id` zugeordnet;
- zeitlich in UTC;
- gegen Vermischung mehrerer Runs geschützt;
- frei von Geheimnissen;
- nach Retentionsregeln archiviert

sein.

---

## 21. Review- und Freigabenachweise

### 21.1 Review Record

```json
{
  "review_id": "string",
  "review_type": "internal|scr|architecture|editorial|certification|external|consolidation",
  "reviewer": "string",
  "reviewer_system": "human|chatgpt|gemini|claude|other",
  "reviewed_artifacts": [],
  "started_at_utc": "string",
  "completed_at_utc": "string",
  "status": "pending|passed|passed_with_findings|failed",
  "findings": [],
  "resolution_references": []
}
```

### 21.2 Unabhängige KI-Reviews

Claude- und Gemini-Reviews werden erst eingetragen, nachdem sie tatsächlich
durchgeführt wurden.

Bis dahin MUSS gelten:

```text
reviewer_system: claude
status: pending
```

beziehungsweise:

```text
reviewer_system: gemini
status: pending
```

Ergebnisse DÜRFEN NICHT erfunden, vorweggenommen oder als bestanden markiert werden.

### 21.3 Reviewartefakte

Jeder externe Reviewnachweis SOLL enthalten:

- geprüftes Dokument oder Dataset mit Hash;
- verwendete Reviewanweisung;
- System- und Modellbezeichnung;
- Datum;
- vollständige Befunde;
- Klassifikation der Befunde;
- Auflösung jedes wesentlichen Befunds;
- Re-Review-Status.

### 21.4 Freigabesequenz

Für die RCC-002-Spezifikationsfamilie gilt:

1. Specification Draft;
2. Internal Review;
3. Scientific Consistency Review;
4. Architecture Integrity Review;
5. Editorial Pass;
6. Internal Certification;
7. Claude Independent Architecture Review;
8. Gemini Independent Scientific and Adversarial Audit;
9. ChatGPT Final Consolidation;
10. Baseline V1 Certified;
11. Release- und Implementierungsfreigabe;
12. Implementierung, primär mit Claude Code.

---

## 22. Sicherheit und Datenschutz

### 22.1 Zulässige Provenienzdaten

Technische Hostinformationen dürfen protokolliert werden, soweit sie für Reproduktion oder Audit relevant sind.

### 22.2 Datenminimierung

Nicht erforderliche personenbezogene Informationen SOLLEN nicht erfasst werden.

Benutzernamen und absolute Home-Pfade SOLLEN in veröffentlichten Manifesten durch portable Bezeichner ersetzt werden.

### 22.3 Signierte Manifeste

Kryptografische Signaturen sind für RCC-002 optional.

Sie werden empfohlen, wenn:

- Artefakte extern verteilt werden;
- mehrere Organisationen beteiligt sind;
- Manipulationsschutz über Dateihashes hinaus benötigt wird.

Eine Signatur ersetzt weder Prüfsummen noch Lineage.

---

## 23. Empfohlene Verzeichnisstruktur

```text
manifests/
  schemas/
  sources/
  stages/
  runs/
  datasets/
  reviews/
  reproductions/

build/
  rcc002/
    temporary/
    quarantine/
    candidates/

data/
  rcc002/
    releases/
      <dataset_id>/

reports/
  rcc002/
    validation/
    lineage/
    reproducibility/
    reviews/
```

Die Implementierung darf abweichende Pfade verwenden, sofern:

- die Namensräume eindeutig bleiben;
- keine Runtime-Module durch gleichnamige Dokumentationsordner dupliziert werden;
- alle Pfade im Manifest portabel referenziert werden;
- temporäre, quarantänisierte und veröffentlichte Ergebnisse klar getrennt sind.

---

## 24. Minimales kanonisches Dataset-Manifest

```json
{
  "manifest_schema_id": "rcc002.dataset-manifest",
  "manifest_schema_version": "1.0.0",
  "manifest_schema_ref": "rcc002.dataset-manifest/1.0.0",
  "manifest_type": "dataset",
  "manifest_id": "manifest:sha256:<computed-after-preimage>",
  "created_at_utc": "2026-07-23T00:00:00Z",
  "producer": {
    "component": "rcc002-manifest-builder",
    "version": "<implementation version>"
  },
  "project": "RCC-002",
  "status": "candidate",
  "dataset_id": "dataset:sha256:<digest>",
  "dataset_artifact_set_id": "dataset-artifact-set:sha256:<digest>",
  "build_id": "build:sha256:<digest>",
  "publication_run_id": "run:<timestamp>:<uuid>",
  "dataset_profile": "rcc002-canonical",
  "source_snapshot_ids": [
    "source:sha256:<digest>"
  ],
  "code_provenance": {
    "repository": "<repository identifier>",
    "commit_sha": "<commit>",
    "worktree_clean": true,
    "dirty_patch_sha256": null,
    "entrypoint": "<entrypoint>"
  },
  "semantic_build_configuration": {
    "profile_id": "<semantic profile>",
    "canonical_sha256": "<digest>",
    "secret_fields_removed": true
  },
  "physical_publication_configuration": {
    "profile_id": "<physical profile>",
    "canonical_sha256": "<digest>"
  },
  "specification_profile": [
    {
      "document_id": "RCC_002_DATA_PIPELINE_SPECIFICATION",
      "version": "0.7.0",
      "sha256": "<digest>"
    },
    {
      "document_id": "RCC-002-DV",
      "version": "0.4.0",
      "sha256": "<digest>"
    },
    {
      "document_id": "RCC-002-IS",
      "version": "0.4.0",
      "sha256": "<digest>"
    },
    {
      "document_id": "RCC-002-ST",
      "version": "0.4.0",
      "sha256": "<digest>"
    },
    {
      "document_id": "RCC-002-RG",
      "version": "0.5.0",
      "sha256": "<digest>"
    },
    {
      "document_id": "RCC-002-LF",
      "version": "0.4.0",
      "sha256": "<digest>"
    },
    {
      "document_id": "RCC-002-RM",
      "version": "0.6.0",
      "sha256": "<digest>"
    }
  ],
  "environment_identity": {
    "profile_id": "RCC_BUILD_ENV_IDENTITY_V2",
    "canonical_sha256": "<digest>"
  },
  "artifacts": [
    {
      "logical_name": "<name>",
      "artifact_id": "artifact:sha256:<digest>",
      "relative_path": "<relative path>",
      "schema_id": "<schema>",
      "schema_version": "<version>",
      "schema_ref": "<schema>/<version>",
      "schema_fingerprint_sha256": "<digest>",
      "field_registry_sha256": "<digest>",
      "view_allowlist_sha256": "<digest-or-null>",
      "byte_sha256": "<digest>",
      "semantic_sha256": "<digest>",
      "physical_layout_sha256": "<digest>",
      "size_bytes": 0,
      "row_count": 0,
      "min_timestamp_utc": "<timestamp>",
      "max_timestamp_utc": "<timestamp>",
      "publication_status": "candidate"
    }
  ],
  "stage_schemas": [
    {
      "stage_id": "S7_LABELS",
      "schema_id": "rcc002.stage.s7-labels",
      "schema_version": "1.0.0",
      "schema_ref": "rcc002.stage.s7-labels/1.0.0",
      "schema_fingerprint_sha256": "<digest>"
    }
  ],
  "views": [
    {
      "view_schema_id": "rcc002.view.live",
      "view_schema_version": "1.0.0",
      "view_schema_ref": "rcc002.view.live/1.0.0",
      "view_allowlist_sha256": "<digest>",
      "s7_fields_allowed": false
    }
  ],
  "quality_summary": {
    "manifest_schema_valid": true,
    "artifact_hashes_valid": true,
    "dataset_lineage_complete": true,
    "knowledge_lineage_complete": true,
    "required_tests_passed": true
  },
  "reviews": [
    {
      "reviewer_system": "claude",
      "status": "pending"
    },
    {
      "reviewer_system": "gemini",
      "status": "pending"
    }
  ],
  "publication": {
    "status": "candidate",
    "published_at_utc": null,
    "supersedes": []
  }
}
```

Der Beispielzeitstempel ist kein vorgegebener realer Buildzeitpunkt. Implementierungen MÜSSEN reale Werte einsetzen.

---

## 25. Veröffentlichungs-Gate

Ein RCC-002-Dataset darf nur `published` werden, wenn:

- [ ] Source Manifest vorhanden und gültig;
- [ ] alle Source Snapshots per SHA-256 verifiziert;
- [ ] Codeprovenienz vollständig;
- [ ] Arbeitsbaum sauber oder Dirty Patch vollständig dokumentiert;
- [ ] `semantic_build_configuration` vollständig kanonisiert und gehasht;
- [ ] `physical_publication_configuration` vollständig kanonisiert und gehasht;
- [ ] jeder wirksame Konfigurationsschlüssel genau einer Klasse zugeordnet;
- [ ] Spezifikationsprofil vollständig;
- [ ] Umgebungsprovenienz vollständig;
- [ ] alle Stage Manifests gültig;
- [ ] alle Eingangs- und Ausgangsschema-IDs registriert und kompatibel;
- [ ] alle Schema-, Feldregistry- und View-Allowlist-Fingerprints gültig;
- [ ] alle Stufen-, Modell-, Profil-, State-, Enum- und Reason-Code-Referenzen auflösbar;
- [ ] alle Artefakte inventarisiert;
- [ ] alle Bytehashes gültig;
- [ ] alle semantischen Fingerprints gültig;
- [ ] Dataset Lineage vollständig und azyklisch;
- [ ] Knowledge Lineage vollständig;
- [ ] alle Datenvalidierungen bestanden;
- [ ] S2-Qualitäts- und Segmentvertrag eindeutig nachgewiesen;
- [ ] S5-/S6-Verträge eindeutig nachgewiesen;
- [ ] S7-Horizon- und Feldnamensraum eindeutig nachgewiesen;
- [ ] S7→S8-Row-Preservation-Reconciliation (§18.4) bestanden;
- [ ] stufenbasierte und präfixbasierte S7-Leakage-Tests bestanden;
- [ ] alle Schema- und Manifesttests bestanden;
- [ ] kein Pflichtartefakt quarantänisiert;
- [ ] Veröffentlichungsziel frei von stiller Überschreibung;
- [ ] atomare Veröffentlichung möglich;
- [ ] bekannte Einschränkungen dokumentiert;
- [ ] erforderliche Review- und Freigabestufe erreicht.

Ein einzelnes fehlgeschlagenes Pflichtkriterium blockiert die Veröffentlichung.

---

## 26. Abnahmekriterien

### 26.1 Spezifikationsreife vor Implementierungsfreigabe

Die Spezifikation ist bereit für `Approved for Implementation`, wenn:

1. alle logischen Stufen- und View-Schemas versioniert vorliegen;
2. alle Manifesttypen und Manifest-Schemas vollständig definiert sind;
3. alle deterministischen ID-Vorabbildungen zirkelfrei festgelegt sind;
4. semantische und physische Konfigurationsklassen vollständig getrennt sind;
5. jeder wirksame Konfigurationsschlüssel genau einer Klasse zugeordnet ist;
6. Schema-, Feldregistry-, Allowlist- und Kompatibilitätsnachweise
   spezifiziert sind;
7. Stufen-, View-, Modell-, Profil-, State-, Enum- und
   Reason-Code-Referenzen vollständig sind;
8. JSON-, Tabellen- und Konfigurationskanonisierung festgelegt ist;
9. numerische Determinismusprofile und Referenztoleranzen feststehen;
10. Build-Einstiegspunkt-, Umgebungs- und Lockstrategie festgelegt sind;
11. Reconciliation-, Rebuild-, Leakage- und Identitätstests vollständig
    spezifiziert sind;
12. alle vorgeschriebenen internen und externen Review-Gates der
    Spezifikationsbaseline bestanden sind;
13. keine offene Entscheidung logische Inhalte, Identitäten, Schemas oder
    Leakage-Schutz verändern kann.

### 26.2 Abnahme der Implementierung

Die RCC-002-Reproduzierbarkeitsimplementierung ist akzeptiert, wenn:

1. ein vollständiger Build automatisch alle erforderlichen Manifeste erzeugt;
2. IDs ohne zirkuläre Abhängigkeit berechnet werden;
3. Zeitstempel und Run-UUIDs die deterministische Build-ID nicht verändern;
4. jede deterministische Eingabeänderung eine neue Build-ID erzeugt;
5. jedes veröffentlichte Artefakt bis zur Quelle rückverfolgbar ist;
6. jede wissenschaftliche Transformationsregel auf ein Spezifikationsobjekt zurückgeführt werden kann;
7. gleiche Inhalte geräteübergreifend mindestens E2 erreichen;
8. Parquet-Byteunterschiede nicht fälschlich als Inhaltsabweichung gelten;
9. ein Clean-Rebuild mit dokumentiertem Einstiegspunkt möglich ist;
10. fehlgeschlagene Builds keine finalen Ausgaben veröffentlichen;
11. alte Releases unveränderlich bleiben;
12. Geheimnisse aus Manifesten ausgeschlossen werden;
13. JSON-Schemata sämtliche Manifesttypen maschinell prüfen;
14. Claude- und Gemini-Reviewstatus nur anhand realer Reviews aktualisiert werden;
15. der vollständige Veröffentlichungs-Gate automatisiert geprüft wird;
16. der semantische Fingerprint den vollständigen registrierten Primärschlüssel `(market_type, symbol, interval, open_time)` und bei unkonsolidierten Multi-Provider-Daten zusätzlich `provider` verwendet;
17. physische Partitionierung und Containerparameter ausschließlich in `physical_layout_sha256`, nicht in `semantic_sha256`, eingehen;
18. die JSON-Kanonisierung die Golden Fixtures von `RCC_JSON_CANONICALIZATION_V1` bytegenau besteht;
19. `source_snapshot_id` weder Abrufzeit noch lokalen Pfad enthält;
20. `build_id` ausschließlich die Allowlist von `RCC_BUILD_ENV_IDENTITY_V2` verwendet;
21. E3 nur für dasselbe persistierte Artefakt oder bei identischer vollständiger kanonischer Vorabbildung verlangt wird;
22. Änderungen von Bytehash, physischem Layout oder `artifact_id` bei
    unverändertem semantischem Inhalt weder `build_id` noch `dataset_id`
    verändern;
23. jede Änderung der veröffentlichten physischen Artefaktmenge eine neue
    `dataset_artifact_set_id` erzeugt.
24. `semantic_build_configuration_sha256` und
    `physical_publication_configuration_sha256` getrennt kanonisiert,
    manifestiert und auf Identitätswirkung geprüft werden;
25. jeder wirksame Konfigurationsschlüssel genau einer Konfigurationsklasse
    angehört;
26. alle Stufen- und View-Schema-IDs aus Abschnitt 8.7 auflösbar sind;
27. jedes Stage Manifest Eingangs- und Ausgangsschema samt Fingerprint
    referenziert;
28. jede S8-View eine positive Feld-Allowlist samt Hash besitzt;
29. jedes View-Feld eine registrierte Eigentümerstufe und Leakage-Klasse
    besitzt;
30. kein S7-Feld in Research-Feature-, Backtest-Input-, Paper- oder
    Live-Views enthalten ist;
31. die kanonischen S0-Provenienzfelder ohne konkurrierende Aliasfelder
    manifestiert werden;
32. `market_segment_id` und `indicator_segment_id` getrennt nachgewiesen
    werden;
33. S5-/S6-Modell-, Profil-, State- und Reason-Code-Identitäten vollständig
    auflösbar sind;
34. S7-Horizon-, Feld-, Kosten-, Barrier-, Numerik- und
    Reason-Code-Registry vollständig auflösbar sind.

---

## 27. Offene Implementierungsentscheidungen

### 27.1 Vor `Approved for Implementation` festzulegen

Vor der Implementierungsfreigabe MÜSSEN versioniert vorliegen:

- vollständige logische Stufen- und View-Schemas;
- konkrete Schema-IDs, Versionen, Fingerprints und Kompatibilitätsregeln;
- vollständige Feldregistries und positive S8-View-Allowlists;
- Manifesttypen und maschinenlesbare Manifest-Schemas;
- Identitätsvorabbildungen für alle deterministischen IDs;
- Grenzvertrag zwischen `semantic_build_configuration` und
  `physical_publication_configuration`;
- kanonische Tabellen-Fingerprint-Spezifikation;
- numerische Determinismusprofile und Referenztoleranzen;
- Golden Fixtures für JSON-, Konfigurations-, Tabellen- und ID-Bildung;
- Build-Einstiegspunktvertrag;
- CLI-Vertrag der Build-Orchestrierung;
- Umgebungs- und Lockstrategie;
- Reconciliation-, Test- und Abnahmekriterien;
- Sicherheits- und Geheimnisbereinigungsregeln.

Diese Punkte dürfen nach `Approved for Implementation` nicht ohne erneuten
Review semantisch verändert werden.

### 27.2 Während der Implementierung konkretisierbar

Innerhalb vorher freigegebener physischer Profile dürfen konkretisiert werden:

- physische Partitionsgrößen;
- Parquet-Row-Group-Größen;
- Kompressionsstufe;
- Writeroptimierungen;
- Retentionsdauer technischer Logs und quarantänisierter Builds;
- technisch gleichwertige Speicherorte großer Source Snapshots;
- temporäre Pfade und Cacheorte;
- optionaler Einsatz signierter Manifeste.

Diese Konkretisierungen MÜSSEN in
`physical_publication_configuration` erscheinen und dürfen keine logischen
Werte, Schemas, Gültigkeit, Reason Codes, `build_id` oder `dataset_id`
verändern.

### 27.3 Re-Review-Pflicht

Jede Änderung mit Wirkung auf:

- fachliche Semantik;
- logische Stufen- oder View-Schemas;
- Feld-Allowlist oder Leakage-Schutz;
- Identitätsvorabbildungen;
- Konfigurationsklassifikation;
- numerische Determinismusregeln;
- Manifestpflichtfelder

MUSS die betroffenen Scientific-, Architecture- und Certification-Gates
erneut durchlaufen.

---

## 28. Abgrenzung

Dieses Dokument:

- definiert keine Handelsstrategie;
- ersetzt keine Datenvalidierungsregeln;
- verändert keine Indikatorformeln;
- verändert keine Signal-, Regime-, Gate- oder Labeldefinition;
- zertifiziert noch keinen konkreten Datensatz;
- behauptet keine bereits durchgeführten Claude- oder Gemini-Reviews.

Es definiert die verbindliche Nachweis- und Reproduzierbarkeitsarchitektur, innerhalb der diese fachlichen Regeln umgesetzt werden.

---

## 29. Schlussbestimmung

RCC-002 betrachtet einen Datensatz erst dann als wissenschaftlich und technisch belastbar, wenn Dateninhalt, Transformationslogik, Herkunft, Umgebung, Konfiguration, Spezifikationsstand und Qualitätsstatus gemeinsam nachweisbar sind.

Der normative Kern lautet:

```text
Source provenance
+ code provenance
+ semantic build configuration
+ physical publication configuration
+ specification profile
+ environment record
+ complete dataset lineage
+ complete knowledge lineage
+ validated artifacts
+ reproducible publication
= auditable RCC-002 dataset
```

Diese Version bewahrt die geschlossenen Korrekturen aus
`RCC-002-SCR-001`, `RCC-002-SCR-002`, `RCC-002-SCR-003` und
`RCC-002-SCR-004`.

Version `0.6.0` bewahrt die in Version 0.5.0 geschlossenen
AIR-001-Korrekturen und korrigiert zusätzlich:

- `SCR-005-B01` – einheitlicher kanonischer Primärschlüssel S1 bis S7 und
  `interval` ohne Feldumbenennung;
- `SCR-005-B02` – eindeutige S0-Provenienz, Source-Manifest-Eigentümerschaft
  und gerichtete Legacy-Aliasmigration;
- `SCR-005-M01` – unversionierte `schema_id`, getrennte
  `schema_version` und abgeleitete `schema_ref`;
- `SCR-005-M03` – neue `build_id` und `dataset_id` bei jeder Änderung der
  semantischen Konfiguration, auch bei zufällig identischem Tabelleninhalt;
- `AIR-005-H01` – versionsgebundene positive S8-Feld-Allowlists,
  Allowlist-Hashes und Fail-closed-Publikationsnachweise.

Sie aktualisiert die Spezifikationsabhängigkeiten auf:

```text
RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md
Version 0.7.0

RCC_002_DATA_VALIDATION_2026-07-23.md
Version 0.4.0

RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md
Version 0.4.0

RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md
Version 0.4.0

RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md
Version 0.5.0

RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md
Version 0.4.0
```

Version `0.7.0` bewahrt die in Version 0.6.0 geschlossenen Korrekturen und
ergänzt beziehungsweise korrigiert zusätzlich:

- neue Unterabschnitt 8.7.1 – explizite S7→S8-Row-Preservation-Invariante
  (`S8_rows = S7_rows` je View) sowie zugehöriger Rückverweis auf
  `RCC_002_DATA_PIPELINE_SPECIFICATION` §5.8;
- neues S7→S8-Reconciliation-Testerfordernis in §18.4;
- Rückverweis auf `RCC_002_DATA_PIPELINE_SPECIFICATION` §5.8 an der
  bestehenden Row-Count-Stelle;
- §12.3 „Spezifikationsprofil" auf die tatsächlich aktuellen
  Dokumentversionen korrigiert (zuvor um ein bis zwei Generationen veraltet
  und in sich widersprüchlich hinsichtlich der eigenen Dokumentversion);
- §25 „Veröffentlichungs-Gate" um einen expliziten Prüfpunkt für die
  S7→S8-Row-Preservation-Reconciliation (§18.4) ergänzt;
- Kopfzeilen-Abhängigkeitsangaben auf die tatsächlich aktuellen Versionen der
  sechs übrigen Spezifikationen korrigiert.

Sie aktualisiert die Spezifikationsabhängigkeiten auf:

```text
RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md
Version 0.7.1

RCC_002_DATA_VALIDATION_2026-07-23.md
Version 0.4.2

RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md
Version 0.4.2

RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md
Version 0.4.1

RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md
Version 0.5.1

RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md
Version 0.4.1
```

Version `0.7.1` ist eine rein mechanische Folgeanpassung ohne eigene
normative Änderung an diesem Dokument: `RCC-002-AIR-004` schloss Minor
Finding `AIR4-MIN-01` (Carve-out-Umfang von
`PASS_WITH_APPROVED_EXCEPTIONS` in Indicator §30 und Signal Transformation
§32) durch eine Klarstellung in diesen beiden Dokumenten, verbunden mit den
Versionsanhebungen Indicator 0.4.2→0.4.3 und Signal Transformation
0.4.1→0.4.2. Diese Version aktualisiert ausschließlich die
Kopfzeilen-Abhängigkeitsangaben und die Tabelle in §12.3 auf diese beiden
neuen Versionen sowie auf ihre eigene Versionsnummer; kein Feld, keine
Invariante, kein Test und keine Ausnahmeregel dieses Dokuments wurde
verändert.

Sie aktualisiert die Spezifikationsabhängigkeiten auf:

```text
RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md
Version 0.7.1

RCC_002_DATA_VALIDATION_2026-07-23.md
Version 0.4.2

RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md
Version 0.4.3

RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md
Version 0.4.2

RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md
Version 0.5.1

RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md
Version 0.4.1
```

Der aktuelle Status lautet:

```text
C1 technisch abgeschlossen; RCC-002-SCR-007 Full-Scope Replacement
Scientific Consistency Review durchgeführt; Major-Findings-Verifikation und
Minor-Findings-Verifikation abgeschlossen; Minor Correction Cycle
umgesetzt; RCC-002-SCR-008 (PASS WITH MINOR CORRECTIONS) und
RCC-002-AIR-004 (PASS WITH MINOR CORRECTIONS) durchgeführt; Minor Finding
AIR4-MIN-01 in Indicator und Signal Transformation behoben, mechanische
Abhängigkeitsfolge in diesem Dokument nachgezogen; Editorial Pass und
Internal Certification ausstehend
```

Nächste vorgeschriebene Schritte:

1. Bundle- und Manifestregeneration gegen die sieben aktuellen
   Spezifikationen sowie unabhängige Hash- und Round-trip-Prüfung;
2. fokussierte Re-Review der AIR4-MIN-01-Korrektur;
3. Editorial Pass;
4. Internal Certification;
5. Claude Independent Architecture Review;
6. Gemini Independent Scientific and Adversarial Audit;
7. ChatGPT Final Consolidation;
8. `Baseline V1 Certified`;
9. Implementierungsfreigabe.

---

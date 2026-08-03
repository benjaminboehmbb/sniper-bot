# RCC-002 Data Pipeline Specification

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Wissenschaftliche und technische Kernspezifikation |
| Dokument-ID | `RCC_002_DATA_PIPELINE_SPECIFICATION` |
| Version | 0.8.0 |
| Datum | 2026-07-23 |
| Status | S8BCP-001 Revision 2 Corrected Candidate – Re-Review Pending |
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
| S8 Blocker Correction | `RCC-002-S8BCP-001` Revision 2 umgesetzt | Version 0.8.0 korrigiert Source Ingest, Zeitstempel-Normalisierung, Source-Row-Identität, Audit View und Manifest-Verträge; wissenschaftlicher und architektonischer Re-Review ausstehend. |
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

S0 besteht aus zwei getrennten normativen Objektklassen:

1. genau einem unveränderten Quellartefakt je physischer Providerdatei;
2. genau einem zugehörigen `source_manifest`.

Quellbytes werden nicht modifiziert. Archiv- oder Kompressionsformate bleiben
als Quellartefakt erhalten. Dekomprimierte Ableitungen erhalten eigene
Artefaktidentitäten. Die Quellartefakte selbst besitzen kein zusätzlich
erfundenes RCC-Zeilenschema. Ein `source_manifest` darf mehrere physische
Quellartefakte aggregieren; jedes Artefakt bleibt dabei einzeln adressierbar.

Der folgende Vertrag ist ausschließlich der Feldvertrag des
`source_manifest`:

| Feld | Logischer Typ | Nullbar | Eigentümerobjekt | Bedeutung |
|---|---|:---:|---|---|
| `source_snapshot_id` | UTF-8-String | Nein | `source_manifest` | Deterministische Identität der Quellenfassung |
| `source_snapshot_preimage_sha256` | 64-stelliger Lowercase-Hex-String | Nein | `source_manifest` | Hash der exakten Source-Snapshot-Vorabbildung |
| `provider` | UTF-8-String | Nein | `source_manifest` | Kanonische Providerkennung |
| `market_type` | UTF-8-String | Nein | `source_manifest` | Registrierter Markttyp |
| `dataset_kind` | UTF-8-String | Nein | `source_manifest` | Registrierte Datenfamilie |
| `symbol` | UTF-8-String | Nein | `source_manifest` | Registriertes Symbol |
| `interval` | UTF-8-String | Nein | `source_manifest` | Registriertes Datenintervall |
| `retrieved_at_utc` | UTC-Timestamp in Millisekunden | Nein | `source_manifest` | Provenienzzeitpunkt des Abrufs; nicht Teil der Source-ID |
| `source_retrieval_profile_id` | UTF-8-String | Nein | `source_manifest` | Registriertes Abrufprofil |
| `source_retrieval_profile_version` | SemVer | Nein | `source_manifest` | Version des Abrufprofils |
| `column_profile_id` | UTF-8-String | Nein | `source_manifest` | Registriertes Spalten-, Header-, Delimiter- und Encodingprofil |
| `timestamp_unit_profile_id` | UTF-8-String | Nein | `source_manifest` | Registriertes periodenselektiertes Zeitstempelprofil |
| `source_row_id_profile_id` | UTF-8-String | Nein | `source_manifest` | `RCC002_S1_SOURCE_ROW_ID_V2` |
| `source_row_id_profile_version` | SemVer | Nein | `source_manifest` | `2.0.0` |
| `source_files` | Geordnete Liste | Nein | `source_manifest` | Physische Quellartefakte in kanonischer Abrufreihenfolge |
| `actual_coverage` | Objekt | Nein | `source_manifest` | Byte-abgeleiteter Gesamtumfang nach Zeitstempelnormalisierung |
| `coverage_reconciliation` | Objekt | Nein | `source_manifest` | Ergebnis der Datei-/Gesamtdeckungsprüfung |
| `license_or_terms_ref` | UTF-8-String | Ja | `source_manifest` | Referenz auf Nutzungsbedingungen |

Jeder Eintrag in `source_files` enthält exakt:

| Feld | Logischer Typ | Nullbar | Bedeutung |
|---|---|:---:|---|
| `provider_relative_name` | UTF-8-String | Nein | Normalisierter portabler Providerpfad |
| `byte_sha256` | 64-stelliger Lowercase-Hex-String | Nein | SHA-256 der unveränderten Providerbytes |
| `provider_checksum_sha256` | 64-stelliger Lowercase-Hex-String | Nein | Vom Provider veröffentlichte und verifizierte SHA-256 |
| `size_bytes` | UInt64 | Nein | Bytegröße der unveränderten Providerdatei |
| `csv_member_name` | UTF-8-String | Nein | Einziger registrierter CSV-Member |
| `source_file_ordinal` | UInt32 | Nein | Nullbasierter Index nach Sortierung auf `provider_relative_name` |
| `archive_period` | Objekt | Nein | Familie, Token, inklusive UTC-Start- und exklusive UTC-Endgrenze |
| `record_count` | UInt64 | Nein | Physische Datenzeilen nach registriertem Headermodus |
| `min_open_time_utc_ms` | Int64 | Nein | Kleinster normalisierter Open-Zeitstempel |
| `max_close_time_utc_ms` | Int64 | Nein | Größter normalisierter Close-Zeitstempel |
| `timestamp_unit` | Enum | Nein | `MILLISECOND` oder `MICROSECOND` gemäß Profil |

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

- `source_files` wird nach normalisiertem `provider_relative_name` sortiert;
  erst danach werden lückenlose `source_file_ordinal`-Werte vergeben;
- `source_snapshot_id` wird gemäß
  `RCC002_SOURCE_SNAPSHOT_ID_V1/1.0.0` über die exakte RFC-8785-
  Vorabbildung aus Retrievalprofil, Provider-/Markt-/Datasetidentität,
  Symbol, Intervall, Spalten- und Zeitstempelprofil, Source Revision,
  vollständiger `source_files`-Liste und `actual_coverage` gebildet;
- `source_snapshot_id` hat die Darstellung
  `source:sha256:<lowercase-sha256>`;
- `retrieved_at_utc`, lokale Pfade, Hostdaten und Transport-Retrys beeinflussen
  `source_snapshot_id` nicht;
- `timezone`, `expected_start` und `expected_end` gehen über
  `semantic_build_configuration_sha256` in `build_id` und `dataset_id` ein,
  nicht in `source_snapshot_id`.

`source_revision` ist ein Source-Manifest-Feld und darf null sein, wenn der
Provider keine Revision ausweist. Dieser Zustand muss explizit serialisiert
werden.

### 7.2 S1_NORMALIZED – Normalisierung

S1 normalisiert:

- Zeitstempel nach UTC;
- Feldnamen;
- Datentypen;
- Intervallbezeichnung;
- Markttyp;
- Symbolbezeichnung;
- numerische Darstellung.

Vor dem Lesen einer Datenzeile muss S1 anhand
`source_retrieval_profile_id` und `archive_period` genau einen
Eintrag des `timestamp_unit_profile_id` auswählen. Eine Einheit darf weder
aus der Stellenzahl noch aus dem Zahlenwert eines Zeitstempels geraten werden.
Für das registrierte Binance-Spot-Profil gilt:

```text
archive_period.period_end_utc <= 2025-01-01T00:00:00Z   -> raw_unit = millisecond
archive_period.period_start_utc >= 2025-01-01T00:00:00Z -> raw_unit = microsecond
```

Bei `raw_unit = millisecond` ist der Rohwert unverändert zu übernehmen. Bei
`raw_unit = microsecond` gilt für `open_time_raw` zwingend
`open_time_raw mod 1000 = 0` und für `close_time_raw` zwingend
`close_time_raw mod 1000 = 999`; anschließend werden beide Werte durch
ganzzahlige Division durch 1000 in kanonische Millisekunden überführt. Jeder
Profil-, Perioden- oder Restklassenkonflikt ist fail-closed abzulehnen.

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
| `source_file_ordinal` | UInt32 | Nein | S0/S1 |
| `original_record_index` | UInt64 | Nein | S1 |
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

`original_record_index` ist der nullbasierte physische Datensatzindex innerhalb
der dekomprimierten registrierten Datendatei; eine Headerzeile zählt nicht als
Datensatz. `source_file_ordinal` verweist auf genau einen Eintrag von
`source_files`.

Für `source_row_id_profile_ref =
RCC002_S1_SOURCE_ROW_ID_V2/2.0.0` wird `source_row_id` ohne Trennzeichen-
Escaping exakt als folgende ASCII-Zeichenfolge gebildet:

```text
RCC002_S1_SOURCE_ROW_ID_V2:<source_snapshot_id>:<source_file_ordinal 8d>:<original_record_index 20d>
```

`source_file_ordinal` ist dabei nullaufgefüllt auf acht Dezimalstellen,
`original_record_index` auf zwanzig Dezimalstellen. Werte außerhalb dieser Breiten,
unbekannte Profilversionen oder nicht auflösbare Ordinale sind fail-closed
abzulehnen.

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

Audit View V1 (`rcc002.view.audit/1.0.0`) ist zurückgezogen und darf nicht erzeugt oder konsumiert werden. Audit View V2 besitzt exakt dieselbe geordnete Feldmenge, denselben Allowlist-Hash und dieselben zulässigen Erzeugerstufen wie `label-research/1.0.0`; insbesondere enthält sie keine S8- oder Manifestfelder.

```json
{
  "schema_id": "rcc002.view.audit",
  "schema_version": "2.0.0",
  "schema_ref": "rcc002.view.audit/2.0.0",
  "allowlist_sha256": "0e223d60ed4139f73194f1cb3b886a8eface9229183ad522a093e966827518cc",
  "allowed_producer_stages": [
    "S0_SOURCE",
    "S1_NORMALIZED",
    "S2_VALIDATED",
    "S3_INDICATORS",
    "S4_SIGNALS",
    "S5_REGIMES",
    "S6_GATES",
    "S7_LABELS"
  ],
  "fields": [
    "source_snapshot_id",
    "provider",
    "market_type",
    "symbol",
    "interval",
    "source_row_id",
    "open_time",
    "close_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "market_segment_id",
    "quality_is_observed",
    "quality_is_synthetic",
    "quality_has_source_conflict",
    "quality_gap_before",
    "quality_gap_after",
    "quality_timestamp_valid",
    "quality_ohlc_valid",
    "quality_volume_valid",
    "quality_market_values_valid",
    "quality_status",
    "quality_reason_codes",
    "quality_rule_version",
    "quality_gate_pass",
    "indicator_profile_id",
    "indicator_profile_version",
    "indicator_schema_id",
    "indicator_schema_version",
    "indicator_schema_ref",
    "indicator_segment_id",
    "sma_close_200",
    "sma_close_200_valid",
    "sma_close_200_warmup_complete",
    "sma_close_200_reason_codes",
    "ema_close_50",
    "ema_close_50_valid",
    "ema_close_50_warmup_complete",
    "ema_close_50_reason_codes",
    "rsi_wilder_14",
    "rsi_wilder_14_valid",
    "rsi_wilder_14_warmup_complete",
    "rsi_wilder_14_reason_codes",
    "macd_line_12_26",
    "macd_line_12_26_valid",
    "macd_line_12_26_warmup_complete",
    "macd_line_12_26_reason_codes",
    "macd_signal_line_12_26_9",
    "macd_signal_line_12_26_9_valid",
    "macd_signal_line_12_26_9_warmup_complete",
    "macd_signal_line_12_26_9_reason_codes",
    "macd_hist_12_26_9",
    "macd_hist_12_26_9_valid",
    "macd_hist_12_26_9_warmup_complete",
    "macd_hist_12_26_9_reason_codes",
    "bb_mid_20",
    "bb_mid_20_valid",
    "bb_mid_20_warmup_complete",
    "bb_mid_20_reason_codes",
    "bb_upper_20_2",
    "bb_upper_20_2_valid",
    "bb_upper_20_2_warmup_complete",
    "bb_upper_20_2_reason_codes",
    "bb_lower_20_2",
    "bb_lower_20_2_valid",
    "bb_lower_20_2_warmup_complete",
    "bb_lower_20_2_reason_codes",
    "bb_width_20_2",
    "bb_width_20_2_valid",
    "bb_width_20_2_warmup_complete",
    "bb_width_20_2_reason_codes",
    "stoch_k_14",
    "stoch_k_14_valid",
    "stoch_k_14_warmup_complete",
    "stoch_k_14_reason_codes",
    "true_range",
    "true_range_valid",
    "true_range_warmup_complete",
    "true_range_reason_codes",
    "atr_wilder_14",
    "atr_wilder_14_valid",
    "atr_wilder_14_warmup_complete",
    "atr_wilder_14_reason_codes",
    "roc_close_12_pct",
    "roc_close_12_pct_valid",
    "roc_close_12_pct_warmup_complete",
    "roc_close_12_pct_reason_codes",
    "obv",
    "obv_valid",
    "obv_warmup_complete",
    "obv_reason_codes",
    "typical_price",
    "typical_price_valid",
    "typical_price_warmup_complete",
    "typical_price_reason_codes",
    "cci_20",
    "cci_20_valid",
    "cci_20_warmup_complete",
    "cci_20_reason_codes",
    "mfi_14",
    "mfi_14_valid",
    "mfi_14_warmup_complete",
    "mfi_14_reason_codes",
    "plus_di_14",
    "plus_di_14_valid",
    "plus_di_14_warmup_complete",
    "plus_di_14_reason_codes",
    "minus_di_14",
    "minus_di_14_valid",
    "minus_di_14_warmup_complete",
    "minus_di_14_reason_codes",
    "dx_14",
    "dx_14_valid",
    "dx_14_warmup_complete",
    "dx_14_reason_codes",
    "adx_wilder_14",
    "adx_wilder_14_valid",
    "adx_wilder_14_warmup_complete",
    "adx_wilder_14_reason_codes",
    "signal_profile_id",
    "signal_profile_version",
    "signal_schema_id",
    "signal_schema_version",
    "signal_schema_ref",
    "sig_rsi_mr_d",
    "sig_rsi_mr_d_valid",
    "sig_rsi_mr_d_reason_codes",
    "sig_macd_momentum_d",
    "sig_macd_momentum_d_valid",
    "sig_macd_momentum_d_reason_codes",
    "sig_bollinger_mr_d",
    "sig_bollinger_mr_d_valid",
    "sig_bollinger_mr_d_reason_codes",
    "sig_stoch_mr_d",
    "sig_stoch_mr_d_valid",
    "sig_stoch_mr_d_reason_codes",
    "sig_cci_mr_d",
    "sig_cci_mr_d_valid",
    "sig_cci_mr_d_reason_codes",
    "sig_mfi_mr_d",
    "sig_mfi_mr_d_valid",
    "sig_mfi_mr_d_reason_codes",
    "sig_obv_momentum_d",
    "sig_obv_momentum_d_valid",
    "sig_obv_momentum_d_reason_codes",
    "sig_roc_momentum_d",
    "sig_roc_momentum_d_valid",
    "sig_roc_momentum_d_reason_codes",
    "state_ma200_trend_d",
    "state_ma200_trend_d_valid",
    "state_ma200_trend_d_reason_codes",
    "state_ema50_trend_d",
    "state_ema50_trend_d_valid",
    "state_ema50_trend_d_reason_codes",
    "state_atr_relative_d",
    "state_atr_relative_d_valid",
    "state_atr_relative_d_reason_codes",
    "state_adx_strength_d",
    "state_adx_strength_d_valid",
    "state_adx_strength_d_reason_codes",
    "score_rsi_mr_c",
    "score_rsi_mr_c_valid",
    "score_rsi_mr_c_reason_codes",
    "score_macd_momentum_c",
    "score_macd_momentum_c_valid",
    "score_macd_momentum_c_reason_codes",
    "score_bollinger_mr_c",
    "score_bollinger_mr_c_valid",
    "score_bollinger_mr_c_reason_codes",
    "score_stoch_mr_c",
    "score_stoch_mr_c_valid",
    "score_stoch_mr_c_reason_codes",
    "score_cci_mr_c",
    "score_cci_mr_c_valid",
    "score_cci_mr_c_reason_codes",
    "score_mfi_mr_c",
    "score_mfi_mr_c_valid",
    "score_mfi_mr_c_reason_codes",
    "score_obv_momentum_c",
    "score_obv_momentum_c_valid",
    "score_obv_momentum_c_reason_codes",
    "score_roc_momentum_c",
    "score_roc_momentum_c_valid",
    "score_roc_momentum_c_reason_codes",
    "score_ma200_trend_c",
    "score_ma200_trend_c_valid",
    "score_ma200_trend_c_reason_codes",
    "score_ema50_trend_c",
    "score_ema50_trend_c_valid",
    "score_ema50_trend_c_reason_codes",
    "score_atr_relative_c",
    "score_atr_relative_c_valid",
    "score_atr_relative_c_reason_codes",
    "score_adx_strength_c",
    "score_adx_strength_c_valid",
    "score_adx_strength_c_reason_codes",
    "regime_raw",
    "regime_effective",
    "regime_candidate",
    "regime_candidate_count",
    "regime_transition_flag",
    "regime_transition_from",
    "regime_transition_to",
    "ma200_slope_1440_pct",
    "trend_strength",
    "trend_strength_valid",
    "trend_strength_reason_codes",
    "volatility_relative",
    "volatility_relative_valid",
    "volatility_relative_reason_codes",
    "regime_model_id",
    "regime_model_version",
    "regime_schema_id",
    "regime_schema_version",
    "regime_schema_ref",
    "regime_valid",
    "regime_reason_codes",
    "allow_long",
    "allow_short",
    "data_gate_pass",
    "gate_state",
    "gate_reason_codes_long",
    "gate_reason_codes_short",
    "gate_profile_id",
    "gate_profile_version",
    "gate_schema_id",
    "gate_schema_version",
    "gate_schema_ref",
    "gate_valid",
    "gate_evaluated_at",
    "label_profile_id",
    "label_profile_version",
    "label_schema_id",
    "label_schema_version",
    "label_schema_ref",
    "horizon_registry_id",
    "horizon_registry_version",
    "cost_profile_id",
    "cost_profile_version",
    "barrier_profile_id",
    "barrier_profile_version",
    "label_reason_code_registry_version",
    "label_numeric_profile_id",
    "label_numeric_profile_version",
    "label_horizon_bars_h001",
    "label_available_at_h001",
    "fwd_cc_valid_h001",
    "fwd_cc_reason_codes_h001",
    "fwd_cc_label_segment_id_h001",
    "fwd_cc_long_ret_h001",
    "fwd_cc_short_ret_h001",
    "fwd_cc_log_ret_h001",
    "fwd_cc_short_log_ret_h001",
    "fwd_noc_valid_h001",
    "fwd_noc_reason_codes_h001",
    "fwd_noc_label_segment_id_h001",
    "fwd_noc_long_ret_h001",
    "fwd_noc_short_ret_h001",
    "fwd_noc_long_net_proxy_fee_rt_0004_h001",
    "fwd_noc_short_net_proxy_fee_rt_0004_h001",
    "fwd_excursion_valid_h001",
    "fwd_excursion_reason_codes_h001",
    "fwd_excursion_label_segment_id_h001",
    "fwd_long_mfe_h001",
    "fwd_long_mae_h001",
    "fwd_short_mfe_h001",
    "fwd_short_mae_h001",
    "fwd_long_mfe_first_bar_h001",
    "fwd_long_mae_first_bar_h001",
    "fwd_short_mfe_first_bar_h001",
    "fwd_short_mae_first_bar_h001",
    "label_cc_direction_valid_h001",
    "label_cc_direction_reason_codes_h001",
    "label_cc_direction_segment_id_h001",
    "label_cc_long_direction_h001",
    "label_cc_short_direction_h001",
    "label_noc_direction_valid_h001",
    "label_noc_direction_reason_codes_h001",
    "label_noc_direction_segment_id_h001",
    "label_noc_long_direction_h001",
    "label_noc_short_direction_h001",
    "label_noc_long_net_proxy_fee_rt_0004_direction_h001",
    "label_noc_short_net_proxy_fee_rt_0004_direction_h001",
    "barrier_valid_h001",
    "barrier_reason_codes_h001",
    "barrier_label_segment_id_h001",
    "barrier_long_outcome_tp050_sl020_h001",
    "barrier_short_outcome_tp050_sl020_h001",
    "barrier_long_first_hit_bar_tp050_sl020_h001",
    "barrier_short_first_hit_bar_tp050_sl020_h001",
    "barrier_long_first_hit_time_tp050_sl020_h001",
    "barrier_short_first_hit_time_tp050_sl020_h001",
    "label_horizon_bars_h005",
    "label_available_at_h005",
    "fwd_cc_valid_h005",
    "fwd_cc_reason_codes_h005",
    "fwd_cc_label_segment_id_h005",
    "fwd_cc_long_ret_h005",
    "fwd_cc_short_ret_h005",
    "fwd_cc_log_ret_h005",
    "fwd_cc_short_log_ret_h005",
    "fwd_noc_valid_h005",
    "fwd_noc_reason_codes_h005",
    "fwd_noc_label_segment_id_h005",
    "fwd_noc_long_ret_h005",
    "fwd_noc_short_ret_h005",
    "fwd_noc_long_net_proxy_fee_rt_0004_h005",
    "fwd_noc_short_net_proxy_fee_rt_0004_h005",
    "fwd_excursion_valid_h005",
    "fwd_excursion_reason_codes_h005",
    "fwd_excursion_label_segment_id_h005",
    "fwd_long_mfe_h005",
    "fwd_long_mae_h005",
    "fwd_short_mfe_h005",
    "fwd_short_mae_h005",
    "fwd_long_mfe_first_bar_h005",
    "fwd_long_mae_first_bar_h005",
    "fwd_short_mfe_first_bar_h005",
    "fwd_short_mae_first_bar_h005",
    "label_cc_direction_valid_h005",
    "label_cc_direction_reason_codes_h005",
    "label_cc_direction_segment_id_h005",
    "label_cc_long_direction_h005",
    "label_cc_short_direction_h005",
    "label_noc_direction_valid_h005",
    "label_noc_direction_reason_codes_h005",
    "label_noc_direction_segment_id_h005",
    "label_noc_long_direction_h005",
    "label_noc_short_direction_h005",
    "label_noc_long_net_proxy_fee_rt_0004_direction_h005",
    "label_noc_short_net_proxy_fee_rt_0004_direction_h005",
    "barrier_valid_h005",
    "barrier_reason_codes_h005",
    "barrier_label_segment_id_h005",
    "barrier_long_outcome_tp050_sl020_h005",
    "barrier_short_outcome_tp050_sl020_h005",
    "barrier_long_first_hit_bar_tp050_sl020_h005",
    "barrier_short_first_hit_bar_tp050_sl020_h005",
    "barrier_long_first_hit_time_tp050_sl020_h005",
    "barrier_short_first_hit_time_tp050_sl020_h005",
    "label_horizon_bars_h015",
    "label_available_at_h015",
    "fwd_cc_valid_h015",
    "fwd_cc_reason_codes_h015",
    "fwd_cc_label_segment_id_h015",
    "fwd_cc_long_ret_h015",
    "fwd_cc_short_ret_h015",
    "fwd_cc_log_ret_h015",
    "fwd_cc_short_log_ret_h015",
    "fwd_noc_valid_h015",
    "fwd_noc_reason_codes_h015",
    "fwd_noc_label_segment_id_h015",
    "fwd_noc_long_ret_h015",
    "fwd_noc_short_ret_h015",
    "fwd_noc_long_net_proxy_fee_rt_0004_h015",
    "fwd_noc_short_net_proxy_fee_rt_0004_h015",
    "fwd_excursion_valid_h015",
    "fwd_excursion_reason_codes_h015",
    "fwd_excursion_label_segment_id_h015",
    "fwd_long_mfe_h015",
    "fwd_long_mae_h015",
    "fwd_short_mfe_h015",
    "fwd_short_mae_h015",
    "fwd_long_mfe_first_bar_h015",
    "fwd_long_mae_first_bar_h015",
    "fwd_short_mfe_first_bar_h015",
    "fwd_short_mae_first_bar_h015",
    "label_cc_direction_valid_h015",
    "label_cc_direction_reason_codes_h015",
    "label_cc_direction_segment_id_h015",
    "label_cc_long_direction_h015",
    "label_cc_short_direction_h015",
    "label_noc_direction_valid_h015",
    "label_noc_direction_reason_codes_h015",
    "label_noc_direction_segment_id_h015",
    "label_noc_long_direction_h015",
    "label_noc_short_direction_h015",
    "label_noc_long_net_proxy_fee_rt_0004_direction_h015",
    "label_noc_short_net_proxy_fee_rt_0004_direction_h015",
    "barrier_valid_h015",
    "barrier_reason_codes_h015",
    "barrier_label_segment_id_h015",
    "barrier_long_outcome_tp050_sl020_h015",
    "barrier_short_outcome_tp050_sl020_h015",
    "barrier_long_first_hit_bar_tp050_sl020_h015",
    "barrier_short_first_hit_bar_tp050_sl020_h015",
    "barrier_long_first_hit_time_tp050_sl020_h015",
    "barrier_short_first_hit_time_tp050_sl020_h015",
    "label_horizon_bars_h060",
    "label_available_at_h060",
    "fwd_cc_valid_h060",
    "fwd_cc_reason_codes_h060",
    "fwd_cc_label_segment_id_h060",
    "fwd_cc_long_ret_h060",
    "fwd_cc_short_ret_h060",
    "fwd_cc_log_ret_h060",
    "fwd_cc_short_log_ret_h060",
    "fwd_noc_valid_h060",
    "fwd_noc_reason_codes_h060",
    "fwd_noc_label_segment_id_h060",
    "fwd_noc_long_ret_h060",
    "fwd_noc_short_ret_h060",
    "fwd_noc_long_net_proxy_fee_rt_0004_h060",
    "fwd_noc_short_net_proxy_fee_rt_0004_h060",
    "fwd_excursion_valid_h060",
    "fwd_excursion_reason_codes_h060",
    "fwd_excursion_label_segment_id_h060",
    "fwd_long_mfe_h060",
    "fwd_long_mae_h060",
    "fwd_short_mfe_h060",
    "fwd_short_mae_h060",
    "fwd_long_mfe_first_bar_h060",
    "fwd_long_mae_first_bar_h060",
    "fwd_short_mfe_first_bar_h060",
    "fwd_short_mae_first_bar_h060",
    "label_cc_direction_valid_h060",
    "label_cc_direction_reason_codes_h060",
    "label_cc_direction_segment_id_h060",
    "label_cc_long_direction_h060",
    "label_cc_short_direction_h060",
    "label_noc_direction_valid_h060",
    "label_noc_direction_reason_codes_h060",
    "label_noc_direction_segment_id_h060",
    "label_noc_long_direction_h060",
    "label_noc_short_direction_h060",
    "label_noc_long_net_proxy_fee_rt_0004_direction_h060",
    "label_noc_short_net_proxy_fee_rt_0004_direction_h060",
    "barrier_valid_h060",
    "barrier_reason_codes_h060",
    "barrier_label_segment_id_h060",
    "barrier_long_outcome_tp050_sl020_h060",
    "barrier_short_outcome_tp050_sl020_h060",
    "barrier_long_first_hit_bar_tp050_sl020_h060",
    "barrier_short_first_hit_bar_tp050_sl020_h060",
    "barrier_long_first_hit_time_tp050_sl020_h060",
    "barrier_short_first_hit_time_tp050_sl020_h060",
    "label_horizon_bars_h240",
    "label_available_at_h240",
    "fwd_cc_valid_h240",
    "fwd_cc_reason_codes_h240",
    "fwd_cc_label_segment_id_h240",
    "fwd_cc_long_ret_h240",
    "fwd_cc_short_ret_h240",
    "fwd_cc_log_ret_h240",
    "fwd_cc_short_log_ret_h240",
    "fwd_noc_valid_h240",
    "fwd_noc_reason_codes_h240",
    "fwd_noc_label_segment_id_h240",
    "fwd_noc_long_ret_h240",
    "fwd_noc_short_ret_h240",
    "fwd_noc_long_net_proxy_fee_rt_0004_h240",
    "fwd_noc_short_net_proxy_fee_rt_0004_h240",
    "fwd_excursion_valid_h240",
    "fwd_excursion_reason_codes_h240",
    "fwd_excursion_label_segment_id_h240",
    "fwd_long_mfe_h240",
    "fwd_long_mae_h240",
    "fwd_short_mfe_h240",
    "fwd_short_mae_h240",
    "fwd_long_mfe_first_bar_h240",
    "fwd_long_mae_first_bar_h240",
    "fwd_short_mfe_first_bar_h240",
    "fwd_short_mae_first_bar_h240",
    "label_cc_direction_valid_h240",
    "label_cc_direction_reason_codes_h240",
    "label_cc_direction_segment_id_h240",
    "label_cc_long_direction_h240",
    "label_cc_short_direction_h240",
    "label_noc_direction_valid_h240",
    "label_noc_direction_reason_codes_h240",
    "label_noc_direction_segment_id_h240",
    "label_noc_long_direction_h240",
    "label_noc_short_direction_h240",
    "label_noc_long_net_proxy_fee_rt_0004_direction_h240",
    "label_noc_short_net_proxy_fee_rt_0004_direction_h240",
    "barrier_valid_h240",
    "barrier_reason_codes_h240",
    "barrier_label_segment_id_h240",
    "barrier_long_outcome_tp050_sl020_h240",
    "barrier_short_outcome_tp050_sl020_h240",
    "barrier_long_first_hit_bar_tp050_sl020_h240",
    "barrier_short_first_hit_bar_tp050_sl020_h240",
    "barrier_long_first_hit_time_tp050_sl020_h240",
    "barrier_short_first_hit_time_tp050_sl020_h240",
    "label_horizon_bars_h1440",
    "label_available_at_h1440",
    "fwd_cc_valid_h1440",
    "fwd_cc_reason_codes_h1440",
    "fwd_cc_label_segment_id_h1440",
    "fwd_cc_long_ret_h1440",
    "fwd_cc_short_ret_h1440",
    "fwd_cc_log_ret_h1440",
    "fwd_cc_short_log_ret_h1440",
    "fwd_noc_valid_h1440",
    "fwd_noc_reason_codes_h1440",
    "fwd_noc_label_segment_id_h1440",
    "fwd_noc_long_ret_h1440",
    "fwd_noc_short_ret_h1440",
    "fwd_noc_long_net_proxy_fee_rt_0004_h1440",
    "fwd_noc_short_net_proxy_fee_rt_0004_h1440",
    "fwd_excursion_valid_h1440",
    "fwd_excursion_reason_codes_h1440",
    "fwd_excursion_label_segment_id_h1440",
    "fwd_long_mfe_h1440",
    "fwd_long_mae_h1440",
    "fwd_short_mfe_h1440",
    "fwd_short_mae_h1440",
    "fwd_long_mfe_first_bar_h1440",
    "fwd_long_mae_first_bar_h1440",
    "fwd_short_mfe_first_bar_h1440",
    "fwd_short_mae_first_bar_h1440",
    "label_cc_direction_valid_h1440",
    "label_cc_direction_reason_codes_h1440",
    "label_cc_direction_segment_id_h1440",
    "label_cc_long_direction_h1440",
    "label_cc_short_direction_h1440",
    "label_noc_direction_valid_h1440",
    "label_noc_direction_reason_codes_h1440",
    "label_noc_direction_segment_id_h1440",
    "label_noc_long_direction_h1440",
    "label_noc_short_direction_h1440",
    "label_noc_long_net_proxy_fee_rt_0004_direction_h1440",
    "label_noc_short_net_proxy_fee_rt_0004_direction_h1440",
    "barrier_valid_h1440",
    "barrier_reason_codes_h1440",
    "barrier_label_segment_id_h1440",
    "barrier_long_outcome_tp050_sl020_h1440",
    "barrier_short_outcome_tp050_sl020_h1440",
    "barrier_long_first_hit_bar_tp050_sl020_h1440",
    "barrier_short_first_hit_bar_tp050_sl020_h1440",
    "barrier_long_first_hit_time_tp050_sl020_h1440",
    "barrier_short_first_hit_time_tp050_sl020_h1440"
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

Für `S8BCP-001` Revision 2 sind Source-Retrieval-, Spalten-, Zeitstempel-,
Source-Snapshot- und Source-Row-ID-Profile, Audit View V2,
Manifest-Schemaablage und Golden Fixtures konkret festgelegt. Diese Punkte
sind nicht mehr als freie Implementierungsentscheidung behandelbar. Die
verbleibenden Punkte dieser Liste betreffen nur noch die nicht durch
`S8BCP-001` materialisierten Gesamtbaseline-Verträge.

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
S8BCP-001 Revision 2 Corrected Candidate – Re-Review Pending
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

# RCC-002 Data Validation Specification

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Scientific Software Specification |
| Dokument-ID | RCC-002-DV |
| Titel | Data Validation Specification |
| Speicherort im Repository | `docs/specifications/RCC_002_DATA_VALIDATION_2026-07-23.md` |
| Dateiname | `RCC_002_DATA_VALIDATION_2026-07-23.md` |
| Version | 0.6.0 |
| Datum | 2026-07-23 |
| Status | S8BCP-001 Revision 2 Corrected Candidate – Re-Review Pending |
| Übergeordnetes Dokument | `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`, Version 0.8.0 |
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
| Reason-Code-Severity-Korrekturzyklus | `RCC-002-DVSEV-001` umgesetzt | Version 0.5.0, 2026-07-27: neuer Abschnitt 16.3 „Reason-Code-Severity-Register" ergänzt die in §16.2 geforderte, bislang für 26 von 32 Reason Codes fehlende Standard-Severity und schließt damit die Abnahmevoraussetzung §24.1 Nr. 3. Additive Ergänzung; keine bestehende Regel, kein bestehender Reason Code und keine bestehende Severity-Zuweisung wurde verändert. Grundlage: `docs/review/RCC_002_DVSEV_001_REASON_CODE_SEVERITY_CORRECTION_PROPOSAL_2026-07-27.md`. |
| S8 Blocker Correction | `RCC-002-S8BCP-001` Revision 2 umgesetzt | Version 0.6.0 bindet Datei-, Spalten- und Zeitstempelprofile sowie Source-Row-Identität normativ; wissenschaftlicher und architektonischer Re-Review ausstehend. |

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
| `source_snapshot_preimage_sha256` | 64-stelliger Lowercase-Hex-String | Nein | Hash der exakten Source-Snapshot-Vorabbildung |
| `provider` | UTF-8-String | Nein | Kanonische Anbieterkennung, z. B. Binance |
| `market_type` | UTF-8-String | Nein | Registrierter Markttyp, z. B. Spot oder Futures |
| `dataset_kind` | UTF-8-String | Nein | Registrierte Datenfamilie, z. B. `klines` |
| `symbol` | UTF-8-String | Nein | Registriertes Symbol, z. B. BTCUSDT |
| `interval` | UTF-8-String | Nein | Registriertes Datenintervall, z. B. `1m` |
| `retrieved_at_utc` | UTC-Timestamp in Millisekunden | Nein | Provenienzzeitpunkt des Abrufs; nicht Teil der Source-ID |
| `source_retrieval_profile_id` | UTF-8-String | Nein | Registriertes Abruf- und Periodenprofil |
| `source_retrieval_profile_version` | SemVer | Nein | Version des Abrufprofils |
| `column_profile_id` | UTF-8-String | Nein | Registriertes Spalten-, Header-, Delimiter- und Encodingprofil |
| `timestamp_unit_profile_id` | UTF-8-String | Nein | Registriertes periodenselektiertes Zeitstempelprofil |
| `source_row_id_profile_id` | UTF-8-String | Nein | `RCC002_S1_SOURCE_ROW_ID_V2` |
| `source_row_id_profile_version` | SemVer | Nein | `2.0.0` |
| `source_files` | Geordnete Liste | Nein | Vollständige physische Quellartefakte gemäß Source Snapshot V1 |
| `actual_coverage` | Objekt | Nein | Byte-abgeleitete Gesamtdeckung und Zeilenzahl |
| `coverage_reconciliation` | Objekt | Nein | Datei-/Perioden-/Gesamtdeckungsstatus |
| `license_or_terms_ref` | UTF-8-String | Ja | Referenz auf Nutzungsbedingungen |

Fehlende Identitäts- oder Zeitmetadaten blockieren `CANONICAL_BUILD`.

Die kanonischen Feldnamen lauten `provider` und `retrieved_at_utc`.
`source_provider` und `source_retrieved_at_utc` dürfen nur als registrierte
Legacy-Eingangsaliase akzeptiert und nicht parallel in S0 oder S1
weitergeführt werden.

Das S0 Source Manifest muss das Schema
`rcc002.source-manifest/1.0.0` erfüllen. Das logische S0-Stufenschema bleibt
davon getrennt `rcc002.stage.s0-source/1.0.0`.
Die unveränderten Quelldateien selbst behalten ihr Providerformat und werden
als geordnete Einzelartefakte referenziert.
`source_files.source_file_ordinal` wird erst nach Sortierung auf
`provider_relative_name` vergeben und ist nullbasiert, lückenlos und
eindeutig. Doppelte Namen oder Perioden, abweichende Byte-/Providerhashes,
Pfadtraversierung oder nicht registrierte Perioden blockieren
`CANONICAL_BUILD`.

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

Für jede erwartete Periode werden als `source_files`-Eintrag erfasst:

- `source_file_ordinal`,
- erwarteter Dateiname,
- vorhanden/nicht vorhanden,
- Dateigröße,
- Quellchecksumme, falls angeboten,
- lokal berechnete Checksumme,
- Downloadstatus,
- Extraktionsstatus.

Die Liste wird vor dem Parsing kanonisch nach `provider_relative_name`
sortiert und anschließend ordinalisiert. Eine
spätere Dateisystem-, Glob- oder Locale-Reihenfolge darf sie nicht verändern.

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
- die im Spaltenprofil erwartete Anzahl interner Datendateien ist exakt erfüllt,
- Headerzustand entspricht exakt `header_mode` des registrierten Spaltenprofils,
- Encoding, BOM-Zustand, Zeilenende, Delimiter und Spaltenanzahl entsprechen
  exakt dem registrierten Spaltenprofil,
- lokale SHA-256-Checksumme wurde berechnet,
- angebotene Anbieterchecksumme stimmt, sofern verfügbar,
- keine unerwarteten zusätzlichen Nutzdaten wurden still übernommen.

`header_mode = ABSENT` bedeutet ausdrücklich, dass die erste physische Zeile
eine Datenzeile ist. Eine scheinbar plausible Headererkennung oder
Spaltenzuordnung nach Inhalt ist unzulässig. Das für Binance Spot Klines
registrierte Profil verlangt UTF-8 ohne BOM, LF, Komma, keinen Header und
exakt zwölf Spalten in registrierter Reihenfolge.

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
| `source_file_ordinal` | UInt32 | Nein | S0/S1 |
| `original_record_index` | UInt64 | Nein | S1 |
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

`original_record_index` ist der nullbasierte physische Datenzeilenindex innerhalb
der registrierten dekomprimierten Datendatei. Bei `header_mode = PRESENT`
zählt die Headerzeile nicht, bei `ABSENT` erhält die erste Zeile den Index
null.

Für `RCC002_S1_SOURCE_ROW_ID_V2/2.0.0` lautet die exakte UTF-8-/ASCII-
Darstellung:

```text
RCC002_S1_SOURCE_ROW_ID_V2:<source_snapshot_id>:<source_file_ordinal 8d>:<original_record_index 20d>
```

Die beiden Dezimalwerte sind links mit Nullen auf acht beziehungsweise
zwanzig Stellen aufzufüllen. Eine parallele Integerdarstellung oder eine
Ableitung aus dem später sortierten Zeilenindex ist unzulässig.

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

### 7.4 Providergebundene Spaltenabbildung

Für das registrierte Binance-Spot-Kline-Profil werden die zwölf
nullbasierten Quellspalten ausschließlich über
`column_profile_id` abgebildet:

```text
0 open_time_raw
1 open
2 high
3 low
4 close
5 volume
6 close_time_raw
7 quote_asset_volume
8 trade_count
9 taker_buy_base_asset_volume
10 taker_buy_quote_asset_volume
11 ignore
```

Fehlende, zusätzliche, vertauschte oder nicht parsebare Spalten sind
fail-closed. Namens- oder Typinferenz aus Datenwerten ist unzulässig.

### 7.5 Schema-Fingerprint

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

### 8.4 Zeitstempel-Einheit und Normalisierung

Vor dem Parsing wird aus `archive_period` und
`timestamp_unit_profile_id` exakt eine Einheit ausgewählt. Die Stellenzahl
oder Größenordnung eines einzelnen Rohwerts darf nicht zur Einheitserkennung
verwendet werden.

Für `BINANCE_SPOT_TIMESTAMP_UNITS_V1/1.0.0` gilt:

```text
archive period before 2025-01-01 -> millisecond
archive period from   2025-01-01 -> microsecond
```

Millisekundenwerte werden unverändert übernommen. Mikrosekundenwerte sind nur
gültig, wenn `open_time_raw mod 1000 = 0` und
`close_time_raw mod 1000 = 999`; beide kanonischen Zeitstempel entstehen
dann durch ganzzahlige Division durch 1000. Danach muss für `1m` gelten:

```text
close_time = open_time + 59999
```

Nicht registrierte Perioden, uneindeutige Profile oder Restklassenverletzungen
sind `CRITICAL` und blockieren den Build.

### 8.5 Entscheidungszeitpunkt

S2 MUST unterscheiden:

- Intervallbeginn,
- Intervallende,
- Zeitpunkt, zu dem eine geschlossene Kerze verfügbar ist.

Indikatoren oder Signale für Kerze `t` dürfen im späteren Handel erst nach dem
definierten Verfügbarkeitszeitpunkt dieser Kerze verwendet werden.

### 8.6 Sortierung

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

### 16.3 Reason-Code-Severity-Register

Jeder in §16.2 registrierte Reason Code besitzt genau eine
Standard-Severity gemäß nachfolgendem Register. Dieses Register erfüllt
die in §16.2 geforderte Eigenschaft „eine Standard-Severity besitzen" und
die Abnahmevoraussetzung §24.1 Nr. 3 vollständig.

Für Reason Codes, deren Severity bereits an anderer Stelle dieses
Dokuments normativ explizit festgelegt ist, übernimmt dieses Register
unverändert den dort festgelegten Wert. Das Register ersetzt keine dieser
Festlegungen; es konsolidiert sie an einer Stelle.

| # | Reason Code | Standard-Severity | Normative Referenz |
|---:|---|---|---|
| 1 | `DV_FILE_MISSING` | `ERROR` | §5.2 (mindestens `ERROR`; Herabstufung auf `WARN` nur bei genehmigter, dokumentierter Ausnahme) |
| 2 | `DV_FILE_EMPTY` | `ERROR` | §5.2 analog; §6.1 (nur `VERIFIED` darf regulär in S1 eingehen) |
| 3 | `DV_FILE_CORRUPT` | `CRITICAL` | §6.2 (strukturelle Öffnungs-/Parsefehler); §16.1 |
| 4 | `DV_CHECKSUM_MISMATCH` | `CRITICAL` | §6.2; §16.1 |
| 5 | `DV_FILE_SUSPECTED_ROW_LIMIT_TRUNCATION` | `ERROR` im Standardfall; `CRITICAL` bei vorgelagerter Evidenz für mehr Zeilen oder einen erwarteten längeren Zeitbereich | §6.3 (Eskalationsregel unverändert) |
| 6 | `DV_SCHEMA_REQUIRED_COLUMN_MISSING` | `CRITICAL` | §14.1 (Nullwerte in Primärschlüssel-, Zeit- oder OHLCV-Pflichtfeldern) |
| 7 | `DV_SCHEMA_UNEXPECTED_COLUMN` | `WARN` | §7.3 (Berichtspflicht ohne Blockierungswirkung) |
| 8 | `DV_PARSE_TIMESTAMP_FAILED` | `CRITICAL` | §14.1 |
| 9 | `DV_PARSE_NUMERIC_FAILED` | `CRITICAL` | §7.2 |
| 10 | `DV_TIME_NOT_UTC` | `CRITICAL` | §8.1 (unzulässig für `CANONICAL_BUILD`); §14.1 |
| 11 | `DV_TIME_MISALIGNED` | `CRITICAL` | §8.3; §14.1 |
| 12 | `DV_TIME_OUT_OF_RANGE` | `ERROR` | §9.3 (aktive Behandlungspflicht statt stillem Verwerfen) |
| 13 | `DV_DUPLICATE_IDENTICAL_COLLAPSED` | `INFO` | §10.1 (genehmigte, deterministische, verlustfreie Operation) |
| 14 | `DV_DUPLICATE_CONFLICT` | `CRITICAL` | §10.2 |
| 15 | `DV_SOURCE_CONFLICT_RESOLVED` | `INFO` | §15.2 (dokumentierter, genehmigt aufgelöster Zustand) |
| 16 | `DV_GAP_DETECTED` | `WARN` | §11.1 (unklassifizierter Befund; spezifischere Klassifikation kann eskalieren) |
| 17 | `DV_GAP_UNEXPLAINED` | `ERROR` | §11.2 (`UNKNOWN`-Klasse: mindestens `ERROR`; `CRITICAL` bei nachgewiesener Systematik) |
| 18 | `DV_TIME_GAP_SEGMENT_STARTED` | `INFO` | §11.3.1 (normale, dokumentierte Folge der Segmentbildungsregel) |
| 19 | `DV_NUMERIC_NONFINITE` | `CRITICAL` | §14.1 (funktionale Gleichwertigkeit zu Nullwert in OHLCV-Pflichtfeld) |
| 20 | `DV_OHLC_INVARIANT_FAILED` | `CRITICAL` | §12.1 |
| 21 | `DV_VOLUME_NEGATIVE` | `CRITICAL` | §12.2 |
| 22 | `DV_VOLUME_ZERO_OBSERVED` | `WARN` | §12.2 (nicht automatisch ungültig, aber aktive Beobachtungspflicht) |
| 23 | `DV_ANOMALY_EXTREME_CANDLE_RETURN` | `WARN` | §13.1, §13.3 (Untersuchungszweck; keine Wertveränderung) |
| 24 | `DV_ANOMALY_EXTREME_HIGH_LOW_RANGE` | `WARN` | §13.1, §13.3 |
| 25 | `DV_ANOMALY_EXTREME_VOLUME` | `WARN` | §13.1, §13.3 |
| 26 | `DV_ANOMALY_ZERO_VOLUME_CLUSTER` | `WARN` | §13.1, §13.3 |
| 27 | `DV_ANOMALY_REPEATED_IDENTICAL_OHLC` | `WARN` | §13.1, §13.3 |
| 28 | `DV_ANOMALY_PARTITION_BOUNDARY_JUMP` | `WARN` | §13.1, §13.3 |
| 29 | `DV_SYNTHETIC_ROW_NONCANONICAL` | `CRITICAL` | §11.4; Data Pipeline §7.3 (Ausschluss synthetischer Zeilen aus kanonischen Views) |
| 30 | `DV_APPROVED_WARNING_ACTIVE` | `INFO` | §20 (dokumentierte, genehmigte Nichtblockierung eines `WARN`) |
| 31 | `DV_ROW_RECONCILIATION_FAILED` | `CRITICAL` | §3.4; §17 (Reconciliation-Gleichungen) |
| 32 | `DV_SCHEMA_FINGERPRINT_MISMATCH` | `CRITICAL` | §7.4 (fail-closed bei unbekannter Major-Version) |

Die in der Spalte „Normative Referenz" mit einer wörtlichen Bestandsregel
belegten Severities sind unverändert aus der jeweils zitierten Stelle
übernommen. Alle übrigen Zuordnungen wurden im Rahmen des
Korrekturzyklus `RCC-002-DVSEV-001` (2026-07-27) hergeleitet, geprüft und
freigegeben; ihre Herleitung ist dokumentiert in
`docs/review/RCC_002_DVSEV_001_REASON_CODE_SEVERITY_CORRECTION_PROPOSAL_2026-07-27.md`.

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
- `source_file_ordinal`;
- `original_record_index`;
- `provider`

auf genau einen inventarisierten `source_files`-Eintrag und genau eine
physische Datenzeile zurückführen. Das Paar
`(source_file_ordinal, original_record_index)` muss innerhalb eines
`source_snapshot_id` eindeutig sein und die V2-Source-Row-ID exakt
reproduzieren.

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
- registriertes Abruf-, Spalten-, Zeitstempel- oder Source-Row-ID-Profil;
- registrierte Archivperiode;
- Inhalt oder Ordnung des kanonischen `source_files`-Inventars;
- byte-abgeleitete `actual_coverage`.

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
S8BCP-001 Revision 2 Corrected Candidate – Re-Review Pending
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

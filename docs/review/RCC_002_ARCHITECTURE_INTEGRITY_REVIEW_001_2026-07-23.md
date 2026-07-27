# RCC-002 Architecture Integrity Review 001

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokument-ID | `RCC_002_ARCHITECTURE_INTEGRITY_REVIEW_001` |
| Review-ID | `RCC-002-AIR-001` |
| Projekt | `RCC-002` |
| Dokumentklasse | Architecture Integrity Review |
| Datum | `2026-07-23` |
| Status | Completed – Architecture Corrections Required |
| Ergebnis | **NOT PASSED** |
| Prüfumfang | Vollständige RCC-002-Spezifikationsfamilie |
| Eingabepaket | `RCC_002_SCR_004_FULL_SPEC_BUNDLE_2026-07-23.md` |
| Eingabepaket SHA-256 | `e61b74ebf1775cf54b7a31c9d0759f0ce45763c58f1bace8e510499e82206b38` |
| Eingabepaket Zeilen | `8462` |
| Eingabepaket Bytes | `236099` |
| Vorgelagerter Review | `RCC-002-SCR-004` |
| Vorgelagertes Ergebnis | Passed |
| Nachgelagerter Schritt | Architekturkorrektur und erneute Prüfung |

---

## 1. Zweck

Dieser Bericht prüft die Architekturintegrität der vollständigen
RCC-002-Spezifikationsfamilie.

Der Review bewertet insbesondere:

- Stufengrenzen von `S0_SOURCE` bis `S8_EXPORT`;
- Eingabe- und Ausgabeverträge zwischen den Stufen;
- Feld-, Schema-, Zustands- und Identitätssemantik;
- Datenqualitäts- und Segmentierungsverträge;
- Trennung von Marktklassifikation, Handelsfreigabe und Strategie;
- Schutz vor Zukunftsinformationen;
- Reproduzierbarkeits- und Manifestarchitektur;
- logische und physische Konfigurationsverantwortung;
- Implementierungs- und Veröffentlichungs-Gates;
- Abhängigkeitsrichtung und Änderungsfolgen.

Der Review wiederholt nicht die vollständige wissenschaftliche Prüfung aus
`RCC-002-SCR-004`. Wissenschaftliche Inhalte werden nur dort erneut
betrachtet, wo ihre Spezifikation zu einem Architekturkonflikt führt.

---

## 2. Geprüfte Dokumente

| Nr. | Dokument | Version | Zeilen | Normalisierter SHA-256 |
|---:|---|---:|---:|---|
| 1 | `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md` | `0.5.0` | 1052 | `464f7d6901859266314875cd63a0c00ec9ab65106f46a76537da3b0dc2b02246` |
| 2 | `RCC_002_DATA_VALIDATION_2026-07-23.md` | `0.2.0` | 1000 | `4df3afc3c1c7cd77118f1dec12d3dc534eef943fa5c0eb72c3e29de142530e63` |
| 3 | `RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md` | `0.2.0` | 1191 | `9d452b7724d7088064438db08b9e92ca661397c6895fe1ce6cfe3c014415008a` |
| 4 | `RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md` | `0.2.0` | 1027 | `c4abe520fffcb70a2cfd731980c5b2806a85238a94312eed40cc6d363d1c38d3` |
| 5 | `RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md` | `0.3.0` | 1280 | `841f202c409d242f2908a77eedb492c24592115a42887b95be54caf4df6309c6` |
| 6 | `RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md` | `0.2.0` | 1241 | `ee3019ebfc91781d754195fd6139ebd251a2283f4cce2728eb82e21f1e7594c8` |
| 7 | `RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md` | `0.4.0` | 1599 | `abc1039b41117e7e468591b9dfe854aadeff29a6f5d8259aed90cb61307c03df` |

---

## 3. Bewertungsmaßstab

### 3.1 Schweregrade

| Schweregrad | Bedeutung |
|---|---|
| Blocker | Verhindert eine eindeutige, sichere oder unabhängig reproduzierbare Implementierung. |
| Major | Wesentliche Architekturlücke oder Mehrdeutigkeit mit hohem Risiko divergierender Implementierungen. |
| Minor | Begrenzter Konsistenz- oder Governancefehler ohne unmittelbare Verfälschung des Datenflusses. |

### 3.2 Reviewurteil

Der Review gilt nur als bestanden, wenn:

- kein Blocker offen ist;
- kein wesentlicher Architekturvertrag widersprüchlich ist;
- alle Stufenschnittstellen unabhängig implementierbar sind;
- Zukunftsinformationen durch vollständige logische Verträge ausgeschlossen
  werden;
- logische Identitäten und physische Artefaktidentitäten eindeutig getrennt
  sind;
- Implementierungs- und Veröffentlichungs-Gates widerspruchsfrei sind.

---

## 4. Rekonstruiertes Architekturmodell

Die Spezifikationsfamilie definiert folgenden gerichteten Datenfluss:

1. `S0_SOURCE` – unveränderte Quellartefakte und Quellenprovenienz;
2. `S1_NORMALIZED` – kanonische Zeit-, Feld- und Typnormalisierung;
3. `S2_VALIDATED` – validierte beobachtete Marktzeitreihe;
4. `S3_INDICATORS` – kausale Indikatoren und Zustandsqualität;
5. `S4_SIGNALS` – versionierte Signaltransformationen;
6. `S5_REGIMES` – kausale Marktklassifikation;
7. `S6_GATES` – getrennte Long- und Short-Freigaben;
8. `S7_LABELS` – Forward Returns und Forschungslabels;
9. `S8_EXPORT` – konsumbezogene, manifestgebundene Views.

### 4.1 Grundlegende Abhängigkeitsrichtung

Die vorgesehene Richtung ist azyklisch:

`S0 → S1 → S2 → S3 → S4 → S5 → S6 → S7 → S8`

`S7_LABELS` darf Zukunftsinformationen verwenden, darf aber keine Felder oder
Entscheidungen aus `S0` bis `S6` verändern.

### 4.2 Verantwortungsgrenzen

Die Spezifikationsfamilie trennt grundsätzlich:

- Marktdatenqualität in `S2`;
- Indikatorberechnung in `S3`;
- Signaltransformation in `S4`;
- Marktklassifikation in `S5`;
- Handelsfreigaben in `S6`;
- Forschungsziele in `S7`;
- konsumbezogene Veröffentlichung in `S8`.

Diese Trennung ist architektonisch tragfähig. Die im vorliegenden Review
gefundenen Probleme betreffen überwiegend die konkrete Ausformulierung der
gemeinsamen Verträge, nicht die grundsätzliche Stufenfolge.

---

## 5. Bestätigte Architekturqualitäten

### 5.1 Gerichteter Datenfluss

Es wurde keine normative Rückkopplung von einer späteren auf eine frühere
Stufe gefunden.

Insbesondere:

- `S7` darf keine `S0`-bis-`S6`-Felder verändern;
- Labels dürfen keine Point-in-Time-Gates beeinflussen;
- Regime beschreiben den Markt und erzeugen keine Trades;
- Gates erlauben oder blockieren Richtungen und erzeugen ebenfalls keine
  Trades.

### 5.2 Trennung von Regime, Gate, Strategie und Ausführung

Die Dokumente unterscheiden nachvollziehbar:

- Regimemodell;
- Gate-Profil;
- Entry- und Exit-Strategie;
- Risiko- und Ausführungslogik.

Ein `allow_long = true` oder `allow_short = true` ist ausdrücklich keine
Orderentscheidung.

### 5.3 Fail-closed-Grundsatz

Ungültige Pflichtinputs führen grundsätzlich zu:

- expliziter Invalidität;
- blockierten Richtungen;
- abgebrochener Veröffentlichung oder Quarantäne;
- maschinenlesbaren Fehlergründen.

Dieser Grundsatz ist dokumentübergreifend erkennbar.

### 5.4 Zeileninvarianten

Für die transformationsorientierten Stufen ist vorgesehen:

- `S3` behält die Zeilenmenge von `S2`;
- `S4` behält die Zeilenmenge von `S3`;
- `S5` behält die Zeilenmenge von `S4`;
- `S6` behält die Zeilenmenge von `S5`;
- `S7` behält die Zeilenmenge von `S6`.

Ungültige Zustände sollen gekennzeichnet und nicht still entfernt werden.

### 5.5 Partitionierung und Zustandswiederaufnahme

Die Spezifikationen berücksichtigen:

- Rolling-Overlap für fensterbasierte Berechnungen;
- Zustands-Snapshots für rekursive Indikatoren;
- Replay-Grenzen für persistierte Regime;
- Zukunfts-Overlap für Labels;
- Purge und Embargo an Splitgrenzen;
- invalidierte Tail-Horizonte.

### 5.6 Identitäts- und Lineagemodell

Das Reproduzierbarkeitsdokument trennt:

- `source_snapshot_id`;
- `build_id`;
- `dataset_id`;
- `artifact_id`;
- `dataset_artifact_set_id`;
- `run_id`;
- `manifest_id`.

Die Trennung von semantischem Inhalt, physischem Layout, konkreter Ausführung
und Manifestinhalt ist im Grundmodell korrekt angelegt.

### 5.7 Primärschlüssel

Der kanonische Primärschlüssel ist dokumentübergreifend:

- `market_type`;
- `symbol`;
- `interval`;
- `open_time`.

Vor einer Providerkonsolidierung wird zusätzlich `provider` berücksichtigt.

---

## 6. Befundübersicht

| Befund-ID | Schweregrad | Kurzbezeichnung | Status |
|---|---|---|---|
| `AIR-001-B01` | Blocker | Uneinheitlicher S0–S2-Qualitäts-, Provenienz- und Segmentvertrag | Offen |
| `AIR-001-B02` | Blocker | Widersprüchlicher S7-Namensraum und unvollständiger S8-Leakageschutz | Offen |
| `AIR-001-B03` | Blocker | Widersprüchliche S5-/S6-Zustands- und Ausgabeverträge | Offen |
| `AIR-001-M01` | Major | Fehlendes kanonisches Stufen- und View-Schemaregister | Offen |
| `AIR-001-M02` | Major | Semantische und physische Konfiguration nicht explizit getrennt | Offen |
| `AIR-001-M03` | Major | Widersprüchliche Zeitpunkte für offene Implementierungsentscheidungen | Offen |
| `AIR-001-m01` | Minor | Inkonsistente Dokument-ID der Data-Pipeline-Spezifikation | Offen |

Gesamt:

- Blocker: `3`
- Major: `3`
- Minor: `1`
- Offene Befunde: `7`

---

## 7. Blocker

### 7.1 `AIR-001-B01` – Uneinheitlicher S0–S2-Qualitäts-, Provenienz- und Segmentvertrag

#### Feststellung

Die Data-Pipeline-, Datenvalidierungs-, Indikator-, Regime-/Gate- und
Label-Spezifikationen verwenden unterschiedliche Feldnamen und teilweise
unterschiedliche Zustandsmodelle für dieselben Architekturinformationen.

#### Belege

Die Data-Pipeline-Spezifikation verlangt in `S0` unter anderem:

- `source_snapshot_id`;
- `source_provider`;
- `source_retrieved_at_utc`;
- `source_file_name`;
- `source_byte_sha256`;
- `source_revision`.

Die Datenvalidierung definiert dagegen als Eingabemetadaten unter anderem:

- `provider`;
- `retrieved_at_utc`;
- `source_format`;
- `source_location`.

Eine normative Abbildung zwischen diesen Namensräumen ist nicht festgelegt.

Die Data-Pipeline-Spezifikation verlangt in `S2`:

- `segment_id`;
- `is_observed_bar`;
- `synthetic_bar`;
- `duplicate_flag`;
- `gap_before`;
- `gap_after`;
- `source_conflict`;
- `market_values_valid`;
- `quality_gate_pass`;
- `quality_reason_mask`.

Die Datenvalidierung verlangt dagegen:

- `quality_is_observed`;
- `quality_is_synthetic`;
- `quality_has_source_conflict`;
- `quality_gap_before`;
- `quality_gap_after`;
- `quality_anomaly_flags`;
- `quality_status`;
- `quality_rule_version`.

Die Indikatorspezifikation konsumiert ausdrücklich den
`quality_*`-Namensraum und erzeugt zusätzlich einen
`indicator_segment_id`.

Die Label-Spezifikation verlangt eine Segmentgrenze, ohne dokumentübergreifend
eindeutig festzulegen, ob die relevante Identität:

- der `segment_id` aus `S2`;
- der `indicator_segment_id` aus `S3`;
- oder eine eigene Labelsegment-ID

ist.

Die Regime-/Gate-Spezifikation definiert `data_gate_pass` anhand der Freigabe
der aktuellen `S2`-Zeile. Die exakte Abbildung von `quality_status`,
Anomaliecodes und Gültigkeitsfeldern auf diese Freigabe fehlt.

#### Architekturrisiko

Unabhängige Implementierungen können:

- verschiedene Felder als kanonisch behandeln;
- Aliasfelder mit divergierenden Werten erzeugen;
- Datenlücken an unterschiedlichen Stellen zurücksetzen;
- Rolling Windows über unterschiedliche Segmentgrenzen berechnen;
- Labelhorizonte über unzulässige Grenzen führen;
- `data_gate_pass` unterschiedlich bestimmen.

Damit sind Stufenparität, Reproduzierbarkeit und unabhängige Verifikation nicht
gewährleistet.

#### Verbindlicher Korrekturauftrag

Es ist ein kanonischer gemeinsamer Vertrag für `S0`, `S1` und `S2`
festzulegen.

Dieser Vertrag muss mindestens enthalten:

1. exakte kanonische Feldnamen;
2. Datentypen;
3. Nullsemantik;
4. Eigentümerstufe;
5. erlaubte Alias- oder Migrationsnamen;
6. eindeutige Abbildung der Provenienzfelder;
7. eindeutige Abbildung aller Qualitätsfelder;
8. eine kanonische `S2`-Marktsegment-ID;
9. klare Abgrenzung zur `indicator_segment_id`;
10. Regeln für Labelsegment- und Zukunftsfenstergrenzen;
11. exakte Abbildung von `S2`-Qualität auf `data_gate_pass`;
12. versionierte Reason Codes und Gültigkeitsregeln.

Alle betroffenen Spezifikationen müssen denselben Vertrag referenzieren.

#### Schließungskriterium

Der Befund ist geschlossen, wenn eine maschinenlesbar umsetzbare
Feld- und Zustandsabbildung von `S0` bis zum Eingang von `S3`, `S5`, `S6` und
`S7` vorliegt und keine konkurrierenden kanonischen Feldnamen verbleiben.

---

### 7.2 `AIR-001-B02` – Widersprüchlicher S7-Namensraum und unvollständiger S8-Leakageschutz

#### Feststellung

Die Data-Pipeline-Spezifikation und die Label-Spezifikation definieren
unterschiedliche S7-Namensräume und unterschiedliche Horizon-Register.

Der S8-Schutz in der Data-Pipeline-Spezifikation deckt dadurch nicht alle
zulässigen S7-Felder ab.

#### Belege

Die Data-Pipeline-Spezifikation verlangt für S7-Felder das reservierte Präfix:

- `label_`.

Sie nennt als Horizonte:

- 5 Minuten;
- 15 Minuten;
- 30 Minuten;
- 60 Minuten;
- 240 Minuten.

Für Live- und Paper-Views verbietet sie ausdrücklich Felder, deren Namen mit
`label_` beginnen.

Die Label-Spezifikation reserviert dagegen drei S7-Präfixe:

- `fwd_`;
- `label_`;
- `barrier_`.

Sie definiert folgende Horizon-Suffixe:

- `_h001`;
- `_h005`;
- `_h015`;
- `_h060`;
- `_h240`;
- `_h1440`.

Damit:

- fehlt der 30-Minuten-Horizont im Labelregister;
- kommen 1 Minute und 1440 Minuten zusätzlich vor;
- können `fwd_*`- und `barrier_*`-Felder den ausschließlich auf `label_`
  bezogenen Ausschluss der Data-Pipeline-Spezifikation umgehen.

Die Label-Spezifikation selbst verlangt zwar den Ausschluss aller drei
Präfixe. Der übergeordnete S8-Vertrag bleibt jedoch widersprüchlich.

#### Architekturrisiko

Eine Implementierung, die nur den übergeordneten S8-Vertrag umsetzt, kann
Forward Returns oder Barrier-Outcomes in Live- oder Paper-Views
veröffentlichen.

Das ist ein unmittelbares Label-Leakage-Risiko.

Zusätzlich können unterschiedliche Horizon-Register zu:

- inkompatiblen S7-Schemata;
- unterschiedlichen Tail-Invaliditäten;
- abweichenden Purge- und Embargo-Grenzen;
- nicht vergleichbaren Forschungsartefakten

führen.

#### Verbindlicher Korrekturauftrag

Es ist genau ein verbindlicher S7-Vertrag festzulegen.

Dieser muss mindestens definieren:

1. das vollständige authoritative Horizon-Register;
2. alle zulässigen S7-Feldfamilien;
3. alle reservierten S7-Präfixe;
4. eindeutige S7-Schema-IDs und Versionen;
5. Horizon-, Kosten- und Barrier-Profilzuordnung;
6. S7-Feldprovenienz unabhängig vom bloßen Feldnamen;
7. positive S8-Allowlist je View;
8. vollständigen Ausschluss aller S7-Felder aus Live und Paper;
9. Leakage-Tests gegen Schema- und Stufenherkunft;
10. Präfixprüfungen nur als zusätzliche Schutzschicht.

Der Ausschluss darf nicht ausschließlich von Zeichenkettenpräfixen abhängen.
Ein Feld, das der Stufe `S7` gehört, muss unabhängig von seinem Namen aus Live
und Paper ausgeschlossen werden.

#### Schließungskriterium

Der Befund ist geschlossen, wenn Data-Pipeline-, Label- und Exportvertrag
dasselbe Horizon-Register und denselben S7-Namensraum verwenden und ein
automatischer Test jedes S7-Feld aus Live- und Paper-Views ausschließt.

---

### 7.3 `AIR-001-B03` – Widersprüchliche S5-/S6-Zustands- und Ausgabeverträge

#### Feststellung

Der übergeordnete Data-Pipeline-Vertrag und die detaillierte
Regime-/Gate-Spezifikation definieren unterschiedliche Zustände,
Serialisierungen und Pflichtfelder.

#### Belege

Die Data-Pipeline-Spezifikation nennt für `S5` mindestens:

- `bull`;
- `bear`;
- `side`;
- `unknown`;
- `invalid`.

Die Regime-/Gate-Spezifikation definiert dagegen:

- `BULL`;
- `SIDE`;
- `BEAR`;
- `UNKNOWN`.

Sie bestimmt zusätzlich, dass `UNKNOWN` ausschließlich einen
Invalid-/Unavailable-Zustand repräsentiert. Ein separater S5-Zustand
`INVALID` ist dort nicht definiert.

Die Data-Pipeline-Spezifikation verlangt für `S6`:

- `allow_long`;
- `allow_short`;
- `gate_profile_id`;
- `gate_profile_version`;
- `gate_reason_mask`;
- `gate_inputs_valid`.

Die Regime-/Gate-Spezifikation verlangt dagegen:

- `allow_long`;
- `allow_short`;
- `data_gate_pass`;
- `gate_state`;
- `gate_reason_codes_long`;
- `gate_reason_codes_short`;
- `gate_profile_id`;
- `gate_profile_version`;
- `gate_valid`;
- `gate_evaluated_at`;
- referenzierte Regime- und Kontextversionen.

Die detaillierte Spezifikation definiert außerdem für `gate_state`:

- `ALLOW_BOTH`;
- `ALLOW_LONG_ONLY`;
- `ALLOW_SHORT_ONLY`;
- `BLOCK_BOTH`;
- `INVALID`.

Damit bleiben insbesondere folgende Fragen widersprüchlich:

- Groß- oder Kleinschreibung der S5-Serialisierung;
- `UNKNOWN` versus `INVALID` in S5;
- Reason-Code-Liste versus Reason-Maske in S6;
- `gate_inputs_valid` versus `gate_valid`;
- Pflichtstatus von `data_gate_pass`;
- verbindliche S6-Ausgabemenge.

#### Architekturrisiko

Die Widersprüche verhindern ein eindeutiges:

- S5-Ausgabeschema;
- S6-Eingabeschema;
- S6-Ausgabeschema;
- Paritätsverfahren;
- Gate-Audit;
- Schema-Migrationsverfahren.

Ein ungültiger Zustand kann je nach Implementierung als Unknown-Regime,
Invalid-Regime, gültiges `BLOCK_BOTH` oder ungültiges Gate serialisiert werden.

#### Verbindlicher Korrekturauftrag

Es ist ein einziger kanonischer S5-/S6-Vertrag festzulegen.

Dieser muss mindestens enthalten:

1. vollständige S5-Enums;
2. exakte serialisierte Schreibweise;
3. getrennte Semantik von unbekannt, ungültig und neutral;
4. vollständige S5-Ausgabefelder;
5. vollständige S6-Eingabefelder;
6. vollständige S6-Ausgabefelder;
7. exakte Bedeutung von `data_gate_pass`;
8. exakte Bedeutung von `gate_valid`;
9. Behandlung profilabhängiger Pflichtinputs;
10. Long- und Short-spezifische Reason Codes;
11. definierte Reihenfolge und Serialisierung von Reason Codes;
12. versionierte Schema- und Kompatibilitätsregeln.

Die detaillierte Regime-/Gate-Spezifikation kann den fachlichen Vertrag
definieren. Die Data-Pipeline-Spezifikation muss ihn anschließend exakt und
ohne konkurrierende Kurzfassung referenzieren.

#### Schließungskriterium

Der Befund ist geschlossen, wenn aus demselben S5-/S6-Eingang in jeder
konformen Implementierung dieselben Zustände, Gültigkeitswerte,
Freigabeentscheidungen und Reason Codes entstehen.

---

## 8. Major-Befunde

### 8.1 `AIR-001-M01` – Fehlendes kanonisches Stufen- und View-Schemaregister

#### Feststellung

Die Data-Pipeline-Spezifikation verlangt für jede Stufe:

- Eingabeschemaversion;
- Ausgabeschemaversion;
- Pflichtfelder;
- Datentypen;
- Primärschlüssel;
- Sortierung;
- Warm-up;
- Invaliditätssemantik;
- Fehlerverhalten;
- Zeileninvariante;
- Komponenten-ID und Version.

Die Dokumente nennen einzelne Schemafelder und Fingerprints, weisen den
Schnittstellen aber kein vollständiges gemeinsames Register mit konkreten
Schema-IDs und Kompatibilitätsregeln zu.

Für `S8_EXPORT` werden Viewklassen genannt, jedoch keine vollständigen
logischen Viewverträge.

#### Architekturrisiko

Ein Build kann nicht zuverlässig prüfen, ob:

- ein Eingangsschema akzeptiert wird;
- eine Feldänderung kompatibel ist;
- eine View vollständig ist;
- ein Feld seiner Eigentümerstufe entspricht;
- zwei Implementierungen dieselbe Schnittstelle erzeugen.

#### Verbindlicher Korrekturauftrag

Die Spezifikationsfamilie benötigt ein normatives Schnittstellenregister.

Es muss mindestens enthalten:

1. Schema-ID und Version je Stufeneingang;
2. Schema-ID und Version je Stufenausgang;
3. Feldname, Datentyp und Nullbarkeit;
4. Feldverantwortung und Erzeugerstufe;
5. Primärschlüssel und Sortierung;
6. Enums und Reason-Code-Typen;
7. Segment- und Gültigkeitsfelder;
8. Kompatibilitätsregeln;
9. Migrationsregeln;
10. positive Feld-Allowlist je S8-View;
11. Leakage-Klasse je Feld;
12. Manifestreferenz auf die verwendeten Schema-IDs.

Die Data-Pipeline-Spezifikation muss Eigentümerin der logischen
Stufen- und Viewverträge sein.

Die Reproduzierbarkeits- und Manifest-Spezifikation bleibt Eigentümerin der:

- physischen Artefakte;
- physischen Layoutidentitäten;
- Manifeste;
- atomaren Veröffentlichung.

#### Schließungskriterium

Der Befund ist geschlossen, wenn alle Stufen und Views anhand konkreter,
versionierter und gegenseitig referenzierter Schemaverträge implementiert und
automatisch geprüft werden können.

---

### 8.2 `AIR-001-M02` – Semantische und physische Konfiguration nicht explizit getrennt

#### Herkunft

Dieser Befund übernimmt und präzisiert den aus `RCC-002-SCR-004`
weitergereichten Architekturpunkt `AIR-004-01`.

#### Feststellung

Die Reproduzierbarkeits- und Manifest-Spezifikation bestimmt:

- der `build_id` enthält einen kanonischen Konfigurations-Hash;
- das Stage Manifest enthält die effektive Konfiguration;
- deterministische Eingabeänderungen erzeugen eine neue Build-ID.

Sie bestimmt zugleich:

- Writerprofil;
- Kompression;
- Row-Group-Grenzen;
- Partitionierung;
- Containerparameter

dürfen `build_id` und `dataset_id` nicht verändern. Diese Merkmale gehören zur
physischen Artefaktprovenienz, zu `physical_layout_sha256`,
`artifact_id` und `dataset_artifact_set_id`.

Die beabsichtigte Semantik ist rekonstruierbar, aber der Namensraum
`configuration` trennt beide Konfigurationsklassen nicht normativ.

#### Architekturrisiko

Zwei konforme Implementierungen können unterschiedliche Konfigurationsmengen
in den Build-Hash aufnehmen.

Dadurch kann:

- derselbe logische Build verschiedene `build_id` erhalten;
- eine reine Repartitionierung unnötig einen neuen `dataset_id` erzeugen;
- eine semantische Regeländerung fälschlich nur als Layoutänderung gelten.

#### Verbindlicher Korrekturauftrag

Die Konfiguration ist normativ in mindestens zwei Namensräume zu trennen:

1. `semantic_build_configuration`
2. `physical_publication_configuration`

Für beide Namensräume sind festzulegen:

- kanonische Vorabbildung;
- eigener SHA-256;
- enthaltene und ausgeschlossene Schlüssel;
- Eigentümerkomponente;
- Wirkung auf alle Identitäten;
- Manifestposition;
- Änderungs- und Kompatibilitätsregeln.

Verbindliche Wirkung:

- `semantic_build_configuration_sha256` beeinflusst `build_id` und damit den
  logischen Datasetinhalt;
- `physical_publication_configuration_sha256` beeinflusst
  `physical_layout_sha256`, `artifact_id` und
  `dataset_artifact_set_id`;
- reine physische Neuverpackung verändert weder `build_id` noch
  `dataset_id`.

Manifestbeispiel, ID-Vorabbildungen, Akzeptanzkriterien und Tests müssen
dieselbe Trennung verwenden.

#### Schließungskriterium

Der Befund ist geschlossen, wenn jede Konfigurationsoption genau einer
Identitätsklasse zugeordnet ist und Golden Tests die erwartete ID-Wirkung
belegen.

---

### 8.3 `AIR-001-M03` – Widersprüchliche Zeitpunkte für offene Implementierungsentscheidungen

#### Feststellung

Die Data-Pipeline-Spezifikation verlangt vor dem Status
`Approved for Implementation` die Schließung oder versionierte Festlegung
unter anderem von:

- physischem Parquet-Schema;
- Partitionierungs- und Verzeichnislayout;
- Bibliotheksauswahl;
- Float-Toleranzen;
- JSON-Schema-Dateien und Versionsstrategie;
- Build-Einstiegspunkt;
- Lockdateiformat und ausführbarer Umgebung.

Die Reproduzierbarkeits- und Manifest-Spezifikation erlaubt, vergleichbare
Punkte vor oder während der Implementierung festzulegen, sofern sie vor einem
zertifizierten Dataset-Release dokumentiert sind.

#### Architekturrisiko

Es bleibt unklar, ob:

- die Spezifikationsbaseline bereits implementierungsbereit ist;
- logische Schnittstellen während der Implementierung noch verändert werden
  dürfen;
- die Freigabe `Approved for Implementation` erteilt werden kann;
- physische Optimierungen eine erneute Architekturprüfung benötigen.

#### Verbindlicher Korrekturauftrag

Die offenen Entscheidungen sind in zwei Klassen zu teilen.

Vor `Approved for Implementation` müssen mindestens verbindlich sein:

- logische Stufenschemata;
- logische S8-Viewverträge;
- Schema-IDs und Kompatibilitätsregeln;
- Identitätsvorabbildungen;
- semantische Konfigurationsgrenzen;
- numerische Determinismusprofile;
- Referenztoleranzen;
- Build-Einstiegspunktvertrag;
- Umgebungs- und Lockstrategie;
- Test- und Abnahmekriterien.

Während der Implementierung dürfen innerhalb zuvor definierter Profile
konkretisiert werden:

- physische Partitionsgrößen;
- Row-Group-Größen;
- Kompressionsstufe;
- Writeroptimierungen;
- Retentionsparameter;
- technisch gleichwertige Speicherorte.

Jede Änderung mit Wirkung auf fachliche Semantik, logische Schemata oder
Identitätsvorabbildungen muss die entsprechenden früheren Review-Gates erneut
durchlaufen.

#### Schließungskriterium

Der Befund ist geschlossen, wenn beide Dokumente denselben
Implementierungsfreigabezeitpunkt und dieselbe Klassifikation offener
Entscheidungen verwenden.

---

## 9. Minor-Befund

### 9.1 `AIR-001-m01` – Inkonsistente Dokument-ID der Data-Pipeline-Spezifikation

#### Herkunft

Dieser Punkt entspricht dem aus `RCC-002-SCR-004` weitergereichten
Editorialpunkt `ED-004-01`.

#### Feststellung

Die Data-Pipeline-Spezifikation verwendet in ihren Metadaten:

`RCC_002_DATA_PIPELINE_SPECIFICATION`

Das minimale Dataset-Manifest der Reproduzierbarkeits- und
Manifest-Spezifikation verwendet:

`RCC-002-DP`

Da das Spezifikationsprofil Bestandteil der Build-Identität ist, darf diese
Abweichung nicht als rein kosmetisch behandelt werden.

#### Verbindlicher Korrekturauftrag

Es ist genau eine kanonische Dokument-ID festzulegen und anschließend
einheitlich zu verwenden in:

- Dokumentmetadaten;
- Spezifikationsprofil;
- Manifestbeispielen;
- Build-ID-Vorabbildung;
- Reviewmanifesten;
- maschinenlesbaren Registern.

#### Schließungskriterium

Der Befund ist geschlossen, wenn derselbe Identifier in allen normativen und
beispielhaften Spezifikationsreferenzen vorkommt.

---

## 10. Auflösung der Übergabepunkte aus RCC-002-SCR-004

| Übergabepunkt | Bewertung in diesem Review | Ergebnis |
|---|---|---|
| `AIR-004-01` – semantische versus physische Konfiguration | Als `AIR-001-M02` vollständig geprüft | Nicht geschlossen; Architekturkorrektur erforderlich |
| `ED-004-01` – Dokument-ID | Als `AIR-001-m01` geprüft | Nicht geschlossen; vor Zertifizierung vereinheitlichen |

Damit wurden beide Übergabepunkte übernommen und nicht still verworfen.

---

## 11. Dokumentübergreifende Korrekturmatrix

| Befund | DP | DV | IND | SIG | RG | LBL | RM |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `AIR-001-B01` | X | X | X |  | X | X | X |
| `AIR-001-B02` | X |  |  |  |  | X | X |
| `AIR-001-B03` | X |  |  | X | X | X | X |
| `AIR-001-M01` | X | X | X | X | X | X | X |
| `AIR-001-M02` | X |  |  |  |  |  | X |
| `AIR-001-M03` | X |  | X | X | X | X | X |
| `AIR-001-m01` | X |  |  |  |  |  | X |

Legende:

- `DP` – Data Pipeline;
- `DV` – Data Validation;
- `IND` – Indicator Specification;
- `SIG` – Signal Transformation;
- `RG` – Regime and Gate;
- `LBL` – Label and Forward Return;
- `RM` – Reproducibility and Manifest.

Die Matrix kennzeichnet voraussichtlich betroffene Dokumente. Sie ersetzt
nicht die erneute vollständige Abhängigkeitsprüfung nach der Korrektur.

---

## 12. Verbindliche Korrekturreihenfolge

Die Befunde sollen in folgender Reihenfolge bearbeitet werden:

1. kanonisches Stufen- und View-Schemaregister festlegen;
2. S0–S2-Provenienz-, Qualitäts- und Segmentvertrag vereinheitlichen;
3. S5-/S6-Zustands- und Ausgabevertrag vereinheitlichen;
4. S7-Namensraum, Horizon-Register und S8-Allowlist vereinheitlichen;
5. semantische und physische Konfigurationsnamensräume trennen;
6. Implementierungs- und Veröffentlichungszeitpunkte vereinheitlichen;
7. kanonische Dokument-ID festlegen;
8. alle sieben Dokumente und ihre Abhängigkeitsreferenzen aktualisieren;
9. vollständige interne Struktur- und Hashprüfung durchführen;
10. ein neues vollständiges Reviewpaket erzeugen.

Die Korrekturen dürfen nicht ausschließlich in einem Reviewbericht oder
zusätzlichen Kommentar stehen. Sie müssen in den normativen
Spezifikationsdokumenten selbst wirksam werden.

---

## 13. Erforderliche Wiederholungsprüfungen

Mehrere Blockerkorrekturen berühren wissenschaftlich relevante Semantik:

- Horizon-Register;
- Labelgültigkeit;
- Segmentgrenzen;
- Unknown-/Invalid-Semantik;
- Datenqualitäts-Gates.

Deshalb gilt nach der Korrektur folgende Reihenfolge:

1. interne Qualitätskontrolle aller geänderten Spezifikationen;
2. neues vollständiges Spezifikationspaket;
3. fokussierter Scientific Consistency Re-Review der semantisch geänderten
   Verträge;
4. fokussierter Architecture Integrity Re-Review aller sieben Befunde;
5. Editorial Pass;
6. Internal Certification;
7. Claude Independent Architecture Review;
8. Gemini Independent Scientific and Adversarial Audit;
9. ChatGPT Final Consolidation;
10. `Baseline V1 Certified`.

Claude- oder Gemini-Prüfungen werden durch diesen Bericht weder behauptet noch
vorweggenommen.

---

## 14. Abnahmekriterien für den Architecture Integrity Re-Review

Der nächste Architecture Integrity Re-Review darf nur bestehen, wenn:

1. alle sieben Befunde explizit adressiert sind;
2. alle geänderten Dokumentversionen und Abhängigkeiten konsistent sind;
3. S0–S2 genau einen Feld- und Segmentvertrag besitzen;
4. `data_gate_pass` aus einer eindeutigen S2-Regel entsteht;
5. S5 genau ein Zustandsenum und eine Serialisierung besitzt;
6. S6 genau einen vollständigen Eingabe- und Ausgabevertrag besitzt;
7. S7 genau ein Horizon-Register und einen Feldnamensraum besitzt;
8. jede S8-View eine positive Allowlist besitzt;
9. Live und Paper sämtliche S7-Felder unabhängig vom Präfix ausschließen;
10. alle Stufenschemata konkrete IDs und Versionen besitzen;
11. logische und physische Konfiguration getrennt gehasht werden;
12. Identitätsänderungstests die erwartete Wirkung jeder
    Konfigurationsklasse nachweisen;
13. Implementierungs- und Release-Gates denselben Zeitplan verwenden;
14. die Data-Pipeline-Dokument-ID einheitlich ist;
15. kein neuer dokumentübergreifender Widerspruch entstanden ist;
16. die vollständige Spezifikationsfamilie erneut geprüft wurde.

---

## 15. Reviewurteil

### 15.1 Ergebnis

**NOT PASSED – ARCHITECTURE CORRECTIONS REQUIRED**

### 15.2 Begründung

Die grundlegende RCC-002-Stufenarchitektur ist sinnvoll und weitgehend sauber
getrennt.

Die aktuelle Spezifikationsfamilie ist dennoch noch nicht eindeutig und sicher
implementierbar, weil:

- der gemeinsame S0–S2-Vertrag nicht kanonisch vereinheitlicht ist;
- S7- und S8-Verträge ein Label-Leakage-Risiko offenlassen;
- S5- und S6-Verträge widersprüchliche Zustände und Pflichtfelder verwenden;
- konkrete gemeinsame Stufen- und View-Schemata fehlen;
- semantische und physische Konfiguration nicht normativ getrennt sind;
- der Zeitpunkt offener Implementierungsentscheidungen widersprüchlich ist.

Die drei Blocker verhindern die Architekturfreigabe.

### 15.3 Freigabewirkung

Mit diesem Stand dürfen folgende Status nicht erteilt werden:

- `Architecture Integrity Passed`;
- `Editorial Ready`;
- `Internal Certification Ready`;
- `Baseline V1 Certified`;
- `Approved for Implementation`.

Der nächste zulässige Arbeitsschritt ist die dokumentübergreifende
Architekturkorrektur.

---

## 16. Schlussbestimmung

`RCC-002-AIR-001` bestätigt eine tragfähige Grundarchitektur, verweigert aber
die Freigabe der aktuellen Spezifikationsfamilie.

Die Architektur kann nach Schließung der sieben Befunde erneut geprüft werden.
Eine Freigabe darf ausschließlich auf Grundlage des vollständig korrigierten,
neu paketierten und erneut verifizierten Dokumentstands erfolgen.
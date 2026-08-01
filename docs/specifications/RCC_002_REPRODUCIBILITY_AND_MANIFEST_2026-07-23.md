# RCC-002 Reproducibility and Manifest Specification

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Normative technische und wissenschaftliche Spezifikation |
| Speicherort | `docs/specifications/` |
| Dateiname | `RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md` |
| Dokument-ID | `RCC-002-RM` |
| Version | `0.9.0` |
| Datum | `2026-07-23` |
| Status | RCC-002-S8RR002-BCP-001-REV2 Corrected Candidate – Independent Review of Generated Artifacts Pending |
| Geltungsbereich | RCC-002-Datenpipeline, Stufen S0–S8 |
| Verbindlichkeit | Normativ für die RCC-002-Implementierung |
| Primäre Abhängigkeit | `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`, Version `0.8.0` |
| Fachliche Abhängigkeiten | `RCC_002_DATA_VALIDATION_2026-07-23.md`, Version `0.6.0`; `RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md`, Version `0.4.3`; `RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md`, Version `0.4.2`; `RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md`, Version `0.5.1`; `RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md`, Version `0.5.0` |
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

Die Vorabbildung des `source_snapshot_id` MUSS exakt dem Profil
`RCC002_SOURCE_SNAPSHOT_ID_V1/1.0.0` entsprechen und folgende Schlüssel
enthalten:

- `identity_profile_id`;
- `source_retrieval_profile_id` und `source_retrieval_profile_version`;
- `provider`, `market_type`, `dataset_kind`, `symbol` und `interval`;
- `column_profile_id` und `timestamp_unit_profile_id`;
- `source_revision`;
- `source_files`;
- `actual_coverage`.

Jeder `source_files`-Eintrag enthält exakt `provider_relative_name`,
`byte_sha256`, `provider_checksum_sha256`, `size_bytes`, `csv_member_name`,
`source_file_ordinal`, `archive_period`, `record_count`,
`min_open_time_utc_ms`, `max_close_time_utc_ms` und `timestamp_unit`.
`archive_period` enthält Familie, Token, inklusive UTC-Start- und exklusive
UTC-Endgrenze. Die Liste wird nach normalisiertem `provider_relative_name`
sortiert; erst danach werden nullbasierte, lückenlose und eindeutige Ordinale
vergeben. Die ID-Darstellung lautet:

```text
source:sha256:<64 lowercase hex characters>
```

Provider-Revisionskennungen, registrierte Perioden, alle Source-Dateiwerte,
die byte-abgeleitete Gesamtdeckung und die registrierten Profile MÜSSEN die
Identität beeinflussen. Abrufzeitpunkt, lokaler
Speicherpfad, Hostname, Benutzername, Transport-Retrys und Cache-Ort sind
Run- beziehungsweise Provenienzmetadaten und DÜRFEN den
`source_snapshot_id` NICHT verändern.

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

Die `dataset_artifact_set_id` identifiziert ausschließlich die konkrete
physische Menge der als `DATA_ARTIFACT` klassifizierten veröffentlichten
Datenartefakte eines logischen Datasets. Ihre exakte Vorabbildung lautet:

```json
{
  "identity_profile_id": "RCC002_DATASET_ARTIFACT_SET_ID_V1",
  "dataset_id": "dataset:sha256:<digest>",
  "physical_publication_configuration_sha256": "<64 lowercase hex>",
  "data_artifacts": [
    {
      "logical_name": "<registered name>",
      "relative_path": "<portable path>",
      "artifact_id": "artifact:sha256:<digest>",
      "byte_sha256": "<64 lowercase hex>",
      "semantic_sha256": "<64 lowercase hex>",
      "physical_layout_sha256": "<64 lowercase hex>",
      "size_bytes": 0,
      "schema_ref": "<schema_id>/<schema_version>",
      "schema_fingerprint_sha256": "<64 lowercase hex>",
      "view_allowlist_sha256": "<64 lowercase hex or null>"
    }
  ]
}
```

`data_artifacts` wird nach normalisiertem `relative_path` und danach
`logical_name` sortiert. Nur `DATA_ARTIFACT`-Einträge sind zulässig. Die
nach RFC 8785 kanonisierten Bytes werden mit SHA-256 gehasht und als
`dataset-artifact-set:sha256:<digest>` dargestellt.

Eine reine Repartitionierung oder Neuverpackung behält bei semantisch
identischen Inhalten denselben `dataset_id`, erzeugt aber eine neue
`dataset_artifact_set_id`.

JSON Schemas, Spezifikationen und Registries sind `SCHEMA_ARTIFACT`;
Source-, Stage-, Run-, Dataset- und Reproduktionsmanifeste sind
`CONTROL_MANIFEST`; Review-Manifeste und menschliche Review-/
Zertifizierungsnachweise sind `REVIEW_ARTIFACT`; die abschließende
Prüfsummenliste ist `RELEASE_LEDGER`. Diese vier Klassen gehen weder in die
`dataset_artifact_set_id` noch in deren geordnete Artefaktliste ein.

### 5.9 Manifest ID

Der `manifest_id` wird erst berechnet, nachdem alle anderen deterministischen
IDs im Manifest feststehen. Ein Manifest enthält weder seinen finalen
Datei-Bytehash noch seine finale Dateigröße noch eine eigene `artifact_id`.

Berechnung:

1. Manifestinhalt ohne Feld `manifest_id` kanonisieren;
2. SHA-256 der kanonischen Bytes berechnen;
3. Ergebnis als `manifest_id` einsetzen;
4. das vollständige Manifest speichern.

Der Bytehash und die Bytegröße der finalen Manifestdatei werden ausschließlich
von einem nachgelagerten Objekt protokolliert: bei Kandidaten durch den
Release-Builder außerhalb des Kandidatenmanifests, bei finalen Releases durch
`RELEASE_LEDGER`. Der Ledger enthält weder seinen eigenen Hash noch seine
eigene Größe; deren Nachweis gehört in den externen Release-Record. Damit
existiert keine Selbsthash- oder gegenseitige Hashzirkularität.

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
| `source_snapshot_preimage_sha256` | Hash der exakt kanonisierten Source-Snapshot-Vorabbildung |
| `provider` | kanonische Providerbezeichnung |
| `market_type` | registrierter Markttyp |
| `dataset_kind` | registrierte Datenfamilie |
| `symbol` | registriertes Symbol |
| `interval` | registriertes Datenintervall |
| `retrieved_at_utc` | tatsächlicher Abrufzeitpunkt, nur Provenienz |
| `source_retrieval_profile_id` / `source_retrieval_profile_version` | registriertes Abruf- und Periodenprofil |
| `column_profile_id` | registriertes Spalten-, Header-, Delimiter- und Encodingprofil |
| `timestamp_unit_profile_id` | registriertes periodenselektiertes Zeitstempelprofil |
| `source_row_id_profile_id` / `source_row_id_profile_version` | Source-Row-ID-Profil V2 |
| `source_files` | vollständige geordnete Liste physischer Quellartefakte |
| `actual_coverage` | byte-abgeleitete Gesamtdeckung und Zeilenzahl |
| `coverage_reconciliation` | Ergebnis der Datei-/Gesamtdeckungsprüfung |
| `license_or_terms_ref` | optionale Referenz auf Nutzungsbedingungen |

Jeder `source_files`-Eintrag MUSS die in §5.3 definierte exakte Feldmenge
besitzen. Der Manifest-Validator MUSS zusätzlich beweisen, dass:

- nach `provider_relative_name` sortiert und danach ordinalisiert wurde;
- `source_file_ordinal` mit null beginnt, lückenlos und eindeutig ist;
- jeder Bytehash und jede Bytegröße auf das unveränderte Einzelartefakt zeigt;
- jeder Providerhash verifiziert ist;
- jede `archive_period` durch das Abrufprofil zulässig ist;
- Datei- und Gesamtdeckung byte-abgeleitet und widerspruchsfrei sind.

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
  "publication_candidate": {},
  "review_requirements": []
}
```

Dieses Objekt ist der deterministische Dataset-Manifest-Kandidat. Es darf
keine Ergebnisse enthalten, die erst nach seiner Erzeugung entstehen,
insbesondere keine Review-Manifest-IDs, Reproduktions-Manifest-IDs,
Release-Ledger-Hashes oder eigenen finalen Dateiwerte.

Review- und Reproduktionsmanifeste referenzieren den Kandidaten einseitig über
`subject_dataset_manifest_id`. Der externe Release-Record darf anschließend
den Kandidaten, die erfolgreichen Review-/Reproduktionsmanifeste und den
Release Ledger gemeinsam referenzieren. Kein Pfeil darf zum erneuten Hashen
eines bereits identifizierten Vorgängerobjekts führen.

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

Die Korrektur `RCC-002-S8RR002-BCP-001-REV2` führt zusätzlich Dataset
Manifest Schema `1.0.1` ein:

| Manifesttyp | `schema_id` | `schema_version` | `schema_ref` |
|---|---|---|---|
| Dataset Manifest | `rcc002.dataset-manifest` | `1.0.1` | `rcc002.dataset-manifest/1.0.1` |

Schema `1.0.1` behebt die strukturelle Akzeptanz von `views`- und
`specification_profile`-Arrays, die bereits gegen den fachlichen Vertrag
dieses Dokuments (§8.7 und §12.3) ungültig sind: fehlende, doppelte,
umgeordnete, unbekannte oder veraltete Einträge sowie hash-inkonsistente
Einträge. Dataset Manifest Schema `1.0.0` bleibt als zertifiziertes,
bytegleiches historisches Artefakt samt seiner historischen Fixtures
unverändert erhalten und bleibt für historische Verifikation zulässig. Es
ist für prospektive S8-Produktion zurückgezogen: neuer Code DARF Dataset
Manifest `1.0.0` NICHT ausgeben.

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
| `rcc002.view.audit` | `2.0.0` | `rcc002.view.audit/2.0.0` | Ja | `0e223d60ed4139f73194f1cb3b886a8eface9229183ad522a093e966827518cc` |

`DatasetManifest.views` ist die kanonische, geordnete Registry-Momentaufnahme
des aktuellen RCC-002-Datenprofils in exakt der oben angegebenen Reihenfolge
mit exakt den oben genannten sechs Einträgen; es ist nicht das physische
Artefaktinventar. Physisch materialisierte Views eines konkreten Builds
werden getrennt unter `artifacts` erfasst; ein minimaler Build kann daher
weniger als sechs physische Datenartefakte enthalten, während `views`
weiterhin exakt die genannten sechs Schemata registriert. Fehlende,
doppelte, umgeordnete, unbekannte, veraltete oder hash-inkonsistente
Einträge in `views` machen das gesamte Dataset Manifest ungültig.

Die vollständig expandierten Listen und ihre kanonische Hashvorabbildung
stehen autoritativ in
`RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`, Version `0.8.0`,
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

Audit View V1 ist zurückgezogen. Audit View V2 enthält exakt die 534
geordneten Felder von `label-research/1.0.0`, denselben Allowlist-Hash und nur
Felder der Erzeugerstufen S0 bis S7.

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
| `RCC_002_DATA_PIPELINE_SPECIFICATION` | `0.8.0` |
| `RCC-002-DV` | `0.6.0` |
| `RCC-002-IS` | `0.4.3` |
| `RCC-002-ST` | `0.4.2` |
| `RCC-002-RG` | `0.5.1` |
| `RCC-002-LF` | `0.5.0` |
| `RCC-002-RM` | `0.9.0` |

Eine bloße Dateinennung ohne Dokument-ID und Version ist nicht ausreichend.

Für ein deklariertes Dataset-Manifest-Profil ist `specification_profile`
exakt, geordnet und geschlossen: genau die sieben oben genannten Dokumente in
der angegebenen Reihenfolge, ohne zusätzlichen, fehlenden, doppelten,
umgeordneten, unbekannten oder veralteten Eintrag. Die Formulierung „MUSS
mindestens... referenzieren" regelt ausschließlich die Vollständigkeit über
künftige Profilversionen der RCC-002-Spezifikationsfamilie hinweg; sie
erlaubt keine zusätzlichen Einträge innerhalb eines einzelnen deklarierten
aktuellen Profils. Eine künftige zusätzliche Spezifikation erfordert ein
explizites neues Profil und eine Schema-Revision; sie DARF NICHT still an ein
`1.0.1`-Manifest angehängt werden. Fehlende, doppelte, umgeordnete,
unbekannte, veraltete oder hash-inkonsistente Einträge machen das gesamte
Dataset Manifest ungültig.

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
| `artifact_class` | Exakt eine der fünf normativen Release-Klassen |
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

Die normative Klassifikation lautet:

| `artifact_class` | Beispiele | Teil von `dataset_artifact_set_id` |
|---|---|:---:|
| `DATA_ARTIFACT` | S8-Viewdaten und veröffentlichte Datenpartitionen | Ja |
| `SCHEMA_ARTIFACT` | JSON Schemas, Feldregistries, Profile | Nein |
| `CONTROL_MANIFEST` | Source-, Stage-, Run-, Dataset- und Reproduktionsmanifeste | Nein |
| `REVIEW_ARTIFACT` | Review-Manifeste und menschliche Review-/Zertifizierungsnachweise | Nein |
| `RELEASE_LEDGER` | abschließende portable Prüfsummenliste | Nein |

Jedes inventarisierte Objekt besitzt genau eine Klasse. Eine fehlende oder
mehrdeutige Klasse ist fail-closed. Nur `DATA_ARTIFACT`-Einträge fließen in
die Artefaktmengenvorabbildung aus §5.8 ein.

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

Die zirkelfreie Erzeugungs- und Referenzreihenfolge ist:

1. `DATA_ARTIFACT` und `SCHEMA_ARTIFACT` finalisieren;
2. Source-, Stage- und Run-Manifeste finalisieren;
3. den deterministischen Dataset-Manifest-Kandidaten ohne nachgelagerte
   Review- oder Ledgerergebnisse bilden;
4. Review- und Reproduktionsmanifeste erzeugen; sie referenzieren den
   Kandidaten einseitig;
5. alle freizugebenden Dateien außer dem Ledger byteweise finalisieren;
6. `SHA256SUMS` als `RELEASE_LEDGER` zuletzt erzeugen; er listet alle
   freizugebenden Dateien außer sich selbst in lexikographischer Pfadreihenfolge;
7. den Ledger-Bytehash ausschließlich im externen Release-Record erfassen;
8. den vollständig geprüften Kandidaten atomar veröffentlichen.

Kein früheres Objekt wird nach Bildung seiner ID wegen eines späteren
Review-, Reproduktions- oder Ledgerobjekts neu geschrieben.

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
  "manifest_schema_version": "1.0.1",
  "manifest_schema_ref": "rcc002.dataset-manifest/1.0.1",
  "manifest_type": "dataset",
  "manifest_id": "manifest:sha256:0000000000000000000000000000000000000000000000000000000000000000",
  "created_at_utc": "2026-07-30T12:00:00Z",
  "producer": {
    "component": "rcc002-fixture-builder",
    "version": "1.0.0"
  },
  "project": "RCC-002",
  "status": "candidate",
  "dataset_id": "dataset:sha256:0000000000000000000000000000000000000000000000000000000000000000",
  "dataset_artifact_set_id": "dataset-artifact-set:sha256:0000000000000000000000000000000000000000000000000000000000000000",
  "dataset_artifact_set_preimage_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
  "dataset_profile": "rcc002-canonical",
  "build_id": "build:sha256:0000000000000000000000000000000000000000000000000000000000000000",
  "publication_run_id": "run:2026-07-30T12:00:00Z:00000000-0000-4000-8000-000000000000",
  "source_snapshot_ids": [
    "source:sha256:0000000000000000000000000000000000000000000000000000000000000000"
  ],
  "artifacts": [
    {
      "artifact_class": "DATA_ARTIFACT",
      "logical_name": "audit-v2",
      "relative_path": "data/rcc002/audit.parquet",
      "artifact_id": "artifact:sha256:0000000000000000000000000000000000000000000000000000000000000000",
      "byte_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
      "semantic_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
      "physical_layout_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
      "size_bytes": 1,
      "schema_ref": "rcc002.view.audit/2.0.0",
      "schema_fingerprint_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
      "view_allowlist_sha256": "0e223d60ed4139f73194f1cb3b886a8eface9229183ad522a093e966827518cc"
    }
  ],
  "schema_artifacts": [
    {
      "artifact_class": "SCHEMA_ARTIFACT",
      "logical_name": "source-manifest-schema",
      "relative_path": "schemas/rcc002/manifests/source-manifest/1.0.0.schema.json",
      "byte_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
      "size_bytes": 1
    }
  ],
  "child_manifests": [
    {
      "artifact_class": "CONTROL_MANIFEST",
      "manifest_type": "source",
      "manifest_id": "manifest:sha256:0000000000000000000000000000000000000000000000000000000000000000",
      "relative_path": "manifests/source.json",
      "byte_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
      "size_bytes": 1
    }
  ],
  "stages": [
    {
      "id": "S0",
      "version": "1.0.0",
      "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
    },
    {
      "id": "S1",
      "version": "1.0.0",
      "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
    },
    {
      "id": "S2",
      "version": "1.0.0",
      "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
    },
    {
      "id": "S3",
      "version": "1.0.0",
      "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
    },
    {
      "id": "S4",
      "version": "1.0.0",
      "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
    },
    {
      "id": "S5",
      "version": "1.0.0",
      "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
    },
    {
      "id": "S6",
      "version": "1.0.0",
      "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
    },
    {
      "id": "S7",
      "version": "1.0.0",
      "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
    }
  ],
  "registries": [
    {
      "id": "RCC002_SOURCE_RETRIEVAL_REGISTRY_V1",
      "version": "1.0.0",
      "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
    }
  ],
  "views": [
    {
      "schema_id": "rcc002.view.research-features",
      "schema_version": "1.0.0",
      "schema_ref": "rcc002.view.research-features/1.0.0",
      "schema_fingerprint_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
      "allowlist_sha256": "2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e"
    },
    {
      "schema_id": "rcc002.view.backtest-inputs",
      "schema_version": "1.0.0",
      "schema_ref": "rcc002.view.backtest-inputs/1.0.0",
      "schema_fingerprint_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
      "allowlist_sha256": "2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e"
    },
    {
      "schema_id": "rcc002.view.paper",
      "schema_version": "1.0.0",
      "schema_ref": "rcc002.view.paper/1.0.0",
      "schema_fingerprint_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
      "allowlist_sha256": "2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e"
    },
    {
      "schema_id": "rcc002.view.live",
      "schema_version": "1.0.0",
      "schema_ref": "rcc002.view.live/1.0.0",
      "schema_fingerprint_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
      "allowlist_sha256": "2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e"
    },
    {
      "schema_id": "rcc002.view.label-research",
      "schema_version": "1.0.0",
      "schema_ref": "rcc002.view.label-research/1.0.0",
      "schema_fingerprint_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
      "allowlist_sha256": "0e223d60ed4139f73194f1cb3b886a8eface9229183ad522a093e966827518cc"
    },
    {
      "schema_id": "rcc002.view.audit",
      "schema_version": "2.0.0",
      "schema_ref": "rcc002.view.audit/2.0.0",
      "schema_fingerprint_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
      "allowlist_sha256": "0e223d60ed4139f73194f1cb3b886a8eface9229183ad522a093e966827518cc"
    }
  ],
  "specification_profile": [
    {
      "id": "RCC_002_DATA_PIPELINE_SPECIFICATION",
      "version": "0.8.0",
      "sha256": "0e060d30b75082b74eb5211b1d378837aa7872d86f62e5e162586e2a2cc37fad"
    },
    {
      "id": "RCC-002-DV",
      "version": "0.6.0",
      "sha256": "459c4a99a266b420d52a69f2fb1a6b36a99529e999842bc8271f3336c444bb31"
    },
    {
      "id": "RCC-002-IS",
      "version": "0.4.3",
      "sha256": "0d8ad604cce88daa56193ee054f4d28237d60135a67cebbde883d2c00d18539d"
    },
    {
      "id": "RCC-002-ST",
      "version": "0.4.2",
      "sha256": "b3de8b4b7c69c30fd811edbeceb246b1b981d7d561c54b585535e72ca0fd8c74"
    },
    {
      "id": "RCC-002-RG",
      "version": "0.5.1",
      "sha256": "37ee84f1ddd86c0765e9c4df3b57aa5907472ba481f54181e8f8d6dccf354cdc"
    },
    {
      "id": "RCC-002-LF",
      "version": "0.5.0",
      "sha256": "526665966c83c8fc7254c663474fe08ee721125ae6cdcd88e5a4f5b80af5882f"
    },
    {
      "id": "RCC-002-RM",
      "version": "0.9.0",
      "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
    }
  ],
  "code_provenance": {
    "repository": "sniper-bot",
    "commit_sha": "0000000000000000000000000000000000000000",
    "worktree_clean": true,
    "dirty_patch_sha256": null
  },
  "semantic_build_configuration": {
    "profile_id": "semantic-v1",
    "canonical_sha256": "0000000000000000000000000000000000000000000000000000000000000000"
  },
  "physical_publication_configuration": {
    "profile_id": "physical-v1",
    "canonical_sha256": "0000000000000000000000000000000000000000000000000000000000000000"
  },
  "environment_reference": {
    "id": "RCC_BUILD_ENV_IDENTITY_V2",
    "version": "1.0.0",
    "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
  },
  "quality_summary": {
    "status": "PASS",
    "critical_findings": 0,
    "error_findings": 0,
    "warning_findings": 0
  },
  "dataset_lineage": {
    "graph_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
    "acyclic": true
  },
  "knowledge_lineage": {
    "graph_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
    "acyclic": true
  },
  "publication_candidate": {
    "status": "candidate",
    "supersedes": []
  },
  "review_requirements": [
    {
      "review_type": "scientific",
      "required": true
    }
  ]
}
```

Der Beispielzeitstempel ist kein vorgegebener realer Buildzeitpunkt.
Implementierungen MÜSSEN reale Werte einsetzen. Das Beispiel enthält bewusst
keine Reviewresultate, Reproduktionsresultate, Ledgerreferenz und keine
Selbstwerte der finalen Manifestdatei.

Der `sha256`-Wert des `specification_profile`-Eintrags `RCC-002-RM/0.9.0`
ist ausschließlich ein expliziter Nullwert-Platzhalter (64 Nullzeichen) für
die unvermeidliche Selbstreferenz dieses Dokuments auf sich selbst; er ist
kein realer Dateihash und darf niemals als solcher interpretiert werden. Alle
sechs übrigen `specification_profile`-Einträge verwenden reale, literale
SHA-256-Dateihashes der referenzierten Dokumente in ihrer jeweils genannten
Version. Konkrete `1.0.1`-Fixtures werden erst nach Finalisierung der
`RCC-002-RM/0.9.0`-Bytes erzeugt und MÜSSEN für alle sieben Dokumente,
einschließlich `RCC-002-RM/0.9.0`, reale SHA-256-Werte enthalten; kein
anderer `specification_profile`-Digest in diesem Beispiel oder in einer
`1.0.1`-Fixture darf ein Platzhalter sein.

**Korrekturvermerk (`RCC-002-S8RR002-BCP-001-REV2`, `2026-08-01`).** Dieses
Beispiel korrigiert zwei in `RCC_002_S8_IMPLEMENTATION_READINESS_REVIEW_
2026-07-31.md` festgestellte Blocker der Vorversion `0.8.0`:

- `S8-RR2-B01`: `views` enthielt sechsfach `rcc002.view.audit/2.0.0` statt der
  sechs verschiedenen registrierten Views aus §8.7. Korrigiert durch die
  exakte, geordnete Sechs-View-Registry-Momentaufnahme.
- `S8-RR2-B02`: `specification_profile` enthielt die Platzhalter-IDs
  `RCC-002-SPEC-0` bis `RCC-002-SPEC-6`, jeweils Version `1.0.0`, statt des
  verbindlichen Siebendokument-Profils aus §12.3. Korrigiert durch das exakte,
  geordnete Siebendokument-Profil mit sechs literalen Nicht-Selbst-Hashes und
  genau einem gekennzeichneten Nullwert-Platzhalter für den
  `RCC-002-RM/0.9.0`-Selbsteintrag.

Ausdrücklich außerhalb dieses Korrekturumfangs bleiben: das gleichnamige,
aber semantisch getrennte Feld `specification_profile` des Stage Manifest
Schema `1.0.0` (§8.4, referenziert stufenspezifische Spezifikationsstände,
nicht das Dataset-Manifest-Profil) sowie die vorbestehende illustrative
Felddrift in §8.5.

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

Durch `S8BCP-001` Revision 2 sind die Source- und Dataset-Manifest-Verträge,
alle Manifest-Schema-IDs aus §8.6, Source Snapshot V1, Source Row ID V2,
Artefaktklassen, Dataset-Manifest-Kandidat, Review-/Reproduktionsrichtung,
Release-Ledger-Regel und die zugehörigen Golden Fixtures festgelegt. Diese
Punkte dürfen nicht erneut als freie Implementierungsentscheidung geöffnet
werden. Offen bleiben ausschließlich nicht materialisierte Verträge der
Gesamtbaseline.

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

Version `0.7.2` ist eine rein mechanische Folgeanpassung ohne eigene
normative Änderung an diesem Dokument: Der Korrekturzyklus
`RCC-002-DVSEV-001` schloss die in `RCC_002_DATA_VALIDATION` §16.2 und
§24.1 Nr. 3 offene Lücke fehlender Standard-Severities für 26 von 32
registrierten Reason Codes durch einen neuen Abschnitt 16.3
„Reason-Code-Severity-Register", verbunden mit der Versionsanhebung
Data Validation 0.4.2→0.5.0. Diese Version aktualisiert ausschließlich die
Kopfzeilen-Abhängigkeitsangabe und die Tabelle in §12.3 auf diese neue
Version sowie auf ihre eigene Versionsnummer; kein Feld, keine Invariante,
kein Test und keine Ausnahmeregel dieses Dokuments wurde verändert.

Sie aktualisiert die Spezifikationsabhängigkeiten auf:

```text
RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md
Version 0.7.1

RCC_002_DATA_VALIDATION_2026-07-23.md
Version 0.5.0

RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md
Version 0.4.3

RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md
Version 0.4.2

RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md
Version 0.5.1

RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md
Version 0.4.1
```

Version `0.9.0` korrigiert im fokussierten Korrekturzyklus
`RCC-002-S8RR002-BCP-001-REV2` die von
`RCC_002_S8_IMPLEMENTATION_READINESS_REVIEW_2026-07-31.md` festgestellten
Blocker `S8-RR2-B01` und `S8-RR2-B02` an den zertifizierten
Dataset-Manifest-Artefakten der Vorversion `0.8.0`. Dies ist eine geringfügige
normative Änderung, da sie explizite kanonische Snapshot-Semantik, exakte
geordnete Mitgliedschaftsregeln, eine neue Schemaidentität und eine
prospektive Rückzugsregel einführt, ohne bestehende zertifizierte Verträge
byteweise zu verändern. Im Einzelnen:

- §8.6: Einführung von Dataset Manifest Schema `1.0.1` neben dem
  unveränderten, historisch bytegleichen Schema `1.0.0`; Rückzug von
  Schema `1.0.0` für prospektive S8-Produktion;
- §8.7: explizite Kanonisierungs- und Abgeschlossenheitsregel für
  `DatasetManifest.views` (exakt sechs Einträge in exakt der registrierten
  Reihenfolge, Trennung von `views` und `artifacts`);
- §12.3: Aktualisierung des Selbsteintrags auf `RCC-002-RM/0.9.0` sowie
  explizite Kanonisierungs- und Abgeschlossenheitsregel für
  `specification_profile` (exakt sieben Einträge in exakt der registrierten
  Reihenfolge je deklariertem Profil; „mindestens" regelt nur künftiges
  Familienwachstum über Profilversionen hinweg);
- §24: Ersetzung der defekten sechsfachen `rcc002.view.audit/2.0.0`-Wiederholung
  durch die exakte Sechs-View-Registry-Momentaufnahme; Ersetzung der
  Platzhalter-IDs `RCC-002-SPEC-0` bis `RCC-002-SPEC-6` durch das exakte
  Siebendokument-Profil mit sechs literalen Nicht-Selbst-Hashes und einem
  gekennzeichneten Nullwert-Platzhalter ausschließlich für den
  `RCC-002-RM/0.9.0`-Selbsteintrag; dazugehöriger datierter Korrekturvermerk
  mit Befund-IDs und Umfangsausschlüssen.

Ausdrücklich außerhalb dieses Korrekturumfangs bleiben das gleichnamige, aber
semantisch getrennte `specification_profile`-Feld des Stage Manifest Schema
`1.0.0` sowie die vorbestehende illustrative Felddrift in §8.5. Kein Feld,
keine Invariante und kein Test der sechs übrigen aktuellen Spezifikationen
wurde verändert; ihre Abhängigkeitsversionen bleiben `RCC_002_DATA_PIPELINE_
SPECIFICATION_2026-07-23.md` Version `0.8.0`, `RCC_002_DATA_VALIDATION_2026-
07-23.md` Version `0.6.0`, `RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md`
Version `0.4.3`, `RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md` Version
`0.4.2`, `RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md` Version
`0.5.1` und `RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md`
Version `0.5.0`, wie in der Kopfzeile dieses Dokuments angegeben.

Der aktuelle Status lautet:

```text
RCC-002-S8RR002-BCP-001-REV2 Corrected Candidate – Independent Review of
Generated Artifacts Pending
```

Nächste vorgeschriebene Schritte:

1. mechanische Verifikation und fokussierte Tests des korrigierten
   Kandidaten (`scripts/rcc002/verify_s8rr002_artifacts.py`);
2. unabhängiger Scientific Consistency Re-Review der generierten Artefakte;
3. unabhängiger Architecture Integrity Re-Review der generierten Artefakte;
4. Zertifizierung und Commit des korrigierten Kandidaten;
5. Regeneration der S8-Implementierungseingabe gegen den neuen zertifizierten
   `HEAD`;
6. Wiederholung der S8-Implementation-Readiness-Review;
7. Implementierungsfreigabe erst nach explizitem `READY`-Verdikt.

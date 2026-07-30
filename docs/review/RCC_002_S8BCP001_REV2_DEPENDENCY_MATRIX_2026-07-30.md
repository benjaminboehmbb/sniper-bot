# RCC-002 S8BCP-001 Revision 2 Dependency Matrix

## Dokumentstatus

| Feld | Wert |
|---|---|
| Dokument-ID | `RCC_002_S8BCP001_REV2_DEPENDENCY_MATRIX` |
| Datum | 2026-07-30 |
| Status | Corrected Candidate — Re-Review Pending |
| Zweck | Mechanisch prüfbare Abhängigkeits- und Eigentumsmatrix |

## 1. Spezifikationsprofil

| Dokument | Version | Geänderter normativer Umfang |
|---|---:|---|
| Data Pipeline | 0.8.0 | S0-Aggregat, Source Snapshot V1, Source Row ID V2, Zeitstempelprofil, Audit V2 |
| Data Validation | 0.6.0 | Profilgebundener Datei-/Spaltenvertrag, Zeitstempelprüfung, S0→S1-Lineage |
| Indicator | 0.4.3 | Nur Abhängigkeiten nachgezogen |
| Signal Transformation | 0.4.2 | Nur Abhängigkeiten nachgezogen |
| Regime and Gate | 0.5.1 | Nur Abhängigkeiten nachgezogen |
| Label and Forward Return | 0.5.0 | Audit V2 und S8-Viewvertrag |
| Reproducibility and Manifest | 0.8.0 | Zirkelfreie Manifest- und Release-Identitäten, Artefaktklassen |

## 2. Source-Ingest-Abhängigkeiten

| Konsument | Muss referenzieren | Eigentümer | Fail-closed bei |
|---|---|---|---|
| Source Manifest 1.0.0 | Retrieval-, Column-, Timestamp-, Snapshot-ID- und Row-ID-Profil | RM 0.8.0 / Source Registries | unbekannter Version oder nicht registrierter Periode |
| S0 | geordnete `source_files` | DP 0.8.0 | Hash-, Größen-, Ordinal- oder Periodenkonflikt |
| S1 Parser | `column_profile_id` | DV 0.6.0 / Column Registry | Header-, Encoding-, Delimiter- oder Spaltenabweichung |
| S1 Timestamp Normalizer | `timestamp_unit_profile_id` plus `archive_period` | DV 0.6.0 / Timestamp Registry | Einheitenraten oder Restklassenverletzung |
| S1 Lineage | `source_snapshot_id`, `source_file_ordinal`, `original_record_index` | DP 0.8.0 / Row-ID Registry | nicht reproduzierbarer V2-ID |

## 3. View-Abhängigkeiten

| View | Version | Erzeugerstufen | Felder | Allowlist SHA-256 |
|---|---:|---|---:|---|
| `research-features` | 1.0.0 | S0–S6 | 232 | `2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e` |
| `backtest-inputs` | 1.0.0 | S0–S6 | 232 | `2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e` |
| `paper` | 1.0.0 | S0–S6 | 232 | `2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e` |
| `live` | 1.0.0 | S0–S6 | 232 | `2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e` |
| `label-research` | 1.0.0 | S0–S7 | 534 | `0e223d60ed4139f73194f1cb3b886a8eface9229183ad522a093e966827518cc` |
| `audit` | 2.0.0 | S0–S7 | 534 | `0e223d60ed4139f73194f1cb3b886a8eface9229183ad522a093e966827518cc` |

Audit V1 ist zurückgezogen. Audit V2 darf keine S8-, Manifest- oder
Release-Felder enthalten.

## 4. Manifest- und Release-Abhängigkeiten

| Objektklasse | Darf referenzieren | Darf nicht beeinflussen |
|---|---|---|
| `DATA_ARTIFACT` | Parent-Daten, Schema- und Profilreferenzen | nachgelagerte Reviews und Ledger |
| `SCHEMA_ARTIFACT` | Spezifikations- und Registryversionen | `dataset_artifact_set_id` |
| `CONTROL_MANIFEST` | bereits finalisierte Vorgängerobjekte; Reproduktionsmanifest einseitig den Dataset-Kandidaten | eigenen finalen Bytehash, eigene Größe, eigene `artifact_id` |
| `REVIEW_ARTIFACT` | Dataset-Manifest-Kandidat | ID oder Bytes des Kandidaten |
| `RELEASE_LEDGER` | alle finalen Release-Dateien außer sich selbst | `dataset_id`, `dataset_artifact_set_id`, Vorgänger-IDs |

## 5. Re-Review-Gates

- Alle JSON-Dateien müssen syntaktisch valide sein.
- Alle sieben Spezifikationsversionen müssen exakt dem Profil in §1 entsprechen.
- Audit V2 und Label Research müssen identische Feldarrays und Hashes besitzen.
- Source-Identity-Golden-Fixtures müssen byte- und hashgenau bestehen.
- Provider-Evidence muss alle vier Archive und sämtliche 92.160 Datensätze abdecken.
- Der Identitätsgraph muss azyklisch sein.

Das Dokument bestätigt noch keine Implementierungsfreigabe.

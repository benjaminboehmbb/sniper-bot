# RCC-002 S8BCP-001 Revision 2 Identity Graph

## Dokumentstatus

| Feld | Wert |
|---|---|
| Dokument-ID | `RCC_002_S8BCP001_REV2_IDENTITY_GRAPH` |
| Datum | 2026-07-30 |
| Status | Corrected Candidate — Re-Review Pending |
| Zweck | Normativer azyklischer Identitäts- und Publikationsgraph |

## 1. Graph

```text
provider bytes + registered source profiles
                    |
                    v
             source_snapshot_id
                    |
                    v
                 build_id
                    |
          +---------+---------+
          |                   |
          v                   v
  semantic DATA_ARTIFACT   physical DATA_ARTIFACT
          |                   |
          +---------+---------+
                    |
          +---------+---------+
          |                   |
          v                   v
       dataset_id     dataset_artifact_set_id
          |                   |
          +---------+---------+
                    |
                    v
       Dataset Manifest Candidate
                    |
          +---------+---------+
          |                   |
          v                   v
   Review Manifests    Reproduction Manifest
          |                   |
          +---------+---------+
                    |
                    v
     final files except SHA256SUMS
                    |
                    v
          SHA256SUMS / Release Ledger
                    |
                    v
         external Release Record
```

Alle Pfeile zeigen ausschließlich von einem späteren Objekt auf bereits
finalisierte Vorgänger. Rückkanten sind verboten.

## 2. Exakte Identitätsgrenzen

| Identität | Beeinflussende Vorabbildung | Explizit ausgeschlossen |
|---|---|---|
| `source_snapshot_id` | Provider-/Markt-/Symbol-/Intervallwerte, vier Profilreferenzen, geordnete `source_files` | Abrufzeit, Host, Benutzer, lokaler Pfad, Retry, Cache, Erwartungen |
| `source_row_id` | Source Snapshot V1, Dateiordinal, ursprünglicher physischer Datensatzindex | Sortierindex, kanonischer Primärschlüssel, lokaler Dateipfad |
| `build_id` | Source-Identitäten, Code, semantische Konfiguration, Spezifikations- und Umgebungsprofil | Run-ID, Manifest-ID, physische Publikationsparameter |
| `artifact_id` | Schema, semantischer Hash, physischer Layout-Hash, Bytehash, Zeilen- und Zeitumfang | Reviews und Release Ledger |
| `dataset_id` | geordnete logische Datenkomponenten | Pfad, Partitionierung, Bytehash, Manifest und Reviews |
| `dataset_artifact_set_id` | `dataset_id`, geordnete `DATA_ARTIFACT`-IDs, physische Publikationskonfiguration | Schemas, Manifeste, Reviews, Ledger |
| `manifest_id` | JCS-Manifest ohne `manifest_id` | eigener finaler Bytehash, eigene Größe, eigene Artefakt-ID |

## 3. Verbotene Zyklen

- Dataset-Manifest-Kandidat → Review → zurückgeschriebener Reviewhash im Kandidaten.
- Manifest → eigener finaler Bytehash → verändertes Manifest.
- Release Ledger → eigener Ledgerhash.
- `dataset_artifact_set_id` → Control-/Review-/Ledgerobjekt → Dataset Manifest → `dataset_artifact_set_id`.

## 4. Release-Reihenfolge

1. Daten und Schemas finalisieren.
2. Source-, Stage- und Run-Manifeste finalisieren.
3. Dataset-Manifest-Kandidat bilden.
4. Reviews und Reproduktion gegen diesen unveränderten Kandidaten ausführen.
5. Alle Release-Dateien außer `SHA256SUMS` finalisieren.
6. `SHA256SUMS` lexikographisch und ohne Selbsteintrag zuletzt erzeugen.
7. Ledgerhash und -größe ausschließlich im externen Release-Record speichern.

## 5. Prüfregel

Eine Implementierung muss aus den manifestierten Referenzen einen gerichteten
Graphen bilden und per topologischer Sortierung beweisen, dass keine
Rückkante existiert. Ein Zyklus blockiert die Veröffentlichung.

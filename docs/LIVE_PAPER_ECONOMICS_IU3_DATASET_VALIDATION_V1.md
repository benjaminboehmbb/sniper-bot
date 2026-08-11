# LIVE PAPER ECONOMICS — IU-3 DATASET VALIDATION V1

- **Prüfdatum:** 2026-08-06
- **Runner-Commit:** `737beba19c90a496c4b9d5a4a2eed09da5ba85e7`
- **Branch:** `codex/pee-wip-recovery-2026-08-06`
- **Freigabestufe:** IU-3 SHADOW
- **IU-4-/Live-Freigabe:** NEIN

## Gebundener Quelldatensatz

- **Dateiname:** `price_data_with_signals_regime.csv`
- **Pfad:** `/mnt/c/Users/benja/Desktop/von G15/TradingBot 2026 old PC/ARCHIV_SB_2025/alte files SB/Stick_181225/Backup_SB_101225/Backup_9.12.2025_K3_K4longtodo/from K3 long/price_data_with_signals_regime.csv`
- **Dateigröße:** `446578512` Bytes
- **Datenzeilen:** `1048575`
- **SHA-256:** `2896badb62e3236df301a1ccf56b878916c48b22ff57483e86b9fc32bffaf104`
- **Gültige Close-Zeilen:** `1042658`
- **Zeilen ohne Close:** `5917`
- **Gültiger Zeitraum:** `2017-08-17 04:00:00+00:00` bis
  `2019-08-15 01:59:00+00:00`

Der Runner prüft den Quell-Hash vor jedem Lauf. Die Quelldatei wurde nicht in
Git kopiert. Normalisiert werden ausschließlich gültige Zeilen mit vorhandenem
Zeitstempel sowie endlichem, positivem `close`; `open_time_iso` wird zu
`timestamp_utc` umbenannt.

## Gebundenes Profil und Seed

- **Profil-ID:** `PEE_V1_PAPER_CONSERVATIVE_CANDIDATE_001`
- **Profil-Fingerprint:** `ac4cc746b57c2b802cf765c9c102f9921858c4d3cde2040f452b69ba1e6b14e1`
- **Profil-Datei-SHA-256:** `f65f00038c9420d09b7f4a0f8c28cc81a7f38998cdce52fd4f1619f89cffbc86`
- **Seed:** `seeds/5m/btcusdt_5m_timing_core_v2.csv`
- **Seed-SHA-256:** `6a07c0e6ca24cfd7b9e6bdea3562a7e505cf922e07a54c85dac6ff97473ef5e5`

## Ergebnisübersicht

| Kriterium | 10.000 Ticks | 200.000 Ticks |
|---|---:|---:|
| Runtime Return Code | 0 | 0 |
| Execution-Events | 10.000 | 200.000 |
| Ausgeführte Transitions | 18 | 60 |
| OPEN_LONG / CLOSE_LONG | 9 / 9 | 30 / 30 |
| PEE-SHADOW-Observations | 9 | 115 |
| Sidecar Issues | 0 | 0 |
| Aktive IDs = Sidecar-IDs | JA | JA |
| L1-Logzeilen | 70.012 | 1.400.118 |

### 10.000-Tick-Gate

- **Source-ID:** `PEE-IU3-SHADOW-10K-20260806`
- **Zeitraum:** `2017-08-17 04:00:00+00:00` bis
  `2017-08-24 02:39:00+00:00`
- **Normalisierter Slice-SHA-256:**
  `9f83f5500ab0bc91de641146fdc5ad5910d2fdf6a7818227b29743e51b46fdba`
- **L1-Log-SHA-256:**
  `fe0a3ef5d600513eb6b68ec2fbf88a1d139d699a1fd62e27453b9272cc4dc2b6`
- **Sidecar Report-ID:**
  `a70f3d7b9759205c207808e049b490377c4d28ce3679f845294fe995156f957e`
- **Sidecar-Report-SHA-256:**
  `23cd395ad42866fa28e2af2e1f91646a8f68bfe655364edf3c4ac46a51c36f93`

### 200.000-Tick-Lauf

- **Source-ID:** `PEE-IU3-SHADOW-200K-20260806`
- **Zeitraum:** `2017-08-17 04:00:00+00:00` bis
  `2018-01-03 10:23:00+00:00`
- **Gescannte Quellzeilen:** `200544`
- **Übersprungene ungültige Zeilen:** `544`
- **Normalisierter Slice-SHA-256:**
  `0b38752473c3082fc20c206ee35b0fd2f0f2e26a6b1426501bc74a667f5d4d6f`
- **L1-Log-SHA-256:**
  `111f4b2925e299881fb5f932f5de48c419b7895df7b8dc25359c9b47c7b1ecb5`
- **S2-SHA-256:**
  `18ea4baad434e0f11af186a3bbc9c3f3533b0a14225831942de2492a28c25b3c`
- **S4-SHA-256:**
  `c791e48568463a483fb2c36286ad7b26ad664836202d6b2b1c837e9713a4f7c5`
- **Sidecar Report-ID:**
  `db8a9a4978bdbb281b74276afefbf4eaa4a06ad2b4d1de3fd6bfe4512a75331e`
- **Sidecar-Report-SHA-256:**
  `95b57bd6cdd438474c9d839f3a29b8ec2d3bdb0accbc7df0a9604339a2f5bb00`

## Reproduzierbarkeit und Ablage

Der Runner `live_l1/tools/run_pee_shadow_validation.py` erzeugt pro Lauf ein
isoliertes Verzeichnis unter dem per `.gitignore` ausgeschlossenen
`runtime_runs/`. Sein `run_manifest.json` bindet Git-Commit, Quelle, Profil,
Seed, normalisierten Slice und sämtliche Kernausgaben per SHA-256. Der Lauf
bricht ab, wenn Quell-, Profil- oder Seed-Identität abweichen, die Runtime
fehlschlägt, der Sidecar Issues meldet oder die Observation-IDs nicht exakt
übereinstimmen.

## Aussagegrenzen

- Die Ergebnisse autorisieren ausschließlich IU-3 SHADOW.
- PEE bleibt ohne Wirkung auf Legacy-Orders, S2, S4 und Trade-PnL.
- Es gibt kein IU-4-Enforcement, keine Exchange-Anbindung und keine echten
  Orders.
- Der geprüfte Slice deckt den Anfang des Archivs ab; Offset-, Neustart- und
  Wiederaufnahmeprüfungen sind separate nächste Gates.

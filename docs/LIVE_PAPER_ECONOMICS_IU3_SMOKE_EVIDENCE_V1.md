# LIVE PAPER ECONOMICS — IU-3 SHADOW SMOKE EVIDENCE V1

- **Prüfdatum:** 2026-08-06
- **Git-Basis:** `c4bb13b`
- **Betriebsart:** isolierter SHADOW-Smoke-Lauf in `/tmp`
- **Ticks:** 1.000
- **Profil-ID:** `PEE_V1_PAPER_CONSERVATIVE_CANDIDATE_001`
- **Profil-Fingerprint:** `ac4cc746b57c2b802cf765c9c102f9921858c4d3cde2040f452b69ba1e6b14e1`

## Datensatzbindung

Verwendet wurde ein vorhandenes lokales Archiv mit dem Dateinamen
`price_data_with_signals_regime.csv`.

- Quelldateigröße: `446578512` Bytes
- Quelldatenzeilen: `1048575`
- Quell-SHA-256: `2896badb62e3236df301a1ccf56b878916c48b22ff57483e86b9fc32bffaf104`
- Verwendeter Ausschnitt: Header plus erste 1.000 Datenzeilen
- Einzige Normalisierung: Headername `open_time_iso` wurde zu
  `timestamp_utc` geändert; Datenwerte blieben unverändert.
- SHA-256 des normalisierten Ausschnitts:
  `31559170abd63e00c084e6db29e871b087092c674427279d6139fe8053280ddd`

Die Quelldatei und der Ausschnitt wurden nicht ins Repository kopiert.

## Ergebnis

- Runtime Return Code: `0`
- L1-Logzeilen: `7005`
- Persistierte S2-Snapshots: `1000`
- Persistierte S4-Snapshots: `1000`
- Execution-Ereignisse: `1000`
- Ausgeführte Legacy-Transitions: `3`
- Integrierte PEE-SHADOW-Entry-Datensätze: `2`
- Beide SHADOW-Entries: `PEE_AUTHORIZED`
- Beide Legacy-Paritätscodes:
  `PEE_SHADOW_LEGACY_EXECUTED_PEE_ALLOWED`

L1-Log-SHA-256:
`ade6921d9cfd7f9378a6a469f1d8f7d4d81fc58e1aba46b7b3b0c8a4587b7c6f`

## Unabhängiger Sidecar-Abgleich

Das vollständige Lauf-Log wurde anschließend mit dem read-only PEE-Sidecar
und demselben Profil erneut ausgewertet.

- Sidecar Observations: `2`
- Sidecar Issues: `0`
- Sidecar Report-ID:
  `07ee4c0319653500b7f1c63a923f7ad2876c4e0b0f1d1f28b275fedc02ca4259`
- Sidecar-Report-SHA-256:
  `09606da205cc21369add49bcaad2a0abc2c26aa86476bf1bb58066c8e50cd079`

Die Observation-IDs des aktiven SHADOW-Pfads und des unabhängigen Sidecars
stimmten exakt überein:

1. `9452ffd241562a54587d3d99b34f2000db648f61e66cfb7ae632b5e787fd6da1`
2. `9abc41220a8604a17120fe3b6c0d46a9be50bf01e45c1a833c8ace9ff9198f76`

## Aussagegrenzen

- Der Lauf war ein kleiner Smoke-Test, kein IU-5-Langlauf.
- Das lokale Archiv ist noch nicht als kanonischer Projektdatensatz gebunden.
- Es gab kein IU-4-Enforcement, keine Exchange-Anbindung und keine echten
  Orders.
- Sämtliche Laufartefakte lagen außerhalb des Repositorys unter `/tmp`.
